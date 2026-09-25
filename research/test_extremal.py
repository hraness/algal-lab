"""Tests for the extremal-construction discovery loop (research/extremal)."""

import dataclasses
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from research.extremal import claims, novelty, registry
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
# One claim small enough to regenerate end to end in CI: ls5x from the published
# n = 17 certificate (milesandmistakes entry, index 1), logged seed and KMAX.
REGENERATE = {"target": "no-five-on-sphere-17", "n": 17, "k": 45, "kmax": 45, "seed": 790491471,
              "seed_target": "no-five-on-sphere-17", "seed_index": 1, "found": "FOUND n=17 k=45 it=2643 "}
SIGNIFICANCE = {"crowding": "uncontested", "evidence": "one source, 2026-09-24", "open_question": None}


def _target(**overrides):
    base = dict(id="t", title="t", objective="minimize", verifier="covering_design", parameters={"v": 6, "k": 3, "t": 2},
                best_known=Fraction(6), best_known_kind="exact", source="s", url="https://example.org", retrieved="2026-09-24", notes="",
                crowding="uncontested", evidence="one source, 2026-09-24", open_question=None, control_required=True)
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
                 "best_known": {"value": "1/3", "kind": "reported-decimal", "source": "s", "url": "https://e", "retrieved": "2026-09-24"},
                 "significance": SIGNIFICANCE, "control_required": True}
        with self.assertRaises(ValueError):
            registry.parse_target(entry)
        entry["best_known"]["value"] = "2.635"
        target = registry.parse_target(entry)
        self.assertEqual(target.reporting_precision(), Fraction(1, 2000))
        self.assertFalse(target.improves(Fraction("2.6354")))
        self.assertTrue(target.improves(Fraction("2.6356")))

    def test_significance_and_control_required_are_parsed_strictly(self):
        base = {"id": "x", "title": "x", "objective": "maximize", "verifier": "isosceles_free", "parameters": {"n": 4},
                "best_known": {"value": "3", "kind": "exact", "source": "s", "url": "https://e", "retrieved": "2026-09-24"},
                "significance": dict(SIGNIFICANCE, open_question="Is 3 optimal?"), "control_required": False}
        target = registry.parse_target(base)
        self.assertEqual((target.crowding, target.evidence, target.open_question, target.control_required),
                         ("uncontested", "one source, 2026-09-24", "Is 3 optimal?", False))
        self.assertIsNone(registry.parse_target(dict(base, significance=SIGNIFICANCE)).open_question)
        bad = [{k: v for k, v in base.items() if k != "significance"}, {k: v for k, v in base.items() if k != "control_required"},
               dict(base, control_required="yes"), dict(base, control_required=1), dict(base, significance="uncontested")]
        for sig in (dict(SIGNIFICANCE, crowding="hot"), dict(SIGNIFICANCE, crowding=None), dict(SIGNIFICANCE, evidence=""),
                    dict(SIGNIFICANCE, evidence=3), dict(SIGNIFICANCE, open_question=5), dict(SIGNIFICANCE, open_question=""),
                    dict(SIGNIFICANCE, extra=1), {k: v for k, v in SIGNIFICANCE.items() if k != "open_question"}):
            bad.append(dict(base, significance=sig))
        for entry in bad:
            with self.assertRaises(ValueError, msg=str(entry)):
                registry.parse_target(entry)

    def test_every_registry_target_states_dated_significance(self):
        for target in registry.load_registry().values():
            with self.subTest(target=target.id):
                self.assertIn(target.crowding, registry.CROWDING)
                self.assertRegex(target.evidence, r"20\d\d")
                self.assertTrue(target.control_required)


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

    def test_sphere_axis_plane_precheck_and_size_cap(self):
        layer = [[2, 0, 0], [2, 1, 3], [2, 3, 1], [2, 4, 4], [0, 0, 1], [2, 2, 5]]  # five points on x = 2
        with self.assertRaisesRegex(ValueError, "5 points on the plane x = 2"):
            no_five_on_sphere.verify({"points": layer}, {"n": 6})
        too_many = [[x, y, z] for x in range(5) for y in range(5) for z in range(4)][:no_five_on_sphere.MAX_POINTS + 1]
        with self.assertRaises(ValueError):
            no_five_on_sphere.verify({"points": too_many}, {"n": 5})

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


class ClaimTests(unittest.TestCase):
    PATHS = sorted((ROOT / "claims").glob("*.json"))
    # Round 26 ran unseeded controls at n = 18, 20 and 21 only; every other claim is labelled control-missing.
    SEARCH_STATUS = {"no-five-on-sphere-18": "under-searched", "no-five-on-sphere-20": "under-searched",
                     "no-five-on-sphere-21": "under-searched"}

    def _all(self):
        return [claim for path in self.PATHS for claim in claims.load_claims(path)]

    def test_claims_parse_and_reject_unknown_or_missing_fields(self):
        self.assertTrue(self.PATHS)
        raw = json.loads(self.PATHS[0].read_text())["claims"][0]
        self.assertEqual(claims.parse_claim(raw).target, raw["target"])
        with self.assertRaises(ValueError):
            claims.parse_claim(dict(raw, bogus=1))
        with self.assertRaises(ValueError):
            claims.parse_claim({k: v for k, v in raw.items() if k != "derivation"})
        with self.assertRaises(ValueError):
            claims.parse_claim(dict(raw, claimed="24 September 2026"))
        with self.assertRaises(ValueError):
            claims.parse_claim({k: v for k, v in raw.items() if k != "control"})
        with self.assertRaises(ValueError):
            claims.parse_claim(dict(raw, control=dict(raw["control"], kind="seeded")))

    def test_every_claim_reverifies_and_beats_its_registry_snapshot(self):
        targets = registry.load_registry()
        for claim in self._all():
            with self.subTest(target=claim.target):
                result = claims.check(claim, targets)
                self.assertEqual(result["status"], "improves-recorded-best")
                self.assertEqual(result["search_status"], self.SEARCH_STATUS.get(claim.target, "control-missing"))
                self.assertEqual(result["control"]["outcome"], claim.control.outcome)
                self.assertEqual(result["recorded_value"], str(claim.recorded_best))
                self.assertGreater(claim.value, claim.recorded_best)

    def test_stale_snapshot_wrong_value_and_tampering_are_rejected(self):
        targets = registry.load_registry()
        claim = min(self._all(), key=lambda c: len(c.construction["points"]))
        with self.assertRaisesRegex(ValueError, "registry holds"):
            claims.check(dataclasses.replace(claim, recorded_best=claim.recorded_best - 1), targets)
        with self.assertRaisesRegex(ValueError, "repeated point"):
            points = claim.construction["points"]
            claims.check(dataclasses.replace(claim, construction={"points": points + [points[0]]}), targets)
        with self.assertRaisesRegex(ValueError, "claim states"):
            claims.check(dataclasses.replace(claim, value=claim.value + 1), targets)

    def test_control_is_parsed_strictly(self):
        good = {"kind": "unseeded", "value": "47", "budget": "900 CPU seconds", "command": "ls5x 18 40 900 887588671", "outcome": "below"}
        control = claims.parse_control(good)
        self.assertEqual((control.value, control.budget, control.outcome), (Fraction(47), "900 CPU seconds", "below"))
        not_run = {"kind": "unseeded", "value": None, "budget": "2400 CPU seconds", "command": None, "outcome": "not-run"}
        self.assertEqual((claims.parse_control(not_run).value, claims.parse_control(not_run).command), (None, None))
        for bad in (dict(good, kind="seeded"), dict(good, outcome="won"), dict(good, outcome=None), dict(good, value=None),
                    dict(good, value=4.5), dict(good, value=True), dict(good, value="1/0"), dict(good, command=""),
                    dict(good, command=None), dict(good, budget=900), dict(good, extra=1),
                    {k: v for k, v in good.items() if k != "budget"}, dict(not_run, value="47"), dict(not_run, command="ls5x"),
                    "unseeded", ["unseeded"]):
            with self.assertRaises(ValueError, msg=str(bad)):
                claims.parse_control(bad)

    def test_search_status_labels(self):
        # A six-block C(6,3,2) covering against a synthetic recorded best of 7 blocks keeps this off the O(k^5) sphere verifier.
        blocks = [[0, 1, 2], [0, 1, 3], [0, 4, 5], [1, 4, 5], [2, 3, 4], [2, 3, 5]]
        target = _target(best_known=Fraction(7))
        targets = {"t": target}

        def control(value, outcome):
            return claims.Control(kind="unseeded", value=None if value is None else Fraction(value), budget="same as the seeded run",
                                  command=None if value is None else "cmd", outcome=outcome)

        def claim(ctrl, recorded=Fraction(7)):
            return claims.Claim(target="t", verifier="covering_design", parameters=target.parameters, value=Fraction(6),
                                recorded_best=recorded, claimed="2026-09-24", derivation=("d",), control=ctrl,
                                construction={"blocks": blocks})

        def label(ctrl, tgts=targets):
            result = claims.check(claim(ctrl), tgts)
            self.assertEqual(result["status"], "improves-recorded-best")
            return result["search_status"]

        # minimize: a control stuck at the recorded 7 blocks did not reach the claimed 6 (below) but did reach the recorded best.
        self.assertEqual(label(control(7, "below")), "under-searched")
        self.assertEqual(label(control(6, "matched")), "under-searched")
        self.assertEqual(label(control(5, "above")), "under-searched")
        self.assertEqual(label(control(8, "below")), "improves-recorded-best")
        self.assertEqual(label(control(None, "not-run")), "control-missing")
        self.assertEqual(label(control(None, "not-run"), {"t": dataclasses.replace(target, control_required=False)}), "control-not-required")
        for ctrl in (control(7, "matched"), control(6, "below"), control(8, "above")):
            with self.assertRaisesRegex(ValueError, "outcome"):
                claims.check(claim(ctrl), targets)
        # maximize: the same rule in the other direction.
        up = {"t": dataclasses.replace(target, objective="maximize", best_known=Fraction(5))}
        self.assertEqual(claims.check(claim(control(5, "below"), Fraction(5)), up)["search_status"], "under-searched")
        self.assertEqual(claims.check(claim(control(4, "below"), Fraction(5)), up)["search_status"], "improves-recorded-best")
        with self.assertRaisesRegex(ValueError, "outcome"):
            claims.check(claim(control(4, "above"), Fraction(5)), up)


class NativeSearchTests(unittest.TestCase):
    """Build the committed C searches and check them against published constructions and a claim."""

    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
        if compiler is None:
            raise unittest.SkipTest("no C compiler")
        cls.tmp = tempfile.TemporaryDirectory()
        cls.bin = {}
        for name, flags in (("ls5x", ["-DMAXP=32768", "-DMAXK=128"]), ("sym5", []), ("iso2", [])):
            out = Path(cls.tmp.name) / name
            subprocess.run([compiler, "-O2", *flags, "-o", str(out), str(ROOT / "native" / f"{name}.c"), "-lm"],
                           check=True, capture_output=True)
            cls.bin[name] = out

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def _points_file(self, name, points):
        path = Path(self.tmp.name) / name
        path.write_text("".join(" ".join(map(str, p)) + "\n" for p in points))
        return path

    def _run(self, args, env=None):
        proc = subprocess.run([str(a) for a in args], capture_output=True, text=True, timeout=600, env={**os.environ, **(env or {})})
        self.assertNotIn("SELFCHECK FAIL", proc.stderr)
        return proc, [json.loads(line) for line in proc.stdout.splitlines() if line.startswith("{")]

    def _known(self, target, index=0):
        return [e for e in KNOWN["entries"] if e["target"] == target][index]["construction"]["points"]

    def test_ls5x_keeps_a_published_record_and_regenerates_a_claim(self):
        ae7 = self._known("no-five-on-sphere-7")
        proc, found = self._run([self.bin["ls5x"], 7, 21, 5, 1, self._points_file("ae7.txt", ae7)])
        self.assertIn("FOUND n=7 k=21 it=0", proc.stderr)
        self.assertEqual(sorted(map(tuple, found[0]["points"])), sorted(map(tuple, ae7)))
        spec = REGENERATE
        seed_points = self._known(spec["seed_target"], spec["seed_index"])
        proc, found = self._run([self.bin["ls5x"], spec["n"], spec["k"], 600, spec["seed"], self._points_file("seed.txt", seed_points)],
                                env={"KMAX": str(spec["kmax"])})
        self.assertIn(spec["found"], proc.stderr)
        claim = next(c for c in ClaimTests()._all() if c.target == spec["target"])
        self.assertEqual(sorted(map(tuple, found[-1]["points"])), sorted(map(tuple, claim.construction["points"])))

    def test_sym5_and_iso2_print_only_verified_sets(self):
        proc, found = self._run([self.bin["sym5"], 6, 12, 3, 1])
        self.assertTrue(found, proc.stderr[-500:])
        for item in found[:3]:
            self.assertEqual(no_five_on_sphere.verify({"points": item["points"]}, {"n": 6}), Fraction(len(item["points"])))
        proc, found = self._run([self.bin["iso2"], 16, 14, 3, 1])
        self.assertTrue(found, proc.stderr[-500:])
        self.assertEqual(isosceles_free.verify({"points": found[0]["points"]}, {"n": 16}), Fraction(14))


if __name__ == "__main__":
    unittest.main()
