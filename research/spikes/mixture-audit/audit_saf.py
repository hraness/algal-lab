"""Audit of SAF2022 (Shojaee-Asadi-Finkelstein, generalized finite alpha-mixtures).

Accepted-manuscript numbering (Strathprints 79140): Thm 3.1, 3.5, 4.1, 5.1,
5.2, 6.5 (= publ. Thm 6.1), 6.9, Cors 6.12-6.14, Remark 6.15, Thm 6.17
(= publ. Thm 6.3), Cor 6.21, Remark 6.18 (= publ. Remark 6.3).

Model: Sbar(t) = [sum_i p_i Fbar_i(t)^{a_i}]^{1/abar}, abar = sum p_i a_i.
Hazard rate r(t) = (1/abar) * sum_i a_i p_i r_i(t) Fbar_i^{a_i} / S_inner.

Baselines in exact arithmetic:
  exp:   Fbar_i = e^{-lam_i t}          -> monomials in s = e^{-t/N}
  lomax: Fbar(t|lam) = lam/(lam+t)      -> rationals in t (incr. concave in lam)
  prh:   Fbar(t|lam) = 1-(1-e^{-t})^lam -> polynomials in x = 1-e^{-t}
"""
import sys
import random
import itertools
import sympy as sp
from audit_lib import R, weak_super, weak_sub, majorizes, inc_order, in_Un

s = sp.Symbol("s", positive=True)
t = sp.Symbol("t", positive=True)
GRID = [R(1, 16), R(1, 8), R(1, 4), R(2, 5), R(1, 2), R(3, 4), R(7, 8), R(15, 16)]


def sign_scan(d, var, grid=GRID):
    return [(v, sp.sign(d.subs(var, v))) for v in grid]


def report(vals, expected, tie_ok=True):
    signs = {sg for _, sg in vals} - {0}
    if not signs:
        return "ok" if tie_ok else "ok-zero"
    if len(signs) > 1:
        return "crossing"
    return "ok" if signs.pop() == expected else "violation"


# ---- SAF generalized alpha-mixture with exp components (integer exps) ----
def saf_inner_exp(lam, p, alpha, var):
    """sum p_i var^{a_i lam_i} (exponents must be nonnegative integers)."""
    return sum(pi * var ** int(sp.nsimplify(ai * li))
               for pi, ai, li in zip(p, alpha, lam))


def saf_r_exp(lam, p, alpha, var):
    """r(t,abar) = (1/abar) sum_i a_i p_i lam_i var^{a_i l_i} / inner.
    Negative exponents: caller must shift (multiply num and den by var^{-min})."""
    abar = sum(pi * ai for pi, ai in zip(p, alpha))
    num = sum(ai * pi * li * var ** sp.nsimplify(ai * li)
              for pi, ai, li in zip(p, alpha, lam))
    den = sum(pi * var ** sp.nsimplify(ai * li) for pi, ai, li in zip(p, alpha, lam))
    return sp.cancel(num / (abar * den))


# ==========================================================================
# SAF Thm 3.1: F1 <=hr ... <=hr Fn (rates lam1 >= lam2 >= ... >= lamn).
#  a_i > 0 ordered (either direction): claim F1 <=hr mix  <=> r_mix <= r1.
#  a_i < 0 ordered: claim mix <=hr Fn  <=> r_mix >= rn.
# ==========================================================================
def audit_saf31(trials=4000, seed=101):
    rng = random.Random(seed)
    res = {"pos": [0, 0], "neg": [0, 0]}
    ex = {"pos": None, "neg": None}
    for _ in range(trials):
        n = 3
        lam = tuple(sorted((rng.randint(1, 9) for _ in range(n)), reverse=True))
        p_raw = [R(rng.randint(1, 30), 30) for _ in range(n)]
        tot = sum(p_raw)
        p = tuple(pi / tot for pi in p_raw)
        alpha_dir = rng.choice([1, -1])
        alpha = tuple(sorted((rng.randint(1, 5) for _ in range(n)),
                             reverse=rng.random() < 0.5))
        if alpha_dir > 0:
            alpha_pos = alpha  # any monotone direction admissible
            rmix = saf_r_exp(lam, p, alpha_pos, s)
            d = sp.cancel(sp.together(rmix - R(lam[0])))
            vals = sign_scan(d, s)
            res["pos"][0] += 1
            if report(vals, -1) != "ok":
                res["pos"][1] += 1
                ex["pos"] = ex["pos"] or (lam, p, alpha, vals, d)
        else:
            # a_i < 0: use a_i in {-5..-1} ordered (either direction)
            alpha_n = tuple(-a for a in alpha)
            exps = [ai * li for ai, li in zip(alpha_n, lam)]
            M = min(exps)  # negative
            abar = sum(pi * ai for pi, ai in zip(p, alpha_n))
            num = sum(ai * pi * li * s ** sp.nsimplify(ai * li - M)
                      for pi, ai, li in zip(p, alpha_n, lam))
            den = sum(pi * s ** sp.nsimplify(ai * li - M)
                      for pi, ai, li in zip(p, alpha_n, lam))
            rmix = sp.cancel(num / (abar * den))
            # claim r_mix >= r_n = lam[-1] (smallest rate):  d >= 0
            d = sp.cancel(sp.together(rmix - R(lam[-1])))
            vals = sign_scan(d, s)
            res["neg"][0] += 1
            if report(vals, +1) != "ok":
                res["neg"][1] += 1
                ex["neg"] = ex["neg"] or (lam, p, alpha_n, vals, d)
    return res, ex


# ==========================================================================
# SAF Thm 3.5 (a): all F_i DFR & a_i>0 -> mix DFR; all IFR & a_i<0 -> IFR.
# Exponential components are both DFR and IFR.
# For a_i>0 the mixture is DFR iff r'(t)<=0 i.e. dr/ds >= 0 (s=e^{-t}, ds/dt<0).
# Wait: r decreasing in t iff dr/ds >= 0?  dt: r'(t) = dr/ds * (-N s) -> sign
# of r'(t) = -sign(dr/ds).  DFR <=> r'(t) <= 0 <=> dr/ds >= 0 on (0,1).
# For a_i<0: IFR <=> r'(t) >= 0 <=> dr/ds <= 0.
# ==========================================================================
def audit_saf35(trials=3000, seed=103):
    rng = random.Random(seed)
    res = {"dfr": [0, 0], "ifr": [0, 0]}
    ex = {"dfr": None, "ifr": None}
    for _ in range(trials):
        n = 3
        lam = tuple(rng.randint(1, 9) for _ in range(n))
        p_raw = [R(rng.randint(1, 30), 30) for _ in range(n)]
        tot = sum(p_raw)
        p = tuple(pi / tot for pi in p_raw)
        alpha = tuple(rng.randint(1, 4) for _ in range(n))
        rmix = saf_r_exp(lam, p, alpha, s)
        drds = sp.cancel(sp.together(sp.diff(rmix, s)))
        num, den = sp.fraction(drds)
        # DFR claim: dr/ds >= 0 on (0,1)
        vals = sign_scan(num, s)
        res["dfr"][0] += 1
        rr = report(vals, +1)
        if rr not in ("ok", "ok-zero"):
            res["dfr"][1] += 1
            ex["dfr"] = ex["dfr"] or (lam, p, alpha, vals, drds)
        # negative alpha branch: IFR claim
        alpha_n = tuple(-a for a in alpha)
        exps = [ai * li for ai, li in zip(alpha_n, lam)]
        M = min(exps)
        abar = sum(pi * ai for pi, ai in zip(p, alpha_n))
        num_r = sum(ai * pi * li * s ** sp.nsimplify(ai * li - M)
                    for pi, ai, li in zip(p, alpha_n, lam))
        den_r = sum(pi * s ** sp.nsimplify(ai * li - M)
                    for pi, ai, li in zip(p, alpha_n, lam))
        rmix_n = sp.cancel(num_r / (abar * den_r))
        drds_n = sp.cancel(sp.together(sp.diff(rmix_n, s)))
        num2, _ = sp.fraction(drds_n)
        vals2 = sign_scan(num2, s)
        res["ifr"][0] += 1
        r2 = report(vals2, -1)
        if r2 not in ("ok", "ok-zero"):
            res["ifr"][1] += 1
            ex["ifr"] = ex["ifr"] or (lam, p, alpha_n, vals2, drds_n)
    return res, ex


# ==========================================================================
# SAF Thm 6.5 (publ. 6.1): st order, weak SUPERmajorization.
#  (p,lam),(p,gam) in U_n; Fbar dec convex in lam; a_1<=..<=a_n; a_i>=1;
#  a_i p_i >= a_j p_j for i<=j; lam <^w gam -> S_lam >= S_gam.
#  Exp baseline: inner lam-sum vs gam-sum; claim inner diff >= 0 (abar>0).
#  WLOG: p dec, lam inc (antiordered); require a inc AND a_i p_i dec.
# ==========================================================================
def audit_saf65(trials=4000, seed=107):
    rng = random.Random(seed)
    res = [0, 0]
    ex = None
    for _ in range(trials):
        n = 3
        p = tuple(sorted((R(rng.randint(1, 40), 40) for _ in range(n)), reverse=True))
        tot = sum(p)
        p = tuple(pi / tot for pi in p)
        lam = tuple(sorted(rng.randint(1, 9) for _ in range(n)))
        gam = tuple(sorted(rng.randint(1, 10) for _ in range(n)))
        if not (in_Un(list(p), list(lam)) and in_Un(list(p), list(gam))):
            continue
        if not weak_super(list(gam), list(lam)) or lam == gam:  # SAF lam weakly supermajorizes gam = inc partial sums of lam <= gam
            continue
        alpha = tuple(sorted(rng.randint(1, 5) for _ in range(n)))
        if not all(alpha[i] * p[i] >= alpha[i + 1] * p[i + 1] for i in range(n - 1)):
            continue
        # inner sums: sum p_i s^{a_i lam_i}; claim S_lam >= S_gam.
        # abar>0 -> inner_U >= inner_V
        du = saf_inner_exp(lam, p, alpha, s)
        dv = saf_inner_exp(gam, p, alpha, s)
        d = sp.expand(du - dv)
        vals = sign_scan(d, s)
        res[0] += 1
        if report(vals, +1) != "ok":
            res[1] += 1
            ex = ex or (p, lam, gam, alpha, vals, d)
    return res, ex


# ==========================================================================
# SAF Thm 6.9: st order, weak supermaj, Fbar INCREASING CONCAVE in lam,
#  a_i <= 0  or  0<a_i<1 with a_i p_i >= a_j p_j;  claim S_lam <= S_gam.
# Baseline Lomax Fbar(t|lam) = lam/(lam+t): rational in t for rational lam.
#  a_i <= 0: inner = sum p_i (lam/(lam+t))^{a_i} = sum p_i ((lam+t)/lam)^{|a_i|}
#  claim: S_lam <= S_gam; abar<0 -> S = inner^{1/abar} dec in inner ->
#  need inner_lam >= inner_gam.
#  0<a_i<1: abar>0 -> need inner_lam <= inner_gam; use a_i=1/2 (algebraic).
# ==========================================================================
def audit_saf69(trials=2500, seed=109):
    rng = random.Random(seed)
    res = {"neg": [0, 0], "frac": [0, 0]}
    ex = {"neg": None, "frac": None}
    TT = [R(1, 4), R(1, 2), R(1), R(2), R(5), R(10)]
    for _ in range(trials):
        n = 3
        p = tuple(sorted((R(rng.randint(1, 40), 40) for _ in range(n)), reverse=True))
        tot = sum(p)
        p = tuple(pi / tot for pi in p)
        lam = tuple(sorted(rng.randint(1, 9) for _ in range(n)))
        gam = tuple(sorted(rng.randint(1, 10) for _ in range(n)))
        if not (in_Un(list(p), list(lam)) and in_Un(list(p), list(gam))):
            continue
        if not weak_super(list(gam), list(lam)) or lam == gam:  # SAF lam weakly supermajorizes gam = inc partial sums of lam <= gam
            continue
        # negative branch: a_i in {-4..-1} inc (i.e. a_1<=a_2<=a_3<0)
        alpha = tuple(sorted((-rng.randint(1, 5) for _ in range(n))))
        # weight condition applies only to 0<a<1 branch per statement, but the
        # (a_i<=0) case needs alpha_1<=...<=alpha_n; keep it.
        du = sum(p[i] * ((R(lam[i]) + t) / R(lam[i])) ** int(-alpha[i]) for i in range(n))
        dv = sum(p[i] * ((R(gam[i]) + t) / R(gam[i])) ** int(-alpha[i]) for i in range(n))
        d = sp.cancel(sp.together(du - dv))
        vals = [(v, sp.sign(d.subs(t, v))) for v in TT]
        res["neg"][0] += 1
        if report(vals, +1) != "ok":  # need inner_lam >= inner_gam (abar<0)
            res["neg"][1] += 1
            ex["neg"] = ex["neg"] or (p, lam, gam, alpha, vals, d)
        # fractional branch 0<a_i<1 with a_i p_i >= a_j p_j
        alpha_f = tuple(sorted((R(1, 2),) * n)) if rng.random() < 0.5 else \
            tuple(sorted(sp.nsimplify(v) for v in (R(1, 4), R(1, 2), R(3, 4))))
        if not all(alpha_f[i] * p[i] >= alpha_f[i + 1] * p[i + 1] for i in range(n - 1)):
            continue
        du = sum(p[i] * (R(lam[i]) / (R(lam[i]) + t)) ** alpha_f[i] for i in range(n))
        dv = sum(p[i] * (R(gam[i]) / (R(gam[i]) + t)) ** alpha_f[i] for i in range(n))
        d = du - dv
        vals = [(v, sp.sign(d.subs(t, v))) for v in TT]
        res["frac"][0] += 1
        if report(vals, -1) != "ok":  # abar>0 -> need inner diff <= 0
            res["frac"][1] += 1
            ex["frac"] = ex["frac"] or (p, lam, gam, alpha_f, vals, d)
    return res, ex


# ==========================================================================
# SAF Cor 6.14: PRH family Fbar(t|lam) = 1 - F(t)^lam, F=1-e^{-t}; integer lam.
#  a_i <= 0 or 0<a_i<1 (weight condition), a inc, lam <^w gam, U_n:
#  claim S_lam <= S_gam.  With x = 1 - e^{-t} in (0,1), Fbar_i = 1 - x^{lam_i}
#  polynomial.  alpha_i integer <= -1 -> inner terms (1-x^{l_i})^{a_i} are
#  rational; multiply through by product of denominators.
# ==========================================================================
def audit_cor614(trials=2500, seed=113):
    rng = random.Random(seed)
    x = sp.Symbol("x", positive=True)
    res = {"neg": [0, 0]}
    ex = {"neg": None}
    for _ in range(trials):
        n = 3
        p = tuple(sorted((R(rng.randint(1, 40), 40) for _ in range(n)), reverse=True))
        tot = sum(p)
        p = tuple(pi / tot for pi in p)
        lam = tuple(sorted(rng.randint(1, 6) for _ in range(n)))
        gam = tuple(sorted(rng.randint(1, 7) for _ in range(n)))
        if not (in_Un(list(p), list(lam)) and in_Un(list(p), list(gam))):
            continue
        if not weak_super(list(gam), list(lam)) or lam == gam:  # SAF lam weakly supermajorizes gam = inc partial sums of lam <= gam
            continue
        alpha = tuple(sorted((-rng.randint(1, 4) for _ in range(n))))
        # inner = sum p_i (1 - x^{l_i})^{a_i}; a_i negative -> denominator terms
        def inn(vec):
            out = 0
            for i in range(n):
                out += p[i] * (1 - x ** vec[i]) ** int(alpha[i])
            return sp.together(out)
        d = sp.cancel(inn(lam) - inn(gam))
        vals = sign_scan(d, x)
        res["neg"][0] += 1
        if report(vals, +1) != "ok":  # abar<0, claim S_lam<=S_gam -> inner>=
            res["neg"][1] += 1
            ex["neg"] = ex["neg"] or (p, lam, gam, alpha, vals, d)
    return res, ex


# ==========================================================================
# SAF Thm 6.17 (publ. 6.3): n=2 hazard rate.
# Branch A: r(t|lam) inc+concave, Fbar dec in lam; a1<=a2, a_i>=0,
#   a1 p1 >= a2 p2, (p,lam),(p,gam) in U2, lam >^m gam => r_lam <= r_gam.
#   Test with exp baseline, general a1,a2>0.
# Branch B: r dec+convex, Fbar inc in lam; a_i<0 => r_lam >= r_gam.
#   Lomax Fbar=lam/(lam+t): r(t|lam)=1/(lam+t) dec convex; a_i<0.
# ==========================================================================
def audit_saf617(trials=4000, seed=127):
    rng = random.Random(seed)
    res = {"A": [0, 0], "B": [0, 0]}
    ex = {"A": None, "B": None}
    for _ in range(trials):
        # Branch A: exp baseline, a1,a2>0 integers (exponents a_i l_i integer)
        # generate admissible: p1 >= p2, lam inc, gam = T-transform of lam,
        # alpha inc with a1 p1 >= a2 p2
        p1 = R(rng.randint(21, 40), 40)
        p = (p1, 1 - p1)
        l1, l2 = sorted((rng.randint(1, 9) for _ in range(2)))
        lam = (l1, l2)
        om = R(rng.randint(1, 19), 20)
        gam = (om * l1 + (1 - om) * l2, (1 - om) * l1 + om * l2)
        # U2: (p1-p2)(lam1-lam2) <= 0 (lam inc, p1>=p2 OK); gam sandwiched inc
        if not (in_Un(list(p), list(lam)) and in_Un(list(p), list(gam))):
            continue
        if not majorizes(list(lam), list(gam)) or lam == gam:
            continue
        alpha = tuple(sorted(rng.randint(1, 5) for _ in range(2)))
        if not (alpha[0] * p[0] >= alpha[1] * p[1]):
            continue
        rlam = saf_r_exp(lam, p, alpha, s)
        rgam = saf_r_exp(gam, p, alpha, s)
        d = sp.cancel(sp.together(rlam - rgam))
        vals = sign_scan(d, s)
        res["A"][0] += 1
        rr = report(vals, -1)
        if rr not in ("ok", "ok-zero"):
            res["A"][1] += 1
            ex["A"] = ex["A"] or (p, lam, gam, alpha, vals, d)
        # Branch B: Lomax, a_i<0, claim r_lam >= r_gam on (0,inf)
        p1 = R(rng.randint(21, 40), 40)
        pB = (p1, 1 - p1)
        l1, l2 = sorted((rng.randint(1, 9) for _ in range(2)))
        lamB = (l1, l2)
        om = R(rng.randint(1, 19), 20)
        gamB = (om * l1 + (1 - om) * l2, (1 - om) * l1 + om * l2)
        if not (in_Un(list(pB), list(lamB)) and in_Un(list(pB), list(gamB))):
            continue
        if not majorizes(list(lamB), list(gamB)) or lamB == gamB:
            continue
        alphaB = tuple(sorted((-rng.randint(1, 5) for _ in range(2))))
        def r_lomax(lvec):
            # Fbar_i = lam_i/(lam_i+t); Fbar_i^{a_i} = ((lam_i+t)/lam_i)^{|a_i|}
            # r_i = 1/(lam_i + t); abar < 0
            abar = pB[0] * alphaB[0] + pB[1] * alphaB[1]
            Fi_a = [((l + t) / l) ** int(-a) for l, a in zip(lvec, alphaB)]
            num = sum(alphaB[i] * pB[i] * (1 / (R(lvec[i]) + t)) * Fi_a[i]
                      for i in range(2))
            den = sum(pB[i] * Fi_a[i] for i in range(2))
            return sp.cancel(num / (abar * den))
        d = sp.cancel(sp.together(r_lomax(lamB) - r_lomax(gamB)))
        TT = [R(1, 4), R(1, 2), R(1), R(2), R(5), R(10)]
        vals = [(v, sp.sign(d.subs(t, v))) for v in TT]
        res["B"][0] += 1
        if report(vals, +1) != "ok":
            res["B"][1] += 1
            ex["B"] = ex["B"] or (pB, lamB, gamB, alphaB, vals, d)
    return res, ex


# ==========================================================================
# SAF Thm 5.2: two different baseline sequences F_i <=hr G_i (rates a_i>=b_i),
# common p.  (i) a_i/abar*r_{Fi} inc in i or same for G; (ii) Fbar_i/Gbar_i
# inc in i <=> (b_i - a_i) inc; (iii) F_i <=hr G_i; (iv) a_1>=...>=a_n>0.
# Claim: F_p <=hr G_p i.e. r_F_mix >= r_G_mix.
# ==========================================================================
def audit_saf52(trials=4000, seed=131):
    rng = random.Random(seed)
    res = {"Fi": [0, 0], "Gi": [0, 0]}
    ex = {"Fi": None, "Gi": None}
    for _ in range(trials):
        n = 3
        # constructive admissibility: b_i>=1 arbitrary; delta_i=a_i-b_i>=0 DEC
        # (so b-a inc => Fbar_i/Gbar_i inc); alpha dec; cond (i): alpha_i*a_i
        # inc (F) or alpha_i*b_i inc (G).
        b = tuple(rng.randint(1, 9) for _ in range(n))
        delta = tuple(sorted((rng.randint(0, 6) for _ in range(n)),
                             reverse=True))
        a = tuple(b[i] + delta[i] for i in range(n))
        if a == b:
            continue
        alpha = tuple(sorted((rng.randint(1, 5) for _ in range(n)),
                             reverse=True))
        p_raw = [R(rng.randint(1, 30), 30) for _ in range(n)]
        tot = sum(p_raw)
        p = tuple(pi / tot for pi in p_raw)
        condF = all(alpha[i] * a[i] <= alpha[i + 1] * a[i + 1] for i in range(n - 1))
        condG = all(alpha[i] * b[i] <= alpha[i + 1] * b[i + 1] for i in range(n - 1))
        if not (condF or condG):
            continue
        rF = saf_r_exp(a, p, alpha, s)
        rG = saf_r_exp(b, p, alpha, s)
        d = sp.cancel(sp.together(rF - rG))
        vals = sign_scan(d, s)
        key = "Fi" if condF else "Gi"
        res[key][0] += 1
        if report(vals, +1) != "ok":
            res[key][1] += 1
            ex[key] = ex[key] or (p, a, b, alpha, vals, d)
    # --- alpha_i < 0 branch: (ii) now requires Fbar_i/Gbar_i DEC in i
    # (delta_i = a_i - b_i INC); alpha dec (negative). ---
    for _ in range(trials):
        n = 3
        b = tuple(rng.randint(1, 9) for _ in range(n))
        delta = tuple(sorted(rng.randint(0, 6) for _ in range(n)))
        a = tuple(b[i] + delta[i] for i in range(n))
        if a == b:
            continue
        alpha = tuple(sorted((-rng.randint(1, 5) for _ in range(n)),
                             reverse=True))  # e.g. (-1,-2,-3) dec
        p_raw = [R(rng.randint(1, 30), 30) for _ in range(n)]
        tot = sum(p_raw)
        p = tuple(pi / tot for pi in p_raw)
        # (i) for alpha<0: (alpha_i/abar)*rate_i inc <=> alpha_i*rate_i DEC
        condF = all(alpha[i] * a[i] >= alpha[i + 1] * a[i + 1] for i in range(n - 1))
        condG = all(alpha[i] * b[i] >= alpha[i + 1] * b[i + 1] for i in range(n - 1))
        if not (condF or condG):
            continue
        abarN = sum(p[i] * alpha[i] for i in range(n))
        def rE(rate):
            exps = [alpha[i] * rate[i] for i in range(n)]
            M = min(exps)
            num = sum(alpha[i] * p[i] * rate[i] * s ** sp.nsimplify(exps[i] - M)
                      for i in range(n))
            den = sum(p[i] * s ** sp.nsimplify(exps[i] - M) for i in range(n))
            return sp.cancel(num / (abarN * den))
        d = sp.cancel(sp.together(rE(a) - rE(b)))
        vals = sign_scan(d, s)
        key = "FiN" if condF else "GiN"
        res.setdefault(key, [0, 0])
        res[key][0] += 1
        if report(vals, +1) != "ok":
            res[key][1] += 1
            ex.setdefault(key, None)
            ex[key] = ex[key] or (p, a, b, alpha, vals, d)
    return res, ex


# ==========================================================================
# SAF Thm 4.1: n=2 multiplicative model r_i = lam_i r(t); exp baseline r=1.
# Hypothesis: lam1<=lam2, a1 <= c a2 with c = lam2/lam1, a_i>0.
# Claim (a): r_mix -> (a1/abar) lam1 as t->oo; (b) difference ->0 iff
#            r(t) exp(-(a2 l2 - a1 l1) int r) -> 0; for r=1 iff a2 l2 > a1 l1.
# Exact limit check.
# ==========================================================================
def audit_saf41(trials=500, seed=137):
    rng = random.Random(seed)
    res = {"a": [0, 0], "b": [0, 0]}
    ex = {"a": None, "b": None}
    tt = sp.Symbol("t", positive=True)
    for _ in range(trials):
        lam1 = rng.randint(1, 5)
        lam2 = lam1 + rng.randint(0, 5)
        if lam2 == 0:
            continue
        c = R(lam2, lam1)
        p1 = R(rng.randint(1, 30), 30)
        p = (p1, 1 - p1)
        a1 = rng.randint(1, 5)
        a2 = rng.randint(1, 8)
        if not (a1 <= c * a2):
            continue
        abar = p[0] * a1 + p[1] * a2
        rmix = (a1 * p[0] * lam1 * sp.exp(-a1 * lam1 * tt)
                + a2 * p[1] * lam2 * sp.exp(-a2 * lam2 * tt)) / \
               (abar * (p[0] * sp.exp(-a1 * lam1 * tt)
                        + p[1] * sp.exp(-a2 * lam2 * tt)))
        lim = sp.limit(rmix, tt, sp.oo)
        res["a"][0] += 1
        expected = R(a1) * lam1 / abar
        if sp.simplify(lim - expected) != 0:
            res["a"][1] += 1
            ex["a"] = ex["a"] or (p, lam1, lam2, a1, a2, lim, expected)
        # part (b): r_mix - (a1/abar) r1 -> 0 iff a2 l2 > a1 l1 (r=1).
        # For a2 l2 = a1 l1 the model is degenerate (single exponential).
        limd = sp.limit(rmix - expected, tt, sp.oo)
        holds = sp.simplify(limd) == 0
        should_hold = bool(a2 * lam2 > a1 * lam1)
        res["b"][0] += 1
        if holds != should_hold:
            res["b"][1] += 1
            ex["b"] = ex["b"] or (p, lam1, lam2, a1, a2, limd, should_hold)
    return res, ex


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    tr = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
    funcs = {"saf31": audit_saf31, "saf35": audit_saf35, "saf52": audit_saf52,
             "saf65": audit_saf65, "saf69": audit_saf69, "cor614": audit_cor614,
             "saf617": audit_saf617, "saf41": audit_saf41}
    for tag, fn in funcs.items():
        if which in ("all", tag):
            res, ex = fn(tr)
            print(f"== SAF {tag} ==  admissible/violations: {res}")
            if isinstance(ex, dict):
                for k, v in ex.items():
                    if v is not None:
                        print(f"   FIRST VIOLATION ({k}): {v}")
            elif ex is not None:
                print(f"   FIRST VIOLATION: {ex}")
            sys.stdout.flush()
