"""Ring loading lower-bound instances (AlphaEvolve problem 61).

An instance is m pairs (u_i, v_i) of nonnegative rationals with u_i + v_i <= 1.
Its value is min over z in prod {v_i, -u_i} of max_{1<=k<m} |sum_{i<=k} z_i -
sum_{i>k} z_i|; every instance value is a lower bound on the constant C.
Larger is better. Exhaustive over 2^m assignments in integer arithmetic.
"""

from fractions import Fraction
from math import lcm

DESCRIPTION = (
    "Ring loading instance: m pairs (u_i, v_i) of nonnegative rationals with u_i + v_i <= 1. "
    "Value = min over all 2^m choices z_i in {v_i, -u_i} of max over k=1..m-1 of "
    "|sum_{i<=k} z_i - sum_{i>k} z_i|. Larger is better (it lower-bounds the ring loading "
    "constant). Output: {\"pairs\": [[u_1, v_1], ..., [u_m, v_m]]} with each entry a decimal or "
    "fraction string such as \"0.3125\" or \"5/16\" (exact rationals are used; floats are rejected)."
)
MAX_M = 18


MAX_LITERAL_CHARS = 400


def _rational(text):
    if isinstance(text, bool) or not isinstance(text, (str, int)):
        raise ValueError(f"entry {text!r} must be a string or int")
    if isinstance(text, str) and len(text) > MAX_LITERAL_CHARS:
        raise ValueError("literal too long")
    try:
        value = Fraction(text)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"bad rational literal {text!r}: {exc}") from None
    if value < 0:
        raise ValueError(f"entry {text!r} is negative")
    return value


def verify(construction, parameters) -> Fraction:
    m = int(parameters["m"])
    if not 1 <= m <= MAX_M:
        raise ValueError("m out of range")
    raw = construction.get("pairs") if isinstance(construction, dict) else None
    if not isinstance(raw, list) or len(raw) != m:
        raise ValueError(f"pairs must be a list of exactly {m} pairs")
    pairs = []
    for item in raw:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"pair {item!r} malformed")
        u, v = _rational(item[0]), _rational(item[1])
        if u + v > 1:
            raise ValueError(f"pair {item!r} has u + v > 1")
        pairs.append((u, v))
    scale = lcm(*(x.denominator for pair in pairs for x in pair))
    us = [int(u * scale) for u, _ in pairs]
    vs = [int(v * scale) for _, v in pairs]
    best = None
    # Enumerate assignments by index bits; prefix sums in integers.
    for bits in range(1 << m):
        total = 0
        z = []
        for i in range(m):
            zi = vs[i] if bits >> i & 1 else -us[i]
            z.append(zi)
            total += zi
        worst = 0
        prefix = 0
        for k in range(m - 1):
            prefix += z[k]
            gap = abs(2 * prefix - total)
            if gap > worst:
                worst = gap
                if best is not None and worst >= best:
                    break
        if best is None or worst < best:
            best = worst
    return Fraction(best, scale)
