"""Small independent-set oracles and rejection controls for the public proof."""

import copy
import itertools
import json
from pathlib import Path
import unittest

import verify


class Controls(unittest.TestCase):
    def test_all_75_graphs_through_order_four(self):
        graph_count = 0
        for n in range(1, 5):
            all_pairs = list(itertools.combinations(range(n), 2))
            for bits in range(1 << len(all_pairs)):
                neighbours = [set() for _ in range(n)]
                for index, (u, v) in enumerate(all_pairs):
                    if bits >> index & 1:
                        neighbours[u].add(v)
                        neighbours[v].add(u)
                adjacency = [sum(1 << v for v in row) for row in neighbours]
                demands = [[u, v] for u, v in all_pairs if v not in neighbours[u] and not neighbours[u].intersection(neighbours[v])]
                maximum = 0
                for selected_bits in range(1 << n):
                    selected = {v for v in range(n) if selected_bits >> v & 1}
                    if any(v in neighbours[u] for u, v in itertools.combinations(selected, 2)):
                        continue
                    maximum = max(maximum, sum(u in selected and v in selected for u, v in demands))
                for capacity in range(len(demands) + 1):
                    counterexample = verify.capacity_bound(adjacency, demands, capacity, verify.Budget())
                    self.assertEqual(counterexample is None, maximum <= capacity)
                graph_count += 1
        self.assertEqual(graph_count, 75)

    def test_six_cycle_boundary_and_independent_endpoint_witness(self):
        adjacency = [(1 << ((v - 1) % 6)) | (1 << ((v + 1) % 6)) for v in range(6)]
        pairs = [[0, 3], [1, 4], [2, 5]]
        verify.graph_ok(adjacency)
        verify.demands_ok(adjacency, pairs)
        budget = verify.Budget()
        self.assertIsNone(verify.capacity_bound(adjacency, pairs, 1, budget))
        self.assertEqual(budget.checked, 3)
        result = verify.verify_claim(adjacency, pairs, 1, 2, verify.Budget())
        self.assertTrue(result["maximal_extension_excluded"])
        self.assertEqual(result["centre_degree"], 2)
        with self.assertRaises(verify.InvalidCertificate):
            verify.verify_claim(adjacency, pairs, 1, 3, verify.Budget())
        witness = verify.capacity_bound(adjacency, pairs, 0, verify.Budget())
        self.assertIsNotNone(witness)
        vertices = {v for v in range(6) if witness["independent_endpoint_mask"] >> v & 1}
        self.assertEqual(vertices, {0, 3})

    def test_graph_and_demand_rejections(self):
        base = [(1 << ((v - 1) % 6)) | (1 << ((v + 1) % 6)) for v in range(6)]
        for adjacency in ([True] + base[1:], [row | (1 << v) for v, row in enumerate(base)], [-1] + base[1:]):
            with self.assertRaises(verify.InvalidCertificate):
                verify.graph_ok(adjacency)
        asymmetric = base.copy()
        asymmetric[0] ^= 1 << 1
        with self.assertRaises(verify.InvalidCertificate):
            verify.graph_ok(asymmetric)
        triangle = base.copy()
        triangle[0] |= 1 << 2
        triangle[2] |= 1
        with self.assertRaises(verify.InvalidCertificate):
            verify.graph_ok(triangle)
        for pairs in ([[0, 1]], [[0, 2]], [[0, 3], [0, 3]], [[3, 0]], [[False, 3]], [[0, 6]]):
            with self.assertRaises(verify.InvalidCertificate):
                verify.demands_ok(base, pairs)

    def test_false_capacity_strict_equality_and_identity_rejected(self):
        bundle, _ = verify.read_bundle(Path(__file__).with_name("certificates.json"))
        original = next(case for case in bundle["cases"] if case["class"] == 8)
        for edit in ("false_capacity", "equality", "identity", "extra"):
            case = copy.deepcopy(original)
            if edit == "false_capacity":
                case["capacity_bound"] = 0
            elif edit == "equality":
                case["demands"].pop()
            elif edit == "identity":
                case["adjacency_sha256"] = "0" * 64
            else:
                case["unexpected"] = True
            with self.assertRaises(verify.InvalidCertificate):
                verify.verify_case(case, 6, verify.Budget())

    def test_parse_and_resource_fail_closed(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(verify.InvalidCertificate):
                json.loads(raw, object_pairs_hook=verify.unique_fields, parse_constant=verify.reject_constant)
        with self.assertRaises(verify.VerificationLimit):
            verify.capacity_bound([0] * 6, [[0, 3], [1, 4], [2, 5]], 1, verify.Budget(subsets=1))
        budget = verify.Budget()
        budget.start -= 11
        with self.assertRaises(verify.VerificationLimit):
            verify.capacity_bound([0] * 2, [[0, 1]], 1, budget)
        with self.assertRaises(verify.InvalidCertificate):
            verify.capacity_bound([0] * 2, [[0, 1]], True, verify.Budget())


if __name__ == "__main__":
    unittest.main()
