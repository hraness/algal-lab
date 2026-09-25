#!/usr/bin/env python3
"""kplane.py -- numerical value of the coplanar constant K (Section 4.4, hypothesis H2).

K = (1/120) * sum over primitive v in Z^3 (one of each pair +-v) of  int phi_v(s)^5 ds,
where phi_v is the density of v.U with U uniform on [0,1]^3.  Heuristically
Z_plane(n) = (K + o(1)) n^11 (each lattice plane v.x = k carries ~ n^2 phi_v(k/n) grid points).

phi_v depends only on the multiset of |v_i|.  One nonzero entry: int phi^5 = 1.  Two nonzero
entries a <= b: phi is a trapezoid and int phi^5 = (b - 2a/3)/b^5.  Three nonzero entries: phi is
piecewise quadratic with breakpoints at the subset sums; int phi^5 is computed exactly (up to
floating point) with 6-point Gauss-Legendre per piece (degree 10 integrand).

Prints the partial sums S(A) = sum over max|v_i| <= A and a tail fit S(A) ~ K - beta/A - gamma/A^2.
This is a numerical estimate, not a proof: the tail fit is an extrapolation.
Usage: kplane.py [Amax]
"""
import sys
from math import gcd
import numpy as np

AMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 60
GX, GW = np.polynomial.legendre.leggauss(6)


def int_phi5_three(a, b, c):
    """int phi^5 for phi = density of aU1 + bU2 + cU3, a, b, c > 0."""
    eps = [(e1, e2, e3) for e1 in (0, 1) for e2 in (0, 1) for e3 in (0, 1)]
    shifts = np.array([e1 * a + e2 * b + e3 * c for e1, e2, e3 in eps], dtype=float)
    signs = np.array([(-1) ** (e1 + e2 + e3) for e1, e2, e3 in eps], dtype=float)
    bps = np.unique(shifts)
    lo, hi = bps[:-1], bps[1:]
    mid, half = (lo + hi) / 2, (hi - lo) / 2
    s = (mid[:, None] + half[:, None] * GX[None, :]).ravel()
    w = (half[:, None] * GW[None, :]).ravel()
    d = np.clip(s[:, None] - shifts[None, :], 0, None)
    phi = (d * d * signs[None, :]).sum(axis=1) / (2.0 * a * b * c)
    return float((w * phi ** 5).sum())


def contribution(v):
    a = sorted(abs(x) for x in v if x != 0)
    if len(a) == 1:
        return 1.0
    if len(a) == 2:
        p, q = a
        return (q - 2.0 * p / 3.0) / q ** 5
    return int_phi5_three(*a)


cache = {}
shell = {}  # shell[A] = sum of contributions of primitive v (up to sign) with max|v_i| = A
for x in range(0, AMAX + 1):
    for y in range(-AMAX, AMAX + 1):
        for z in range(-AMAX, AMAX + 1):
            # one representative of +-v: first nonzero coordinate positive
            if x < 0 or (x == 0 and (y < 0 or (y == 0 and z <= 0))):
                continue
            if gcd(gcd(x, abs(y)), abs(z)) != 1:
                continue
            key = tuple(sorted((x, abs(y), abs(z))))
            if key not in cache:
                cache[key] = contribution(key)
            A = max(x, abs(y), abs(z))
            shell[A] = shell.get(A, 0.0) + cache[key]

S, run = {}, 0.0
for A in range(1, AMAX + 1):
    run += shell.get(A, 0.0)
    S[A] = run / 120.0
for A in (1, 2, 5, 10, 20, 30, 40, 50, 60, 80, 100):
    if A <= AMAX:
        print(f"A={A} partial_K={S[A]:.6f}")
# Proved tail bound: every v with max|v_i| = A has int phi_v^5 <= (sup phi_v)^4 <= A^-4, and there
# are at most 12A^2 + 1 such v up to sign, so the tail beyond AMAX is at most
# (1/120) * (12/AMAX + 1/(3 AMAX^3)).
tail = (12.0 / AMAX + 1.0 / (3.0 * AMAX ** 3)) / 120.0
print(f"bracket: {S[AMAX]:.6f} <= K <= {S[AMAX] + tail:.6f} (partial sum + proved tail bound {tail:.6f})")
As = np.array([A for A in range(AMAX // 3, AMAX + 1)], dtype=float)
Ys = np.array([S[int(A)] for A in As])
M = np.vstack([np.ones_like(As), -1 / As, -1 / As ** 2]).T
coef, *_ = np.linalg.lstsq(M, Ys, rcond=None)
print(f"tail fit over A in [{AMAX // 3},{AMAX}]: K ~ {coef[0]:.5f} (beta={coef[1]:.4f}, gamma={coef[2]:.4f})")
print(f"threshold (4/5)^4/5 = {0.8 ** 4 / 5:.5f}; 0.8*(5K)^(-1/4) at fitted K = {0.8 * (5 * coef[0]) ** -0.25:.4f}")
