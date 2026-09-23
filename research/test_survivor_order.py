"""Focused exact checks for the bounded survivor-order conjecture judge."""
from fractions import Fraction
from itertools import combinations, permutations
import unittest

from research.survivor_order import (admit_claim, admit_weights, judge,
                                     one_deletion_pair_probabilities,
                                     pair_inclusion_probabilities)


def permutation_reference(weights, survivors):
    """Enumerate ordered deletion prefixes, independent of subset DP."""
    n = len(weights)
    result = {pair: Fraction(0) for pair in combinations(range(n), 2)}
    deleted = n - survivors
    for order in permutations(range(n), deleted):
        alive = set(range(n))
        probability = Fraction(1)
        for node in order:
            probability *= Fraction(weights[node], sum(weights[i] for i in alive))
            alive.remove(node)
        for pair in combinations(sorted(alive), 2):
            result[pair] += probability
    return result


class SurvivorOrderTests(unittest.TestCase):
    def test_subset_dp_against_independent_order_enumeration(self):
        for weights in ([1, 2, 3, 4], [2, 2, 1, 3], [1, 3, 2, 1, 2]):
            for survivors in range(2, len(weights) - 1):
                with self.subTest(weights=weights, survivors=survivors):
                    self.assertEqual(pair_inclusion_probabilities(weights, survivors),
                                     permutation_reference(weights, survivors))

    def test_one_deletion_dp_matches_analytic_fixture(self):
        weights = [2, 5, 1, 4, 3]
        total = sum(weights)
        actual = one_deletion_pair_probabilities(weights)
        for i, j in combinations(range(len(weights)), 2):
            self.assertEqual(actual[i, j], Fraction(total - weights[i] - weights[j], total))
        self.assertEqual(actual, pair_inclusion_probabilities(weights, len(weights) - 1))

    def test_judge_counts_all_quadruples_and_selected_horizons(self):
        claim = {"expression": "sum_adjacent_vs_crossing", "relation": "ge", "horizons": "all"}
        self.assertEqual(judge([{"weights": [1, 1, 1, 1]}, {"weights": [2, 2, 2, 2, 2]}], claim),
                         {"status": "passed", "passedCount": 11})
        interior = {**claim, "horizons": "interior"}
        self.assertEqual(judge([{"weights": [1, 1, 1, 1]}], interior),
                         {"status": "passed", "passedCount": 0})

    def test_strict_contract_and_bounds(self):
        for raw in (None, (1, 2, 3, 4), [1, 2, 3], [1] * 10, [True, 1, 1, 1],
                    [0, 1, 1, 1], [13, 1, 1, 1], [1.0, 1, 1, 1]):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                admit_weights(raw)
        good = {"expression": "product_crossing_vs_nested", "relation": "le", "horizons": "pair"}
        for raw in (None, {}, {**good, "extra": 1}, {**good, "relation": True},
                    {**good, "expression": "arbitrary formula"}, {**good, "horizons": [2]}):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                admit_claim(raw)
        for environments in (None, [], [{"weights": [1, 2, 3, 4], "values": []}],
                             [{"weights": (1, 2, 3, 4)}]):
            with self.subTest(environments=environments), self.assertRaises(ValueError):
                judge(environments, good)
        for horizon in (True, 1, 5):
            with self.subTest(horizon=horizon), self.assertRaises(ValueError):
                pair_inclusion_probabilities([1, 2, 3, 4], horizon)


if __name__ == "__main__":
    unittest.main()
