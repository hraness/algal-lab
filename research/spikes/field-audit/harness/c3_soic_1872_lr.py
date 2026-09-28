"""Independent C3 check for the refuted printed direction in
doi:10.19139/soic-2310-5070-1872 (TL-TIIEHL-MO-G), claim "X2 <lr X1".

Instance: b1=1, b2=2, alpha=1, delta=1, baseline Gbar = exp(-x).
Then M = e^{-x}, h = (e^{-x}/(2 - e^{-x}))^2, S_b = 1 - (1 - h)^b.

Printed claim: X2 <=lr X1 requires E = f_{X1}' f_{X2} - f_{X1} f_{X2}' >= 0.
In fact f_{X1}/f_{X2} = (b1/b2)(1-h)^{b1-b2} with 1-h strictly increasing
and b1-b2 < 0, so the ratio is strictly DECREASING: X1 <lr X2 and the
printed direction fails. Verified below by interval evaluation of E at
x = 1/1000000000000 plus an exact sign argument.
"""
import sympy as sp
from mpmath import iv, mp, mpf

mp.dps = 80
iv.dps = 80

t = sp.Symbol("t", positive=True)
M = sp.exp(-t)
h = (M / (2 - M)) ** 2
S1 = 1 - (1 - h) ** 1
S2 = 1 - (1 - h) ** 2
f1, f2 = -sp.diff(S1, t), -sp.diff(S2, t)
E = sp.diff(f1, t) * f2 - f1 * sp.diff(f2, t)   # X2 <=lr X1 needs E >= 0

x0 = sp.Rational(1, 10 ** 12)


def ie(expr):
    if expr == t:
        return iv.mpf(int(x0.p)) / iv.mpf(int(x0.q))
    if expr.is_Rational:
        return iv.mpf(int(expr.p)) / iv.mpf(int(expr.q))
    if expr.is_Add:
        s = iv.mpf(0)
        for a in expr.args:
            s += ie(a)
        return s
    if expr.is_Mul:
        p = iv.mpf(1)
        for a in expr.args:
            p *= ie(a)
        return p
    if expr.is_Pow:
        b_, e_ = expr.args
        if e_.is_Integer:
            r = iv.mpf(1)
            for _ in range(abs(int(e_))):
                r *= ie(b_)
            return r if int(e_) >= 0 else 1 / r
        return iv.exp(ie(e_) * iv.log(ie(b_)))
    if isinstance(expr, sp.exp):
        return iv.exp(ie(expr.args[0]))
    raise ValueError(type(expr))


v = ie(E)
print("iv enclosure of E at x=1e-12:", v)
assert v.b < 0
print("REFUTATION CONFIRMED for printed direction X2 <=lr X1")

# exact argument: f1/f2 = (1/2)(1-h)^{-1}; 1-h strictly increasing =>
# f1/f2 strictly decreasing => X1 <lr X2 (corrected direction), so the
# printed claim cannot hold (the ratio would have to be increasing).
ratio = sp.simplify(f2 / f1)
print("f2/f1 =", ratio)
print("d/dx(f2/f1) sign at x=0.5 (mp):",
      sp.lambdify(t, sp.diff(ratio, t), "mpmath")(mpf("0.5")))
