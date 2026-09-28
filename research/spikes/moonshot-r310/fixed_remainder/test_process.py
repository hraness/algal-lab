"""Actual owned-child termination controls, without a research solver run."""

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from process import run_process, terminate_owned_worker


class ProcessControls(unittest.TestCase):
    def test_wall_and_memory_stops_reap_the_exact_child(self):
        for condition in ("wall", "memory", "monitor"):
            with self.subTest(condition=condition), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                kwargs = {"return_value": 65 * 1024**2} if condition == "memory" else {
                    "side_effect": ValueError("control sample failure")} if condition == "monitor" else {"return_value": 1}
                with patch("process.resident_bytes", **kwargs):
                    result = run_process([sys.executable, "-c", "import time; time.sleep(30)"],
                                         output / "child.log", output / "stage.json",
                                         cpu_seconds=2, wall_seconds=0.3, memory_mib=64)
                self.assertEqual(result["external_stop"], {
                    "wall": "wall_limit", "memory": "memory_threshold", "monitor": "memory_monitor_failed"}[condition])
                self.assertTrue(result["owned_child_collected"])
                with self.assertRaises(ProcessLookupError):
                    os.kill(result["pid"], 0)

    def test_supervisor_signals_collect_worker(self):
        source = str(Path(__file__).resolve().parent)
        for signum in (signal.SIGINT, signal.SIGTERM):
            with self.subTest(signal=signum), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                code = (
                    "import json,sys;from pathlib import Path;"
                    f"sys.path.insert(0,{source!r});from process import run_process;"
                    "p=Path(sys.argv[1]);r=run_process([sys.executable,'-c','import time;time.sleep(30)'],"
                    "p/'child.log',p/'stage.json',cpu_seconds=5,wall_seconds=10);"
                    "print(json.dumps(r));sys.exit(128+r['supervisor_signal'] if r['supervisor_signal'] else 0)"
                )
                supervisor = subprocess.Popen([sys.executable, "-c", code, str(output)],
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                try:
                    deadline = time.monotonic() + 4
                    while True:
                        receipt = output / "stage.json"
                        if receipt.exists() and json.loads(receipt.read_text())["status"] == "running":
                            break
                        if supervisor.poll() is not None or time.monotonic() >= deadline:
                            self.fail("supervised child did not start")
                        time.sleep(0.01)
                    supervisor.send_signal(signum)
                    stdout, stderr = supervisor.communicate(timeout=10)
                finally:
                    if supervisor.poll() is None:
                        terminate_owned_worker(supervisor)
                    supervisor.communicate(timeout=5)
                self.assertEqual(supervisor.returncode, 128 + signum, stderr)
                result = json.loads(stdout)
                self.assertEqual(result["external_stop"], "supervisor_interrupted")
                self.assertTrue(result["owned_child_collected"])
                self.assertEqual(result["supervisor_signal"], signum)
                with self.assertRaises(ProcessLookupError):
                    os.kill(result["pid"], 0)

    def test_unresponsive_owned_child_is_killed_and_waited(self):
        with tempfile.TemporaryDirectory() as directory:
            ready = Path(directory) / "ready"
            child = subprocess.Popen([sys.executable, "-c",
                                      "import signal,time,sys;from pathlib import Path;"
                                      "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
                                      "Path(sys.argv[1]).write_text('ready');time.sleep(30)", str(ready)])
            try:
                deadline = time.monotonic() + 4
                while not ready.exists():
                    if child.poll() is not None or time.monotonic() >= deadline:
                        self.fail("unresponsive control did not start")
                    time.sleep(0.01)
                terminate_owned_worker(child)
                self.assertEqual(child.returncode, -signal.SIGKILL)
            finally:
                if child.poll() is None:
                    child.kill()
                    child.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
