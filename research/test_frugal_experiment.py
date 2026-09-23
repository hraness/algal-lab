"""Offline transport and replay checks for the bounded conjecture pilot."""
from __future__ import annotations

import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from research.spikes.frugal import experiment


CLAIMS = [
    {"expression": "sum_adjacent_vs_crossing", "relation": "ge", "horizons": "all"},
    {"expression": "sum_crossing_vs_nested", "relation": "ge", "horizons": "all"},
    {"expression": "product_crossing_vs_nested", "relation": "ge", "horizons": "pair"},
]


class FakeOpener:
    def __init__(self, failures=None, price="0.00000012", usage=None):
        self.failures = failures or {}
        self.price = price
        self.usage = usage or {"prompt_tokens": 100, "completion_tokens": 50}
        self.posts = 0

    def open(self, request, timeout):
        if request.get_method() == "GET":
            catalog = {"data": {"id": "alibaba/qwen-3-14b", "endpoints": [
                {"provider_name": "deepinfra", "status": 0, "context_length": 40960,
                 "max_completion_tokens": 16384,
                 "pricing": {"prompt": self.price, "completion": "0.00000024", "request": "0"}}]}}
            return io.BytesIO(json.dumps(catalog).encode())
        self.posts += 1
        failure = self.failures.get(self.posts)
        if failure == "http":
            raise urllib.error.HTTPError(request.full_url, 503, "upstream", None, None)
        if failure == "transport":
            raise urllib.error.URLError("connection lost")
        response = {"model": "alibaba/qwen-3-14b", "choices": [{"finish_reason": "stop",
                    "message": {"content": json.dumps({"claims": CLAIMS})}}],
                    "usage": self.usage}
        return io.BytesIO(json.dumps(response).encode())


class FrugalExperimentTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        plan = json.loads(experiment.PROTOCOL.read_text())
        plan["development"] = {"nodes": [4], "rateCeiling": 4, "environmentsPerSize": 1, "seed": 17}
        plan["holdout"] = {"nodes": [4], "rateCeiling": 4, "environmentsPerSize": 1, "seed": 23}
        self.protocol = self.root / "protocol.json"
        self.protocol.write_text(json.dumps(plan))
        self.patcher = patch.object(experiment, "PROTOCOL", self.protocol)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def run_mock(self, opener):
        out = self.root / "run"
        with patch.dict("os.environ", {"AI_GATEWAY_API_KEY": "offline-test-key-123"}), \
             patch.object(experiment.urllib.request, "build_opener", return_value=opener):
            experiment.run(out)
        return out

    def test_success_replays_requests_selection_and_cost(self):
        opener = FakeOpener()
        out = self.run_mock(opener)
        self.assertEqual(opener.posts, 6)
        result = json.loads((out / "results.json").read_text())
        self.assertEqual(result["cost"]["dispatchedCalls"], 6)
        self.assertEqual(result["cost"]["unknownUsageCalls"], [])
        self.assertEqual(len(result["cost"]["standaloneArms"]), 4)
        experiment.replay(out)
        frozen_path = out / "frozen.json"
        original_frozen = frozen_path.read_text()
        frozen = json.loads(original_frozen)
        frozen["portfolios"][0]["claims"] = []
        frozen_path.write_text(json.dumps(frozen))
        with self.assertRaisesRegex(ValueError, "frozen selection mismatch"):
            experiment.replay(out)
        frozen_path.write_text(original_frozen)
        intent_path = out / "call-1-intent.json"
        result_path = out / "call-1-result.json"
        for path in (intent_path, result_path):
            record = json.loads(path.read_text())
            record["request"]["messages"][1]["content"] = "tampered initial context"
            path.write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, "request or intent mismatch"):
            experiment.replay(out)

    def test_failure_slots_and_uncertain_stop_replay(self):
        opener = FakeOpener({1: "http", 3: "transport"})
        out = self.run_mock(opener)
        self.assertEqual(opener.posts, 3)
        frozen = json.loads((out / "frozen.json").read_text())["portfolios"]
        self.assertEqual([p["status"] for p in frozen[:-1]],
                         ["skipped-initial-failed", "skipped-initial-failed",
                          "failed", "skipped-uncertain"])
        self.assertEqual(json.loads((out / "results.json").read_text())["cost"]["unknownUsageCalls"], [1, 3])
        experiment.replay(out)

    def test_catalog_price_gate_precedes_paid_call(self):
        opener = FakeOpener(price="0.00000013")
        with self.assertRaisesRegex(ValueError, "catalog limits or prices"):
            self.run_mock(opener)
        self.assertEqual(opener.posts, 0)

    def test_reported_usage_over_cap_stops_dispatch(self):
        opener = FakeOpener(usage={"prompt_tokens": 100, "completion_tokens": 1025})
        out = self.run_mock(opener)
        self.assertEqual(opener.posts, 1)
        statuses = [p["status"] for p in json.loads((out / "frozen.json").read_text())["portfolios"][:-1]]
        self.assertEqual(statuses, ["skipped-uncertain"] * 4)
        experiment.replay(out)

    def test_invalid_response_with_excess_usage_still_freezes_skipped_slots(self):
        class InvalidOverBudget(FakeOpener):
            def open(self, request, timeout):
                result = super().open(request, timeout)
                if request.get_method() == "POST":
                    response = json.loads(result.getvalue())
                    response["choices"][0]["message"]["content"] = "invalid JSON"
                    return io.BytesIO(json.dumps(response).encode())
                return result
        opener = InvalidOverBudget(usage={"prompt_tokens": 100, "completion_tokens": 1025})
        out = self.run_mock(opener)
        self.assertEqual(opener.posts, 1)
        statuses = [p["status"] for p in json.loads((out / "frozen.json").read_text())["portfolios"][:-1]]
        self.assertEqual(statuses, ["skipped-initial-failed"] * 2 + ["skipped-uncertain"] * 2)
        experiment.replay(out)


if __name__ == "__main__":
    unittest.main()
