"""Audit of SKF2026 Theorems 3.7-3.12, Corollaries 3.2-3.3 (hr and rh orders).

For scalar theta and exponential baseline Gbar=e^{-t}: hazard rate of the
alpha-mixture is h_U(t) = (1/theta) * htilde_{p,g}(s^alpha) where
    htilde_{p,g}(y) = sum_i p_i g_i y^{g_i} / sum_i p_i y^{g_i},  y = e^{-t}.
So hr comparisons reduce to comparing htilde in y in (0,1) (a>0), i.e. to
ordinary exponential-mixture hazard differences (rational in s).

Thm 3.7 (n=2): [p;gam] >> [q;del] chain maj, [p;gam] in V2 and a>=0 (or W2 and
    a<=0) => U2 >=hr V2 (resp <=hr).  htilde comparison in y.
Thm 3.10 (n=2, rh): two readings:
  (a) displayed formula r_U = (r/theta) htilde(G^a): reduces to the SAME
      htilde comparison in y' = G(t/theta)^a in (0,1) for a>0.
  (b) literal rh of model (1.3): r_U = f/F with F_U = 1 - S_U.
Thm 3.8/3.9, Cor 3.2 (hr, n>=2); Thm 3.11/3.12, Cor 3.3 (rh) — the V_n, a>=0
halves are already refuted by the manuscript; here we additionally probe the
W_n / a<=0 halves which the manuscript leaves untouched.
"""
import sys
import random
import itertools
import sympy as sp
from audit_lib import R, in_Vn, in_Wn, inc_order, dec_order

s = sp.Symbol("s", positive=True)
GRID = [R(1, 16), R(1, 8), R(1, 4), R(2, 5), R(1, 2), R(3, 4), R(7, 8), R(15, 16)]


def htilde(p, g, alpha, var):
    """sum p_i g_i var^{a g_i} / sum p_i var^{a g_i}."""
    num = sum(pi * gi * var ** sp.nsimplify(alpha * gi) for pi, gi in zip(p, g))
    den = sum(pi * var ** sp.nsimplify(alpha * gi) for pi, gi in zip(p, g))
    return sp.cancel(num / den)


def t_transform(row1, row2, i, j, omega):
    """Apply T = omega I + (1-omega) Pi_{ij} to the 2xn matrix [row1;row2]."""
    r1, r2 = list(row1), list(row2)
    for row in (r1, r2):
        ai, aj = row[i], row[j]
        row[i] = omega * ai + (1 - omega) * aj
        row[j] = (1 - omega) * ai + omega * aj
    return tuple(r1), tuple(r2)


def diff_sign_scan(d, var, grid=GRID):
    return [(v, sp.sign(d.subs(var, v))) for v in grid]


def certify(d, var):
    num, den = sp.fraction(sp.cancel(sp.together(d)))
    num, den = sp.expand(num), sp.expand(den)
    nroots = sp.Poly(num, var).count_roots(0, 1) if num != 0 else 0
    return nroots


# ==========================================================================
# Theorem 3.7 (n=2, hr).  [p;gam] in V2, a>=0 => h_U >= h_V (U >=hr V means
# h_U >= h_V?  Def 2.1(ii): Y <=hr Z iff h_Y >= h_Z.  Claim U2 >=hr V2 means
# h_U <= h_V.  Wait: Y <=hr Z iff h_Y >= h_Z, so U >=hr V iff h_U <= h_V.)
# Actually the claim: "U2 >=hr V2" i.e. h_U <= h_V on (0,inf).
# For a>0, y = Gbar(t/theta)^a sweeps (0,1): compare htilde_p,g(y) <=
# htilde_q,d(y).
# ==========================================================================
def audit_thm37(trials=6000, seed=31):
    rng = random.Random(seed)
    res = {"V_aPos": [0, 0], "W_aNeg": [0, 0], "V_a0": [0, 0], "W_a0": [0, 0]}
    ex = {k: None for k in res}
    for _ in range(trials):
        # n=2 matrix [p;gam] in V2: (p1-p2)(g1-g2) <= 0
        p1 = R(rng.randint(1, 40), 40)
        g1, g2 = rng.randint(1, 12), rng.randint(1, 12)
        if p1 <= R(1, 2):
            p = (p1, 1 - p1)
            gam = (max(g1, g2), min(g1, g2))
        else:
            p = (p1, 1 - p1)
            gam = (min(g1, g2), max(g1, g2))
        if not in_Vn(list(p), list(gam)):
            continue
        omega = R(rng.randint(1, 19), 20)
        i, j = 0, 1
        q, dele = t_transform(list(p), list(gam), i, j, omega)
        # claim (V2, a>=0): h_U <= h_V i.e. htilde_p,g <= htilde_q,d on (0,1)
        alpha = rng.choice([R(1), R(2), R(3), R(1, 2)])
        d = sp.cancel(sp.together(htilde(p, gam, alpha, s) - htilde(q, dele, alpha, s)))
        vals = [(v, sp.sign(d.subs(s, v))) for v in GRID]
        signs = {sg for _, sg in vals} - {0}
        res["V_aPos"][0] += 1
        if len(signs) > 1 or (signs and signs.pop() != -1):
            res["V_aPos"][1] += 1
            ex["V_aPos"] = ex["V_aPos"] or (p, gam, q, dele, alpha, vals, d)
        # W2 / a<=0 half: need [p;gam] in W2: same-order p and gam
        p1 = R(rng.randint(1, 40), 40)
        pW = (p1, 1 - p1)
        gW = (min(g1, g2), max(g1, g2)) if p1 <= R(1, 2) else (max(g1, g2), min(g1, g2))
        # wait: W2 wants (p1-p2)(g1-g2) >= 0
        if not in_Wn(list(pW), list(gW)):
            continue
        qW, dW = t_transform(list(pW), list(gW), 0, 1, omega)
        alpha_n = rng.choice([R(-1), R(-2), R(-1, 2)])
        eg = [alpha_n * g for g in gW] + [alpha_n * dd for dd in dW]
        M = min(eg)
        # htilde with negative exponents: multiply num/den by s^{-M}
        def ht_neg(p_, g_):
            num = sum(pi * gi * s ** sp.nsimplify(alpha_n * gi - M)
                      for pi, gi in zip(p_, g_))
            den = sum(pi * s ** sp.nsimplify(alpha_n * gi - M)
                      for pi, gi in zip(p_, g_))
            return sp.cancel(num / den)
        d = sp.cancel(sp.together(ht_neg(pW, gW) - ht_neg(qW, dW)))
        vals = [(v, sp.sign(d.subs(s, v))) for v in GRID]
        signs = {sg for _, sg in vals} - {0}
        res["W_aNeg"][0] += 1
        if len(signs) > 1 or (signs and signs.pop() != +1):  # claim: U <=hr V => h_U >= h_V
            res["W_aNeg"][1] += 1
            ex["W_aNeg"] = ex["W_aNeg"] or (pW, gW, qW, dW, alpha_n, vals, d)
        # alpha = 0: h_U = (h(t/th)/th)(p.gam) -> claim h_U <= h_V iff p.g <= q.d
        lhs = sum(pi * gi for pi, gi in zip(p, gam))
        rhs = sum(qi * di for qi, di in zip(q, dele))
        res["V_a0"][0] += 1
        if not (lhs <= rhs):
            res["V_a0"][1] += 1
            ex["V_a0"] = ex["V_a0"] or (p, gam, q, dele, lhs, rhs)
        lhsW = sum(pi * gi for pi, gi in zip(pW, gW))
        rhsW = sum(qi * di for qi, di in zip(qW, dW))
        res["W_a0"][0] += 1
        if not (lhsW >= rhsW):
            res["W_a0"][1] += 1
            ex["W_a0"] = ex["W_a0"] or (pW, gW, qW, dW, lhsW, rhsW)
    return res, ex


# ==========================================================================
# Theorem 3.8/3.9 (hr, n>=3): explore the UNTOUCHED half: [p;gam] in Wn,
# alpha <= 0, claim U <=hr V i.e. h_U >= h_V.
# With a<0, y = Gbar^a > 1: htilde evaluated on y in (1,inf); work in
# var = 1/s > 1, i.e. test in s' = 1/y in (0,1) via substitution.
# htilde(1/s) - comparison rational in s still.
# ==========================================================================
def audit_thm38_Whalf(trials=4000, seed=37):
    rng = random.Random(seed)
    res = {"n3": [0, 0], "n4": [0, 0]}
    ex = {"n3": None, "n4": None}
    for _ in range(trials):
        n = rng.choice([3, 4])
        # [p;gam] in Wn: p and gam comonotone (same order)
        p_raw = rand_perm = [R(rng.randint(1, 40), 40) for _ in range(n)]
        tot = sum(p_raw)
        order = sorted(range(n), key=lambda i: p_raw[i])
        p = [0] * n
        gam_sorted = sorted(rng.randint(1, 10) for _ in range(n))
        gam = [0] * n
        for rank, idx in enumerate(order):
            p[idx] = p_raw[idx] / tot
            gam[idx] = gam_sorted[rank]
        p, gam = tuple(p), tuple(gam)
        # single T-transform on a random pair
        i, j = rng.sample(range(n), 2)
        omega = R(rng.randint(1, 19), 20)
        q, dele = t_transform(list(p), list(gam), i, j, omega)
        # claim (Wn, a<=0): U <=hr V => h_U >= h_V.
        # For a<0, y = s^alpha = s^{-|a|} > 1.  htilde(y) in s: exponents
        # alpha*g_i < 0; normalize by s^{-min} to get polynomials.
        alpha = rng.choice([R(-1), R(-2)])
        allexp = [alpha * g for g in gam] + [alpha * dd for dd in dele]
        M = min(allexp)
        def ht_inv(p_, g_):
            num = sum(pi * gi * s ** sp.nsimplify(alpha * gi - M) for pi, gi in zip(p_, g_))
            den = sum(pi * s ** sp.nsimplify(alpha * gi - M) for pi, gi in zip(p_, g_))
            return sp.cancel(num / den)
        d = sp.cancel(sp.together(ht_inv(p, gam) - ht_inv(q, dele)))
        vals = [(v, sp.sign(d.subs(s, v))) for v in GRID]
        signs = {sg for _, sg in vals} - {0}
        key = "n3" if n == 3 else "n4"
        res[key][0] += 1
        if len(signs) > 1 or (signs and signs.pop() != +1):
            res[key][1] += 1
            ex[key] = ex[key] or (p, gam, q, dele, (i, j, omega), alpha, vals, d)
    return res, ex


# ==========================================================================
# Theorem 3.11 Wn/alpha<=0 half (rh order, displayed formula reading):
# claim U >=rh V: r_U >= r_V where r_U = (r/theta) htilde_{p,g}(G^a).
# For a<0, G^a > 1, y=1/x in (0,1): same htilde comparison on (0,1).
# ==========================================================================
def audit_thm311_Whalf(trials=4000, seed=41):
    rng = random.Random(seed)
    res = [0, 0]
    example = None
    for _ in range(trials):
        n = 3
        p_raw = [R(rng.randint(1, 40), 40) for _ in range(n)]
        tot = sum(p_raw)
        order = sorted(range(n), key=lambda i: p_raw[i])
        p = [0] * n
        gam_sorted = sorted(rng.randint(1, 10) for _ in range(n))
        gam = [0] * n
        for rank, idx in enumerate(order):
            p[idx] = p_raw[idx] / tot
            gam[idx] = gam_sorted[rank]
        p, gam = tuple(p), tuple(gam)
        i, j = rng.sample(range(n), 2)
        omega = R(rng.randint(1, 19), 20)
        q, dele = t_transform(list(p), list(gam), i, j, omega)
        alpha = rng.choice([R(-1), R(-2)])
        allexp = [alpha * g for g in gam] + [alpha * dd for dd in dele]
        M = min(allexp)
        def ht_inv(p_, g_):
            num = sum(pi * gi * s ** sp.nsimplify(alpha * gi - M) for pi, gi in zip(p_, g_))
            den = sum(pi * s ** sp.nsimplify(alpha * gi - M) for pi, gi in zip(p_, g_))
            return sp.cancel(num / den)
        d = sp.cancel(sp.together(ht_inv(p, gam) - ht_inv(q, dele)))
        vals = [(v, sp.sign(d.subs(s, v))) for v in GRID]
        signs = {sg for _, sg in vals} - {0}
        res[0] += 1
        if len(signs) > 1 or (signs and signs.pop() != +1):
            res[1] += 1
            example = example or (p, gam, q, dele, (i, j, omega), alpha, vals, d)
    return res, example


# ==========================================================================
# Theorem 3.10 (n=2, rh) under the LITERAL reading (b): r_U = f_U/F_U of
# the model (1.3).  For exp baseline theta=1, alpha=1 this is the reversed
# hazard of an ordinary exponential mixture.  The manuscript shows the pair
# (3,5) vs (4,4), equal weights, already fails.  Search for more instances.
# ==========================================================================
def rh_exp(rates, p):
    num = sum(pi * vi * s ** vi for pi, vi in zip(p, rates))
    den = 1 - sum(pi * s ** vi for pi, vi in zip(p, rates))
    return sp.cancel(num / den)


def audit_thm310_literal(trials=4000, seed=43):
    rng = random.Random(seed)
    res = [0, 0]
    example = None
    for _ in range(trials):
        # n=2: [p;gam] in V2 or W2, alpha=1 (>=0 branch) claim U <=rh V:
        # r_p,g <= r_q,d i.e. for V2 claim d <= 0.
        p1 = R(rng.randint(1, 40), 40)
        g1, g2 = rng.randint(1, 12), rng.randint(1, 12)
        if p1 <= R(1, 2):
            p = (p1, 1 - p1)
            gam = (max(g1, g2), min(g1, g2))
        else:
            p = (p1, 1 - p1)
            gam = (min(g1, g2), max(g1, g2))
        omega = R(rng.randint(1, 19), 20)
        q, dele = t_transform(list(p), list(gam), 0, 1, omega)
        d = sp.cancel(sp.together(rh_exp(gam, p) - rh_exp(dele, q)))
        vals = [(v, sp.sign(d.subs(s, v))) for v in GRID]
        signs = {sg for _, sg in vals} - {0}
        res[0] += 1
        if len(signs) > 1 or (signs and signs.pop() != -1):
            res[1] += 1
            example = example or (p, gam, q, dele, vals, d)
    return res, example


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    tr = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
    if which in ("all", "37"):
        res, ex = audit_thm37(tr)
        print("== Thm 3.7 (n=2 hr) ==  admissible/viol:", res)
        for k, v in ex.items():
            if v: print("  VIOL", k, v)
        sys.stdout.flush()
    if which in ("all", "38"):
        res, ex = audit_thm38_Whalf(tr)
        print("== Thm 3.8 Wn/a<=0 half ==", res)
        for k, v in ex.items():
            if v: print("  VIOL", k, v)
        sys.stdout.flush()
    if which in ("all", "311"):
        res, ex = audit_thm311_Whalf(tr)
        print("== Thm 3.11 Wn/a<=0 half (displayed-formula reading) ==", res)
        if ex: print("  VIOL", ex)
        sys.stdout.flush()
    if which in ("all", "310"):
        res, ex = audit_thm310_literal(tr)
        print("== Thm 3.10 literal-model rh reading ==", res)
        if ex: print("  VIOL", ex)
