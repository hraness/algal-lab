"""Independent controls for interruption and recovery paths."""

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

from encoding import structural_formula
from native import Solver
from run import recorded_cuts, terminate_owned_worker
from search import SearchLimit, search


LIBRARY = os.environ.get("CADICAL_LIBRARY")


@unittest.skipUnless(LIBRARY, "set CADICAL_LIBRARY for native controls")
class NativeInterruptionControls(unittest.TestCase):
    def test_native_requested_interruption_is_unknown(self):
        formula, variables, _ = structural_formula()
        with Solver(LIBRARY, formula.variables, terminate=lambda: True,
                    freeze=variables.values()) as solver:
            for clause in formula.clauses:
                solver.add(clause)
            self.assertEqual(solver.solve(), 0)

    def test_native_callback_exception_fails_closed(self):
        formula, variables, _ = structural_formula()

        def failing_callback():
            raise ValueError("intentional review control")

        with Solver(LIBRARY, formula.variables, terminate=failing_callback,
                    freeze=variables.values()) as solver:
            for clause in formula.clauses:
                solver.add(clause)
            with self.assertRaisesRegex(RuntimeError, "termination callback failed"):
                solver.solve()

    def test_graph_check_interruption_keeps_model_unresolved(self):
        formula, variables, metadata = structural_formula(5, 3, 2, 2)
        events = []
        with patch("search.independent_set", side_effect=SearchLimit("review deadline")):
            result = search(formula, variables, metadata, LIBRARY,
                            stop=lambda: False, event=lambda kind, _: events.append(kind))
        self.assertEqual(result["status"], "graph_check_limit")
        self.assertFalse(result["graph_checked_without_independent_target_set"])
        self.assertFalse(result["unsat_verified"])
        self.assertIsNotNone(result["last_graph"])
        self.assertNotIn("candidate", events)

    def test_supervisor_signals_collect_worker_and_preserve_formula(self):
        driver = Path(__file__).with_name("run.py")
        for signum in (signal.SIGINT, signal.SIGTERM):
            with self.subTest(signal=signum), tempfile.TemporaryDirectory(prefix="r310-review-") as directory:
                output = Path(directory) / "interrupted"
                process = subprocess.Popen(
                    [sys.executable, str(driver), "--library", str(Path(LIBRARY).resolve()),
                     "--output", str(output), "--seconds", "5", "--batch", "16"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                try:
                    deadline = time.monotonic() + 4
                    progress = output / "progress.jsonl"
                    while not (progress.exists() and '"event":"before_solve"' in progress.read_text()):
                        if process.poll() is not None or time.monotonic() >= deadline:
                            self.fail("worker did not reach its supervised solve")
                        time.sleep(0.01)
                    process.send_signal(signum)
                    stdout, stderr = process.communicate(timeout=10)
                finally:
                    if process.poll() is None:
                        terminate_owned_worker(process)
                    process.communicate(timeout=5)
                self.assertEqual(process.returncode, 128 + signum, stderr)
                result = json.loads(stdout)
                self.assertEqual(result["status"], "interrupted_or_error")
                self.assertEqual(result["external_stop"], "supervisor_interrupted")
                self.assertEqual(result["supervisor_signal"], signum)
                self.assertEqual(result["worker_returncode"], -signal.SIGTERM)
                self.assertFalse(result["unsat_verified"])
                self.assertFalse(result["graph_checked_without_independent_target_set"])
                self.assertTrue(result["final_formula_includes_every_complete_recorded_cut"])
                self.assertEqual(json.loads((output / "result.json").read_text()), result)
                lines = (output / "final.cnf").read_text().splitlines()
                self.assertEqual(int(lines[0].split()[3]), len(lines) - 1)
                with self.assertRaises(ProcessLookupError):
                    os.kill(result["worker_pid"], 0)


class RecoveryControls(unittest.TestCase):
    def test_complete_cuts_survive_a_truncated_tail(self):
        masks = [(1 << 10) - 1, ((1 << 10) - 1) << 1]
        entry = {"model": 1, "graph_sha256": "a" * 64, "masks": masks}
        with tempfile.TemporaryDirectory(prefix="r310-review-") as directory:
            path = Path(directory) / "cuts.jsonl"
            path.write_text(json.dumps(entry) + '\n{"model":2,"masks":[')
            self.assertEqual(recorded_cuts(path, 2), (masks, True))
            path.write_text(json.dumps(entry) + "\n" + json.dumps(entry) + "\n")
            with self.assertRaisesRegex(ValueError, "duplicate recorded cut"):
                recorded_cuts(path, 4)

    def test_owned_worker_escalation_and_collection(self):
        class UnresponsiveChild:
            def __init__(self):
                self.actions = []

            def poll(self):
                return None

            def terminate(self):
                self.actions.append("terminate")

            def wait(self, timeout):
                self.actions.append(("wait", timeout))
                if timeout == 2:
                    raise subprocess.TimeoutExpired("owned-child", timeout)
                return -signal.SIGKILL

            def kill(self):
                self.actions.append("kill")

        child = UnresponsiveChild()
        terminate_owned_worker(child)
        self.assertEqual(child.actions, ["terminate", ("wait", 2), "kill", ("wait", 5)])


if __name__ == "__main__":
    unittest.main()
