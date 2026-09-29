"""Frozen dependencies and bounded I/O for the 198-incidence pilot."""

import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import shutil
import sys
import time
import types

HERE = Path(__file__).resolve().parent
PROFILE = "fixed-h-six-incidence-v1"
MAX_VARIABLES, MAX_CLAUSES = 10_000, 60_000
MAX_CNF_BYTES, MAX_PROOF_BYTES = 2 * 1024**2, 128 * 1024**2
MAX_RUN_BYTES, MAX_JSON_BYTES = 256 * 1024**2, 4 * 1024**2
MAX_ROUNDS, MAX_CUTS, INDEPENDENT_NODES = 64, 63, 500_000
DEPENDENCIES = ("degree_six/encoding.py", "degree_four/lrat.py",
                "vertex_transitive/checker.py", "fixed_remainder/process.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, HERE.parent / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


encoding = load("degree_six/encoding.py", "_ie_encoding")
checker = load("vertex_transitive/checker.py", "_ie_graph_checker")
rup = load("degree_four/lrat.py", "_ie_rup")
Formula, cardinality, SearchLimit = encoding.Formula, encoding.cardinality, checker.SearchLimit


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(262_144), b""):
            h.update(block)
    return h.hexdigest()


def canonical(value):
    return json.dumps(value, separators=(",", ":"), allow_nan=False).encode()


def object_digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def decode(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON field")
            result[key] = value
        return result

    def constant(value):
        raise ValueError("nonfinite JSON constant: " + value)

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def read_json(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_JSON_BYTES + 1)
    require(len(raw) <= MAX_JSON_BYTES, "JSON byte limit")
    return decode(raw)


def write_json(path, value):
    path = Path(path)
    raw = canonical(value) + b"\n"
    require(len(raw) <= MAX_JSON_BYTES, "JSON byte limit")
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(raw)
    temporary.replace(path)


previous_shared = sys.modules.get("shared")
try:
    sys.modules["shared"] = types.SimpleNamespace(digest=digest, write_json=write_json)
    process = load("fixed_remainder/process.py", "_ie_process")
finally:
    if previous_shared is None:
        sys.modules.pop("shared", None)
    else:
        sys.modules["shared"] = previous_shared


def total_cpu():
    values = [resource.getrusage(which) for which in (resource.RUSAGE_SELF, resource.RUSAGE_CHILDREN)]
    return sum(value.ru_utime + value.ru_stime for value in values)


class Budget:
    def __init__(self, seconds=60, memory_mib=896):
        require(type(seconds) in (int, float) and 0 < seconds <= 60
                and type(memory_mib) is int and 64 <= memory_mib <= 896, "unsupported budget")
        self.start, self.wall_start = total_cpu(), time.monotonic()
        self.seconds, self.memory_mib = seconds, memory_mib

    @property
    def deadline(self):
        return self.wall_start + self.seconds + 20

    def check(self):
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        peak *= 1 if sys.platform == "darwin" else 1024
        if total_cpu() - self.start >= self.seconds:
            raise SearchLimit("shared CPU allowance")
        if time.monotonic() >= self.deadline:
            raise SearchLimit("wall allowance")
        if peak >= self.memory_mib * 1024**2:
            raise SearchLimit("memory allowance")


def disk_bytes(path):
    return sum(p.stat().st_size for p in Path(path).rglob("*") if p.is_file())


def source_hashes():
    paths = sorted([str(p.relative_to(HERE.parent)) for p in HERE.glob("*.py")]
                   + ["incidence_extension/PROFILE.md"] + list(DEPENDENCIES))
    return {relative: digest(HERE.parent / relative) for relative in paths}


def snapshot(output):
    hashes = source_hashes()
    for relative, expected in hashes.items():
        destination = Path(output) / "source" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE.parent / relative, destination)
        require(digest(destination) == digest(HERE.parent / relative) == expected, "source changed")
    return hashes
