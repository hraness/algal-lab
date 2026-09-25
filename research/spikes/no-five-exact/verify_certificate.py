#!/usr/bin/env python3
"""Verify a point-set certificate {"n": n, "points": [[x,y,z], ...]} three ways:
 1. an independent big-integer check: Laplace expansion of the raw 5x5 lifted matrix
    (rows (x, y, z, x^2+y^2+z^2, 1)) over every 5-subset, pure Python ints;
 2. the repository verifier research/extremal/verifiers/no_five_on_sphere.py;
 3. optionally the hypergraph constraints (at most 4 per sphere/plane set, 3 per circle/line).
Usage: verify_certificate.py cert.json [hg.json]"""
import hashlib
import json
import os
import sys
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, ROOT)


def det(m):
    if len(m) == 1:
        return m[0][0]
    s = 0
    for c in range(len(m)):
        sub = [row[:c] + row[c + 1:] for row in m[1:]]
        t = m[0][c] * det(sub)
        s += -t if c & 1 else t
    return s


def main():
    path = sys.argv[1]
    cert = json.load(open(path))
    n = int(cert["n"])
    pts = [tuple(int(c) for c in p) for p in cert["points"]]
    assert len(set(pts)) == len(pts), "repeated point"
    assert all(0 <= c < n for p in pts for c in p), "outside grid"
    lifted = [[x, y, z, x * x + y * y + z * z, 1] for (x, y, z) in pts]
    checked = 0
    for five in combinations(lifted, 5):
        if det([row[:] for row in five]) == 0:
            raise SystemExit(f"FAIL independent check: degenerate 5-subset {five}")
        checked += 1
    print(f"independent 5x5 Laplace check: {len(pts)} points, {checked} 5-subsets, all nonzero")
    from research.extremal.verifiers import no_five_on_sphere
    value = no_five_on_sphere.verify({"points": [list(p) for p in pts]}, {"n": n})
    print(f"repo verifier value: {value}")
    if len(sys.argv) > 2:
        hg = json.load(open(sys.argv[2]))
        assert hg["n"] == n
        idx = {p[0] * n * n + p[1] * n + p[2] for p in pts}
        bad4 = sum(1 for s in hg["at_most_4"] if len(idx.intersection(s)) > 4)
        bad3 = sum(1 for s in hg["at_most_3"] if len(idx.intersection(s)) > 3)
        print(f"hypergraph constraints: violated at_most_4={bad4} at_most_3={bad3}")
        assert bad4 == 0 and bad3 == 0
    print("sha256", hashlib.sha256(open(path, "rb").read()).hexdigest(), "size", len(pts), "n", n)


if __name__ == "__main__":
    main()
