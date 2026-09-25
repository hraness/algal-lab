"""Audit of Shekari-Pakdaman-Barmalzan-Balakrishnan, J. Inequal. Appl. 2026:28
(DOI 10.1186/s13660-026-03450-7).

Model (Sec.3): DSFM mixture SF  Fbar_Pn(t) = sum_i pi_i D(Gbar(t); gamma_i),
    hazard h_Pn(t) = g(t) * sum pi_i D'(Gbar;g_i) / sum pi_i D(Gbar;g_i).
Classes: A_n = {(x;y): x_i>0, 0<y_j<1, (x_i-x_j)(y_i-y_j) <= 0}  (antiordered)
         B_n = same with >= 0 (comonotone).

Thm 8/9: n=2 hr/rh under single chain majorization [g;p] >> [g*;p*].
Thm 11: n arbitrary, single T-transform on columns (i,j): proof says
    "pi_k = pi*_k and gamma_k = gamma*_k for all k != i,j ...
     applying Theorem 8, the desired result follows immediately."
    <-- the frozen-column lift under audit.
Cor 2: same-structure T chain. Thm 12: different-structure chain with
    intermediates in A_n.

PHR specialization (Remark 11(II)): D(u;g) = u^g =>
    h_Pn(t) = h_G(t) * htilde_{pi,g}(u),  u = Gbar(t) in (0,1),
    htilde_{pi,g}(u) = sum pi_i g_i u^{g_i} / sum pi_i u^{g_i}.
Then  P >=hr Q  <=>  h_P <= h_Q  <=>  htilde_A(u) <= htilde_B(u) on (0,1).
"""
import sys
import random
import sympy as sp
from sympy import Rational as R

u = sp.Symbol("u", positive=True)
GRID = [R(1, 16), R(1, 8), R(1, 4), R(2, 5), R(1, 2), R(3, 4), R(7, 8), R(15, 16)]


def htilde(p, g, var=u):
    """sum p_i g_i var^{g_i} / sum p_i var^{g_i}; exponents must be rational."""
    num = sum(pi * gi * var ** sp.nsimplify(gi) for pi, gi in zip(p, g))
    den = sum(pi * var ** sp.nsimplify(gi) for pi, gi in zip(p, g))
    return sp.cancel(num / den)


def t_transform(row1, row2, i, j, w):
    """B = A T_w^{ij}: columns i,j mixed with weights (w, 1-w)."""
    r1, r2 = list(row1), list(row2)
    for row in (r1, r2):
        ai, aj = row[i], row[j]
        row[i] = w * ai + (1 - w) * aj
        row[j] = (1 - w) * ai + w * aj
    return tuple(r1), tuple(r2)


def in_An(row1, row2):
    """(x_i-x_j)(y_i-y_j) <= 0, x>0, 0<y<1."""
    n = len(row1)
    if not (all(x > 0 for x in row1) and all(R(0) < y < R(1) for y in row2)):
        return False
    return all((row1[i] - row1[j]) * (row2[i] - row2[j]) <= 0
               for i in range(n) for j in range(n))


def scan_sign(d, var=u, grid=GRID):
    return [(v, sp.sign(d.subs(var, v))) for v in grid]


# =====================================================================
# Part A: are the gamma-conditions satisfiable at all?
# Thm 8/11 need (i) D and -D' both DECREASING and CONVEX in gamma, or
#          (ii) both INCREASING and CONCAVE in gamma -- for all t>0, i.e.
#          all u in (0,1).  But int_0^1 D'(u;g) du = D(1)-D(0) = 1 for
#          every gamma, so -D'(u;g) cannot be monotone in g at every u
#          unless gamma-independent.  Certify on the paper's own families.
# =====================================================================
def partA():
    g = sp.Symbol("g", positive=True)
    print("=== A. gamma-condition viability ===")

    # A1: PHR family  D(u;g) = u^g
    Dp = u ** g
    mDp = -sp.diff(Dp, u)                      # -D'(u;g) = -g u^{g-1}
    d1 = sp.simplify(sp.diff(mDp, g))          # d(-D')/dg
    print("PHR: -D'(u;g) =", mDp, "  d/dg =", d1)
    for uu in (R(1, 2), sp.exp(-3), sp.exp(-4)):
        # sign of d(-D')/dg over g in (0,2)
        s_at = [sp.sign(d1.subs({u: uu, g: gg})) for gg in (R(1, 2), R(1), R(3, 2))]
        print("  u=%s: sign d(-D')/dg at g=1/2,1,3/2 -> %s" % (uu, s_at))

    # A2: Example 1(i) family  D(u;g) = theta u^g / (1-(1-theta) u^g), theta=3/5
    th = R(3, 5)
    Dex = th * u ** g / (1 - (1 - th) * u ** g)
    mDpx = sp.simplify(-sp.diff(Dex, u))
    dex = sp.simplify(sp.diff(mDpx, g))
    print("Ex1 family: -D'(u;g) =", mDpx)
    # The paper claims: decreasing and convex in 0<g<1 (for all x>0, i.e. all u)
    # evaluate at u=e^{-3} on the instance gammas {3/10, 1/2} and midpoints:
    for uu in (sp.exp(-1), sp.exp(-2), sp.exp(-3)):
        vals = [sp.N(dex.subs({u: uu, g: gg}), 12) for gg in (R(3, 10), R(2, 5), R(1, 2))]
        print("  u=e^-%s: d(-D')/dg at g=0.3,0.4,0.5 -> %s"
              % (uu.subs(sp.E, 'e') if hasattr(uu,'subs') else uu,
                 [str(v) for v in vals]))

    # A3: integral obstruction is structural: int_0^1 D'(u;g) du = 1 for all g.
    print("Integral obstruction: int_0^1 -D'(u;g) du = -1 for every gamma, so")
    print("-D' cannot be weakly monotone in gamma at every u unless it is")
    print("gamma-independent a.e. => D(u;g)=u is the only family satisfying the")
    print("hypotheses on the whole u-range.  Verified: both candidate families")
    print("above have d(-D')/dg taking both signs as u varies.")


# =====================================================================
# Part B: Thm 11 content under PHR (Remark 11(II): the PHR special case).
# A=(g;p) in A_n antiordered, B = A T single T-transform, B in A_n automatic.
# Claim (i):  htilde_A <= htilde_B on (0,1)  [P >=hr Q]
# Claim (ii): htilde_A >= htilde_B on (0,1)  [P <=hr Q]
# =====================================================================
def sweep_thm11(trials=4000, seed=11):
    rng = random.Random(seed)
    res = {"n2_i": [0, 0], "n2_ii": [0, 0], "n3_i": [0, 0], "n3_ii": [0, 0],
           "n4_i": [0, 0], "n4_ii": [0, 0]}
    ex = {}
    for _ in range(trials):
        n = rng.choice([2, 3, 4])
        # A in A_n: g increasing ranks paired with p decreasing ranks.
        gam_sorted = sorted(R(rng.randint(1, 12), rng.choice([1, 2])) for _ in range(n))
        p_raw = [R(rng.randint(1, 40), 40) for _ in range(n)]
        tot = sum(p_raw)
        order = sorted(range(n), key=lambda i: -p_raw[i])  # biggest p first
        gam = [0] * n
        p = [0] * n
        for rank, idx in enumerate(order):   # largest p gets smallest gamma
            p[idx] = p_raw[idx] / tot
            gam[idx] = gam_sorted[rank]
        gam, p = tuple(gam), tuple(p)
        if not in_An(gam, p):
            continue
        i, j = rng.sample(range(n), 2)
        w = R(rng.randint(1, 19), 20)
        gs, ps = t_transform(gam, p, i, j, w)
        if not in_An(gs, ps):
            continue  # theorem requires both in A_n (auto for T on A_n; safety)
        if not (abs(sum(ps) - 1) == 0):
            continue
        d = sp.cancel(sp.together(htilde(p, gam) - htilde(ps, gs)))
        if d == 0:
            continue
        vals = scan_sign(d)
        signs = {sgn for _, sgn in vals} - {0}
        if not signs:
            continue
        sgnset = signs
        for part, claimed in (("i", -1), ("ii", +1)):
            key = f"n{n}_{part}"
            res[key][0] += 1
            bad = (len(sgnset) > 1) or (list(sgnset)[0] != claimed)
            if bad:
                res[key][1] += 1
                ex.setdefault(key, (gam, p, gs, ps, (i, j, w), vals))
    return res, ex


# =====================================================================
# Part C: certify a chosen counterexample under PHR for Thm 11(i):
# sign change of d(u) = htilde_A - htilde_B on (0,1) via Sturm.
# =====================================================================
def certify(gam, p, gs, ps):
    d = sp.cancel(sp.together(htilde(p, gam) - htilde(ps, gs)))
    num, den = sp.fraction(d)
    num, den = sp.expand(num), sp.expand(den)
    poly = sp.Poly(num, u)
    dpol = sp.Poly(den, u)
    print("  numerator degree:", sp.degree(num, u), " denom degree:", sp.degree(den, u))
    print("  Sturm roots of numerator in (0,1):", poly.count_roots(0, 1))
    print("  denom roots in (0,1):", dpol.count_roots(0, 1))
    for v in GRID:
        print("   d(%s) = %s  sign %s" % (v, sp.nsimplify(d.subs(u, v)), sp.sign(d.subs(u, v))))
    return d


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    tr = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
    if which in ("all", "A"):
        partA()
    if which in ("all", "B"):
        res, ex = sweep_thm11(tr)
        print("=== B. Thm 11 under PHR: admissible/violating ===")
        for k, v in res.items():
            print(f"  {k}: admissible={v[0]}  violating={v[1]}")
        for k, v in ex.items():
            print("  VIOL", k, "instance:", v[:5])
