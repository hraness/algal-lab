"""Exact bounded judge for ordered survivor-pair inequalities.

This is a finite-panel conjecture judge, not a theorem prover. The deletion
process repeatedly removes i with probability w_i / sum(w_alive).
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations


MAX_ENVIRONMENTS = 256
EXPRESSIONS = {
    "sum_adjacent_vs_crossing": (((0, 1), (2, 3)), ((0, 2), (1, 3)), "sum"),
    "sum_crossing_vs_nested": (((0, 2), (1, 3)), ((0, 3), (1, 2)), "sum"),
    "product_adjacent_vs_crossing": (((0, 1), (2, 3)), ((0, 2), (1, 3)), "product"),
    "product_crossing_vs_nested": (((0, 2), (1, 3)), ((0, 3), (1, 2)), "product"),
}


def _positive_int(value: object, label: str, high: int = 12) -> int:
    if type(value) is not int or not 1 <= value <= high:
        raise ValueError(f"{label}: requires an integer in 1..{high}")
    return value


def admit_weights(value: object) -> list[int]:
    if type(value) is not list or not 4 <= len(value) <= 9:
        raise ValueError("weights: requires a list of 4..9 rates")
    return [_positive_int(rate, "rate") for rate in value]


def admit_claim(value: object) -> dict[str, str]:
    if type(value) is not dict or set(value) != {"expression", "relation", "horizons"}:
        raise ValueError("claim: requires exactly expression, relation, and horizons")
    expression, relation, horizons = (value[key] for key in ("expression", "relation", "horizons"))
    if type(expression) is not str or expression not in EXPRESSIONS:
        raise ValueError("expression: unsupported comparison")
    if type(relation) is not str or relation not in ("ge", "le"):
        raise ValueError("relation: requires ge or le")
    if type(horizons) is not str or horizons not in ("all", "pair", "interior"):
        raise ValueError("horizons: requires all, pair, or interior")
    return {"expression": expression, "relation": relation, "horizons": horizons}


def pair_inclusion_probabilities(weights: object, survivors: object) -> dict[tuple[int, int], Fraction]:
    """Return exact probability that each labeled pair survives to this horizon."""
    rates = admit_weights(weights)
    n = len(rates)
    if type(survivors) is not int or not 2 <= survivors <= n:
        raise ValueError("survivors: requires an integer in 2..n")
    full = (1 << n) - 1
    totals = [0] * (1 << n)
    for mask in range(1, 1 << n):
        bit = mask & -mask
        totals[mask] = totals[mask ^ bit] + rates[bit.bit_length() - 1]
    mass = [Fraction(0) for _ in range(1 << n)]
    mass[full] = Fraction(1)
    for size in range(n, survivors, -1):
        for mask in range(1, full + 1):
            if mask.bit_count() != size or not mass[mask]:
                continue
            remaining = mask
            while remaining:
                bit = remaining & -remaining
                remaining ^= bit
                node = bit.bit_length() - 1
                next_mask = mask ^ bit
                mass[next_mask] += mass[mask] * Fraction(rates[node], totals[mask])
    result = {pair: Fraction(0) for pair in combinations(range(n), 2)}
    for mask in range(1, full + 1):
        if mask.bit_count() != survivors or not mass[mask]:
            continue
        nodes = [i for i in range(n) if mask & (1 << i)]
        for pair in combinations(nodes, 2):
            result[pair] += mass[mask]
    return result


def one_deletion_pair_probabilities(weights: object) -> dict[tuple[int, int], Fraction]:
    """Separately callable one-deletion DP (horizon n-1), for analytic checks."""
    rates = admit_weights(weights)
    n = len(rates)
    full = (1 << n) - 1
    total = sum(rates)
    mass = {full ^ (1 << removed): Fraction(rates[removed], total)
            for removed in range(n)}
    return {
        (i, j): sum((probability for mask, probability in mass.items()
                     if mask & (1 << i) and mask & (1 << j)), Fraction(0))
        for i, j in combinations(range(n), 2)
    }


def _horizons(selection: str, n: int) -> range:
    if selection == "pair":
        return range(2, 3)
    if selection == "interior":
        return range(3, n - 1)
    return range(2, n - 1)


def _side(probabilities: dict, pairs: tuple, operation: str) -> Fraction:
    values = [probabilities[pair] for pair in pairs]
    return sum(values, Fraction(0)) if operation == "sum" else values[0] * values[1]


def judge(environments: object, claim: object) -> dict:
    """Check every sorted-rate quadruple at requested horizons exactly.

    Passing means only that this supplied finite panel has no counterexample.
    """
    admitted_claim = admit_claim(claim)
    if type(environments) is not list or not 1 <= len(environments) <= MAX_ENVIRONMENTS:
        raise ValueError(f"environments: requires a list of 1..{MAX_ENVIRONMENTS} entries")
    rates_panel = []
    for env in environments:
        if type(env) is not dict or set(env) != {"weights"}:
            raise ValueError("environment: requires exactly weights")
        rates_panel.append(admit_weights(env["weights"]))

    left_spec, right_spec, operation = EXPRESSIONS[admitted_claim["expression"]]
    checked = 0
    for env_index, rates in enumerate(rates_panel):
        n = len(rates)
        ordered = sorted(range(n), key=lambda i: (rates[i], i))
        for horizon in _horizons(admitted_claim["horizons"], n):
            probabilities = pair_inclusion_probabilities(rates, horizon)
            for quad in combinations(ordered, 4):
                def actual(spec):
                    return tuple(tuple(sorted((quad[i], quad[j]))) for i, j in spec)

                left_pairs, right_pairs = actual(left_spec), actual(right_spec)
                left = _side(probabilities, left_pairs, operation)
                right = _side(probabilities, right_pairs, operation)
                holds = left >= right if admitted_claim["relation"] == "ge" else left <= right
                checked += 1
                if not holds:
                    return {
                        "status": "counterexample",
                        "checked": checked,
                        "counterexample": {
                            "environmentIndex": env_index,
                            "survivors": horizon,
                            "vertices": list(quad),
                            "left": left,
                            "right": right,
                        },
                    }
    return {"status": "passed", "passedCount": checked}
