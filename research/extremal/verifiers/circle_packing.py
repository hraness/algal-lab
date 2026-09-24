"""Exact verifier for n disjoint circles inside the unit square, scored by the sum of radii.

Coordinates and radii must be rationals (strings like "3/7" or decimals).  The
check is exact: containment and pairwise non-overlap are integer comparisons
after clearing denominators, so a returned score is a certificate.
"""

from __future__ import annotations

from fractions import Fraction

MAX_N = 64
MAX_DENOMINATOR = 10**30

DESCRIPTION = (
    "Place n circles inside the unit square [0,1]^2 so that no two overlap (touching is "
    "allowed) and every circle lies inside the square. The score is the sum of the radii; "
    "larger is better. Output JSON: {\"circles\": [[x, y, r], ...]} with x, y, r given as "
    "decimal or rational strings; they are checked exactly."
)


def _rational(value) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ValueError("coordinates must be integers or rational strings")
    if isinstance(value, str) and len(value) > 400:
        raise ValueError("literal too long")
    try:
        q = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"bad rational literal: {exc}") from None
    if q.denominator > MAX_DENOMINATOR:
        raise ValueError("denominator too large")
    return q


def verify(construction, parameters) -> Fraction:
    n = int(parameters["n"])
    if not 1 <= n <= MAX_N:
        raise ValueError("need 1 <= n <= 64")
    if not isinstance(construction, dict) or "circles" not in construction:
        raise ValueError("construction must be an object with 'circles'")
    circles = construction["circles"]
    if not isinstance(circles, list) or len(circles) != n:
        raise ValueError(f"need exactly {n} circles")
    parsed = []
    for item in circles:
        if not isinstance(item, list) or len(item) != 3:
            raise ValueError("each circle is [x, y, r]")
        x, y, r = (_rational(c) for c in item)
        if r <= 0:
            raise ValueError("radius must be positive")
        if x - r < 0 or x + r > 1 or y - r < 0 or y + r > 1:
            raise ValueError("circle leaves the unit square")
        parsed.append((x, y, r))
    for i in range(n):
        xi, yi, ri = parsed[i]
        for j in range(i + 1, n):
            xj, yj, rj = parsed[j]
            if (xi - xj) ** 2 + (yi - yj) ** 2 < (ri + rj) ** 2:
                raise ValueError(f"circles {i} and {j} overlap")
    return sum((c[2] for c in parsed), Fraction(0))
