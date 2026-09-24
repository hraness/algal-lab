"""Run a candidate construction program in a bounded subprocess.

A candidate is Python source defining ``construct(parameters, seed) -> dict``.
It runs with ``python3 -I`` (isolated mode), a wall-clock timeout, an address
space limit, and a bounded output.  The program's output is data: only the
verifier decides what it is worth.
"""

from __future__ import annotations

import json
import os
import resource
import subprocess
import sys
from dataclasses import dataclass

MAX_PROGRAM_BYTES = 16 * 1024
MAX_OUTPUT_BYTES = 1024 * 1024
MAX_STDERR_BYTES = 4 * 1024
MAX_TIMEOUT_SECONDS = 120
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


@dataclass(frozen=True)
class RunResult:
    ok: bool
    construction: object
    error: str
    seconds: float


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
    timeout = min(float(timeout), MAX_TIMEOUT_SECONDS)
    memory_bytes = min(int(memory_bytes), MAX_MEMORY_BYTES)
    payload = json.dumps({"parameters": parameters, "seed": int(seed)})
    import time
    start = time.monotonic()
    try:
        proc = subprocess.run(
            [sys.executable, "-I", "-c", HARNESS, payload],
            input=program.encode(),
            capture_output=True,
            timeout=timeout,
            preexec_fn=_limits(memory_bytes, int(timeout) + 1),
            env={"PATH": os.environ.get("PATH", ""), "PYTHONHASHSEED": "0"},
            check=False,
        )
    except subprocess.TimeoutExpired:
        return RunResult(False, None, f"timeout after {timeout:g}s", time.monotonic() - start)
    seconds = time.monotonic() - start
    stderr = proc.stderr[-MAX_STDERR_BYTES:].decode(errors="replace")
    if proc.returncode != 0:
        return RunResult(False, None, f"exit {proc.returncode}: {stderr.strip()[-600:]}", seconds)
    if len(proc.stdout) > MAX_OUTPUT_BYTES:
        return RunResult(False, None, "output too large", seconds)
    try:
        construction = json.loads(proc.stdout.decode())
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return RunResult(False, None, f"output is not JSON: {exc}", seconds)
    return RunResult(True, construction, "", seconds)
