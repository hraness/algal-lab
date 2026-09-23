from fractions import Fraction
from itertools import combinations
import unittest

from research.two_failure_groups import (
    adjacent_all_groups,
    expected_group_counts,
    optimal_triples_after_two_deletions,
    three_partition_reduction,
    universal_regret_bound,
)


def partitions(vertices, r):
    if not vertices:
        yield []
        return
    first, *tail = vertices
    for chosen in combinations(tail, r - 1):
        group = [first, *chosen]
        remaining = [v for v in tail if v not in chosen]
        for rest in partitions(remaining, r):
            yield [group, *rest]


def direct_ordered_deletions(weights, groups):
    """Independent two-step enumeration; no closed pair-probability formula."""
    n = len(weights)
    W = sum(weights)
    r = len(groups[0])
    all_score = Fraction(0)
    majority_score = Fraction(0)
    same = Fraction(0)
    for first in range(n):
        for second in range(n):
            if first == second:
                continue
            probability = Fraction(weights[first], W) * Fraction(weights[second], W - weights[first])
            counts = [r - int(first in group) - int(second in group) for group in groups]
            all_score += probability * sum(count == r for count in counts)
            majority_score += probability * sum(count >= r - 1 for count in counts)
            same += probability * int(any(first in group and second in group for group in groups))
    return same, all_score, majority_score


class TwoFailureGroupsTests(unittest.TestCase):
    def test_formula_against_ordered_deletion_enumeration(self):
        checked = 0
        for weights, r in (([1, 2, 3, 4, 5, 6], 3),
                           ([1, 2, 3, 4, 5, 6, 7, 8], 4),
                           ([1, 2, 3, 4, 5, 6, 7, 8, 9], 3)):
            for groups in partitions(list(range(len(weights))), r):
                expected = direct_ordered_deletions(weights, groups)
                actual = expected_group_counts({"weights": weights, "groups": groups})
                self.assertEqual((actual["same_group_probability"], actual["all"],
                                  actual["at_least_r_minus_one"]), expected)
                self.assertEqual(actual["survivors"], len(weights) - 2)
                checked += 1
        self.assertEqual(checked, 325)

    def test_adjacent_all_optimum_and_majority_magnitude_dependence(self):
        for weights in ([1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 9],
                        [1, 2, 3, 4, 5, 6, 7, 8, 9]):
            optimum = optimal_triples_after_two_deletions(weights, 3)
            adjacent = adjacent_all_groups(weights, 3)
            self.assertEqual(optimum["groups"], adjacent)
            self.assertEqual(optimum["tie_count"], 1)
            self.assertEqual(optimum["score"], expected_group_counts(
                {"weights": weights, "groups": adjacent})["all"])
        self.assertEqual(optimal_triples_after_two_deletions(
            [1, 2, 3, 4, 5, 6], 2)["groups"], [[0, 2, 5], [1, 3, 4]])
        self.assertEqual(optimal_triples_after_two_deletions(
            [1, 2, 3, 4, 5, 9], 2)["groups"], [[0, 1, 5], [2, 3, 4]])
        self.assertEqual(adjacent_all_groups([6, 1, 5, 2, 4, 3], 3),
                         [[1, 3, 5], [4, 2, 0]])

    def test_reduction_threshold_separates_yes_and_no_instances(self):
        cases = (
            ([5, 5, 5, 5, 6, 6], True),
            ([5, 5, 5, 5, 5, 7], False),
            ([5, 5, 5, 5, 5, 5, 6, 6, 6], True),
            ([5, 5, 5, 5, 5, 5, 5, 6, 7], False),
        )
        for items, yes in cases:
            construction = three_partition_reduction(items, 16)
            weights = construction["weights"]
            best = optimal_triples_after_two_deletions(weights, 2)
            self.assertEqual(best["score"] >= construction["threshold"], yes)
            if yes:
                self.assertEqual(best["score"], construction["baseline"])
            else:
                self.assertLess(best["score"], construction["baseline"] -
                                construction["no_instance_gap_lower_bound"])
            self.assertEqual(construction["denominator_bound"],
                             2 * (sum(weights) - len(items) * 16**3)**2)
            self.assertLessEqual(construction["threshold"].denominator,
                                 construction["denominator_bound"])

    def test_universal_additive_regret_bound(self):
        self.assertEqual(universal_regret_bound([10] * 6, 3), 0)
        for weights, r in (([100, 101, 102, 103, 104, 105], 3),
                           (list(range(100, 108)), 4),
                           (list(range(100, 109)), 3)):
            bound = universal_regret_bound(weights, r)
            self.assertLess(bound, 1)
            scores = [expected_group_counts({"weights": weights, "groups": groups})
                      for groups in partitions(list(range(len(weights))), r)]
            for objective in ("all", "at_least_r_minus_one"):
                values = [score[objective] for score in scores]
                self.assertLessEqual(max(values) - min(values), bound)
        self.assertEqual(universal_regret_bound([1, 2, 3, 4, 5, 6], 3), Fraction(3, 4))
        self.assertEqual(universal_regret_bound([1, 1, 1, 1, 100, 100], 3), 1)

    def test_admission(self):
        valid = {"weights": [1, 2, 3, 4, 5, 6],
                 "groups": [[0, 1, 2], [3, 4, 5]]}
        invalid = [
            {**valid, "extra": 1},
            {"weights": [1, 2, 3, 4, 5, True], "groups": valid["groups"]},
            {"weights": [1, 2, 3, 4, 5, 10**19], "groups": valid["groups"]},
            {"weights": valid["weights"], "groups": [[0, 1, 2], [3, 4, 4]]},
            {"weights": valid["weights"], "groups": [[0, 1, 2], [3, 4, True]]},
            {"weights": valid["weights"], "groups": [[0, 1], [2, 3, 4, 5]]},
            {"weights": valid["weights"], "groups": [[0, 1, 2, 3, 4, 5]]},
            {"weights": valid["weights"], "groups": []},
        ]
        for spec in invalid:
            with self.subTest(spec=spec), self.assertRaises(ValueError):
                expected_group_counts(spec)
        for weights, group_size in (([1, 2, 3, True], 2), ([1, 2, 3, 4], True),
                                    ([1, 2, 3, 4, 5], 2), ([1, 2, 3, 4], 4)):
            with self.assertRaises(ValueError):
                adjacent_all_groups(weights, group_size)
            with self.assertRaises(ValueError):
                universal_regret_bound(weights, group_size)
        for weights, threshold in (([1, 2, 3, 4, 5, 6], True),
                                   ([1, 2, 3, 4, 5, 6], 1),
                                   ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 2)):
            with self.assertRaises(ValueError):
                optimal_triples_after_two_deletions(weights, threshold)
        for items, target in (([5, 5, 5, 5, 6, True], 16),
                              ([5, 5, 5, 5, 6, 6], True),
                              ([5, 5, 5, 5, 5, 5], 16),
                              ([5, 5, 5, 5, 6, 7], 16)):
            with self.assertRaises(ValueError):
                three_partition_reduction(items, target)


if __name__ == "__main__":
    unittest.main()
