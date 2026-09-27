"""C3 for jsta Example 3.1(ii) case 2: independent evaluation, typed from the
printed model. GE series systems, a = 0.6, lam = (1, 2.25), lam* = (1.1, 2.14);
the paper prints X_{1:2} >=st X*_{1:2}, i.e. S_X(x) >= S_X*(x) for all x."""
from mpmath import exp, iv, mp, mpf, nstr


def surv(lams, x, lib, a):
    out = 1
    for l in lams:
        out *= 1 - (1 - lib.exp(-l * x)) ** a
    return out


iv.dps = 50
a = iv.mpf(3) / 5
lam, lam_s = [iv.mpf(1), iv.mpf(9) / 4], [iv.mpf(11) / 10, iv.mpf(107) / 50]
for x in ["0.001", "0.01", "0.05", "0.5", "2", "5"]:
    X = iv.mpf(x)
    d = surv(lam, X, iv, a) - surv(lam_s, X, iv, a)
    sign = "negative" if d.b < 0 else ("positive" if d.a > 0 else "undecided")
    print(f"x = {x:6s} S_X - S_X* in [{nstr(d.a, 8)}, {nstr(d.b, 8)}]  {sign}")
