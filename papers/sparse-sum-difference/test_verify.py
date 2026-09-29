"""Small exact controls independent of the public verifier's integer maxima."""

from fractions import Fraction
from itertools import combinations
import unittest

import verify


class CertificateTests(unittest.TestCase):
    def test_all_small_alphabets_against_rational_grouping(self):
        cases = 0
        for b in range(1, 7):
            for size in range(b):
                for interior in combinations(range(1, b), size):
                    alphabet = (0, *interior, b)
                    for p, h in ((1, 2), (2, 3), (3, 4)):
                        q = Fraction(p, h)
                        sums, differences, denominator = verify.totals(alphabet, p, h)
                        expected_sums = {
                            s: max(q**(a+c) for a in alphabet for c in alphabet if a+c == s)
                            for s in {a+c for a in alphabet for c in alphabet}
                        }
                        expected_differences = {
                            d: max(q**(a+c) for a in alphabet for c in alphabet if a-c == d)
                            for d in {a-c for a in alphabet for c in alphabet}
                        }
                        self.assertEqual(expected_sums, {s: Fraction(v, denominator) for s, v in sums.items()})
                        self.assertEqual(expected_differences, {d: Fraction(v, denominator) for d, v in differences.items()})
                        cases += 1
        self.assertEqual(cases, 189)

    def test_stated_certificates_and_false_stronger_claim(self):
        for case in verify.CASES:
            self.assertTrue(verify.verify_case(*case)["verified"])
        with self.assertRaisesRegex(ValueError, "does not certify"):
            verify.verify_case("false", (0, *range(2, 12)), 3, 4, 1181, 1000)
        with self.assertRaisesRegex(ValueError, "does not certify"):
            verify.verify_case("false-extreme", (0, 1), 1, 2, 2, 1)
        with self.assertRaisesRegex(ValueError, "does not certify"):
            verify.verify_case("false-sparse", (0, 3, 4, *range(6, 17)), 16, 19, 741, 625)

    def test_reduced_fraction_and_invalid_inputs(self):
        self.assertEqual(verify.totals((0, 2, 3), 3, 4), verify.totals((0, 2, 3), 6, 8))
        for alphabet, p, h in (
            ((0,), 1, 2), ((0, 2, 2), 1, 2), ((0, 2, 1), 1, 2),
            ((0, 65), 1, 2), ((0, True), 1, 2), ((1, 2), 1, 2),
            ((0, 1), 0, 2), ((0, 1), 2, 2), ((0, 1), 1, 1000001),
            ((0, 1), True, 2), ((0, 1), 1.0, 2),
        ):
            with self.subTest(alphabet=alphabet, p=p, h=h):
                with self.assertRaises(ValueError):
                    verify.totals(alphabet, p, h)
        with self.assertRaises(ValueError):
            verify.verify_case("bad-bound", (0, 1), 1, 2, 1, 1)


if __name__ == "__main__":
    unittest.main()
