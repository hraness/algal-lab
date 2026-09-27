"""Exact order decisions for distributions written in one shared variable z.

A distribution is its survival function S as a rational function of z with
rational coefficients, on an open interval (lo, hi) of z, where z is a strictly
monotone function of t that both compared distributions share. Examples:

  z = s = exp(-t/D), decreasing   exponential mixtures, minima, maxima and
                                  order statistics with rational rates
                                  (rates times D are integers)
  z = t, increasing               polynomial or rational survival functions

Because both sides share z, the positive factor |dz/dt| cancels from every
comparison below, and each order reduces to the sign of one polynomial on
(lo, hi). Signs are decided exactly: real roots are isolated with rational
intervals (sympy's Vincent/Sturm based isolation) and the polynomial is
evaluated exactly between them. A violation comes with a rational witness z0
where the required sign fails.

Orders (X on the left, Y on the right), with S survival, F = 1 - S and
f proportional to -dS/dt:
  st   X <=st Y   S_X <= S_Y
  hr   X <=hr Y   f_X S_Y - f_Y S_X >= 0          (h_X >= h_Y)
  rh   X <=rh Y   f_X F_Y - f_Y F_X <= 0          (r_X <= r_Y)
  lr   X <=lr Y   f_Y / f_X increasing in t
"""
from dataclasses import dataclass
from fractions import Fraction

import sympy as sp

z = sp.Symbol("z", real=True)


@dataclass(frozen=True)
class Dist:
    survival: sp.Expr          # S as a rational function of z
    lo: sp.Rational
    hi: sp.Rational
    increasing: bool           # whether z increases with t

    def density(self):
        """-dS/dt up to the shared positive factor |dz/dt|."""
        d = sp.diff(self.survival, z)
        return sp.together(-d if self.increasing else d)


def exp_mixture(weights, rates, denominator):
    """Mixture of exponentials, S = sum p_i exp(-rate_i t), in s = exp(-t/D)."""
    terms = []
    for p, r in zip(weights, rates):
        k = sp.Rational(r) * denominator
        assert k.is_integer and k > 0, "rates times D must be positive integers"
        terms.append(sp.Rational(p) * z ** int(k))
    return Dist(sp.Add(*terms), sp.Integer(0), sp.Integer(1), increasing=False)


def exp_poly(coefficients_by_exponent):
    """S = sum c_k s^k in s = exp(-t/D), given {k: c_k}."""
    return Dist(sp.Add(*[sp.Rational(c) * z ** int(k) for k, c in coefficients_by_exponent.items()]),
                sp.Integer(0), sp.Integer(1), increasing=False)


def order_statistic_exponentials(rates, k, denominator):
    """Survival of the k-th smallest of independent exponentials, as a polynomial in s."""
    n = len(rates)
    s_i = [z ** int(sp.Rational(r) * denominator) for r in rates]
    F_i = [1 - v for v in s_i]
    # P(X_{k:n} > t) = P(fewer than k of the X_i are <= t)
    total = sp.Integer(0)
    import itertools
    for j in range(k):
        for failed in itertools.combinations(range(n), j):
            term = sp.Integer(1)
            for i in range(n):
                term *= F_i[i] if i in failed else s_i[i]
            total += term
    return Dist(sp.expand(total), sp.Integer(0), sp.Integer(1), increasing=False)


def _numerator(expr):
    num, den = sp.fraction(sp.together(sp.expand(expr)))
    return sp.Poly(sp.expand(num), z), sp.Poly(sp.expand(den), z)




def _interior_negative_near(poly, edge, inner):
    """poly(edge) < 0 and no root strictly between edge and the first root:
    bisect from inner toward edge until a point with poly < 0 appears."""
    x = inner
    for _ in range(400):
        x = (x + edge) / 2
        if poly.eval(x) < 0:
            return x
    raise ArithmeticError("no interior witness found near the edge")


def _separated_intervals(poly, lo, hi):
    """Isolating intervals refined until consecutive ones are strictly apart.

    sympy's isolating intervals are open around irrational roots and may share
    an endpoint with a neighbouring exact root, as in (0,0), (0,1), (1,1);
    refining until b_i < a_{i+1} leaves a gap with a sample point between every
    pair of consecutive roots.
    """
    width = hi - lo
    for k in range(4, 400, 4):
        raw = poly.intervals(inf=lo, sup=hi, eps=width / 2 ** k)
        intervals = sorted((sp.Rational(a), sp.Rational(b)) for (a, b), _m in raw)
        if all(b < a for (_, b), (a, _) in zip(intervals, intervals[1:])):
            return intervals
    raise ArithmeticError("could not separate the isolating intervals")


def _negative_witness(poly, lo, hi):
    """A rational z0 in (lo, hi) with poly(z0) < 0, or None if poly >= 0 there.

    Every open gap between consecutive real roots in (lo, hi) gets one sample:
    the isolating intervals are disjoint and hold one root each, so the midpoint
    of the space between two consecutive intervals lies between their roots, and
    a gap cut off by an interval touching lo or hi takes the sign of poly at that
    endpoint (no root lies between them).
    """
    if poly.is_zero:
        return None
    intervals = _separated_intervals(poly, lo, hi)
    if not intervals:
        mid = (lo + hi) / 2
        return mid if poly.eval(mid) < 0 else None
    a1, b1 = intervals[0]
    if a1 > lo:
        x = (lo + a1) / 2
        if poly.eval(x) < 0:
            return x
    elif poly.eval(lo) < 0:
        return _interior_negative_near(poly, lo, b1)
    for (_, b), (a, _) in zip(intervals, intervals[1:]):
        x = (b + a) / 2
        if lo < x < hi and poly.eval(x) < 0:
            return x
    a_n, b_n = intervals[-1]
    if b_n < hi:
        x = (b_n + hi) / 2
        if poly.eval(x) < 0:
            return x
    elif poly.eval(hi) < 0:
        return _interior_negative_near(poly, hi, a_n)
    return None


def _nonnegative(expr, lo, hi):
    """Is expr >= 0 on (lo, hi)? Returns (holds, witness z0 where expr < 0)."""
    num, den = _numerator(expr)
    if den.count_roots(lo, hi) != 0:
        raise ValueError("denominator vanishes inside the interval")
    if den.eval((lo + hi) / 2) < 0:
        num = -num
    witness = _negative_witness(num, lo, hi)
    return witness is None, witness


def _check(X, Y):
    assert X.lo == Y.lo and X.hi == Y.hi and X.increasing == Y.increasing, "sides must share z"


def st(X, Y):
    """X <=st Y ?"""
    _check(X, Y)
    return _nonnegative(Y.survival - X.survival, X.lo, X.hi)


def hr(X, Y):
    """X <=hr Y ?"""
    _check(X, Y)
    return _nonnegative(X.density() * Y.survival - Y.density() * X.survival, X.lo, X.hi)


def rh(X, Y):
    """X <=rh Y ?"""
    _check(X, Y)
    return _nonnegative(Y.density() * (1 - X.survival) - X.density() * (1 - Y.survival), X.lo, X.hi)


def lr(X, Y):
    """X <=lr Y ?  f_Y/f_X increasing in t."""
    _check(X, Y)
    fX, fY = X.density(), Y.density()
    d = sp.diff(fY, z) * fX - fY * sp.diff(fX, z)      # sign of d/dz (fY/fX) times fX^2
    return _nonnegative(d if X.increasing else -d, X.lo, X.hi)


ORDERS = {"st": st, "hr": hr, "rh": rh, "lr": lr}


def to_fraction(x):
    return Fraction(int(sp.Rational(x).p), int(sp.Rational(x).q))
