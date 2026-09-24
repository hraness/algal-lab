"""Bounded exact checks for fixed softmax allocation formulas.

This finite checker does not claim theorem origination or establish the
universal theorem. It accepts no external inputs and writes no files.
"""
from fractions import Fraction as F
from itertools import product

from research.spikes.stochastic.softmax_spread import _softmax


def _profiles():
    values = (F(0), F(1, 2), F(1))
    result = tuple(row for row in product(values, repeat=3)
                   if sum(row) <= 1)
    assert len(result) == 10
    return result


def _is_permutation(matrix):
    return (all(sum(row) == 1 and all(value in (0, 1) for value in row)
                for row in matrix)
            and all(sum(matrix[i][j] for i in range(3)) == 1
                    for j in range(3)))


def _small_allocation_checks():
    profiles = _profiles()
    matrices = tuple(product(profiles, repeat=3))
    assert len(matrices) == 1000
    positive_column_factor = F(256, 258)
    positive_values = []
    negative_values = []
    positive_maximizers = 0
    negative_maximizers = 0

    for matrix in matrices:
        columns = tuple(tuple(matrix[i][j] for i in range(3))
                        for j in range(3))
        positive_scores = tuple(_softmax(column, 1) for column in columns)
        negative_scores = tuple(_softmax(column, -1) for column in columns)

        for column, positive_score, negative_score in zip(
                columns, positive_scores, negative_scores):
            assert positive_score <= positive_column_factor * sum(column)
            assert negative_score <= sum(column) / 3

        # The outer temperature is ZERO: take the arithmetic mean of task
        # scores. Row budgets bound total allocation by three.
        positive_outer = sum(positive_scores, F(0)) / 3
        negative_outer = sum(negative_scores, F(0)) / 3
        assert positive_outer <= positive_column_factor
        assert negative_outer <= F(1, 3)
        if positive_outer == positive_column_factor:
            assert _is_permutation(matrix)
            positive_maximizers += 1
        if negative_outer == F(1, 3):
            negative_maximizers += 1
        positive_values.append(positive_outer)
        negative_values.append(negative_outer)

    positive_max = max(positive_values)
    negative_max = max(negative_values)
    permutation_count = sum(_is_permutation(matrix) for matrix in matrices)
    assert positive_max == positive_column_factor
    assert negative_max == F(1, 3)
    assert permutation_count == 6
    assert positive_maximizers == 6
    assert all(positive_values[index] == positive_column_factor
               for index, matrix in enumerate(matrices)
               if _is_permutation(matrix))
    assert negative_maximizers == sum(value == negative_max
                                      for value in negative_values)
    return {
        "allocationGridProfiles": len(profiles),
        "allocationThreeByThreeMatrices": len(matrices),
        "allocationPositiveOuterTemperature": "0",
        "allocationPositiveColumnBoundFactor": "256/258",
        "allocationPositiveMaximum": str(positive_max),
        "allocationPositiveMaximizers": positive_maximizers,
        "allocationPositiveMaximizersArePermutations": True,
        "allocationNegativeOuterTemperature": "0",
        "allocationNegativeMaximum": str(negative_max),
        "allocationNegativeHomogeneousReward": "1/3",
        "allocationNegativeMaximizers": negative_maximizers,
        "allocationNegativeInnerMeanBoundChecks": len(matrices) * 3,
        "allocationPositiveColumnBoundChecks": len(matrices) * 3,
    }


def _base_softmax(values, base: int) -> F:
    """Exact B_{log(base)} on vectors whose entries are zero or one."""
    assert base >= 2 and all(value in (0, 1) for value in values)
    weights = tuple(F(base ** int(value)) for value in values)
    return sum((value * weight for value, weight in zip(values, weights)), F(0)) / sum(weights, F(0))


def _balanced_allocation(n: int, k: int):
    assert n % k == 0
    agents_per_task = n // k
    rows = []
    for agent in range(n):
        task = agent // agents_per_task
        rows.append(tuple(int(task == column) for column in range(n)))
    matrix = tuple(rows)
    assert all(sum(row) == 1 for row in matrix)
    counts = tuple(sum(matrix[i][j] for i in range(n)) for j in range(n))
    assert counts == (agents_per_task,) * k + (0,) * (n - k)
    return matrix, counts


def _divisors(n: int):
    return tuple(k for k in range(2, n) if n % k == 0)


def _balanced_family_checks():
    cases = allocations = row_budget_checks = column_count_checks = 0
    for n in range(4, 33):
        for k in _divisors(n):
            m = n // k
            matrix, counts = _balanced_allocation(n, k)
            allocations += 1
            assert len(matrix) == len(counts) == n
            row_budget_checks += len(matrix)
            column_count_checks += len(counts)
            for E in range(2, 9):
                # A task column with m ones and n-m zeros has exact inner score
                # mE/(mE+n-m)=E/(E+k-1) at t=log(E).
                column = tuple(F(matrix[i][0]) for i in range(n))
                s_direct = _base_softmax(tuple(map(int, column)), E)
                s_expected = F(E, E + k - 1)
                assert s_direct == s_expected
                cases += 1

                power = E + k - 1
                # Since r=E**s and s=E/power, this integer inequality is
                # exactly equivalent to r>power/k.
                left = k ** power * E ** E
                right = power ** power
                assert left > right
                # At matched temperatures, homogeneous columns attain the
                # same optimal reward as full specialization. Both exceed the
                # uniform-across-tasks allocation baseline 1/n.
                homogeneous_optimum = _base_softmax((1,) + (0,) * (n - 1), E)
                full_specialization = F(E, E + n - 1)
                assert homogeneous_optimum == full_specialization
                assert full_specialization > F(1, n)
    return {
        "balancedAllocationFamilyCases": cases,
        "balancedAllocationMatrices": allocations,
        "balancedAllocationRowBudgetChecks": row_budget_checks,
        "balancedAllocationColumnCountChecks": column_count_checks,
    }


def _exact_example_e4():
    n, k, E = 4, 2, 4
    agents_per_task = n // k
    s = F(E, E + k - 1)
    assert s == F(4, 5)
    r_power = E ** E
    assert r_power == 256
    assert 3 ** 5 < r_power < F(31, 10) ** 5
    # Thus 3<r<31/10. The matched reward R=(4/5)r/(r+1)
    # is strictly increasing in r, giving the claimed exact bounds.
    reward_lower = s * F(3, 1) / (F(3, 1) + 1)
    reward_upper = s * F(31, 10) / (F(31, 10) + 1)
    assert reward_lower == F(3, 5)
    assert reward_upper == F(124, 205)
    assert reward_lower < reward_upper
    homogeneous = _base_softmax((1, 0, 0, 0), E)
    full_specialization = F(E, E + n - 1)
    uniform_baseline = F(1, n)
    assert homogeneous == F(4, 7)
    assert full_specialization == F(4, 7)
    assert homogeneous == full_specialization
    gain_lower = reward_lower - full_specialization
    assert gain_lower == F(1, 35)
    return {
        "allocationE4MatchedBase": E,
        "allocationE4MatchedTemperature": "t=tau=ln(4)",
        "allocationE4N": n,
        "allocationE4K": k,
        "allocationE4AgentsPerTask": agents_per_task,
        "allocationE4TaskScore": str(s),
        "allocationE4RPower5": r_power,
        "allocationE4RLowerPower": "3^5=243",
        "allocationE4RUpperPower": "(31/10)^5=28629151/100000",
        "allocationE4RewardInterval": (str(reward_lower), str(reward_upper)),
        "allocationE4HomogeneousOptimum": str(homogeneous),
        "allocationE4FullSpecializationReward": str(full_specialization),
        "allocationE4UniformAllocationBaseline": str(uniform_baseline),
        "allocationE4RewardStrictlyExceedsFullSpecializationByMoreThan": str(gain_lower),
    }


def _exact_example_e2():
    n, k, E = 4, 2, 2
    agents_per_task = n // k
    s = F(E, E + k - 1)
    assert s == F(2, 3)
    r_power = E ** E
    assert r_power == 4
    threshold = F(19, 12)
    assert 4 * 12 ** 3 > 19 ** 3
    assert r_power > threshold ** 3
    reward_lower = s * threshold / (threshold + 1)
    assert reward_lower == F(38, 93)

    homogeneous = _base_softmax((1, 0, 0, 0), E)
    full_specialization = F(E, E + n - 1)
    uniform_baseline = F(1, n)
    assert homogeneous == full_specialization == F(2, 5)
    assert uniform_baseline == F(1, 4)
    gain_lower = reward_lower - full_specialization
    assert gain_lower == F(4, 465)
    return {
        "allocationE2MatchedBase": E,
        "allocationE2MatchedTemperature": "t=tau=ln(2)",
        "allocationE2N": n,
        "allocationE2K": k,
        "allocationE2AgentsPerTask": agents_per_task,
        "allocationE2TaskScore": str(s),
        "allocationE2RPower3": r_power,
        "allocationE2RLowerBound": str(threshold),
        "allocationE2RLowerPowerNumerators": ("19^3=6859", "4*12^3=6912"),
        "allocationE2RewardStrictLowerBound": str(reward_lower),
        "allocationE2HomogeneousOptimum": str(homogeneous),
        "allocationE2FullSpecializationReward": str(full_specialization),
        "allocationE2UniformAllocationBaseline": str(uniform_baseline),
        "allocationE2RewardStrictlyExceedsFullSpecializationByMoreThan": str(gain_lower),
    }


def _integer_partitions(total, maximum=None):
    if total == 0:
        yield ()
        return
    if maximum is None:
        maximum = total
    for first in range(min(total, maximum), 0, -1):
        for tail in _integer_partitions(total - first, first):
            yield (first, *tail)


def _occupancy_allocation(n, occupancies):
    assert len(occupancies) <= n and sum(occupancies) == n
    rows = []
    task = 0
    remaining = occupancies[0] if occupancies else 0
    for _agent in range(n):
        while remaining == 0:
            task += 1
            remaining = occupancies[task] if task < len(occupancies) else 0
        row = tuple(int(column == task) for column in range(n))
        rows.append(row)
        remaining -= 1
    matrix = tuple(rows)
    counts = tuple(sum(matrix[i][j] for i in range(n)) for j in range(n))
    expected = tuple(occupancies) + (0,) * (n - len(occupancies))
    assert counts == expected
    assert all(sum(row) == 1 for row in matrix)
    return matrix, counts


def _occupancy_partition_checks():
    total_partitions = total_cases = nonendpoint_partitions = 0
    nonendpoint_cases = row_checks = column_checks = 0
    per_size = []
    for n in range(3, 13):
        partitions = tuple(_integer_partitions(n))
        assert len(partitions) == len(set(partitions))
        total_partitions += len(partitions)
        size_nonendpoint = size_cases = 0
        for partition in partitions:
            occupancies = partition + (0,) * (n - len(partition))
            assert len(occupancies) == n and sum(occupancies) == n
            matrix, counts = _occupancy_allocation(n, partition)
            assert counts == occupancies
            row_checks += len(matrix)
            column_checks += len(counts)
            nonendpoint = partition not in ((n,), (1,) * n)
            size_nonendpoint += int(nonendpoint)
            total_cases += 7
            size_cases += 7
            nonendpoint_cases += 7 * int(nonendpoint)

            for E in range(2, 9):
                h = F(E, E + n - 1)
                strict_contribution = False
                for m in partition:
                    P = m * E + n - m
                    D = F(P, n)
                    s = F(m * E, P)
                    assert s - h == h * F(m - 1, 1) / D
                    power_left = n ** P * E ** (m * E)
                    power_right = P ** P
                    if m == n:
                        assert power_left == power_right
                        assert s == 1 and D == E
                    else:
                        assert power_left > power_right
                        # Raising positive quantities to the integer power P
                        # makes this inequality exactly equivalent to
                        # E**s > D, without evaluating an irrational power.
                    if 0 < m < n and m > 1:
                        strict_contribution = True
                assert strict_contribution == nonendpoint

        per_size.append({
            "n": n,
            "integerPartitionCount": len(partitions),
            "nonendpointPartitionCount": size_nonendpoint,
            "occupancyBaseCases": size_cases,
        })
        nonendpoint_partitions += size_nonendpoint
    assert total_partitions == 268
    assert total_cases == 1876
    assert nonendpoint_partitions == 248
    assert nonendpoint_cases == 1736
    return {
        "occupancySizes": tuple(range(3, 13)),
        "occupancyTotalIntegerPartitions": total_partitions,
        "occupancyFormulaCases": total_cases,
        "occupancyNonendpointPartitions": nonendpoint_partitions,
        "occupancyNonendpointCases": nonendpoint_cases,
        "occupancyRowBudgetChecks": row_checks,
        "occupancyColumnCountChecks": column_checks,
        "occupancyPerSizeCounts": tuple(per_size),
        "occupancyCheckedIdentity": "s-h = h*(m-1)/D; P=mE+n-m; D=P/n; s=mE/P",
        "occupancyCheckedPowerInequality": "n^P * E^(mE) > P^P for 0<m<n; equality for m=n",
    }


def _minimal_pure_class_example():
    n, k, E = 3, 2, 2
    occupancies = (2, 1, 0)
    allocation, counts = _occupancy_allocation(n, occupancies[:2])
    assert counts == occupancies
    assert all(sum(row) == 1 for row in allocation)

    scores = tuple(_base_softmax(tuple(allocation[i][j] for i in range(n)), E)
                   for j in range(n))
    assert scores == (F(4, 5), F(1, 2), F(0))
    assert scores == (F(2 * E, 2 * E + n - 2),
                      F(E, E + n - 1), F(0))
    homogeneous = _base_softmax((1, 0, 0), E)
    assert homogeneous == F(1, 2)

    # Let r=2^(4/5), q=sqrt(2). The pure-class team reward R obeys
    # R-h=(3r-5)/(10(r+q+1)). Its partial derivatives have signs given by
    # 3q+8>0 and -(3r-5)<0, respectively, so exact bounds suffice.
    assert 12 ** 5 < 16 * 7 ** 5
    r_lower = F(12, 7)
    assert 2 < F(9, 4)  # q^2=2 < (3/2)^2, hence q<3/2.
    q_upper = F(3, 2)
    assert 3 * r_lower - 5 == F(1, 7) > 0
    assert 3 * q_upper + 8 > 0
    lower_gap = (3 * r_lower - 5) / (10 * (r_lower + q_upper + 1))
    assert lower_gap == F(1, 295)
    return {
        "minimalPureClassN": n,
        "minimalPureClassK": k,
        "minimalPureClassBase": E,
        "minimalPureClassTemperature": "t=tau=ln(2)",
        "minimalPureClassOccupancies": occupancies,
        "minimalPureClassScores": tuple(map(str, scores)),
        "minimalPureClassHomogeneousOptimum": str(homogeneous),
        "minimalPureClassRPower5": 16,
        "minimalPureClassRLowerBound": "12/7",
        "minimalPureClassRLowerPowerCheck": "12^5=248832 < 16*7^5=268912",
        "minimalPureClassQUpperBound": "3/2",
        "minimalPureClassQUpperSquareCheck": "2 < 9/4",
        "minimalPureClassRewardGapStrictlyGreaterThan": str(lower_gap),
    }


def verify():
    """Run fixed, finite exact allocation and reward checks."""
    return {
        **_small_allocation_checks(),
        **_balanced_family_checks(),
        **_exact_example_e4(),
        **_exact_example_e2(),
        **_occupancy_partition_checks(),
        **_minimal_pure_class_example(),
        "allocationOuterTemperatureScope": "Small-grid enumeration uses outer temperature zero only.",
        "allocationFormulaOrigin": "Fixed formulas are checked here; this finite verifier does not prove the universal theorem.",
    }


if __name__ == "__main__":
    print("softmax allocation checks:", verify())
