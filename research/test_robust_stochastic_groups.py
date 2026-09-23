"""Exact ranking checks for CDF projection and its regret certificate."""
from contextlib import redirect_stdout
from fractions import Fraction
from io import StringIO
from itertools import combinations, product
import json
from math import comb
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from research.robust_stochastic_groups import main, robust_histogram_groups
from research.stochastic_groups import (
    MAX_BINS, MAX_CLOCKS, MAX_COUNT, MAX_INPUT_BYTES, optimal_histogram_groups,
)
from research.test_intact_groups import partitions


CROSSING = [[1, 8, 11], [2, 5, 13], [3, 5, 12], [4, 5, 11]]
SIX_CLOCKS = [[1, 9, 10], [2, 6, 12], [3, 8, 9], [4, 5, 11], [5, 7, 8], [6, 4, 10]]


def _cdfs(rows):
    return [[sum(Fraction(value) for value in row[:end]) / sum(row)
             for end in range(len(row) + 1)] for row in rows]


def _projected_rows(result):
    endpoints = [[Fraction(value) for value in row]
                 for row in result["projectedCdfEndpoints"]]
    return [[right - left for left, right in zip(row, row[1:])] for row in endpoints]


def _selection_laws(rows, horizons=None):
    """Independent categorical oracle for uniform common-bin scores.

    Conditional on bins, every subset filling the cutoff bin is equiprobable.
    Enumerating those subsets yields whole selected-set laws, without CDF
    ordering, projection, grouping exchanges, or an inclusion-polynomial oracle.
    Only nonzero bins are enumerated, keeping the sparse sharpness case small.
    """
    n = len(rows)
    horizons = tuple(range(n + 1)) if horizons is None else horizons
    laws = {k: {} for k in horizons}
    masses = [[Fraction(value) / sum(row) for value in row] for row in rows]
    choices = [[index for index, value in enumerate(row) if value] for row in rows]
    for intervals in product(*choices):
        mass = Fraction(1)
        for label, interval in enumerate(intervals):
            mass *= masses[label][interval]
        ranking = sorted(intervals, reverse=True)
        for survivors, law in laws.items():
            if survivors == 0:
                law[0] = law.get(0, Fraction(0)) + mass
                continue
            cutoff = ranking[survivors - 1]
            above = [label for label, interval in enumerate(intervals) if interval > cutoff]
            tied = [label for label, interval in enumerate(intervals) if interval == cutoff]
            slots = survivors - len(above)
            weight = mass / comb(len(tied), slots)
            mask = sum(1 << label for label in above)
            for subset in combinations(tied, slots):
                selected = mask | sum(1 << label for label in subset)
                law[selected] = law.get(selected, Fraction(0)) + weight
    for law in laws.values():
        assert sum(law.values()) == 1
    return laws


def _tails(law, groups):
    masks = [sum(1 << label for label in group) for group in groups]
    result = [Fraction(0)] * len(groups)
    for selected, probability in law.items():
        intact = sum(selected & mask == mask for mask in masks)
        for threshold in range(intact):
            result[threshold] += probability
    return result


class RobustStochasticGroupsTests(unittest.TestCase):
    def test_exact_projection_and_minimax_witness(self):
        result = robust_histogram_groups(CROSSING, 2)
        self.assertEqual(result["labels"], [0, 1, 2, 3])
        self.assertEqual(result["groups"], [[0, 1], [2, 3]])
        self.assertEqual(result["projectedCdfEndpoints"], [
            ["0", "1/20", "2/5", "1"], ["0", "1/10", "2/5", "1"],
            ["0", "3/20", "17/40", "1"], ["0", "1/5", "9/20", "1"],
        ])
        self.assertEqual(result["kolmogorovErrors"], ["1/20", "1/20", "1/40", "0"])
        self.assertEqual(result["minimaxUniformRadius"], "1/20")
        self.assertEqual(result["totalKolmogorovError"], "1/8")
        self.assertEqual(result["regretBounds"], {
            "mean": "1/4", "eachTail": "1/4", "summedPositiveTailShortfall": "1/4",
        })
        witness = result["certificate"]["minimaxWitness"]
        self.assertEqual(witness, {
            "earlierLabel": 0, "laterLabel": 1, "endpoint": 2, "violation": "1/10",
        })
        original = _cdfs(CROSSING)
        gap = original[witness["earlierLabel"]][witness["endpoint"]] - original[
            witness["laterLabel"]][witness["endpoint"]]
        # Any ordered approximant must close this gap with two error budgets.
        self.assertEqual(gap, 2 * Fraction(result["minimaxUniformRadius"]))
        insufficient = gap / 2 - Fraction(1, 1000)
        self.assertGreater(original[witness["earlierLabel"]][witness["endpoint"]] - insufficient,
                           original[witness["laterLabel"]][witness["endpoint"]] + insufficient)
        with self.assertRaisesRegex(ValueError, "cannot certify CDF block cut"):
            optimal_histogram_groups(CROSSING, 2)

    def test_projection_is_a_proper_ordered_chain_with_exact_errors(self):
        for rows, size in ((CROSSING, 2), (SIX_CLOCKS, 3),
                           ([[0, 100, 0], [1, 0, 99], [2, 97, 1], [3, 0, 97]], 2)):
            with self.subTest(rows=rows):
                result = robust_histogram_groups(rows, size)
                labels = result["labels"]
                original = _cdfs(rows)
                reference = _cdfs(_projected_rows(result))
                for row in reference:
                    self.assertEqual((row[0], row[-1]), (0, 1))
                    self.assertTrue(all(left <= right for left, right in zip(row, row[1:])))
                for left, right in zip(labels, labels[1:]):
                    self.assertTrue(all(a <= b for a, b in zip(reference[left], reference[right])))
                errors = [max(abs(a - b) for a, b in zip(old, new))
                          for old, new in zip(original, reference)]
                self.assertEqual(errors, list(map(Fraction, result["kolmogorovErrors"])))
                # Brute pairs are confined to this small independent check;
                # production uses prefix maxima to avoid quadratic work.
                largest = max([Fraction(0)] + [original[a][t] - original[b][t]
                              for a, b in combinations(labels, 2)
                              for t in range(len(rows[0]) + 1)])
                self.assertEqual(max(errors), largest / 2)
                self.assertEqual(Fraction(result["minimaxUniformRadius"]), largest / 2)
                self.assertEqual(Fraction(result["totalKolmogorovError"]), sum(errors))

    def test_exact_tail_mean_and_simultaneous_regret_bounds_for_all_partitions(self):
        cases = 0
        for rows, size in ((CROSSING, 2), (SIX_CLOCKS, 2), (SIX_CLOCKS, 3),
                           ([[i, 8 - i] for i in range(8)], 4)):
            result = robust_histogram_groups(rows, size)
            original = _selection_laws(rows)
            reference = _selection_laws(_projected_rows(result))
            candidates = list(partitions(list(range(len(rows))), size))
            error = Fraction(result["totalKolmogorovError"])
            bounds = {key: Fraction(value) for key, value in result["regretBounds"].items()}
            for survivors in original:
                target_original = _tails(original[survivors], result["groups"])
                target_reference = _tails(reference[survivors], result["groups"])
                for groups in candidates:
                    with self.subTest(n=len(rows), size=size, k=survivors, groups=groups):
                        actual = _tails(original[survivors], groups)
                        projected = _tails(reference[survivors], groups)
                        self.assertLessEqual(sum(abs(a - b) for a, b in zip(actual, projected)),
                                             error)
                        self.assertLessEqual(abs(sum(actual) - sum(projected)), error)
                        self.assertTrue(all(a <= b for a, b in zip(projected, target_reference)))
                        shortfalls = [max(Fraction(0), a - b)
                                      for a, b in zip(actual, target_original)]
                        self.assertLessEqual(max(shortfalls), bounds["eachTail"])
                        self.assertLessEqual(sum(shortfalls), bounds["summedPositiveTailShortfall"])
                        self.assertLessEqual(sum(actual) - sum(target_original), bounds["mean"])
                    cases += 1
        self.assertEqual(cases, 505)

    def test_independent_and_dependent_background_laws(self):
        result = robust_histogram_groups(CROSSING, 2)
        reference_rows = _projected_rows(result)
        # In the mixture, both background clocks draw from the same randomly
        # chosen low/high stock. They are dependent unconditionally while the
        # whole vector is independent of all focal clocks.
        for contexts in (
            [(Fraction(1), [[2, 1, 1], [1, 2, 1]])],
            [(Fraction(1, 2), [[1, 0, 0], [1, 0, 0]]),
             (Fraction(1, 2), [[0, 0, 1], [0, 0, 1]])],
        ):
            originals = [(weight, _selection_laws(CROSSING + background))
                         for weight, background in contexts]
            references = [(weight, _selection_laws(reference_rows + background))
                          for weight, background in contexts]
            for survivors in range(7):
                def mixture(laws, groups):
                    tails = [Fraction(0)] * 2
                    for weight, law in laws:
                        tails = [old + weight * new for old, new in
                                 zip(tails, _tails(law[survivors], groups))]
                    return tails
                target = mixture(originals, result["groups"])
                target_reference = mixture(references, result["groups"])
                for groups in partitions(list(range(4)), 2):
                    actual = mixture(originals, groups)
                    projected = mixture(references, groups)
                    self.assertTrue(all(a <= b for a, b in zip(projected, target_reference)))
                    self.assertLessEqual(sum(abs(a - b) for a, b in zip(actual, projected)),
                                         Fraction(result["totalKolmogorovError"]))
                    self.assertLessEqual(sum(max(Fraction(0), a - b) for a, b in zip(actual, target)),
                                         Fraction(result["regretBounds"]["summedPositiveTailShortfall"]))

    def test_categorical_oracle_exchangeability(self):
        rows = [[1, 2]] * 4
        laws = _selection_laws(rows)
        for survivors, law in laws.items():
            self.assertEqual(len(law), comb(4, survivors))
            self.assertEqual(set(law.values()), {Fraction(1, comb(4, survivors))})
        self.assertEqual(_tails(laws[2], [[0, 1], [2, 3]]), [Fraction(1, 3), 0])

    def test_fixed_reference_regret_sharpness_example(self):
        # Scale and translate the scratch theorem's delta=1/4 example onto
        # common unit bins. Sparse enumeration uses only 448 assignments.
        scale = 4
        bins = 6 * scale
        reference = [[0] * bins for _ in range(4)]
        for label, start in ((0, 5 * scale), (1, 2 * scale),
                             (2, 2 * scale), (3, 0)):
            reference[label][start:start + scale] = [scale] * scale
        original = [row.copy() for row in reference]
        original[2][2 * scale] = 0
        original[2][3 * scale:4 * scale] = [1] * scale
        reference_law = _selection_laws(reference, (2,))[2]
        original_law = _selection_laws(original, (2,))[2]
        target, competitor = [[0, 1], [2, 3]], [[0, 2], [1, 3]]
        self.assertEqual(_tails(reference_law, target), _tails(reference_law, competitor))
        first = _tails(original_law, target)
        second = _tails(original_law, competitor)
        delta = max(abs(a - b) for a, b in zip(_cdfs(original)[2], _cdfs(reference)[2]))
        self.assertEqual(delta, Fraction(1, 4))
        self.assertEqual(second[0] - first[0], 2 * delta - delta * delta)
        self.assertEqual(sum(second) - sum(first), Fraction(7, 16))
        self.assertEqual(_tails(original_law, [[0, 3], [1, 2]]), [0, 0])

    def test_original_labels_permutations_and_normalization(self):
        permutation = [2, 0, 3, 1]
        result = robust_histogram_groups([CROSSING[label] for label in permutation], 2)
        self.assertEqual(result["labels"], [1, 3, 0, 2])
        self.assertEqual(result["groups"], [[1, 3], [0, 2]])
        baseline = robust_histogram_groups(CROSSING, 2)
        for key in ("projectedCdfEndpoints", "kolmogorovErrors"):
            self.assertEqual(result[key], [baseline[key][label] for label in permutation])
        scaled = [[value * (label + 2) for value in row] for label, row in enumerate(CROSSING)]
        rescaled = robust_histogram_groups(scaled, 2)
        for key in ("labels", "groups", "projectedCdfEndpoints", "kolmogorovErrors",
                    "minimaxUniformRadius", "totalKolmogorovError", "regretBounds"):
            self.assertEqual(rescaled[key], baseline[key])

    def test_ordered_inputs_ties_and_single_groups(self):
        for rows, size in (([[i, 6 - i] for i in range(6)], 3),
                           ([[1, 1], [2, 2], [3, 3], [4, 4]], 2),
                           ([[1], [MAX_COUNT]], 2)):
            result = robust_histogram_groups(rows, size)
            self.assertEqual(result["groups"], optimal_histogram_groups(rows, size)["groups"])
            self.assertEqual(result["minimaxUniformRadius"], "0")
            self.assertEqual(result["totalKolmogorovError"], "0")
            self.assertEqual(set(result["regretBounds"].values()), {"0"})
            self.assertIsNone(result["certificate"]["minimaxWitness"])
            self.assertEqual(result["status"], "approximation-certified")
        result = robust_histogram_groups([[2, 1], [1, 2], [1, 1]], 3)
        self.assertEqual(result["labels"], [1, 2, 0])
        self.assertEqual(result["groups"], [[1, 2, 0]])

    def test_regret_bound_clipping(self):
        result = robust_histogram_groups([[0, 100, 0], [1, 0, 99],
                                          [2, 97, 1], [3, 0, 97]], 2)
        self.assertGreater(2 * Fraction(result["totalKolmogorovError"]), 2)
        self.assertEqual(result["regretBounds"], {
            "mean": "2", "eachTail": "1", "summedPositiveTailShortfall": "2",
        })

    def test_positive_regret_remains_within_an_informative_certificate(self):
        rows = [[1, 1, 18], [2, 8, 10], [3, 2, 15], [4, 7, 9]]
        result = robust_histogram_groups(rows, 2)
        law = _selection_laws(rows, (2,))[2]
        candidate = _tails(law, result["groups"])
        competitor = _tails(law, [[0, 2], [1, 3]])
        regret = sum(competitor) - sum(candidate)
        self.assertEqual(result["groups"], [[0, 1], [2, 3]])
        self.assertEqual(regret, Fraction(387, 4000))
        self.assertEqual(result["totalKolmogorovError"], "1/4")
        self.assertEqual(set(result["regretBounds"].values()), {"1/2"})
        self.assertGreater(regret, 0)
        self.assertLess(regret, Fraction(result["regretBounds"]["mean"]))
        self.assertEqual(result["status"], "approximation-certified")

    def test_certificate_scope_and_copied_source(self):
        rows = [row.copy() for row in CROSSING]
        result = robust_histogram_groups(rows, 2)
        self.assertEqual(result["contract"], "algal.lab.robust-stochastic-grouping.v1")
        self.assertEqual(result["status"], "approximation-certified")
        self.assertEqual(result["objective"], "intact")
        self.assertEqual(result["probabilityEvaluations"], 0)
        self.assertIn("histogram laws", result["scope"])
        self.assertIn("every fixed survivor count", result["horizons"])
        self.assertTrue(any("mutually independent" in text for text in result["assumptions"]))
        self.assertTrue(any("jointly independent" in text for text in result["assumptions"]))
        self.assertIn("fixed label order", result["certificate"]["minimaxScope"])
        self.assertIn("one competing partition", result["certificate"]["regretComparison"])
        self.assertTrue(any("sum of errors" in text for text in result["certificate"]["limitations"]))
        rows[0][0] = 999
        rows.append([1, 1, 1])
        self.assertEqual(result["histograms"], CROSSING)

    def test_maximum_admitted_shape_without_probability_oracle(self):
        rows = [[MAX_COUNT - (label * endpoint) % 997 for endpoint in range(MAX_BINS)]
                for label in range(MAX_CLOCKS)]
        result = robust_histogram_groups(rows, 16)
        self.assertEqual(len(result["groups"]), 8)
        self.assertEqual(sorted(result["labels"]), list(range(MAX_CLOCKS)))
        self.assertEqual(len(result["projectedCdfEndpoints"]), MAX_CLOCKS)
        self.assertTrue(all(len(row) == MAX_BINS + 1 for row in result["projectedCdfEndpoints"]))
        self.assertEqual(result["probabilityEvaluations"], 0)
        self.assertLess(len(json.dumps(result).encode()), 1_048_576)

    def test_shared_strict_admission(self):
        invalid = [None, {}, (), [], [[1]], [[1]] * (MAX_CLOCKS + 1), [[], []],
                   [[1] * (MAX_BINS + 1)] * 2, [[1], [1, 1]], [[1], None],
                   [[1], (1,)], [[0], [1]], [[-1], [1]], [[MAX_COUNT + 1], [1]],
                   [[10 ** 1000], [1]], [[True], [1]], [[1.0], [1]],
                   [[float("nan")], [1]], [[float("inf")], [1]], [["1"], [1]], [[None], [1]]]
        for rows in invalid:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                robust_histogram_groups(rows, 2)
        for size in (None, True, False, 0, 1, -1, 4, 7, 2.0, "3", float("nan")):
            with self.subTest(size=size), self.assertRaises(ValueError):
                robust_histogram_groups([[1]] * 6, size)

    def test_cli_emits_the_public_certificate(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            source.write_text(json.dumps({"histograms": CROSSING, "groupSize": 2}), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "research.robust_stochastic_groups", str(source)],
                cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=10,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), robust_histogram_groups(CROSSING, 2))

    def test_cli_rejects_unknown_duplicate_and_invalid_numbers(self):
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
        ]
        with TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            for raw in invalid:
                source.write_text(raw, encoding="utf-8")
                output = StringIO()
                with self.subTest(raw=raw), redirect_stdout(output), self.assertRaises(ValueError):
                    main([str(source)])
                self.assertEqual(output.getvalue(), "")

    def test_cli_input_byte_boundary(self):
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


if __name__ == "__main__":
    unittest.main()
