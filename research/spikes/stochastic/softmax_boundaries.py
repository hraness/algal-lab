"""Bounded exact checks for two-agent optima and pure-allocation asymptotics.

Finite examples supplement the analytic proofs. There are no external inputs,
network operations, file writes, or model calls.
"""
from fractions import Fraction as F
from math import isqrt
from itertools import product

from research.spikes.stochastic.softmax_allocation import _integer_partitions


def _two_mean(x: F, y: F, log2_factor: int) -> F:
    exponent = log2_factor * (x - y)
    assert exponent.denominator == 1
    weight = F(2) ** exponent.numerator
    return (x * weight + y) / (weight + 1)


def _two_agent_grid():
    grid = tuple(F(i, 4) for i in range(5))
    temperatures = (-8, -4, 0, 4, 8)
    cases = positive_cases = 0
    for inner, outer in product(temperatures, repeat=2):
        maximum = F(2) ** max(inner, outer, 0)
        maximum /= maximum + 1
        homogeneous = F(2) ** max(outer, 0)
        homogeneous /= homogeneous + 1
        observed = []
        observed_homogeneous = []
        maximizers = set()
        for a, b in product(grid, repeat=2):
            first = _two_mean(a, b, inner)
            second = _two_mean(1-a, 1-b, inner)
            assert first - second == a + b - 1
            reward = _two_mean(first, second, outer)
            assert reward <= maximum
            observed.append(reward)
            if a == b:
                observed_homogeneous.append(reward)
            if reward == maximum:
                maximizers.add((a, b))
            cases += 1
        assert max(observed) == maximum
        assert max(observed_homogeneous) == homogeneous
        if inner > 0 and outer > 0:
            concentration = {(F(0), F(0)), (F(1), F(1))}
            permutation = {(F(1), F(0)), (F(0), F(1))}
            expected = (concentration if outer > inner else permutation
                        if inner > outer else concentration | permutation)
            assert maximizers == expected
            positive_cases += len(observed)
    return {"twoAgentExactFullBudgetCases": cases,
            "twoAgentTemperaturePairs": len(temperatures) ** 2,
            "twoAgentPositiveOptimizerCases": positive_cases,
            "twoAgentPartialBudgetScope": "Arbitrary unused budgets are handled by the analytic proof, not this grid."}


def _cubic_score(partition):
    n = sum(partition)
    return sum(m * (m - 1) * (n - m) for m in partition)


def _large_temperature_coefficient(partition):
    n, k = sum(partition), len(partition)
    return F(n, k) * (1 + sum((F(1, m) for m in partition), F(0))) - 2


def _asymptotic_coefficients():
    small_cases = merge_checks = square_cases = 0
    small_maxima = []
    square_minima = []
    for n in range(3, 21):
        partitions = tuple(_integer_partitions(n))
        scores = [_cubic_score(p) for p in partitions]
        expected = (n - 2) * (n * n // 4)
        assert max(scores) == expected
        assert [p for p, score in zip(partitions, scores) if score == expected] == [((n+1)//2, n//2)]
        for partition, score in zip(partitions, scores):
            assert sum(partition) == n and all(m > 0 for m in partition)
            if len(partition) >= 3:
                a, b = partition[-2:]
                assert 3 * (a+b) <= 2*n
                merged = partition[:-2] + (a+b,)
                increment = a*b*(2*(n+1)-3*(a+b))
                assert increment > 0
                assert _cubic_score(merged)-score == increment
                merge_checks += 1
        small_cases += len(partitions)
        small_maxima.append((n, str(F(expected, 2*n**4))))
    for n in (4, 9, 16, 25):
        r = isqrt(n)
        assert r*r == n
        partitions = tuple(_integer_partitions(n))
        coefficients = [_large_temperature_coefficient(p) for p in partitions]
        expected = F(2*r-2)
        assert min(coefficients) == expected
        assert [p for p, a in zip(partitions, coefficients) if a == expected] == [(r,)*r]
        square_cases += len(partitions)
        square_minima.append((n, str(expected)))
    two_groups, three_groups = (5, 4), (3, 3, 3)
    assert F(_cubic_score(two_groups), 2*9**4) == F(70, 6561)
    assert F(_cubic_score(three_groups), 2*9**4) == F(54, 6561)
    assert _large_temperature_coefficient(two_groups) == F(181, 40)
    assert _large_temperature_coefficient(three_groups) == 4
    return {"smallTemperaturePartitionCases": small_cases,
            "smallTemperatureStrictMergeChecks": merge_checks,
            "smallTemperatureMaximumCoefficients": tuple(small_maxima),
            "largeTemperatureSquarePartitionCases": square_cases,
            "largeTemperatureSquareMinimumCoefficients": tuple(square_minima),
            "nineAgentSmallOptimalOccupancies": two_groups,
            "nineAgentLargeOptimalOccupancies": three_groups,
            "asymptoticScope": "Exact leading coefficients; eventual-optimality and remainders require the analytic proof. No crossover temperature is computed."}


def verify():
    return {**_two_agent_grid(), **_asymptotic_coefficients()}


if __name__ == "__main__":
    print("softmax allocation boundaries:", verify())
