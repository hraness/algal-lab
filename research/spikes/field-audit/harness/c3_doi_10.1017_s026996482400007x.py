"""C3 second evaluations for eval_doi_10.1017_s026996482400007x.py.

Thm 3.7 refutation is re-verified by direct high-precision evaluation of the
hazard difference  h_{X_{1:n}}(x) - h_{Y_{1:n}}(x)  at and around the witness
t = 1/10, with h_{X_{1:n}} = sum_i k*lam_i*(lam_i x)^{k-1}/(1-Ā e^{-(lam_i x)^k})
(the paper's own printed formula, eq. (3.11)) — an independent path that does
not go through closedform.check's order-expression machinery.  Also verified
again via closedform.check at a different working precision.
"""

import sympy as sp
from mpmath import mp, mpf, exp

import closedform as cf
from closedform import x as t

mp.dps = 100
R = sp.Rational


def ew_hazard_terms(lams, alpha, k):
    """h_{X_{1:n}}(x) = sum_i k*l_i*(l_i x)^{k-1} / (1 - (1-alpha) e^{-(l_i x)^k})."""
    terms = []
    for li in lams:
        li = mpf(li)
        def g(x, li=li):
            u = (li * x) ** k
            return k * li * (li * x) ** (k - 1) / (1 - (1 - alpha) * exp(-u))
        terms.append(g)
    def h(x):
        return sum(g(x) for g in terms)
    return h


def ew_surv(a, lam, k):
    e = sp.exp(-(R(lam) * t) ** R(k))
    return R(a) * e / (1 - (1 - R(a)) * e)


if __name__ == "__main__":
    # --- Theorem 3.7: lam=(5,2) >=m mu=(7/2,7/2), alpha=1/3, k=3/2 ---
    alpha, k = mpf(1) / 3, mpf(3) / 2
    lam, mu = [mpf(5), mpf(2)], [mpf(7) / 2, mpf(7) / 2]
    # premise sanity: totals equal, mu asc sums >= lam asc sums
    assert sum(lam) == sum(mu) and mu[0] >= min(lam)
    hX = ew_hazard_terms(lam, alpha, k)
    hY = ew_hazard_terms(mu, alpha, k)
    print("Thm 3.7 (k=3/2, a=1/3):  diff = h_X - h_Y at ...")
    for xs in [mpf("0.02"), mpf("0.05"), mpf("0.08"), mpf("0.1"),
               mpf("0.12"), mpf("0.15"), mpf("0.2"), mpf("0.3"), mpf("0.4"),
               mpf("0.5")]:
        d = hX(mpf(xs)) - hY(mpf(xs))
        print(f"   t={mp.nstr(xs,3)}: {mp.nstr(d,8)}")
    # printed claim requires diff >= 0 for all t; observed diff < 0 on
    # ~[0.07, 0.35] -> refutes the Schur-convexity argument.
    # closedform cross-check of the order at higher working precisions
    SX = sp.prod([ew_surv(R(1, 3), 5, R(3, 2)),
                  ew_surv(R(1, 3), 2, R(3, 2))])
    SY = sp.prod([ew_surv(R(1, 3), R(7, 2), R(3, 2))] * 2)
    print("   closedform hr(X<=Y):", cf.check("hr", cf.Closed(SX), cf.Closed(SY),
                                             precisions=(120, 300)))

    # --- Theorem 3.8/3.9 sensitivity (sub-reading) witness: alpha=(9/10,3/5),
    #     beta=(3/5,7/10) ---
    a, b = [mpf(9) / 10, mpf(3) / 5], [mpf(3) / 5, mpf(7) / 10]
    # sub-majorization premise: alpha desc sums >= beta desc sums
    assert (a[0] >= max(b)) and (a[0] + min(a) >= sum(b))
    # For tilt-comparison (lam=1,k=1): h_i = 1/(1-(1-a_i)e^{-x})
    def h_tilt(aa, x):
        return 1 / (1 - (1 - aa) * exp(-x))
    def hmin_tilt(params, x):
        return sum(h_tilt(ai, x) for ai in params)
    print("Thm 3.8 sub-reading (alpha top-dominant): h_X - h_Y")
    for xs in [mpf("0.5"), mpf(1), mpf(2)]:
        d = hmin_tilt(a, xs) - hmin_tilt(b, xs)
        print(f"   t={mp.nstr(xs,3)}: {mp.nstr(d,8)}  (claim Y>=hr X needs <=0)")
