"""C3 for doi:10.1007/s11587-026-01094-9 refutations.

All refutations use Fbar(x;a)=e^{-a x} (decreasing & log-convex & convex in
a), psi=1/p (decreasing, convex, log-convex; psi^{-1}(v)=1/v), and the
paper's Def 2.2 convention:  a <=w b means ascending partial sums of a
are >= those of b (weak supermajorization).

Checked claims (X side = (v,alpha;N1), starred side = (u,beta;N2)):
  Thm 3.1/3.3-like series:  S_min = prod_i (1/v_i) e^{-a_i x}
  Thm 3.4/3.5 parallel:     F_max = prod_i (1 - (1/v_i) e^{-a_i x})
All differences are computed symbolically with sympy and numerically
(300-digit mpmath) at the evaluator's witness x = 1e-12 and at x = 1.
"""
from mpmath import mp, mpf, exp

mp.dps = 300


def S_min(v, a, xv):
    s = mpf(1)
    for vi, ai in zip(v, a):
        s *= (1 / mpf(vi)) * exp(-mpf(ai) * xv)
    return s


def S_max(v, a, xv):
    f = mpf(1)
    for vi, ai in zip(v, a):
        f *= 1 - (1 / mpf(vi)) * exp(-mpf(ai) * xv)
    return 1 - f


w = mpf(10) ** -12

cases = [
    # (label, v, alpha, u, beta, kind)
    ("T3.1", (3, 3), (4, 4), (3, 3), (2, 5), "min"),
    ("T3.1b", (3, 3), (3, 3), (2, 4), (3, 3), "min"),   # via beta row
    ("T3.2", (4, 4), (1, 1), (2, 5), (1, 1), "min"),
    ("T3.4", (3, 3), (1, 1), (2, 4), (mpf(1) / 2, mpf(3) / 2), "max"),
    ("T3.6/7/8", (3, 3), (1, 1), (2, 4), (mpf(1) / 2, mpf(3) / 2), "max"),
]

for lab, v, a, u, b, kind in cases:
    f = S_min if kind == "min" else S_max
    # claim: T_side >= st T*_side  =>  S_X >= S_Y ; diff = S_X - S_Y
    for xv in (w, mpf(1), mpf(10)):
        d = f(v, a, xv) - f(u, b, xv)
        print("%-9s x=%-8s S_X-S_Y = %s" %
              (lab, mp.nstr(xv, 4), mp.nstr(d, 15)))
