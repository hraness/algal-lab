"""Independent graph enumeration, catalogue maps, and proof/model controls."""

import ctypes
import itertools
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from catalogue import base_graph, induced, is_isomorphism, pair_catalogue, ramsey_catalogue
from encode import encode, independent_sets, write_instance
from proof import verify
from run import parse_model, run_attempt
from shared import SearchLimit, native

LIBRARY = os.environ.get("CADICAL_LIBRARY")
SOLVER = os.environ.get("CADICAL_BINARY")


def graph_from_edges(n, edges):
    graph = [0] * n
    for u, v in edges:
        graph[u] |= 1 << v
        graph[v] |= 1 << u
    return graph


def has_independent(adj, size):
    return any(all(not (adj[u] >> v & 1) for u, v in itertools.combinations(vertices, 2))
               for vertices in itertools.combinations(range(len(adj)), size))


def has_triangle(adj):
    return any(all(adj[u] >> v & 1 for u, v in itertools.combinations(vertices, 2))
               for vertices in itertools.combinations(range(len(adj)), 3))


class CatalogueControls(unittest.TestCase):
    def test_complete_pair_cover_with_explicit_edge_and_nonedge_maps(self):
        catalogue = ramsey_catalogue()
        self.assertEqual(catalogue["labelled_pairs"], 595)
        self.assertEqual(len(catalogue["automorphisms"]), 210)
        self.assertEqual(sorted({item["a"] for item in catalogue["automorphisms"]}),
                         [1, 11, 16, 19, 24, 34])
        cases = catalogue["cases"]
        self.assertEqual([case["representative_pair"] for case in cases],
                         [[0, 1], [0, 2], [0, 4], [0, 5], [0, 7], [0, 8], [0, 14]])
        self.assertEqual([len(case["members"]) for case in cases], [105, 105, 105, 105, 35, 105, 35])
        self.assertEqual([case["edges"] for case in cases], [124] * 5 + [125] * 2)
        seen = set()
        source = catalogue["source_adjacency"]
        # Compare actual adjacency entries without using the runtime map helper.
        for case in cases:
            for member in case["members"]:
                pair = tuple(member["pair"])
                self.assertNotIn(pair, seen)
                seen.add(pair)
                kept = [v for v in range(35) if v not in pair]
                permutation = member["induced_permutation"]
                self.assertEqual(sorted(permutation), list(range(33)))
                for u, v in itertools.combinations(range(33), 2):
                    self.assertEqual((case["adjacency"][u] >> v) & 1,
                                     (source[kept[permutation[u]]] >> kept[permutation[v]]) & 1)
        self.assertEqual(seen, set(itertools.combinations(range(35), 2)))
        self.assertFalse(catalogue["is_complete_33_vertex_ramsey_catalogue"])

    def test_false_permutation_and_generic_cycle_catalogue(self):
        permutation = list(range(35))
        permutation[0], permutation[1] = permutation[1], permutation[0]
        self.assertFalse(is_isomorphism(base_graph(), base_graph(), permutation))
        cycle = graph_from_edges(5, [(v, (v + 1) % 5) for v in range(5)])
        catalogue = pair_catalogue(cycle)
        self.assertEqual(len(catalogue["automorphisms"]), 10)
        self.assertEqual(sorted(len(case["members"]) for case in catalogue["cases"]), [5, 5])
        with self.assertRaises(ValueError):
            induced(cycle, [0, 0])


class EnumerationControls(unittest.TestCase):
    def test_all_four_vertex_graphs_against_combinations(self):
        edges = list(itertools.combinations(range(4), 2))
        for pattern in range(1 << len(edges)):
            graph = graph_from_edges(4, [edge for bit, edge in enumerate(edges) if pattern >> bit & 1])
            for size in range(6):
                expected = {sum(1 << v for v in vertices)
                            for vertices in itertools.combinations(range(4), size)
                            if all(not (graph[u] >> v & 1) for u, v in itertools.combinations(vertices, 2))}
                observed = list(independent_sets(graph, size))
                self.assertEqual(set(observed), expected)
                self.assertEqual(len(observed), len(set(observed)))

    def test_interruption_never_publishes_a_complete_instance(self):
        with self.assertRaises(SearchLimit):
            list(independent_sets([0] * 4, 2, node_limit=1))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            with patch("encode.MAX_CLAUSES", 1), self.assertRaises(SearchLimit):
                write_instance(output, [2, 1], target=3, neighbours=2, minimum=2)
            self.assertFalse((output / "instance.cnf").exists())
            self.assertFalse((output / "instance.json").exists())
            self.assertTrue((output / "clauses.partial").exists())

    def test_invalid_base_graphs_rejected(self):
        with self.assertRaisesRegex(ValueError, "triangle"):
            encode([6, 5, 3], lambda _: None, target=4, neighbours=2, minimum=2)
        with self.assertRaisesRegex(ValueError, "independent"):
            encode([0, 0], lambda _: None, target=3, neighbours=2, minimum=2)


@unittest.skipUnless(LIBRARY, "set CADICAL_LIBRARY for projected SAT equivalence")
class ExhaustiveAttachmentControls(unittest.TestCase):
    def test_every_attachment_over_all_18_four_vertex_remainders(self):
        edges = list(itertools.combinations(range(4), 2))
        checked, accepted, bases = 0, 0, 0
        for pattern in range(1 << len(edges)):
            base = graph_from_edges(4, [edge for bit, edge in enumerate(edges) if pattern >> bit & 1])
            if has_triangle(base) or has_independent(base, 3):
                continue
            bases += 1
            clauses = []
            metadata = encode(base, clauses.append, target=4, neighbours=3, minimum=3)
            with native.Solver(LIBRARY, metadata["variables"], freeze=range(1, 13)) as solver:
                # Public CaDiCaL assumption API: assumptions reset after solve.
                assume = solver.api.ccadical_assume
                assume.argtypes, assume.restype = [ctypes.c_void_p, ctypes.c_int], None
                for clause in clauses:
                    solver.add(clause)
                for mask in range(1 << 12):
                    # Build the complete graph directly, independent of extension().
                    graph = list(base) + [0] * 4
                    for a in range(3):
                        graph[4 + a] |= 1 << 7
                        graph[7] |= 1 << (4 + a)
                    for v in range(4):
                        for a in range(3):
                            if mask >> (3 * v + a) & 1:
                                graph[v] |= 1 << (4 + a)
                                graph[4 + a] |= 1 << v
                    expected = (all(row.bit_count() == 3 for row in graph)
                                and all(any(graph[v] >> a & 1 for a in (4, 5, 6)) for v in range(4))
                                and not has_triangle(graph) and not has_independent(graph, 4))
                    for variable in range(1, 13):
                        assume(solver.handle, variable if mask >> (variable - 1) & 1 else -variable)
                    status = solver.solve()
                    self.assertIn(status, (10, 20))
                    self.assertEqual(status == 10, expected, (base, mask))
                    checked += 1
                    accepted += expected
        self.assertEqual(bases, 18)
        self.assertEqual(checked, 73_728)
        self.assertGreater(accepted, 0)


class ProofControls(unittest.TestCase):
    def test_large_variable_index_valid_proof_and_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            cnf, proof = Path(directory) / "x.cnf", Path(directory) / "x.lrat"
            cnf.write_text("p cnf 1001 2\n1001 0\n-1001 0\n")
            proof.write_text("3 0 1 2 0\n")
            self.assertTrue(verify(cnf, proof)["verified_unsatisfiable"])
            for bad in ("3 0 1 0\n", "3 0 -1 2 0\n", "3 0 7 0\n", ""):
                proof.write_text(bad)
                with self.assertRaises(ValueError):
                    verify(cnf, proof)
            proof.write_text("3 0 1 2 0\n")
            cnf.write_text("p cnf 1001 2\n1001 0\n1001 0\n")
            with self.assertRaises(ValueError):
                verify(cnf, proof)

    def test_model_contract_is_complete_and_consistent(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "solver.log"
            path.write_text("s SATISFIABLE\nv 1 -2 0\n")
            self.assertEqual(parse_model(path, 2), {1: True, 2: False})
            for bad in ("v 1 0\n", "v 1 -1 -2 0\n", "v 1 -2 3 0\n"):
                path.write_text(bad)
                with self.assertRaises(ValueError):
                    parse_model(path, 2)


@unittest.skipUnless(SOLVER, "set CADICAL_BINARY for tiny supervised SAT/LRAT controls")
class EndToEndControls(unittest.TestCase):
    def test_small_sat_and_unsat_with_source_snapshots(self):
        cycle = graph_from_edges(5, [(v, (v + 1) % 5) for v in range(5)])
        controls = [({"adjacency": [2, 1], "target": 3, "neighbours": 2, "minimum": 2}, "candidate_found"),
                    ({"adjacency": cycle, "target": 4, "neighbours": 3, "minimum": 3}, "unsat_rup_verified")]
        for control, expected in controls:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "attempt"
                result = run_attempt(output, Path(SOLVER), small_control=control,
                                     construction_seconds=5, solve_seconds=5, audit_seconds=5)
                self.assertEqual(result["status"], expected, result)
                self.assertEqual(result["unsat_verified"], expected == "unsat_rup_verified")
                self.assertFalse(result["external_ramsey_bound_claim_made"])
                for stage in result["stages"].values():
                    self.assertTrue(stage["owned_child_collected"])
                    self.assertIsNone(stage["external_stop"])
                self.assertTrue((output / "source" / "fixed_remainder" / "run.py").exists())
                with self.assertRaises(FileExistsError):
                    run_attempt(output, Path(SOLVER), small_control=control)
                self.assertEqual(json.loads((output / "result.json").read_text()), result)


if __name__ == "__main__":
    unittest.main()
