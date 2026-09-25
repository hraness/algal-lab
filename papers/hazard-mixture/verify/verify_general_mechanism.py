#!/usr/bin/env python
"""Symbolic verification of the common-slow-component mechanism.

Survival functions (t > 0, parameters a > 0, d > 0, b - d > a, 0 < w < 1):
    S_X(t) = w e^{-a t} + (1 - w) e^{-b t} cosh(d t)
    S_Y(t) = w e^{-a t} + (1 - w) e^{-b t}
X is the mixture with weights (w, (1-w)/2, (1-w)/2) and rates (a, b-d, b+d);
Y is the mixture with the same weights and rates (a, b, b).

Claims checked exactly with sympy:
  1. R = S_X/S_Y = 1 + (1-w)(cosh(dt) - 1)/(w e^{ct} + 1 - w), c = b - a.
  2. h_X - h_Y = -(log R)'.
  3. (log(R - 1))' = d coth(dt/2) - c w e^{ct}/(w e^{ct} + 1 - w).
  4. d coth(dt/2) is strictly decreasing (derivative -d^2/(2 sinh^2(dt/2))),
     c w e^{ct}/(w e^{ct} + 1 - w) is strictly increasing
     (derivative c^2 w (1-w) e^{ct}/(w e^{ct} + 1 - w)^2), with the stated limits.
  5. With w = 0: h_X = b - d tanh(dt) <= b = h_Y.
  6. Specialisation a = 1, b = 4, d = 1, w = m/(m+2) is the padded family, and the
     zero of (log(R-1))' is the root of B_m(q) = m(1-2q) - q^3(1+q), q = e^{-t}.
"""
import sys

import sympy as sp

t, a, b, d, w, c, m = sp.symbols("t a b d w c m", positive=True)
q = sp.Symbol("q", positive=True)
RESULTS = []


def check(name, condition):
    ok = bool(condition)
    RESULTS.append((name, ok))
    print(("PASS " if ok else "FAIL ") + name)


def is_zero(expr):
    """Exact zero test for expressions in exp, cosh, sinh, coth, tanh."""
    e = sp.expand(sp.powsimp(sp.expand(expr.rewrite(sp.exp)), force=True))
    e = sp.cancel(sp.together(e))
    return sp.simplify(e) == 0


SX = w * sp.exp(-a * t) + (1 - w) * sp.exp(-b * t) * sp.cosh(d * t)
SY = w * sp.exp(-a * t) + (1 - w) * sp.exp(-b * t)
R_ratio = SX / SY
R_claim = 1 + (1 - w) * (sp.cosh(d * t) - 1) / (w * sp.exp(c * t) + 1 - w)

check("1 survival ratio identity (with c = b - a)",
      is_zero(R_ratio - R_claim.subs(c, b - a)))
check("1' R - 1 > 0: numerator factors cosh(dt) - 1 > 0 and 1 - w > 0, denominator > 0",
      sp.simplify(sp.cosh(d * t) - 1 - 2 * sp.sinh(d * t / 2)**2) == 0)

hX = -sp.diff(SX, t) / SX
hY = -sp.diff(SY, t) / SY
check("2 h_X - h_Y = -(log R)'", is_zero(hX - hY + sp.diff(sp.log(R_ratio), t)))

F = sp.diff(sp.log(R_claim - 1), t)
F_claim = d * sp.coth(d * t / 2) - c * w * sp.exp(c * t) / (w * sp.exp(c * t) + 1 - w)
check("3 derivative of log(R - 1)", is_zero(F - F_claim))

check("4a d/dt [d coth(dt/2)] = -d^2 / (2 sinh^2(dt/2))",
      is_zero(sp.diff(d * sp.coth(d * t / 2), t) + d**2 / (2 * sp.sinh(d * t / 2)**2)))
G = c * w * sp.exp(c * t) / (w * sp.exp(c * t) + 1 - w)
check("4b d/dt [c w e^{ct}/(w e^{ct} + 1 - w)] = c^2 w (1-w) e^{ct}/(w e^{ct} + 1 - w)^2",
      is_zero(sp.diff(G, t) - c**2 * w * (1 - w) * sp.exp(c * t) / (w * sp.exp(c * t) + 1 - w)**2))
check("4c limits: d coth(dt/2) -> oo at 0+, -> d at oo",
      sp.limit(d * sp.coth(d * t / 2), t, 0, "+") == sp.oo
      and sp.limit(d * sp.coth(d * t / 2), t, sp.oo) == d)
check("4d limits: G -> c w at 0+, -> c at oo",
      sp.simplify(sp.limit(G, t, 0, "+") - c * w) == 0 and sp.limit(G, t, sp.oo) == c)

hX0 = (-sp.diff(SX, t) / SX).subs(w, 0)
check("5 with w = 0, h_X = b - d tanh(dt)", is_zero(hX0 - (b - d * sp.tanh(d * t))))
check("5' with w = 0, h_Y = b", sp.simplify((-sp.diff(SY, t) / SY).subs(w, 0) - b) == 0)

# 6. Specialisation to the padded family.
spec = {a: 1, b: 4, d: 1, w: m / (m + 2)}
SX_spec = SX.subs(spec)
padded = (m * sp.exp(-t) + sp.exp(-3 * t) + sp.exp(-5 * t)) / (m + 2)
check("6a S_X with (a,b,d,w) = (1,4,1,m/(m+2)) is the padded survival function",
      is_zero(SX_spec - padded))
check("6b S_Y with the same parameters is the padded comparison survival function",
      is_zero(SY.subs(spec) - (m * sp.exp(-t) + 2 * sp.exp(-4 * t)) / (m + 2)))
F_spec = F_claim.subs(c, b - a).subs(spec)
# coth(t/2) = (1 + q)/(1 - q) and e^{3t} = q^{-3} with q = e^{-t}
F_in_q = (1 + q) / (1 - q) - 3 * (m / (m + 2)) * q**-3 / ((m / (m + 2)) * q**-3 + 2 / (m + 2))
check("6c F in the variable q = e^{-t}", is_zero(F_spec.subs(t, -sp.log(q)) - F_in_q))
Bm = m * (1 - 2 * q) - q**3 * (1 + q)
check("6d numerator of F(q) is -2 B_m(q)/((1-q)(m + 2 q^3)) up to the stated positive factors",
      sp.cancel(F_in_q + 2 * Bm / ((1 - q) * (m + 2 * q**3))) == 0)
check("6e antiordering of weights needs w >= 1/3, i.e. m >= 1",
      sp.solve(sp.Eq(m / (m + 2), sp.Rational(1, 3)), m) == [1])
check("6f hypothesis b - d > a holds: 4 - 1 > 1", 4 - 1 > 1)

failed = [name for name, ok in RESULTS if not ok]
print(f"\n{len(RESULTS) - len(failed)} passed, {len(failed)} failed")
sys.exit(1 if failed else 0)
