"""Independent exact checks of the all-horizon intact-group construction.

The product integral is expanded by inclusion-exclusion and compared with the
source's deletion-state DP. A separate partition DP checks global optima.
These bounded checks support, but do not replace, the mathematical proof.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import combinations

from research.intact_groups import group_inclusion_probabilities, optimal_intact_groups


def integral_group_probability(weights: list[int], group: tuple[int, ...],
                               deletions: int) -> Fraction:
    """Integrate the dth-outside-failure density by exact inclusion-exclusion."""
    n = len(weights)
    outside = tuple(i for i in range(n) if i not in group)
    if deletions == 0:
        return Fraction(1)
    if deletions > len(outside):
        return Fraction(0)
    total = sum(weights)
    answer = Fraction(0)
    for final in outside:
        previous_pool = tuple(i for i in outside if i != final)
        for prior in combinations(previous_pool, deletions - 1):
            integrated_product = Fraction(0)
            for size in range(len(prior) + 1):
                for positive in combinations(prior, size):
                    sign = -1 if (len(prior) - size) % 2 else 1
                    integrated_product += Fraction(
                        sign, total - sum(weights[i] for i in positive))
            answer += weights[final] * integrated_product
    return answer


def max_partition_score(q: dict[tuple[int, ...], Fraction], n: int, r: int) -> Fraction:
    """Exact global partition DP; independent of the sorting constructor."""
    @lru_cache(None)
    def solve(mask: int) -> Fraction:
        if mask == 0:
            return Fraction(0)
        first_bit = mask & -mask
        first = first_bit.bit_length() - 1
        rest = tuple(i for i in range(first + 1, n) if mask & (1 << i))
        best: Fraction | None = None
        for others in combinations(rest, r - 1):
            group = (first, *others)
            group_mask = first_bit | sum(1 << i for i in others)
            candidate = q[group] + solve(mask ^ group_mask)
            if best is None or candidate > best:
                best = candidate
        assert best is not None
        return best
    return solve((1 << n) - 1)


def _elementary(values: list[int], degree: int) -> int:
    result = [0] * (degree + 1)
    result[0] = 1
    for value in values:
        for j in range(degree, 0, -1):
            result[j] += value * result[j - 1]
    return result[degree]


def phi_at_log_two(weights: list[int], vertices: tuple[int, ...],
                   deletions: int) -> int:
    """The pointwise polynomial Phi_d at t=log(2), with integer odds."""
    return sum(weights[j] * _elementary(
        [(1 << weights[i]) - 1 for i in vertices if i != j], deletions - 1)
        for j in vertices)


def main() -> None:
    fixtures = (
        (list(range(1, 7)), 3),
        (list(range(1, 9)), 4),
        (list(range(1, 10)), 3),
        (list(range(1, 13)), 3),
        ([1, 3, 6, 7, 8, 13, 18, 20, 21, 25, 29, 33], 4),
    )
    integral_checks = 0
    optimal_horizons = 0
    for weights, r in fixtures:
        n = len(weights)
        construction = optimal_intact_groups(weights, r)
        groups = construction["groups"]
        assert construction["probabilityEvaluations"] == 0
        for k in range(n + 1):
            q = group_inclusion_probabilities(weights, r, k)
            if n <= 9:
                checked_groups = q
            else:
                checked_groups = {group: q[group] for group in (
                    tuple(range(r)), tuple(range(n-r, n)),
                    tuple(range(0, n, n // r))[:r])}
            for group, probability in checked_groups.items():
                assert integral_group_probability(weights, group, n-k) == probability
                integral_checks += 1
            if r <= k <= n - 2:
                score = sum((q[tuple(sorted(group))] for group in groups), Fraction(0))
                assert score == max_partition_score(q, n, r)
                optimal_horizons += 1
            elif k < r:
                assert set(q.values()) == {Fraction(0)}
            elif k == n:
                assert set(q.values()) == {Fraction(1)}

    # Pointwise local exchange at one exact time, not a numerical time grid.
    weights = list(range(1, 10))
    exchange_checks = 0
    for union in combinations(range(9), 6):
        remainder = tuple(i for i in range(9) if i not in union)
        lower, upper = union[:3], union[3:]
        for deletions in range(2, 7):
            sorted_score = (phi_at_log_two(weights, remainder + lower, deletions)
                            + phi_at_log_two(weights, remainder + upper, deletions))
            for others in combinations(union[1:], 2):
                first = (union[0], *others)
                second = tuple(i for i in union if i not in first)
                score = (phi_at_log_two(weights, remainder + first, deletions)
                         + phi_at_log_two(weights, remainder + second, deletions))
                assert sorted_score >= score
                exchange_checks += 1

    print("all-horizon intact groups: "
          f"{integral_checks} exact integral/DP checks, "
          f"{optimal_horizons} global horizon optima, "
          f"{exchange_checks} pointwise exchanges")


if __name__ == "__main__":
    main()
