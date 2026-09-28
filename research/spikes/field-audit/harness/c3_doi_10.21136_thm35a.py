"""C3 independent check: doi:10.21136/am.2018.0105-17 Theorem 3.5(a).

Claim (printed): for 0 < alpha <= 1, beta ~m beta* implies X1:n >=fr Y1:n,
i.e. r_{X1:n}(x) <= r_{Y1:n}(x) for all x > max(beta_i) under the paper's
convention X1 <=fr X2 iff r_X1 >= r_X2.

Instance: alpha = 1/2, beta = (1/10, 1, 9), beta* = (1/10, 4, 6); both
premises hold (alpha = 1/2 <= 1; beta majorizes beta*: descending partial
sums 9 >= 6, 10 >= 10, totals 10.1 = 10.1).

The hazard of a series system is the SUM of component hazards:
  r_{X1:3}(x) = sum_i alpha x^{alpha-1} / (x^alpha + beta_i^alpha).
We evaluate d(x) = r_Y - r_X = r_{Y1:3}(x) - r_{X1:3}(x) with mpmath interval
arithmetic: d(x) < 0 (strict enclosure) refutes X1:3 >=fr Y1:3.
"""
from mpmath import iv, nstr

iv.dps = 80
a = iv.mpf(1) / 2
beta = [iv.mpf(1) / 10, iv.mpf(1), iv.mpf(9)]
betas = [iv.mpf(1) / 10, iv.mpf(4), iv.mpf(6)]


def rmin(scales, xx):
    return sum(a * xx ** (a - 1) / (xx ** a + b ** a) for b in scales)


for xx in [iv.mpf("9.000000000001"), iv.mpf("9.1"), iv.mpf("10"), iv.mpf("12"),
           iv.mpf("16"), iv.mpf("20"), iv.mpf("30"), iv.mpf("50"), iv.mpf("100")]:
    d = rmin(betas, xx) - rmin(beta, xx)
    tag = "STRICTLY NEGATIVE -> refuted" if d.b < 0 else (
        "positive" if d.a > 0 else "undecided")
    print("x =", nstr(xx, 8), " r_Y - r_X in", nstr(d.a, 10), nstr(d.b, 10), tag)
