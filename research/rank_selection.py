"""Exact, bounded rank-selection probabilities for continuous histogram clocks.

Each row gives integer masses on the same consecutive unit intervals. A clock
chooses its interval by normalized mass and is uniform inside it; all clocks
are independent, so there are no ties. Polynomial integration uses Fractions.
This is a research oracle, not an assertion that arbitrary clocks are ordered.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations


def admit_histograms(value: object) -> list[list[Fraction]]:
    if type(value) is not list or not 4 <= len(value) <= 9:
        raise ValueError("histograms: requires a list of 4..9 rows")
    bins = len(value[0]) if type(value[0]) is list else 0
    if not 1 <= bins <= 6:
        raise ValueError("histograms: requires 1..6 common unit intervals")
    rows = []
    for row in value:
        if type(row) is not list or len(row) != bins:
            raise ValueError("histogram: rows must have the same number of bins")
        if any(type(x) is not int or not 0 <= x <= 64 for x in row) or sum(row) == 0:
            raise ValueError("histogram: integer counts in 0..64 with positive total required")
        rows.append([Fraction(x, sum(row)) for x in row])
    return rows


def _add(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    result = [Fraction(0)] * max(len(left), len(right))
    for i, x in enumerate(left):
        result[i] += x
    for i, x in enumerate(right):
        result[i] += x
    return result


def _multiply(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    result = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            result[i + j] += x * y
    return result


def _exceedance_polynomials(cdfs: list[list[Fraction]]) -> list[list[Fraction]]:
    """Coefficient j is the polynomial probability of exactly j exceedances."""
    counts = [[Fraction(1)]]
    for cdf in cdfs:
        survival = [1 - cdf[0], -cdf[1]]
        updated = [[Fraction(0)] for _ in range(len(counts) + 1)]
        for j, probability in enumerate(counts):
            updated[j] = _add(updated[j], _multiply(probability, cdf))
            updated[j + 1] = _add(updated[j + 1], _multiply(probability, survival))
        counts = updated
    return counts


def pair_probabilities(histograms: object, survivors: object) -> dict[tuple[int, int], Fraction]:
    """Exact probability each labeled pair belongs to the largest k clocks."""
    rows = admit_histograms(histograms)
    n = len(rows)
    if type(survivors) is not int or not 0 <= survivors <= n:
        raise ValueError("survivors: requires an integer in 0..n")
    q = {pair: Fraction(0) for pair in combinations(range(n), 2)}
    if survivors < 2:
        return q
    before = [Fraction(0)] * n
    for interval in range(len(rows[0])):
        density = [row[interval] for row in rows]
        cdfs = [[before[i], density[i]] for i in range(n)]
        for i, j in q:
            others = [cdfs[r] for r in range(n) if r not in (i, j)]
            exact = _exceedance_polynomials(others)
            at_most = [Fraction(0)]
            for probability in exact[:survivors - 1]:
                at_most = _add(at_most, probability)
            # Density of the smaller of the two selected clocks.
            pair_density = [density[i] * (1 - before[j]) + density[j] * (1 - before[i]),
                            -2 * density[i] * density[j]]
            integrand = _multiply(pair_density, at_most)
            q[i, j] += sum((x / (degree + 1) for degree, x in enumerate(integrand)), Fraction(0))
        before = [before[i] + density[i] for i in range(n)]
    return q


def ordered_conditions(histograms: object) -> dict[str, bool]:
    """Check given row order: ascending CDFs and descending reverse hazards.

On each open interval the density cross-product is constant, so endpoint CDF
comparisons and this cross-product check are exact, not a time-grid heuristic.
The cross-product formulation also handles zero densities/CDFs.
"""
    rows = admit_histograms(histograms)
    before = [Fraction(0)] * len(rows)
    cdf_ordered = hazard_ordered = True
    for interval in range(len(rows[0])):
        density = [row[interval] for row in rows]
        after = [before[i] + density[i] for i in range(len(rows))]
        for i in range(len(rows) - 1):
            j = i + 1
            cdf_ordered &= before[i] <= before[j] and after[i] <= after[j]
            hazard_ordered &= density[i] * before[j] >= density[j] * before[i]
        before = after
    return {"cdfOrdered": cdf_ordered, "reverseHazardOrdered": hazard_ordered}


ORDERED_EXAMPLE = [[1, 3, 12], [2, 6, 8], [4, 8, 4], [8, 6, 2]]
STOCHASTIC_ONLY_EXAMPLE = [[0, 1, 2], [1, 0, 2], [2, 0, 1], [2, 1, 0]]


if __name__ == "__main__":
    for name, rows in (("reverse-hazard ordered", ORDERED_EXAMPLE),
                       ("stochastic order alone", STOCHASTIC_ONLY_EXAMPLE)):
        q = pair_probabilities(rows, 2)
        print(name, ordered_conditions(rows))
        print("adjacent crossing nested", q[0, 1] + q[2, 3],
              q[0, 2] + q[1, 3], q[0, 3] + q[1, 2])
