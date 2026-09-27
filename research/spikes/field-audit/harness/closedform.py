"""Rigorous refutation search for closed-form families (protocol amendment 3).

A distribution is a closed-form survival function S(x) in sympy, with every
parameter already replaced by a rational number, on (lo, hi). Each order's
defining expression E(x) must be >= 0 for the claim X <=order Y:

  st   E = S_Y - S_X
  hr   E = f_X S_Y - f_Y S_X
  rh   E = f_Y F_X - f_X F_Y
  lr   E = f_Y' f_X - f_Y f_X'      (f_Y / f_X increasing)

E is evaluated at rational points with mpmath interval arithmetic by walking
the expression tree (numbers enter as exact rational enclosures), so a point
whose enclosure lies strictly below zero is a rigorous counterexample. A claim
with no such point is reported as surviving a bounded search, never as true.
"""
import sympy as sp
from mpmath import iv

x = sp.Symbol("x", positive=True)


def _rat(value):
    value = sp.Rational(value)
    return iv.mpf(int(value.p)) / iv.mpf(int(value.q))


def iv_eval(expr, point):
    """Interval enclosure of expr at x = point (a sympy Rational)."""
    if expr == x:
        return _rat(point)
    if expr.is_Rational:
        return _rat(expr)
    if expr.is_Number:
        raise ValueError("inexact number in expression: %s" % expr)
    if expr.is_Add:
        total = iv.mpf(0)
        for arg in expr.args:
            total += iv_eval(arg, point)
        return total
    if expr.is_Mul:
        product = iv.mpf(1)
        for arg in expr.args:
            product *= iv_eval(arg, point)
        return product
    if expr.is_Pow:
        base, exponent = expr.args
        if exponent.is_Integer:
            b = iv_eval(base, point)
            n = int(exponent)
            result = iv.mpf(1)
            for _ in range(abs(n)):
                result *= b
            return result if n >= 0 else 1 / result
        return iv.exp(iv_eval(exponent, point) * iv.log(iv_eval(base, point)))
    if isinstance(expr, sp.exp):
        return iv.exp(iv_eval(expr.args[0], point))
    if isinstance(expr, sp.log):
        return iv.log(iv_eval(expr.args[0], point))
    if expr == sp.E:
        return iv.exp(iv.mpf(1))
    raise ValueError("unsupported expression node: %s" % type(expr).__name__)


class Closed:
    def __init__(self, survival, lo=0, hi=sp.oo):
        free = survival.free_symbols - {x}
        if free:
            raise ValueError("unsubstituted parameters: %s" % free)
        self.survival = survival
        self.density = -sp.diff(survival, x)
        self.lo, self.hi = sp.Rational(lo), hi


def expression(order, X, Y):
    SX, SY, fX, fY = X.survival, Y.survival, X.density, Y.density
    if order == "st":
        return SY - SX
    if order == "hr":
        return fX * SY - fY * SX
    if order == "rh":
        return fY * (1 - SX) - fX * (1 - SY)
    if order == "lr":
        return sp.diff(fY, x) * fX - fY * sp.diff(fX, x)
    raise ValueError("unsupported order %s" % order)


def resolvable_top(survivals, lo):
    """Smallest x (a dyadic rational) where every survival function is below 1e-40.

    Beyond it the survivals cannot be separated at any working precision, so a
    fixed grid out to a large x would spend its points where nothing can be
    decided; the grid is scaled to this point instead.
    """
    from mpmath import mp, mpf
    mp.dps = 60
    funcs = [sp.lambdify(x, S, modules="mpmath") for S in survivals]
    tiny = mpf(10) ** -40
    small = lambda t: all(abs(f(mpf(t))) < tiny for f in funcs)
    top = sp.Rational(1, 64)
    while top < 10 ** 6 and not small(top):
        top *= 2
    return top


def grid(lo, hi, survivals=()):
    lo = sp.Rational(lo)
    points = [lo + sp.Rational(1, 10 ** k) for k in range(1, 13)]
    if hi == sp.oo:
        top = resolvable_top(survivals, lo) if survivals else sp.Rational(30)
    else:
        top = sp.Rational(hi)
    span = top - lo
    points += [lo + span * sp.Rational(i, 120) for i in range(1, 120)]
    if hi == sp.oo:
        points += [top * 2, top * 4]
    else:
        points += [top - sp.Rational(1, 10 ** k) for k in range(1, 13)]
    return sorted({p for p in points if p > lo and (hi == sp.oo or p < hi)})


def check(order, X, Y, precisions=(60, 150, 400)):
    """(holds_on_grid, witness, undecided_points)."""
    assert X.lo == Y.lo and X.hi == Y.hi, "sides must share the support"
    E = expression(order, X, Y)
    undecided = 0
    for point in grid(X.lo, X.hi, (X.survival, Y.survival)):
        decided = False
        for dps in precisions:
            iv.dps = dps
            value = iv_eval(E, point)
            if value.b < 0:
                return False, point, undecided
            if value.a >= 0:
                decided = True
                break
        undecided += not decided
    return True, None, undecided
