"""Finite controls for the portable packet wrapper; no solver or graph search."""

import argparse
from contextlib import contextmanager
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import types
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("_portable_verify", HERE / "verify.py")
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)
PACKET_ROOT = None


def example_manifest():
    manifest = copy.deepcopy(verify.manifest_header())
    manifest["files"] = {name: {"bytes": verify.FROZEN.get(name, (1, "0" * 64))[0],
                              "sha256": verify.FROZEN.get(name, (1, "0" * 64))[1]}
                         for name in verify.PAYLOAD}
    return manifest


class WrapperControls(unittest.TestCase):
    def test_inherited_limits_are_never_raised(self):
        infinity, mib = verify.resource.RLIM_INFINITY, 1024**2
        cases = (
            ((2, 30), (64 * mib, 512 * mib), 2, 64 * mib),
            ((infinity, 3), (infinity, 96 * mib), 3, 96 * mib),
            ((infinity, infinity), (infinity, infinity), 11, 256 * mib),
            ((20, 30), (512 * mib, 1024 * mib), 11, 256 * mib),
        )
        for cpu, memory, expected_cpu, expected_memory in cases:
            with self.subTest(cpu=cpu, memory=memory), \
                 mock.patch.object(verify.sys, "platform", "linux"), \
                 mock.patch.object(verify.resource, "getrusage",
                                   return_value=types.SimpleNamespace(ru_utime=0.25, ru_stime=0.25)), \
                 mock.patch.object(verify.resource, "getrlimit", side_effect=(cpu, memory)), \
                 mock.patch.object(verify.resource, "setrlimit") as limits, \
                 mock.patch.object(verify.signal, "signal"), \
                 mock.patch.object(verify.signal, "alarm"):
                verify.cli_limits()
                self.assertEqual(limits.call_args_list, [
                    mock.call(verify.resource.RLIMIT_CPU, (expected_cpu, expected_cpu)),
                    mock.call(verify.resource.RLIMIT_AS, (expected_memory, expected_memory)),
                ])

    def test_strict_json(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                verify.decode(raw)

    def test_exact_scope_and_frozen_identity(self):
        verify.check_manifest(example_manifest())
        for field, value in (("minimum_degree_at_least", 0),
                             ("maximal_triangle_free", False), ("triangle_free", 1)):
            manifest = example_manifest()
            manifest["scope"][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "scope"):
                verify.check_manifest(manifest)
        manifest = example_manifest()
        manifest["files"]["data/proof.lrat"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "frozen"):
            verify.check_manifest(manifest)

    def test_manifest_cannot_add_paths(self):
        for name in ("../outside", "/absolute", "extra.json"):
            manifest = example_manifest()
            manifest["files"][name] = {"bytes": 1, "sha256": "0" * 64}
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "allowlist"):
                verify.check_manifest(manifest)

    def test_inventory_rejects_extra_missing_and_linked_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(ValueError, "incomplete"):
                verify.inventory(root)
            extra = root / "extra"
            extra.write_text("x")
            with self.assertRaisesRegex(ValueError, "unexpected"):
                verify.inventory(root)
            extra.unlink()
            (root / "README.md").symlink_to("missing")
            with self.assertRaisesRegex(ValueError, "nonregular"):
                verify.inventory(root)


class PacketControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if PACKET_ROOT is None:
            raise unittest.SkipTest("supply --packet for exact-artifact controls")
        verify.validate_packet(PACKET_ROOT)

    def copy_packet(self, temporary):
        destination = Path(temporary) / "packet"
        shutil.copytree(PACKET_ROOT, destination)
        return destination

    def test_modified_data_and_sources_rejected_before_import(self):
        for name in ("data/input.json", "data/cuts.json", "data/instance.cnf",
                     "data/proof.lrat", "source/incidence_extension/audit.py"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                root = self.copy_packet(temporary)
                with (root / name).open("ab") as stream:
                    stream.write(b" ")
                with mock.patch.object(verify, "source_modules", side_effect=AssertionError("imported")):
                    with self.assertRaisesRegex(ValueError, "member changed"):
                        verify.verify_packet(root)

    def test_updated_manifest_cannot_replace_frozen_proof(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = self.copy_packet(temporary)
            proof = root / "data/proof.lrat"
            proof.write_bytes(b"1 0 0\n")
            manifest = json.loads((root / "manifest.json").read_text())
            manifest["files"]["data/proof.lrat"] = verify.identity(proof.read_bytes())
            (root / "manifest.json").write_bytes(verify.canonical(manifest) + b"\n")
            with self.assertRaisesRegex(ValueError, "frozen"):
                verify.verify_packet(root)

    def test_both_reconstruction_and_complete_replay_are_required(self):
        budget = types.SimpleNamespace(check=lambda: None)
        support = types.SimpleNamespace(Budget=lambda *_args: budget)
        cnf = (PACKET_ROOT / "data/instance.cnf").read_bytes()
        for rebuilt_bytes, message in ((b"p cnf 1 1\n0\n", "reconstruction"),
                                       (cnf, "proof replay")):
            formula = types.SimpleNamespace(variables=2452, clauses=[None] * 9838,
                                            bytes=lambda: rebuilt_bytes)
            audit = types.SimpleNamespace(reconstruct=lambda *_a, **_k: formula)
            proof = types.SimpleNamespace(verify=lambda *_a: {"python_rup_verified": False})

            @contextmanager
            def fake_sources(_root):
                yield support, audit, proof

            with self.subTest(message=message), mock.patch.object(verify, "source_modules", fake_sources):
                with self.assertRaisesRegex(ValueError, message):
                    verify.verify_packet(PACKET_ROOT)

    def test_complete_replay_uses_no_search_or_process(self):
        original = verify.source_modules

        @contextmanager
        def watched_sources(root):
            with original(root) as (support, audit, proof):
                with mock.patch.object(support.checker, "independent_set", side_effect=AssertionError("search")), \
                     mock.patch.object(support.process, "run_process", side_effect=AssertionError("process")), \
                     mock.patch("subprocess.Popen", side_effect=AssertionError("child")):
                    yield support, audit, proof

        with mock.patch.object(verify, "source_modules", watched_sources):
            result = verify.verify_packet(PACKET_ROOT)
        self.assertEqual(result["status"], "verified")
        self.assertFalse(result["public_sample_count_changed"])
        self.assertEqual(result["scope"]["minimum_degree_at_least"], 6)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path)
    args, remaining = parser.parse_known_args()
    PACKET_ROOT = args.packet
    if PACKET_ROOT is None and (HERE / "manifest.json").is_file():
        PACKET_ROOT = HERE
    unittest.main(argv=[__file__, *remaining])
