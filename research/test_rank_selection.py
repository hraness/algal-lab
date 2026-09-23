"""Independent categorical integration for the continuous-clock oracle."""

from fractions import Fraction
from itertools import combinations, product
from math import comb
from random import Random
import unittest

from research.rank_selection import (
    ORDERED_EXAMPLE, STOCHASTIC_ONLY_EXAMPLE, admit_histograms,
    ordered_conditions, pair_probabilities,
)


def categorical_oracle(rows, survivors):
    """Condition on interval choices, then uniformly order the cutoff interval."""
    n = len(rows)
    q = {pair: Fraction(0) for pair in combinations(range(n), 2)}
    if survivors < 2:
        return q
    for intervals in product(range(len(rows[0])), repeat=n):
        mass = Fraction(1)
        for i, interval in enumerate(intervals):
            mass *= Fraction(rows[i][interval], sum(rows[i]))
        if not mass:
            continue
        cutoff = sorted(intervals, reverse=True)[survivors - 1]
        above = {i for i, interval in enumerate(intervals) if interval > cutoff}
        at_cutoff = {i for i, interval in enumerate(intervals) if interval == cutoff}
        slots = survivors - len(above)
        for pair in q:
            if any(intervals[i] < cutoff for i in pair):
                continue
            need = len(set(pair) & at_cutoff)
            if need <= slots:
                q[pair] += mass * Fraction(comb(len(at_cutoff) - need, slots - need),
                                            comb(len(at_cutoff), slots))
    return q


class RankSelectionTests(unittest.TestCase):
    def test_independent_integrals(self):
        rng = Random(2026092351)
        fixtures = [ORDERED_EXAMPLE, STOCHASTIC_ONLY_EXAMPLE]
        fixtures += [[[rng.randrange(1, 5) for _ in range(3)] for _ in range(n)]
                     for n in (4, 5, 6)]
        for rows in fixtures:
            for k in range(len(rows) + 1):
                with self.subTest(rows=rows, k=k):
                    q = pair_probabilities(rows, k)
                    self.assertEqual(q, categorical_oracle(rows, k))
                    self.assertEqual(sum(q.values()), Fraction(k * (k - 1), 2))
                    self.assertTrue(all(0 <= value <= 1 for value in q.values()))

    def test_ordered_and_stochastic_counterexample(self):
        self.assertEqual(ordered_conditions(ORDERED_EXAMPLE),
                         {"cdfOrdered": True, "reverseHazardOrdered": True})
        q = pair_probabilities(ORDERED_EXAMPLE, 2)
        self.assertEqual((q[0, 1] + q[2, 3], q[0, 2] + q[1, 3], q[0, 3] + q[1, 2]),
                         (Fraction(731, 1536), Fraction(1781, 6144), Fraction(1439, 6144)))
        self.assertEqual(ordered_conditions(STOCHASTIC_ONLY_EXAMPLE),
                         {"cdfOrdered": True, "reverseHazardOrdered": False})
        q = pair_probabilities(STOCHASTIC_ONLY_EXAMPLE, 2)
        self.assertEqual(q[0, 2] + q[1, 3] - q[0, 3] - q[1, 2], Fraction(-1, 54))
        # A common 10% uniform mixture removes zero bin masses, retaining failure.
        positive = [[9 * x + 1 for x in row] for row in STOCHASTIC_ONLY_EXAMPLE]
        self.assertTrue(ordered_conditions(positive)["cdfOrdered"])
        q = pair_probabilities(positive, 2)
        self.assertLess(q[0, 2] + q[1, 3] - q[0, 3] - q[1, 2], 0)

    def test_boundaries_permutation_and_maximum(self):
        rows = [ORDERED_EXAMPLE[0]] * 9
        for k in (0, 1, 2, 7, 8, 9):
            self.assertEqual(set(pair_probabilities(rows, k).values()),
                             {Fraction(k * (k - 1), 9 * 8)})
        order = [2, 0, 3, 1]
        original = pair_probabilities(ORDERED_EXAMPLE, 2)
        relabeled = pair_probabilities([ORDERED_EXAMPLE[i] for i in order], 2)
        for (i, j), value in relabeled.items():
            self.assertEqual(value, original[tuple(sorted((order[i], order[j])))])
        self.assertEqual(set(pair_probabilities([[64] * 6 for _ in range(9)], 8).values()),
                         {Fraction(7, 9)})

    def test_strict_admission(self):
        for rows in (None, {}, [], [[1]] * 3, [[1]] * 10, [[1] * 7] * 4,
                     [[0]] * 4, [[True]] * 4, [[1.0]] * 4, [[65]] * 4,
                     [[-1]] * 4, [["1"]] * 4, [[1], [1], [1], [1, 2]],
                     [[float("nan")]] * 4, [[1], [1], [1], None]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                admit_histograms(rows)
        for k in (True, -1, 5, 2.0, "2", None):
            with self.subTest(k=k), self.assertRaises(ValueError):
                pair_probabilities(ORDERED_EXAMPLE, k)


if __name__ == "__main__":
    unittest.main()
