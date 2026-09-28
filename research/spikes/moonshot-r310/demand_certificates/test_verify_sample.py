"""Independent weighted-set oracles and controls for the expanded sample."""

import copy
import hashlib
import itertools
import json
from pathlib import Path
import unittest

import verify
import verify_sample as sampled

HERE = Path(__file__).resolve().parent


class WeightedControls(unittest.TestCase):
    def test_all_75_small_graphs_with_three_weight_patterns(self):
        graphs = patterns = 0
        for n in range(1, 5):
            pairs = list(itertools.combinations(range(n), 2))
            for edge_bits in range(1 << len(pairs)):
                graph = [set() for _ in range(n)]
                for i, (u, v) in enumerate(pairs):
                    if edge_bits & (1 << i):
                        graph[u].add(v)
                        graph[v].add(u)
                adjacency = [sum(1 << v for v in row) for row in graph]
                demands = [[u, v] for u, v in pairs
                           if v not in graph[u] and graph[u].isdisjoint(graph[v])]
                independent = []
                for selected_bits in range(1 << n):
                    vertices = {v for v in range(n) if selected_bits & (1 << v)}
                    if all(graph[v].isdisjoint(vertices) for v in vertices):
                        independent.append(vertices)
                assignments = ([1] * len(demands),
                               [i % 4 for i in range(len(demands))],
                               [1 + i % 3 for i in range(len(demands))])
                for weights in assignments:
                    maximum = max(sum(w for w, (u, v) in zip(weights, demands)
                                      if u in vertices and v in vertices)
                                  for vertices in independent)
                    for capacity in range(sum(weights) + 1):
                        counterexample = sampled.weighted_capacity_bound(
                            adjacency, demands, weights, capacity, sampled.Budget())
                        self.assertEqual(counterexample is None, maximum <= capacity)
                        if counterexample is not None:
                            vertices = {v for v in range(n)
                                        if counterexample["independent_endpoint_mask"] & (1 << v)}
                            self.assertTrue(all(graph[v].isdisjoint(vertices) for v in vertices))
                            self.assertGreater(counterexample["total_weight"], capacity)
                    patterns += 1
                graphs += 1
        self.assertEqual((graphs, patterns), (75, 225))

    def test_six_cycle_weighted_minimality_and_strict_boundary(self):
        adjacency = [(1 << ((v - 1) % 6)) | (1 << ((v + 1) % 6)) for v in range(6)]
        demands, weights = [[0, 3], [1, 4], [2, 5]], [2, 1, 1]
        budget = sampled.Budget()
        result = sampled.verify_claim(adjacency, demands, weights, 2, 1, budget)
        self.assertTrue(result["maximal_extension_excluded"])
        self.assertEqual((budget.considered, budget.checked), (7, 2))
        with self.assertRaises(verify.InvalidCertificate):
            sampled.verify_claim(adjacency, demands, weights, 2, 2, sampled.Budget())
        witness = sampled.weighted_capacity_bound(adjacency, demands, weights, 1, sampled.Budget())
        self.assertEqual(witness, {"demand_indices": [0], "total_weight": 2,
                                   "independent_endpoint_mask": (1 << 0) | (1 << 3)})
        zero_result = sampled.verify_claim(adjacency, demands, [0, 1, 1], 1, 1, sampled.Budget())
        self.assertEqual(zero_result["selected_demands"], 2)
        self.assertIsNone(sampled.weighted_capacity_bound([0, 0], [[0, 1]], [0], 0, sampled.Budget()))

    def test_original_nine_preserved_and_matched_by_graph_bytes(self):
        original, old_hash = verify.read_bundle(HERE / "certificates.json")
        self.assertEqual(old_hash, "b04e152fe80f1f4e6cda1c76dd432506cc70d221794b0dc99c9f6d7ca85eaa45")
        self.assertEqual(hashlib.sha256((HERE / "verify.py").read_bytes()).hexdigest(),
                         "897e545c9e3e74a067423bfd65238e985e150ab7f1e4a34abde8db7931f70ebb")
        bundle, _ = verify.read_bundle(HERE / "sampled-certificates.json")
        by_bytes = {json.dumps(row["adjacency"], separators=(",", ":")).encode(): row["index"]
                    for row in bundle["sample"]}
        self.assertEqual(len(by_bytes), 128)
        certificates = {case["sample_index"]: case for case in bundle["certificates"]}
        matches = {}
        for row in original["cases"]:
            key = json.dumps(row["adjacency"], separators=(",", ":")).encode()
            index = by_bytes[key]
            matches[row["class"]] = index
            certificate = certificates[index]
            self.assertEqual(certificate["demands"], row["demands"])
            self.assertEqual(certificate["capacity_bound"], row["capacity_bound"])
            self.assertEqual(certificate["weights"], [1] * len(row["demands"]))
        self.assertEqual(matches, {i: i for i in range(9)})

    def test_false_capacities_weights_and_case_fields_rejected(self):
        bundle, _ = verify.read_bundle(HERE / "sampled-certificates.json")
        sample = {row["index"]: row for row in bundle["sample"]}
        original = next(case for case in bundle["certificates"] if case["sample_index"] == 8)
        for kind in ("capacity", "equality", "heavy", "negative", "boolean", "float", "too_large",
                     "zero", "missing", "unknown_field", "unknown_source", "boolean_index", "ragged"):
            case = copy.deepcopy(original)
            if kind == "capacity":
                case["capacity_bound"] = 0
            elif kind == "equality":
                case["demands"].pop()
                case["weights"].pop()
            elif kind in ("heavy", "negative", "boolean", "float", "too_large", "zero"):
                case["weights"][0] = {"heavy": 2, "negative": -1, "boolean": True,
                                       "float": 1.0, "too_large": 4, "zero": 0}[kind]
            elif kind == "missing":
                case["weights"].pop()
            elif kind == "unknown_field":
                case["unexpected"] = True
            elif kind == "unknown_source":
                case["source"] = []
            elif kind == "boolean_index":
                case["sample_index"] = True
            else:
                case["demands"] = None
            with self.subTest(kind=kind), self.assertRaises(verify.InvalidCertificate):
                sampled.verify_case(case, sample, sampled.Budget())

    def test_sample_partition_and_graph_identity_rejected(self):
        original, _ = verify.read_bundle(HERE / "sampled-certificates.json")
        for kind in ("duplicate_graph", "duplicate_index", "digest", "certificate_overlap",
                     "remaining_overlap", "missing_case", "extra_field", "source", "schema"):
            bundle = copy.deepcopy(original)
            if kind == "duplicate_graph":
                bundle["sample"][1] = copy.deepcopy(bundle["sample"][0])
                bundle["sample"][1]["index"] = 1
            elif kind == "duplicate_index":
                bundle["sample"][1]["index"] = 0
            elif kind == "digest":
                bundle["sample"][0]["adjacency_sha256"] = "0" * 64
            elif kind == "certificate_overlap":
                bundle["certificates"][1] = copy.deepcopy(bundle["certificates"][0])
            elif kind == "remaining_overlap":
                bundle["remaining_indices"][0] = 0
            elif kind == "missing_case":
                bundle["certificates"].pop()
            elif kind == "extra_field":
                bundle["unexpected"] = True
            elif kind == "source":
                bundle["sources"]["unexpected"] = "0" * 64
            else:
                bundle["schema_version"] = True
            with self.subTest(kind=kind), self.assertRaises(verify.InvalidCertificate):
                sampled.verify_bundle(bundle)

    def test_weighted_limits_fail_closed(self):
        adjacency = [(1 << ((v - 1) % 6)) | (1 << ((v + 1) % 6)) for v in range(6)]
        pairs, weights = [[0, 3], [1, 4], [2, 5]], [2, 1, 1]
        with self.assertRaises(verify.VerificationLimit):
            sampled.weighted_capacity_bound(adjacency, pairs, weights, 2, sampled.Budget(combinations=1))
        budget = sampled.Budget()
        budget.start -= 11
        with self.assertRaises(verify.VerificationLimit):
            sampled.weighted_capacity_bound(adjacency, pairs, weights, 2, budget)
        for kwargs in ({"combinations": 500_001}, {"combinations": True}, {"seconds": float("nan")}):
            with self.assertRaises(ValueError):
                sampled.Budget(**kwargs)
        for capacity in (-1, True, 1.0):
            with self.assertRaises(verify.InvalidCertificate):
                sampled.weighted_capacity_bound(adjacency, pairs, weights, capacity, sampled.Budget())


if __name__ == "__main__":
    unittest.main()
