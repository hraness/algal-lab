"""Finite endpoint-pair controls and fail-closed certificate checks."""

import copy
from itertools import product
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import carry_verify as verifier


CERTIFICATE = Path(__file__).with_name("carry-certificate.json")


class CarryCertificateTests(unittest.TestCase):
    def test_cost_recurrence_against_all_endpoint_pairs(self):
        configurations = 0
        for alphabet in ((0, 1), (0, 2), (0, 1, 2), (0, 1, 3)):
            for base in (alphabet[-1] + 1, 2 * alphabet[-1] + 1):
                for depth in (1, 2, 3):
                    endpoints = {
                        sum(digit * base**j for j, digit in enumerate(digits)): sum(digits)
                        for digits in product(alphabet, repeat=depth)
                    }
                    expected_sums, expected_differences = {}, {}
                    for x, cx in endpoints.items():
                        for y, cy in endpoints.items():
                            cost = cx + cy
                            expected_sums[x + y] = min(expected_sums.get(x + y, 255), cost)
                            expected_differences[x - y] = min(expected_differences.get(x - y, 255), cost)
                    sums, differences, radius = verifier.cost_tables(alphabet, base, depth)
                    self.assertEqual(radius, max(endpoints))
                    self.assertEqual(expected_sums, {i: c for i, c in enumerate(sums) if c != 255})
                    self.assertEqual(expected_differences, {
                        i - radius: c for i, c in enumerate(differences) if c != 255
                    })
                    configurations += 1
        self.assertEqual(configurations, 24)

    def test_strict_comparison_and_integer_limits(self):
        self.assertTrue(verifier.strict_ratio_exceeds(3, 1, 32, 1, 5))
        self.assertFalse(verifier.strict_ratio_exceeds(2, 1, 32, 1, 5))
        self.assertFalse(verifier.strict_ratio_exceeds(1, 1, 32, 1, 5))
        self.assertFalse(verifier.strict_ratio_exceeds(3, 2, 32, 1, 5))
        for arguments in ((True, 1, 32, 1, 5), (3, 0, 32, 1, 5),
                          (3, 1, 1, 1, 5), (3, 1, 32, 0, 5),
                          (3, 1, 32, 1, 20001), (2**1024, 1, 32, 1, 5)):
            with self.assertRaises(ValueError):
                verifier.strict_ratio_exceeds(*arguments)

    def test_json_and_certificate_limits(self):
        original = verifier.read_certificate(CERTIFICATE)
        for key, value in (("block_depth", True), ("radius", 541201),
                           ("sum_histogram", [0] * 128),
                           ("sum_histogram", [True] + [0] * 128),
                           ("difference_histogram", [1082402] + [0] * 128),
                           ("sum_numerator", "1e100"),
                           ("difference_numerator", "9" * 257),
                           ("common_denominator", "0"), ("q", [True, 19])):
            changed = copy.deepcopy(original)
            changed[key] = value
            with self.subTest(key=key, value=value):
                with self.assertRaises(ValueError):
                    verifier.validate_certificate(changed)
        extra = dict(original, extra="unrecognized")
        with self.assertRaises(ValueError):
            verifier.validate_certificate(extra)
        missing = dict(original)
        del missing["strict_bound"]
        with self.assertRaises(ValueError):
            verifier.validate_certificate(missing)
        malformed = (b'{"schema_version":1,"schema_version":1}', b'{"q":NaN}',
                     b"\xff", b" " * (verifier.MAX_BYTES + 1))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            for raw in malformed:
                path.write_bytes(raw)
                with self.assertRaises(ValueError):
                    verifier.read_certificate(path)
        for alphabet, base, depth in (((0, True), 2, 1), ((0, 2), 2, 1),
                                      ((0, 1), 33, 4), ((0, 1), 2, 5)):
            with self.assertRaises(ValueError):
                verifier.cost_tables(alphabet, base, depth)

    def test_one_corrupted_full_histogram_is_rejected_before_exponentiation(self):
        changed = verifier.read_certificate(CERTIFICATE)
        changed["sum_histogram"][0] += 1
        with mock.patch.object(verifier, "strict_ratio_exceeds",
                               side_effect=AssertionError("unverified histogram reached exponentiation")):
            with self.assertRaisesRegex(ValueError, "sum histogram differs"):
                verifier.verify_certificate(changed)


if __name__ == "__main__":
    unittest.main()
