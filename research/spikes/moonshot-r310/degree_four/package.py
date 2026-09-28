"""Build a deterministic, portable archive of the exact checked proof."""

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pack(run, third_party, output):
    here = Path(__file__).resolve().parent
    if output.exists():
        raise ValueError("output archive already exists")
    result = json.loads((run / "result.json").read_text())
    official = json.loads((run / "lrat-trim-receipt.json").read_text())
    audit = json.loads((run / "independent-audit.json").read_text())
    if (result["status"] != "unsat_verified" or official["status"] != "verified_unsatisfiable"
            or official["returncode"] != 20 or audit["status"] != "independently_verified"
            or not audit["exact_cnf_equivalence"]):
        raise ValueError("missing successful independent verification receipts")
    members = {}

    def add(name, path):
        raw = path.read_bytes()
        if len(raw) > 64 * 1024 * 1024:
            raise ValueError("unexpectedly large artifact")
        members[name] = raw

    for name in ("encode.py", "lrat.py", "solve.py", "test_encoding.py", "independent_audit.py", "package.py", "README.md"):
        add("degree_four/" + name, here / name)
    add("vertex_transitive/checker.py", here.parent / "vertex_transitive/checker.py")
    add("vertex_transitive/README.md", here.parent / "vertex_transitive/README.md")
    add("plan.md", here.parent / "plan.md")
    add("frontier-review-20260928.md", here.parent / "frontier-review-20260928.md")
    license_path = next((parent / "LICENSE" for parent in here.parents if (parent / "LICENSE").is_file()), None)
    if license_path is None:
        raise ValueError("repository license not found")
    add("LICENSE", license_path)
    for name in ("instance.cnf", "instance.json", "proof.lrat", "solver.log", "lrat-trim.log",
                 "lrat-trim-receipt.json", "independent-audit.json"):
        add("evidence/" + name, run / name)
    for name in ("lrat-trim.c", "LICENSE", "README.md"):
        add("third-party/lrat-trim/" + name, third_party / name)

    for name, field in (("instance.cnf", "cnf_sha256"), ("proof.lrat", "proof_sha256")):
        actual = sha(members["evidence/" + name])
        if any(receipt[field] != actual for receipt in (result, official, audit)):
            raise ValueError("formula/proof receipt mismatch")
    for name, expected in result["source_sha256"].items():
        if sha(members["degree_four/" + name]) != expected:
            raise ValueError("solver-run source drift")
    if sha(members["degree_four/independent_audit.py"]) != audit["reviewer_script_sha256"]:
        raise ValueError("independent audit source drift")
    if sha(members["third-party/lrat-trim/lrat-trim.c"]) != official["source_sha256"]:
        raise ValueError("established checker source drift")
    if sha(members["third-party/lrat-trim/LICENSE"]) != official["license_sha256"]:
        raise ValueError("established checker license drift")
    if (sha(members["evidence/solver.log"]) != result["solver_log_sha256"]
            or sha(members["evidence/lrat-trim.log"]) != official["log_sha256"]):
        raise ValueError("verification log drift")

    # Preserve exact formula/proof/source identities without publishing local
    # user-directory or executable-installation paths. No proof bytes change.
    result["solver_argv"] = ["cadical", *result["solver_argv"][1:-2], "instance.cnf", "proof.lrat"]
    result["receipt_note"] = "Local absolute paths were replaced by portable names; all artifact and binary digests are unchanged."
    members["evidence/result.json"] = (json.dumps(result, indent=2) + "\n").encode()
    members["README.md"] = b"""# A checked degree-four exclusion for (3,10,40) graphs

This bundle supports the claim that every triangle-free graph on 40 vertices
with independence number at most 9 has minimum degree at least 5. It does not
settle R(3,10), and no publication-priority claim is made. The mathematical
reduction and its published uniqueness premise are in degree_four/README.md.
All source, formula, proof and receipt files are hashed in MANIFEST.json.
The repository source is MIT licensed; the third-party checker has its own
included MIT license. No solver or checker executable is needed from the
original machine.

From this extracted directory, inspect the report and run:

```sh
python3 -m unittest discover -s degree_four -p 'test_*.py'
python3 degree_four/encode.py --output regenerated
shasum -a 256 regenerated/instance.cnf evidence/instance.cnf
python3 degree_four/lrat.py evidence/instance.cnf evidence/proof.lrat
python3 -O degree_four/independent_audit.py evidence
clang -std=c11 -O2 -Wall -Wextra third-party/lrat-trim/lrat-trim.c -o lrat-trim
./lrat-trim --no-trim evidence/instance.cnf evidence/proof.lrat
```

The two CNF digests must agree. Both Python checks must succeed; lrat-trim
must print `s VERIFIED` and exit with code 20. The established checker source
is arminbiere/lrat-trim commit b30f400f4ee5c32b77ee566a7c006081b521534f.
All checks use the saved proof, so the solver itself need not be trusted.
Timing values describe the original execution and will vary by machine.
"""
    manifest = {"schema_version": 1, "result": "minimum_degree_at_least_5",
                "graph_order": 40, "triangle_free": True, "maximum_independence_number": 9,
                "ramsey_number_settled": False, "novelty_claimed": False,
                "cnf_sha256": result["cnf_sha256"], "proof_sha256": result["proof_sha256"],
                "files": {name: sha(raw) for name, raw in sorted(members.items())}}
    members["MANIFEST.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    for name, raw in members.items():
        if not name.endswith(".py") and (b"/Users/" in raw or b"/private/tmp/" in raw):
            raise ValueError("private machine path in archive member: " + name)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as destination:
        with gzip.GzipFile(fileobj=destination, filename="", mode="wb", mtime=0, compresslevel=9) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as archive:
                for name, raw in sorted(members.items()):
                    entry = tarfile.TarInfo("r310-degree-four-proof/" + name)
                    entry.size = len(raw)
                    entry.mode = 0o644
                    entry.mtime = 0
                    archive.addfile(entry, io.BytesIO(raw))
    digest = sha(output.read_bytes())
    output.with_name(output.name + ".sha256").write_text(digest + "  " + output.name + "\n")
    return {"archive": str(output), "bytes": output.stat().st_size, "sha256": digest,
            "members": len(members), "cnf_sha256": result["cnf_sha256"], "proof_sha256": result["proof_sha256"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("third_party", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(pack(args.run_dir, args.third_party, args.output), indent=2))
