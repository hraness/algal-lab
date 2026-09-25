#!/usr/bin/env python3
"""Run cadical with LRAT proof logging on a CNF, check the proof with an independent
checker (lrat-check from marijnheule/drat-trim), and record everything in JSON.

Usage: solve_sat.py file.cnf result.json [--time 7200] [--drat] [--nice 10]
  UNSAT: proof written next to the CNF (.lrat, text format), checked with lrat-check;
         with --drat a binary DRAT proof is produced instead and checked with drat-trim.
  SAT:   the model is decoded into a certificate {"n", "points"} written to result.json.cert.json.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(HERE, "runs", "tools", "drat-trim")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def arg(flag, default, cast=str):
    return cast(sys.argv[sys.argv.index(flag) + 1]) if flag in sys.argv else default


def main():
    cnf, out = sys.argv[1], sys.argv[2]
    limit = arg("--time", 7200, int)
    niceness = arg("--nice", 10, int)
    drat = "--drat" in sys.argv
    head = open(cnf).readline()
    n = int(re.search(r" n=(\d+)", head).group(1))
    k = int(re.search(r"k>=(\d+)", head).group(1))
    proof = cnf[:-4] + (".drat" if drat else ".lrat")
    log = cnf[:-4] + ".cadical.log"
    cmd = ["nice", "-n", str(niceness), "cadical", "-t", str(limit)] + ([] if drat else ["--lrat", "--no-binary"]) + [cnf, proof]
    t0 = time.time()
    with open(log, "w") as lf:
        rc = subprocess.call(cmd, stdout=lf, stderr=subprocess.STDOUT)
    wall = time.time() - t0
    text = open(log).read()
    status = "UNSAT" if rc == 20 else "SAT" if rc == 10 else f"UNKNOWN(rc={rc})"
    res = {"cnf": os.path.basename(cnf), "cnf_sha256": sha256(cnf), "n": n, "k": k, "command": " ".join(cmd),
           "cadical_version": subprocess.run(["cadical", "--version"], capture_output=True, text=True).stdout.strip(),
           "status": status, "solver_wall_seconds": round(wall, 1), "time_limit": limit}
    m = re.search(r"c total process time since initialization:\s+([\d.]+)", text)
    if m:
        res["cadical_process_seconds"] = float(m.group(1))
    if status == "UNSAT":
        res["proof_file"] = os.path.basename(proof)
        res["proof_bytes"] = os.path.getsize(proof)
        res["proof_sha256"] = sha256(proof)
        checker = os.path.join(TOOLS, "drat-trim" if drat else "lrat-check")
        ccmd = ["nice", "-n", str(niceness), checker, cnf, proof]
        t1 = time.time()
        cp = subprocess.run(ccmd, capture_output=True, text=True)
        res["checker_command"] = " ".join(ccmd)
        res["checker_wall_seconds"] = round(time.time() - t1, 1)
        res["checker_exit"] = cp.returncode
        res["checker_output_tail"] = cp.stdout.strip().splitlines()[-6:]
        ok = ("s VERIFIED" in cp.stdout) if drat else ("c VERIFIED" in cp.stdout and "NOT VERIFIED" not in cp.stdout)
        res["proof_verified"] = bool(ok and cp.returncode == 0)
    elif status == "SAT":
        model = set()
        for line in text.splitlines():
            if line.startswith("v "):
                for tok in line.split()[1:]:
                    v = int(tok)
                    if v > 0:
                        model.add(v)
        N = n ** 3
        pts = [[i // (n * n), (i // n) % n, i % n] for i in range(N) if (i + 1) in model]
        cert = {"n": n, "points": pts, "source": f"cadical model of {os.path.basename(cnf)}"}
        cpath = out[:-5] + ".cert.json"
        json.dump(cert, open(cpath, "w"))
        res["certificate"] = os.path.basename(cpath)
        res["certificate_size"] = len(pts)
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps(res))


if __name__ == "__main__":
    main()
