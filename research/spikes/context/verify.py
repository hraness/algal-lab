"""Independent exact reference for two-background quartet certificates.

The direct oracle splits histogram bins at deterministic background values,
enumerates quartet cell assignments, and uses uniform cutoff ranks within a
cell. It never calls the gap polynomial or its integral. A slower O(B^2)
minimizer interpolates its own quadratics from those direct probabilities.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
from math import comb

from research.context_certificate import (
    ORDERED_TWO_BACKGROUND_NECESSARY,
    STRICT_ORDERED_TWO_BACKGROUND_NECESSARY,
    TWO_BACKGROUND_NECESSARY,
    UNIVERSAL_BEYOND_HAZARD_ORDERS,
    small_background_minima,
    threshold_gaps,
    universal_gap_minima,
)
from research.rank_selection import ORDERED_EXAMPLE, STOCHASTIC_ONLY_EXAMPLE


def direct_gaps(rows: list[list[int]], background: list[Fraction | int],
                survivors: int) -> tuple[Fraction, Fraction]:
    """Calculate gaps from rank membership, with no use of C, D, or K."""
    bins = len(rows[0])
    thresholds = {Fraction(i) for i in range(bins + 1)}
    thresholds.update(Fraction(x) for x in background if 0 < x < bins)
    endpoints = sorted(thresholds)
    cells = [(lo, hi) for lo, hi in zip(endpoints, endpoints[1:]) if lo < hi]
    normalized = [[Fraction(x, sum(row)) for x in row] for row in rows]
    masses = []
    for i in range(4):
        masses.append([normalized[i][int(lo)] * (hi - lo) for lo, hi in cells])
    q = {pair: Fraction(0) for pair in combinations(range(4), 2)}
    if survivors < 2:
        return Fraction(0), Fraction(0)
    for assignment in product(range(len(cells)), repeat=4):
        probability = Fraction(1)
        for i, cell in enumerate(assignment):
            probability *= masses[i][cell]
        if not probability:
            continue
        for pair in q:
            cutoff_cell = min(assignment[i] for i in pair)
            midpoint = sum(cells[cutoff_cell], Fraction(0)) / 2
            above = (sum(Fraction(x) > midpoint for x in background)
                     + sum(cell > cutoff_cell for cell in assignment))
            in_cell = sum(cell == cutoff_cell for cell in assignment)
            needed = sum(assignment[i] == cutoff_cell for i in pair)
            slots = survivors - above
            if slots < needed:
                included = Fraction(0)
            elif slots >= in_cell:
                included = Fraction(1)
            else:
                included = Fraction(comb(in_cell - needed, slots - needed),
                                    comb(in_cell, slots))
            q[pair] += probability * included
    return (q[0, 1] + q[2, 3] - q[0, 2] - q[1, 3],
            q[0, 2] + q[1, 3] - q[0, 3] - q[1, 2])


def effective_thresholds(background: list[Fraction | int], survivors: int,
                         bins: int) -> tuple[Fraction, Fraction]:
    """Order statistics of fixed backgrounds, with finite support endpoints."""
    ordered = sorted((Fraction(x) for x in background), reverse=True)
    m = survivors - 2

    def rank(index: int) -> Fraction:
        if index <= 0:
            return Fraction(bins)
        if index > len(ordered):
            return Fraction(0)
        return min(Fraction(bins), max(Fraction(0), ordered[index - 1]))

    return rank(m + 1), rank(m)


def _quadratic(y0: Fraction, half: Fraction, y1: Fraction) -> tuple[Fraction, Fraction, Fraction]:
    second = 2 * (y1 - 2 * half + y0)
    return y0, y1 - y0 - second, second


def _value(poly: tuple[Fraction, Fraction, Fraction], x: Fraction) -> Fraction:
    return poly[0] + poly[1] * x + poly[2] * x * x


def _vertex(poly: tuple[Fraction, Fraction, Fraction]) -> Fraction | None:
    if poly[2] == 0:
        return None
    x = -poly[1] / (2 * poly[2])
    return x if 0 <= x <= 1 else None


def slow_minima(rows: list[list[int]]) -> tuple[Fraction, Fraction]:
    """O(B^2) stationary/boundary search, anchored in direct rank probabilities."""
    bins = len(rows[0])
    pieces: list[list[tuple[tuple[Fraction, ...], tuple[Fraction, ...],
                             tuple[Fraction, ...]]]] = [[], []]
    for j in range(bins):
        values = []
        for offset in (Fraction(0), Fraction(1, 2), Fraction(1)):
            t = Fraction(j) + offset
            a = direct_gaps(rows, [0, t], 3)
            d = direct_gaps(rows, [t, t], 3)
            values.append((a, d))
        for gap in range(2):
            a = _quadratic(*(values[p][0][gap] for p in range(3)))
            d = _quadratic(*(values[p][1][gap] for p in range(3)))
            k = tuple(a[i] - d[i] for i in range(3))
            pieces[gap].append((k, a, d))

    answers = []
    for segments in pieces:
        lower_candidates = {Fraction(j) for j in range(bins + 1)}
        upper_candidates = lower_candidates.copy()
        diagonal_candidates = lower_candidates.copy()
        for j, (k, a, d) in enumerate(segments):
            for poly, target in ((k, lower_candidates), (a, upper_candidates),
                                 (d, diagonal_candidates)):
                vertex = _vertex(poly)
                if vertex is not None:
                    target.add(j + vertex)

        def evaluate(poly_index: int, t: Fraction) -> Fraction:
            j = min(int(t), bins - 1)
            return _value(segments[j][poly_index], t - j)

        answer = min(evaluate(1, u) - evaluate(0, l)
                     for l in lower_candidates for u in upper_candidates if l <= u)
        answer = min(answer, *(evaluate(2, t) for t in diagonal_candidates))
        answers.append(answer)
    return answers[0], answers[1]


def slow_small_background_minima(rows: list[list[int]]) -> tuple[tuple[Fraction, Fraction, Fraction], ...]:
    """Independently search one-background stationary and boundary values."""
    bins = len(rows[0])
    no_background = direct_gaps(rows, [], 2)
    one_top_two: list[list[tuple[Fraction, Fraction, Fraction]]] = [[], []]
    one_top_three: list[list[tuple[Fraction, Fraction, Fraction]]] = [[], []]
    for j in range(bins):
        samples = []
        for offset in (Fraction(0), Fraction(1, 2), Fraction(1)):
            t = Fraction(j) + offset
            samples.append((direct_gaps(rows, [t], 2), direct_gaps(rows, [t], 3)))
        for gap in range(2):
            one_top_two[gap].append(_quadratic(*(samples[p][0][gap] for p in range(3))))
            one_top_three[gap].append(_quadratic(*(samples[p][1][gap] for p in range(3))))

    def minimum(pieces: list[tuple[Fraction, Fraction, Fraction]]) -> Fraction:
        values = []
        for poly in pieces:
            points = [Fraction(0), Fraction(1)]
            vertex = _vertex(poly)
            if vertex is not None:
                points.append(vertex)
            values.extend(_value(poly, x) for x in points)
        return min(values)

    return tuple((no_background[g], minimum(one_top_two[g]),
                  minimum(one_top_three[g])) for g in range(2))


VERTEX_EXAMPLE = [[0, 6, 5], [3, 4, 5], [1, 7, 2], [1, 2, 7]]
DIAGONAL_EXAMPLE = [[0, 5, 0], [3, 1, 2], [7, 8, 0], [8, 2, 4]]
DEGENERATE_EXAMPLE = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1]]


def verify() -> dict[str, int]:
    fixtures = (ORDERED_EXAMPLE, STOCHASTIC_ONLY_EXAMPLE, VERTEX_EXAMPLE,
                DIAGONAL_EXAMPLE, DEGENERATE_EXAMPLE,
                UNIVERSAL_BEYOND_HAZARD_ORDERS, TWO_BACKGROUND_NECESSARY,
                ORDERED_TWO_BACKGROUND_NECESSARY,
                STRICT_ORDERED_TWO_BACKGROUND_NECESSARY,
                [ORDERED_EXAMPLE[i] for i in (0, 2, 1, 3)],
                list(reversed(ORDERED_EXAMPLE)))
    conditional_checks = 0
    for rows in fixtures:
        bins = len(rows[0])
        backgrounds = ([], [Fraction(1, 2)], [1, 1],
                       [Fraction(1, 3), Fraction(5, 3)],
                       [0, Fraction(3, 2), Fraction(3, 2), bins],
                       [Fraction(-1), Fraction(bins + 1)])
        for bg in backgrounds:
            for k in range(2, len(bg) + 5):
                lower, upper = effective_thresholds(bg, k, bins)
                assert direct_gaps(rows, bg, k) == threshold_gaps(rows, lower, upper)
                conditional_checks += 1
        assert slow_minima(rows) == tuple(x.value for x in universal_gap_minima(rows))
        assert slow_small_background_minima(rows) == small_background_minima(rows)

    witness = universal_gap_minima(VERTEX_EXAMPLE)[1]
    assert witness.value < 0 and witness.lower.denominator > 1 and witness.upper.denominator > 1
    assert direct_gaps(VERTEX_EXAMPLE, [witness.lower, witness.upper], 3)[1] == witness.value
    diagonal = universal_gap_minima(DIAGONAL_EXAMPLE)[1]
    assert diagonal.value < 0 and diagonal.lower == diagonal.upper
    assert diagonal.lower.denominator > 1
    assert direct_gaps(DIAGONAL_EXAMPLE, [diagonal.lower, diagonal.upper], 3)[1] == diagonal.value

    # The 4,096-bin admission path should remain bounded and exact.
    uniform = [[1] * 4096 for _ in range(4)]
    assert all(result.value == 0 for result in universal_gap_minima(uniform))
    assert small_background_minima(uniform) == ((Fraction(0),) * 3,) * 2
    return {"conditionalCases": conditional_checks, "slowMinimizers": len(fixtures),
            "smallBackgroundMinimizers": len(fixtures), "vertexWitnesses": 2,
            "maxBins": 4096}


if __name__ == "__main__":
    from research.spikes.context.pathwise import verify as verify_pathwise
    from research.spikes.context.support_width import verify as verify_support_width

    print("context certificate:", verify())
    print("pathwise context reduction:", verify_pathwise())
    print("minimal rank contexts:", verify_support_width())
