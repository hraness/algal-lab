"""Focused admission and independent deletion-order checks."""
from fractions import Fraction
from itertools import combinations, permutations
import unittest

from research.intact_groups import (
    exact_intact_count,
    group_inclusion_probabilities,
    optimal_intact_groups,
)


def partitions(vertices, r):
    if not vertices:
        yield []
        return
    first, *rest = vertices
    for others in combinations(rest, r - 1):
        group = [first, *others]
        remaining = [i for i in rest if i not in others]
        for tail in partitions(remaining, r):
            yield [group, *tail]


def ordered_deletion_group_probabilities(weights, r, k):
    """Enumerate deletion sequences, independently of subset-state DP."""
    n = len(weights)
    answer = {group: Fraction(0) for group in combinations(range(n), r)}
    for removed in permutations(range(n), n - k):
        probability = Fraction(1)
        total = sum(weights)
        for i in removed:
            probability *= Fraction(weights[i], total)
            total -= weights[i]
        alive = set(range(n)) - set(removed)
        for group in answer:
            if all(i in alive for i in group):
                answer[group] += probability
    return answer


class IntactGroupsTests(unittest.TestCase):
    def test_exact_probability_against_ordered_deletions(self):
        weights = [1, 3, 5, 7, 9, 11]
        for k in range(7):
            actual = group_inclusion_probabilities(weights, 3, k)
            self.assertEqual(actual, ordered_deletion_group_probabilities(weights, 3, k))
            self.assertEqual(sum(actual.values(), Fraction(0)), Fraction(k * (k - 1) * (k - 2), 6)
                             if k >= 3 else Fraction(0))

    def test_all_horizons_and_uniqueness_at_six_vertices(self):
        weights = [1, 2, 3, 4, 5, 6]
        optimum = optimal_intact_groups(weights, 3)["groups"]
        self.assertEqual(optimum, [[0, 1, 2], [3, 4, 5]])
        candidates = list(partitions(list(range(6)), 3))
        self.assertEqual(len(candidates), 10)
        for k in range(7):
            q = group_inclusion_probabilities(weights, 3, k)
            score = lambda p: sum((q[tuple(group)] for group in p), Fraction(0))
            best = max(score(p) for p in candidates)
            self.assertEqual(score(optimum), best)
            if k in (3, 4):
                self.assertEqual(sum(score(p) == best for p in candidates), 1)
            self.assertEqual(exact_intact_count(
                {"weights": weights, "groups": optimum, "survivors": k}), best)

    def test_sorting_relabeling_ties_and_large_constructor(self):
        self.assertEqual(optimal_intact_groups([6, 1, 5, 2, 4, 3], 3)["groups"],
                         [[1, 3, 5], [4, 2, 0]])
        self.assertEqual(optimal_intact_groups([1, 1, 2, 2], 2)["groups"],
                         [[0, 1], [2, 3]])
        large = optimal_intact_groups(list(range(96, 0, -1)), 3)
        self.assertEqual(len(large["groups"]), 32)
        self.assertEqual(large["groups"][0], [95, 94, 93])
        self.assertEqual(large["probabilityEvaluations"], 0)
        self.assertEqual(sorted(i for group in large["groups"] for i in group), list(range(96)))

    def test_admission(self):
        for weights, r in (([1, 2, 3], 2), ([1, 2, 3, 4], True),
                           ([1, 2, 3, 4, 5], 2), ([1, 2, 3, 4], 4),
                           ([1, 2, 3, False], 2), ([1, 2, 3, 10**19], 2),
                           ([1] * 97, 2)):
            with self.assertRaises(ValueError):
                optimal_intact_groups(weights, r)
        for weights, r, k in (([1] * 14, 2, 3), ([1, 2, 3, 4], 2, True),
                              ([1, 2, 3, 4], 2, 5), ([1, 2, 3, 4], 3, 2)):
            with self.assertRaises(ValueError):
                group_inclusion_probabilities(weights, r, k)
        valid = {"weights": [1, 2, 3, 4, 5, 6],
                 "groups": [[0, 1, 2], [3, 4, 5]], "survivors": 3}
        invalid = [
            {**valid, "extra": 1},
            {**valid, "groups": [[0, 1, 2], [3, 4, 4]]},
            {**valid, "groups": [[0, 1, 2], [3, 4, True]]},
            {**valid, "groups": [[0, 1], [2, 3, 4, 5]]},
            {**valid, "survivors": 2.0},
        ]
        for spec in invalid:
            with self.subTest(spec=spec), self.assertRaises(ValueError):
                exact_intact_count(spec)


if __name__ == "__main__":
    unittest.main()
