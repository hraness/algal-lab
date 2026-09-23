"""Focused exact checks, including an independent weighted-order reference."""

from copy import deepcopy
from fractions import Fraction
from itertools import permutations, product
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from research.tree_certificate import MAX_INPUT_BYTES, admit, certify, read_input


def trees(nodes):
    result = []
    for sequence in product(range(nodes), repeat=nodes - 2):
        degrees = [1] * nodes
        for node in sequence:
            degrees[node] += 1
        edges = []
        for node in sequence:
            leaf = next(i for i in range(nodes) if degrees[i] == 1)
            edges.append([leaf, node])
            degrees[leaf] -= 1
            degrees[node] -= 1
        edges.append([i for i in range(nodes) if degrees[i] == 1])
        result.append({"nodes": nodes, "edges": edges})
    return result


def star(nodes, center):
    return {"nodes": nodes, "edges": [[center, i] for i in range(nodes) if i != center]}


def order_reference(graph, weights, values, steps):
    """Removal-order enumeration plus independent union-find components."""
    nodes = graph["nodes"]
    expected = [Fraction(0)] * (steps + 1)
    for order in permutations(range(nodes), steps):
        alive = set(range(nodes))
        chance = Fraction(1)
        service = [Fraction(1)]
        for removed in order:
            chance *= Fraction(weights[removed], sum(weights[i] for i in alive))
            alive.remove(removed)
            parent = list(range(nodes))

            def root(i):
                while parent[i] != i:
                    i = parent[i]
                return i

            for a, b in graph["edges"]:
                if a in alive and b in alive:
                    parent[root(a)] = root(b)
            sums = {}
            for i in alive:
                r = root(i)
                sums[r] = sums.get(r, 0) + values[i]
            service.append(Fraction(max(sums.values(), default=0), sum(values)))
        for k in range(steps + 1):
            expected[k] += chance * service[k]
    auc = (expected[0] + expected[-1] + 2 * sum(expected[1:-1])) / (2 * steps)
    return auc, expected


class TreeCertificateTests(unittest.TestCase):
    def request(self, graph=None, weights=None, values=None, steps=2):
        return {"graph": graph or star(4, 0),
                "environment": {"weights": weights or [1, 2, 3, 4], "values": values or [5, 4, 3, 2]},
                "steps": steps}

    def test_exhaustive_four_node_panel_against_independent_orders(self):
        candidates = trees(4)
        self.assertEqual(len(candidates), 16)
        comparisons = 0
        for weights in product((1, 2), repeat=4):
            for values in product((1, 2), repeat=4):
                for steps in (1, 2):
                    scores = []
                    certificates = []
                    for graph in candidates:
                        reference, trajectory = order_reference(graph, weights, values, steps)
                        certificate = certify(self.request(graph, list(weights), list(values), steps))
                        self.assertEqual(Fraction(certificate["candidateAuc"]), reference)
                        self.assertEqual([Fraction(row["candidateExpectedService"]) for row in certificate["trajectory"]], trajectory)
                        scores.append(reference)
                        certificates.append(certificate)
                        comparisons += 1
                    optimum = max(scores)
                    for certificate, score in zip(certificates, scores):
                        upper = Fraction(certificate["treeOptimumUpperBound"])
                        gap = Fraction(certificate["additiveRegretUpperBound"])
                        self.assertGreaterEqual(upper, optimum)
                        self.assertEqual(gap, upper - score)
                        self.assertEqual(certificate["status"] == "optimal", gap == 0)
                        if steps == 1:
                            self.assertEqual(upper, optimum)
        self.assertEqual(comparisons, 8192)

    def test_aligned_hub_and_non_aligned_one_failure_are_certified(self):
        for nodes in (4, 6, 10):
            weights = list(range(1, nodes + 1))
            values = list(range(nodes, 0, -1))
            for steps in (1, nodes - 2):
                certificate = certify(self.request(star(nodes, 0), weights, values, steps))
                self.assertEqual(certificate["status"], "optimal")
                self.assertEqual(certificate["additiveRegretUpperBound"], "0")
        request = self.request(star(4, 2), [1, 1, 2, 5], [1, 1, 4, 4], 1)
        certificate = certify(request)
        self.assertEqual(certificate["status"], "optimal")
        self.assertEqual(certificate["boundRoot"], 0)
        tied = certify(self.request(star(4, 1), [1, 1, 2, 3], [1, 5, 3, 2], 2))
        self.assertEqual(tied["boundRoot"], 1)
        self.assertEqual(tied["status"], "optimal")

    def test_known_optimum_can_have_a_positive_valid_bound(self):
        graph = {"nodes": 4, "edges": [[0, 1], [0, 2], [2, 3]]}
        certificate = certify(self.request(graph, [1, 1, 2, 5], [1, 1, 4, 4], 2))
        self.assertEqual(certificate["candidateAuc"], "12937/20160")
        self.assertEqual(certificate["status"], "bounded")
        gap = Fraction(certificate["additiveRegretUpperBound"])
        self.assertGreater(gap, 0)
        for candidate in trees(4):
            score, _ = order_reference(candidate, [1, 1, 2, 5], [1, 1, 4, 4], 2)
            self.assertLessEqual(score, Fraction(certificate["candidateAuc"]))
        self.assertIn("does not prove suboptimality", certificate["interpretation"])

    def test_boundaries_canonical_input_and_strict_rejections(self):
        request = self.request({"nodes": 4, "edges": [[3, 0], [2, 0], [1, 0]]}, [99] * 4, [99] * 4)
        certificate = certify(request)
        self.assertEqual(certificate["input"]["graph"]["edges"], [[0, 1], [0, 2], [0, 3]])
        request["environment"]["weights"][0] = 1
        self.assertEqual(certificate["input"]["environment"]["weights"][0], 99)
        valid = self.request()
        invalid = [None, [], {**valid, "extra": 1}, {"graph": valid["graph"], "environment": valid["environment"]}]
        for path, value in [(("graph", "nodes"), 3), (("graph", "nodes"), 11), (("graph", "nodes"), True),
                            (("steps",), 0), (("steps",), 3), (("steps",), 1.0), (("steps",), True),
                            (("environment", "weights"), [0, 1, 1, 1]), (("environment", "values"), [100, 1, 1, 1]),
                            (("environment", "values"), [True, 1, 1, 1]), (("environment", "weights"), [1, 1, 1]),
                            (("graph", "edges"), [[0, 1], [1, 0], [2, 3]]),
                            (("graph", "edges"), [[0, 0], [0, 2], [0, 3]]),
                            (("graph", "edges"), [[0, 1], [1, 2], [2, 0]]),
                            (("graph", "edges"), [[0, 1], [0, 2], [0, 4]]),
                            (("graph", "edges"), [[0, 1], [0, 2], [0, 3], [1, 2]])]:
            candidate = deepcopy(valid)
            target = candidate
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            invalid.append(candidate)
        for field in ("graph", "environment"):
            candidate = deepcopy(valid)
            candidate[field]["extra"] = 1
            invalid.append(candidate)
        for candidate in invalid:
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                admit(candidate)

    def test_file_byte_limit_duplicate_keys_and_stdout_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            path.write_text(json.dumps(self.request()))
            script = Path(__file__).with_name("tree_certificate.py")
            result = subprocess.run([sys.executable, str(script), str(path)], capture_output=True, text=True, check=True)
            self.assertEqual(result.stderr, "")
            self.assertEqual(json.loads(result.stdout), certify(self.request()))
            self.assertEqual(sorted(p.name for p in Path(directory).iterdir()), ["request.json"])
            for content in [b" " * (MAX_INPUT_BYTES + 1), b'{"graph":null,"graph":null}',
                            b'{"graph":NaN}', b'{"graph":Infinity}', b'\xff', b'[' * 2000 + b']' * 2000, b'[]']:
                path.write_bytes(content)
                with self.subTest(content=content[:30]), self.assertRaises((ValueError, UnicodeError)):
                    read_input(path)
            result = subprocess.run([sys.executable, str(script), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertIn("tree certificate:", result.stderr)


if __name__ == "__main__":
    unittest.main()
