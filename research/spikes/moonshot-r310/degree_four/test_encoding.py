"""Exhaustive semantic controls for the attachment formula and proof checker."""

import itertools
from pathlib import Path
import tempfile
import unittest

from encode import base_graph, encode, extension, independent_sets
from lrat import verify
from checker import SearchLimit, independent_set, triangle


def graph(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def satisfies(clauses, positive):
    return all(any((literal in positive) if literal > 0 else (-literal not in positive)
                   for literal in clause) for clause in clauses)


class EncodingControls(unittest.TestCase):
    def test_enumeration_matches_all_five_vertex_graphs(self):
        pairs = list(itertools.combinations(range(5), 2))
        for bits in range(1 << len(pairs)):
            adj = graph(5, [edge for i, edge in enumerate(pairs) if bits >> i & 1])
            for size in range(6):
                expected = {sum(1 << v for v in selected)
                            for selected in itertools.combinations(range(5), size)
                            if all(not adj[u] >> v & 1 for u, v in itertools.combinations(selected, 2))}
                actual = list(independent_sets(adj, size))
                self.assertEqual(set(actual), expected)
                self.assertEqual(len(actual), len(expected))

    def test_formula_matches_every_small_attachment_assignment(self):
        # Includes overlapping attachment sets, not just one colour per vertex.
        for adj, target, neighbours in [(graph(2, [(0, 1)]), 3, 2),
                                        (graph(5, [(v, (v + 1) % 5) for v in range(5)]), 4, 2)]:
            clauses, metadata = encode(adj, target, neighbours)
            positive_count = 0
            for bits in range(1 << metadata["variables"]):
                positive = {i + 1 for i in range(metadata["variables"]) if bits >> i & 1}
                full = extension(adj, neighbours, positive)
                expected = triangle(full) is None and independent_set(full, target) is None
                self.assertEqual(satisfies(clauses, positive), expected, (adj, bits))
                positive_count += expected
            self.assertGreater(positive_count, 0)

    def test_order35_inventory_and_seed(self):
        adj = base_graph()
        self.assertTrue(all(row.bit_count() == 8 for row in adj))
        self.assertIsNone(triangle(adj))
        self.assertIsNone(independent_set(adj, 9))
        self.assertIsNotNone(independent_set(adj, 8))
        clauses, metadata = encode(adj)
        self.assertEqual(metadata["variables"], 140)
        self.assertEqual(metadata["independent_set_counts"], {"8": 3360, "7": 13760, "6": 22995})
        self.assertEqual(len(clauses), 98_965)
        self.assertFalse(metadata["symmetry_breaking"])

    def test_invalid_inputs_and_exhaustion_limits(self):
        with self.assertRaises(ValueError):
            encode([0] * 5, 4, 2)
        with self.assertRaises(ValueError):
            encode(graph(3, [(0, 1), (1, 2), (0, 2)]), 4, 2)
        with self.assertRaises(SearchLimit):
            list(independent_sets([0] * 8, 4, node_limit=1))
        with self.assertRaises(SearchLimit):
            list(independent_sets([0] * 8, 4, deadline=0))


class LratControls(unittest.TestCase):
    def check(self, formula, proof):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            cnf, lrat = directory / "input.cnf", directory / "proof.lrat"
            cnf.write_text(formula)
            lrat.write_text(proof)
            return verify(cnf, lrat)

    def test_contradictory_units(self):
        result = self.check("p cnf 1 2\n1 0\n-1 0\n", "3 0 1 2 0\n")
        self.assertTrue(result["verified_unsatisfiable"])

    def test_resolution_chain_and_deletion(self):
        formula = "p cnf 2 4\n1 2 0\n-1 2 0\n1 -2 0\n-1 -2 0\n"
        proof = "5 2 0 1 2 0\n6 -2 0 3 4 0\n6 d 1 2 3 4 0\n7 0 5 6 0\n"
        self.assertEqual(self.check(formula, proof)["additions"], 3)

    def test_tampered_or_incomplete_proofs_fail(self):
        formula = "p cnf 1 2\n1 0\n-1 0\n"
        for proof in ["", "3 0 1 0\n", "3 0 1 9 0\n", "3 0 -1 2 0\n",
                      "3 2 0 1 2 0\n", "1 0 1 2 0\n", "3 1 0 1 0\n"]:
            with self.assertRaises(ValueError, msg=proof):
                self.check(formula, proof)
        with self.assertRaises(ValueError):
            self.check("p cnf 2 1\n1 2 0\n", "2 0 1 0\n")


if __name__ == "__main__":
    unittest.main()
