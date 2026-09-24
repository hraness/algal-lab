"""Run a candidate construction program in a bounded subprocess.

A candidate is Python source defining ``construct(parameters, seed) -> dict``.
It runs with ``python3 -I`` (isolated mode) in a fresh temporary working
directory with a wall-clock timeout, a CPU-time limit, an address-space limit
where the platform enforces one, and a bounded output.  On macOS the process
additionally runs under ``sandbox-exec`` with a profile that denies network
access and every file write outside the temporary directory; elsewhere the
run is resource-limited only, and the result records which mode applied.
This is a containment measure for programs written by the loop's own
operators, not a boundary for hostile code.  The program's output is data:
only the verifier decides what it is worth.
"""

from __future__ import annotations

import json
import os
import resource
import subprocess
import shutil
import sys
import tempfile
from dataclasses import dataclass

MAX_PROGRAM_BYTES = 16 * 1024
MAX_OUTPUT_BYTES = 1024 * 1024
MAX_STDERR_BYTES = 4 * 1024
MAX_TIMEOUT_SECONDS = 600
MAX_MEMORY_BYTES = 2 * 1024**3

HARNESS = r'''
import json, sys, random
source = sys.stdin.read()
payload = json.loads(sys.argv[1])
namespace = {"__name__": "candidate"}
exec(compile(source, "<candidate>", "exec"), namespace)
construct = namespace.get("construct")
if not callable(construct):
    raise SystemExit("candidate defines no construct(parameters, seed)")
random.seed(payload["seed"])
result = construct(payload["parameters"], payload["seed"])
sys.stdout.write(json.dumps(result, separators=(",", ":")))
'''


SANDBOX_PROFILE = """(version 1)
(deny default)
(allow process-exec)
(allow process-fork)
(allow file-read*)
(allow file-write* (subpath "{work}"))
(allow file-write* (subpath "/dev"))
(allow sysctl-read)
(allow mach-lookup)
(allow signal (target self))
(deny network*)
"""


def isolation_mode() -> str:
    """Name of the containment applied by run_program on this host."""
    if sys.platform == "darwin" and shutil.which("sandbox-exec"):
        return "sandbox-exec+rlimit"
    return "rlimit-only"


@dataclass(frozen=True)
class RunResult:
    ok: bool
    construction: object
    error: str
    seconds: float
    isolation: str = "rlimit-only"


def _limits(memory_bytes: int, cpu_seconds: int):
    def apply():
        try:
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        except (ValueError, OSError):
            pass
        try:
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        except (ValueError, OSError):
            pass
    return apply


def run_program(program: str, parameters: dict, seed: int, timeout: float = 30.0,
                memory_bytes: int = 1024**3) -> RunResult:
    if not isinstance(program, str) or len(program.encode()) > MAX_PROGRAM_BYTES:
        return RunResult(False, None, "program too large or not text", 0.0)
    timeout = float(timeout)
    if not 0 < timeout <= MAX_TIMEOUT_SECONDS:
        raise ValueError(f"timeout must be in (0, {MAX_TIMEOUT_SECONDS}] seconds")
    memory_bytes = min(int(memory_bytes), MAX_MEMORY_BYTES)
    payload = json.dumps({"parameters": parameters, "seed": int(seed)})
    mode = isolation_mode()
    import time
    start = time.monotonic()
    work = tempfile.mkdtemp(prefix="extremal-")
    try:
        command = [sys.executable, "-I", "-c", HARNESS, payload]
        if mode == "sandbox-exec+rlimit":
            profile = os.path.join(work, "profile.sb")
            with open(profile, "w", encoding="utf-8") as handle:
                handle.write(SANDBOX_PROFILE.format(work=os.path.realpath(work)))
            command = ["sandbox-exec", "-f", profile] + command
        try:
            proc = subprocess.run(
                command,
                input=program.encode(),
                capture_output=True,
                timeout=timeout,
                cwd=work,
                preexec_fn=_limits(memory_bytes, int(timeout) + 1),
                env={"PATH": os.environ.get("PATH", ""), "PYTHONHASHSEED": "0", "TMPDIR": work},
                check=False,
            )
        except subprocess.TimeoutExpired:
            return RunResult(False, None, f"timeout after {timeout:g}s", time.monotonic() - start, mode)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    seconds = time.monotonic() - start
    stderr = proc.stderr[-MAX_STDERR_BYTES:].decode(errors="replace")
    if proc.returncode != 0:
        return RunResult(False, None, f"exit {proc.returncode}: {stderr.strip()[-600:]}", seconds, mode)
    if len(proc.stdout) > MAX_OUTPUT_BYTES:
        return RunResult(False, None, "output too large", seconds, mode)
    try:
        construction = json.loads(proc.stdout.decode())
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        return RunResult(False, None, f"output is not JSON: {str(exc)[:200]}", seconds, mode)
    return RunResult(True, construction, "", seconds, mode)
