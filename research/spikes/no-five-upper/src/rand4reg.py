#!/usr/bin/env python3
"""Random 4-regular point sets in {0..n-1}^3: exactly 4 points on every axis-parallel plane.

Model: four independent uniformly random pairs of permutations (sigma_j, tau_j) of [n];
the set is {(i, sigma_j(i), tau_j(i)) : i in [n], j = 1..4}, resampled until all 4n
points are distinct.  Every plane x=i, y=d, z=e then contains exactly 4 points.
Writes one "x y z" triple per line.
"""
import random, sys
def sample(n, rng):
    while True:
        pts = set()
        for _ in range(4):
            s = list(range(n)); t = list(range(n)); rng.shuffle(s); rng.shuffle(t)
            for i in range(n): pts.add((i, s[i], t[i]))
        if len(pts) == 4 * n: return sorted(pts)
if __name__ == "__main__":
    n = int(sys.argv[1]); seed = int(sys.argv[2]); out = sys.argv[3]
    pts = sample(n, random.Random(seed))
    with open(out, "w") as f:
        for x, y, z in pts: f.write(f"{x} {y} {z}\n")
    # self-check of 4-regularity
    from collections import Counter
    for a in range(3):
        assert set(Counter(p[a] for p in pts).values()) == {4}
    print(out, len(pts))
