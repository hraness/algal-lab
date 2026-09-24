"""Subsets of [n]^3 with no five points on a common sphere or plane (AlphaEvolve problem 60).

Five points are cospherical or coplanar iff the 5x5 determinant with rows
(x, y, z, x^2+y^2+z^2, 1) vanishes. After subtracting the first point that is
the 4x4 integer determinant of the lifted difference vectors. The score is the
number of points; larger is better.
"""

from fractions import Fraction
from itertools import combinations

DESCRIPTION = (
    "Subset of the n x n x n grid {0..n-1}^3 such that no 5 points lie on a common sphere or plane "
    "(the 5x5 determinant with rows (x, y, z, x^2+y^2+z^2, 1) must be nonzero for every 5-subset). "
    "Score = number of points; more is better. Output: {\"points\": [[x, y, z], ...]} with plain "
    "ints in [0, n-1], no repeats."
)
MAX_N = 64
MAX_POINTS = 48


def _det4(m):
    (a, b, c, d), (e, f, g, h), (i, j, k, l), (m0, n0, o, p) = m
    kp_lo = k * p - l * o
    jp_ln = j * p - l * n0
    jo_kn = j * o - k * n0
    ip_lm = i * p - l * m0
    io_km = i * o - k * m0
    in_jm = i * n0 - j * m0
    return (a * (f * kp_lo - g * jp_ln + h * jo_kn)
            - b * (e * kp_lo - g * ip_lm + h * io_km)
            + c * (e * jp_ln - f * ip_lm + h * in_jm)
            - d * (e * jo_kn - f * io_km + g * in_jm))


def _points(construction, n):
    raw = construction.get("points") if isinstance(construction, dict) else None
    if not isinstance(raw, list) or len(raw) > MAX_POINTS:
        raise ValueError("points must be a list of at most %d triples" % MAX_POINTS)
    points = []
    for item in raw:
        if not isinstance(item, (list, tuple)) or len(item) != 3:
            raise ValueError(f"point {item!r} is not a triple")
        if any(isinstance(c, bool) or not isinstance(c, int) for c in item):
            raise ValueError(f"point {item!r} must have integer coordinates")
        if any(not 0 <= c < n for c in item):
            raise ValueError(f"point {item!r} outside the grid")
        points.append(tuple(item))
    if len(set(points)) != len(points):
        raise ValueError("repeated point")
    return points


def verify(construction, parameters) -> Fraction:
    n = int(parameters["n"])
    if not 1 <= n <= MAX_N:
        raise ValueError("n out of range")
    points = _points(construction, n)
    lifted = [(x, y, z, x * x + y * y + z * z) for x, y, z in points]
    for five in combinations(range(len(points)), 5):
        p0 = lifted[five[0]]
        rows = [tuple(lifted[i][c] - p0[c] for c in range(4)) for i in five[1:]]
        if _det4(rows) == 0:
            raise ValueError(f"five cospherical/coplanar points {[points[i] for i in five]}")
    return Fraction(len(points))
