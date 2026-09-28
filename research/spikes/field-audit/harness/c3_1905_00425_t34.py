"""C3 for arxiv:1905.00425, Theorem 3.4 refutation.

Claim: mu >=^m mu* => X_{1:n} <=hr Y_{1:n} for independent Gumbel(mu_i, sigma).
Series minima hazard: h_{1:n}(x) = (1/sigma) sum_i z_i/(e^{z_i} - 1),
z_i = e^{(mu_i - x)/sigma} (hazard of Gumbel(mu,sigma): f/S = z/(e^z-1)/sigma).

Instance tested by the evaluator: mu = (3,1), mu* = (2,2), sigma = 1,
witness x = 8/5.  Here verified at 400 digits with mpmath float eval of the
closed hazard formula (independent of the iv pipeline).
"""
from mpmath import mp, mpf, exp

mp.dps = 400


def g(z):
    return z / (exp(z) - 1)


def h_min(mus, sig, t):
    s = mpf(0)
    for m in mus:
        s += g(exp((mpf(m) - mpf(t)) / mpf(sig)))
    return s / mpf(sig)


mu = (3, 1)
mus = (2, 2)
sig = mpf(1)
t = mpf(8) / 5
d = h_min(mu, sig, t) - h_min(mus, sig, t)
print("h_Xmin(8/5) - h_Ymin(8/5) =", mp.nstr(d, 25))
# X <=hr Y requires h_X >= h_Y; d<0 refutes.
assert d < 0

# also scan for a point where the REVERSED direction fails: is there any
# ordering?  Print the difference on a coarse grid.
print("scan h_X - h_Y over x:")
for i in range(-10, 25):
    tt = mpf(i) / 4
    dd = h_min(mu, sig, tt) - h_min(mus, sig, tt)
    tag = " <== negative" if dd < 0 else ""
    print("  x=%s: %s%s" % (mp.nstr(tt, 5), mp.nstr(dd, 15), tag))
