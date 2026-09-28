"""C3 for doi:10.11648/j.ijsda.20261201.11 Theorem 9.1 case ii.

Claim: KwEE(a1,b1,lam) vs (a2,b2,lam) with a1<a2, b1<b2 => X <=lr Y (=>hr,st).

Instance a1=b1=1, a2=b2=2, lam=1:  S1 = e^{-x}, S2 = e^{-2x}(2-e^{-x})^2.
In z = e^{-x}: S2/S1 = z(2-z)^2, which crosses 1 at z=1/2 (S2-S1 changes sign),
so even the implied st order fails both ways.  Density-ratio derivative:
  E_lr = f_Y' f_X - f_Y f_X',  evaluated exactly at z = 1/5 and z = 4/5
(rational arithmetic; the sign decides the direction of the lr expression).
"""
import sympy as sp
from fractions import Fraction
import auditlib as A
from ratdist import z

X_SURV = z                      # S1 = z
Y_SURV = z ** 2 * (2 - z) ** 2  # S2 = z^2 (2-z)^2


def eval_at(expr, q):
    return sp.nsimplify(expr.subs(z, sp.Rational(*q.as_integer_ratio())))


def main():
    # st direction: S2 - S1 = z^2(2-z)^2 - z = z( z(2-z)^2 - 1 )
    E_st = sp.expand(Y_SURV - X_SURV)
    print("S2-S1 =", sp.factor(E_st))
    for q in [Fraction(1, 5), Fraction(4, 5), Fraction(9, 10)]:
        print(f"  S2-S1 at z={q}: {sp.N(E_st.subs(z, sp.Rational(q.numerator, q.denominator)), 8)}")
    # lr direction via exact derivatives: f(x) = -dS/dx = z * dS/dz (z = e^{-x});
    # f'(x) = -z d/dz(z S'(z)).  E_lr = f_Y' f_X - f_Y f_X' simplifies to
    # z^3 (S_Y'' S_X' - S_Y' S_X'').
    pX = sp.diff(X_SURV, z)
    pY = sp.diff(Y_SURV, z)
    # E_lr = z^3 (S_Y' S_X'' - S_X' S_Y'')
    E_lr = z ** 3 * (pY * sp.diff(pX, z) - sp.diff(pY, z) * pX)
    E_lr = sp.expand(E_lr)
    print("E_lr =", sp.factor(E_lr))
    for q in [Fraction(1, 5), Fraction(4, 5)]:
        v = E_lr.subs(z, sp.Rational(q.numerator, q.denominator))
        print(f"  E_lr at z={q}: {sp.nsimplify(v)}  ({sp.N(v,8)})")


if __name__ == "__main__":
    main()
