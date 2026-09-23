"""Standalone exact categorical-rank check of the ordered continuous witness.

There are four independent focal histogram clocks on seven unit bins and two
independent uniform backgrounds. All six clocks are integrated directly; no
C, D, K formula, deterministic-threshold oracle, or quadrature is used.
"""

from fractions import Fraction
from itertools import combinations, product
from math import comb, prod


def verify() -> dict[str, object]:
    rows = [
        [0, 3, 0, 1, 2, 0, 3],
        [1, 2, 1, 0, 2, 1, 2],
        [2, 1, 2, 0, 1, 2, 1],
        [3, 0, 2, 1, 0, 3, 0],
    ]
    background_intervals = (
        (Fraction(7, 4), Fraction(9, 4)),
        (Fraction(19, 4), Fraction(21, 4)),
    )
    endpoints = sorted(
        {Fraction(i) for i in range(8)}
        | {x for interval in background_intervals for x in interval}
    )
    cells = list(zip(endpoints, endpoints[1:]))

    # Every clock has constant density on every refined cell. Conditional on
    # a cell assignment, all clocks in that cell are independent uniforms.
    masses = [
        [Fraction(row[int(lo)], sum(row)) * (hi - lo) for lo, hi in cells]
        for row in rows
    ]
    for start, end in background_intervals:
        masses.append([
            (hi - lo) / (end - start) if start <= lo and hi <= end else Fraction(0)
            for lo, hi in cells
        ])
    assert all(sum(row) == 1 for row in masses)
    supports = [
        [(cell, mass) for cell, mass in enumerate(row) if mass]
        for row in masses
    ]

    q = {pair: Fraction(0) for pair in combinations(range(4), 2)}
    assignments = 0
    total_probability = Fraction(0)
    for outcomes in product(*supports):
        indices = [outcome[0] for outcome in outcomes]
        weight = prod(outcome[1] for outcome in outcomes)
        assignments += 1
        total_probability += weight
        for pair in q:
            cutoff = min(indices[i] for i in pair)
            above = sum(cell > cutoff for cell in indices)
            in_cell = indices.count(cutoff)
            needed = sum(indices[i] == cutoff for i in pair)
            slots = 3 - above
            if slots < needed:
                chance = Fraction(0)
            elif slots >= in_cell:
                chance = Fraction(1)
            else:
                # All size-slots subsets of the cutoff cell are equiprobable.
                chance = Fraction(
                    comb(in_cell - needed, slots - needed), comb(in_cell, slots)
                )
            q[pair] += weight * chance

    gaps = (
        q[0, 1] + q[2, 3] - q[0, 2] - q[1, 3],
        q[0, 2] + q[1, 3] - q[0, 3] - q[1, 2],
    )
    assert len(cells) == 11
    assert assignments == 14_400
    assert total_probability == 1
    assert gaps == (Fraction(133, 11664), Fraction(-7, 11664))
    return {
        "cells": len(cells),
        "assignments": assignments,
        "totalProbability": total_probability,
        "pairProbabilities": q,
        "gaps": gaps,
    }


if __name__ == "__main__":
    print(verify())
