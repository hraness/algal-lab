#!/usr/bin/env python3
"""Exact degenerate-set hypergraph for "no five points of [n]^3 on a sphere or plane".

Lifted point L(p) = (x, y, z, x^2+y^2+z^2, 1). Five points lie on a common sphere
or plane iff their lifted vectors are linearly dependent (the 5x5 determinant
vanishes). For a generalized sphere (sphere or plane) G with at least five grid
points, the grid points on G form a *degenerate set*; a 5-subset is forbidden
iff it lies inside one such set, so the exact constraint is "at most 4 chosen
points in every inclusion-maximal degenerate set".

Four points whose lifted vectors have rank <= 3 (four concyclic or four
collinear points) lie on a pencil of generalized spheres that covers the whole
space, so any fifth grid point completes a degenerate 5-subset. For |S| >= 5 the
constraint "at most 3 chosen points on every circle or line with >= 4 grid
points" is therefore implied; it is emitted as a redundant strengthening.

Method. For every non-collinear triple T = (i, j, k) the 4x5 lifted matrix
[L_i; L_j; L_k; L_q] has, for each grid point q, the null vector
v_c = (-1)^c det(minor omitting column c); v is the coefficient vector of the
unique generalized sphere through T and q (v = 0 iff q is on the circle of T).
v is linear in L_q: v = D(T) L_q with an integer 5x5 matrix D(T) built from the
ten 3x3 minors of the 3x5 matrix [L_i; L_j; L_k]. Normalising v by its gcd and
sign gives a canonical key per generalized sphere; a key seen for >= 2 points q
outside T names a sphere/plane with >= 5 grid points. Its full point set is then
evaluated exactly (L v = 0 over the whole grid) and the family is reduced to
inclusion-maximal members.

All arithmetic is int64 numpy on entries bounded by 24 * (n-1)^2 * 3 (n-1)^2,
i.e. below 2^20 for n <= 7; gcd/sign normalisation uses exact integer ops.

Point index convention: idx = x*n*n + y*n + z (the same as native/ls5x.c).

Usage: hypergraph.py n out.json   |   hypergraph.py --selftest
"""
import hashlib
import itertools
import json
import sys
import time

import numpy as np


def det2(a, b, c, d):
    return a * d - b * c


def det3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def det4(m):
    s = 0
    for c in range(4):
        sub = [[m[r][j] for j in range(4) if j != c] for r in range(1, 4)]
        t = m[0][c] * det3(sub)
        s += -t if c & 1 else t
    return s


def det5(m):
    s = 0
    for c in range(5):
        sub = [[m[r][j] for j in range(5) if j != c] for r in range(1, 5)]
        t = m[0][c] * det4(sub)
        s += -t if c & 1 else t
    return s


def grid(n):
    pts = [(x, y, z) for x in range(n) for y in range(n) for z in range(n)]
    L = np.array([(x, y, z, x * x + y * y + z * z, 1) for (x, y, z) in pts], dtype=np.int64)
    return pts, L


SIGNS = np.array([1, -1, 1, -1, 1], dtype=np.int64)  # (-1)^c


def null_matrix(A):
    """D such that for r (5-vector), D @ r = v with v_c = (-1)^c det([A; r] omitting column c).

    Expanding the 4x4 minor omitting column c along its last row r:
    det = sum_{d != c} r_d (-1)^(4 + pos_c(d)) det3(A without columns c, d),
    pos_c(d) = 1-based position of column d among the columns other than c.
    A is a 3x5 list of Python ints; returns a 5x5 numpy int64 matrix (already
    multiplied by the (-1)^c sign so that D r is the null vector).
    """
    minors = {}
    D = np.zeros((5, 5), dtype=np.int64)
    for c in range(5):
        for d in range(5):
            if c == d:
                continue
            key = (min(c, d), max(c, d))
            if key not in minors:
                cols = [t for t in range(5) if t not in key]
                minors[key] = det3([[A[r][t] for t in cols] for r in range(3)])
            pos = d + 1 if d < c else d
            coeff = minors[key] if (4 + pos) % 2 == 0 else -minors[key]
            D[c, d] = coeff if c % 2 == 0 else -coeff
    return D


def normalise_rows(v):
    """Divide each row by its gcd and make the first nonzero entry positive. Zero rows stay zero."""
    g = np.gcd.reduce(np.abs(v), axis=1)
    nz = g != 0
    gg = np.where(nz, g, 1)
    v = v // gg[:, None]
    first = (v != 0).argmax(axis=1)
    s = np.sign(v[np.arange(v.shape[0]), first])
    s = np.where(s == 0, 1, s)
    return v * s[:, None], nz


def pack_keys(v):
    """Two exact int64 keys per row (entries are bounded well below 2^20 in magnitude)."""
    B = np.int64(1 << 20)
    k1 = ((v[:, 0] + B) * (2 * B) + (v[:, 1] + B)) * (2 * B) + (v[:, 2] + B)
    k2 = (v[:, 3] + B) * (2 * B) + (v[:, 4] + B)
    return k1, k2


def collinear(p, q, r):
    ux, uy, uz = q[0] - p[0], q[1] - p[1], q[2] - p[2]
    vx, vy, vz = r[0] - p[0], r[1] - p[1], r[2] - p[2]
    return (uy * vz - uz * vy) == 0 and (uz * vx - ux * vz) == 0 and (ux * vy - uy * vx) == 0


def enumerate_family(n, log=lambda *a: print(*a, flush=True)):
    pts, L = grid(n)
    N = len(pts)
    Lpy = [list(map(int, row)) for row in L]
    keys = {}           # normalised coefficient tuple -> None (spheres/planes with >= 5 grid points)
    circles = set()     # frozenset of point indices on a circle with >= 4 grid points
    t0 = time.time()
    n_triples = 0
    n_collinear = 0
    ar = np.arange(N)
    for i in range(N):
        for j in range(i + 1, N):
            for k in range(j + 1, N):
                if collinear(pts[i], pts[j], pts[k]):
                    n_collinear += 1
                    continue
                n_triples += 1
                D = null_matrix([Lpy[i], Lpy[j], Lpy[k]])
                v = L @ D.T                     # row q = null vector of [L_i; L_j; L_k; L_q]
                v, nz = normalise_rows(v)
                nz[[i, j, k]] = False           # the triple itself gives zero rows; exclude
                zero = ~nz
                zero[[i, j, k]] = False
                if zero.any():                  # concyclic points with the triple
                    circ = frozenset(ar[zero].tolist() + [i, j, k])
                    circles.add(circ)
                vv = v[nz]
                if vv.shape[0] < 2:
                    continue
                k1, k2 = pack_keys(vv)
                order = np.lexsort((k2, k1))
                k1s, k2s = k1[order], k2[order]
                same = (k1s[1:] == k1s[:-1]) & (k2s[1:] == k2s[:-1])
                if same.any():
                    idx = np.nonzero(same)[0]
                    for t in idx:
                        key = tuple(int(x) for x in vv[order[t]])
                        keys[key] = None
        if (i + 1) % max(1, N // 20) == 0:
            log(f"  i={i+1}/{N} triples={n_triples} keys={len(keys)} circles={len(circles)} t={time.time()-t0:.1f}s")
    log(f"triples: {n_triples} non-collinear, {n_collinear} collinear; distinct sphere/plane keys: {len(keys)}; circles: {len(circles)}; {time.time()-t0:.1f}s")

    # exact point sets of every generalized sphere with >= 5 grid points
    fam = {}
    for key in keys:
        vec = np.array(key, dtype=np.int64)
        on = np.nonzero(L @ vec == 0)[0]
        assert on.shape[0] >= 5, (key, on)
        kind = "plane" if key[3] == 0 else "sphere"
        fam[frozenset(on.tolist())] = kind
    # lines with >= 4 grid points
    lines = set()
    for i in range(N):
        for j in range(i + 1, N):
            d = tuple(pts[j][c] - pts[i][c] for c in range(3))
            g = np.gcd.reduce(np.abs(np.array(d)))
            d = tuple(int(x) // int(g) for x in d)
            on = []
            t = 0
            while True:
                p = tuple(pts[i][c] + t * d[c] for c in range(3))
                if not all(0 <= c < n for c in p):
                    break
                on.append(p[0] * n * n + p[1] * n + p[2])
                t += 1
            t = -1
            while True:
                p = tuple(pts[i][c] + t * d[c] for c in range(3))
                if not all(0 <= c < n for c in p):
                    break
                on.append(p[0] * n * n + p[1] * n + p[2])
                t -= 1
            if len(on) >= 4:
                lines.add(frozenset(on))
    circles4 = {c for c in circles if len(c) >= 4}
    return pts, L, fam, circles4, lines


def rank_deficient4(pts, a, b, c, d):
    """True iff the lifted vectors of four points have rank <= 3 (concyclic or collinear)."""
    rows = []
    for e in (b, c, d):
        rows.append([pts[e][t] - pts[a][t] for t in range(3)] + [sum(pts[e][t] ** 2 for t in range(3)) - sum(pts[a][t] ** 2 for t in range(3))])
    for drop in range(4):
        m = [[r[t] for t in range(4) if t != drop] for r in rows]
        if det3(m) != 0:
            return False
    return True


def concyclic(pts, s):
    """True iff all points of s (>= 4 points) lie on one circle or line."""
    s = sorted(s)
    a, b, c = s[0], s[1], s[2]
    return all(rank_deficient4(pts, a, b, c, q) for q in s[3:])


def maximal(pts, sets):
    """Inclusion-maximal members of a family of point sets of generalized spheres.

    Two distinct generalized spheres meet in a circle, a line, a point or nothing, so a
    member with >= 5 points can only be contained in another one if all of its points
    are concyclic or collinear. Only those members are tested for a strict superset
    (among the sets containing their three smallest points).
    """
    sets = list(set(sets))
    index = {}
    for t, s in enumerate(sets):
        for p in s:
            index.setdefault(p, set()).add(t)
    kept = []
    dropped = 0
    for t, s in enumerate(sets):
        if len(s) >= 4 and concyclic(pts, s):
            a, b, c = sorted(s)[:3]
            cands = index[a] & index[b] & index[c]
            if any(u != t and s < sets[u] for u in cands):
                dropped += 1
                continue
        kept.append(s)
    return kept, dropped


def symmetries(n):
    """The 48 symmetries of the cube acting on point indices."""
    maps = []
    for perm in itertools.permutations(range(3)):
        for flips in itertools.product((0, 1), repeat=3):
            m = []
            for x in range(n):
                for y in range(n):
                    for z in range(n):
                        p = (x, y, z)
                        q = [p[perm[c]] for c in range(3)]
                        q = [n - 1 - q[c] if flips[c] else q[c] for c in range(3)]
                        m.append(q[0] * n * n + q[1] * n + q[2])
            maps.append(m)
    return maps


def selftest():
    rng = np.random.default_rng(1)
    for n in (3, 4, 5, 7):
        pts, L = grid(n)
        Lpy = [list(map(int, r)) for r in L]
        N = len(pts)
        for _ in range(300):
            i, j, k, q = rng.choice(N, 4, replace=False)
            if collinear(pts[i], pts[j], pts[k]):
                continue
            D = null_matrix([Lpy[i], Lpy[j], Lpy[k]])
            v = D @ L[q]
            M = [Lpy[i], Lpy[j], Lpy[k], Lpy[q]]
            # direct minors with Python ints
            direct = []
            for c in range(5):
                sub = [[M[r][t] for t in range(5) if t != c] for r in range(4)]
                dd = det4(sub)
                direct.append(dd if c % 2 == 0 else -dd)
            assert list(map(int, v)) == direct, (n, i, j, k, q, v, direct)
            for r in M:
                assert sum(int(a) * int(b) for a, b in zip(r, v)) == 0
            # rank test: v == 0 iff every 5-subset with any extra point is degenerate
            if all(x == 0 for x in direct):
                for extra in rng.choice(N, 5, replace=False):
                    if extra in (i, j, k, q):
                        continue
                    assert det5([Lpy[i], Lpy[j], Lpy[k], Lpy[q], Lpy[extra]]) == 0
            else:
                # some extra point off the sphere must exist
                assert any(det5([Lpy[i], Lpy[j], Lpy[k], Lpy[q], Lpy[e]]) != 0 for e in range(N) if e not in (i, j, k, q))
    print("selftest ok")


def main():
    if sys.argv[1] == "--selftest":
        selftest()
        return
    n = int(sys.argv[1])
    out = sys.argv[2]
    t0 = time.time()
    pts, L, fam, circles, lines = enumerate_family(n)
    spheres = [s for s, kind in fam.items() if kind == "sphere"]
    planes = [s for s, kind in fam.items() if kind == "plane"]
    max_sets, dropped4 = maximal(pts, list(fam))
    kinds = {s: fam[s] for s in max_sets}
    max_spheres = [s for s in max_sets if kinds[s] == "sphere"]
    max_planes = [s for s in max_sets if kinds[s] == "plane"]
    max_circ, dropped3 = maximal(pts, list(circles) + list(lines))
    line_set = set(lines)
    max_lines = [s for s in max_circ if s in line_set]
    max_circles = [s for s in max_circ if s not in line_set]

    # symmetry invariance check
    fam_all = set(max_sets)
    circ_all = set(max_circ)
    sym_ok = True
    for m in symmetries(n):
        img = {frozenset(m[p] for p in s) for s in fam_all}
        img2 = {frozenset(m[p] for p in s) for s in circ_all}
        if img != fam_all or img2 != circ_all:
            sym_ok = False
    def hist(sets):
        h = {}
        for s in sets:
            h[len(s)] = h.get(len(s), 0) + 1
        return dict(sorted(h.items()))
    stats = {
        "n": n, "N": len(pts),
        "spheres_ge5_raw": len(spheres), "planes_ge5_raw": len(planes),
        "spheres_maximal": len(max_spheres), "planes_maximal": len(max_planes),
        "degenerate_sets_maximal": len(max_sets), "dropped_nonmaximal_4": dropped4, "dropped_nonmaximal_3": dropped3,
        "circles_ge4_raw": len(circles), "lines_ge4_raw": len(lines),
        "circles_maximal": len(max_circles), "lines_maximal": len(max_lines),
        "size_histogram_spheres": hist(max_spheres), "size_histogram_planes": hist(max_planes),
        "size_histogram_circles": hist(max_circles), "size_histogram_lines": hist(max_lines),
        "symmetry_invariant_under_48": sym_ok,
        "seconds": round(time.time() - t0, 1),
    }
    doc = {
        "contract": "algal.lab.no-five-hypergraph.v1",
        "n": n, "index": "x*n*n + y*n + z",
        "stats": stats,
        "at_most_4": [sorted(s) for s in sorted(max_sets, key=lambda s: (len(s), sorted(s)))],
        "at_most_4_kind": [kinds[s] for s in sorted(max_sets, key=lambda s: (len(s), sorted(s)))],
        "at_most_3": [sorted(s) for s in sorted(max_circ, key=lambda s: (len(s), sorted(s)))],
        "at_most_3_kind": ["line" if s in line_set else "circle" for s in sorted(max_circ, key=lambda s: (len(s), sorted(s)))],
    }
    with open(out, "w") as f:
        json.dump(doc, f, separators=(",", ":"))
    sha = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print(json.dumps(stats, indent=1))
    print("wrote", out, "sha256", sha)


if __name__ == "__main__":
    main()
