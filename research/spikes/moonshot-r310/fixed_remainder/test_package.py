"""Artifact controls: privacy, tampering, path containment and honest status."""

import importlib.util
import json
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("fixed_remainder_package", Path(__file__).with_name("package.py"))
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class PackageControls(unittest.TestCase):
    def test_build_preserves_stricter_inherited_resource_limits(self):
        script = """
import importlib.util,json,resource,sys
spec=importlib.util.spec_from_file_location('bounded_package',sys.argv[1])
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.apply_build_limits()
print(json.dumps({'file':resource.getrlimit(resource.RLIMIT_FSIZE),
                  'cpu':resource.getrlimit(resource.RLIMIT_CPU)}))
"""

        def inherited_limits():
            resource.setrlimit(resource.RLIMIT_FSIZE, (1024**2, 1024**2))
            resource.setrlimit(resource.RLIMIT_CPU, (3, 3))

        run = subprocess.run([sys.executable, "-B", "-c", script, str(Path(package.__file__))],
                             capture_output=True, text=True, timeout=5, check=False,
                             preexec_fn=inherited_limits)
        self.assertEqual(run.returncode, 0, run.stderr)
        limits = json.loads(run.stdout)
        self.assertEqual(limits["file"], [1024**2, 1024**2])
        self.assertEqual(limits["cpu"], [3, 3])

    def test_projection_preserves_failed_status_and_removes_private_process_fields(self):
        record = {"status": "selector_unsat_unverified", "python_rup_verified": False,
                  "stages": {"audit": {"argv": ["private executable"], "pid": 123,
                                          "status": "complete", "returncode": 1}}}
        result = package.public_record(record, "a" * 64)
        self.assertEqual(result["status"], "selector_unsat_unverified")
        self.assertIs(result["python_rup_verified"], False)
        self.assertEqual(result["stages"], {"audit": {"status": "complete", "returncode": 1}})
        package.privacy_check("result.json", package.json_bytes(result))
        self.assertIn("pid", record["stages"]["audit"])

    def test_privacy_guard_rejects_nested_process_fields_and_home_paths(self):
        with self.assertRaisesRegex(ValueError, "private process field"):
            package.privacy_check("x.json", b'{"nested":[{"pid":123}]}')
        with self.assertRaisesRegex(ValueError, "private path"):
            package.privacy_check("x.py", b"/" + b"Users/example/file")

    def test_missing_success_or_uncollected_child_is_not_accepted(self):
        stage = {"status": "complete", "returncode": 20, "owned_child_collected": True,
                 "external_stop": None, "supervisor_signal": None}
        package.check_stage(stage, 20)
        for changed in ({"returncode": 0}, {"owned_child_collected": False}, {"external_stop": "timeout"}):
            with self.assertRaises(ValueError):
                package.check_stage({**stage, **changed}, 20)

    def test_manifest_rejects_tampering_unlisted_files_and_escaping_names(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "payload.txt").write_bytes(b"exact")
            manifest = {"schema_version": 1, "archive_root": package.ARCHIVE_ROOT,
                        "files": {"payload.txt": package.sha(b"exact")}, "file_bytes": {"payload.txt": 5}}
            (root / "MANIFEST.json").write_bytes(package.json_bytes(manifest))
            self.assertEqual(package.verify_manifest(root)["files_checked"], 1)
            (root / "extra.txt").write_bytes(b"unexpected")
            with self.assertRaisesRegex(ValueError, "unlisted"):
                package.verify_manifest(root)
            (root / "extra.txt").unlink()
            (root / "payload.txt").write_bytes(b"wrong")
            with self.assertRaisesRegex(ValueError, "file changed"):
                package.verify_manifest(root)
            for name in ("../outside", "/outside", "a//b", "a/./b", "a/../b", "a\\b"):
                with self.assertRaises(ValueError):
                    package.safe_name(name)

    def test_bounded_reader_rejects_symlinks_and_oversized_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "regular").write_bytes(b"1234")
            (root / "alias").symlink_to(root / "regular")
            self.assertEqual(package.bounded_bytes(root / "regular", 4), b"1234")
            for path in (root / "alias", root / "regular"):
                with self.assertRaises(ValueError):
                    package.bounded_bytes(path, 3)


if __name__ == "__main__":
    unittest.main()
