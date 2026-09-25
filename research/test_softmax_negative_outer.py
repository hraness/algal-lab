"""Finite checks for ``docs/softmax-negative-outer.md``."""

import unittest
from decimal import Decimal, localcontext
from fractions import Fraction

from research.softmax_negative_outer import (
    balanced_pure,
    binary_allocations,
    bottleneck,
    column_score,
    crumb_threshold_ok,
    fractional_threshold,
    grid_allocations,
    is_balanced_pure,
    mean_score,
    occupancy_score,
    outer_reward,
    spread_witness,
    to_decimal,
)

E4 = Fraction(4)
ROOT2 = Fraction(2)  # exp(t/2) when exp(t) = 4
PRECISION = 40
TOLERANCE = Decimal("1e-30")  # operands are O(1) at precision 40, so rounding error is ~1e-39


def _ln(value: int) -> Decimal:
    with localcontext() as context:
        context.prec = PRECISION
        return Decimal(value).ln()


class ColumnScoreTests(unittest.TestCase):
    def test_rejects_bad_entries_and_roots(self):
        with self.assertRaises(ValueError):
            column_score((Fraction(1, 3),), ROOT2, 2)
        with self.assertRaises(ValueError):
            column_score((), ROOT2, 2)
        with self.assertRaises(TypeError):
            column_score((Fraction(1, 2),), 1.1, 2)
        with self.assertRaises(ValueError):
            spread_witness(4, 2)

    def test_occupancy_scores_match_binary_columns(self):
        for n in range(1, 6):
            for k in range(n + 1):
                column = (Fraction(1),) * k + (Fraction(0),) * (n - k)
                self.assertEqual(column_score(column, ROOT2, 2), occupancy_score(k, n, E4))

    def test_crumb_criterion_matches_direct_comparison(self):
        # h(1/2) > 0 iff f_t(1^q, 1/2, 0...) > s_q, with exp(-t/2) = 1/2 when E = 4.
        for n, m in ((3, 2), (5, 3), (7, 4), (2, 3)):
            q = n // m
            column = (Fraction(1),) * q + (Fraction(1, 2),) + (Fraction(0),) * (n - q - 1)
            h = Fraction(1, 2) * (q * E4 + n - q) - q * E4 * (1 - Fraction(1, 2))
            self.assertEqual(column_score(column, ROOT2, 2) > occupancy_score(q, n, E4), h > 0)


class OuterSoftmaxBoundTests(unittest.TestCase):
    def test_mean_and_bottleneck_bounds_on_grid(self):
        n, m = 3, 2
        with localcontext() as context:
            context.prec = PRECISION
            e = Decimal(1).exp()
            for tau in (Decimal(-1), Decimal(-8)):
                for matrix in grid_allocations(n, m, 2):
                    scores = [column_score(tuple(row[j] for row in matrix), ROOT2, 2) for j in range(m)]
                    reward = outer_reward(scores, tau, PRECISION)
                    mean = to_decimal(sum(scores, Fraction(0)) / m)
                    low = to_decimal(min(scores))
                    self.assertLessEqual(reward, mean + TOLERANCE)
                    self.assertGreaterEqual(reward, low - TOLERANCE)
                    self.assertLessEqual(reward - low, Decimal(m - 1) / (e * abs(tau)) + TOLERANCE)
                    if len(set(scores)) > 1:
                        # Strict part of (3): unequal scores and tau < 0 give a strict gap.
                        self.assertLess(reward, mean - Decimal("1e-6"))


class DivisibleTests(unittest.TestCase):
    CASES = ((4, 2), (6, 2), (3, 3), (4, 4))

    def test_mean_score_maximized_only_by_balanced_pure(self):
        for n, m in self.CASES:
            target = occupancy_score(n // m, n, E4)
            winners = 0
            for matrix in grid_allocations(n, m, 2):
                value = mean_score(matrix, ROOT2, 2)
                self.assertLessEqual(value, target)
                if value == target:
                    winners += 1
                    self.assertTrue(is_balanced_pure(matrix, n, m))
                else:
                    self.assertFalse(is_balanced_pure(matrix, n, m))
            self.assertGreater(winners, 0)

    def test_negative_tau_maximized_only_by_balanced_pure(self):
        for n, m in ((4, 2), (3, 3)):
            with localcontext() as context:
                context.prec = PRECISION
                target = to_decimal(occupancy_score(n // m, n, E4))
                for tau in (Decimal(-1), Decimal(-8), Decimal(-64)):
                    for matrix in grid_allocations(n, m, 2):
                        scores = [column_score(tuple(row[j] for row in matrix), ROOT2, 2) for j in range(m)]
                        reward = outer_reward(scores, tau, PRECISION)
                        if is_balanced_pure(matrix, n, m):
                            # Equal scores make R_tau the common score; only rounding remains.
                            self.assertLess(abs(reward - target), TOLERANCE)
                        else:
                            # The smallest grid gap is above 0.03, far beyond rounding.
                            self.assertLess(reward, target - Decimal("1e-12"))


class IndivisibleTests(unittest.TestCase):
    def test_pure_bottleneck_ceiling(self):
        for n, m in ((3, 2), (5, 3), (2, 3), (4, 3)):
            ceiling = occupancy_score(n // m, n, E4)
            attained = False
            for matrix in binary_allocations(n, m):
                value = bottleneck(matrix, ROOT2, 2)
                self.assertLessEqual(value, ceiling)
                attained |= value == ceiling
            self.assertTrue(attained)
            self.assertEqual(bottleneck(balanced_pure(n, m), ROOT2, 2), ceiling)

    def test_spread_witness_beats_pure_bottleneck(self):
        expected = {(3, 2): Fraction(5, 7), (5, 3): Fraction(5, 9), (2, 3): Fraction(1, 3)}
        heavy = spread_witness(5, 3)
        heavy_scores = sorted(column_score(tuple(row[j] for row in heavy), ROOT2, 2) for j in range(3))
        self.assertEqual(heavy_scores, [Fraction(5, 9), Fraction(5, 9), Fraction(8, 11)])
        self.assertEqual(Fraction(5, 9) - occupancy_score(1, 5, E4), Fraction(1, 18))
        for (n, m), value in expected.items():
            self.assertTrue(crumb_threshold_ok(n, m, E4, _ln(4)))
            witness = spread_witness(n, m)
            for row in witness:
                self.assertEqual(sum(row), 1)
            self.assertTrue(any(0 < entry < 1 for row in witness for entry in row))
            self.assertEqual(bottleneck(witness, ROOT2, 2), value)
            self.assertGreater(value, occupancy_score(n // m, n, E4))

    def test_finite_tau_transition_for_three_agents_two_tasks(self):
        n, m = 3, 2
        witness = spread_witness(n, m)
        delta = bottleneck(witness, ROOT2, 2) - occupancy_score(1, n, E4)
        self.assertEqual(delta, Fraction(1, 21))
        threshold = fractional_threshold(delta, m, PRECISION)
        self.assertLess(threshold, Decimal(-15))
        self.assertGreater(threshold, Decimal(-16))
        witness_scores = [column_score(tuple(row[j] for row in witness), ROOT2, 2) for j in range(m)]
        cold = Decimal(-16)
        witness_cold = outer_reward(witness_scores, cold, PRECISION)
        with localcontext() as context:
            context.prec = PRECISION
            self.assertLess(abs(witness_cold - to_decimal(Fraction(5, 7))), TOLERANCE)
        best_pure_zero = Fraction(0)
        for matrix in binary_allocations(n, m):
            scores = [column_score(tuple(row[j] for row in matrix), ROOT2, 2) for j in range(m)]
            self.assertLess(outer_reward(scores, cold, PRECISION), witness_cold)
            best_pure_zero = max(best_pure_zero, sum(scores, Fraction(0)) / m)
        # At zero outer temperature the pure balanced allocation wins instead.
        self.assertEqual(best_pure_zero, Fraction(7, 9))
        self.assertGreater(best_pure_zero, mean_score(witness, ROOT2, 2))

    def test_large_inner_temperature_boundary(self):
        # E = 64: t s_1 > 1, so the hypothesis fails and the spread column loses.
        root8, e64 = Fraction(8), Fraction(64)
        self.assertFalse(crumb_threshold_ok(3, 2, e64, _ln(64)))
        column = (Fraction(1), Fraction(0), Fraction(1, 2))
        self.assertEqual(column_score(column, root8, 2), Fraction(68, 73))
        self.assertLess(Fraction(68, 73), occupancy_score(1, 3, e64))
        self.assertEqual(occupancy_score(1, 3, e64), Fraction(32, 33))


if __name__ == "__main__":
    unittest.main()
