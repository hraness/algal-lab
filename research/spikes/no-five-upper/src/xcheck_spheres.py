#!/usr/bin/env python3
"""xcheck_spheres.py n SPHEREFILE CENSUS_SPHERE_COUNT [maxcheck] -- checks the spheres.c output against
the exact 5-subset census of count5.c.  Every listed sphere must be genuinely cospherical (lifted
rank <= 3), maximal (equal to its closure; all entries if <= maxcheck, else a fixed sample) and
distinct.  Then, writing m_S for the number of grid points on sphere S and G for the circles with
>= 5 grid points,   sum_S C(m_S,5) - sum_G C(|G|,5) * #{S : G subset S}   must equal the census
count of cospherical non-coplanar 5-subsets (every coplanar 5-subset of a sphere lies on one circle
of it), which proves that no sphere carrying a non-coplanar 5-subset is missing from the file."""
import sys, random
from math import comb
from lp_bound import build_constraints, lifted_affine_rank
n = int(sys.argv[1]); sph = sys.argv[2]; census = int(sys.argv[3]); maxcheck = int(sys.argv[4]) if len(sys.argv) > 4 else 50000
pts, cons, nsph = build_constraints(n, sph)
spheres = [tuple(map(int, l.split()))[1:] for l in open(sph) if int(l.split()[0]) >= 5]
assert len(set(spheres)) == len(spheres), "duplicate sphere entries"
def closure(mem, maxrank):
    base = list(mem)
    return tuple(i for i in range(len(pts)) if i in mem or lifted_affine_rank(pts, base + [i]) <= maxrank)
sample = spheres if len(spheres) <= maxcheck else random.Random(1).sample(spheres, maxcheck)
bad = 0
for S in sample:
    if lifted_affine_rank(pts, S) > 3 or closure(S, 3) != S: bad += 1
print(f"n={n} spheres={len(spheres)} checked={len(sample)} not-cospherical-or-not-maximal={bad}")
circles = [mem for rhs, mem in cons if rhs == 3 and len(mem) >= 5]
sets = [frozenset(S) for S in spheres]
total = sum(comb(len(S), 5) for S in spheres)
corr = 0
for G in circles:
    g = frozenset(G); k = sum(1 for s in sets if g <= s); corr += comb(len(G), 5) * k
print(f"n={n} sum C(m,5)={total} coplanar-corrections={corr} (circles>=5pts: {len(circles)}) -> {total-corr}; census sphere count {census}; {'OK' if total-corr == census and bad == 0 else 'MISMATCH'}")
