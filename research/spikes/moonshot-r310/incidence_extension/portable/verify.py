"""Replay one fixed, published incidence-extension proof using only the stdlib."""

import argparse
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import resource
import signal
import stat
import sys

sys.dont_write_bytecode = True
PACKET = "ramsey-incidence-sample19-v1"
PROFILE = "fixed-h-six-incidence-v1"
RAW_SHA256 = "159658dd5992a1c1ab00a12917328c9d216cd7ab99e4cc76d5b6d5c6a0ec0fb3"
SCOPE = {
    "order": 40, "triangle_free": True, "maximal_triangle_free": True,
    "independence_number_at_most": 9, "minimum_degree_at_least": 6,
    "distinguished_centre_degree": 6, "remainder_order": 33,
    "exact_induced_remainder_adjacency_sha256": RAW_SHA256,
}
# Exact bytes from the accepted pilot. These identities are not supplied by the
# packet manifest, so editing the manifest cannot substitute another instance.
FROZEN = {
    "data/input.json": (339, "26ac4e5d1b7cf895a98f92b13cb39e0fb78fcbdd0c85f549613d216aebe43323"),
    "data/cuts.json": (4283, "fda4dbe1d34c4782e442f5d5ae4c264e78d9b90a1cfaefbf8be135beef7ff811"),
    "data/instance.cnf": (152836, "ab7ed48b0ebb8c2aa47778fdbb5f12f7a7285f0635efc288d3647079bd52326a"),
    "data/proof.lrat": (188141, "9b8df3dae71e877e43b7cce88b78068f98d4cb120a2fe60f59aeed026be2ad02"),
    "data/instance.json": (557, "4567384d0d7ecfa1645a4a734f6df84f150da5da3ec545d3322c2ff8486f9964"),
    "source/degree_four/lrat.py": (6216, "8db2970f7a97494c605cadd53f6b5b417ccad1974f58c296d175e086b857ff4a"),
    "source/degree_six/encoding.py": (8709, "525808c8cb36924c35b5c35cc47055a11976dc20465a22b4be04c921edc6545b"),
    "source/fixed_remainder/process.py": (6312, "72f269e0506a2ea57bb3f73d2ae622aeb51470410ce4319de8586fe410bbbc76"),
    "source/incidence_extension/PROFILE.md": (7364, "f5bbc3abb211e39e69588f33cd4e178e0bc68e9d232598fe13ba9aa48fb815ee"),
    "source/incidence_extension/audit.py": (10865, "f23e8d046f3cae6d3d95c3b9058c09471428d151e2b67b79c7424c2f666ced7d"),
    "source/incidence_extension/encode.py": (6341, "0f465ecc2fcf9f2d144b10617c46ef63f76c0662cd0a01cfae791c79e388051b"),
    "source/incidence_extension/proof.py": (5114, "e615b5f24c26efb7e20730d209f299be3a916e25f5b2ffe5257366b0f6b565d2"),
    "source/incidence_extension/run.py": (20625, "ab6b674f47f763a61fe2b1c13c5cd34a111215ad4f4d9a40af80a23212f0e01c"),
    "source/incidence_extension/support.py": (4625, "1a71156ddbbacf09944691805be93d0b94fc93bcc38c85f981edfcbef90490dc"),
    "source/incidence_extension/test_focused.py": (11681, "80e6bff51c9fbfe43c83841cd4e0507a686ac26234fdca347c45db8cdfe41bad"),
    "source/vertex_transitive/checker.py": (4287, "aecfd40ba0e6cda88b72a66c8c03431e1d07301fc4f1665739b7f8e2c0ac5bf1"),
}
PAYLOAD = set(FROZEN) | {"verify.py", "test_verify.py", "README.md", "LICENSE"}
MEMBERS = PAYLOAD | {"manifest.json"}
DIRECTORIES = {str(parent) for name in MEMBERS for parent in Path(name).parents
               if str(parent) != "."}
MAX_FILE_BYTES = 256 * 1024
MAX_PACKET_BYTES = 1024 * 1024
PROVENANCE = {
    "historical_source_review_sha256": "ad797ed8c68240b1839224be485054b6f657efe445afab0b15256f9deb179de7",
    "historical_input_manifest_sha256": "14cc659a147d94ea28536db026b7e2a8e4366bb3a5f1aa4034197938ad308bc9",
    "historical_result_review_sha256": "930b919830db5d97ffbc1f81f90e265d1ef15417baea8824212a7e7a66b16bf4",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def decode(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON field")
            result[key] = value
        return result

    def constant(_value):
        raise ValueError("nonfinite JSON value")

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def read_bytes(path, limit=MAX_FILE_BYTES):
    require(stat.S_ISREG(path.lstat().st_mode), "nonregular packet member")
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    require(len(raw) <= limit, "packet file byte limit")
    return raw


def identity(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def manifest_header():
    return {
        "schema_version": 1, "packet": PACKET, "profile": PROFILE,
        "sample_index": 19, "scope": SCOPE,
        "conclusion": "no_graph_satisfies_the_stated_conditions",
        "public_sample_count": {"excluded": 113, "total": 128, "changed": False},
        "new_ramsey_bound": False, "provenance": PROVENANCE,
        "manifest_checksum": "detached_SHA256SUMS",
    }


def check_manifest(manifest):
    require(type(manifest) is dict, "manifest must be an object")
    header = manifest_header()
    require(set(manifest) == set(header) | {"files"}, "manifest fields")
    # Canonical JSON distinguishes true from 1 and false from 0.
    require(canonical({k: manifest[k] for k in header}) == canonical(header),
            "manifest scope or provenance differs")
    files = manifest["files"]
    require(type(files) is dict and set(files) == PAYLOAD, "manifest member allowlist")
    for name, metadata in files.items():
        require(type(metadata) is dict and set(metadata) == {"bytes", "sha256"}, "file metadata fields")
        size, digest = metadata["bytes"], metadata["sha256"]
        require(type(size) is int and 0 < size <= MAX_FILE_BYTES, "file size metadata")
        require(type(digest) is str and len(digest) == 64
                and all(c in "0123456789abcdef" for c in digest), "file digest metadata")
        if name in FROZEN:
            require((size, digest) == FROZEN[name], "frozen artifact identity differs")


def inventory(root):
    require(root.is_dir() and not root.is_symlink(), "packet root must be a directory")
    found, total = set(), 0
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in dirs:
            path = Path(directory) / name
            require(not path.is_symlink() and str(path.relative_to(root)) in DIRECTORIES,
                    "unexpected or linked packet directory")
        for name in files:
            path = Path(directory) / name
            relative = path.relative_to(root).as_posix()
            require(relative in MEMBERS, "unexpected packet member")
            size = path.lstat().st_size
            require(stat.S_ISREG(path.lstat().st_mode) and size <= MAX_FILE_BYTES,
                    "nonregular or oversized packet member")
            found.add(relative)
            total += size
            require(total <= MAX_PACKET_BYTES, "packet byte limit")
    require(found == MEMBERS, "incomplete packet")


def validate_packet(root):
    root = Path(root)
    inventory(root)
    manifest = decode(read_bytes(root / "manifest.json", 32 * 1024))
    check_manifest(manifest)
    for name, expected in manifest["files"].items():
        require(identity(read_bytes(root / name)) == expected, "packet member changed: " + name)
    require(read_bytes(root / "verify.py") == read_bytes(Path(__file__)), "replay program differs")
    return manifest


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextmanager
def source_modules(root):
    directory = root / "source" / "incidence_extension"
    previous = sys.modules.get("support")
    try:
        support = load(directory / "support.py", "_packet_support")
        sys.modules["support"] = support
        audit = load(directory / "audit.py", "_packet_audit")
        proof = load(directory / "proof.py", "_packet_proof")
        yield support, audit, proof
    finally:
        if previous is None:
            sys.modules.pop("support", None)
        else:
            sys.modules["support"] = previous


def verify_packet(root):
    root = Path(root)
    validate_packet(root)  # Check every source identity before importing it.
    raw = decode(read_bytes(root / "data/input.json"))
    cuts = decode(read_bytes(root / "data/cuts.json"))
    require(hashlib.sha256(canonical(raw)).hexdigest() == RAW_SHA256
            and type(raw) is list and len(raw) == 33, "raw graph identity")
    require(type(cuts) is list and len(cuts) == 7, "cut count")
    with source_modules(root) as (support, audit, proof):
        budget = support.Budget(10, 256)
        budget.check()
        rebuilt = audit.reconstruct(raw, cuts, m=6, r=9, minimum=6, ordered=True)
        budget.check()
        require(rebuilt.variables == 2452 and len(rebuilt.clauses) == 9838
                and rebuilt.bytes() == read_bytes(root / "data/instance.cnf"),
                "independent CNF reconstruction failed")
        replay = proof.verify(root / "data/instance.cnf", root / "data/proof.lrat", budget)
        expected = {
            "profile": PROFILE, "python_rup_verified": True, "initial_clauses": 9838,
            "additions": 2326, "deletions": 4144, "lines": 3231,
            "cnf_sha256": FROZEN["data/instance.cnf"][1],
            "proof_sha256": FROZEN["data/proof.lrat"][1],
        }
        require(canonical(replay) == canonical(expected), "incomplete or different proof replay")
        budget.check()
    validate_packet(root)  # Also bind the bytes present when verification ends.
    return {"status": "verified", "packet": PACKET, "scope": SCOPE,
            "variables": 2452, "clauses": 9838, "cuts_checked": 7,
            "proof_replay": replay, "public_sample_count_changed": False,
            "new_ramsey_bound": False, "solver_or_graph_search_run": False}


def cli_limits():
    """Limit this replay process; never launch or signal a child."""
    def lower_limit(kind, requested):
        inherited = resource.getrlimit(kind)
        limit = min([requested] + [value for value in inherited
                                   if value != resource.RLIM_INFINITY])
        resource.setrlimit(kind, (limit, limit))

    usage = resource.getrusage(resource.RUSAGE_SELF)
    requested = math.ceil(usage.ru_utime + usage.ru_stime) + 10
    lower_limit(resource.RLIMIT_CPU, requested)
    if sys.platform.startswith("linux"):
        lower_limit(resource.RLIMIT_AS, 256 * 1024**2)

    def expired(_signum, _frame):
        raise TimeoutError("30-second replay wall limit")

    signal.signal(signal.SIGALRM, expired)
    signal.alarm(30)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path, nargs="?", default=Path(__file__).parent)
    args = parser.parse_args()
    try:
        cli_limits()
        result = verify_packet(args.packet)
    except Exception as error:
        print(json.dumps({"status": "not_verified", "reason": str(error)}), file=sys.stderr)
        return 1
    finally:
        signal.alarm(0)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
