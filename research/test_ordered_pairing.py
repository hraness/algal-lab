from fractions import Fraction
from itertools import combinations_with_replacement
import unittest

from research.ordered_pairing import optimal_pairing
from research.survivor_order import pair_inclusion_probabilities


def matchings(vertices):
    if not vertices:
        yield []
        return
    first, *rest = vertices
    for i, other in enumerate(rest):
        for tail in matchings(rest[:i] + rest[i + 1:]):
            yield [(first, other), *tail]


class OrderedPairingTests(unittest.TestCase):
    def test_all_small_profiles_and_all_matchings(self):
        # Independent subset DP supplies the objective; the optimizer uses only
        # a rate ordering. Compare every matching at every nontrivial horizon.
        checked = 0
        for n in (4, 6):
            alternatives = list(matchings(list(range(n))))
            for profile in combinations_with_replacement(range(1, 4), n):
                weights = list(profile)
                for k in range(2, n):
                    q = pair_inclusion_probabilities(weights, k)
                    def score(pairs):
                        return sum((q[tuple(sorted(p))] for p in pairs), Fraction(0))
                    values = [score(p) for p in alternatives]
                    self.assertEqual(score(optimal_pairing(weights, "both")["pairs"]), max(values))
                    # OR objective is sum of fixed single-node inclusion
                    # probabilities minus this joint-probability sum.
                    self.assertEqual(score(optimal_pairing(weights, "either")["pairs"]), min(values))
                    checked += len(alternatives) * 2
        self.assertEqual(checked, 3540)

    def test_relabeling_and_large_population_without_probability_work(self):
        self.assertEqual(optimal_pairing([4, 1, 3, 2], "both")["pairs"], [[0, 2], [1, 3]])
        self.assertEqual(optimal_pairing([4, 1, 3, 2], "either")["pairs"], [[0, 1], [2, 3]])
        result = optimal_pairing(list(range(128, 0, -1)), "either")
        self.assertEqual(len(result["pairs"]), 64)
        self.assertEqual(result["probabilityEvaluations"], 0)
        self.assertEqual(sorted(v for pair in result["pairs"] for v in pair), list(range(128)))

    def test_admission(self):
        for weights, objective in [([1, 2, 3], "both"), ([0, 1], "both"),
                                   ([True, 2], "either"), ([float("nan"), 1], "both"),
                                   ([1, float("inf")], "both"), ([1, 2], "sum"),
                                   ([1] * 130, "both"), ([1, 1_000_001], "both"),
                                   ([10 ** 1000, 1], "both")]:
            with self.assertRaises(ValueError):
                optimal_pairing(weights, objective)


if __name__ == "__main__":
    unittest.main()
