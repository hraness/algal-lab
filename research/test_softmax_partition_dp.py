"""Independent exhaustive checks for the exact partition DP."""

from fractions import Fraction
import unittest

from research.softmax_partition_dp import maximize_partition


def _integer_partitions(total: int, largest: int | None = None):
    """Yield each nonincreasing integer partition exactly once."""
    if largest is None:
        largest = total
    if total == 0:
        yield ()
        return
    for first in range(min(total, largest), 1 - 1, -1):
        for suffix in _integer_partitions(total - first, first):
            yield (first,) + suffix


def _exhaustive(profits: tuple[Fraction, ...], cap: int):
    candidates = (
        (sum((profits[size - 1] for size in partition), Fraction(0)), partition)
        for partition in _integer_partitions(len(profits))
        if len(partition) <= cap
    )
    return max(candidates, key=lambda pair: pair[0])


class SoftmaxPartitionDPTests(unittest.TestCase):
    def assert_matches_exhaustive(self, profits, cap):
        expected_value, _ = _exhaustive(profits, cap)
        value, witness, transitions = maximize_partition(profits, cap)
        self.assertEqual(value, expected_value)
        self.assertEqual(witness, tuple(sorted(witness, reverse=True)))
        self.assertEqual(sum(witness), len(profits))
        self.assertLessEqual(len(witness), cap)
        self.assertEqual(
            sum((profits[size - 1] for size in witness), Fraction(0)), value
        )
        self.assertGreater(transitions, 0)
        if cap >= len(profits):
            self.assertEqual(transitions, len(profits) * (len(profits) + 1) // 2)
            self.assertLessEqual(transitions, len(profits) ** 2)
        else:
            self.assertEqual(transitions, sum(
                (1 if groups == 1 else budget - groups + 1)
                for groups in range(1, min(len(profits), cap) + 1)
                for budget in range(groups, len(profits) + 1)
            ))
            self.assertLessEqual(transitions, cap * len(profits) ** 2)

    def test_exhaustive_small_integer_profiles_and_caps(self):
        for population in range(1, 10):
            # Distinct profiles exercise positive, negative, and mixed values.
            profiles = (
                tuple(Fraction((size * 7 + population * 3) % 13 - 6)
                      for size in range(1, population + 1)),
                tuple(Fraction(-size - population) for size in range(1, population + 1)),
                tuple(Fraction(population - 2 * size) for size in range(1, population + 1)),
            )
            for profits in profiles:
                for cap in range(1, population + 1):
                    with self.subTest(population=population, cap=cap, profits=profits):
                        self.assert_matches_exhaustive(profits, cap)

    def test_rational_profiles(self):
        profiles = (
            (Fraction(1, 2), Fraction(-2, 3), Fraction(5, 7), Fraction(-1, 5)),
            (Fraction(-1, 11), Fraction(3, 8), Fraction(-5, 9), Fraction(7, 13)),
            (Fraction(1, 2), Fraction(1, 4), Fraction(1, 6), Fraction(1, 8)),
        )
        for profits in profiles:
            for cap in range(1, len(profits) + 1):
                with self.subTest(cap=cap, profits=profits):
                    self.assert_matches_exhaustive(profits, cap)

    def test_all_partitions_tied(self):
        for population in range(1, 10):
            # Profit m is m, so every full-budget partition has value N.
            profits = tuple(Fraction(size) for size in range(1, population + 1))
            for cap in range(1, population + 1):
                with self.subTest(population=population, cap=cap):
                    self.assert_matches_exhaustive(profits, cap)

    def test_negative_profits_still_consume_full_budget(self):
        profits = (Fraction(-4), Fraction(-9), Fraction(-3), Fraction(-20))
        for cap in range(1, 5):
            with self.subTest(cap=cap):
                value, witness, _ = maximize_partition(profits, cap)
                self.assertEqual(sum(witness), len(profits))
                self.assertEqual(value, _exhaustive(profits, cap)[0])

    def test_deterministic_witness(self):
        profits = (Fraction(1),) * 8
        self.assertEqual(maximize_partition(profits, 3), maximize_partition(profits, 3))

    def test_admission_rejects_wrong_shapes_and_inexact_values(self):
        invalid = (
            ((1.0,), 1, TypeError),
            ((True,), 1, TypeError),
            (("1/2",), 1, TypeError),
            ((1,), True, TypeError),
            ((1,), 1.0, TypeError),
            ([Fraction(1, 2)], 1, TypeError),
            ((), 1, ValueError),
            ((1,) * 129, 1, ValueError),
            ((1,), 0, ValueError),
            ((1,), 129, ValueError),
            ((Fraction(1, 1 << 4096),), 1, ValueError),
            ((Fraction(1 << 4096),), 1, ValueError),
        )
        for profits, cap, error in invalid:
            with self.subTest(profits=profits, cap=cap, error=error):
                with self.assertRaises(error):
                    maximize_partition(profits, cap)

    def test_limits_and_transition_cap_at_population_128(self):
        profits = tuple(Fraction((size % 7) - 3, size + 1) for size in range(1, 129))
        for cap in (1, 17, 127, 128):
            value, witness, transitions = maximize_partition(profits, cap)
            self.assertIsInstance(value, Fraction)
            self.assertEqual(sum(witness), 128)
            self.assertLessEqual(len(witness), cap)
            self.assertLessEqual(transitions, min(cap, 128) * 128 * 128)


if __name__ == "__main__":
    unittest.main()
