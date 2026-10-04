from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from research.foundation_allocation import benchmark, generate, run, verify


class FoundationAllocationTests(unittest.TestCase):
    def test_stable_inputs_and_exact_controls(self):
        dataset = generate()
        self.assertEqual(dataset, generate())
        self.assertEqual(len(dataset["cases"]), 24)
        report = benchmark(dataset)
        self.assertEqual(len(report["results"]), 24)
        self.assertTrue(all(row["certificateValid"] for row in report["results"]))
        self.assertTrue(all(row["oracleEqual"] for row in report["results"]))
        self.assertTrue(all(row["mutatedCertificateRejected"] for row in report["results"]))
        self.assertEqual(report["modelCalls"], 0)
        self.assertEqual(report["scope"], "synthetic-development-controls")

    def test_inputs_are_frozen_and_output_never_overwritten(self):
        wrong = deepcopy(generate())
        wrong["cases"][0]["n"] = 1000
        with self.assertRaises(ValueError):
            benchmark(wrong)
        with TemporaryDirectory() as root:
            out = Path(root) / "run"
            run(out)
            self.assertTrue(verify(out)["verified"])
            with self.assertRaises(FileExistsError):
                run(out)
            report = out / "report.json"
            report.write_bytes(report.read_bytes().replace(b'"oracleEqual": true', b'"oracleEqual": false', 1))
            with self.assertRaisesRegex(ValueError, "reproduction"):
                verify(out)


if __name__ == "__main__":
    unittest.main()
