"""Exact equal-size group service after two rate-proportional deletions.

For n = m*r, the expected number of wholly intact groups is maximized by
consecutive blocks in sorted rate order. The expected count of groups retaining
at least r-1 members is a separate minimization problem. These claims concern
exactly two deletions, not arbitrary survivor horizons.

The 3-PARTITION reduction below constructs bounded executable examples of a
theoretical, unbounded strong NP-completeness proof for 2-of-3 optimization.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations


MAX_VERTICES = 96
MAX_RATE = 10**18
MAX_TARGET = 200_000
MAX_EXHAUSTIVE_VERTICES = 9


def _weights(value: object) -> list[int]:
    if type(value) is not list or not 4 <= len(value) <= MAX_VERTICES:
        raise ValueError(f"weights requires a list of 4..{MAX_VERTICES} rates")
    if any(type(w) is not int or not 1 <= w <= MAX_RATE for w in value):
        raise ValueError(f"rates require integers in 1..{MAX_RATE}")
    return value.copy()


def _group_size(value: object, n: int) -> int:
    if type(value) is not int or not 2 <= value <= n // 2 or n % value:
        raise ValueError("group_size must divide n and leave at least two groups of size >=2")
    return value


def _groups(value: object, n: int) -> list[list[int]]:
    if type(value) is not list or not value:
        raise ValueError("groups requires a nonempty list")
    if any(type(group) is not list for group in value):
        raise ValueError("each group requires a list")
    r = _group_size(len(value[0]), n)
    if len(value) != n // r or any(len(group) != r for group in value):
        raise ValueError("groups must form equally sized blocks covering all vertices")
    flattened = [i for group in value for i in group]
    if any(type(i) is not int or not 0 <= i < n for i in flattened):
        raise ValueError("group indices must be integers in 0..n-1")
    if len(set(flattened)) != n:
        raise ValueError("groups must partition all vertices exactly once")
    return [group.copy() for group in value]


def _same_group_probability(weights: list[int], groups: list[list[int]]) -> Fraction:
    total = sum(weights)
    b = [Fraction(w, total - w) for w in weights]
    diagonal = sum((weights[i] * b[i] for i in range(len(weights))), Fraction(0))
    grouped = sum((sum(weights[i] for i in group) *
                   sum((b[i] for i in group), Fraction(0))
                   for group in groups), Fraction(0))
    return (grouped - diagonal) / total


def expected_group_counts(spec: object) -> dict:
    """Exact expected counts for ALL and (r-1)-of-r service after two deletions.

    `spec` has exactly `weights` and `groups` keys. Rates and group indices are
    integers, with no implicit float or bool coercion.
    """
    if type(spec) is not dict or set(spec) != {"weights", "groups"}:
        raise ValueError("spec requires exactly weights and groups")
    weights = _weights(spec["weights"])
    groups = _groups(spec["groups"], len(weights))
    same = _same_group_probability(weights, groups)
    m = len(groups)
    return {
        "survivors": len(weights) - 2,
        "group_size": len(groups[0]),
        "same_group_probability": same,
        "all": Fraction(m - 2) + same,
        "at_least_r_minus_one": Fraction(m) - same,
    }


def adjacent_all_groups(weights: object, group_size: object) -> list[list[int]]:
    """Return a rate-order optimal ALL-survive grouping after two deletions."""
    rates = _weights(weights)
    r = _group_size(group_size, len(rates))
    ordered = sorted(range(len(rates)), key=lambda i: (rates[i], i))
    return [ordered[i:i + r] for i in range(0, len(rates), r)]


def universal_regret_bound(weights: object, group_size: object) -> Fraction:
    """Upper bound on the service gap between any two equal-size groupings.

    Applies to both ALL and (r-1)-of-r expected counts after two deletions.
    It is a universal additive bound, not an estimate of actual regret.
    """
    rates = _weights(weights)
    r = _group_size(group_size, len(rates))
    n = len(rates)
    low, high = min(rates), max(rates)
    total = sum(rates)
    spread = high - low
    bound = Fraction(n * r * spread * spread,
                     2 * (total - high) * (total - low))
    return min(Fraction(1), bound)


def _partitions(vertices: tuple[int, ...], r: int):
    if not vertices:
        yield ()
        return
    first = vertices[0]
    for rest in combinations(vertices[1:], r - 1):
        group = (first, *rest)
        remainder = tuple(v for v in vertices if v not in group)
        for tail in _partitions(remainder, r):
            yield (group, *tail)


def optimal_triples_after_two_deletions(weights: object, threshold: object) -> dict:
    """Exhaustive exact optimum for 2- or 3-of-3 at n=6 or n=9.

    `threshold=3` is ALL and `threshold=2` is majority. For n>9 use the
    structural ALL construction or score a candidate partition directly.
    """
    rates = _weights(weights)
    n = len(rates)
    if n not in (6, 9) or n > MAX_EXHAUSTIVE_VERTICES:
        raise ValueError("exhaustive triples require n=6 or n=9")
    if type(threshold) is not int or threshold not in (2, 3):
        raise ValueError("threshold requires integer 2 or 3")
    best: Fraction | None = None
    winners: list[list[list[int]]] = []
    examined = 0
    for partition in _partitions(tuple(range(n)), 3):
        groups = [list(group) for group in partition]
        same = _same_group_probability(rates, groups)
        score = Fraction(n // 3 - 2) + same if threshold == 3 else Fraction(n // 3) - same
        examined += 1
        if best is None or score > best:
            best = score
            winners = [groups]
        elif score == best:
            winners.append(groups)
    assert best is not None
    return {"threshold": threshold, "score": best,
            "groups": winners[0], "tie_count": len(winners),
            "partitions_examined": examined}


def three_partition_reduction(items: object, target: object) -> dict:
    """Bounded exact constructor for the majority-triple hardness reduction.

    The mathematical reduction is unbounded; these caps keep an executable
    certificate small. A valid 3-PARTITION instance satisfies sum(items)=mB
    and B/4 < item < B/2. A triple partition reaches `threshold` exactly
    when each of its original-item triples sums to B.
    """
    if type(items) is not list or not 6 <= len(items) <= MAX_VERTICES or len(items) % 3:
        raise ValueError("items requires 6..96 integers in a multiple of three")
    if type(target) is not int or not 1 <= target <= MAX_TARGET:
        raise ValueError(f"target requires an integer in 1..{MAX_TARGET}")
    if any(type(x) is not int or not 1 <= x <= MAX_TARGET or not target < 4 * x or not 2 * x < target
           for x in items):
        raise ValueError("items require positive integers strictly between target/4 and target/2")
    n = len(items)
    m = n // 3
    if sum(items) != m * target:
        raise ValueError("items must sum to group_count * target")
    K = n * target**3
    weights = [K + x for x in items]
    if max(weights) > MAX_RATE:
        raise ValueError("constructed rates exceed executable bound")
    W = sum(weights)
    D = W - K
    b = [Fraction(w, W - w) for w in weights]
    C = (3 * K + target) * sum(b, Fraction(0))
    diagonal = sum((weights[i] * b[i] for i in range(n)), Fraction(0))
    baseline = Fraction(m) - (C - diagonal) / W
    Q = 2 * D * D
    threshold = Fraction((Q * baseline).__floor__(), Q)
    return {
        "weights": weights,
        "survivors": n - 2,
        "group_size": 3,
        "required_survivors_per_group": 2,
        "threshold": threshold,
        "baseline": baseline,
        "denominator_bound": Q,
        "no_instance_gap_lower_bound": Fraction(1, D * D),
    }
