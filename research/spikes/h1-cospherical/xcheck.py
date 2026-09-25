#!/usr/bin/env python3
"""xcheck.py -- independent verification of esamp output.

Recomputes the circumsphere of the base quadruple with exact Fraction
arithmetic, derives the primitive integer equation a|p|^2+b.p+c=0, counts grid
points on the sphere by direct scan, and compares with the spheres.tsv /
extras.tsv records.

Usage: xcheck.py spheres.tsv extras.tsv n [num_to_check]
"""
import sys
from fractions import Fraction
from math import gcd
from itertools import product


def circumsphere(P):
    """Return (u,v,w,t) with |p|^2 + u x + v y + w z + t = 0, or None if coplanar."""
    A = P[0]
    M = [[Fraction(2 * (P[i + 1][j] - A[j])) for j in range(3)] for i in range(3)]
    r = [Fraction(sum(x * x for x in P[i + 1]) - sum(x * x for x in A)) for i in range(3)]
    # solve M . sol = r  (3x3, exact)
    det = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])
           - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
           + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
    if det == 0:
        return None
    # center = M^{-1} r ; sphere |p|^2 - 2 c.p + (|c|^2 - R^2) = 0
    # solve via adjugate: sol = adj(M) r / det with adj[i][j] = C[j][i]
    Cof = [[0] * 3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            minor = [[M[x][y] for y in range(3) if y != j] for x in range(3) if x != i]
            Cof[i][j] = ((-1) ** (i + j)) * (minor[0][0] * minor[1][1] - minor[0][1] * minor[1][0])
    c = [sum(Cof[j][i] * r[j] for j in range(3)) / det for i in range(3)]
    R2 = sum((Fraction(A[j]) - c[j]) ** 2 for j in range(3))
    u, v, w = (-2 * c[0], -2 * c[1], -2 * c[2])
    t = sum(x * x for x in c) - R2
    return u, v, w, t


def primitive(uvwt):
    """Scale (u,v,w,t) to primitive ints a|p|^2+b.p+c=0, a>0."""
    u, v, w, t = uvwt
    dens = [x.denominator for x in (u, v, w, t)]
    L = dens[0]
    for d in dens[1:]:
        L = L * d // gcd(L, int(d))
    a = int(L)
    co = [a, int(u * L), int(v * L), int(w * L), int(t * L)]
    g = 0
    for x in co:
        g = gcd(g, abs(x))
    co = [x // g for x in co]
    return tuple(co)


def count_on_sphere(a, b, c, n):
    cnt, pts = 0, []
    for p in product(range(n), repeat=3):
        if a * (p[0] ** 2 + p[1] ** 2 + p[2] ** 2) + b[0] * p[0] + b[1] * p[1] + b[2] * p[2] + c == 0:
            cnt += 1
            pts.append(p)
    return cnt, pts


def main():
    sp = open(sys.argv[1])
    ex = open(sys.argv[2])
    n = int(sys.argv[3])
    want = int(sys.argv[4]) if len(sys.argv) > 4 else 300
    next(ex)
    elines = [l for l in ex]
    # map sample id -> extras line
    exmap = {}
    for l in elines:
        p = l.split('|')
        sid = int(p[0].split()[0])
        exmap[sid] = l.strip()
    checked, bad = 0, 0
    next(sp)
    sid = 0
    for line in sp:
        parts = line.split()
        a, b1, b2, b3, c, det, k = (int(x) for x in parts)
        if sid in exmap:
            p = exmap[sid].split('|')
            base = [int(x) for x in p[1].split()]
            P = [tuple(base[3 * i:3 * i + 3]) for i in range(4)]
            uvwt = circumsphere(P)
            assert uvwt is not None, f"sample {sid}: coplanar base?"
            pr = primitive(uvwt)
            cnt, pts = count_on_sphere(pr[0], pr[1:4], pr[4], n)
            ok = (pr == (a, b1, b2, b3, c)) and (cnt - 4 == k)
            stored = [int(x) for x in p[2].replace('TRUNC', '0 ').split('(')[0].split()]
            sp_pts = [tuple(stored[3 * i:3 * i + 3]) for i in range(len(stored) // 3)]
            tot = int(p[0].split()[1])
            ok = ok and (tot == cnt) and sorted(sp_pts) == sorted(pts)
            if not ok:
                bad += 1
                print(f"MISMATCH sid={sid}: mine {pr} cnt={cnt}; file a={a} b=({b1},{b2},{b3}) c={c} k={k}")
            checked += 1
            if checked >= want:
                break
        sid += 1
    print(f"checked {checked} spheres with extras: {bad} mismatches")


if __name__ == "__main__":
    main()
