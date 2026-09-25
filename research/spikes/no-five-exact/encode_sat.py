#!/usr/bin/env python3
"""CNF encoder for "exists S subset of [n]^3 with |S| >= k and no five points on a sphere or plane".

Variables 1..N are the grid points (index x*n*n+y*n+z, variable = index+1).
Constraints (from the exact hypergraph produced by hypergraph.py):
  * at most 4 chosen points in every inclusion-maximal sphere/plane point set;
  * at most 3 chosen points on every circle/line with >= 4 grid points (implied for |S| >= 5);
  * at least k chosen points (totalizer);
  * optional symmetry breaking (--sym): lex-leader clauses x <=_lex pi(x) for every
    non-identity element pi of the 48-element symmetry group of the cube, with the
    standard "prefix equal" auxiliary chain. Sound because the lexicographically
    smallest member of every orbit satisfies all 47 constraints simultaneously.
Small cardinality constraints are written as the explicit forbidden (bound+1)-subsets;
larger ones use pysat's sequential counter with fresh auxiliary variables.
Usage: encode_sat.py hg.json k out.cnf [--sym] [--direct-max 60]
"""
import hashlib
import itertools
import json
import sys
import time

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

sys.path.insert(0, __import__("os").path.dirname(__file__))
from hypergraph import symmetries  # noqa: E402


def lex_leader(perm, x, pool, clauses):
    """Clauses for (x_0..x_{N-1}) <=_lex (x_{perm 0}..x_{perm N-1}); returns #aux vars."""
    e_prev = None
    aux = 0
    for p in range(len(x)):
        q = perm[p]
        if q == p:
            continue
        xp, xq = x[p], x[q]
        pre = [-e_prev] if e_prev is not None else []
        clauses.append(pre + [-xp, xq])
        e = pool.id(("lex", id(perm), p))
        aux += 1
        clauses.append(pre + [-xp, -xq, e])
        clauses.append(pre + [xp, xq, e])
        e_prev = e
    return aux


def encode(hg, k, sym, direct_max=60):
    n = hg["n"]
    N = n ** 3
    pool = IDPool()
    x = [pool.id(("p", i)) for i in range(N)]
    assert x == list(range(1, N + 1))
    clauses = []
    stats = {"direct": 0, "counter_sets": 0}
    for sets, bound in ((hg["at_most_4"], 4), (hg["at_most_3"], 3)):
        for s in sets:
            m = len(s)
            ncl = 1
            for t in range(bound + 1):
                ncl = ncl * (m - t) // (t + 1)
            if ncl <= direct_max:
                for sub in itertools.combinations(s, bound + 1):
                    clauses.append([-x[p] for p in sub])
                stats["direct"] += ncl
            else:
                enc = CardEnc.atmost(lits=[x[p] for p in s], bound=bound, vpool=pool, encoding=EncType.seqcounter)
                clauses.extend(enc.clauses)
                stats["counter_sets"] += 1
    enc = CardEnc.atleast(lits=x, bound=k, vpool=pool, encoding=EncType.totalizer)
    clauses.extend(enc.clauses)
    stats["atleast_clauses"] = len(enc.clauses)
    stats["sym_aux"] = 0
    if sym:
        for perm in symmetries(n):
            if all(perm[p] == p for p in range(N)):
                continue
            stats["sym_aux"] += lex_leader(perm, x, pool, clauses)
    return pool.top, clauses, stats


def main():
    hg_path, k, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    sym = "--sym" in sys.argv
    direct_max = 60
    if "--direct-max" in sys.argv:
        direct_max = int(sys.argv[sys.argv.index("--direct-max") + 1])
    hg = json.load(open(hg_path))
    hg_sha = hashlib.sha256(open(hg_path, "rb").read()).hexdigest()
    t0 = time.time()
    nv, clauses, stats = encode(hg, k, sym, direct_max)
    with open(out, "w") as f:
        f.write(f"c no-five-on-sphere n={hg['n']} k>={k} sym={int(sym)} hypergraph_sha256={hg_sha}\n")
        f.write(f"c at_most_4 sets={len(hg['at_most_4'])} at_most_3 sets={len(hg['at_most_3'])} {json.dumps(stats)}\n")
        f.write(f"p cnf {nv} {len(clauses)}\n")
        for c in clauses:
            f.write(" ".join(map(str, c)) + " 0\n")
    sha = hashlib.sha256(open(out, "rb").read()).hexdigest()
    meta = {"n": hg["n"], "k": k, "sym": sym, "vars": nv, "clauses": len(clauses), "stats": stats,
            "hypergraph_sha256": hg_sha, "cnf_sha256": sha, "seconds": round(time.time() - t0, 1)}
    json.dump(meta, open(out + ".meta.json", "w"), indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
