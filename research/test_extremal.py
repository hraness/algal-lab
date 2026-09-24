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
from research.extremal.sandbox import isolation_mode, run_program
from research.extremal.verifiers import (circle_packing, covering_design, heilbronn_square, isosceles_free, load_verifier,
                                         no_five_on_sphere, ring_loading, sum_difference)

ROOT = Path(__file__).resolve().parent / "extremal"
SEED_COVER = (ROOT / "seeds" / "covering_greedy.py").read_text()
SEED_CIRCLES = (ROOT / "seeds" / "circles_grid.py").read_text()
SEED_ISO = (ROOT / "seeds" / "isosceles_greedy.py").read_text()
KNOWN = json.loads((ROOT / "known" / "record-constructions.json").read_text())


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

    def test_reported_decimal_must_terminate_and_improves_uses_precision(self):
        entry = {"id": "x", "title": "x", "objective": "maximize", "verifier": "isosceles_free", "parameters": {"n": 4},
                 "best_known": {"value": "1/3", "kind": "reported-decimal", "source": "s", "url": "https://e", "retrieved": "2026-09-24"}}
        with self.assertRaises(ValueError):
            registry.parse_target(entry)
        entry["best_known"]["value"] = "2.635"
        target = registry.parse_target(entry)
        self.assertEqual(target.reporting_precision(), Fraction(1, 2000))
        self.assertFalse(target.improves(Fraction("2.6354")))
        self.assertTrue(target.improves(Fraction("2.6356")))


class KnownConstructionTests(unittest.TestCase):
    def test_every_verifier_reproduces_its_published_value(self):
        targets = registry.load_registry()
        for entry in KNOWN["entries"]:
            with self.subTest(target=entry["target"]):
                value = load_verifier(entry["verifier"]).verify(entry["construction"], entry["parameters"])
                if entry["expected"] is not None:
                    self.assertEqual(value, Fraction(entry["expected"]))
                else:
                    self.assertGreaterEqual(value, Fraction(entry["expected_at_least"]))
                    self.assertLess(value, Fraction(entry["expected_below"]))
                target = targets[entry["target"]]
                self.assertEqual(target.verifier, entry["verifier"])
                self.assertEqual(target.parameters, entry["parameters"])
                # A published construction never passes the novelty gate against the registry's own bar.
                status = novelty.assess(target, value)["status"]
                self.assertIn(status, ("matches-recorded-best", "below-recorded-best", "within-reporting-precision"))
                if target.best_known_kind == "exact":
                    self.assertFalse(target.improves(value))

    def test_registry_bars_are_at_least_the_reproduced_values(self):
        targets = registry.load_registry()
        reproduced = {e["target"]: Fraction(e["expected"]) for e in KNOWN["entries"] if e["expected"] is not None}
        for tid, value in reproduced.items():
            self.assertEqual(targets[tid].best_known, value, tid)


class GridVerifierTests(unittest.TestCase):
    def test_isosceles_rejects_apex_and_flat_triangles(self):
        self.assertEqual(isosceles_free.verify({"points": [[0, 0], [1, 0], [3, 0]]}, {"n": 4}), Fraction(3))
        with self.assertRaises(ValueError):
            isosceles_free.verify({"points": [[0, 0], [1, 0], [2, 0]]}, {"n": 4})  # flat, midpoint
        with self.assertRaises(ValueError):
            isosceles_free.verify({"points": [[0, 0], [2, 0], [1, 5]]}, {"n": 8})  # apex
        with self.assertRaises(ValueError):
            isosceles_free.verify({"points": [[0, 0], [0, 0]]}, {"n": 4})
        with self.assertRaises(ValueError):
            isosceles_free.verify({"points": [[0, 4]]}, {"n": 4})

    def test_sphere_rejects_coplanar_and_cospherical(self):
        square_plane = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [2, 3, 0]]
        with self.assertRaises(ValueError):
            no_five_on_sphere.verify({"points": square_plane}, {"n": 4})
        cube_face_plus = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 1]]  # five vertices of a cube: cospherical
        with self.assertRaises(ValueError):
            no_five_on_sphere.verify({"points": cube_face_plus}, {"n": 2})
        ok = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [2, 2, 1]]
        self.assertEqual(no_five_on_sphere.verify({"points": ok}, {"n": 3}), Fraction(5))

    def test_ring_loading_exact(self):
        # m=1: no interior cut, value 0. m=2 with u=v=1/2: z choices give |z1 - z2|; best is 0.
        self.assertEqual(ring_loading.verify({"pairs": [["1/2", "1/2"]]}, {"m": 1}), Fraction(0))
        self.assertEqual(ring_loading.verify({"pairs": [["1/2", "1/2"], ["1/2", "1/2"]]}, {"m": 2}), Fraction(0))
        self.assertEqual(ring_loading.verify({"pairs": [["0", "1"], ["0", "1"], ["0", "1"]]}, {"m": 3}), Fraction(0))
        # u = v = 1/2, m = 3: z = (1/2, -1/2, 1/2) gives cuts 1/2 and 1/2; no assignment reaches 0.
        self.assertEqual(ring_loading.verify({"pairs": [["1/2", "1/2"]] * 3}, {"m": 3}), Fraction(1, 2))
        with self.assertRaises(ValueError):
            ring_loading.verify({"pairs": [["0.6", "0.5"]]}, {"m": 1})
        with self.assertRaises(ValueError):
            ring_loading.verify({"pairs": [[0.5, 0.5]]}, {"m": 1})

    def test_sum_difference_ratio(self):
        # A = {0, 1, 3}: A+A = {0,1,2,3,4,6} (6), A-A = {-3,-2,-1,0,1,2,3} (7): ln(2)/ln(7/3)
        value = sum_difference.verify({"set": [0, 1, 3]}, {})
        self.assertAlmostEqual(float(value), 0.8180679, places=6)
        with self.assertRaises(ValueError):
            sum_difference.verify({"set": [5]}, {})
        with self.assertRaises(ValueError):
            sum_difference.verify({"set": [1, 1, 2]}, {})

    def test_bad_literals_are_rejections_not_crashes(self):
        with self.assertRaises(ValueError):
            heilbronn_square.verify({"points": [["1/0", "0"], ["1", "0"], ["0", "1"]]}, {"n": 3})
        with self.assertRaises(ValueError):
            ring_loading.verify({"pairs": [["1/0", "0"]]}, {"m": 1})
        with self.assertRaises(ValueError):
            heilbronn_square.verify({"points": [["1e-" + "9" * 500, "0"], ["1", "0"], ["0", "1"]]}, {"n": 3})

    def test_heilbronn_square_exact(self):
        pts = [["0", "0"], ["1", "0"], ["0", "1"], ["1", "1"]]
        self.assertEqual(heilbronn_square.verify({"points": pts}, {"n": 4}), Fraction(1, 2))
        with self.assertRaises(ValueError):
            heilbronn_square.verify({"points": pts[:3]}, {"n": 4})
        with self.assertRaises(ValueError):
            heilbronn_square.verify({"points": [["0", "0"], ["1", "0"], ["0", "1.0000001"]]}, {"n": 3})
        with self.assertRaises(ValueError):
            heilbronn_square.verify({"points": [[0.0, 0.0], ["1", "0"], ["0", "1"]]}, {"n": 3})


class DeterminantTests(unittest.TestCase):
    def test_det4_matches_fraction_elimination(self):
        def elim(m):
            m = [[Fraction(x) for x in row] for row in m]
            det = Fraction(1)
            for c in range(4):
                pivot = next((r for r in range(c, 4) if m[r][c] != 0), None)
                if pivot is None:
                    return Fraction(0)
                if pivot != c:
                    m[c], m[pivot] = m[pivot], m[c]
                    det = -det
                det *= m[c][c]
                for r in range(c + 1, 4):
                    factor = m[r][c] / m[c][c]
                    for k in range(c, 4):
                        m[r][k] -= factor * m[c][k]
            return det
        rng = random.Random(7)
        for _ in range(300):
            m = [[rng.randint(-9, 9) for _ in range(4)] for _ in range(4)]
            self.assertEqual(no_five_on_sphere._det4(m), elim(m))


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
        result = run_program(SEED_ISO, {"n": 16}, 0, timeout=30)
        self.assertTrue(result.ok, result.error)
        self.assertGreater(isosceles_free.verify(result.construction, {"n": 16}), Fraction(4))
        result = run_program(SEED_COVER, {"v": 6, "k": 3, "t": 2}, 0, timeout=30)
        self.assertTrue(result.ok, result.error)
        self.assertEqual(covering_design.verify(result.construction, {"v": 6, "k": 3, "t": 2}), Fraction(len(result.construction["blocks"])))

    def test_containment_on_this_host(self):
        probe = (
            "import socket\n"
            "def construct(p, s):\n"
            "    out = {}\n"
            "    try:\n"
            "        open(p['path'], 'a').close(); out['write'] = 'allowed'\n"
            "    except Exception as exc:\n"
            "        out['write'] = type(exc).__name__\n"
            "    try:\n"
            "        s = socket.socket(); s.settimeout(1); s.connect(('127.0.0.1', 9)); out['net'] = 'allowed'\n"
            "    except Exception as exc:\n"
            "        out['net'] = type(exc).__name__\n"
            "    return out\n")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "outside.txt"
            result = run_program(probe, {"path": str(target)}, 0, timeout=20)
            self.assertTrue(result.ok, result.error)
            self.assertEqual(result.isolation, isolation_mode())
            if result.isolation == "sandbox-exec+rlimit":
                self.assertEqual(result.construction["write"], "PermissionError")
                self.assertFalse(target.exists())
                self.assertEqual(result.construction["net"], "PermissionError")

    def test_timeout_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            run_program("def construct(p, s):\n    return {}\n", {}, 0, timeout=10**6)

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
        proto = {"contract": "algal.lab.extremal-protocol.v1", "target": "isosceles-free-64", "seed": 5, "evaluations": 4,
                 "population": 3, "elites": 2, "operator": "scripted", "constructionSeeds": [0],
                 "programTimeout": 30, "seedProgram": str(ROOT / "seeds" / "isosceles_greedy.py")}
        proto.update(extra)
        path = Path(tmp) / "protocol.json"
        path.write_text(json.dumps(proto))
        return path

    def test_protocol_bounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            for bad in ({"evaluations": 5000}, {"operator": "command"}, {"programTimeout": 100000}, {"programTimeout": -5},
                        {"programTimeout": True}, {"commandTimeout": 10**5}, {"constructionSeeds": [-1]}):
                path = self._protocol(tmp, **bad)
                with self.assertRaises(ValueError, msg=str(bad)):
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
            self.assertEqual(a["evaluable"], sum(1 for l in lines_a if json.loads(l)["selection_value"] is not None))
            self.assertEqual(a["inputs_changed_during_run"], [])
            self.assertIn("registry.json", a["inputs_sha256"])
            self.assertIn("seedProgram", a["inputs_sha256"])
            self.assertTrue((Path(tmp) / "a" / "best-construction.json").exists())
            self.assertEqual(len(list((Path(tmp) / "a" / "programs").glob("*.py"))), len({json.loads(l)["program_sha256"] for l in lines_a}))

    def test_command_operator_with_fake_wrapper(self):
        with tempfile.TemporaryDirectory() as tmp:
            wrapper = Path(tmp) / "fake.py"
            wrapper.write_text(
                "import json,sys\nreq=json.load(sys.stdin)\nassert req['contract']=='algal.lab.extremal-request.v1'\n"
                "p=req['parents'][0]['program']\nprint('```python\\n'+p.replace('\"restarts\": 6','\"restarts\": 2')+'\\n```')\n")
            path = self._protocol(tmp, operator="command", command=[sys.executable, str(wrapper)], evaluations=3)
            result = run(path, Path(tmp) / "c")
            lines = [json.loads(l) for l in (Path(tmp) / "c" / "candidates.jsonl").read_text().splitlines()]
            self.assertEqual([l["operator"] for l in lines], ["seed", "command", "command"])
            self.assertTrue(all(l["selection_value"] for l in lines))
            self.assertEqual(result["best"]["novelty"]["status"], "below-recorded-best")
            # The wrapper returns the same program every time: the second command entry is a recorded duplicate.
            self.assertIn("duplicate of candidate 1", lines[2]["note"])
            self.assertEqual(lines[2]["evaluations"], [])

    def test_command_failures_trigger_repair_and_never_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            wrapper = Path(tmp) / "flaky.py"
            wrapper.write_text(
                "import json,sys\nreq=json.load(sys.stdin)\n"
                "failed=[p for p in req['parents'] if p['score'] is None]\n"
                "if failed:\n    print('```python\\n'+req['parents'][0]['program']+'\\n```')\n"
                "else:\n    print('```python\\ndef construct(p, s):\\n    return {\"points\": [[\"1/0\", 0]]}\\n```')\n")
            path = self._protocol(tmp, operator="command", command=[sys.executable, str(wrapper)], evaluations=3)
            result = run(path, Path(tmp) / "d")
            lines = [json.loads(l) for l in (Path(tmp) / "d" / "candidates.jsonl").read_text().splitlines()]
            self.assertIsNone(lines[1]["selection_value"])
            self.assertIn("verifier rejected", lines[1]["evaluations"][0]["error"])
            self.assertEqual(lines[2]["note"].split(";")[-1].strip(), "repair")
            self.assertEqual(result["evaluable"], 2)


if __name__ == "__main__":
    unittest.main()
