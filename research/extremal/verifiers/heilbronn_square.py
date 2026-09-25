"""Heilbronn problem in the unit square: n points maximising the smallest triangle area.

Coordinates are exact rationals in [0, 1]; the value is the minimum over all
triples of |cross product| / 2. Larger is better. This matches the exact
verifier of the record ledger at math.tejstead.com/heilbronn (square frame).
"""

from fractions import Fraction
from itertools import combinations

DESCRIPTION = (
    "Heilbronn problem in the unit square: place n points with 0 <= x, y <= 1 maximising the "
    "smallest area among all C(n,3) triangles. Score = that minimum area (exact rational); larger is "
    "better. Output: {\"points\": [[x, y], ...]} with exactly n points, each coordinate a decimal or "
    "fraction string (e.g. \"0.24732605271\" or \"1/3\"); floats are rejected. Truncate decimals "
    "toward zero so points stay inside the square."
)
MAX_POINTS = 64
MAX_DENOMINATOR = 10**60


MAX_LITERAL_CHARS = 400


def _coord(text):
    if isinstance(text, bool) or not isinstance(text, (str, int)):
        raise ValueError(f"coordinate {text!r} must be a string or int")
    if isinstance(text, str) and len(text) > MAX_LITERAL_CHARS:
        raise ValueError("literal too long")
    try:
        value = Fraction(text)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"bad rational literal {text!r}: {exc}") from None
    if not 0 <= value <= 1:
        raise ValueError(f"coordinate {text!r} outside [0, 1]")
    if value.denominator > MAX_DENOMINATOR:
        raise ValueError("coordinate denominator too large")
    return value


def verify(construction, parameters) -> Fraction:
    n = int(parameters["n"])
    if not 3 <= n <= MAX_POINTS:
        raise ValueError("n out of range")
    raw = construction.get("points") if isinstance(construction, dict) else None
    if not isinstance(raw, list) or len(raw) != n:
        raise ValueError(f"points must be a list of exactly {n} pairs")
    points = []
    for item in raw:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"point {item!r} malformed")
        points.append((_coord(item[0]), _coord(item[1])))
    if len(set(points)) != n:
        raise ValueError("repeated point")
    best = None
    for (ax, ay), (bx, by), (cx, cy) in combinations(points, 3):
        area = abs((bx - ax) * (cy - ay) - (cx - ax) * (by - ay)) / 2
        if best is None or area < best:
            best = area
            if best == 0:
                break
    return best
