"""C3 for the arxiv:2407.18801 counterexample: independent evaluator.

Independent exponentials (the SC or PHR model after the increasing transform to
exponential rates, independence copula). P(X_{2:3} > t) = P(at most one failed)
computed directly: prod_j e^{-r_j t} + sum_i (1 - e^{-r_i t}) prod_{j != i} e^{-r_j t}.
theta = (11/4, 1/4, 3) is p-larger than theta* = (1/2, 9/4, 2); the claim is
X_{2:3} >=st Y_{2:3}, i.e. S_X(t) >= S_Y(t) for all t.
"""
from mpmath import exp, iv, mp, mpf, nstr


def surv(rates, t, lib):
    e = [lib.exp(-r * t) for r in rates]
    total = e[0] * e[1] * e[2]
    for i in range(3):
        others = [e[j] for j in range(3) if j != i]
        total += (1 - e[i]) * others[0] * others[1]
    return total


iv.dps = 50
theta = [iv.mpf(11) / 4, iv.mpf(1) / 4, iv.mpf(3)]
theta_s = [iv.mpf(1) / 2, iv.mpf(9) / 4, iv.mpf(2)]
for t in ["2", "2.7725887222397812", "4", "8"]:
    T = iv.mpf(t)
    d = surv(theta, T, iv) - surv(theta_s, T, iv)
    print("t =", t, " S_X - S_Y in", nstr(d.a, 12), nstr(d.b, 12), "negative" if d.b < 0 else ("positive" if d.a > 0 else "undecided"))
