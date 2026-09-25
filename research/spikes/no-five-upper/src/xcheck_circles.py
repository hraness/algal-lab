#!/usr/bin/env python3
"""xcheck_circles.py n SPHEREFILE -- independent brute-force check of the LP constraint generator.

Circles/lines: every 4-subset of [n]^3 with lifted affine rank <= 2 (concyclic or collinear) is
closed under 'add every grid point that keeps the rank <= 2'; the closures are exactly the circles
and lines with >= 4 grid points.  They must coincide with the rhs-3 constraints of lp_bound.py.
Spheres/planes (n <= 3 only, 5-subsets): every 5-subset of lifted affine rank exactly 3 is closed
under rank <= 3; the closures are the spheres/planes with >= 5 grid points that contain a
non-coplanar 5-subset.  (A rank-2 5-subset, e.g. five points of one circle, has no single closure
and is skipped; spheres all of whose grid points are concyclic are redundant for the LP.)"""
import sys, itertools
from lp_bound import build_constraints, lifted_affine_rank
n = int(sys.argv[1]); sph = sys.argv[2]
pts, cons, nsph = build_constraints(n, sph)
lp3 = {mem for rhs, mem in cons if rhs == 3}
lp4 = {mem for rhs, mem in cons if rhs == 4}
def closure(mem, maxrank):
    base = list(mem)
    return tuple(i for i in range(len(pts)) if i in mem or lifted_affine_rank(pts, base + [i]) <= maxrank)
bf3 = set()
for S in itertools.combinations(range(len(pts)), 4):
    if lifted_affine_rank(pts, S) <= 2: bf3.add(closure(S, 2))
print(f"n={n} rhs-3 (circles/lines >=4 pts): lp {len(lp3)} brute {len(bf3)} lp-minus-brute {len(lp3-bf3)} brute-minus-lp {len(bf3-lp3)}")
for mem in sorted(bf3 - lp3)[:5]: print("  missing in lp:", [pts[i] for i in mem])
for mem in sorted(lp3 - bf3)[:5]: print("  extra in lp:", [pts[i] for i in mem])
if n <= 3:
    bf4 = set()
    for S in itertools.combinations(range(len(pts)), 5):
        if lifted_affine_rank(pts, S) == 3: bf4.add(closure(S, 3))
    print(f"n={n} rhs-4 (spheres/planes >=5 pts with a non-coplanar 5-subset): lp {len(lp4)} brute {len(bf4)} lp-minus-brute {len(lp4-bf4)} brute-minus-lp {len(bf4-lp4)}")
    for mem in sorted(bf4 - lp4)[:5]: print("  missing in lp:", len(mem), [pts[i] for i in mem])
    for mem in sorted(lp4 - bf4)[:5]: print("  extra in lp:", len(mem), [pts[i] for i in mem])
print("OK" if not (bf3 - lp3) and not (lp3 - bf3) and (n > 3 or (not (bf4 - lp4) and not (lp4 - bf4))) else "MISMATCH")
