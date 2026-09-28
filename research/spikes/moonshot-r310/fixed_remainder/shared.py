"""Explicit, source-bound access to the already reviewed research helpers."""

import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time

HERE = Path(__file__).resolve().parent
DEPENDENCIES = (
    "degree_six/encoding.py", "degree_six/native.py",
    "degree_four/lrat.py", "vertex_transitive/checker.py",
)


def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, HERE.parent / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cardinality_module = load("degree_six/encoding.py", "_fixed_remainder_cardinality")
native = load("degree_six/native.py", "_fixed_remainder_native")
rup = load("degree_four/lrat.py", "_fixed_remainder_rup")
checker = load("vertex_transitive/checker.py", "_fixed_remainder_graph_checker")
Formula, cardinality = cardinality_module.Formula, cardinality_module.cardinality
SearchLimit = checker.SearchLimit


def digest(path):
    state = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(262144), b""):
            state.update(block)
    return state.hexdigest()


def graph_digest(adj):
    return hashlib.sha256(json.dumps(adj, separators=(",", ":")).encode()).hexdigest()


def peak_bytes():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value if sys.platform == "darwin" else value * 1024


class Budget:
    """Cooperative construction/audit limits, backed by the process supervisor."""

    def __init__(self, seconds=60, memory_mib=1024):
        if not 0 < seconds <= 300 or not 64 <= memory_mib <= 1024:
            raise ValueError("invalid resource budget")
        self.cpu_start, self.wall_start = time.process_time(), time.monotonic()
        self.seconds, self.memory_bytes = seconds, memory_mib * 1024**2

    def check(self):
        if time.process_time() - self.cpu_start >= self.seconds:
            raise SearchLimit("CPU limit")
        if time.monotonic() - self.wall_start >= self.seconds + 30:
            raise SearchLimit("wall limit")
        if peak_bytes() >= self.memory_bytes:
            raise SearchLimit("memory threshold")


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def sources():
    return sorted([str(path.relative_to(HERE.parent)) for path in HERE.glob("*.py")]
                  + list(DEPENDENCIES))


def source_hashes():
    return {relative: digest(HERE.parent / relative) for relative in sources()}
