#!/usr/bin/env python3
"""Exact rational enclosures of the sharp softmax thresholds c_n and d_n.

Fresh re-verification for the manuscript "Sharp thresholds for Schur
ordering of the softmax mean".  The certificate uses only the Python
standard library (exact rational arithmetic).  mpmath is used afterwards
for an independent floating cross-check that is not part of the certificate.

Definitions (n >= 3):
    c_n : unique root x > 2 of  f_n(x) = (n-2)(x-2) exp(x) - 4
    d_n : unique root x > 2 of  h_n(x) = (x-2) exp(x) - 2(n-1)

Certificate.  For rational 0 <= x <= 8 we enclose exp(x) as follows:
exp(x) = exp(x/8)^8, and for y = x/8 <= 1 the Taylor polynomial of
degree 30 is a lower bound (all terms are positive), while the omitted
tail is at most its first term divided by 1 - y/32 (each further term
ratio y/(k+1) is at most y/32 < 1).  Raising the positive bounds to the
eighth power encloses exp(x).  Both f_n and h_n are strictly increasing on
[2, 8] (derivatives (n-2)(x-1)exp(x) and (x-1)exp(x)), so certified
opposite signs at the ends of an interval prove that it contains the unique
root.  Bisection then yields an enclosure of width 2^-32 (c_n) or 6*2^-32 (d_n).
"""
from fractions import Fraction as Fr
import json
import sys

DEGREE = 30
REDUCTION = 8
STEPS = 32
SIZES = (3, 4, 5, 8, 16, 32, 57, 58, 64, 128, 1024)

# Decimal enclosures printed in the research notes (strict, deliberately wide).
NOTE_C = {3: ("2.372856", "2.372857"), 4: ("2.217715", "2.217716"),
          8: ("2.083034", "2.083035"), 32: ("2.017727", "2.017728"),
          128: ("2.004278", "2.004279")}
NOTE_D = {3: ("2.372856", "2.372857"), 4: ("2.494985", "2.494986"),
          8: ("2.827909", "2.827910"), 32: ("3.635304", "3.635306"),
          57: ("4.016924", "4.016925"), 58: ("4.028769", "4.028770"),
          128: ("4.586881", "4.586882")}
NOTE_2C = {3: ("4.745712", "4.745713"), 4: ("4.435430", "4.435431"),
           8: ("4.166068", "4.166070"), 32: ("4.035455", "4.035456"),
           57: ("4.019494", "4.019495"), 58: ("4.019149", "4.019150"),
           128: ("4.008556", "4.008557")}


def exp_enclosure(x):
    """Return rationals (lo, hi) with lo <= exp(x) <= hi for 0 <= x <= 8."""
    x = Fr(x)
    assert 0 <= x <= 8
    y = x / REDUCTION
    term = Fr(1)
    partial = Fr(1)
    for k in range(1, DEGREE + 1):
        term = term * y / k
        partial += term
    first_omitted = term * y / (DEGREE + 1)
    ratio = y / (DEGREE + 2)
    assert 0 <= ratio < 1
    upper = partial + first_omitted / (1 - ratio)
    assert 0 < partial <= upper
    return partial ** REDUCTION, upper ** REDUCTION


def f_box(n, x):
    """Enclosure of f_n(x) = (n-2)(x-2)exp(x) - 4 for x >= 2."""
    lo, hi = exp_enclosure(x)
    k = (n - 2) * (Fr(x) - 2)
    assert k >= 0
    return k * lo - 4, k * hi - 4


def h_simplex(n, x):
    """Enclosure of h_n(x) = (x-2)exp(x) - 2(n-1) for x >= 2."""
    lo, hi = exp_enclosure(x)
    k = Fr(x) - 2
    assert k >= 0
    return k * lo - 2 * (n - 1), k * hi - 2 * (n - 1)


def enclose_root(G, lo, hi, steps=STEPS):
    """Bisection with certified endpoint signs for an increasing G."""
    lo, hi = Fr(lo), Fr(hi)
    assert G(lo)[1] < 0, "left endpoint not certified negative"
    assert G(hi)[0] > 0, "right endpoint not certified positive"
    for _ in range(steps):
        mid = (lo + hi) / 2
        a, b = G(mid)
        if b < 0:
            lo = mid
        elif a > 0:
            hi = mid
        else:
            raise RuntimeError("exp enclosure too wide at a bisection point")
    assert G(lo)[1] < 0 < G(hi)[0]
    return lo, hi


def dec_bounds(lo, hi, digits=12):
    """Decimal strings: floor of lo and ceiling of hi at the given digits."""
    s = 10 ** digits
    fl = (lo * s).numerator // (lo * s).denominator
    ce = -((-hi * s).numerator // (-hi * s).denominator)

    def fmt(k):
        return f"{k // s}.{k % s:0{digits}d}"
    return fmt(fl), fmt(ce)


def main():
    c, d = {}, {}
    for n in SIZES:
        c[n] = enclose_root(lambda x: f_box(n, x), 2, 3)
        d[n] = enclose_root(lambda x: h_simplex(n, x), 2, 8)
        assert c[n][1] - c[n][0] == Fr(1, 2 ** STEPS)
        assert d[n][1] - d[n][0] == Fr(6, 2 ** STEPS)
        assert 2 < c[n][0] and 2 < d[n][0]

    # Containment in the decimal tables of the research notes.
    for n, (lo, hi) in NOTE_C.items():
        assert Fr(lo) < c[n][0] and c[n][1] < Fr(hi), ("c", n)
    for n, (lo, hi) in NOTE_D.items():
        assert Fr(lo) < d[n][0] and d[n][1] < Fr(hi), ("d", n)
    for n, (lo, hi) in NOTE_2C.items():
        assert Fr(lo) < 2 * c[n][0] and 2 * c[n][1] < Fr(hi), ("2c", n)

    # Certified monotonicity between listed sizes: c decreases, d increases.
    for n1, n2 in zip(SIZES, SIZES[1:]):
        assert c[n2][1] < c[n1][0], ("c not decreasing", n1, n2)
        assert d[n1][1] < d[n2][0], ("d not increasing", n1, n2)

    # c_3 = d_3 exactly (same defining equation); enclosures must overlap.
    assert max(c[3][0], d[3][0]) < min(c[3][1], d[3][1])

    # Certified dimension-58 crossover of d_n against 2 c_n.
    assert d[57][1] < 2 * c[57][0], "d_57 < 2c_57 not certified"
    assert d[58][0] > 2 * c[58][1], "d_58 > 2c_58 not certified"
    # Every other listed n is separated as well.
    relation = {}
    for n in SIZES:
        if d[n][1] < 2 * c[n][0]:
            relation[n] = "d_n < 2c_n"
        elif d[n][0] > 2 * c[n][1]:
            relation[n] = "d_n > 2c_n"
        else:
            relation[n] = "unresolved"
    assert all(v != "unresolved" for v in relation.values())
    assert all(relation[n] == "d_n < 2c_n" for n in SIZES if n <= 57)
    assert all(relation[n] == "d_n > 2c_n" for n in SIZES if n >= 58)

    # Certified lower bound log 2 > 3/5 (used to place tau = 8 log 2 above
    # every dimension-3 cutoff): exp(3/5) < 2.
    assert exp_enclosure(Fr(3, 5))[1] < 2
    assert Fr(24, 5) > 2 * c[3][1] and Fr(24, 5) > d[3][1] and Fr(24, 5) > c[3][1]

    out = {"degree": DEGREE, "reduction": REDUCTION, "bisection_steps": STEPS,
           "c": {}, "d": {}, "two_c": {}, "relation": relation}
    for n in SIZES:
        out["c"][n] = dec_bounds(*c[n])
        out["d"][n] = dec_bounds(*d[n])
        out["two_c"][n] = dec_bounds(2 * c[n][0], 2 * c[n][1])
    print(json.dumps(out, indent=1))

    # Optional LaTeX table export for the manuscript: roots.py --tex FILE
    if len(sys.argv) == 3 and sys.argv[1] == "--tex":
        rows = []
        for n in SIZES:
            cl, ch = dec_bounds(c[n][0], c[n][1], 10)
            dl, dh = dec_bounds(d[n][0], d[n][1], 10)
            tl, th = dec_bounds(2 * c[n][0], 2 * c[n][1], 10)
            rel = "$-$" if relation[n] == "d_n < 2c_n" else "$+$"
            rows.append(f"{n} & [{cl},\\ {ch}] & [{dl},\\ {dh}] & [{tl},\\ {th}] & {rel} \\\\")
        body = "\n".join(rows)
        table = ("% Generated by verify/roots.py --tex; do not edit by hand.\n"
                 "% Interval ends are outward decimal roundings (10 digits) of exact rational bounds.\n"
                 "\\begin{tabular}{r l l l c}\n\\toprule\n"
                 "$n$ & $c_n$ & $d_n$ & $2c_n$ & $\\sgn(d_n-2c_n)$ \\\\\n\\midrule\n"
                 + body + "\n\\bottomrule\n\\end{tabular}\n")
        with open(sys.argv[2], "w") as fh:
            fh.write(table)
        print(f"wrote {sys.argv[2]}")

    # Independent floating cross-check (not part of the certificate).
    try:
        import mpmath as mp
    except ImportError:
        print("mpmath unavailable; floating cross-check skipped")
        return
    mp.mp.dps = 40
    for n in SIZES:
        cn = 2 + mp.lambertw(mp.mpf(4) / ((n - 2) * mp.e ** 2)).real
        dn = 2 + mp.lambertw(mp.mpf(2) * (n - 1) / mp.e ** 2).real
        tomp = lambda fr: mp.mpf(fr.numerator) / mp.mpf(fr.denominator)
        assert tomp(c[n][0]) <= cn <= tomp(c[n][1]), ("c", n)
        assert tomp(d[n][0]) <= dn <= tomp(d[n][1]), ("d", n)
    sign_changes = []
    prev = None
    for n in range(3, 401):
        cn = 2 + mp.lambertw(mp.mpf(4) / ((n - 2) * mp.e ** 2)).real
        dn = 2 + mp.lambertw(mp.mpf(2) * (n - 1) / mp.e ** 2).real
        sgn = 1 if dn > 2 * cn else -1
        if prev is not None and sgn != prev:
            sign_changes.append(n)
        prev = sgn
    assert sign_changes == [58], sign_changes
    print("floating cross-check: Lambert-W values lie inside every enclosure;"
          " d_n - 2c_n changes sign once, at n = 58, for 3 <= n <= 400")


if __name__ == "__main__":
    main()
