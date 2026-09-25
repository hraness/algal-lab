#!/usr/bin/env python3
"""Cube-and-conquer driver with one checked LRAT proof per cube.

Cubes are assignments to a prefix of the point variables 1..m; the 2^m initial cubes are
exhaustive by construction, and a cube that times out is split on the next variable into
two children, so the leaves always partition the assignment space. Each leaf cube is
solved by cadical on (base CNF + unit clauses) with LRAT logging; an UNSAT answer is
checked by lrat-check; a SAT answer stops the run and is reported with its model.
The base formula is UNSAT iff every leaf is checked UNSAT.

Usage: cube_solve.py base.cnf outdir [--vars 6] [--workers 2] [--cpu 900] [--wall 7200]
       [--nice 10] [--keep-proofs] [--max-depth 40] [--split-vars v1,v2,...]
The split variables default to the last point variables in decreasing order: under the
lex-leader symmetry breaking the orbit representative packs its points towards high
indices, so those variables are the informative ones.
"""
import hashlib
import json
import os
import queue
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKER = os.path.join(HERE, "runs", "tools", "drat-trim", "lrat-check")


def arg(flag, default, cast=str):
    return cast(sys.argv[sys.argv.index(flag) + 1]) if flag in sys.argv else default


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    base, outdir = sys.argv[1], sys.argv[2]
    m0 = arg("--vars", 6, int)
    workers = arg("--workers", 2, int)
    cpu = arg("--cpu", 900, int)
    wall = arg("--wall", 7200, int)
    niceness = arg("--nice", 10, int)
    keep = "--keep-proofs" in sys.argv
    keep_max = arg("--keep-max-bytes", 300_000_000, int)
    max_depth = arg("--max-depth", 40, int)
    split_vars = [int(v) for v in arg("--split-vars", "", str).split(",") if v]
    os.makedirs(outdir, exist_ok=True)
    with open(base) as f:
        lines = f.readlines()
    hdr = [i for i, l in enumerate(lines) if l.startswith("p cnf")][0]
    nv, nc = map(int, lines[hdr].split()[2:4])
    body = "".join(lines[hdr + 1:])
    comments = "".join(lines[:hdr])
    base_sha = sha256(base)
    log = open(os.path.join(outdir, "cubes.jsonl"), "a")
    lock = threading.Lock()
    q = queue.Queue()
    if not split_vars:
        split_vars = list(range(nv, 0, -1))  # default: from the last variable downwards
    for bits in range(1 << m0):
        cube = tuple(split_vars[v] if (bits >> v) & 1 else -split_vars[v] for v in range(m0))
        q.put(cube)
    state = {"pending": 1 << m0, "unsat": 0, "sat": None, "split": 0, "cpu_total": 0.0, "proof_bytes": 0, "check_wall": 0.0}
    t0 = time.time()

    def name(cube):
        return "c" + "".join("1" if l > 0 else "0" for l in cube)

    def run(cube):
        cid = name(cube)
        cnf = os.path.join(outdir, cid + ".cnf")
        proof = os.path.join(outdir, cid + ".lrat")
        with open(cnf, "w") as f:
            f.write(comments)
            f.write(f"c cube {' '.join(map(str, cube))} base_sha256={base_sha}\n")
            f.write(f"p cnf {nv} {nc + len(cube)}\n")
            f.write(body)
            for l in cube:
                f.write(f"{l} 0\n")
        cmd = f"ulimit -t {cpu}; exec nice -n {niceness} cadical -q -t {wall} --lrat --no-binary {cnf} {proof}"
        t1 = time.time()
        cp = subprocess.run(["/bin/zsh", "-c", cmd], capture_output=True, text=True)
        wall_used = time.time() - t1
        rec = {"cube": cube, "id": cid, "rc": cp.returncode, "wall": round(wall_used, 1)}
        if cp.returncode == 20:
            t2 = time.time()
            ck = subprocess.run(["nice", "-n", str(niceness), CHECKER, cnf, proof], capture_output=True, text=True)
            ok = ck.returncode == 0 and "c VERIFIED" in ck.stdout and "NOT VERIFIED" not in ck.stdout
            rec.update({"status": "UNSAT", "proof_bytes": os.path.getsize(proof), "proof_sha256": sha256(proof),
                        "verified": ok, "check_wall": round(time.time() - t2, 1), "cnf_sha256": sha256(cnf)})
            if not ok:
                rec["checker_tail"] = ck.stdout.strip().splitlines()[-5:]
        elif cp.returncode == 10:
            model = [int(t) for line in cp.stdout.splitlines() if line.startswith("v ") for t in line.split()[1:]]
            rec.update({"status": "SAT", "model_true": [v for v in model if v > 0]})
        else:
            rec["status"] = "TIMEOUT"
        os.remove(cnf)
        if os.path.exists(proof) and (not keep or rec["status"] != "UNSAT" or os.path.getsize(proof) > keep_max):
            os.remove(proof)
            rec["proof_kept"] = False
        else:
            rec["proof_kept"] = True
        return rec

    def wanted():
        try:
            return int(open(os.path.join(outdir, "workers")).read().strip())
        except Exception:  # noqa: BLE001
            return workers

    def worker(idx):
        while True:
            if idx >= wanted():
                return
            try:
                cube = q.get(timeout=2)
            except queue.Empty:
                with lock:
                    if state["pending"] == 0 or state["sat"]:
                        return
                continue
            rec = run(cube)
            with lock:
                log.write(json.dumps(rec) + "\n")
                log.flush()
                if rec["status"] == "UNSAT" and rec["verified"]:
                    state["unsat"] += 1
                    state["proof_bytes"] += rec["proof_bytes"]
                    state["check_wall"] += rec["check_wall"]
                elif rec["status"] == "SAT":
                    state["sat"] = rec
                elif rec["status"] == "UNSAT":
                    state["sat"] = {"status": "CHECK FAILED", "cube": cube}
                else:
                    if len(cube) >= max_depth:
                        state["sat"] = {"status": "DEPTH LIMIT", "cube": cube}
                    else:
                        state["split"] += 1
                        nxt = split_vars[len(cube)]
                        q.put(cube + (nxt,))
                        q.put(cube + (-nxt,))
                        state["pending"] += 2
                state["pending"] -= 1
                done = state["unsat"]
                print(f"[{time.time()-t0:7.0f}s] {rec['id']} {rec['status']} wall={rec['wall']} pending={state['pending']} unsat={done} split={state['split']}", flush=True)
            q.task_done()

    threads = {}
    while True:
        with lock:
            finished = state["pending"] == 0 or state["sat"] is not None
        if finished:
            break
        for idx in range(wanted()):
            if idx not in threads or not threads[idx].is_alive():
                threads[idx] = threading.Thread(target=worker, args=(idx,), daemon=True)
                threads[idx].start()
        time.sleep(5)
    for t in threads.values():
        t.join()
    summary = {"base": os.path.basename(base), "base_sha256": base_sha, "initial_vars": m0, "split_vars": split_vars[:max_depth], "workers": workers,
               "cpu_cap": cpu, "wall_cap": wall, "leaves_unsat_verified": state["unsat"], "splits": state["split"],
               "result": "UNSAT" if state["sat"] is None and state["pending"] == 0 else state["sat"],
               "total_proof_bytes": state["proof_bytes"], "total_check_wall": round(state["check_wall"], 1),
               "wall_seconds": round(time.time() - t0, 1)}
    json.dump(summary, open(os.path.join(outdir, "summary.json"), "w"), indent=1)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
