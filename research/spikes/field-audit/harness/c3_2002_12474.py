"""C3 for arXiv:2002.12474 -- refuted maximum-order claims.

The maximum-order theorems print the wrong order direction: bigger/more-spread
parameters give a SMALLER maximum, so all four statements as printed fail.

  Theorem 4 : alpha ~_w alpha* (weak submajorization) => Xn:n <=rh Yn:n.
              Instance alpha=(1,2), alpha*=(2,3): r~Xn:n > r~Yn:n, i.e. the
              TRUE order is >=rh.  Exact: for W-Exp b=g=1, each component
              r~_i = a_i e^x/(e^{a_i(e^x-1)}-1) and g(a)=a/(e^{a u}-1) is
              decreasing, so a weakly-submajorized vector has LARGER total r~.
  Theorem 5 : gamma ~_w gamma* => Xn:n <=st Yn:n.  Same instance shape:
              F_n:n is increasing in each gamma_i, so the starred (bigger)
              vector has the bigger cdf -> Xn:n >=st Yn:n, opposite of printed.
  Theorem 9 : X1:n =st Y1:n under weak majorization on lambda.  F_{1:n} =
              e^{-(sum l_i)x - n(a/b)(e^{bx}-1)} depends only on sum l_i;
              (1,4) ~^w (3,3) with sums 5 != 6 gives different survival.
  Theorem 10: alpha ~_w alpha* => Xn:n <=st Yn:n; again F increases in alpha_i
              so Xn:n >=st Yn:n.

All witnesses interval-verified; checks use plain interval evaluation on the
order-defining expressions.
"""
import sympy as sp
from mpmath import iv
import auditlib as A
import closedform as cf

x = A.x
e = A.e


def iv_at(E, pt, dps=80):
    iv.dps = dps
    return cf.iv_eval(E, sp.Rational(pt))


def wg_surv(a, b, g):
    return e ** (-A.R(a) * (e ** (A.R(g) * x) - 1) ** A.R(b))


def gm_cdf(a, b, l):
    return 1 - e ** (-A.R(l) * x - (A.R(a) / A.R(b)) * (e ** (A.R(b) * x) - 1))


def main():
    # ---- Theorem 4: rh on maxima, alpha=(1,2) ~_w (2,3) -------------------
    FX = sp.prod([1 - wg_surv(a, 1, 1) for a in (1, 2)])
    FY = sp.prod([1 - wg_surv(a, 1, 1) for a in (2, 3)])
    rX = sp.diff(FX, x) / FX
    rY = sp.diff(FY, x) / FY
    print("Theorem 4: claim Xn:n <=rh Yn:n requires r~X <= r~Y")
    for pt in ["1/4", "1", "2"]:
        v = iv_at(rX - rY, pt)
        print(f"  r~X-r~Y at x={pt}: {v}  (lower>0: {v.a>0})")
    # ---- Theorem 5: st on maxima, gamma=(1,2) ~_w (2,3) -------------------
    FX = sp.prod([1 - wg_surv(1, 2, g) for g in (1, 2)])
    FY = sp.prod([1 - wg_surv(1, 2, g) for g in (2, 3)])
    E = (1 - FY) - (1 - FX)          # S_Y - S_X = F_X - F_Y
    print("Theorem 5: claim Xn:n <=st Yn:n requires F_X >= F_Y")
    for pt in ["1/2", "1", "2"]:
        v = iv_at(FY - FX, pt)
        print(f"  F_Y-F_X at x={pt}: {v}  (lower>0: {v.a>0})")
    # ---- Theorem 9: equality of minima under weak majorization -----------
    lX, lY = [1, 4], [3, 3]
    SX = sp.prod([1 - gm_cdf(2, 1, l) for l in lX])
    SY = sp.prod([1 - gm_cdf(2, 1, l) for l in lY])
    print("Theorem 9: '=st' needs S_X == S_Y; sums 5 vs 6")
    for pt in ["1/10", "1/2", "1"]:
        v = iv_at(SY - SX, pt)
        print(f"  S_Y-S_X at x={pt}: {v}")
    # ---- Theorem 10: st on maxima, alpha=(1,2) ~_w (2,3) -----------------
    FX = sp.prod([gm_cdf(a, 1, 1) for a in (1, 2)])
    FY = sp.prod([gm_cdf(a, 1, 1) for a in (2, 3)])
    print("Theorem 10: claim Xn:n <=st Yn:n requires F_X >= F_Y")
    for pt in ["1/4", "1", "2"]:
        v = iv_at(FY - FX, pt)
        print(f"  F_Y-F_X at x={pt}: {v}  (lower>0: {v.a>0})")


if __name__ == "__main__":
    main()
