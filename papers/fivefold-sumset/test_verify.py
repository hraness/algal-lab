"""Literal finite-set controls for the two simplex counting formulas."""
from itertools import product
import unittest

from verify import double_sum, single_sum, verify_certificate


def literal_counts(m, a, b):
    first = {word for word in product(range(a + 1), repeat=m) if sum(word) <= a}
    second = {word for word in product(range(b + 1), repeat=m) if sum(word) <= b}
    sums = {tuple(x + y for x, y in zip(u, v)) for u in first for v in second}
    differences = {tuple(x - y for x, y in zip(u, v)) for u in first for v in second}
    fivefold = {tuple(sum(coordinates) for coordinates in zip(*words))
                for words in product(second, repeat=5)}
    return len(differences), len(sums), len(fivefold)


class CertificateTests(unittest.TestCase):
    def test_literal_sets(self):
        for case in ((1, 0, 0), (1, 2, 1), (2, 2, 1), (3, 2, 1)):
            with self.subTest(case=case):
                expected = literal_counts(*case)
                self.assertEqual(single_sum(*case), expected)
                self.assertEqual(double_sum(*case), expected)

    def test_input_limits(self):
        for case in ((0, 1, 1), (129, 1, 1), (1, -1, 1), (1, 161, 1),
                     (1, 1, 33), (True, 1, 1), (1, 1.0, 1)):
            for method in (single_sum, double_sum):
                with self.subTest(case=case, method=method.__name__):
                    with self.assertRaises(ValueError):
                        method(*case)

    def test_fixed_certificate(self):
        difference, sums, fivefold = verify_certificate()
        self.assertGreater(difference ** 5, sums ** 5 * fivefold)


if __name__ == '__main__':
    unittest.main()
