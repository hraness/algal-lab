"""Independent exhaustive small controls and input/termination regressions."""

import itertools
from pathlib import Path
import random
import subprocess
import tempfile
import unittest

from actions import (all_homomorphisms, cayley_actions, closure, compose, coset_action,
                     cycle, cyclic_action, eight_groups, nonregular_actions)
from checker import SearchLimit, independent_set, triangle, validate_adjacency, verify_candidate, verify_independent
from census import decode_graph6, scan
from import_transgrp import parse_chunk, parse_generators, parse_minimals
from orbits import adjacency_from_selection, edge_orbits, validate_action
from run import input_text, search_action, verify_certificates


HERE = Path(__file__).resolve().parent


def graph(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def brute_independent(adj, target):
    for selected in itertools.combinations(range(len(adj)), target):
        if all(not (adj[u] >> v & 1) for u, v in itertools.combinations(selected, 2)):
            return sum(1 << v for v in selected)
    return None


class TransGrpChecks(unittest.TestCase):
    def test_literal_cycles(self):
        self.assertEqual(parse_generators("(1,2,3)(4,5), (1,5)\n(2,4), ()", 5),
                         [[1, 2, 0, 4, 3], [4, 3, 2, 1, 0], [0, 1, 2, 3, 4]])
        with self.assertRaises(ValueError):
            parse_generators("(1 2,3)", 40)
        for malformed in ["(1,2)(2,3)", "(1,1)", "(0,1)", "(1,6)", "(1,)",
                          "(1)", "(1,2)*(3,4)", "(1,2),Exec(1)", "(1,2),", "[]"]:
            with self.assertRaises(ValueError, msg=malformed):
                parse_generators(malformed, 5)

    def test_chunk_indices_and_semantics(self):
        chunk = "# fixture\nTRANSGRP[5]{[3..4]}:=\n[[(1,2,3,4,5)],[(1,2,3,4,5),(1,2)]];\n"
        first, last, actions = parse_chunk(chunk, 5, {4})
        self.assertEqual((first, last), (3, 4))
        self.assertEqual(list(actions), [4])
        self.assertEqual(actions[4]["generators"], [[1, 2, 3, 4, 0], [1, 0, 2, 3, 4]])
        named = chunk.replace("(1,2)]]", '(1,2),"t5n4"]]')
        self.assertEqual(parse_chunk(named, 5, {4})[2], actions)
        with self.assertRaises(ValueError):
            parse_chunk(named.replace('"t5n4"', '"t5n3"'), 5, {4})
        for malformed in [chunk.replace("3..4", "3..5"), chunk.replace(",[(1,2,3,4,5)", "[(1,2,3,4,5)"),
                          chunk + chunk, "Quit;\n" + chunk, chunk.replace("(1,2,3,4,5)", "(1,2)")]:
            with self.assertRaises(ValueError):
                parse_chunk(malformed, 5, {3, 4})

    def test_minimal_indices(self):
        import json
        lists = [[] for _ in range(16)]
        lists[7] = [1, 2, 16, 60]
        literal = "TRANSMINIMALS{[32..47]}:=" + json.dumps(lists) + ";"
        self.assertEqual(parse_minimals(literal, 39), [1, 2, 16, 60])
        for malformed in [literal.replace("16", "2"), literal.replace("32..47", "32..48"), literal + "Quit;"]:
            with self.assertRaises(ValueError):
                parse_minimals(malformed, 39)


class Graph6Checks(unittest.TestCase):
    def test_known_graphs(self):
        self.assertEqual(decode_graph6(b"B?"), [0, 0, 0])
        self.assertEqual(decode_graph6(b"Bw"), [6, 5, 3])
        self.assertEqual(decode_graph6(b"Bg"), [2, 5, 2])
        cycle5 = decode_graph6(b">>graph6<<Dhc")
        self.assertTrue(all(row.bit_count() == 2 for row in cycle5))
        self.assertIsNone(triangle(cycle5))
        self.assertIsNone(independent_set(cycle5, 3))

    def test_strict_parser(self):
        for record in [b"", b"?", b"~??", b"B??", b"Bx", b"B~", b"B\x00", b"B? "]:
            with self.assertRaises(ValueError, msg=repr(record)):
                decode_graph6(record)

    def test_scanner_bounds_and_count(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "graphs.g6"
            path.write_bytes(b">>graph6<<\nB?\nBg\nBw\n")
            result = scan(path, order=3, target=2, expected_count=3)
            self.assertTrue(result["complete_file"])
            self.assertEqual(result["with_triangles"], 1)
            self.assertEqual(result["with_independent_set"], 2)
            self.assertIsNone(result["candidate"])
            limited = scan(path, order=3, target=2, max_records=1)
            self.assertFalse(limited["complete_file"])
            self.assertEqual(limited["reason"], "record_limit")
            with self.assertRaises(ValueError):
                scan(path, order=3, target=2, expected_count=4)
            path.write_bytes(b"B?\nB?\n")
            with self.assertRaises(ValueError):
                scan(path, order=3, target=2)
            path.write_bytes(b"Dhc\n")
            positive = scan(path, order=5, target=3)
            self.assertIsNotNone(positive["candidate"])
            self.assertFalse(positive["complete_file"])

    def test_oracle_limits_never_return_negative(self):
        with self.assertRaises(SearchLimit):
            independent_set([0] * 8, 4, node_limit=1)
        with self.assertRaises(SearchLimit):
            independent_set([0] * 8, 4, deadline=0)


class GraphChecks(unittest.TestCase):
    def test_checker_matches_all_five_vertex_graphs(self):
        edges = list(itertools.combinations(range(5), 2))
        for selection in range(1 << len(edges)):
            adj = graph(5, [edge for i, edge in enumerate(edges) if selection >> i & 1])
            for target in range(1, 6):
                expected = brute_independent(adj, target)
                actual = independent_set(adj, target)
                self.assertEqual(actual is None, expected is None, (selection, target))
                if actual is not None:
                    self.assertTrue(verify_independent(adj, actual, target))

    def test_checker_random_relabelings(self):
        rng = random.Random(31040)
        for _ in range(100):
            adj = graph(10, [edge for edge in itertools.combinations(range(10), 2) if rng.randrange(3) == 0])
            target = rng.randrange(2, 7)
            self.assertEqual(independent_set(adj, target) is None, brute_independent(adj, target) is None)
            perm = list(range(10))
            rng.shuffle(perm)
            renamed = graph(10, [(perm[u], perm[v]) for u, v in itertools.combinations(range(10), 2) if adj[u] >> v & 1])
            self.assertEqual(independent_set(renamed, target) is None, independent_set(adj, target) is None)

    def test_known_clebsch_graph(self):
        # Folded 5-cube: F_2^4 Cayley graph with four basis vectors and 1111.
        adj = [sum(1 << (v ^ s) for s in (1, 2, 4, 8, 15)) for v in range(16)]
        self.assertIsNone(triangle(adj))
        self.assertIsNotNone(independent_set(adj, 5))
        self.assertIsNone(independent_set(adj, 6))
        self.assertTrue(verify_candidate(adj, 6, 16)["is_ramsey_witness"])

    def test_invalid_graphs(self):
        for adj in ([1, 0], [2, 0], [4, 0], [False, 0]):
            with self.assertRaises(ValueError):
                validate_adjacency(adj)


class ActionChecks(unittest.TestCase):
    def test_group_tables_and_homomorphisms(self):
        totals = []
        for name, table in eight_groups():
            self.assertEqual(table[0], list(range(8)), name)
            for a, b, c in itertools.product(range(8), repeat=3):
                self.assertEqual(table[table[a][b]][c], table[a][table[b][c]])
            expected = {images for tail in itertools.product(range(4), repeat=7)
                        for images in [(0,) + tail]
                        if all(images[table[a][b]] == (images[a] + images[b]) % 4
                               for a, b in itertools.product(range(8), repeat=2))}
            actual = set(all_homomorphisms(table))
            self.assertEqual(expected, actual)
            totals.append(len(actual))
        self.assertEqual(totals, [4, 8, 8, 4, 4])

    def test_all_declared_actions(self):
        cayley = cayley_actions()
        self.assertEqual(len(cayley), 28)
        for action in cayley + nonregular_actions():
            self.assertEqual(action["n"], 40)
            orbits = edge_orbits(action)
            self.assertEqual(sum(item["degree"] for item in orbits), 39)
            for orbit in orbits:
                adj = orbit["adjacency"]
                validate_adjacency(adj)
                for perm in action["generators"]:
                    for v in range(40):
                        mapped = sum(1 << perm[w] for w in range(40) if adj[v] >> w & 1)
                        self.assertEqual(mapped, adj[perm[v]])

    def test_reject_invalid_actions(self):
        invalid = [
            {"name": "identity", "n": 3, "generators": [[0, 1, 2]]},
            {"name": "not permutation", "n": 3, "generators": [[1, 1, 0]]},
            {"name": "boolean", "n": 3, "generators": [[True, 2, 0]]},
            {"name": "unknown", "n": 3, "generators": [[1, 2, 0]], "complete": True},
        ]
        for action in invalid:
            with self.assertRaises(ValueError):
                validate_action(action)


class CompiledSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix="r310-controls-")
        cls.binary = Path(cls.directory.name) / "search"
        subprocess.run(["clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                        str(HERE / "search.c"), "-o", str(cls.binary)], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_cyclic_search_matches_brute_force(self):
        for n in range(3, 12):
            action = cyclic_action(n)
            orbits = edge_orbits(action)
            # Reference enumerates the whole Boolean cube and checks triples.
            selections = sorted(range(1 << len(orbits)),
                                key=lambda s: int(f"{s:0{len(orbits)}b}"[::-1], 2))
            candidates = [(s, adjacency_from_selection(orbits, s, n)) for s in selections]
            candidates = [(s, adj) for s, adj in candidates if triangle(adj) is None]
            for target in range(2, n + 1):
                expected = next(((s, adj) for s, adj in candidates if brute_independent(adj, target) is None), None)
                result = search_action(self.binary, action, maximum=n - 1, target=target, seconds=2)
                self.assertEqual(result["complete"], expected is None, (n, target))
                if expected is not None:
                    self.assertEqual(result["candidate"]["selection"], expected[0])
                else:
                    self.assertEqual(result["candidate_count"], len(candidates))

    def test_petersen_positive_control(self):
        action = coset_action("Petersen action", tuple(range(5)),
                              [cycle(5, 0, 1, 2, 3, 4), cycle(5, 0, 1, 2)],
                              [cycle(5, 0, 1, 2), compose(cycle(5, 0, 1), cycle(5, 3, 4))], compose, 60)
        result = search_action(self.binary, action, maximum=3, target=5, seconds=2)
        self.assertIsNotNone(result["candidate"])
        self.assertEqual(result["candidate"]["independent_verification"]["edges"], 15)

    def test_c35_ramsey_positive_control(self):
        result = search_action(self.binary, cyclic_action(35), minimum=8,
                               maximum=8, target=9, seconds=2)
        self.assertIsNotNone(result["candidate"])
        verified = result["candidate"]["independent_verification"]
        self.assertTrue(verified["is_ramsey_witness"])
        self.assertEqual(verified["edges"], 140)

    def test_nonregular_counts_match_full_boolean_cube(self):
        for action in nonregular_actions():
            orbits = edge_orbits(action)
            counts = [0] * 40
            for selection in range(1 << len(orbits)):
                degree = sum(orbit["degree"] for i, orbit in enumerate(orbits) if selection >> i & 1)
                if degree > 9:
                    continue
                adj = adjacency_from_selection(orbits, selection, 40)
                if triangle(adj) is None:
                    counts[degree] += 1
            result = search_action(self.binary, action, seconds=2)
            self.assertTrue(result["complete"])
            self.assertEqual(result["degree_counts"], counts, action["name"])

    def test_c40_counts_against_modular_arithmetic(self):
        counts = [0] * 40
        examined = 0
        for pairs in range(5):
            for combo in itertools.combinations(range(1, 20), pairs):
                for antipode in (False, True):
                    differences = {d for s in combo for d in (s, 40 - s)}
                    if antipode:
                        differences.add(20)
                    examined += 1
                    if all((a + b) % 40 not in differences for a in differences for b in differences):
                        counts[len(differences)] += 1
        self.assertEqual(examined, 10_072)
        self.assertEqual(sum(counts), 2_921)
        result = search_action(self.binary, cyclic_action(40), seconds=2)
        self.assertTrue(result["complete"])
        self.assertEqual(result["degree_counts"], counts)

    def test_limits_never_report_exhaustion(self):
        result = search_action(self.binary, cyclic_action(40), node_limit=1, seconds=2)
        self.assertFalse(result["complete"])
        self.assertEqual(result["reason"], "node_limit")
        self.assertIsNone(result["candidate"])

    def test_rejection_certificate_tampering(self):
        path = Path(self.directory.name) / "c5-rejections.txt"
        action = cyclic_action(5)
        result = search_action(self.binary, action, maximum=2, target=2, seconds=2, certificates=path)
        self.assertEqual(result["rejection_certificates_verified"], 3)
        path.write_text("0 0\n")
        with self.assertRaises(ValueError):
            verify_certificates(path, edge_orbits(action), 5, 0, 2, 2, 1)

    def test_c_refuses_incomplete_partition(self):
        action = cyclic_action(5)
        orbits = edge_orbits(action)
        data = input_text(action, orbits[:1], 0, 2, 3, 1000, 2)
        result = subprocess.run([str(self.binary)], input=data, text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("incomplete edge partition", result.stderr)


if __name__ == "__main__":
    unittest.main()
