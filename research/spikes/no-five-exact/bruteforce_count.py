#!/usr/bin/env python3
"""Third opinion on the number of degenerate 5-subsets of [n]^3: pure Python integers,
Laplace expansion of the raw 5x5 lifted matrix (no difference trick, no numpy).
Usage: bruteforce_count.py n"""
import sys
from itertools import combinations


def det(m):
    if len(m) == 1:
        return m[0][0]
    s = 0
    for c in range(len(m)):
        sub = [row[:c] + row[c + 1:] for row in m[1:]]
        t = m[0][c] * det(sub)
        s += -t if c & 1 else t
    return s


n = int(sys.argv[1])
pts = [(x, y, z, x * x + y * y + z * z, 1) for x in range(n) for y in range(n) for z in range(n)]
total = deg = 0
for five in combinations(pts, 5):
    total += 1
    if det([list(p) for p in five]) == 0:
        deg += 1
print(f"n={n} subsets5={total} degenerate5={deg}")
