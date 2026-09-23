"""Admission and independent exact ranking checks for two-base grouping."""
from contextlib import redirect_stdout
from fractions import Fraction
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from research.mixture_stochastic_groups import main, optimal_mixture_histogram_groups
from research.stochastic_groups import (
    MAX_BINS, MAX_CLOCKS, MAX_COUNT, MAX_INPUT_BYTES, optimal_histogram_groups,
)
from research.test_intact_groups import partitions
from research.test_robust_stochastic_groups import _selection_laws, _tails


FOUR_CLOCKS = [[6 - i, 3 + 2 * i, 6 - i] for i in range(4)]
SIX_CLOCKS = [[10 - i, 5 + 2 * i, 10 - i] for i in range(6)]


def _reconstruct(result):
    bases = [[Fraction(value) for value in row] for row in result["baseMasses"]]
    return [[(1 - Fraction(weight)) * a + Fraction(weight) * b
             for a, b in zip(*bases)] for weight in result["mixingWeights"]]


class MixtureStochasticGroupsTests(unittest.TestCase):
    def test_crossing_bases_and_exact_mixture_certificate(self):
        result = optimal_mixture_histogram_groups(SIX_CLOCKS, 3)
        self.assertEqual(result["baseLabels"], [5, 0])
        self.assertEqual(result["baseMasses"], [["1/5", "3/5", "1/5"],
                                                ["2/5", "1/5", "2/5"]])
        self.assertEqual(result["mixingWeights"], ["1", "4/5", "3/5", "2/5", "1/5", "0"])
        self.assertEqual(result["labels"], [5, 4, 3, 2, 1, 0])
        self.assertEqual(result["groups"], [[5, 4, 3], [2, 1, 0]])
        self.assertEqual(result["certificate"]["differingBin"], 0)
        self.assertEqual(result["certificate"]["affineDimension"], 1)
        for normalized, original in zip(_reconstruct(result), SIX_CLOCKS):
            self.assertEqual(normalized, [Fraction(value, sum(original)) for value in original])
        # Every distinct pair of input CDFs crosses between the two interior
        # endpoints, so the ordinary CDF block optimizer cannot certify this.
        for i in range(6):
            for j in range(i + 1, 6):
                self.assertGreater(SIX_CLOCKS[i][0], SIX_CLOCKS[j][0])
                self.assertLess(sum(SIX_CLOCKS[i][:2]), sum(SIX_CLOCKS[j][:2]))
        with self.assertRaisesRegex(ValueError, "cannot certify CDF block cut"):
            optimal_histogram_groups(SIX_CLOCKS, 3)

    def test_all_small_partitions_at_all_horizons(self):
        cases = 0
        # This categorical oracle conditions on the sampled bins and averages
        # uniformly over cutoff-bin subsets. It knows no mixture identities,
        # CDF comparisons, or grouping proof. Reuse each selected-set law.
        for rows, sizes in ((FOUR_CLOCKS, (2,)), (SIX_CLOCKS, (2, 3)),
                            ([[i, 8 - i] for i in range(8)], (4,))):
            laws = _selection_laws(rows)
            for size in sizes:
                result = optimal_mixture_histogram_groups(rows, size)
                candidates = list(partitions(list(range(len(rows))), size))
                for survivors, law in laws.items():
                    target = _tails(law, result["groups"])
                    for groups in candidates:
                        with self.subTest(n=len(rows), size=size, k=survivors, groups=groups):
                            actual = _tails(law, groups)
                            self.assertTrue(all(a <= b for a, b in zip(actual, target)))
                            self.assertLessEqual(sum(actual), sum(target))
                        cases += 1
        self.assertEqual(cases, 505)

    def test_independent_and_jointly_dependent_background_vectors(self):
        result = optimal_mixture_histogram_groups(FOUR_CLOCKS, 2)
        cases = 0
        # The second context chooses one common low/high stock for both
        # backgrounds. Their vector is independent of the four focal clocks.
        for contexts in (
            [(Fraction(1), [[1, 2, 1], [2, 1, 1]])],
            [(Fraction(1, 2), [[1, 0, 0], [1, 0, 0]]),
             (Fraction(1, 2), [[0, 0, 1], [0, 0, 1]])],
        ):
            laws = [(weight, _selection_laws(FOUR_CLOCKS + background))
                    for weight, background in contexts]
            for survivors in range(7):
                def tails(groups):
                    return [sum(weight * _tails(law[survivors], groups)[tail]
                                for weight, law in laws) for tail in range(2)]
                target = tails(result["groups"])
                for groups in partitions(list(range(4)), 2):
                    actual = tails(groups)
                    self.assertTrue(all(a <= b for a, b in zip(actual, target)))
                    self.assertLessEqual(sum(actual), sum(target))
                    cases += 1
        self.assertEqual(cases, 42)

    def test_extreme_pairs_minimize_intact_and_maximize_redundant_tails(self):
        extreme = [[0, 5], [1, 4], [2, 3]]
        candidates = list(partitions(list(range(6)), 2))
        self.assertEqual(len(candidates), 15)
        cases = tail_checks = strict_intact = strict_redundant = 0

        def count_tails(law, groups):
            intact = _tails(law, groups)
            masks = [sum(1 << label for label in group) for group in groups]
            redundant = [Fraction(0)] * 3
            # Compute the redundant count directly, also when backgrounds
            # make the number of retained focal labels random.
            for selected, probability in law.items():
                working = sum(bool(selected & mask) for mask in masks)
                for threshold in range(working):
                    redundant[threshold] += probability
            return intact, redundant

        for contexts in (
            [(Fraction(1), [])],
            [(Fraction(1, 2), [[1, 0, 0], [1, 0, 0]]),
             (Fraction(1, 2), [[0, 0, 1], [0, 0, 1]])],
        ):
            # The shared low/high stock makes the two backgrounds dependent;
            # their whole vector remains independent of the six focal clocks.
            components = [(weight, _selection_laws(SIX_CLOCKS + background))
                          for weight, background in contexts]
            for survivors in components[0][1]:
                law = {}
                for weight, laws in components:
                    for selected, probability in laws[survivors].items():
                        law[selected] = law.get(selected, Fraction(0)) + weight * probability
                self.assertEqual(sum(law.values()), 1)
                target_intact, target_redundant = count_tails(law, extreme)
                for groups in candidates:
                    actual_intact, actual_redundant = count_tails(law, groups)
                    with self.subTest(contexts=len(contexts), k=survivors, groups=groups):
                        for threshold in range(3):
                            self.assertLessEqual(target_intact[threshold], actual_intact[threshold])
                            self.assertLessEqual(actual_redundant[threshold], target_redundant[threshold])
                            strict_intact += target_intact[threshold] < actual_intact[threshold]
                            strict_redundant += actual_redundant[threshold] < target_redundant[threshold]
                            tail_checks += 2
                    cases += 1
        self.assertEqual(cases, 240)
        self.assertEqual(tail_checks, 1440)
        self.assertGreater(strict_intact, 0)
        self.assertGreater(strict_redundant, 0)

    def test_row_scaling_and_input_permutation(self):
        baseline = optimal_mixture_histogram_groups(SIX_CLOCKS, 3)
        scaled = [[value * (label + 2) for value in row]
                  for label, row in enumerate(SIX_CLOCKS)]
        result = optimal_mixture_histogram_groups(scaled, 3)
        for key in ("baseLabels", "baseMasses", "mixingWeights", "labels", "groups"):
            self.assertEqual(result[key], baseline[key])
        permutation = [3, 0, 5, 1, 4, 2]
        result = optimal_mixture_histogram_groups([SIX_CLOCKS[label] for label in permutation], 3)
        self.assertEqual(result["baseLabels"], [2, 1])
        self.assertEqual(result["mixingWeights"], [baseline["mixingWeights"][i] for i in permutation])
        self.assertEqual(result["labels"], [2, 4, 0, 5, 3, 1])
        self.assertEqual(result["groups"], [[2, 4, 0], [5, 3, 1]])

    def test_normalized_ties_identical_laws_and_single_group(self):
        result = optimal_mixture_histogram_groups([[1, 3], [2, 6], [3, 1], [6, 2]], 2)
        self.assertEqual(result["baseLabels"], [0, 2])
        self.assertEqual(result["mixingWeights"], ["0", "0", "1", "1"])
        self.assertEqual(result["groups"], [[0, 1], [2, 3]])
        for rows, size in (([[1, 2], [2, 4], [3, 6], [4, 8]], 2),
                           ([[1], [MAX_COUNT]], 2), ([[1, 2], [2, 1]], 2)):
            result = optimal_mixture_histogram_groups(rows, size)
            if rows != [[1, 2], [2, 1]]:
                self.assertEqual(result["baseLabels"], [0, 0])
                self.assertEqual(result["mixingWeights"], ["0"] * len(rows))
                self.assertEqual(result["certificate"]["affineDimension"], 0)
                self.assertIsNone(result["certificate"]["differingBin"])
            self.assertEqual(result["labels"], list(range(len(rows))))
        # Odd n is legal when the requested size divides n.
        self.assertEqual(optimal_mixture_histogram_groups([[1, 3], [2, 2], [3, 1]], 3)["groups"],
                         [[0, 1, 2]])

    def test_later_differing_coordinate_and_exact_small_deviation_rejection(self):
        rows = [[2, 1, 3, 2], [2, 2, 2, 2], [2, 3, 1, 2], [4, 4, 4, 4]]
        result = optimal_mixture_histogram_groups(rows, 2)
        self.assertEqual(result["certificate"]["differingBin"], 1)
        self.assertEqual(result["baseLabels"], [0, 2])
        self.assertEqual(result["mixingWeights"], ["0", "1/2", "1", "1/2"])
        self.assertEqual(result["groups"], [[0, 1], [3, 2]])
        scaled = [[value * 100_000 for value in row] for row in rows]
        scaled[3][2] += 1
        scaled[3][3] -= 1
        with self.assertRaisesRegex(ValueError, "affine-collinear"):
            optimal_mixture_histogram_groups(scaled, 2)

    def test_noncollinear_profiles_are_rejected_without_fallback(self):
        for rows, size in (([[1, 0, 0], [0, 1, 0], [0, 0, 1]], 3),
                           ([[1, 9, 20], [10, 1, 19], [19, 1, 10], [20, 9, 1]], 2)):
            with self.subTest(rows=rows), self.assertRaisesRegex(ValueError, "affine-collinear"):
                optimal_mixture_histogram_groups(rows, size)

    def test_certificate_scope_and_copied_inputs(self):
        rows = [row.copy() for row in SIX_CLOCKS]
        result = optimal_mixture_histogram_groups(rows, 3)
        self.assertEqual(result["contract"], "algal.lab.mixture-stochastic-grouping.v1")
        self.assertEqual(result["status"], "structurally-optimal")
        self.assertEqual(result["objective"], "intact")
        self.assertEqual(result["probabilityEvaluations"], 0)
        self.assertIn("usual stochastic order", result["optimality"])
        self.assertIn("histogram laws", result["scope"])
        self.assertIn("every fixed survivor count", result["horizons"])
        self.assertIn("may cross", result["certificate"]["baseCdfOrder"])
        self.assertTrue(any("mutually independent" in text for text in result["assumptions"]))
        self.assertTrue(any("jointly independent" in text for text in result["assumptions"]))
        self.assertTrue(any("sampling-confidence" in text
                            for text in result["certificate"]["limitations"]))
        rows[0][0] = 999
        rows.append([1, 1, 1])
        self.assertEqual(result["histograms"], SIX_CLOCKS)

    def test_maximum_shape(self):
        first = [1 + index % 2 for index in range(MAX_BINS)]
        second = [2 - index % 2 for index in range(MAX_BINS)]
        rows = [[(MAX_CLOCKS - 1 - label) * a + label * b for a, b in zip(first, second)]
                for label in range(MAX_CLOCKS)]
        result = optimal_mixture_histogram_groups(rows, 16)
        self.assertEqual(result["baseLabels"], [0, MAX_CLOCKS - 1])
        self.assertEqual(result["mixingWeights"],
                         [str(Fraction(label, MAX_CLOCKS - 1)) for label in range(MAX_CLOCKS)])
        self.assertEqual(len(result["groups"]), 8)
        self.assertEqual(result["probabilityEvaluations"], 0)
        self.assertEqual(len(result["baseMasses"][0]), MAX_BINS)
        self.assertLess(len(json.dumps(result).encode()), 1_048_576)

    def test_shared_strict_admission(self):
        invalid = [None, {}, (), [], [[1]], [[1]] * (MAX_CLOCKS + 1), [[], []],
                   [[1] * (MAX_BINS + 1)] * 2, [[1], [1, 1]], [[1], None],
                   [[1], (1,)], [[0], [1]], [[-1], [1]], [[MAX_COUNT + 1], [1]],
                   [[10 ** 1000], [1]], [[True], [1]], [[1.0], [1]],
                   [[float("nan")], [1]], [[float("inf")], [1]], [["1"], [1]], [[None], [1]]]
        for rows in invalid:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                optimal_mixture_histogram_groups(rows, 2)
        for size in (None, True, False, 0, 1, -1, 4, 7, 2.0, "3", float("nan")):
            with self.subTest(size=size), self.assertRaises(ValueError):
                optimal_mixture_histogram_groups([[1]] * 6, size)

    def test_example_and_module_cli(self):
        example = Path(__file__).resolve().parents[1] / "examples" / "mixture-stochastic-groups.json"
        value = json.loads(example.read_text(encoding="utf-8"))
        self.assertEqual(value, {"histograms": SIX_CLOCKS, "groupSize": 3})
        result = subprocess.run(
            [sys.executable, "-m", "research.mixture_stochastic_groups", str(example)],
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), optimal_mixture_histogram_groups(SIX_CLOCKS, 3))

    def test_cli_rejects_unknown_duplicate_fields_and_invalid_numbers(self):
        invalid = [
            '{"histograms":[[1],[1]],"groupSize":2,"objective":"intact"}',
            '{"histograms":[[1],[1]],"groupSize":2,"extra":0}',
            '{"histograms":[[1],[1]],"groupSize":2,"histograms":[[2],[2]]}',
            '{"histograms":[[1],[1]],"groupSize":2,"groupSize":2}',
            '{"histograms":[[1.0],[1]],"groupSize":2}',
            '{"histograms":[[1e0],[1]],"groupSize":2}',
            '{"histograms":[[true],[1]],"groupSize":2}',
            '{"histograms":[[NaN],[1]],"groupSize":2}',
            '{"histograms":[[Infinity],[1]],"groupSize":2}',
            '{"histograms":[[-Infinity],[1]],"groupSize":2}',
            '{"histograms":[[1],[1]],"groupSize":2.0}',
            '{"histograms":[[1],[1]],"groupSize":true}',
            '{"histograms":[[1],[1]]}', '{"groupSize":2}', '{}', '[]', 'null', '{',
            '{"histograms":[[1,0,0],[0,1,0],[0,0,1]],"groupSize":3}',
        ]
        with TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            for raw in invalid:
                source.write_text(raw, encoding="utf-8")
                output = StringIO()
                with self.subTest(raw=raw), redirect_stdout(output), self.assertRaises(ValueError):
                    main([str(source)])
                self.assertEqual(output.getvalue(), "")

    def test_cli_input_byte_limit_and_invalid_utf8(self):
        raw = b'{"histograms":[[1],[1]],"groupSize":2}'
        with TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            source.write_bytes(raw + b" " * (MAX_INPUT_BYTES - len(raw)))
            output = StringIO()
            with redirect_stdout(output):
                main([str(source)])
            self.assertEqual(json.loads(output.getvalue())["groups"], [[0, 1]])
            source.write_bytes(raw + b" " * (MAX_INPUT_BYTES + 1 - len(raw)))
            with self.assertRaisesRegex(ValueError, "input exceeds 131072 bytes"):
                main([str(source)])
            source.write_bytes(b"\xff")
            with self.assertRaises(UnicodeDecodeError):
                main([str(source)])


if __name__ == "__main__":
    unittest.main()
