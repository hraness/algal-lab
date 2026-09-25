#!/usr/bin/env python3
"""Collect the round-27 manifest: SHA-256 of every committed script, every generated
hypergraph, CNF, proof and result file under runs/, tool versions and host facts.
Usage: manifest.py manifest.json"""
import glob
import hashlib
import json
import os
import platform
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception as e:  # noqa: BLE001
        return f"error: {e}"


def main():
    out = sys.argv[1]
    files = {}
    for pattern in ("*.py", "*.c", "certificates/*.json", "runs/*.json", "runs/*.cnf", "runs/*.lrat", "runs/*.drat",
                    "runs/*.sets", "runs/*.log", "runs/*.sh", "runs/lb/*"):
        for p in sorted(glob.glob(os.path.join(HERE, pattern))):
            rel = os.path.relpath(p, HERE)
            files[rel] = {"sha256": sha256(p), "bytes": os.path.getsize(p)}
    py = sys.executable
    tools = {
        "python": run([py, "--version"]),
        "cadical": run(["cadical", "--version"]),
        "kissat": run(["kissat", "--version"]),
        "ortools": run([py, "-c", "import ortools; print(ortools.__version__)"]),
        "pysat": run([py, "-c", "import pysat; print(pysat.__version__)"]),
        "numpy": run([py, "-c", "import numpy; print(numpy.__version__)"]),
        "cc": run(["cc", "--version"]).splitlines()[0] if run(["cc", "--version"]) else "",
        "drat-trim_commit": run(["git", "-C", os.path.join(HERE, "runs", "tools", "drat-trim"), "rev-parse", "HEAD"]),
        "drat-trim_remote": "https://github.com/marijnheule/drat-trim",
    }
    repo_verifier = os.path.join(HERE, "..", "..", "..", "..", "extremal", "verifiers", "no_five_on_sphere.py")
    manifest = {
        "contract": "algal.lab.round27-no-five-exact-manifest.v1",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "host": {"platform": platform.platform(), "machine": platform.machine(), "cpu_count": os.cpu_count(),
                 "loadavg_at_generation": os.getloadavg()},
        "tools": tools,
        "repo_verifier_sha256": sha256(os.path.abspath(repo_verifier)),
        "git_head": run(["git", "-C", HERE, "rev-parse", "HEAD"]),
        "files": files,
    }
    json.dump(manifest, open(out, "w"), indent=1)
    print("wrote", out, len(files), "files")


if __name__ == "__main__":
    main()
