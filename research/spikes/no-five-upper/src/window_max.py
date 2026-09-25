#!/usr/bin/env python3
"""Exact window maxima W(k, n): the largest valid subset of {0..n-1}^2 x {0..k-1}.

Exact criterion: no 5-subset with vanishing lifted determinant.  Solved with CP-SAT and
lazy constraint generation: start from the axis-plane cardinality bounds (<= 4 per plane),
and whenever the incumbent contains a degenerate 5-subset, add the clause forbidding it
and re-solve.  Every degenerate 4-subset (four concyclic or collinear points) found in an
incumbent is also forbidden by a 4-clause, which is valid for every set of >= 5 points
(kill lemma).  The final incumbent is verified from scratch by a full exact census, and
the reported optimum is proved by CP-SAT on the accumulated clause set (a relaxation),
so it is a rigorous upper bound; the incumbent is a rigorous lower bound.

Usage: window_max.py n k [time_limit_s]
"""
import itertools, sys, time
from ortools.sat.python import cp_model

def lift(p): x, y, z = p; return (x, y, z, x*x + y*y + z*z)
def det4(r):
    (a,b,c,d),(e,f,g,h),(i,j,k,l),(m,n0,o,p) = r
    return (a*(f*(k*p-l*o)-g*(j*p-l*n0)+h*(j*o-k*n0)) - b*(e*(k*p-l*o)-g*(i*p-l*m)+h*(i*o-k*m))
            + c*(e*(j*p-l*n0)-f*(i*p-l*m)+h*(i*n0-j*m)) - d*(e*(j*o-k*n0)-f*(i*o-k*m)+g*(i*n0-j*m)))
def det5(pts):
    L = [lift(p) for p in pts]; p0 = L[0]
    return det4([tuple(L[i][c]-p0[c] for c in range(4)) for i in range(1,5)])
def rank_lift(pts):
    """affine rank of lifted 4 points <= 2 iff concyclic or collinear (all 3x3 minors of differences vanish)"""
    L = [lift(p) for p in pts]; p0 = L[0]; V = [tuple(L[i][c]-p0[c] for c in range(4)) for i in range(1,4)]
    for cols in itertools.combinations(range(4), 3):
        a, b, c = [tuple(v[t] for t in cols) for v in V]
        d = a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0]) + a[2]*(b[0]*c[1]-b[1]*c[0])
        if d != 0: return 3
    return 2
def violations(sel):
    bad5 = [S for S in itertools.combinations(sel, 5) if det5(S) == 0]
    bad4 = [S for S in itertools.combinations(sel, 4) if rank_lift(S) <= 2] if len(sel) >= 5 else []
    return bad5, bad4

def solve(n, k, limit=600.0):
    pts = [(x, y, z) for x in range(n) for y in range(n) for z in range(k)]
    idx = {p: i for i, p in enumerate(pts)}
    clauses5, clauses4 = [], []
    t0 = time.time(); rounds = 0
    while True:
        m = cp_model.CpModel(); v = [m.NewBoolVar(f"p{i}") for i in range(len(pts))]
        for a in range(3):
            for val in set(p[a] for p in pts):
                m.Add(sum(v[idx[p]] for p in pts if p[a] == val) <= 4)
        for S in clauses5: m.AddBoolOr([v[idx[p]].Not() for p in S])
        for S in clauses4: m.AddBoolOr([v[idx[p]].Not() for p in S])
        m.Maximize(sum(v))
        s = cp_model.CpSolver(); s.parameters.num_workers = 2; s.parameters.max_time_in_seconds = limit
        st = s.Solve(m); rounds += 1
        if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return None
        sel = [p for p in pts if s.Value(v[idx[p]])]
        bad5, bad4 = violations(sel)
        if not bad5 and not bad4:
            proved = (st == cp_model.OPTIMAL)
            return dict(n=n, k=k, W=len(sel), proved_optimal=proved, rounds=rounds,
                        clauses5=len(clauses5), clauses4=len(clauses4), secs=round(time.time()-t0, 1), set=sel)
        clauses5 += bad5; clauses4 += bad4

if __name__ == "__main__":
    n, k = int(sys.argv[1]), int(sys.argv[2]); lim = float(sys.argv[3]) if len(sys.argv) > 3 else 600.0
    r = solve(n, k, lim)
    # independent from-scratch verification of the returned set
    assert r and not any(violations(r["set"])), "verification failed"
    print({key: r[key] for key in r if key != "set"}); print("set", r["set"])
