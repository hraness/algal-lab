"""Independent exact references for the separate two-survivor endpoint."""
from fractions import Fraction
from itertools import combinations, permutations, product
import json
from math import comb
from pathlib import Path
from random import Random
import subprocess
import sys
import tempfile
import unittest

from research.terminal_tree import (MAX_INPUT_BYTES, PairProbabilities, admit_environment,
                                    admit_tree, maximum_spanning_tree, optimize, read_input)


def permutation_pairs(weights):
    """Independent complete sequential-removal orders, exact probabilities."""
    result = {pair: Fraction(0) for pair in combinations(range(len(weights)), 2)}
    for order in permutations(range(len(weights))):
        remaining = sum(weights)
        chance = Fraction(1)
        for node in order:
            chance *= Fraction(weights[node], remaining)
            remaining -= weights[node]
        result[tuple(sorted(order[-2:]))] += chance
    if sum(result.values()) != 1:
        raise AssertionError("reference order probabilities do not normalize")
    return result


def trees(nodes):
    for sequence in product(range(nodes), repeat=nodes - 2):
        degrees = [1] * nodes
        for node in sequence:
            degrees[node] += 1
        edges = []
        for node in sequence:
            leaf = next(i for i in range(nodes) if degrees[i] == 1)
            edges.append(tuple(sorted((leaf, node))))
            degrees[leaf] -= 1
            degrees[node] -= 1
        edges.append(tuple(i for i in range(nodes) if degrees[i] == 1))
        yield edges


def direct_score(tree, values, probabilities):
    """Evaluate the two actual connected components, independently of solver."""
    present = set(tree)
    total = sum(values)
    return sum(chance * Fraction(values[i] + values[j] if (i, j) in present else max(values[i], values[j]), total)
               for (i, j), chance in probabilities.items())


def kruskal_reference(nodes, scores):
    """Component sets rather than production union-find or ordered frontier."""
    components = [{node} for node in range(nodes)]
    tree = []
    for edge in sorted(scores, key=lambda e: (-scores[e], e)):
        left = next(component for component in components if edge[0] in component)
        right = next(component for component in components if edge[1] in component)
        if left is not right:
            merged = left | right
            components.remove(left)
            components.remove(right)
            components.append(merged)
            tree.append(edge)
        if len(components) == 1:
            return tree
    raise AssertionError("reference complete graph failed to connect")


class TerminalTreeTests(unittest.TestCase):
    def test_polynomial_against_independent_weighted_permutations(self):
        random = Random(9302301)
        compared = 0
        for nodes in range(2, 7):
            panel = [[1] * nodes, [33] * nodes, list(range(1, nodes + 1)), [1 if i % 2 else 99 for i in range(nodes)]]
            panel += [[random.randint(1, 5) for _ in range(nodes)] for _ in range(8)]
            for weights in panel:
                reference = permutation_pairs(weights)
                probabilities = PairProbabilities(weights)
                for (i, j), expected in reference.items():
                    self.assertEqual(Fraction(probabilities.numerator(i, j), probabilities.denominator), expected)
                    self.assertEqual(probabilities.numerator(i, j), probabilities.numerator(j, i))
                    compared += 1
        self.assertEqual(compared, 420)

    def test_frontier_optimizer_on_complete_four_vertex_integer_grid(self):
        all_trees = list(trees(4))
        self.assertEqual(len({tuple(sorted(t)) for t in all_trees}), 16)
        compared_trees = 0
        for weights in product((1, 2, 3), repeat=4):
            probabilities = permutation_pairs(weights)
            for values in product((1, 2, 3), repeat=4):
                scores = {pair: chance * min(values[i] for i in pair) for pair, chance in probabilities.items()}
                expected = direct_score(kruskal_reference(4, scores), values, probabilities)
                candidate = all_trees[0]
                result = optimize({"weights": list(weights), "values": list(values)}, candidate)
                actual_edges = [tuple(edge) for edge in result["graph"]["edges"]]
                self.assertEqual(Fraction(result["expectedService"]), expected)
                self.assertEqual(direct_score(actual_edges, values, probabilities), expected)
                self.assertEqual(Fraction(result["candidate"]["exactRegret"]), expected - direct_score(candidate, values, probabilities))
                frontier = set(result["paretoFrontier"])
                for node in range(4):
                    if node not in frontier:
                        self.assertEqual(sum(node in edge for edge in actual_edges), 1)
                for tree in all_trees:
                    self.assertLessEqual(direct_score(tree, values, probabilities), expected)
                    compared_trees += 1
        self.assertEqual(compared_trees, 104976)

    def test_exhaustive_five_and_six_vertex_trees(self):
        random = Random(9302302)
        compared = 0
        for nodes in (5, 6):
            all_trees = list(trees(nodes))
            self.assertEqual(len(all_trees), nodes ** (nodes - 2))
            for _ in range(8):
                weights = [random.randint(1, 5) for _ in range(nodes)]
                values = [random.randint(1, 9) for _ in range(nodes)]
                probabilities = permutation_pairs(weights)
                result = optimize({"weights": weights, "values": values})
                expected = Fraction(result["expectedService"])
                for tree in all_trees:
                    self.assertLessEqual(direct_score(tree, values, probabilities), expected)
                    compared += 1
                self.assertEqual(direct_score([tuple(e) for e in result["graph"]["edges"]], values, probabilities), expected)
        self.assertEqual(compared, 11368)

    def test_nonstar_optimum_and_attachment_to_nondominator(self):
        env = {"weights": [2, 2, 1, 1], "values": [3, 3, 1, 1]}
        star = [(0, 2), (1, 2), (2, 3)]
        result = optimize(env, star)
        self.assertEqual(result["expectedService"], "181/480")
        self.assertEqual(result["candidate"]["expectedService"], "89/240")
        self.assertEqual(result["candidate"]["exactRegret"], "1/160")
        self.assertEqual(result["candidate"]["status"], "suboptimal-tree")
        for center in range(4):
            star = [tuple(sorted((center, i))) for i in range(4) if i != center]
            self.assertGreater(Fraction(optimize(env, star)["candidate"]["exactRegret"]), 0)
        other = optimize({"weights": [1, 2, 3, 4], "values": [1, 3, 2, 1]})
        self.assertEqual(other["paretoFrontier"], [0, 1])
        self.assertIn([0, 2], other["graph"]["edges"])

    def test_larger_cases_gcd_equivalence_ties_and_unique_rate_frontier(self):
        random = Random(9302303)
        for nodes in (24, 64, 128):
            weights = [random.randint(1, 5) for _ in range(nodes)]
            values = [random.randint(1, 99) for _ in range(nodes)]
            result = optimize({"weights": weights, "values": values})
            scaled = optimize({"weights": [w * 997 for w in weights], "values": values})
            self.assertEqual(result["graph"], scaled["graph"])
            self.assertEqual(result["expectedService"], scaled["expectedService"])
            probabilities = PairProbabilities(weights)
            scores = {(i, j): probabilities.numerator(i, j) * min(values[i], values[j]) for i, j in combinations(range(nodes), 2)}
            reference = kruskal_reference(nodes, scores)
            self.assertEqual(sum(scores[tuple(e)] for e in result["graph"]["edges"]), sum(scores[e] for e in reference))
        equal = PairProbabilities([1_000_000] * 128)
        self.assertEqual(Fraction(equal.numerator(0, 127), equal.denominator), Fraction(1, comb(128, 2)))
        self.assertEqual(equal.total_weight, 128)
        env = {"weights": [3, 3, 3, 3], "values": [5, 5, 5, 5]}
        self.assertEqual(optimize(env)["paretoFrontier"], [0])
        env = {"weights": [1, 2, 3, 4, 5, 6], "values": [1, 2, 3, 4, 5, 6]}
        self.assertEqual(optimize(env)["paretoFrontier"], list(range(6)))

    def test_strict_environment_probability_and_candidate_bounds(self):
        invalid = [None, [], {}, {"weights": [1, 2], "values": [1, 2], "extra": 1}]
        for weights, values in [([1], [1]), ([1] * 129, [1] * 129), ([1, 2], [1]), ((1, 2), [1, 2]),
                                ([True, 2], [1, 2]), ([1.0, 2], [1, 2]), ([0, 2], [1, 2]),
                                ([1_000_001, 2], [1, 2]), ([1, 2], [1, False]), ([1, 2], [1, 1_000_001])]:
            invalid.append({"weights": weights, "values": values})
        for env in invalid:
            with self.subTest(env=env), self.assertRaises(ValueError):
                admit_environment(env)
        for weights in (None, 7, "12", [8192, 1], list(range(1, 101))):
            with self.subTest(weights=weights), self.assertRaises(ValueError):
                PairProbabilities(weights)
        probabilities = PairProbabilities([1, 2, 3])
        for pair in ((0, 0), (-1, 1), (0, 3), (True, 1), (0.0, 1)):
            with self.subTest(pair=pair), self.assertRaises(ValueError):
                probabilities.numerator(*pair)
        for edges in (None, [], [[0, 1], [1, 0], [2, 3]], [[0, 1], [1, 2], [2, 0]],
                      [[0, 0], [0, 2], [0, 3]], [[0, 1], [0, 2], [0, 4]], [[0, 1], [0, 2], [False, 3]]):
            with self.subTest(edges=edges), self.assertRaises(ValueError):
                admit_tree(edges, 4)
        for scores in ({}, {(0, 1): float("nan")}, {(0, 1): float("inf")}, {(0, 1): True}, {(1, 0): 1}):
            with self.subTest(scores=scores), self.assertRaises(ValueError):
                maximum_spanning_tree(2, scores)
        self.assertEqual(maximum_spanning_tree(3, {(0, 1): -1, (0, 2): -2, (1, 2): -3}), [(0, 1), (0, 2)])

    def test_cli_and_bounded_json_admission(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "terminal.json"
            data = {"environment": {"weights": [2, 2, 1, 1], "values": [3, 3, 1, 1]}, "candidate": [[0, 2], [1, 2], [2, 3]]}
            path.write_text(json.dumps(data))
            result = subprocess.run([sys.executable, "-B", "-m", "research.terminal_tree", str(path)], capture_output=True, text=True, check=True)
            self.assertEqual(result.stderr, "")
            self.assertEqual(json.loads(result.stdout)["candidate"]["exactRegret"], "1/160")
            for raw in (b" " * (MAX_INPUT_BYTES + 1), b'{"environment":{},"environment":{}}', b'{"environment":NaN}',
                        b'[]', b'\xff', b'[' * 2000 + b']' * 2000, json.dumps({**data, "extra": 1}).encode()):
                path.write_bytes(raw)
                with self.subTest(raw=raw[:30]), self.assertRaises((ValueError, UnicodeError)):
                    read_input(path)


if __name__ == "__main__":
    unittest.main()
