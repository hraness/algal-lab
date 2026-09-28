"""Independent C3 check: doi:10.29020/nybg.ejpam.v18i4.6653 Theorem 1.

M(theta): f(x) = th^3 x (1 + x/2) e^{-th x}/(1+th).  With th1 < th2:
f2/f1 = (th2/th1)^3 (1+th1)/(1+th2) e^{-(th2-th1)x} is strictly DECREASING,
so X1 <=lr X2 fails for every pair with th1<th2 (in fact X2 <=lr X1 holds:
larger rate = lighter tail).  Exact symbolic evaluation of each order's E.
"""
import sympy as sp

x = sp.Symbol("x", positive=True)
R = sp.Rational


def S(th):
    th = R(th)
    return (sp.exp(-th * x) / (1 + th)
            * (th * (1 + th * x) + (1 + th * x + th ** 2 * x ** 2 / 2)))


t1, t2 = R(1), R(2)
SX, SY = S(t1), S(t2)
fX, fY = -sp.diff(SX, x), -sp.diff(SY, x)

# sanity: survival at 0
print("S(0) =", sp.simplify(SX.subs(x, 0)), sp.simplify(SY.subs(x, 0)))

exprs = {
    "st": SY - SX,                                        # X <=st Y needs >=0
    "hr": fX * SY - fY * SX,                              # X <=hr Y needs >=0
    "lr": sp.diff(fY, x) * fX - fY * sp.diff(fX, x),      # X <=lr Y needs >=0
}
pt = R(1, 10 ** 12)
for name, E in exprs.items():
    v = sp.simplify(E.subs(x, pt))
    print(name, "E(1e-12) exact =", sp.nsimplify(v) if v.is_rational else v,
          "=", sp.N(v, 15))
# analytic limit argument for st/hr:
print("SY-SX at x=1/2:", sp.N((SY - SX).subs(x, R(1, 2)), 15))
