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

print("\n== Theorem 3.1(ii), reading B (f=u^2, alpha=3, Frechet parallel) ==")
# frechet margins F_i(x) = e^{-(lam_i/x)^3}, x>0; parallel max cdf = prod F_i.
# rh order X <=rh X* iff F*_x/F... numerically: r-bar difference
# D(x) = f_X (1 - F_Y) - f_Y (1 - F_X) >= 0.  f(lam) ~w f(lam*): lam=(1,2),
# lam*=(2,3) -> f(lam)=(1,4) vs f(lam*)=(4,9): top sums 1,5 <= 4,9? no wait:
# f(lam) weakly SUBmajorized: smallest... printed f(lam) ~_w f(lam*) (sub).
def frechet_max_cdf(lams, x):
    out = iv.mpf(1)
    for l in lams:
        out *= iv.exp(-(l / x) ** 3)
    return out


def rh_diff(lams, lams_s, x):
    # D = f_X (1-F_Y) - f_Y (1-F_X) >= 0 needed for X <=rh X* (claim)
    h = iv.mpf("1e-30")
    fa = (frechet_max_cdf(lams, x) - frechet_max_cdf(lams, x - h)) / h
    fb = (frechet_max_cdf(lams_s, x) - frechet_max_cdf(lams_s, x - h)) / h
    return fa * (1 - frechet_max_cdf(lams_s, x)) - fb * (1 - frechet_max_cdf(lams, x))


# printed claim: X* (lam*=(2,3)) <=rh X (lam=(1,2)):
#   D_print = f_{X*} (1-F_X) - f_X (1-F_{X*}) >= 0
# = rh_diff(lams_s, lams, x); equivalently the opposite of D above.
print("D_print(x) = f_X* (1-F_X) - f_X (1-F_X*); printed claim needs >= 0")
for t in ["0.001", "0.05", "0.1", "0.5", "1", "2", "5"]:
    X = iv.mpf(t)
    d = rh_diff([2, 3], [1, 2], X)
    sign = "negative (refutes)" if d.b < 0 else ("positive" if d.a > 0 else "undecided")
    print(f"x = {t:6s} D_print in [{nstr(d.a,8)},{nstr(d.b,8)}]  {sign}")
