"""Focused tests against independent rank and slower minimizer references."""
from fractions import Fraction
import unittest

from research.context_certificate import (
    CONTINUOUS_TWO_BACKGROUND_WITNESS,
    GapMinimum,
    TWO_BACKGROUND_NECESSARY,
    UNIVERSAL_BEYOND_HAZARD_ORDERS,
    small_background_minima,
    threshold_gaps,
    universal_gap_minima,
)
from research.rank_selection import ORDERED_EXAMPLE, STOCHASTIC_ONLY_EXAMPLE, ordered_conditions
from research.spikes.context.verify import (
    DEGENERATE_EXAMPLE,
    DIAGONAL_EXAMPLE,
    VERTEX_EXAMPLE,
    direct_gaps,
    effective_thresholds,
    slow_minima,
    slow_small_background_minima,
)


class ContextCertificateTests(unittest.TestCase):
    def test_conditional_gaps_from_direct_rank_probabilities(self):
        cases = (
            (ORDERED_EXAMPLE, [], 2),
            (STOCHASTIC_ONLY_EXAMPLE, [1], 2),
            (VERTEX_EXAMPLE, [Fraction(1, 3), Fraction(5, 3)], 3),
            (DEGENERATE_EXAMPLE, [1, 1, 1], 3),
            (list(reversed(ORDERED_EXAMPLE)), [0, Fraction(3, 2), 3], 4),
            (DIAGONAL_EXAMPLE, [-1, 4], 3),
        )
        for rows, background, k in cases:
            with self.subTest(rows=rows, background=background, k=k):
                lower, upper = effective_thresholds(background, k, len(rows[0]))
                self.assertEqual(threshold_gaps(rows, lower, upper),
                                 direct_gaps(rows, background, k))

    def test_global_and_small_background_minima(self):
        for rows in (STOCHASTIC_ONLY_EXAMPLE, VERTEX_EXAMPLE, DIAGONAL_EXAMPLE,
                     DEGENERATE_EXAMPLE):
            self.assertEqual(tuple(x.value for x in universal_gap_minima(rows)),
                             slow_minima(rows))
            self.assertEqual(small_background_minima(rows),
                             slow_small_background_minima(rows))
        self.assertEqual(universal_gap_minima(STOCHASTIC_ONLY_EXAMPLE)[1].value,
                         Fraction(-1, 54))
        interior = universal_gap_minima(VERTEX_EXAMPLE)[1]
        self.assertEqual(interior, GapMinimum(Fraction(-645, 13312),
                                               Fraction(241, 208), Fraction(59, 32)))
        diagonal = universal_gap_minima(DIAGONAL_EXAMPLE)[1]
        self.assertEqual(diagonal, GapMinimum(Fraction(-578, 64575),
                                               Fraction(294, 205), Fraction(294, 205)))

    def test_witnesses_and_permutation_direction(self):
        for rows in (VERTEX_EXAMPLE, DIAGONAL_EXAMPLE):
            result = universal_gap_minima(rows)
            for gap, witness in enumerate(result):
                self.assertEqual(threshold_gaps(rows, witness.lower, witness.upper)[gap],
                                 witness.value)
                self.assertEqual(direct_gaps(rows, [witness.lower, witness.upper], 3)[gap],
                                 witness.value)
        misordered = universal_gap_minima([ORDERED_EXAMPLE[i] for i in (0, 2, 1, 3)])
        self.assertLess(misordered[0].value, 0)

    def test_universal_example_outside_both_hazard_orders(self):
        rows = UNIVERSAL_BEYOND_HAZARD_ORDERS
        self.assertEqual(ordered_conditions(rows),
                         {"cdfOrdered": True, "reverseHazardOrdered": False})
        self.assertEqual(tuple(x.value for x in universal_gap_minima(rows)),
                         (Fraction(0), Fraction(0)))
        self.assertEqual(slow_minima(rows), (Fraction(0), Fraction(0)))

        normalized = [[Fraction(x, sum(row)) for x in row] for row in rows]
        before = [Fraction(0)] * 4
        for bin in range(5):
            density = [row[bin] for row in normalized]
            for local in (0, 1):
                F = [before[i] + density[i] * local for i in range(4)]
                c1 = ((density[0] * F[3] - density[3] * F[0]) * (F[2] - F[1])
                      + (F[3] - F[0]) * (density[1] * F[2] - density[2] * F[1]))
                c2 = ((density[0] * F[1] - density[1] * F[0]) * (F[3] - F[2])
                      + (F[1] - F[0]) * (density[2] * F[3] - density[3] * F[2]))
                self.assertGreaterEqual(c1, 0)
                self.assertGreaterEqual(c2, 0)
            before = [before[i] + density[i] for i in range(4)]

        # Reverse hazards cross between labels b and c at t=3/2.
        f_b = Fraction(10, 40) + Fraction(9, 80)
        f_c = Fraction(11, 40) + Fraction(10, 80)
        reverse_b = Fraction(9, 40) / f_b
        reverse_c = Fraction(10, 40) / f_c
        self.assertEqual((reverse_b, reverse_c), (Fraction(18, 29), Fraction(5, 8)))
        self.assertLess(reverse_b, reverse_c)
        # Ordinary hazards also cross, now between a and b at t=5/2.
        f_a = Fraction(8 + 8, 40) + Fraction(8, 80)
        f_b = Fraction(10 + 9, 40) + Fraction(6, 80)
        hazard_a = Fraction(8, 40) / (1 - f_a)
        hazard_b = Fraction(6, 40) / (1 - f_b)
        self.assertEqual((hazard_a, hazard_b), (Fraction(2, 5), Fraction(1, 3)))
        self.assertGreater(hazard_a, hazard_b)

    def test_two_backgrounds_needed_for_counterexample(self):
        rows = TWO_BACKGROUND_NECESSARY
        self.assertEqual(small_background_minima(rows),
                         ((Fraction(203, 4096), Fraction(0), Fraction(0)),
                          (Fraction(121, 8192), Fraction(0), Fraction(0))))
        self.assertEqual(small_background_minima(rows), slow_small_background_minima(rows))
        self.assertEqual(threshold_gaps(rows, 2, 2),
                         (Fraction(1, 64), Fraction(-1, 256)))
        self.assertEqual(threshold_gaps(rows, 2, 2), direct_gaps(rows, [2, 2], 3))
        self.assertEqual(tuple(x.value for x in universal_gap_minima(rows)), slow_minima(rows))

    def test_two_continuous_backgrounds(self):
        from research.rank_selection import pair_probabilities
        from research.test_rank_selection import categorical_oracle

        rows = CONTINUOUS_TWO_BACKGROUND_WITNESS
        q = pair_probabilities(rows, 3)
        self.assertEqual(q, categorical_oracle(rows, 3))
        self.assertEqual(q[0, 2] + q[1, 3] - q[0, 3] - q[1, 2],
                         Fraction(-4531, 1572864))

    def test_admission_and_cap(self):
        invalid_rows = (
            None, [], [[1]] * 3, [[1]] * 5, [[1] * 4097 for _ in range(4)],
            [[0]] * 4, [[True]] * 4, [[1.0]] * 4, [[1_000_001]] * 4,
            [[1], [1], [1], [1, 2]], [[-1]] * 4,
        )
        for rows in invalid_rows:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                universal_gap_minima(rows)
        for lower, upper in ((True, 1), (-1, 1), (0, 4), (2, 1),
                             (Fraction(1, 2**128), 1), (0.5, 1)):
            with self.subTest(lower=lower, upper=upper), self.assertRaises(ValueError):
                threshold_gaps(ORDERED_EXAMPLE, lower, upper)
        rows = [[1] * 4096 for _ in range(4)]
        self.assertEqual(universal_gap_minima(rows),
                         (GapMinimum(Fraction(0), Fraction(0), Fraction(0)),) * 2)


if __name__ == "__main__":
    unittest.main()
