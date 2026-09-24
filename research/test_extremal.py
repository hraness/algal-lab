"""Tests for the extremal-construction discovery loop (research/extremal)."""

import json
import os
import random
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from research.extremal import novelty, registry
from research.extremal.evolve import parse_protocol, run
from research.extremal.operators import extract_program, read_params, scripted_mutate, write_params
from research.extremal.sandbox import run_program
from research.extremal.verifiers import circle_packing, covering_design, load_verifier

ROOT = Path(__file__).resolve().parent / "extremal"
SEED_COVER = (ROOT / "seeds" / "covering_greedy.py").read_text()
SEED_CIRCLES = (ROOT / "seeds" / "circles_grid.py").read_text()


def _target(**overrides):
    base = dict(id="t", title="t", objective="minimize", verifier="covering_design", parameters={"v": 6, "k": 3, "t": 2},
                best_known=Fraction(6), best_known_kind="exact", source="s", url="https://example.org", retrieved="2026-09-24", notes="")
    base.update(overrides)
    return registry.Target(**base)


class RegistryTests(unittest.TestCase):
    def test_registry_loads_and_every_target_has_a_verifier(self):
        targets = registry.load_registry()
        self.assertGreaterEqual(len(targets), 1)
        for target in targets.values():
            load_verifier(target.verifier)
            self.assertTrue(target.url.startswith("https://"))
            self.assertRegex(target.retrieved, r"^\d{4}-\d{2}-\d{2}$")

    def test_improves_respects_objective(self):
        self.assertTrue(_target().improves(Fraction(5)))
        self.assertFalse(_target().improves(Fraction(6)))
        self.assertTrue(_target(objective="maximize").improves(Fraction(7)))
        self.assertFalse(_target(objective="maximize").improves(Fraction(6)))

    def test_unknown_field_rejected(self):
        with self.assertRaises(ValueError):
            registry.parse_target({"id": "x", "bogus": 1})


class VerifierTests(unittest.TestCase):
    def test_covering_counts_blocks_and_rejects_gaps(self):
        blocks = [[0, 1, 2], [0, 1, 3], [0, 4, 5], [1, 4, 5], [2, 3, 4], [2, 3, 5]]
        # C(6,3,2): a known 6-block covering (all pairs covered). Check coverage exactly.
        self.assertEqual(covering_design.verify({"blocks": blocks}, {"v": 6, "k": 3, "t": 2}), Fraction(6))
        with self.assertRaises(ValueError):
            covering_design.verify({"blocks": blocks[:5]}, {"v": 6, "k": 3, "t": 2})
        with self.assertRaises(ValueError):
            covering_design.verify({"blocks": [[0, 1, 1]]}, {"v": 6, "k": 3, "t": 2})

    def test_circle_packing_exact(self):
        two = {"circles": [["1/4", "1/4", "1/4"], ["3/4", "3/4", "1/4"]]}
        self.assertEqual(circle_packing.verify(two, {"n": 2}), Fraction(1, 2))
        with self.assertRaises(ValueError):
            circle_packing.verify({"circles": [["1/2", "1/2", "1/2"], ["1/2", "1/2", "1/4"]]}, {"n": 2})
        with self.assertRaises(ValueError):
            circle_packing.verify({"circles": [["1/2", "1/2", "3/5"]]}, {"n": 1})


class SandboxTests(unittest.TestCase):
    def test_runs_seed_program(self):
        result = run_program(SEED_COVER, {"v": 6, "k": 3, "t": 2}, 0, timeout=30)
        self.assertTrue(result.ok, result.error)
        self.assertEqual(covering_design.verify(result.construction, {"v": 6, "k": 3, "t": 2}), Fraction(len(result.construction["blocks"])))

    def test_timeout_and_errors_are_reported(self):
        result = run_program("def construct(p, s):\n    while True: pass\n", {}, 0, timeout=1)
        self.assertFalse(result.ok)
        self.assertIn("time", result.error.lower())
        result = run_program("def construct(p, s):\n    return 1/0\n", {}, 0, timeout=5)
        self.assertFalse(result.ok)
        self.assertIn("ZeroDivisionError", result.error)
        result = run_program("x = 1\n", {}, 0, timeout=5)
        self.assertFalse(result.ok)


class OperatorTests(unittest.TestCase):
    def test_params_roundtrip_and_mutation_changes_numbers_only(self):
        params = read_params(SEED_COVER)
        self.assertEqual(params["restarts"], 20)
        rng = random.Random(3)
        child = scripted_mutate(SEED_COVER, rng)
        self.assertNotEqual(child, SEED_COVER)
        self.assertEqual(set(read_params(child)), set(params))
        self.assertEqual(write_params(child, params), SEED_COVER)

    def test_extract_program_forms(self):
        self.assertEqual(extract_program(json.dumps({"program": "def construct(p,s): pass"})), "def construct(p,s): pass")
        self.assertEqual(extract_program("text\n```python\ndef construct(p,s):\n    pass\n```\n"), "def construct(p,s):\n    pass\n")
        self.assertIsNone(extract_program("no code here"))


class NoveltyTests(unittest.TestCase):
    def test_statuses(self):
        self.assertEqual(novelty.assess(_target(), Fraction(5))["status"], "improves-recorded-best")
        self.assertEqual(novelty.assess(_target(), Fraction(6))["status"], "matches-recorded-best")
        self.assertEqual(novelty.assess(_target(), Fraction(7))["status"], "below-recorded-best")
        dec = _target(objective="maximize", best_known=Fraction("2.635"), best_known_kind="reported-decimal")
        self.assertEqual(novelty.assess(dec, Fraction("2.6354"))["status"], "within-reporting-precision")
        self.assertEqual(novelty.assess(dec, Fraction("2.64"))["status"], "improves-recorded-best")


class EvolveTests(unittest.TestCase):
    def _protocol(self, tmp, **extra):
        proto = {"contract": "algal.lab.extremal-protocol.v1", "target": "covering-C-12-4-3", "seed": 5, "evaluations": 4,
                 "population": 3, "elites": 2, "operator": "scripted", "constructionSeeds": [0],
                 "programTimeout": 30, "seedProgram": str(ROOT / "seeds" / "covering_greedy.py")}
        proto.update(extra)
        path = Path(tmp) / "protocol.json"
        path.write_text(json.dumps(proto))
        return path

    def test_protocol_bounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._protocol(tmp, evaluations=5000)
            with self.assertRaises(ValueError):
                parse_protocol(json.loads(path.read_text()), Path(tmp))
            path = self._protocol(tmp, operator="command")
            with self.assertRaises(ValueError):
                parse_protocol(json.loads(path.read_text()), Path(tmp))

    def test_scripted_run_is_reproducible_and_archived(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._protocol(tmp)
            a = run(path, Path(tmp) / "a")
            b = run(path, Path(tmp) / "b")
            self.assertEqual(a["candidates"], 4)
            self.assertEqual(a["best"]["value"], b["best"]["value"])
            lines_a = (Path(tmp) / "a" / "candidates.jsonl").read_text().splitlines()
            lines_b = (Path(tmp) / "b" / "candidates.jsonl").read_text().splitlines()
            self.assertEqual([json.loads(l)["program_sha256"] for l in lines_a], [json.loads(l)["program_sha256"] for l in lines_b])
            self.assertEqual(a["best"]["novelty"]["status"], "below-recorded-best")
            self.assertTrue((Path(tmp) / "a" / "best-construction.json").exists())
            self.assertEqual(len(list((Path(tmp) / "a" / "programs").glob("*.py"))), len({json.loads(l)["program_sha256"] for l in lines_a}))

    def test_command_operator_with_fake_wrapper(self):
        with tempfile.TemporaryDirectory() as tmp:
            wrapper = Path(tmp) / "fake.py"
            wrapper.write_text(
                "import json,sys\nreq=json.load(sys.stdin)\nassert req['contract']=='algal.lab.extremal-request.v1'\n"
                "p=req['parents'][0]['program']\nprint('```python\\n'+p.replace('\"restarts\": 20','\"restarts\": 2')+'\\n```')\n")
            path = self._protocol(tmp, operator="command", command=[sys.executable, str(wrapper)], evaluations=3)
            result = run(path, Path(tmp) / "c")
            lines = [json.loads(l) for l in (Path(tmp) / "c" / "candidates.jsonl").read_text().splitlines()]
            self.assertEqual([l["operator"] for l in lines], ["seed", "command", "command"])
            self.assertTrue(all(l["selection_value"] for l in lines))
            self.assertEqual(result["best"]["novelty"]["status"], "below-recorded-best")


if __name__ == "__main__":
    unittest.main()
