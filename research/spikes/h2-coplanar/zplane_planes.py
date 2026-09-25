"""Plane-decomposition count of coplanar 5-subsets of [0,n)^3.

Computes, for each primitive v (one per +-pair) and each level k:
  N_{v,k} = #{x in [0,n)^3 : v.x = k}
Then
  S1 = sum_{v,k} C(N,5)                       (all 5-subsets of all sections)
  Z_nc = sum_{v,k} [C(N,5) - coll_sec(v,k)]   (non-collinear 5-subsets of sections)
  Z_coll = sum over lines C(L,5)              (collinear 5-subsets, counted once)
and the identity to verify:  Z_plane = Z_nc + Z_coll.

coll_sec(v,k) = sum over lines ell contained in the plane section of C(L_ell,5).
A line with direction w and point p lies in section (v,k) iff v.w = 0 and v.p = k.

For n <= 6 the heavy lines (L >= 5) are few; we enumerate lines by (w, start).
"""
import sys
from math import gcd, comb
from itertools import product

def prim_vecs(smax):
    vs = []
    for a in range(-smax, smax+1):
        for b in range(-smax, smax+1):
            for c in range(-smax, smax+1):
                if a == 0 and b == 0 and c == 0:
                    continue
                if gcd(gcd(abs(a), abs(b)), abs(c)) != 1:
                    continue
                # canonical sign: first nonzero coordinate positive
                for t in (a, b, c):
                    if t != 0:
                        if t > 0:
                            vs.append((a, b, c))
                        break
    return vs

def sections(n, smax):
    """dict v -> dict k -> N."""
    pts = list(product(range(n), repeat=3))
    out = {}
    for v in prim_vecs(smax):
        d = {}
        for x in pts:
            k = v[0]*x[0] + v[1]*x[1] + v[2]*x[2]
            d[k] = d.get(k, 0) + 1
        if max(d.values()) >= 5:
            out[v] = d
    return out

def heavy_lines(n, Lmin=5):
    """Lines with >= Lmin box points. Returns list of (w, p_start, L)."""
    pts = list(product(range(n), repeat=3))
    ptset = set(pts)
    seen = set()
    lines = []
    for i, p in enumerate(pts):
        for q in pts[i+1:]:
            w = (q[0]-p[0], q[1]-p[1], q[2]-p[2])
            g = gcd(gcd(abs(w[0]), abs(w[1])), abs(w[2]))
            w = (w[0]//g, w[1]//g, w[2]//g)
            # canonical sign on w
            for t in w:
                if t != 0:
                    if t < 0:
                        w = (-w[0], -w[1], -w[2])
                    break
            # walk back from p to start
            s = p
            while (s[0]-w[0], s[1]-w[1], s[2]-w[2]) in ptset:
                s = (s[0]-w[0], s[1]-w[1], s[2]-w[2])
            key = (w, s)
            if key in seen:
                continue
            seen.add(key)
            L = 0
            t = s
            while t in ptset:
                L += 1
                t = (t[0]+w[0], t[1]+w[1], t[2]+w[2])
            if L >= Lmin:
                lines.append((w, s, L))
    return lines

def main(n):
    smax = (2*n*n)//3 + 2   # beyond ~2n^2/3 no spanning section has N>=5
    sec = sections(n, smax)
    lines = heavy_lines(n)
    S1 = 0
    Z_nc = 0
    for v, d in sec.items():
        for k, N in d.items():
            if N < 5:
                continue
            cN = comb(N, 5)
            S1 += cN
            # collinear 5-subsets inside this section
            coll_in = 0
            for w, p, L in lines:
                if v[0]*w[0]+v[1]*w[1]+v[2]*w[2] == 0 and v[0]*p[0]+v[1]*p[1]+v[2]*p[2] == k:
                    coll_in += comb(L, 5)
            Z_nc += cN - coll_in
    Z_coll = sum(comb(L, 5) for _, _, L in lines)
    print(f"n={n} S1(sum C(N,5))={S1} Z_nc={Z_nc} Z_coll={Z_coll} "
          f"Z_plane(identity)={Z_nc+Z_coll} ratio={ (Z_nc+Z_coll)/n**11:.5f}")

if __name__ == "__main__":
    main(int(sys.argv[1]))
