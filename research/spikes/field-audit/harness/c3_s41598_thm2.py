"""C3 for doi:10.1038/s41598-026-45633-8, Theorem 2 refutation.

Log-LFR(alpha,beta,p): S(x) = ln(1-(1-p) e^{-a x - b x^2/2}) / ln p.
Series min of n components: S_min = prod S_i.

EXACT argument:  S_i'(0) = (1-p) a_i / (p ln p)  (from -Fbar'(0) = a_i).
  Hence S_min'(0) = (1-p)/(p ln p) * sum a_i  and
    (S_min^Y - S_min^X)'(0) = (1-p)/(p ln p) * (sum a*_i - sum a_i).
  For 0 < p < 1 the factor (1-p)/(p ln p) < 0; the hypothesis
  sum a*_i > sum a_i therefore forces the difference NEGATIVE for small x:
  the claimed order X_{1:n} <=st Y_{1:n} fails near 0.

Numerical check at the interval witness x = 1e-12 with panel-(a) parameters,
300-digit mpmath (independent of the iv pipeline).
"""
import sympy as sp
from mpmath import mp, mpf, exp, log

mp.dps = 300

# ---- exact leading coefficient ----
p = sp.Rational(3, 10)          # printed p = 0.3
a = sp.Symbol('a', positive=True)
xx = sp.Symbol('x', positive=True)
Fbar = sp.exp(-a * xx)          # b x^2/2 term contributes O(x^2)
S = sp.log(1 - (1 - p) * Fbar) / sp.log(p)
S0prime = sp.simplify(sp.diff(S, xx).subs(xx, 0))
print("S'(0) =", S0prime)       # expect (1-p)*a/(p*ln p)

sumA = sp.Rational(1, 2) + 1 + sp.Rational(3, 2)          # alpha of X panel (a)
sumB = 2 + sp.Rational(5, 2) + 3                        # alpha* of Y
coef = sp.simplify(S0prime.subs(a, 1))                  # common factor
lead = sp.simplify(coef * (sumB - sumA))
print("leading coeff of S_Y - S_X:", lead, "=", sp.N(lead, 20))
assert lead.is_negative                                 # exact negative

# ---- direct 300-digit evaluation at witness ----
def S_llfr(al, be, pv, xv):
    pv, al, be, xv = mpf(pv), mpf(al), mpf(be), mpf(xv)
    return log(1 - (1 - pv) * exp(-al * xv - be * xv ** 2 / 2)) / log(pv)


aX = (mpf("0.5"), mpf(1), mpf("1.5"))
aY = (mpf(2), mpf("2.5"), mpf(3))
bX = (mpf("0.1"), mpf("0.3"), mpf("0.5"))
bY = (mpf("0.2"), mpf("0.4"), mpf("0.6"))
pv = mpf("0.3")
x0 = mpf(10) ** (-12)
SX = mpf(1)
SY = mpf(1)
for i in range(3):
    SX *= S_llfr(aX[i], bX[i], pv, x0)
    SY *= S_llfr(aY[i], bY[i], pv, x0)
d = SY - SX
print("S_Y - S_X at x=1e-12:", mp.nstr(d, 20))
assert d < 0
print("VERDICT: Theorem 2 fails at x=1e-12 (strict), also proved by the "
      "exact negative leading coefficient")
