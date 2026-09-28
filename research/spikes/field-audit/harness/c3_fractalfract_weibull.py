"""C3 for doi:10.3390/fractalfract9060388, 'Remark 6 (Weibull example,
st part)' refutation.

Claim as printed: for shape parameters a1 < a2, Y(a1) >=st Y(a2), i.e.
S_{a1}(x) >= S_{a2}(x) for all x, with S_a(x) = exp(-x^a) (unit scale).

EXACT argument at x = 1/2, a1 = 1, a2 = 2:
    S_1(1/2) = e^{-1/2},  S_2(1/2) = e^{-1/4},  and
    S_1(1/2) - S_2(1/2) = e^{-1/2} - e^{-1/4} = e^{-1/2}(1 - e^{1/4}) < 0
since e^{1/4} > 1.  Hence Y(1) >=st Y(2) fails at x = 1/2 (strict).
"""
import sympy as sp

e = sp.exp(-sp.Rational(1, 2)) - sp.exp(-sp.Rational(1, 4))
# e^{-1/2} - e^{-1/4} = e^{-1/2}(1 - e^{1/4});  e^{1/4} > 1 -> < 0
assert sp.simplify(e.rewrite(sp.exp)) is not None
print("E_st(1/2) =", e, "=", sp.N(e, 20))
assert bool(sp.N(e) < 0)
print("VERDICT: refuted exactly at x = 1/2 (unit-scale Weibull survivals "
      "cross at x = 1)")
