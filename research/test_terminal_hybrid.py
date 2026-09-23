"""Independent finite references for the frontier-prefix hybrid algorithm."""

from fractions import Fraction
from itertools import combinations, permutations, product
from random import Random
import unittest
from unittest.mock import patch

from research.terminal_hybrid import (
    _choice_groups, _group_regret_bound, optimize_hybrid_counts, sample_hybrid_tree,
)
from research.terminal_sampling import (
    DYADIC_DENOMINATOR, _KLDyadicIntervals, _draw_pair_counts,
)


def permutation_pairs(weights):
    probabilities = {edge: Fraction(0) for edge in combinations(range(len(weights)), 2)}
    for order in permutations(range(len(weights))):
        remaining, chance = sum(weights), Fraction(1)
        for node in order:
            chance *= Fraction(weights[node], remaining)
            remaining -= weights[node]
        probabilities[tuple(sorted(order[-2:]))] += chance
    return probabilities


def all_trees(nodes):
    for code in product(range(nodes), repeat=nodes - 2):
        degree = [1] * nodes
        for node in code:
            degree[node] += 1
        edges = []
        for node in code:
            leaf = next(i for i in range(nodes) if degree[i] == 1)
            edges.append(tuple(sorted((leaf, node))))
            degree[leaf] -= 1
            degree[node] -= 1
        edges.append(tuple(i for i in range(nodes) if degree[i] == 1))
        yield edges


def family_trees(groups):
    for parents in product(*(choices for _, choices in groups)):
        yield [tuple(sorted((node, parent))) for (node, _), parent in zip(groups, parents)]


def benefit(tree, values, probabilities):
    return sum(probabilities[edge] * min(values[i] for i in edge) for edge in tree)


def connected_tree(nodes, tree):
    if len(tree) != nodes - 1 or len(set(tree)) != nodes - 1:
        return False
    seen = {0}
    while True:
        previous = len(seen)
        for i, j in tree:
            if i in seen or j in seen:
                seen.update((i, j))
        if len(seen) == previous:
            return len(seen) == nodes


class TerminalHybridTests(unittest.TestCase):
    def test_complete_four_vertex_grid_preserves_a_global_optimum(self):
        trees = list(all_trees(4))
        self.assertEqual(len(trees), 16)
        environments = comparisons = 0
        for weights in product((1, 2, 3), repeat=4):
            probabilities = permutation_pairs(weights)
            self.assertEqual(sum(probabilities.values()), 1)
            for values in product((1, 2, 3), repeat=4):
                _, groups = _choice_groups({"weights": list(weights), "values": list(values)})
                family = list(family_trees(groups))
                self.assertTrue(all(connected_tree(4, tree) for tree in family))
                family_best = max(benefit(tree, values, probabilities) for tree in family)
                global_best = max(benefit(tree, values, probabilities) for tree in trees)
                self.assertEqual(family_best, global_best)
                environments += 1
                comparisons += len(trees)
        self.assertEqual(environments, 6561)
        self.assertEqual(comparisons, 104976)

    def test_separable_box_bound_matches_exhaustive_family_comparisons(self):
        random = Random(9302304)
        denominator = DYADIC_DENOMINATOR
        compared = 0
        for nodes in (4, 5, 6):
            for _ in range(8):
                env = {"weights": [random.randint(1, 7) for _ in range(nodes)],
                       "values": [random.randint(1, 9) for _ in range(nodes)]}
                values = env["values"]
                probabilities = permutation_pairs(env["weights"])
                _, groups = _choice_groups(env)
                family = list(family_trees(groups))
                relevant = {tuple(sorted((node, parent))) for node, parents in groups
                            if len(parents) > 1 for parent in parents}
                intervals = {}
                for edge in relevant:
                    q = probabilities[edge] * denominator
                    padding = random.randint(0, denominator // 7)
                    intervals[edge] = (max(0, q.numerator // q.denominator - padding),
                                       min(denominator, (q.numerator + q.denominator - 1) // q.denominator + padding))
                truth = max(benefit(tree, values, probabilities) for tree in family)
                for candidate in (family[0], family[len(family) // 2], family[-1]):
                    chosen = set(candidate)
                    box_gaps = []
                    for tree in family:
                        other = set(tree)
                        box_gaps.append(sum(min(values[i] for i in edge) * intervals[edge][1] for edge in other - chosen)
                                        - sum(min(values[i] for i in edge) * intervals[edge][0] for edge in chosen - other))
                    reference = min(Fraction(max(box_gaps), denominator * sum(values)),
                                    Fraction(sorted(values)[-2], sum(values)))
                    bound = _group_regret_bound(values, groups, candidate, intervals)
                    self.assertEqual(bound, reference)
                    self.assertGreaterEqual(bound, (truth - benefit(candidate, values, probabilities)) / sum(values))
                    compared += 1
        self.assertEqual(compared, 72)

    def test_histogram_certificate_uses_only_uncertain_edges(self):
        env = {"weights": [2, 2, 1, 1], "values": [3, 3, 1, 1]}
        counts = [0, 1, 1, 5, 0, 3]
        result = optimize_hybrid_counts(env, counts)
        self.assertEqual(result["status"], "confidence-bounded-tree")
        self.assertEqual(result["graph"]["edges"], [[0, 2], [1, 2], [2, 3]])
        self.assertEqual(result["structure"]["uncertainGroups"], 1)
        self.assertEqual(result["structure"]["forcedGroups"], 2)
        self.assertEqual(result["structure"]["relevantPairs"], 2)
        self.assertEqual(result["operations"]["certificateRelevantPairs"], 2)
        intervals = _KLDyadicIntervals(sum(counts), 2, Fraction(1, 20))
        lower = intervals.bounds(5)[0]
        upper = intervals.bounds(0)[1]
        reference = min(Fraction(max(0, 3 * upper - lower), 8 * DYADIC_DENOMINATOR), Fraction(3, 8))
        bound = Fraction(result["confidenceRegretBoundExact"])
        self.assertEqual(bound, reference)
        self.assertGreaterEqual(Fraction.from_float(result["confidenceRegretBound"]), bound)
        probabilities = permutation_pairs(env["weights"])
        self.assertLess(probabilities[(0, 1)] + probabilities[(1, 2)], 1)
        chosen = list(map(tuple, result["graph"]["edges"]))
        best = max(benefit(tree, env["values"], probabilities) for tree in all_trees(4))
        self.assertEqual((best - benefit(chosen, env["values"], probabilities)) / 8, Fraction(1, 160))
        self.assertGreaterEqual(bound, Fraction(1, 160))

    def test_prefix_keeps_nondominators_and_forced_cases_skip_all_randomness(self):
        other = {"weights": [1, 2, 3, 4], "values": [1, 3, 2, 1]}
        frontier, groups = _choice_groups(other)
        self.assertEqual(frontier, [0, 1])
        self.assertEqual(dict(groups)[2], [0, 1])
        self.assertEqual(dict(groups)[3], [0])

        def forbidden(_):
            self.fail("a deterministic case called the random generator")

        cases = [
            {"weights": [1, 2, 3, 4], "values": [9, 8, 7, 6]},
            {"weights": [1, 2, 3, 4], "values": [3, 5, 1, 2]},
            {"weights": [3, 3, 3, 3], "values": [5, 5, 5, 5]},
            {"weights": [2, 1], "values": [1, 2]},
        ]
        for env in cases:
            with patch("research.terminal_hybrid._KLDyadicIntervals", side_effect=AssertionError("forced case requested intervals")):
                result = sample_hybrid_tree(env, 4096, randbelow=forbidden)
            self.assertEqual(result["status"], "structurally-exact-tree")
            self.assertEqual(result["confidenceRegretBoundExact"], "0")
            self.assertEqual(result["input"]["requestedSamples"], 4096)
            self.assertEqual(result["input"]["samples"], 0)
            self.assertEqual(sum(result["pairCounts"]), 0)
            self.assertIsNone(result["empiricalConnectionBenefitExact"])
            for name in ("integerDraws", "trajectories", "histogramUpdates", "klBoundaryQueries"):
                self.assertEqual(result["operations"][name], 0)
            reference = optimize_hybrid_counts(env, result["pairCounts"])
            self.assertEqual(reference["graph"], result["graph"])
            probabilities = permutation_pairs(env["weights"])
            chosen = list(map(tuple, result["graph"]["edges"]))
            self.assertEqual(benefit(chosen, env["values"], probabilities),
                             max(benefit(tree, env["values"], probabilities) for tree in all_trees(len(env["weights"]))))

    def test_sampling_reuses_the_integer_draw_law_and_replays(self):
        env = {"weights": [2, 2, 1, 1], "values": [3, 3, 1, 1]}
        random = Random(9302305)
        result = sample_hybrid_tree(env, 128, randbelow=random.randrange)
        expected_counts, operations = _draw_pair_counts(env["weights"], 128, Random(9302305).randrange)
        self.assertEqual(result["pairCounts"], expected_counts)
        for key, value in operations.items():
            self.assertEqual(result["operations"][key], value)
        self.assertEqual(result["operations"]["integerDraws"], 256)
        self.assertEqual(result["input"]["samples"], 128)
        replay = optimize_hybrid_counts(env, expected_counts)
        for field in ("graph", "status", "confidenceRegretBoundExact", "structure"):
            self.assertEqual(result[field], replay[field])
        with patch("research.terminal_hybrid.secrets.randbelow", side_effect=Random(9302305).randrange):
            default = sample_hybrid_tree(env, 128)
        self.assertEqual(default["pairCounts"], expected_counts)
        self.assertEqual(default["confidence"]["source"], "secrets.randbelow")
        self.assertEqual(result["confidence"]["source"], "caller-supplied randbelow")

    def test_strict_histogram_budget_environment_and_callback_admission(self):
        env = {"weights": [2, 2, 1, 1], "values": [3, 3, 1, 1]}
        valid = [1, 1, 1, 1, 1, 1]
        for counts in (None, (), tuple(valid), [], valid + [1], [True] + valid[1:],
                       [1.0] + valid[1:], [-1] + valid[1:], [32769] + valid[1:],
                       [0] * 6, [32768, 1, 0, 0, 0, 0]):
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                optimize_hybrid_counts(env, counts)
        for samples in (0, True, 1.5, 32769):
            with self.subTest(samples=samples), self.assertRaises(ValueError):
                sample_hybrid_tree(env, samples)
        for delta in (True, 0, 1e-7, .5, float("nan"), float("inf")):
            with self.subTest(delta=delta), self.assertRaises(ValueError):
                optimize_hybrid_counts(env, valid, delta)
        for invalid in (None, [], {}, {**env, "extra": 1}, {"weights": [1, True], "values": [1, 2]}):
            with self.subTest(environment=invalid), self.assertRaises(ValueError):
                sample_hybrid_tree(invalid, 1)
        for callback in (7, lambda n: True, lambda n: n, lambda n: -1, lambda n: .5):
            with self.subTest(callback=callback), self.assertRaises(ValueError):
                sample_hybrid_tree(env, 1, randbelow=callback)
        forced = {"weights": [1, 1], "values": [1, 1]}
        with self.assertRaises(ValueError):
            sample_hybrid_tree(forced, 0)
        with self.assertRaises(ValueError):
            optimize_hybrid_counts(forced, [0], delta=True)


if __name__ == "__main__":
    unittest.main()
