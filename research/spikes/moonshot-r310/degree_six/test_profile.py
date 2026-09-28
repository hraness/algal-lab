"""Independent truth tables and graph controls for the optional profile."""

import itertools
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from encoding import (Formula, anti_neighborhood_edge_bound, cardinality,
                      nondecreasing_signatures, private_neighbor_cap, structural_formula)
from native import Solver
from search import check_strengthening


LIBRARY = os.environ.get("CADICAL_LIBRARY")


def circulant(n, steps):
    return [sum(1 << ((v + step) % n) for step in steps) for v in range(n)]


def relabel_centre(adj):
    order = [0] + [v for v in range(1, len(adj)) if adj[0] >> v & 1]
    order += [v for v in range(1, len(adj)) if not adj[0] >> v & 1]
    return [sum(1 << w for w, old_w in enumerate(order) if adj[old_v] >> old_w & 1)
            for old_v in order]


def truth_satisfies(formula, assignment):
    return all(any(assignment[abs(literal)] == (literal > 0) for literal in clause)
               for clause in formula.clauses)


def signature_assignment(signatures, values):
    return {literal: bool(value >> (len(row) - 1 - i) & 1)
            for row, value in zip(signatures, values) for i, literal in enumerate(row)}


class PureProfileControls(unittest.TestCase):
    def test_all_six_bit_signature_pairs(self):
        signatures = [list(range(1, 7)), list(range(7, 13))]
        formula = Formula(12)
        nondecreasing_signatures(formula, signatures)
        self.assertEqual((formula.variables, len(formula.clauses)), (12, 63))
        for left, right in itertools.product(range(64), repeat=2):
            self.assertEqual(truth_satisfies(formula, signature_assignment(signatures, (left, right))),
                             left <= right)

    def test_private_cap_all_short_signature_sequences(self):
        checked = 0
        for rows in range(6):
            signatures = [[2 * v + 1, 2 * v + 2] for v in range(rows)]
            for cap in (0, 1, 4):
                formula = Formula(2 * rows)
                nondecreasing_signatures(formula, signatures)
                private_neighbor_cap(formula, signatures, cap)
                for values in itertools.product(range(4), repeat=rows):
                    expected = (list(values) == sorted(values)
                                and values.count(1) <= cap and values.count(2) <= cap)
                    self.assertEqual(truth_satisfies(formula, signature_assignment(signatures, values)),
                                     expected, (values, cap))
                    checked += 1
        self.assertEqual(checked, 4095)

    def test_profile_size_and_restricted_parameters(self):
        baseline, edges, metadata = structural_formula()
        self.assertEqual((len(edges), baseline.variables, len(baseline.clauses)), (780, 14580, 63272))
        self.assertNotIn("strengthening", metadata)
        enhanced, _, receipt = structural_formula(profile="degree-six-structure-v1")
        self.assertEqual((enhanced.variables, len(enhanced.clauses)), (17933, 78702))
        self.assertEqual(receipt["clause_counts"]["anti_neighborhood_edge_bound"], 12844)
        self.assertEqual(receipt["clause_counts"]["anti_neighborhood_signature_order"], 2016)
        self.assertEqual(receipt["clause_counts"]["private_neighbor_cap"], 174)
        self.assertEqual(receipt["clause_counts"]["neighborhood_cross_edge_bound"], 396)
        self.assertEqual(enhanced.clauses[:len(baseline.clauses)], baseline.clauses)
        for parameters in ({"profile": "unknown"}, {"profile": "degree-six-structure-v1", "order": 39},
                           {"profile": "degree-six-structure-v1", "coverage": False}):
            with self.assertRaises(ValueError):
                structural_formula(**parameters)

    def test_recounted_profile_checks_and_failures(self):
        graph = relabel_centre(circulant(5, (1, 4)))
        # Reorder the outside vertices by their two-bit signatures.
        order = [0, 1, 2] + sorted((3, 4), key=lambda v: tuple(bool(graph[v] >> a & 1) for a in (1, 2)))
        graph = [sum(1 << w for w, old_w in enumerate(order) if graph[old_v] >> old_w & 1)
                 for old_v in order]
        bounds = {"anti_neighborhood_minimum_edges": 1, "neighborhood_cross_minimum_edges": 2,
                  "private_neighbor_maximum": 1, "implied_global_minimum_edges": 5}
        check_strengthening(graph, 2, bounds)
        for key, value, message in (("anti_neighborhood_minimum_edges", 2, "anti-neighborhood"),
                                    ("neighborhood_cross_minimum_edges", 3, "cross-edge"),
                                    ("private_neighbor_maximum", 0, "private-neighbor"),
                                    ("implied_global_minimum_edges", 6, "global")):
            with self.assertRaisesRegex(ValueError, message):
                check_strengthening(graph, 2, {**bounds, key: value})
        order = [0, 1, 2, 4, 3]
        unsorted = [sum(1 << w for w, old_w in enumerate(order) if graph[old_v] >> old_w & 1)
                    for old_v in order]
        with self.assertRaisesRegex(ValueError, "signature order"):
            check_strengthening(unsorted, 2, bounds)


@unittest.skipUnless(LIBRARY, "set CADICAL_LIBRARY for native controls")
class NativeProfileControls(unittest.TestCase):
    def test_every_polarity_assignment_and_interval_through_four_inputs(self):
        checked = 0
        for count in range(5):
            for polarity in range(1 << count):
                inputs = [-(v + 1) if polarity >> v & 1 else v + 1 for v in range(count)]
                for lower in range(count + 1):
                    for upper in range(lower, count + 1):
                        formula = Formula(max(1, count))
                        cardinality(formula, inputs, lower, upper)
                        for values in range(1 << count):
                            with Solver(LIBRARY, formula.variables) as solver:
                                for clause in formula.clauses:
                                    solver.add(clause)
                                for v in range(count):
                                    solver.add((v + 1 if values >> v & 1 else -(v + 1),))
                                self.assertEqual(solver.solve() == 10,
                                                 lower <= (values ^ polarity).bit_count() <= upper)
                            checked += 1
        self.assertEqual(checked, 4589)

    def test_returned_thresholds_are_exact_for_signed_inputs(self):
        for polarity in (0, 0b101010, 0b111111):
            inputs = [-(v + 1) if polarity >> v & 1 else v + 1 for v in range(6)]
            formula = Formula(6)
            thresholds = cardinality(formula, inputs, 0, 6)
            for values in range(64):
                with Solver(LIBRARY, formula.variables) as solver:
                    for clause in formula.clauses:
                        solver.add(clause)
                    for v in range(6):
                        solver.add((v + 1 if values >> v & 1 else -(v + 1),))
                    self.assertEqual(solver.solve(), 10)
                    for threshold in range(1, 7):
                        self.assertEqual(solver.value(thresholds[threshold]),
                                         (values ^ polarity).bit_count() >= threshold)

    def test_anti_neighborhood_bound_against_every_five_vertex_graph(self):
        pairs = list(itertools.combinations(range(5), 2))
        checked = 0
        for lower in (0, 1, 2):
            formula, variables, _ = structural_formula(5, 3, 0, 2, coverage=False)
            thresholds = {v: cardinality(formula, [variables[tuple(sorted((v, w)))]
                                                  for w in range(5) if v != w], 0, 2)
                          for v in range(1, 5)}
            anti_neighborhood_edge_bound(formula, thresholds, 5, 2, 0, 2, lower)
            for bits in range(1 << len(pairs)):
                edges = {pair for i, pair in enumerate(pairs) if bits >> i & 1}
                neighbors = [{w for u, w in edges if u == v} | {u for u, w in edges if w == v}
                             for v in range(5)]
                expected = (neighbors[0] == {1, 2} and all(len(row) <= 2 for row in neighbors)
                            and all(not {(a, b), (a, c), (b, c)} <= edges
                                    for a, b, c in itertools.combinations(range(5), 3))
                            and int((3, 4) in edges) >= lower)
                with Solver(LIBRARY, formula.variables) as solver:
                    for clause in formula.clauses:
                        solver.add(clause)
                    for pair, literal in variables.items():
                        solver.add((literal if pair in edges else -literal,))
                    self.assertEqual(solver.solve() == 10, expected, (lower, edges))
                checked += 1
        self.assertEqual(checked, 3072)

    def test_known_graphs_keep_a_sorted_representative(self):
        examples = [(5, 3, (1, 4)), (8, 4, (1, 4, 7)), (13, 5, (1, 5, 8, 12)),
                    (35, 9, (8, 12, 14, 17, 18, 21, 23, 27))]
        for n, target, steps in examples:
            degree = len(steps)
            graph = relabel_centre(circulant(n, steps))
            order = list(range(degree + 1)) + sorted(range(degree + 1, n),
                key=lambda v: tuple(bool(graph[v] >> a & 1) for a in range(1, degree + 1)))
            graph = [sum(1 << w for w, old_w in enumerate(order) if graph[old_v] >> old_w & 1)
                     for old_v in order]
            formula, variables, _ = structural_formula(n, target, degree, degree)
            signatures = [[variables[a, v] for a in range(1, degree + 1)]
                          for v in range(degree + 1, n)]
            nondecreasing_signatures(formula, signatures)
            private_neighbor_cap(formula, signatures, target - degree)
            with Solver(LIBRARY, formula.variables) as solver:
                for clause in formula.clauses:
                    solver.add(clause)
                for (u, v), literal in variables.items():
                    solver.add((literal if graph[u] >> v & 1 else -literal,))
                self.assertEqual(solver.solve(), 10, n)

    def test_copied_source_supervises_and_rebuilds_selected_profile(self):
        source = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(prefix="r310-profile-copy-") as directory:
            root = Path(directory)
            driver_dir = root / "degree_six"
            driver_dir.mkdir()
            for path in source.glob("*.py"):
                shutil.copy2(path, driver_dir / path.name)
            checker_dir = root / "vertex_transitive"
            checker_dir.mkdir()
            shutil.copy2(source.parent / "vertex_transitive/checker.py", checker_dir / "checker.py")
            output = root / "output"
            execution = subprocess.run(
                [sys.executable, str(driver_dir / "run.py"), "--library", str(Path(LIBRARY).resolve()),
                 "--output", str(output), "--seconds", "1", "--models", "1", "--cuts", "1",
                 "--batch", "1", "--profile", "degree-six-structure-v1"],
                capture_output=True, text=True, timeout=15, cwd=root)
            self.assertEqual(execution.returncode, 0, execution.stderr)
            result = json.loads(execution.stdout)
            self.assertFalse(result["unsat_verified"])
            self.assertFalse(result["graph_checked_without_independent_target_set"])
            metadata = json.loads((output / "instance.json").read_text())
            self.assertEqual(metadata["strengthening"]["profile"], "degree-six-structure-v1")
            self.assertEqual((metadata["variables"], metadata["clauses"]), (17933, 78702))
            lines = (output / "final.cnf").read_text().splitlines()
            formula, _, _ = structural_formula(profile="degree-six-structure-v1")
            self.assertEqual(lines[0], f"p cnf 17933 {78702 + result['recorded_cuts']}")
            self.assertEqual(lines[1:1 + 78702],
                             [" ".join(map(str, clause)) + " 0" for clause in formula.clauses])
            with self.assertRaises(ProcessLookupError):
                os.kill(result["worker_pid"], 0)


if __name__ == "__main__":
    unittest.main()
