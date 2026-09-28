"""Independent C3 check for the refuted lr claim in doi:10.35914/mathstat.v2i1.180.

Exact (non-interval) evaluation: E(x) = fY'(x) fX(x) - fY(x) fX'(x) is computed
symbolically with sympy, then evaluated exactly at rational points. For
X <=lr Y we need fY/fX increasing, i.e. E >= 0. Exact E < 0 refutes.

Instance (lam,th)=(1,2) for X, (beta,alpha)=(3,4) for Y satisfies BOTH printed
hypothesis readings: lam<alpha (1<4), th<beta (2<3), lam<beta (1<3), th<alpha (2<4).
"""
import sympy as sp

x = sp.Symbol("x", positive=True)
R = sp.Rational


def S_mgs(lam, th):
    lam, th = R(lam), R(th)
    return (sp.exp(-th * x) / (lam + 1)
            * (lam * (1 + th * x + th ** 2 * x ** 2 / 2)
               + (th ** 2 + th * x + 1) / (th ** 2 + 1)))


fX = -sp.diff(S_mgs(1, 2), x)
fY = -sp.diff(S_mgs(3, 4), x)
E = sp.simplify(sp.diff(fY, x) * fX - fY * sp.diff(fX, x))
for pt in [R(0), R(1, 10 ** 12), R(1, 10 ** 6), R(1, 1000)]:
    print("E(%s) =" % pt, sp.N(E.subs(x, pt), 20))
# Also the exact value at x=0 (closed form): (1/th - th) - (1/al - al) factor
print("E(0) exact =", sp.simplify(E.subs(x, 0)))
print("fX(0)=", sp.simplify(fX.subs(x, 0)), " fY(0)=", sp.simplify(fY.subs(x, 0)))
