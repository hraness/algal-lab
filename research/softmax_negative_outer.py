"""Exact witnesses for nested softmax allocation at negative outer temperature.

Companion to ``docs/softmax-negative-outer.md``. Column entries are multiples
of ``1/denominator`` and ``root`` is the exact rational value of
``exp(t/denominator)``, so every column score is an exact ``Fraction``.
Outer rewards at finite negative temperature use ``Decimal`` arithmetic.
"""

from __future__ import annotations

from decimal import ROUND_CEILING, Decimal, localcontext
from fractions import Fraction
from functools import lru_cache
from itertools import product

__all__ = [
    "balanced_pure",
    "binary_allocations",
    "bottleneck",
    "column_score",
    "crumb_threshold_ok",
    "fractional_threshold",
    "grid_allocations",
    "is_balanced_pure",
    "mean_score",
    "occupancy_score",
    "outer_reward",
    "spread_witness",
]


def _exponent(entry: Fraction, denominator: int) -> int:
    scaled = Fraction(entry) * denominator
    if scaled.denominator != 1:
        raise ValueError(f"entry {entry} is not a multiple of 1/{denominator}")
    if not 0 <= scaled <= denominator:
        raise ValueError(f"entry {entry} is outside [0, 1]")
    return int(scaled)


def _rational(value) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise TypeError(f"expected an int or Fraction, got {type(value).__name__}")
    return Fraction(value)


def to_decimal(value) -> Decimal:
    """Convert a Fraction or Decimal-compatible value under the active context."""
    if isinstance(value, Fraction):
        return Decimal(value.numerator) / Decimal(value.denominator)
    return Decimal(value)


def column_score(column, root, denominator: int) -> Fraction:
    """Exact ``f_t(x)`` with ``exp(t x_i) = root ** (x_i * denominator)``."""
    return _column_score(tuple(Fraction(x) for x in column), _rational(root), int(denominator))


@lru_cache(maxsize=None)
def _column_score(column, root: Fraction, denominator: int) -> Fraction:
    if not column:
        raise ValueError("column must have at least one entry")
    weights = [root ** _exponent(x, denominator) for x in column]
    total = sum(weights, Fraction(0))
    return sum((Fraction(x) * w for x, w in zip(column, weights)), Fraction(0)) / total


def occupancy_score(k: int, n: int, exponential) -> Fraction:
    """``s_k = kE / (N + k(E-1))``: score of a column with ``k`` unit entries."""
    e = _rational(exponential)
    return Fraction(k) * e / (n + k * (e - 1))


def balanced_pure(n: int, m: int):
    """A balanced pure allocation: agent ``i`` works on task ``i mod m``."""
    return tuple(tuple(int(j == i % m) for j in range(m)) for i in range(n))


def is_balanced_pure(matrix, n: int, m: int) -> bool:
    """Whether ``matrix`` is binary, one unit per row, with occupancies ``q`` and ``q+1``."""
    q, r = divmod(n, m)
    if len(matrix) != n or any(len(row) != m for row in matrix):
        return False
    if any(any(entry not in (0, 1) for entry in row) or sum(row) != 1 for row in matrix):
        return False
    counts = sorted(sum(row[j] for row in matrix) for j in range(m))
    return counts == [q] * (m - r) + [q + 1] * r


def spread_witness(n: int, m: int):
    """The spread construction: ``qM`` full agents, ``r`` agents spread over groups."""
    q, r = divmod(n, m)
    if r == 0:
        raise ValueError("spread witness requires M not dividing N")
    rows = []
    for j in range(m):
        for _ in range(q):
            rows.append(tuple(Fraction(int(k == j)) for k in range(m)))
    base, extra = divmod(m, r)
    start = 0
    for group in range(r):
        size = base + (1 if group < extra else 0)
        members = range(start, start + size)
        rows.append(tuple(Fraction(1, size) if k in members else Fraction(0) for k in range(m)))
        start += size
    assert start == m and len(rows) == n
    return tuple(rows)


def _columns(matrix, m: int):
    return [tuple(row[j] for row in matrix) for j in range(m)]


def bottleneck(matrix, root, denominator: int) -> Fraction:
    """``min_j f_t(A_{:j})``, the bottleneck reward."""
    m = len(matrix[0])
    return min(column_score(col, root, denominator) for col in _columns(matrix, m))


def mean_score(matrix, root, denominator: int) -> Fraction:
    """``R_0``, the arithmetic mean of the column scores."""
    m = len(matrix[0])
    return sum((column_score(col, root, denominator) for col in _columns(matrix, m)), Fraction(0)) / m


def outer_reward(scores, tau, precision: int = 50) -> Decimal:
    """``R_tau`` of a score vector in Decimal arithmetic at the given precision."""
    with localcontext() as context:
        context.prec = precision
        tau = to_decimal(tau)
        values = [to_decimal(s) for s in scores]
        weights = [(tau * v).exp() for v in values]
        return sum(v * w for v, w in zip(values, weights)) / sum(weights)


def fractional_threshold(delta, m: int, precision: int = 50) -> Decimal:
    """``-2(M-1)/(e delta)``: below this every maximizer is fractional."""
    with localcontext() as context:
        context.prec = precision
        return -Decimal(2 * (m - 1)) / (Decimal(1).exp() * to_decimal(delta))


def _row_options(m: int, denominator: int):
    steps = range(denominator + 1)
    for row in product(steps, repeat=m):
        if sum(row) <= denominator:
            yield tuple(Fraction(x, denominator) for x in row)


def grid_allocations(n: int, m: int, denominator: int):
    """All allocations with entries in multiples of ``1/denominator`` and row sums at most one."""
    options = list(_row_options(m, denominator))
    for rows in product(options, repeat=n):
        yield rows


def binary_allocations(n: int, m: int):
    """All binary allocations (each row has at most one unit entry)."""
    options = [tuple(int(j == k) for j in range(m)) for k in range(m + 1)]
    for rows in product(options, repeat=n):
        yield rows


def crumb_threshold_ok(n: int, m: int, exponential, t, precision: int = 50) -> bool:
    """Whether ``t * s_q <= 1`` holds.

    ``t`` is a Decimal approximation of the inner temperature; the product is
    rounded upward, so ``True`` certifies the inequality up to the accuracy of
    ``t`` itself, and an exact boundary case is reported as ``False``.
    """
    q = n // m
    s = occupancy_score(q, n, exponential)
    with localcontext() as context:
        context.prec = precision
        context.rounding = ROUND_CEILING
        return to_decimal(t) * to_decimal(s) <= 1
