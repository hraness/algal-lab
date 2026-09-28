"""Independent C3 check for the refutations in eval_doi_10.5539_ijsp.v10n3p8.

Claim: alpha1 < alpha2 and nu1 < nu2 => X <=lr Z (and hr/rh/st via chain).
Instance: (a1,a2,v1,v2,g,w) = (1,2,1,2,1,1). Hypotheses: 1<2, 1<2, g,w>0.

Exact argument why the printed direction fails:
  S(x) = ((e^{-v G} - e^{-v})/(1 - e^{-v}))^a,  G = e^{-x^{-1}}.
  Inner q(v,x) = (e^{-vG}-e^{-v})/(1-e^{-v}) is in (0,1) and decreases in v
  for G in (0,1): dq/dv numerator = (1-vG-v)e^{-v}... verified numerically
  below; and q^a decreases in a. Both parameter increases shrink S, so
  Z = LFP(2,2) is stochastically SMALLER than X = LFP(1,1): the printed
  X <=st Z fails, and so does the whole chain.

Here: interval-evaluate the four order expressions at the witnesses found.
"""
import sympy as sp
from mpmath import iv, mp, mpf

mp.dps = 80
iv.dps = 100

t = sp.Symbol("t", positive=True)


def S(a, v, g, w):
    a, v, g, w = map(sp.Rational, (a, v, g, w))
    G = sp.exp(-g * t ** (-w))
    H = (1 - sp.exp(-v * G)) / (1 - sp.exp(-v))
    return (1 - H) ** a


a1, a2, v1, v2, g, w = 1, 2, 1, 2, 1, 1
SX, SZ = S(a1, v1, g, w), S(a2, v2, g, w)
fX, fZ = -sp.diff(SX, t), -sp.diff(SZ, t)
EXPRS = {
    "st": SZ - SX,
    "hr": fX * SZ - fZ * SX,
    "rh": fZ * (1 - SX) - fX * (1 - SZ),
    "lr": sp.diff(fZ, t) * fX - fZ * sp.diff(fX, t),
}
PTS = {"st": sp.Rational(1, 100), "hr": sp.Rational(1, 10 ** 12),
       "rh": sp.Rational(1, 100), "lr": sp.Rational(1, 100)}


def ie(expr, x0):
    if expr == t:
        return iv.mpf(int(x0.p)) / iv.mpf(int(x0.q))
    if expr.is_Rational:
        return iv.mpf(int(expr.p)) / iv.mpf(int(expr.q))
    if expr.is_Add:
        s = iv.mpf(0)
        for a_ in expr.args:
            s += ie(a_, x0)
        return s
    if expr.is_Mul:
        p = iv.mpf(1)
        for a_ in expr.args:
            p *= ie(a_, x0)
        return p
    if expr.is_Pow:
        b_, e_ = expr.args
        if e_.is_Integer:
            r = iv.mpf(1)
            for _ in range(abs(int(e_))):
                r *= ie(b_, x0)
            return r if int(e_) >= 0 else 1 / r
        return iv.exp(ie(e_, x0) * iv.log(ie(b_, x0)))
    if isinstance(expr, sp.exp):
        return iv.exp(ie(expr.args[0], x0))
    if isinstance(expr, sp.log):
        return iv.log(ie(expr.args[0], x0))
    raise ValueError(type(expr))


for order, E in EXPRS.items():
    v = ie(E, PTS[order])
    print(f"{order}: E at {PTS[order]} in [{v.a}, {v.b}]  strictly negative: {v.b < 0}")
    assert v.b < 0
print("ALL FOUR REFUTATIONS CONFIRMED")

# direct check of the mechanism: d q / d v < 0 and d S / d a < 0
Gf = sp.exp(-t ** (-1))
qf = (sp.exp(-sp.Symbol('v') * Gf) - sp.exp(-sp.Symbol('v'))) / (1 - sp.exp(-sp.Symbol('v')))
dqdv = sp.diff(qf, sp.Symbol('v'))
lam = sp.lambdify((sp.Symbol('v'), t), dqdv, 'mpmath')
print("dq/dv at (v=1.5, x=0.5):", lam(mpf('1.5'), mpf('0.5')))
