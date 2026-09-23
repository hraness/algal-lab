from copy import deepcopy
from fractions import Fraction
import math
import unittest

from research import certify_policy_results as bridge
from research.tree_certificate import certify


def row(regime="primary-tree", seed=1):
    nodes, steps = bridge.REGIMES[regime] or (8, 3)
    graph = {"nodes": nodes, "edges": [[0, i] for i in range(1, nodes)]}
    environment = {"weights": [1] * nodes, "values": [1] * nodes}
    exact = certify({"graph": graph, "environment": environment, "steps": steps})
    result = {field: None for field in bridge.RESULT_FIELDS}
    result.update(graph=graph, score=float(Fraction(exact["candidateAuc"])))
    arms = {name: {} for name in bridge.ARM_NAMES}
    arms["selected"] = {"result": result, "objectiveSelectionEvaluations": 64, "measurementEvaluations": 0}
    return {"key": f"{regime}:{seed}", "seed": seed, "regime": regime, "environment": environment, "ceiling": 1, "arms": arms}


def panel():
    report = {field: None for field in bridge.REPORT_FIELDS}
    report.update(contract="algal.lab.policy-spike-heldout.v1", results=[])
    for regime in bridge.REGIMES:
        template = row(regime)
        for seed in range(32):
            entry = {**template, "key": f"{regime}:{seed}", "seed": seed}
            report["results"].append(entry)
    return report


class PolicyCertificateTests(unittest.TestCase):
    def test_one_exact_entry_and_score_rejection(self):
        entry = row()
        result = bridge._certify_row(entry)
        self.assertEqual(result["certificate"]["status"], "optimal")
        self.assertEqual(result["certificate"]["input"]["steps"], 3)
        self.assertEqual(result["certificate"]["input"]["graph"]["nodes"], 8)
        for score in (math.nan, math.inf, -1, 2, 10 ** 1000, True, "0.5", 0.5):
            bad = deepcopy(entry)
            bad["arms"]["selected"]["result"]["score"] = score
            with self.subTest(score=score), self.assertRaises(ValueError):
                bridge._certify_row(bad)
        bad = deepcopy(entry)
        bad["arms"]["selected"]["result"]["graph"]["edges"].append([1, 2])
        with self.assertRaises(ValueError):
            bridge._certify_row(bad)

    def test_exact_panel_selection_and_duplicate_count_rejections(self):
        valid = panel()
        selected = bridge._selected_rows(valid)
        self.assertEqual(len(selected), 64)
        self.assertEqual({entry["regime"] for entry in selected}, {"primary-tree", "transfer-tree"})
        invalid = []
        for change in ("wrong-contract", "short", "duplicate", "unknown-regime", "mismatched-seeds", "unknown-field"):
            bad = deepcopy(valid)
            if change == "wrong-contract": bad["contract"] = "wrong"
            if change == "short": bad["results"].pop()
            if change == "duplicate": bad["results"][1] = deepcopy(bad["results"][0])
            if change == "unknown-regime": bad["results"][0]["regime"] = "other"
            if change == "mismatched-seeds": bad["results"][0].update(seed=99, key="primary-tree:99")
            if change == "unknown-field": bad["extra"] = 1
            invalid.append((change, bad))
        for change, bad in invalid:
            with self.subTest(change=change), self.assertRaises(ValueError):
                bridge._selected_rows(bad)


if __name__ == "__main__":
    unittest.main()
