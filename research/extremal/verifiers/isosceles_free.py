"""Isosceles-free subsets of the grid [n]^2 (AlphaEvolve repository problem 59).

A subset S of {0,...,n-1}^2 is isosceles-free when no three distinct points
a, b, c in S satisfy |a-b| = |b-c|; flat triangles (b the midpoint of a and c)
count. Equivalently, for every b in S the squared distances from b to the other
points are pairwise distinct. The score is |S|; larger is better.
"""

from fractions import Fraction

DESCRIPTION = (
    "Isosceles-free subset of the n x n grid {0..n-1}^2: no three distinct points a, b, c with "
    "dist(a,b) == dist(b,c) (degenerate/collinear cases included). Equivalently, every point must "
    "have pairwise distinct squared distances to all other points. Score = number of points; more "
    "is better. Output: {\"points\": [[x, y], ...]} with plain ints in [0, n-1], no repeats."
)
MAX_N = 1024
MAX_POINTS = 4096


def _points(construction, n):
    raw = construction.get("points") if isinstance(construction, dict) else None
    if not isinstance(raw, list) or len(raw) > MAX_POINTS:
        raise ValueError("points must be a list of at most %d pairs" % MAX_POINTS)
    points = []
    for item in raw:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"point {item!r} is not a pair")
        x, y = item
        if isinstance(x, bool) or isinstance(y, bool) or not isinstance(x, int) or not isinstance(y, int):
            raise ValueError(f"point {item!r} must have integer coordinates")
        if not (0 <= x < n and 0 <= y < n):
            raise ValueError(f"point {item!r} outside the grid")
        points.append((x, y))
    if len(set(points)) != len(points):
        raise ValueError("repeated point")
    return points


def verify(construction, parameters) -> Fraction:
    n = int(parameters["n"])
    if not 1 <= n <= MAX_N:
        raise ValueError("n out of range")
    points = _points(construction, n)
    for i, (bx, by) in enumerate(points):
        seen = {}
        for j, (x, y) in enumerate(points):
            if i == j:
                continue
            d = (x - bx) ** 2 + (y - by) ** 2
            if d in seen:
                raise ValueError(f"isosceles triangle at apex {points[i]} with {points[seen[d]]} and {points[j]}")
            seen[d] = j
    return Fraction(len(points))
