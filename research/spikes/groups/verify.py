"""Compact public exact checks for the two-deletion group theorem and boundary."""
from fractions import Fraction

from research.two_failure_groups import (
    adjacent_all_groups,
    expected_group_counts,
    optimal_triples_after_two_deletions,
    three_partition_reduction,
    universal_regret_bound,
)


def main() -> None:
    n6 = [1, 2, 3, 4, 5, 6]
    contiguous = adjacent_all_groups(n6, 3)
    all_optimum = optimal_triples_after_two_deletions(n6, 3)
    majority = optimal_triples_after_two_deletions(n6, 2)
    assert all_optimum["groups"] == contiguous
    assert all_optimum["score"] == Fraction(19351, 38760)
    assert majority["groups"] == [[0, 2, 5], [1, 3, 4]]
    assert majority["score"] == Fraction(190001, 116280)
    assert majority["score"] > expected_group_counts(
        {"weights": n6, "groups": contiguous})["at_least_r_minus_one"]

    changed = optimal_triples_after_two_deletions([1, 2, 3, 4, 5, 9], 2)
    assert changed["groups"] == [[0, 1, 5], [2, 3, 4]]
    assert changed["tie_count"] == majority["tie_count"] == 1

    n9 = list(range(1, 10))
    all_n9 = optimal_triples_after_two_deletions(n9, 3)
    assert all_n9["groups"] == adjacent_all_groups(n9, 3)
    assert all_n9["partitions_examined"] == 280

    regret_checks = 0
    assert universal_regret_bound([100] * 6, 3) == 0
    for rates in (list(range(100, 106)), list(range(100, 109))):
        all_best = optimal_triples_after_two_deletions(rates, 3)["score"]
        majority_best = optimal_triples_after_two_deletions(rates, 2)["score"]
        m = len(rates) // 3
        span = all_best + majority_best - (2 * m - 2)
        assert 0 <= span <= universal_regret_bound(rates, 3) < 1
        regret_checks += 1

    reduction_cases = (
        ([5, 5, 5, 5, 6, 6], True),
        ([5, 5, 5, 5, 5, 7], False),
        ([5, 5, 5, 5, 5, 5, 6, 6, 6], True),
        ([5, 5, 5, 5, 5, 5, 5, 6, 7], False),
    )
    reduction_partitions = 0
    for items, yes in reduction_cases:
        certificate = three_partition_reduction(items, 16)
        optimum = optimal_triples_after_two_deletions(certificate["weights"], 2)
        reduction_partitions += optimum["partitions_examined"]
        assert (optimum["score"] >= certificate["threshold"]) == yes
        if yes:
            assert optimum["score"] == certificate["baseline"]
        else:
            assert optimum["score"] < certificate["baseline"] - certificate[
                "no_instance_gap_lower_bound"]

    print("two-deletion groups: exact fractions; 10+280 theorem partitions; "
          f"{reduction_partitions} reduction partitions; 4 threshold decisions; "
          f"{regret_checks + 1} regret bounds passed")


if __name__ == "__main__":
    main()
