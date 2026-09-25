#!/usr/bin/env python3
"""CP-SAT model: maximise |S| subject to the exact degenerate-set hypergraph constraints.

Usage: solve_cpsat.py hg.json out.json [--sym] [--workers 4] [--time 7200] [--hint cert.json] [--lb K]
"""
import hashlib
import json
import sys
import time

from ortools.sat.python import cp_model

sys.path.insert(0, __import__("os").path.dirname(__file__))
from hypergraph import symmetries  # noqa: E402


def arg(flag, default, cast=str):
    return cast(sys.argv[sys.argv.index(flag) + 1]) if flag in sys.argv else default


def main():
    hg_path, out = sys.argv[1], sys.argv[2]
    sym = "--sym" in sys.argv
    workers = arg("--workers", 4, int)
    limit = arg("--time", 7200.0, float)
    hint = arg("--hint", None)
    lb = arg("--lb", 5, int)
    hg = json.load(open(hg_path))
    n = hg["n"]
    N = n ** 3
    m = cp_model.CpModel()
    x = [m.NewBoolVar(f"x{i}") for i in range(N)]
    for s in hg["at_most_4"]:
        m.Add(sum(x[p] for p in s) <= 4)
    for s in hg["at_most_3"]:
        m.Add(sum(x[p] for p in s) <= 3)
    m.Add(sum(x) >= max(lb, 5))  # the circle/line bounds are implied only for |S| >= 5
    naux = 0
    if sym:
        for perm in symmetries(n):
            if all(perm[p] == p for p in range(N)):
                continue
            e_prev = None
            for p in range(N):
                q = perm[p]
                if q == p:
                    continue
                pre = [e_prev.Not()] if e_prev is not None else []
                m.AddBoolOr(pre + [x[p].Not(), x[q]])
                e = m.NewBoolVar(f"e{naux}")
                naux += 1
                m.AddBoolOr(pre + [x[p].Not(), x[q].Not(), e])
                m.AddBoolOr(pre + [x[p], x[q], e])
                e_prev = e
    if hint:
        cert = json.load(open(hint))
        chosen = {p[0] * n * n + p[1] * n + p[2] for p in cert["points"]}
        for i in range(N):
            m.AddHint(x[i], int(i in chosen))
    m.Maximize(sum(x))
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = workers
    solver.parameters.max_time_in_seconds = limit
    solver.parameters.log_search_progress = True
    t0 = time.time()
    status = solver.Solve(m)
    wall = time.time() - t0
    name = solver.StatusName(status)
    res = {"n": n, "sym": sym, "workers": workers, "time_limit": limit, "status": name,
           "objective": solver.ObjectiveValue() if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None,
           "best_bound": solver.BestObjectiveBound(), "wall_seconds": round(wall, 1),
           "conflicts": solver.NumConflicts(), "branches": solver.NumBranches(),
           "hypergraph_sha256": hashlib.sha256(open(hg_path, "rb").read()).hexdigest(),
           "ortools_version": __import__("ortools").__version__, "sym_aux": naux}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        pts = [[i // (n * n), (i // n) % n, i % n] for i in range(N) if solver.Value(x[i])]
        res["points"] = pts
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "points"}))


if __name__ == "__main__":
    main()
