"""Focused controls. Set CADICAL_LIBRARY to the approved local shared library."""

import itertools
import os
from pathlib import Path
import time
import unittest

from encoding import Formula, cardinality, independent_clause, structural_formula
from native import Solver
from search import additional_independent_sets, independent_set, search, validate_structure


LIBRARY = os.environ.get("CADICAL_LIBRARY")


def circulant(n, steps):
    return [sum(1 << ((v + step) % n) for step in steps) for v in range(n)]


def relabel_centre(adj):
    order = [0] + [v for v in range(1, len(adj)) if adj[0] >> v & 1]
    order += [v for v in range(1, len(adj)) if not adj[0] >> v & 1]
    return [sum(1 << w for w, old_w in enumerate(order) if adj[old_v] >> old_w & 1)
            for old_v in order]


@unittest.skipUnless(LIBRARY, "set CADICAL_LIBRARY for native controls")
class NativeControls(unittest.TestCase):
    def test_structural_formula_against_every_five_vertex_graph(self):
        n = 5
        pairs = list(itertools.combinations(range(n), 2))
        for coverage in (False, True):
            formula, variable, _ = structural_formula(n, 3, 1, 2, coverage=coverage)
            for bits in range(1 << len(pairs)):
                edge_set = {pair for i, pair in enumerate(pairs) if bits >> i & 1}
                neighbors = [{w for u, w in edge_set if u == v} | {u for u, w in edge_set if w == v}
                             for v in range(n)]
                expected = (neighbors[0] == {1, 2}
                            and all(1 <= len(row) <= 2 for row in neighbors)
                            and all(not ({(a, b), (a, c), (b, c)} <= edge_set)
                                    for a, b, c in itertools.combinations(range(n), 3))
                            and (not coverage or all(neighbors[v] & {1, 2} for v in (3, 4))))
                with Solver(Path(LIBRARY), formula.variables) as solver:
                    for clause in formula.clauses:
                        solver.add(clause)
                    for pair, literal in variable.items():
                        solver.add((literal if pair in edge_set else -literal,))
                    self.assertEqual(solver.solve() == 10, expected)

    def test_cardinality_every_assignment_through_six_inputs(self):
        checked = 0
        for count in range(7):
            for lower in range(count + 1):
                for upper in range(lower, count + 1):
                    formula = Formula(max(1, count))
                    cardinality(formula, list(range(1, count + 1)), lower, upper)
                    for bits in range(1 << count):
                        with Solver(Path(LIBRARY), formula.variables) as solver:
                            for clause in formula.clauses:
                                solver.add(clause)
                            for v in range(count):
                                solver.add((v + 1 if bits >> v & 1 else -(v + 1),))
                            self.assertEqual(solver.solve() == 10, lower <= bits.bit_count() <= upper)
                            checked += 1
        self.assertEqual(checked, 2815)

    def test_known_graphs_satisfy_full_driver(self):
        examples = [(5, 3, (1, 4)), (8, 4, (1, 4, 7)),
                    (13, 5, (1, 5, 8, 12)), (35, 9, (8, 12, 14, 17, 18, 21, 23, 27))]
        for n, target, steps in examples:
            adj = relabel_centre(circulant(n, steps))
            formula, variable, metadata = structural_formula(n, target, len(steps), len(steps))
            deadline = time.monotonic() + 5
            result = search(formula, variable, metadata, LIBRARY,
                            stop=lambda: time.monotonic() > deadline, fixed_graph=adj)
            self.assertEqual(result["status"], "candidate_found", (n, result))
            self.assertEqual(result["last_graph"], adj)
            self.assertIsNone(independent_set(adj, target))

    def test_recovers_unfixed_five_cycle(self):
        formula, variable, metadata = structural_formula(5, 3, 2, 2)
        result = search(formula, variable, metadata, LIBRARY, stop=lambda: False)
        self.assertEqual(result["status"], "candidate_found")
        self.assertEqual(sum(row.bit_count() for row in result["last_graph"]), 10)

    def test_recovers_unfixed_eight_and_thirteen_vertex_examples(self):
        for n, target, degree in ((8, 4, 3), (13, 5, 4)):
            formula, variable, metadata = structural_formula(n, target, degree, degree)
            deadline = time.monotonic() + 5
            result = search(formula, variable, metadata, LIBRARY,
                            stop=lambda: time.monotonic() > deadline)
            self.assertEqual(result["status"], "candidate_found", (n, result["status"]))
            self.assertIsNone(independent_set(result["last_graph"], target))

    def test_six_cycle_requires_lazy_cut_and_is_not_a_witness(self):
        graph = relabel_centre(circulant(6, (1, 5)))
        formula, variable, metadata = structural_formula(6, 3, 2, 2, coverage=False)
        result = search(formula, variable, metadata, LIBRARY,
                        stop=lambda: False, fixed_graph=graph)
        self.assertEqual(result["status"], "unverified_unsat")
        self.assertFalse(result["unsat_verified"])
        self.assertEqual(result["models"], 1)
        self.assertEqual(len(result["cuts"]), 2)

    def test_resource_stop_cannot_be_negative_result(self):
        formula, variable, metadata = structural_formula(5, 3, 2, 2)
        result = search(formula, variable, metadata, LIBRARY, stop=lambda: True)
        self.assertEqual(result["status"], "resource_limit")
        self.assertFalse(result["unsat_verified"])

    def test_partial_formula_model_limit_is_not_a_witness(self):
        graph = relabel_centre(circulant(6, (1, 5)))
        formula, variable, metadata = structural_formula(6, 3, 2, 2, coverage=False)
        result = search(formula, variable, metadata, LIBRARY, stop=lambda: False,
                        model_limit=1, fixed_graph=graph)
        self.assertEqual(result["status"], "model_limit")
        self.assertFalse(result["graph_checked_without_independent_target_set"])


class PureControls(unittest.TestCase):
    def test_batched_sets_against_all_small_graphs(self):
        n, target = 5, 3
        edges = list(itertools.combinations(range(n), 2))
        for graph_bits in range(1 << len(edges)):
            adj = [0] * n
            for i, (u, v) in enumerate(edges):
                if graph_bits >> i & 1:
                    adj[u] |= 1 << v
                    adj[v] |= 1 << u
            expected = {sum(1 << v for v in subset) for subset in itertools.combinations(range(n), target)
                        if all(not adj[u] >> v & 1 for u, v in itertools.combinations(subset, 2))}
            if expected:
                actual = additional_independent_sets(adj, target, min(expected), 256, lambda: False)
                self.assertEqual(set(actual), expected)
                self.assertEqual(len(actual), len(expected))

    def test_cut_has_every_pair_and_no_other_literal(self):
        _, variable, _ = structural_formula(5, 3, 2, 2)
        self.assertEqual(independent_clause(0b10101, variable, 3),
                         (variable[0, 2], variable[0, 4], variable[2, 4]))
        with self.assertRaises(ValueError):
            independent_clause(0b10001, variable, 3)

    def test_structure_checker_rejects_changed_graph(self):
        _, _, metadata = structural_formula(5, 3, 2, 2)
        graph = relabel_centre(circulant(5, (1, 4)))
        validate_structure(graph, metadata)
        graph[3] ^= 1 << 4
        graph[4] ^= 1 << 3
        with self.assertRaises(ValueError):
            validate_structure(graph, metadata)


if __name__ == "__main__":
    unittest.main()
