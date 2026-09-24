"""Independent numerical and contract checks for the certified partition solver.

Decimal.exp at high precision and direct enumeration provide the numerical
oracle; none of the solver's interval or DP helpers are used for that oracle.
"""

from decimal import Decimal, localcontext
from fractions import Fraction as Q
import subprocess
import sys
import unittest
from unittest.mock import patch

import research.softmax_partition as solver


def _decimal_fraction(value: Q, precision: int = 110) -> Decimal:
    with localcontext() as context:
        context.prec = precision
        return Decimal(value.numerator) / Decimal(value.denominator)


def _partitions(total: int, largest: int | None = None):
    """Enumerate nonincreasing integer partitions independently of the DP."""
    if largest is None:
        largest = total
    if total == 0:
        yield ()
        return
    for first in range(min(total, largest), 0, -1):
        for rest in _partitions(total - first, first):
            yield (first,) + rest


def _decimal_rewards(agents: int, tasks: int, inner: Q, outer: Q):
    with localcontext() as context:
        context.prec = 90
        t = _decimal_fraction(inner, 100)
        tau = _decimal_fraction(outer, 100)
        exp_inner = t.exp()
        scores = [
            Decimal(size) * exp_inner
            / (Decimal(size) * exp_inner + Decimal(agents - size))
            for size in range(1, agents + 1)
        ]
        weights = [(tau * score).exp() for score in scores]
        admissible = [
            group
            for group in _partitions(agents)
            if len(group) <= min(agents, tasks)
        ]
        rewards = []
        for group in admissible:
            numerator = sum(
                (scores[size - 1] * weights[size - 1] for size in group),
                Decimal(0),
            )
            denominator = Decimal(tasks) + sum(
                (weights[size - 1] - 1 for size in group), Decimal(0)
            )
            rewards.append((numerator / denominator, group))
        return rewards


def _unscaled_exp_taylor_enclosure(x: Q, degree: int = 384) -> tuple[Q, Q]:
    """Independent exact enclosure from an unscaled Taylor series."""
    if x < 0:
        raise ValueError("the reference is for nonnegative inputs")
    total = Q(1)
    term = Q(1)
    for k in range(1, degree + 1):
        term *= x / k
        total += term
    next_term = term * x / (degree + 1)
    ratio_bound = x / (degree + 2)
    if ratio_bound >= 1:
        raise ValueError("geometric tail ratio must be below one")
    tail = next_term / (1 - ratio_bound)
    return total, total + tail


class SoftmaxPartitionTests(unittest.TestCase):
    def test_exponential_intervals_contain_independent_decimal_exp(self):
        points = (Q(0), Q(1, 1000), Q(1, 3), Q(1), Q(7, 2), Q(32))
        for point in points:
            for bits in (32, 64, 128):
                with self.subTest(point=point, bits=bits):
                    lo, hi = solver._exp_interval(point, bits)
                    with localcontext() as context:
                        context.prec = 100
                        expected = _decimal_fraction(point, 105).exp()
                        self.assertLessEqual(_decimal_fraction(lo), expected)
                        self.assertGreaterEqual(_decimal_fraction(hi), expected)
                        self.assertLessEqual(hi - lo, Q(8, 1 << (bits - 2)) * max(Q(1), hi))

    def test_solver_exp_intervals_contain_exact_unscaled_taylor_enclosures(self):
        # The reference has no scaling/squaring and shares no solver code.
        for point in (Q(0), Q(1, 3), Q(1), Q(7, 2), Q(16), Q(32)):
            reference_lo, reference_hi = _unscaled_exp_taylor_enclosure(point)
            for bits in (32, 64, 128):
                with self.subTest(point=point, bits=bits):
                    solver_lo, solver_hi = solver._exp_interval(point, bits)
                    self.assertLessEqual(solver_lo, reference_lo)
                    self.assertGreaterEqual(solver_hi, reference_hi)

    def test_temperature_32_epsilon_boundary_refines_and_contains_decimal_optimum(self):
        agents, tasks = 2, 2
        inner = outer = Q(32)
        epsilon = Q(1, 1 << 40)
        result = solver.optimize_partition(agents, tasks, inner, outer, epsilon)
        self.assertGreater(result["precisionBits"], 32)
        rewards = _decimal_rewards(agents, tasks, inner, outer)
        optimum = max(reward for reward, _ in rewards)
        groups = tuple(result["groups"])
        witness = next(reward for reward, group in rewards if group == groups)
        optimum_lo, optimum_hi = map(Q, result["optimumInterval"])
        witness_lo, witness_hi = map(Q, result["witnessRewardInterval"])
        self.assertLessEqual(_decimal_fraction(optimum_lo), optimum)
        self.assertGreaterEqual(_decimal_fraction(optimum_hi), optimum)
        self.assertLessEqual(_decimal_fraction(witness_lo), witness)
        self.assertGreaterEqual(_decimal_fraction(witness_hi), witness)
        self.assertLessEqual(optimum - witness, _decimal_fraction(epsilon) + Decimal("1e-80"))

    def test_nested_item_intervals_contain_independent_decimal_coefficients(self):
        fixtures = ((2, Q(1, 3), Q(2, 5)), (4, Q(3, 2), Q(1, 7)),
                    (7, Q(5, 2), Q(3, 4)))
        for agents, inner, outer in fixtures:
            intervals = solver._item_intervals(agents, inner, outer, 64)
            with localcontext() as context:
                context.prec = 90
                t = _decimal_fraction(inner, 100)
                tau = _decimal_fraction(outer, 100)
                e = t.exp()
                for size, (a_lo, a_hi, b_lo, b_hi) in enumerate(intervals, 1):
                    score = Decimal(size) * e / (
                        Decimal(size) * e + Decimal(agents - size)
                    )
                    weight = (tau * score).exp()
                    a, b = score * weight, weight - 1
                    self.assertLessEqual(_decimal_fraction(a_lo), a)
                    self.assertGreaterEqual(_decimal_fraction(a_hi), a)
                    self.assertLessEqual(_decimal_fraction(b_lo), b)
                    self.assertGreaterEqual(_decimal_fraction(b_hi), b)

    def test_exhaustive_decimal_optima_and_witness_enclosures(self):
        cases = (
            (1, 1, Q(1, 3), Q(2, 5)),
            (1, 4, Q(2), Q(1, 2)),
            (2, 1, Q(3, 2), Q(1, 3)),
            (2, 3, Q(1), Q(2, 3)),
            (3, 2, Q(1, 2), Q(1, 4)),
            (3, 4, Q(2), Q(3, 5)),
            (4, 2, Q(5, 2), Q(1, 2)),
            (4, 5, Q(3, 2), Q(3, 4)),
            (5, 3, Q(2, 3), Q(1, 5)),
            (5, 5, Q(2), Q(1, 2)),
            (6, 4, Q(3, 2), Q(1, 3)),
        )
        epsilon = Q(1, 100)
        for agents, tasks, inner, outer in cases:
            with self.subTest(agents=agents, tasks=tasks, inner=inner, outer=outer):
                result = solver.optimize_partition(agents, tasks, inner, outer, epsilon)
                groups = tuple(result["groups"])
                self.assertEqual(sum(groups), agents)
                self.assertEqual(groups, tuple(sorted(groups, reverse=True)))
                self.assertLessEqual(len(groups), min(agents, tasks))

                rewards = _decimal_rewards(agents, tasks, inner, outer)
                optimum = max(reward for reward, _ in rewards)
                witness_reward = next(reward for reward, group in rewards if group == groups)
                optimum_lo, optimum_hi = map(Q, result["optimumInterval"])
                witness_lo, witness_hi = map(Q, result["witnessRewardInterval"])
                self.assertLessEqual(_decimal_fraction(optimum_lo), optimum)
                self.assertGreaterEqual(_decimal_fraction(optimum_hi), optimum)
                self.assertLessEqual(_decimal_fraction(witness_lo), witness_reward)
                self.assertGreaterEqual(_decimal_fraction(witness_hi), witness_reward)
                self.assertLessEqual(_decimal_fraction(optimum_hi - optimum_lo),
                                     _decimal_fraction(epsilon))
                self.assertLessEqual(_decimal_fraction(Q(result["additiveRegretBound"])),
                                     _decimal_fraction(epsilon))
                self.assertLessEqual(optimum - witness_reward,
                                     _decimal_fraction(epsilon) + Decimal("1e-80"))
                self.assertLessEqual(result["dpTransitions"],
                                     result["admittedTransitionBound"])

    def test_continuous_and_pure_only_scope_labels(self):
        continuous_cases = ((3, 2, Q(2), Q(1)), (3, 2, Q(4), Q(1)))
        pure_only_cases = ((3, 2, Q(4), Q(3, 4)), (4, 5, Q(5), Q(1)))
        for agents, tasks, inner, outer in continuous_cases:
            with self.subTest(inner=inner, outer=outer):
                result = solver.optimize_partition(agents, tasks, inner, outer, Q(1, 20))
                self.assertEqual(result["optimumScope"], "continuous")
        for agents, tasks, inner, outer in pure_only_cases:
            with self.subTest(inner=inner, outer=outer):
                result = solver.optimize_partition(agents, tasks, inner, outer, Q(1, 20))
                self.assertEqual(result["optimumScope"], "pure-only")
                self.assertEqual(sum(result["groups"]), agents)

    def test_exact_threshold_tie_takes_small_residual_branch_synthetic(self):
        # Labeled synthetic rational coefficients, deliberately patched rather
        # than presented as Boltzmann-derived values.  At rho=3/4, the split
        # (1,1) has residual zero while concentration gave the initial reward
        # lower bound 1/2, so the solver must handle the exact tie branch.
        synthetic_items = (
            (Q(3, 4), Q(3, 4), Q(0), Q(0)),
            (Q(1), Q(1), Q(0), Q(0)),
        )
        with patch.object(solver, "_item_intervals", return_value=synthetic_items):
            result = solver.optimize_partition(2, 2, Q(1), Q(1), Q(1, 10))
        self.assertEqual(result["groups"], [1, 1])
        self.assertEqual(result["stopReason"], "small-residual")
        self.assertEqual(Q(result["optimumInterval"][0]), Q(3, 4))
        self.assertEqual(Q(result["optimumInterval"][1]), Q(3, 4))

    def test_nonzero_straddling_residual_encloses_synthetic_rational_optimum(self):
        # Synthetic interval coefficients bracket exact rational coefficients
        # a_1=3/4, a_2=1, b_1=b_2=0. Their exact pure optimum is 3/4.
        # At the first threshold rho=3/4 the residual enclosure is
        # [-1/50,+1/50], so this exercises a genuinely nonzero ambiguity.
        synthetic_items = (
            (Q(37, 50), Q(38, 50), Q(0), Q(0)),
            (Q(1), Q(1), Q(0), Q(0)),
        )
        with patch.object(solver, "_item_intervals", return_value=synthetic_items):
            result = solver.optimize_partition(2, 2, Q(1), Q(1), Q(2, 5))
        true_optimum = Q(3, 4)
        lower, upper = map(Q, result["optimumInterval"])
        witness_lower, witness_upper = map(Q, result["witnessRewardInterval"])
        self.assertEqual(result["stopReason"], "small-residual")
        self.assertEqual(result["groups"], [1, 1])
        self.assertLess(lower, true_optimum)
        self.assertGreater(upper, true_optimum)
        self.assertLessEqual(lower, true_optimum)
        self.assertGreaterEqual(upper, true_optimum)
        self.assertLessEqual(witness_lower, true_optimum)
        self.assertGreaterEqual(witness_upper, true_optimum)
        self.assertEqual(upper - lower, Q(1, 50))

    def test_zero_negative_float_and_boolean_inputs_reject_before_evaluation(self):
        invalid = (
            (2, 2, Q(0), Q(1), Q(1, 10)),
            (2, 2, Q(-1), Q(1), Q(1, 10)),
            (2, 2, Q(1), Q(0), Q(1, 10)),
            (2, 2, Q(1), Q(-1), Q(1, 10)),
            (2, 2, 1.0, Q(1), Q(1, 10)),
            (2, 2, Q(1), 1.0, Q(1, 10)),
            (2, 2, Q(1), Q(1), 0.1),
            (True, 2, Q(1), Q(1), Q(1, 10)),
            (2, False, Q(1), Q(1), Q(1, 10)),
            (2, 2, True, Q(1), Q(1, 10)),
            (2, 2, Q(1), False, Q(1, 10)),
            (2, 2, Q(1), Q(1), True),
        )
        with patch.object(solver, "_item_intervals", side_effect=AssertionError("evaluated")):
            for args in invalid:
                with self.subTest(args=args), self.assertRaises(ValueError):
                    solver.optimize_partition(*args)

    def test_input_and_work_caps_fail_before_interval_evaluation(self):
        invalid = (
            (0, 1, Q(1), Q(1), Q(1, 10)),
            (True, 1, Q(1), Q(1), Q(1, 10)),
            (129, 1, Q(1), Q(1), Q(1, 10)),
            (1, 129, Q(1), Q(1), Q(1, 10)),
            (1, 1, Q(33), Q(1), Q(1, 10)),
            (1, 1, Q(1, 1 << 64), Q(1), Q(1, 10)),
            (1, 1, Q(1), Q(1), Q(1, 1 << 41)),
        )
        with patch.object(solver, "_item_intervals", side_effect=AssertionError("evaluated")):
            for args in invalid:
                with self.subTest(args=args), self.assertRaises(ValueError):
                    solver.optimize_partition(*args)
            with self.subTest(work_cap=True), self.assertRaises(ValueError):
                solver.optimize_partition(128, 64, Q(1), Q(1), Q(1, 1 << 40))

    def test_cli_rejects_exponent_nan_infinity_and_long_components(self):
        malformed = (
            "1e1000000000", "NaN", "Infinity", "-Infinity", "1/0",
            "123456789012345678901", "0.123456789012345678901",
        )
        for raw in malformed:
            command = [
                sys.executable, "-m", "research.softmax_partition",
                "--agents", "1", "--tasks", "1", "--inner", raw,
                "--outer", "1",
            ]
            with self.subTest(raw=raw):
                process = subprocess.run(command, capture_output=True, text=True, timeout=3)
                self.assertNotEqual(process.returncode, 0)
                self.assertTrue(
                    "bounded integer, fraction, or decimal" in process.stderr
                    or "requires a rational" in process.stderr
                    or "expected one argument" in process.stderr,
                    process.stderr,
                )


if __name__ == "__main__":
    unittest.main()
