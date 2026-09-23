"""Exact universal four-point tests for four continuous histogram clocks.

The two gaps compare adjacent/crossing/nested pair-inclusion sums. An arbitrary
background population, independent of the quartet, reduces to two thresholds
L <= U. Its conditional gap is D(U) + K(U) - K(L), where K' = C. On common
histogram bins K and D are quadratic. This module minimizes that expression
exactly in O(bins) rational arithmetic operations, with a threshold witness.

This certifies this quartet's two inequalities, not literature priority or an
ordering of a larger population. Counts describe uniform densities within bins.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


Polynomial = tuple[Fraction, Fraction, Fraction]


@dataclass(frozen=True)
class GapMinimum:
    value: Fraction
    lower: Fraction
    upper: Fraction


def _admit(value: object) -> list[list[Fraction]]:
    if type(value) is not list or len(value) != 4:
        raise ValueError("histograms: exactly four rows required")
    bins = len(value[0]) if type(value[0]) is list else 0
    if not 1 <= bins <= 4096:
        raise ValueError("histograms: 1..4096 common unit bins required")
    result = []
    for row in value:
        if type(row) is not list or len(row) != bins:
            raise ValueError("histograms: rows must have equal length")
        if any(type(x) is not int or not 0 <= x <= 1_000_000 for x in row):
            raise ValueError("histograms: integer masses in 0..1000000 required")
        total = sum(row)
        if total == 0:
            raise ValueError("histograms: every row needs positive total mass")
        result.append([Fraction(x, total) for x in row])
    return result


def _value(poly: Polynomial, x: Fraction) -> Fraction:
    return (poly[2] * x + poly[1]) * x + poly[0]


def _vertex(poly: Polynomial) -> Fraction | None:
    if poly[2] == 0:
        return None
    x = -poly[1] / (2 * poly[2])
    return x if 0 <= x <= 1 else None


def _extrema(poly: Polynomial) -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
    points = [Fraction(0), Fraction(1)]
    vertex = _vertex(poly)
    if vertex is not None:
        points.append(vertex)
    values = [(_value(poly, x), x) for x in points]
    return min(values), max(values)


def _segments(rows: list[list[Fraction]]) -> tuple[list[tuple[Polynomial, Polynomial]], ...]:
    """Return (K,D) on each bin in its local coordinate x in [0,1]."""
    before = [Fraction(0)] * 4
    cumulative = [Fraction(0)] * 2
    result: tuple[list[tuple[Polynomial, Polynomial]], ...] = ([], [])
    for interval in range(len(rows[0])):
        density = [row[interval] for row in rows]

        def difference(i: int, j: int) -> tuple[Fraction, Fraction]:
            return before[i] - before[j], density[i] - density[j]

        def cross(i: int, j: int) -> Fraction:
            return density[i] * before[j] - density[j] * before[i]

        # C = cross(i,j) (F_l-F_k) + (F_j-F_i) cross(k,l).
        for gap, (i, j, k, l) in enumerate(((0, 3, 1, 2), (0, 1, 2, 3))):
            x, y = difference(j, i), difference(l, k)
            c0 = cross(i, j) * y[0] + x[0] * cross(k, l)
            c1 = cross(i, j) * y[1] + x[1] * cross(k, l)
            d = (x[0] * y[0], x[0] * y[1] + x[1] * y[0], x[1] * y[1])
            integral = (cumulative[gap], c0, c1 / 2)
            result[gap].append((integral, d))
            cumulative[gap] = _value(integral, Fraction(1))
        before = [before[i] + density[i] for i in range(4)]
    return result


def _minimum(segments: list[tuple[Polynomial, Polynomial]]) -> GapMinimum:
    best = GapMinimum(Fraction(0), Fraction(0), Fraction(0))
    prefix_value = prefix_at = Fraction(0)

    def consider(value: Fraction, lower: Fraction, upper: Fraction) -> None:
        nonlocal best
        if (value, lower, upper) < (best.value, best.lower, best.upper):
            best = GapMinimum(value, lower, upper)

    for interval, (integral, d) in enumerate(segments):
        a = tuple(integral[i] + d[i] for i in range(3))
        a_min, _ = _extrema(a)
        _, k_max = _extrema(integral)
        d_min, _ = _extrema(d)
        # Earlier bins, including the current left endpoint.
        consider(a_min[0] - prefix_value, prefix_at, interval + a_min[1])
        # The remaining edges of the same-bin triangle L <= U.
        consider(_value(a, Fraction(1)) - k_max[0], interval + k_max[1], Fraction(interval + 1))
        consider(d_min[0], interval + d_min[1], interval + d_min[1])
        # Any interior minimum has both partial derivatives zero. If one
        # polynomial is constant, an edge already realizes the same value.
        lower, upper = _vertex(integral), _vertex(a)
        if lower is not None and upper is not None and lower <= upper:
            consider(_value(a, upper) - _value(integral, lower), interval + lower, interval + upper)
        if k_max[0] > prefix_value:
            prefix_value, prefix_at = k_max[0], interval + k_max[1]
    return best


def universal_gap_minima(histograms: object) -> tuple[GapMinimum, GapMinimum]:
    """Nonnegative values iff both quartet gaps hold in every background.

    A negative value has an exact two-threshold, six-clock/top-three witness.
    Thresholds at 0 and bins represent the infinite endpoints equivalently.
    The guarantee permits dependence within the background, but the whole
    background must be jointly independent of the four independent clocks.
    """
    segments = _segments(_admit(histograms))
    return _minimum(segments[0]), _minimum(segments[1])


def small_background_minima(histograms: object) -> tuple[tuple[Fraction, Fraction, Fraction], ...]:
    """Per gap: no background; min one-background top-2; min top-3.

    The one-background minima range over every real deterministic threshold,
    hence also every independent random single background clock.
    """
    result = []
    for segments in _segments(_admit(histograms)):
        total = _value(segments[-1][0], Fraction(1))
        largest_k = max(_extrema(k)[1][0] for k, _ in segments)
        smallest_a = min(_extrema(tuple(k[i] + d[i] for i in range(3)))[0][0]
                         for k, d in segments)
        result.append((total, total - largest_k, smallest_a))
    return tuple(result)


def threshold_gaps(histograms: object, lower: object, upper: object) -> tuple[Fraction, Fraction]:
    """Exact gaps for top three of this quartet plus fixed clocks L and U."""
    rows = _admit(histograms)
    bins = len(rows[0])
    for x in (lower, upper):
        if type(x) not in (int, Fraction) or not 0 <= x <= bins:
            raise ValueError("threshold: integer or Fraction in [0,bins] required")
        if Fraction(x).denominator.bit_length() > 128:
            raise ValueError("threshold: denominator exceeds 128 bits")
    if lower > upper:
        raise ValueError("thresholds: lower must not exceed upper")
    lower, upper = Fraction(lower), Fraction(upper)
    li, ui = min(int(lower), bins - 1), min(int(upper), bins - 1)
    result = []
    for segments in _segments(rows):
        ku, du = segments[ui]
        kl, _ = segments[li]
        result.append(_value(du, upper - ui) + _value(ku, upper - ui) - _value(kl, lower - li))
    return result[0], result[1]


UNIVERSAL_BEYOND_HAZARD_ORDERS = [
    [8, 8, 8, 8, 8],
    [10, 9, 6, 8, 7],
    [11, 10, 5, 8, 6],
    [13, 11, 4, 8, 4],
]

TWO_BACKGROUND_NECESSARY = [
    [7, 1, 3, 5],
    [5, 4, 0, 7],
    [2, 9, 4, 1],
    [1, 9, 2, 4],
]

# One common increasing change of time sends the original breakpoints
# 0,1,7/4,2,9/4,3,4 to six unit bins. The last two clocks correspond to
# independent Uniform[7/4,9/4] backgrounds before that change of time.
CONTINUOUS_TWO_BACKGROUND_WITNESS = [
    [4 * a, 3 * b, b, c, 3 * c, 4 * d]
    for a, b, c, d in TWO_BACKGROUND_NECESSARY
] + [[0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0]]


if __name__ == "__main__":
    from research.rank_selection import ORDERED_EXAMPLE, STOCHASTIC_ONLY_EXAMPLE

    for name, rows in (("reversed-hazard sufficient", ORDERED_EXAMPLE),
                       ("CDF order alone", STOCHASTIC_ONLY_EXAMPLE),
                       ("universal beyond both hazard orders", UNIVERSAL_BEYOND_HAZARD_ORDERS),
                       ("two backgrounds necessary", TWO_BACKGROUND_NECESSARY)):
        print(name)
        print("universal minima", universal_gap_minima(rows))
        print("zero/one-background minima", small_background_minima(rows))
        print("two backgrounds at 2,2", threshold_gaps(rows, 2, 2))
