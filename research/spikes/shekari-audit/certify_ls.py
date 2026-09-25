"""Fast Sturm certificate for the LS specialization (dict polynomials).

h(s) = sum p_i lam_i s^{lam_i} / sum p_i s^{lam_i},  s = e^{-t}.
gam = (1/7,1/2,1/2), p = (1/3,1/3,1/3);  T on cols (1,3) w=3/20 ->
gam* = (25/56,1/2,11/56), p* = p;  lam = (7,2,2), lam* = (56/25,2,56/11).
In z = s^{1/275}: exponents 275*lam are integers.
d(z) = h_A - h_B = (N_A D_B - N_B D_A) / (D_A D_B).
"""
import sympy as sp
from sympy import Rational as R
from fractions import Fraction as Fr
from collections import defaultdict

z = sp.Symbol("z", positive=True)
L = 275
lam = [Fr(7), Fr(2), Fr(2)]
lams = [Fr(56, 25), Fr(2), Fr(56, 11)]
p = [Fr(1, 3)] * 3
ps = [Fr(1, 3)] * 3


def poly_dict(p_, la_):
    """N and D as dicts exponent->Fraction."""
    N, D = defaultdict(Fr), defaultdict(Fr)
    for pi, li in zip(p_, la_):
        N[int(L * li)] += pi * li
        D[int(L * li)] += pi
    return dict(N), dict(D)


def mul(a, b):
    out = defaultdict(Fr)
    for ea, ca in a.items():
        for eb, cb in b.items():
            out[ea + eb] += ca * cb
    return dict(out)


def sub(a, b):
    out = dict(a)
    for e, c in b.items():
        out[e] = out.get(e, Fr(0)) - c
    return {e: c for e, c in out.items() if c != 0}


NA, DA = poly_dict(p, lam)
NB, DB = poly_dict(ps, lams)
num = sub(mul(NA, DB), mul(NB, DA))
den = mul(DA, DB)

print("numerator degree:", max(num), "  denominator degree:", max(den))

# exact witnesses via Fraction eval
def peval(dd, v):
    tot = Fr(0)
    for e, c in dd.items():
        tot += c * v ** e
    return tot


print("denominator positive on (0,1): all coeffs >0:",
      all(c > 0 for c in den.values()))
for v in [Fr(1, 2), Fr(7, 8), Fr(9, 10), Fr(15, 16), Fr(19, 20), Fr(39, 40)]:
    nv = peval(num, v)
    print(f"  z={v}: num sign {(nv>0)-(nv<0)}")
    print(f"      (s = z^275 ~ {float(v)**275:.3e})")

# Sturm count on numerator
x = sp.Symbol("x")
P = sp.Poly.from_dict({(e,): sp.Rational(c.numerator, c.denominator)
                       for e, c in num.items()}, x)
print("Sturm roots of numerator in (0,1):", P.count_roots(0, 1))
