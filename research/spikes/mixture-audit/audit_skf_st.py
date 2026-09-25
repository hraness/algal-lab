"""Exact audit of SKF2026 Theorems 3.1-3.6 and Corollary 3.1 (st-order claims).

Model (eq (1.3)/(1.4) of SKF2026):
    Gbar_U(t) = [ sum_i p_i Gbar(t/theta_i)^{alpha gamma_i} ]^{1/alpha}   (a != 0)
    Gbar_U(t) = prod_i Gbar(t/theta_i)^{p_i gamma_i}                      (a = 0)

For alpha != 0, sign(Gbar_U - Gbar_V) = sign(alpha) * sign(inner_U - inner_V)
since x -> x^{1/a} is increasing for a>0, decreasing for a<0.  Inner sums are
sums of monomials -> polynomials in s = e^{-t} (exp baseline, theta_i |-> exp
-alpha*g_i/theta_i * t) or in t for rational baselines.  Decided EXACTLY by
Sturm root counts; screened by exact evaluation on a rational grid.

Weak order conventions (SKF Def 2.2):  x weakly SUBmajorized by y, x <_w y:
partial sums of DECREASING rearrangement of x are <= those of y.  x weakly
SUPERmajorized by y, x <^w y: partial sums of INCREASING rearrangement of x
are >= those of y (this includes total(x) >= total(y)).

Hypothesis directions extracted from the accepted manuscript (see notes in
memo.md): Thm 3.1(i) a>=0: gam <^w del; 3.1(ii) a<0: gam <_w del.
Thm 3.2: (i) a>0 p <_w q; (ii) a>0 p <^w q; (iii) a<=0 p <^w q;
(iv) a<=0 p <_w q.  Thm 3.3: (i) a>0: p <_w q and gam <^w del;
(ii) a<0: p <_w q, gam <_w del; (iii) a=0: p <^w q, gam <^w del.
"""
import sys
import itertools
import random
import sympy as sp
from audit_lib import (R, weak_super, weak_sub, p_larger, p_larger_dec,
                       majorizes, inc_order, dec_order)

s = sp.Symbol("s", positive=True)

GRID = [R(1, 16), R(1, 8), R(1, 4), R(2, 5), R(1, 2), R(3, 4), R(7, 8), R(15, 16)]


def poly_sign_report(d, var, expected_sign):
    vals = [(v, sp.sign(d.subs(var, v))) for v in GRID]
    signs = {sg for _, sg in vals} - {0}
    if not signs:
        return ("ok-zero", vals)
    if len(signs) > 1:
        return ("crossing", vals)
    sgn = signs.pop()
    return ("ok", vals) if sgn == expected_sign else ("violation", vals)


def certify(d, var):
    num, den = sp.fraction(sp.cancel(sp.together(d)))
    num, den = sp.expand(num), sp.expand(den)
    nroots = sp.Poly(num, var).count_roots(0, 1) if num != 0 else 0
    droots = sp.Poly(den, var).count_roots(0, 1) if den not in (0, 1) and den.has(var) else 0
    return nroots, droots


def rand_sorted_prob(rng, n, dec=False):
    p = [R(rng.randint(1, 40), 40) for _ in range(n)]
    tot = sum(p)
    p = [pi / tot for pi in p]
    return tuple(sorted(p, reverse=dec))


def rand_sorted_ints(rng, n, lo, hi, dec=True):
    return tuple(sorted((rng.randint(lo, hi) for _ in range(n)), reverse=dec))


# ==========================================================================
# Theorem 3.1 — gamma vs delta, common p, scalar theta (=1), exp baseline.
#  (i)  a>0, p inc, gam/del dec: gam <^w del  =>  inner_U - inner_V <= 0
#  (ii) a<0, all dec: gam <_w del => S_U >= S_V => inner diff <= 0 (a<0 flip)
# ==========================================================================
def audit_thm31(trials=4000, seed=7):
    rng = random.Random(seed)
    res = {"i": [0, 0], "ii": [0, 0]}
    ex = {"i": None, "ii": None}
    for _ in range(trials):
        p = rand_sorted_prob(rng, 3)
        gam = rand_sorted_ints(rng, 3, 1, 10)
        dele = rand_sorted_ints(rng, 3, 1, 10)
        if weak_super(list(gam), list(dele)) and gam != dele:
            alpha = rng.choice([R(1), R(2), R(1, 2), R(3)])
            d = sp.expand(sum(p[i] * s ** sp.nsimplify(alpha * gam[i]) for i in range(3))
                          - sum(p[i] * s ** sp.nsimplify(alpha * dele[i]) for i in range(3)))
            st, det = poly_sign_report(d, s, -1)
            res["i"][0] += 1
            if st != "ok":
                res["i"][1] += 1
                ex["i"] = ex["i"] or (p, gam, dele, alpha, st, det, d)
        # part ii: all dec; gam weakly SUBmaj by del
        p2 = rand_sorted_prob(rng, 3, dec=True)
        gam2 = rand_sorted_ints(rng, 3, 1, 10)
        del2 = rand_sorted_ints(rng, 3, 1, 10)
        if weak_sub(list(gam2), list(del2)) and gam2 != del2:
            alpha = rng.choice([R(-1), R(-2)])
            # true exponents alpha*g_i are negative; shift so min exponent is 0
            exps_g = [alpha * g for g in gam2]
            exps_d = [alpha * d_ for d_ in del2]
            M = min(exps_g + exps_d)
            d = sp.expand(sum(p2[i] * s ** sp.nsimplify(exps_g[i] - M) for i in range(3))
                          - sum(p2[i] * s ** sp.nsimplify(exps_d[i] - M) for i in range(3)))
            st, det = poly_sign_report(d, s, -1)
            res["ii"][0] += 1
            if st != "ok":
                res["ii"][1] += 1
                ex["ii"] = ex["ii"] or (p2, gam2, del2, alpha, st, det, d)
    return res, ex


# ==========================================================================
# Theorem 3.2 — p vs q, common gamma, theta vector. exp baseline.
#  (i)  a>0: p,q,theta inc; gam dec; p <_w q  => inner diff <= 0
#  (ii) a>0: p,q,gam dec; theta inc; p <^w q  => S_U>=S_V => inner diff >= 0
#  (iii) a<=0: p,q,theta inc; gam dec; p <^w q => S_U<=S_V => inner diff >= 0
#        (a<0: S dec in inner -> S_U<=S_V iff inner_U>=inner_V)
#  (iv) a<=0: p,q,gam inc; theta dec; p <_w q => S_U>=S_V => inner diff <= 0
# ==========================================================================
def audit_thm32(trials=4000, seed=11):
    rng = random.Random(seed)
    res = {k: [0, 0] for k in ("i", "ii", "iii", "iv")}
    ex = {k: None for k in res}

    def inner_thetavec(pvec, gam, theta, alpha):
        return sum(pvec[i] * s ** sp.nsimplify(alpha * gam[i] / theta[i])
                   for i in range(3))

    for _ in range(trials):
        # (i) & (iii) orientation: p,q,theta inc; gam dec
        p = rand_sorted_prob(rng, 3)
        q = rand_sorted_prob(rng, 3)
        gam = rand_sorted_ints(rng, 3, 1, 8)
        theta = rand_sorted_ints(rng, 3, 1, 3, dec=False)
        if weak_sub(list(p), list(q)) and p != q:
            alpha = rng.choice([R(1), R(2)])
            d = sp.expand(inner_thetavec(p, gam, theta, alpha)
                          - inner_thetavec(q, gam, theta, alpha))
            st, det = poly_sign_report(d, s, -1)
            res["i"][0] += 1
            if st != "ok":
                res["i"][1] += 1
                ex["i"] = ex["i"] or (p, q, gam, theta, alpha, st, det, d)
        if weak_super(list(p), list(q)) and p != q:
            alpha = rng.choice([R(-1), R(-2)])
            eg = [sp.nsimplify(alpha * gam[i] / theta[i]) for i in range(3)]
            M = int(min(eg + [0]))
            d = sp.expand(inner_thetavec(p, gam, theta, alpha)
                          - inner_thetavec(q, gam, theta, alpha))
            # inner has negative powers; multiply by s^{-M}: sign-preserving
            dM = sp.expand(d * s ** (-M))
            st, det = poly_sign_report(dM, s, +1)
            res["iii"][0] += 1
            if st != "ok":
                res["iii"][1] += 1
                ex["iii"] = ex["iii"] or (p, q, gam, theta, alpha, st, det, d)
        # (ii) & (iv) orientation: p,q,gam dec, theta inc  (resp. inc for iv)
        p = rand_sorted_prob(rng, 3, dec=True)
        q = rand_sorted_prob(rng, 3, dec=True)
        gam = rand_sorted_ints(rng, 3, 1, 8)
        theta = rand_sorted_ints(rng, 3, 1, 3, dec=False)
        if weak_super(list(p), list(q)) and p != q:
            alpha = rng.choice([R(1), R(2)])
            d = sp.expand(inner_thetavec(p, gam, theta, alpha)
                          - inner_thetavec(q, gam, theta, alpha))
            st, det = poly_sign_report(d, s, +1)
            res["ii"][0] += 1
            if st != "ok":
                res["ii"][1] += 1
                ex["ii"] = ex["ii"] or (p, q, gam, theta, alpha, st, det, d)
        # (iv): p,q,gam inc; theta dec; a<0; p <_w q => inner diff <=0
        p = rand_sorted_prob(rng, 3)
        q = rand_sorted_prob(rng, 3)
        gam = rand_sorted_ints(rng, 3, 1, 8, dec=False)
        theta = rand_sorted_ints(rng, 3, 1, 3, dec=True)
        if weak_sub(list(p), list(q)) and p != q:
            alpha = rng.choice([R(-1), R(-2)])
            eg = [sp.nsimplify(alpha * gam[i] / theta[i]) for i in range(3)]
            M = int(min(eg + [0]))
            d = sp.expand((inner_thetavec(p, gam, theta, alpha)
                           - inner_thetavec(q, gam, theta, alpha)) * s ** (-M))
            st, det = poly_sign_report(d, s, -1)
            res["iv"][0] += 1
            if st != "ok":
                res["iv"][1] += 1
                ex["iv"] = ex["iv"] or (p, q, gam, theta, alpha, st, det, d)
    return res, ex


# ==========================================================================
# Theorem 3.3 — p vs q AND gam vs del, scalar theta=1.
#  (i)  a>0: p,q inc; gam,del dec; p <_w q, gam <^w del => inner diff <= 0
#  (ii) a<0: all dec; p <_w q, gam <_w del => S_U>=S_V => inner diff <= 0
#  (iii) a=0: S = exp(-t*sum p_i g_i) (theta=1): S_U<=S_V iff sum p g >= sum q d
# ==========================================================================
def audit_thm33(trials=4000, seed=13):
    rng = random.Random(seed)
    res = {k: [0, 0] for k in ("i", "ii", "iii")}
    ex = {k: None for k in res}
    for _ in range(trials):
        p = rand_sorted_prob(rng, 3)
        q = rand_sorted_prob(rng, 3)
        gam = rand_sorted_ints(rng, 3, 1, 10)
        dele = rand_sorted_ints(rng, 3, 1, 10)
        if weak_sub(list(p), list(q)) and weak_super(list(gam), list(dele)) \
                and (p != q or gam != dele):
            alpha = rng.choice([R(1), R(2), R(1, 2)])
            d = sp.expand(sum(p[i] * s ** sp.nsimplify(alpha * gam[i]) for i in range(3))
                          - sum(q[i] * s ** sp.nsimplify(alpha * dele[i]) for i in range(3)))
            st, det = poly_sign_report(d, s, -1)
            res["i"][0] += 1
            if st != "ok":
                res["i"][1] += 1
                ex["i"] = ex["i"] or (p, q, gam, dele, alpha, st, det, d)
        # (iii) alpha=0: claim sum p_i g_i >= sum q_i d_i
            lhs = sum(p[i] * gam[i] for i in range(3))
            rhs = sum(q[i] * dele[i] for i in range(3))
            res["iii"][0] += 1
            if not (lhs >= rhs):
                res["iii"][1] += 1
                ex["iii"] = ex["iii"] or (p, q, gam, dele, lhs, rhs)
        # (ii) all dec
        p2 = rand_sorted_prob(rng, 3, dec=True)
        q2 = rand_sorted_prob(rng, 3, dec=True)
        gam2 = rand_sorted_ints(rng, 3, 1, 10)
        del2 = rand_sorted_ints(rng, 3, 1, 10)
        if weak_sub(list(p2), list(q2)) and weak_sub(list(gam2), list(del2)) \
                and (p2 != q2 or gam2 != del2):
            alpha = rng.choice([R(-1), R(-2)])
            eg = [sp.nsimplify(alpha * g) for g in gam2]
            ed = [sp.nsimplify(alpha * dd) for dd in del2]
            M = min(eg + ed)
            d = sp.expand(sum(p2[i] * s ** (eg[i] - M) for i in range(3))
                          - sum(q2[i] * s ** (ed[i] - M) for i in range(3)))
            st, det = poly_sign_report(d, s, -1)
            res["ii"][0] += 1
            if st != "ok":
                res["ii"][1] += 1
                ex["ii"] = ex["ii"] or (p2, q2, gam2, del2, alpha, st, det, d)
    return res, ex


# ==========================================================================
# Theorems 3.4-3.6, Corollary 3.1 — scale vectors theta vs xi, common scalar
# gamma.  Rational baselines: Lomax  Gbar(t)=1/(1+t)  (t^2 g increasing);
# power  Gbar(t)=1-t^2, 0<t<1  (t g = 2 t^2 increasing).
# Model inner(t) = sum_i p_i Gbar(t/theta_i)^{a*gamma}; Gbar rational.
# ==========================================================================
t_ = sp.Symbol("t", positive=True)


def inner_lomax(p, theta, agam):
    """Gbar(t/theta) = theta/(theta+t); term = (theta_i/(theta_i+t))^{a*gamma}.
    agam integer -> rational in t."""
    return sum(p[i] * (R(theta[i]) / (R(theta[i]) + t_)) ** int(agam)
               for i in range(len(p)))


def inner_power2(p, theta, agam):
    """Gbar(t/theta) = 1-(t/theta)^2 on 0<t<min theta."""
    return sum(p[i] * (1 - (t_ / R(theta[i])) ** 2) ** int(agam)
               for i in range(len(p)))


def audit_thm34(trials=3000, seed=17):
    """Thm 3.4: t^2 g increasing; alpha < gamma(scalar); p inc; theta,xi dec;
    theta <^w xi => U >=st V.  Baseline Lomax Gbar=1/(1+t) (t^2 g=t^2/(1+t)^2
    increasing).  inner(t)=sum p_i (theta_i/(theta_i+t))^{a g}.
    S = inner^{1/a}: for a>0 claim inner diff >=0; for a<0 claim inner diff<=0.
    a<g and a != 0 both regimes; also a=0 separately (prod form).
    """
    rng = random.Random(seed)
    res = {"pos": [0, 0], "neg": [0, 0], "zero": [0, 0]}
    ex = {"pos": None, "neg": None, "zero": None}
    TG = [R(1, 4), R(1, 2), R(1), R(2), R(3), R(5)]
    for _ in range(trials):
        p = rand_sorted_prob(rng, 3)
        gam = rng.randint(1, 6)
        theta = rand_sorted_ints(rng, 3, 1, 9)
        xi = rand_sorted_ints(rng, 3, 1, 9)
        if not weak_super(list(theta), list(xi)) or theta == xi:
            continue
        ag = rng.choice([g for g in (gam - 1, gam - 2, R(gam - 1, 2), 2 * gam, -gam, -2 * gam)
                         if g != 0 and R(g) < gam])
        # claim: S_U >= S_V
        du = inner_lomax(list(p), list(theta), ag)
        dv = inner_lomax(list(p), list(xi), ag)
        d = sp.cancel(sp.together(du - dv))
        num, den = sp.fraction(d)
        vals = [sp.sign(d.subs(t_, v)) for v in TG]
        signs = set(vals) - {0}
        expected = 1 if ag > 0 else -1   # inner diff sign for S_U>=S_V
        key = "pos" if ag > 0 else "neg"
        res[key][0] += 1
        if len(signs) > 1 or (signs and signs.pop() != expected):
            res[key][1] += 1
            ex[key] = ex[key] or (p, gam, theta, xi, ag, vals, d)
    return res, ex


def audit_thm35(trials=3000, seed=19):
    """Thm 3.5: t g(t) increasing; theta p-larger xi (prod of k smallest theta
    >= prod xi); p inc; theta,xi dec; alpha < gamma scalar => U >=st V.
    Baseline power2: Gbar = 1 - t^2 on (0,1), t/theta in (0,1) needs
    t < min theta => all theta >= 1, evaluate t in (0,1)."""
    rng = random.Random(seed)
    res = {"pos": [0, 0], "neg": [0, 0]}
    ex = {"pos": None, "neg": None}
    TG = [R(1, 8), R(1, 4), R(1, 2), R(3, 4), R(7, 8)]
    for _ in range(trials):
        p = rand_sorted_prob(rng, 3)
        gam = rng.randint(1, 6)
        theta = rand_sorted_ints(rng, 3, 1, 9)
        xi = rand_sorted_ints(rng, 3, 1, 9)
        if not p_larger(list(theta), list(xi)) or theta == xi:
            continue
        ag = rng.choice([g for g in (gam - 1, gam - 2, R(gam - 1, 2), 2 * gam, -gam, -2 * gam)
                         if g != 0 and R(g) < gam])
        du = inner_power2(list(p), list(theta), ag)
        dv = inner_power2(list(p), list(xi), ag)
        d = sp.cancel(sp.together(du - dv))
        vals = [sp.sign(d.subs(t_, v)) for v in TG]
        signs = set(vals) - {0}
        expected = 1 if ag > 0 else -1
        key = "pos" if ag > 0 else "neg"
        res[key][0] += 1
        if len(signs) > 1 or (signs and signs.pop() != expected):
            res[key][1] += 1
            ex[key] = ex[key] or (p, gam, theta, xi, ag, vals, d)
    return res, ex


def audit_thm36_cor31(trials=3000, seed=23):
    """Thm 3.6: a<=0; p,q inc; theta,xi dec; theta <^w xi (weak super),
    p <_w q (weak sub)  => U >=st V.  Same Lomax baseline.
    Cor 3.1: under Thm 3.5 setup with xi=(xi*,..,xi*) constant, claim
    Gbar_U >= Gbar(t/xi*)^gamma  (i.e. inner_U >= Gbar^gamma for a>0
    direction of S inequality; careful: S = inner^{1/a}).
    Cor 3.1 as stated: Gbar_{U_n(p,gam,theta)}(t) >= Gbar(t/xi*)^gamma.
    Condition xi* <= K1(xi) (products test).
    """
    rng = random.Random(seed)
    res = {"36pos": [0, 0], "36neg": [0, 0], "cor": [0, 0]}
    ex = {"36pos": None, "36neg": None, "cor": None}
    TG = [R(1, 4), R(1, 2), R(1), R(2), R(3), R(5)]
    for _ in range(trials):
        p = rand_sorted_prob(rng, 3)
        q = rand_sorted_prob(rng, 3)
        gam = rng.randint(1, 6)
        theta = rand_sorted_ints(rng, 3, 1, 9)
        xi = rand_sorted_ints(rng, 3, 1, 9)
        if weak_super(list(theta), list(xi)) and weak_sub(list(p), list(q)) \
                and (theta != xi or p != q):
            ag = rng.choice([-R(1), -R(2), -R(gam + 1)])
            du = inner_lomax(list(p), list(theta), ag)
            dv = inner_lomax(list(q), list(xi), ag)
            d = sp.cancel(sp.together(du - dv))
            vals = [sp.sign(d.subs(t_, v)) for v in TG]
            signs = set(vals) - {0}
            # a<0: S dec in inner -> S_U>=S_V iff inner diff <=0
            res["36neg"][0] += 1
            if len(signs) > 1 or (signs and signs.pop() != -1):
                res["36neg"][1] += 1
                ex["36neg"] = ex["36neg"] or (p, q, gam, theta, xi, ag, vals, d)
        # Cor 3.1: xi constant = xi* <= K1(xi-vec); theta p-larger xi-vec
        xi_star = rng.randint(1, 6)
        theta2 = rand_sorted_ints(rng, 3, 1, 9)
        gam2 = rng.randint(1, 6)
        xiv = (xi_star,) * 3
        if p_larger(list(theta2), list(xiv)):
            # condition in Cor 3.1: xi* <= K1(xi) is what makes theta <^p xi*
            # admissible; here just test conclusion: S_U >= Gbar(t/xi*)^{gam}
            ag2 = rng.choice([g for g in (gam2 - 1, R(gam2 - 1, 2), -gam2) if g != 0])
            du = inner_lomax(list(p), list(theta2), ag2)
            rhs = (R(xi_star) / (R(xi_star) + t_)) ** int(ag2)
            d = sp.cancel(sp.together(du - rhs))
            vals = [sp.sign(d.subs(t_, v)) for v in TG]
            signs = set(vals) - {0}
            expected = 1 if ag2 > 0 else -1
            res["cor"][0] += 1
            if len(signs) > 1 or (signs and signs.pop() != expected):
                res["cor"][1] += 1
                ex["cor"] = ex["cor"] or (p, gam2, theta2, xi_star, ag2, vals, d)
    return res, ex


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    tr = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
    funcs = {"31": audit_thm31, "32": audit_thm32, "33": audit_thm33,
             "34": audit_thm34, "35": audit_thm35, "36": audit_thm36_cor31}
    for tag, fn in funcs.items():
        if which in ("all", tag):
            res, ex = fn(tr)
            print(f"== Thm/Cor {tag} ==  admissible/violations: {res}")
            for k, v in ex.items():
                if v is not None:
                    print(f"   FIRST VIOLATION ({k}): {v}")
            sys.stdout.flush()
