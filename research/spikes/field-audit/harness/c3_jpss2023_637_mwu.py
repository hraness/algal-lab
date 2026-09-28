"""Independent C3 check for refutations in eval_doi_10.37119_jpss2023.v21i1.637.

MWU(a,lam): S = (1 - lam x)^{a+1} on [0, 1/lam].

Part (i), instance a1=0, a2=1, lam=1 (hypothesis a1<a2 holds):
  f_X = 1, f_Y = 2(1-x) on (0,1).  E_lr = f_Y' f_X - f_Y f_X' = -2 < 0
  for ALL x -> X >=lr Y; the printed X <=lr Y fails. Closed form.
  Similarly E_hr and E_st evaluated at x = 1/2 below.

Part (ii), instance a=1, lam1=1, lam2=2 (hypothesis lam2>lam1 holds):
  f_X = 2(1-x), f_Y = 4(1-2x) on (0,1/2).
  E_lr = -16(1-x) + 8(1-2x) = -8 < 0 identically; checks below confirm.
"""
import sympy as sp
from mpmath import iv

iv.dps = 80
t = sp.Symbol("t", positive=True)


def ie(expr, x0):
    if expr == t:
        return iv.mpf(int(x0.p)) / iv.mpf(int(x0.q))
    if expr.is_Rational:
        return iv.mpf(int(expr.p)) / iv.mpf(int(expr.q))
    if expr.is_Add:
        s = iv.mpf(0)
        for a in expr.args:
            s += ie(a, x0)
        return s
    if expr.is_Mul:
        p = iv.mpf(1)
        for a in expr.args:
            p *= ie(a, x0)
        return p
    if expr.is_Pow:
        b_, e_ = expr.args
        if e_.is_Integer:
            r = iv.mpf(1)
            for _ in range(abs(int(e_))):
                r *= ie(b_, x0)
            return r if int(e_) >= 0 else 1 / r
        return iv.exp(ie(e_, x0) * iv.log(ie(b_, x0)))
    raise ValueError(type(expr))


def report(name, E, pts):
    for pt in pts:
        v = ie(E, sp.Rational(pt))
        print(f"{name}: E({pt}) in [{v.a}, {v.b}]  negative: {v.b < 0}")
        assert v.b < 0


# part (i): X = MWU(0,1) uniform on (0,1); Y = MWU(1,1)
SX1 = (1 - t) ** 1
SY1 = (1 - t) ** 2
fX1, fY1 = -sp.diff(SX1, t), -sp.diff(SY1, t)
report("i-lr", sp.diff(fY1, t) * fX1 - fY1 * sp.diff(fX1, t), ["1/2"])
report("i-hr", fX1 * SY1 - fY1 * SX1, ["1/2"])
report("i-st", SY1 - SX1, ["1/2"])
print("part (i): a1=0 < a2=1, lam=1 -- printed X<=lr/hr/st Y all fail")

# part (ii): X = MWU(1,1) on (0,1); Y = MWU(1,2) on (0,1/2); compare on (0,1/2)
SX2 = (1 - t) ** 2
SY2 = (1 - 2 * t) ** 2
fX2, fY2 = -sp.diff(SX2, t), -sp.diff(SY2, t)
E_lr2 = sp.simplify(sp.diff(fY2, t) * fX2 - fY2 * sp.diff(fX2, t))
print("part (ii) lr expression:", E_lr2)
report("ii-lr", E_lr2, ["1/4"])
report("ii-hr", fX2 * SY2 - fY2 * SX2, ["1/4"])
report("ii-st", SY2 - SX2, ["1/4"])
print("ALL REFUTATIONS CONFIRMED")
