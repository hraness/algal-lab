"""C3 for doi:10.1007/s40745-019-00211-w, Section 3.4 theorem.

Claim: X ~ IXGD(theta1), Y ~ IXGD(theta2), theta1 > theta2 => X <=lr Y.

Independent refutation: for theta1=2, theta2=1,
  f_X/f_Y = C * ((x^2+1)/(x^2+1/2)) * e^{-1/x}, so
  d/dx log(f_X/f_Y) = 1/x^2 - x/((x^2+1)(x^2+1/2)).
Its sign is that of P(x) = 2x^4 - 2x^3 + 3x^2 + 1 > 0 for all x > 0
(checked exactly: no positive roots and P(0)=1>0).  Hence f_X/f_Y is
strictly increasing, i.e. X >=lr Y (strictly), so X <=lr Y fails
everywhere: e.g. at x=1/10 and x=1 the order expression is strictly
negative (interval-verified).
"""
import sympy as sp
from mpmath import iv
import auditlib as A

x = A.x


def main():
    P = 2 * x ** 4 - 2 * x ** 3 + 3 * x ** 2 + 1
    poly = sp.Poly(P, x)
    nroots = sp.polys.polytools.count_roots(poly, 0, sp.oo)
    print("positive roots of P:", nroots, " P(0) =", P.subs(x, 0))
    assert nroots == 0 and P.subs(x, 0) > 0
    print("=> f_X/f_Y strictly increasing on (0,oo): X >=lr Y strictly.")

    # numeric cross-check of E_lr = f_Y' f_X - f_Y f_X' < 0 at two points
    SX = A.ixgd_surv(sp.Rational(2))
    SY = A.ixgd_surv(sp.Rational(1))
    fX = -sp.diff(SX, x)
    fY = -sp.diff(SY, x)
    E_lr = sp.diff(fY, x) * fX - fY * sp.diff(fX, x)
    iv.dps = 80
    for pt in [sp.Rational(1, 10), sp.Rational(1), sp.Rational(3)]:
        val = A.cf.iv_eval(E_lr, pt)
        print(f"E_lr({pt}) in {val}   upper<0: {val.b < 0}")


if __name__ == "__main__":
    main()
