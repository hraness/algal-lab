#!/usr/bin/env python
"""Exact verification of a perturbed example with distinct minimal rates.

Rates lambda = (1, 3, 5) and gamma = (1 + e, 4 - e, 4) with e = 1/40, equal
weights 1/3.  lambda majorizes gamma and min lambda = 1 < 41/40 = min gamma, so
the hazards satisfy h_lambda <= h_gamma near t = 0 and near t = infinity, while
the difference is positive at an intermediate time.  Hence the hazard difference
changes sign exactly twice.  With s = exp(-t/40) every exponential is a monomial
in s with integer exponent, so the hazard difference is a rational function of s
with rational coefficients; its roots in (0,1) are isolated exactly
(Vincent-Collins-Akritas, sympy Poly.intervals) and its sign is evaluated
exactly at rational points.
"""
import sys
import time

import sympy as sp

R = sp.Rational
s = sp.Symbol("s", positive=True)      # s = exp(-t/N), 0 < s < 1
N = 40
EPS_RATE = R(1, N)
RESULTS = []


def check(name, condition):
    ok = bool(condition)
    RESULTS.append((name, ok))
    print(("PASS " if ok else "FAIL ") + name)


def majorizes(x, y):
    xs, ys = sorted(x, reverse=True), sorted(y, reverse=True)
    px = py = 0
    for u, v in zip(xs, ys):
        px, py = px + u, py + v
        if px < py:
            return False
    return px == py


lam = (1, 3, 5)
gam = (1 + EPS_RATE, 4 - EPS_RATE, 4)
w = (R(1, 3),) * 3
check("1 lambda majorizes gamma, equal sums", majorizes(lam, gam) and sum(lam) == sum(gam))
check("2 min lambda = 1 < 41/40 = min gamma", min(lam) == 1 and min(gam) == R(41, 40))


def survival(rates):
    return sum(wi * s**int(N * r) for r, wi in zip(rates, w))


def hazard(rates):
    num = sum(wi * r * s**int(N * r) for r, wi in zip(rates, w))
    return num / survival(rates)


t0 = time.time()
diff = sp.cancel(sp.together(hazard(lam) - hazard(gam)))
num, den = sp.fraction(diff)
num_poly, den_poly = sp.Poly(sp.expand(num), s), sp.Poly(sp.expand(den), s)
print(f"   numerator degree {num_poly.degree()}, denominator degree {den_poly.degree()}")

lo_end, hi_end = R(1, 10**30), 1 - R(1, 10**30)
den_roots = den_poly.intervals(inf=lo_end, sup=hi_end)
check("3 the denominator has no root in (0,1) (it is a product of positive sums)",
      len(den_roots) == 0 and den_poly.eval(R(1, 2)) > 0)

ivs = [(sp.Rational(x), sp.Rational(y)) for (x, y), k in
       num_poly.intervals(inf=lo_end, sup=hi_end, eps=R(1, 10**12))]
print(f"   {len(ivs)} real root(s) of the numerator in (0,1), isolated in {time.time() - t0:.1f}s")
for (x, y) in ivs:
    print(f"      s_* in ({sp.N(x, 12)}, {sp.N(y, 12)}), "
          f"t_* in ({sp.N(-N * sp.log(y), 12)}, {sp.N(-N * sp.log(x), 12)})")
check("4 exactly two roots of the numerator in (0,1)", len(ivs) == 2)
check("4' the root at s = 1 (t = 0, equal mean rates) is simple: numerator vanishes, derivative does not",
      num_poly.eval(1) == 0 and num_poly.diff().eval(1) != 0)

# Sign pattern at exact rational points: s = 483/500 is t = -40 log(0.966) = 1.383..., near log 4.
s_mid = R(483, 500)
val_mid = diff.subs(s, s_mid)
check("5 hazard difference positive at s = 483/500 (t about 1.38)", val_mid > 0)
check("6 hazard difference negative at s = 999/1000 (small t) and at s = 1/2 (t about 27.7)",
      diff.subs(s, R(999, 1000)) < 0 and diff.subs(s, R(1, 2)) < 0)
check("6' consistency: the two isolating intervals separate the three sample points",
      ivs[0][1] < R(1, 2) or (R(1, 2) < ivs[0][0] and ivs[0][1] < s_mid < ivs[1][0] and ivs[1][1] < R(999, 1000)))

sdiff = sp.cancel(survival(lam) - survival(gam))
sd_num = sp.Poly(sp.expand(sp.fraction(sdiff)[0]), s)
check("7 S_lambda > S_gamma on (0,1): numerator has no root in (0,1) and is positive at s = 1/2",
      len(sd_num.intervals(inf=lo_end, sup=hi_end)) == 0 and sdiff.subs(s, R(1, 2)) > 0)

# Limits at the ends: h(0) = 3 for both; h(oo) = 1 for lambda, 41/40 for gamma.
t = sp.Symbol("t", positive=True)
hl_t = hazard(lam).subs(s, sp.exp(-t / N))
hg_t = hazard(gam).subs(s, sp.exp(-t / N))
check("8 h_lambda(0) = h_gamma(0) = 3", sp.limit(hl_t, t, 0) == 3 and sp.limit(hg_t, t, 0) == 3)
check("9 h_lambda(oo) = 1 < 41/40 = h_gamma(oo)",
      sp.limit(hl_t, t, sp.oo) == 1 and sp.limit(hg_t, t, sp.oo) == R(41, 40))
var = lambda v: sum(x * x for x in v) / R(3) - (sum(v) / R(3))**2
check("10 Var(lambda) = 8/3 > Var(gamma), so h_lambda < h_gamma near t = 0",
      var(lam) == R(8, 3) and var(gam) < R(8, 3))
print("   Var(gamma) =", var(gam))

failed = [name for name, ok in RESULTS if not ok]
print(f"\n{len(RESULTS) - len(failed)} passed, {len(failed)} failed")
sys.exit(1 if failed else 0)
