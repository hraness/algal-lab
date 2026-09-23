"""Bounded exact partition comparisons and structural admission checks."""
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

from research.rank_selection import STOCHASTIC_ONLY_EXAMPLE
from research.stochastic_groups import (
    MAX_BINS, MAX_CLOCKS, MAX_COUNT, MAX_INPUT_BYTES, main, optimal_histogram_groups,
)
from research.test_intact_groups import partitions
from research.test_rank_selection import categorical_oracle
from research.spikes.stochastic.tails import _selection_laws, _tails


WITHIN_PAIR_CROSSING = [[0, 2, 0, 4], [1, 0, 2, 3], [3, 3, 0, 0], [4, 0, 2, 0]]
STRICT_STOCHASTIC_EXAMPLE = [[1, 9, 20], [10, 1, 19], [19, 1, 10], [20, 9, 1]]


def _score(probabilities, groups):
    return sum((probabilities[tuple(sorted(group))] for group in groups), Fraction(0))


def categorical_group_oracle(rows, group_size, survivors):
    """Integrate all-member inclusion by bins and uniform cutoff combinations.

    This bounded test reference does not sort CDFs or evaluate the structural
    criterion. Given bin choices, it counts how many equiprobable selections
    from the cutoff bin contain every still-needed member of a given group.
    """
    n = len(rows)
    probabilities = {group: Fraction(0) for group in combinations(range(n), group_size)}
    if survivors < group_size:
        return probabilities
    masses = [[Fraction(count, sum(row)) for count in row] for row in rows]
    for intervals in product(range(len(rows[0])), repeat=n):
        mass = Fraction(1)
        for label, interval in enumerate(intervals):
            mass *= masses[label][interval]
        if not mass:
            continue
        cutoff = sorted(intervals, reverse=True)[survivors - 1]
        above_count = sum(interval > cutoff for interval in intervals)
        cutoff_count = sum(interval == cutoff for interval in intervals)
        slots = survivors - above_count
        denominator = comb(cutoff_count, slots)
        for group in probabilities:
            if any(intervals[label] < cutoff for label in group):
                continue
            needed = sum(intervals[label] == cutoff for label in group)
            if needed <= slots:
                probabilities[group] += mass * Fraction(
                    comb(cutoff_count - needed, slots - needed), denominator
                )
    return probabilities


class StochasticGroupsTests(unittest.TestCase):
    def test_every_pair_partition_at_every_horizon_for_small_populations(self):
        # Preserve the independent pair oracle and all n=4/6/8 comparisons.
        # Two bins keep the eight-clock case at 2^8 categorical cells.
        fixtures = [
            STOCHASTIC_ONLY_EXAMPLE,
            WITHIN_PAIR_CROSSING,
            STRICT_STOCHASTIC_EXAMPLE,
            [[i, 6 - i] for i in range(6)],
            [[i, 8 - i] for i in range(8)],
        ]
        comparisons = 0
        horizons = 0
        for rows in fixtures:
            n = len(rows)
            candidate = optimal_histogram_groups(rows, 2)["groups"]
            alternatives = list(partitions(list(range(n)), 2))
            for survivors in range(n + 1):
                with self.subTest(clocks=n, rows=rows, survivors=survivors):
                    probabilities = categorical_oracle(rows, survivors)
                    best = max(_score(probabilities, groups) for groups in alternatives)
                    self.assertEqual(_score(probabilities, candidate), best)
                comparisons += len(alternatives)
                horizons += 1
        self.assertEqual((comparisons, horizons), (1095, 31))

    def test_every_triple_and_four_member_partition_at_every_horizon(self):
        comparisons = 0
        horizons = 0
        for n, size, partition_count in ((6, 3, 10), (8, 4, 35), (9, 3, 280)):
            rows = [[i, n - i] for i in range(n)]
            candidate = optimal_histogram_groups(rows, size)["groups"]
            alternatives = list(partitions(list(range(n)), size))
            self.assertEqual(len(alternatives), partition_count)
            for survivors in range(n + 1):
                with self.subTest(clocks=n, size=size, survivors=survivors):
                    probabilities = categorical_group_oracle(rows, size, survivors)
                    self.assertEqual(sum(probabilities.values(), Fraction(0)),
                                     Fraction(comb(survivors, size)) if survivors >= size else 0)
                    best = max(_score(probabilities, groups) for groups in alternatives)
                    self.assertEqual(_score(probabilities, candidate), best)
                comparisons += len(alternatives)
                horizons += 1
        self.assertEqual((comparisons, horizons), (3185, 26))

    def test_group_oracle_with_identically_distributed_clocks(self):
        # Exchangeability gives a closed form independent of the reference's
        # categorical enumeration, including partially filled cutoff bins.
        rows = [[1, 2] for _ in range(6)]
        for size in (2, 3, 4, 6):
            for survivors in range(7):
                with self.subTest(size=size, survivors=survivors):
                    expected = (Fraction(comb(survivors, size), comb(6, size))
                                if survivors >= size else Fraction(0))
                    probabilities = categorical_group_oracle(rows, size, survivors)
                    self.assertEqual(set(probabilities.values()), {expected})

    def test_independent_backgrounds_at_every_combined_horizon(self):
        for n, size, background in ((4, 2, [[3, 1], [1, 3]]),
                                    (6, 3, [[1, 1]])):
            focal = [[i, n - i] for i in range(n)]
            candidate = optimal_histogram_groups(focal, size)["groups"]
            alternatives = list(partitions(list(range(n)), size))
            for survivors in range(n + len(background) + 1):
                with self.subTest(clocks=n, size=size, survivors=survivors):
                    rows = focal + background
                    probabilities = (categorical_oracle(rows, survivors) if size == 2 else
                                     categorical_group_oracle(rows, size, survivors))
                    self.assertEqual(_score(probabilities, candidate),
                                     max(_score(probabilities, groups) for groups in alternatives))

    def test_crossing_within_both_pairs_is_admitted(self):
        result = optimal_histogram_groups(WITHIN_PAIR_CROSSING, 2)
        self.assertEqual(result["groups"], [[0, 1], [2, 3]])
        for first, second in result["groups"]:
            differences = [sum(WITHIN_PAIR_CROSSING[first][:end])
                           - sum(WITHIN_PAIR_CROSSING[second][:end])
                           for end in range(1, 4)]
            self.assertLess(min(differences), 0)
            self.assertGreater(max(differences), 0)
        self.assertEqual(result["certificate"]["withinGroupCdfOrder"], "unrestricted")

    def test_crossing_within_two_larger_groups_is_admitted(self):
        rows = [WITHIN_PAIR_CROSSING[0], WITHIN_PAIR_CROSSING[1], [0, 1, 1, 4],
                WITHIN_PAIR_CROSSING[2], WITHIN_PAIR_CROSSING[3], [4, 1, 1, 0]]
        result = optimal_histogram_groups(rows, 3)
        self.assertEqual(result["groups"], [[2, 0, 1], [3, 4, 5]])
        self.assertEqual(result["groupSize"], 3)
        # Both groups retain the crossing pair from the four-clock fixture.
        for a, b in ((0, 1), (3, 4)):
            differences = [sum(rows[a][:end]) - sum(rows[b][:end]) for end in range(1, 4)]
            self.assertLess(min(differences), 0)
            self.assertGreater(max(differences), 0)

    def test_three_separated_crossing_triples_are_admitted(self):
        # Each group occupies its own disjoint three-bin interval. The cuts
        # are ordered, but [0,2,1] and [1,0,2] cross inside each interval.
        blocks = []
        for offset in (6, 3, 0):
            blocks.append([[0] * offset + row + [0] * (6 - offset)
                           for row in ([0, 2, 1], [1, 0, 2], [0, 1, 2])])
        for left, right in zip(blocks, blocks[1:]):
            self.assertTrue(all(max(sum(row[:end]) for row in left)
                                <= min(sum(row[:end]) for row in right)
                                for end in range(10)))
        triples = [row for block in blocks for row in block]
        result = optimal_histogram_groups(triples, 3)
        self.assertEqual([sorted(group) for group in result["groups"]],
                         [[0, 1, 2], [3, 4, 5], [6, 7, 8]])
        self.assertEqual(result["certificate"]["withinGroupCdfOrder"], "unrestricted")
        pairs = [row for block in blocks for row in block[:2]]
        result = optimal_histogram_groups(pairs, 2)
        self.assertEqual(result["groups"], [[0, 1], [2, 3], [4, 5]])
        self.assertEqual(result["certificate"]["withinGroupCdfOrder"], "unrestricted")

    def test_overlapping_positive_crossing_triples_dominate_all_partition_tails(self):
        # Within each target block the first two CDFs cross. Every density
        # is positive, so all score orders and survivor subsets are possible.
        rows = ((10, 20, 70), (11, 18, 71), (12, 19, 69),
                (30, 30, 40), (31, 28, 41), (32, 29, 39),
                (60, 20, 20), (61, 18, 21), (62, 19, 19))
        result = optimal_histogram_groups([list(row) for row in rows], 3)
        self.assertEqual(result["groups"], [[0, 1, 2], [3, 4, 5], [6, 7, 8]])
        for a, b in ((0, 1), (3, 4), (6, 7)):
            self.assertLess(rows[a][0], rows[b][0])
            self.assertGreater(sum(rows[a][:2]), sum(rows[b][:2]))
        horizons = (3, 4, 5, 6, 7)
        laws, _, _, _ = _selection_laws(rows, horizons)
        alternatives = [tuple(sum(1 << label for label in group) for group in partition)
                        for partition in partitions(list(range(9)), 3)]
        candidate = (7, 56, 448)
        comparisons = 0
        for k in horizons:
            best_tails = _tails(laws[k], candidate)
            for partition in alternatives:
                for actual, best in zip(_tails(laws[k], partition), best_tails):
                    self.assertLessEqual(actual, best)
                    comparisons += 1
        self.assertEqual(comparisons, 4200)

    def test_larger_crossing_block_configurations_remain_uncertified(self):
        for size, count in ((3, 4), (4, 3)):
            rows = []
            for offset in reversed(range(0, 3 * count, 3)):
                patterns = ([0, 2, 1], [1, 0, 2], [0, 1, 2], [1, 1, 1])[:size]
                rows.extend([0] * offset + list(row) + [0] * (3 * count - offset - 3)
                            for row in patterns)
            with self.subTest(group_size=size, group_count=count):
                with self.assertRaisesRegex(ValueError, "componentwise ordered CDF chain"):
                    optimal_histogram_groups(rows, size)

    def test_cdf_order_suffices_despite_crossing_nested_reversal(self):
        result = optimal_histogram_groups(STRICT_STOCHASTIC_EXAMPLE, 2)
        probabilities = categorical_oracle(STRICT_STOCHASTIC_EXAMPLE, 2)
        sums = [_score(probabilities, groups) for groups in
                ([[0, 1], [2, 3]], [[0, 2], [1, 3]], [[0, 3], [1, 2]])]
        self.assertEqual(sums, [Fraction(value, 2025) for value in (1016, 503, 506)])
        self.assertEqual(_score(probabilities, result["groups"]), sums[0])
        self.assertEqual(result["objective"], "intact")
        self.assertEqual(optimal_histogram_groups(STOCHASTIC_ONLY_EXAMPLE, 2)["groups"],
                         [[0, 1], [2, 3]])

    def test_permutation_and_original_labels(self):
        permutation = [2, 0, 3, 1]
        rows = [WITHIN_PAIR_CROSSING[i] for i in permutation]
        groups = optimal_histogram_groups(rows, 2)["groups"]
        self.assertEqual(groups, [[1, 3], [0, 2]])
        original_groups = sorted(sorted(permutation[i] for i in group) for group in groups)
        self.assertEqual(original_groups, [[0, 1], [2, 3]])
        permutation = [4, 0, 5, 2, 1, 3]
        rows = [[i, 6 - i] for i in permutation]
        self.assertEqual(optimal_histogram_groups(rows, 3)["groups"], [[1, 4, 3], [5, 0, 2]])

    def test_exact_normalization_and_label_ties(self):
        result = optimal_histogram_groups([[1, 1], [2, 2], [3, 3], [4, 4]], 2)
        self.assertEqual(result["groups"], [[0, 1], [2, 3]])
        self.assertEqual(optimal_histogram_groups([[i, i] for i in range(1, 7)], 3)["groups"],
                         [[0, 1, 2], [3, 4, 5]])
        # Unequal row totals must be normalized before choosing the order.
        self.assertEqual(optimal_histogram_groups([[2, 1], [1, 2], [3, 3], [1, 4]], 2)["groups"],
                         [[3, 1], [2, 0]])

    def test_block_extrema_are_checked_before_certification(self):
        rows = [[0, 3, 0, 1], [1, 0, 1, 2], [2, 0, 1, 1], [3, 0, 0, 1]]
        # The lexicographically adjacent labels at the cut, 1 and 2, are
        # pointwise ordered. Label 0 still crosses label 2 at endpoint 2.
        self.assertTrue(all(sum(rows[1][:end]) <= sum(rows[2][:end])
                            for end in range(5)))
        with self.assertRaisesRegex(ValueError, "cut 1 at bin endpoint 2"):
            optimal_histogram_groups(rows, 2)
        triples = [rows[0], rows[1], rows[1], rows[2], rows[3], rows[3]]
        with self.assertRaisesRegex(ValueError, "cut 1 at bin endpoint 2"):
            optimal_histogram_groups(triples, 3)

    def test_certificate_scope_and_source_copy(self):
        rows = [row.copy() for row in WITHIN_PAIR_CROSSING]
        result = optimal_histogram_groups(rows, 2)
        self.assertEqual(result["contract"], "algal.lab.stochastic-grouping.v1")
        self.assertEqual(result["status"], "structurally-optimal")
        self.assertEqual(result["optimality"],
                         "usual stochastic order of intact-group count at each fixed horizon")
        self.assertEqual(result["probabilityEvaluations"], 0)
        self.assertEqual(result["histograms"], rows)
        self.assertEqual(result["groupSize"], 2)
        self.assertEqual(result["certificate"]["endpointCount"], 5)
        self.assertEqual(result["certificate"]["cutCount"], 1)
        self.assertIn("every fixed survivor count", result["horizons"])
        self.assertIn("background scores are not assigned", result["scope"])
        self.assertTrue(any("jointly independent" in value for value in result["assumptions"]))
        rows[0][0] = 99
        rows.append([1, 1, 1, 1])
        self.assertEqual(result["histograms"], WITHIN_PAIR_CROSSING)

    def test_single_groups_and_odd_clock_counts(self):
        result = optimal_histogram_groups([[0, 2, 0, 4], [1, 0, 2, 3]], 2)
        self.assertEqual(result["groups"], [[0, 1]])
        self.assertEqual(result["certificate"]["cutCount"], 0)
        self.assertEqual(optimal_histogram_groups([[1], [MAX_COUNT]], 2)["groups"], [[0, 1]])
        result = optimal_histogram_groups([[1, 0], [0, 1], [1, 1]], 3)
        self.assertEqual(result["groups"], [[1, 2, 0]])
        self.assertEqual(result["certificate"]["cutCount"], 0)
        result = optimal_histogram_groups([[i, 9 - i] for i in range(9)], 3)
        self.assertEqual(result["groups"], [[0, 1, 2], [3, 4, 5], [6, 7, 8]])
        self.assertEqual(result["certificate"]["criterion"], "separated CDF blocks of equal size")
        self.assertEqual(result["certificate"]["withinGroupCdfOrder"], "unrestricted")
        result = optimal_histogram_groups([[i, 12 - i] for i in range(12)], 3)
        self.assertEqual(result["certificate"]["criterion"], "componentwise ordered CDF chain")
        self.assertEqual(result["certificate"]["withinGroupCdfOrder"], "componentwise ordered")

    def test_full_structural_bounds_without_probability_oracle(self):
        rows = [[MAX_COUNT] * MAX_BINS for _ in range(MAX_CLOCKS)]
        for size in (2, 16, MAX_CLOCKS):
            result = optimal_histogram_groups(rows, size)
            self.assertEqual(result["groups"],
                             [list(range(i, i + size)) for i in range(0, MAX_CLOCKS, size)])
            self.assertEqual(result["certificate"]["clockCount"], MAX_CLOCKS)
            self.assertEqual(result["certificate"]["binCount"], MAX_BINS)
            self.assertEqual(result["probabilityEvaluations"], 0)
            self.assertLess(len(json.dumps(result, separators=(",", ":")).encode()), MAX_INPUT_BYTES)

    def test_strict_histogram_and_group_size_admission(self):
        invalid = [
            None, {}, (), [], [[1]], [[1]] * (MAX_CLOCKS + 1),
            [[], []], [[1] * (MAX_BINS + 1)] * 2,
            [[1], [1, 1]], [[1], None], [[1], (1,)], [[0], [1]],
            [[-1], [1]], [[MAX_COUNT + 1], [1]], [[10 ** 1000], [1]],
            [[True], [1]], [[1.0], [1]], [[float("nan")], [1]],
            [[float("inf")], [1]], [["1"], [1]], [[None], [1]],
        ]
        for rows in invalid:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                optimal_histogram_groups(rows, 2)
        for size in (None, True, False, 0, 1, -1, 4, 7, 2.0, "3", float("nan")):
            with self.subTest(size=size), self.assertRaises(ValueError):
                optimal_histogram_groups([[1]] * 6, size)

    def test_cli_runs_and_emits_json(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "histograms.json"
            source.write_text(json.dumps({"histograms": WITHIN_PAIR_CROSSING, "groupSize": 2}),
                              encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "research.stochastic_groups", str(source)],
                cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=10,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), optimal_histogram_groups(WITHIN_PAIR_CROSSING, 2))

    def test_cli_rejects_unknown_duplicate_and_noninteger_values(self):
        invalid = [
            '{"histograms":[[1],[1]],"groupSize":2,"objective":"both"}',
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
            '{"histograms":[[1],[1]],"groupSize":1}',
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
