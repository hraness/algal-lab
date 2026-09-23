"""All-horizon optimal intact groups for ordered exponential failure clocks.

Independent Exp(w_i) clocks are ranked, retaining the k largest. For equal-size
groups with equal rewards, consecutive blocks in rate order maximize the
expected count of groups whose every member survives at every fixed k.

The construction uses no probabilities. An exact small-population subset DP is
provided for independent verification and examples, with a separate cap.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations


MAX_VERTICES = 96
MAX_RATE = 10**18
MAX_EXACT_VERTICES = 12


def _rates(value: object) -> list[int]:
    if type(value) is not list or not 4 <= len(value) <= MAX_VERTICES:
        raise ValueError(f"weights requires a list of 4..{MAX_VERTICES} rates")
    if any(type(rate) is not int or not 1 <= rate <= MAX_RATE for rate in value):
        raise ValueError(f"rates require integers in 1..{MAX_RATE}")
    return value.copy()


def _group_size(value: object, n: int) -> int:
    if type(value) is not int or not 2 <= value <= n // 2 or n % value:
        raise ValueError("group_size must divide n and leave at least two groups of size >=2")
    return value


def _survivors(value: object, n: int) -> int:
    if type(value) is not int or not 0 <= value <= n:
        raise ValueError("survivors requires an integer in 0..n")
    return value


def _groups(value: object, n: int) -> tuple[list[list[int]], int]:
    if type(value) is not list or not value or any(type(group) is not list for group in value):
        raise ValueError("groups requires a nonempty list of lists")
    r = _group_size(len(value[0]), n)
    if len(value) != n // r or any(len(group) != r for group in value):
        raise ValueError("groups must have equal size and cover all vertices")
    vertices = [i for group in value for i in group]
    if any(type(i) is not int or not 0 <= i < n for i in vertices):
        raise ValueError("group indices require integers in 0..n-1")
    if len(set(vertices)) != n:
        raise ValueError("groups must partition each vertex exactly once")
    return [group.copy() for group in value], r


def optimal_intact_groups(weights: object, group_size: object) -> dict:
    """Construct a simultaneously optimal partition at every fixed horizon."""
    rates = _rates(weights)
    r = _group_size(group_size, len(rates))
    ordered = sorted(range(len(rates)), key=lambda i: (rates[i], i))
    groups = [ordered[i:i + r] for i in range(0, len(rates), r)]
    return {
        "contract": "algal.lab.intact-groups.v1",
        "weights": rates,
        "groupSize": r,
        "groups": groups,
        "horizons": "every fixed survivor count under independent exponential clocks",
        "probabilityEvaluations": 0,
    }


def _survivor_mass(rates: list[int], survivors: int) -> dict[int, Fraction]:
    n = len(rates)
    full = (1 << n) - 1
    totals = [0] * (full + 1)
    for mask in range(1, full + 1):
        bit = mask & -mask
        totals[mask] = totals[mask ^ bit] + rates[bit.bit_length() - 1]
    mass = {full: Fraction(1)}
    for _ in range(n - survivors):
        next_mass: dict[int, Fraction] = {}
        for mask, probability in mass.items():
            remaining = mask
            while remaining:
                bit = remaining & -remaining
                remaining -= bit
                i = bit.bit_length() - 1
                child = mask ^ bit
                next_mass[child] = next_mass.get(child, Fraction(0)) + probability * Fraction(
                    rates[i], totals[mask])
        mass = next_mass
    return mass


def group_inclusion_probabilities(weights: object, group_size: object,
                                  survivors: object) -> dict[tuple[int, ...], Fraction]:
    """Exact small-n chance that each size-r group is wholly in the top k."""
    rates = _rates(weights)
    n = len(rates)
    if n > MAX_EXACT_VERTICES:
        raise ValueError(f"exact probability work requires n<={MAX_EXACT_VERTICES}")
    r = _group_size(group_size, n)
    k = _survivors(survivors, n)
    answer = {group: Fraction(0) for group in combinations(range(n), r)}
    if k < r:
        return answer
    for mask, probability in _survivor_mass(rates, k).items():
        alive = [i for i in range(n) if mask & (1 << i)]
        for group in combinations(alive, r):
            answer[group] += probability
    return answer


def exact_intact_count(spec: object) -> Fraction:
    """Exact expected intact-group count for one admitted partition/horizon.

    Spec keys are exactly `weights`, `groups`, and `survivors`; the exact
    probability path admits at most 12 vertices.
    """
    if type(spec) is not dict or set(spec) != {"weights", "groups", "survivors"}:
        raise ValueError("spec requires exactly weights, groups, and survivors")
    rates = _rates(spec["weights"])
    groups, r = _groups(spec["groups"], len(rates))
    q = group_inclusion_probabilities(rates, r, spec["survivors"])
    return sum((q[tuple(sorted(group))] for group in groups), Fraction(0))
