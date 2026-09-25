"""Checks for the concave envelope and the zero-outer-temperature rectangular optimum.
Independent of repository code."""
import itertools
import math
from fractions import Fraction as Fr

import numpy as np

rng = np.random.default_rng(11)
FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + " " + detail)
    if not ok:
        FAILS.append(name)


def f_t(x, t):
    x = np.asarray(x, dtype=float)
    w = np.exp(t * (x - x.max()))
    return (x * w).sum() / w.sum()


def s_k(k, N, E):
    return k * E / (N + k * (E - 1))


def phi(S, N, E):
    k = int(math.floor(S))
    if k >= N:
        return 1.0
    r = S - k
    return (1 - r) * s_k(k, N, E) + r * s_k(k + 1, N, E)


# 1. slopes decreasing, envelope bound, strict contact
print("=== 1. Envelope ===")
ok = True
for N in range(2, 9):
    for t in [0.1, 1.0, 3.0, 10.0]:
        E = math.exp(t)
        d = [s_k(k + 1, N, E) - s_k(k, N, E) for k in range(N)]
        if not all(d[i] > d[i + 1] > 0 for i in range(N - 1)):
            ok = False
        if abs(d[0] - E * N / (N * (N + (E - 1)))) > 1e-12:
            ok = False
check("slopes d_k positive and strictly decreasing, N=2..8", ok)
worst_gap = 1.0
ok = True
for _ in range(20000):
    N = int(rng.integers(2, 7)); t = rng.random() * 8 + 0.01
    E = math.exp(t)
    x = rng.random(N)
    if rng.random() < 0.3:
        x = (x > 0.5).astype(float)  # binary
    val, env = f_t(x, t), phi(x.sum(), N, E)
    binary = bool(np.all(np.isin(x, [0.0, 1.0])))
    if val > env + 1e-12:
        ok = False
    if binary and abs(val - env) > 1e-12:
        ok = False
    if not binary:
        if env - val <= 0:
            ok = False
        worst_gap = min(worst_gap, env - val)
check("f_t <= phi(sum x) with equality exactly at binary points (20000 random)", ok, f"smallest nonbinary gap {worst_gap:.3e}")
# subset-mass bound P(L) <= s_k
ok = True
for _ in range(5000):
    N = int(rng.integers(2, 7)); t = rng.random() * 6 + 0.01; E = math.exp(t)
    x = rng.random(N); p = np.exp(t * x); p /= p.sum()
    for k in range(1, N):
        top = np.sort(p)[::-1][:k].sum()
        if top > s_k(k, N, E) + 1e-12:
            ok = False
check("subset-mass bound P(L) <= s_k (random)", ok)
# N = 1 exception
check("N=1: f_t(x) = x", all(abs(f_t([x], 2.0) - x) < 1e-15 for x in [0.0, 0.3, 1.0]))
# price formula (7)
ok = True
for _ in range(200):
    N = int(rng.integers(2, 5)); t = rng.random() * 4 + 0.1; E = math.exp(t)
    lam = rng.normal(size=N) * 0.5
    G = 10
    best_grid = -1e9
    for ks in itertools.product(range(G + 1), repeat=N):
        x = np.array(ks) / G
        best_grid = max(best_grid, f_t(x, t) - lam @ x)
    best_sub = max(s_k(len(L), N, E) - sum(lam[i] for i in L) for kk in range(N + 1) for L in itertools.combinations(range(N), kk))
    if best_grid > best_sub + 1e-12 or abs(best_grid - best_sub) > 1e-12:
        ok = False
check("price formula max{f_t - lam.x} = max_L {s_|L| - lam(L)} on a tenth grid (200 random prices)", ok)
# gap constant (11)
ok = True
for N in [2, 3, 5]:
    for t in [0.5, 2.0, 6.0]:
        E = math.exp(t)
        const = max(s_k(k, N, E) - k / N for k in range(N + 1))
        best = 0.0
        for _ in range(4000):
            x = rng.random(N)
            best = max(best, phi(x.sum(), N, E) - f_t(x, t))
        for k in range(N + 1):
            x = np.full(N, k / N)
            best = max(best, phi(x.sum(), N, E) - f_t(x, t))
        if best > const + 1e-12 or abs(best - const) > 1e-12:
            ok = False
check("envelope gap max_x(phi - f_t) = max_k (s_k - k/N), attained at constant vectors", ok)

# 2. rectangular optimum at tau = 0
print("=== 2. Rectangular optimum at tau = 0 ===")
def binary_allocs(N, M):
    choices = [tuple(0 for _ in range(M))] + [tuple(1 if j == k else 0 for j in range(M)) for k in range(M)]
    for rows in itertools.product(choices, repeat=N):
        yield np.array(rows, dtype=float)
for (N, M) in [(2, 2), (3, 2), (4, 3), (5, 2), (5, 3), (7, 3), (2, 3), (3, 5)]:
    q, r = divmod(N, M)
    for t in [0.5, 2.0, 5.0]:
        E = math.exp(t)
        target = ((M - r) * s_k(q, N, E) + r * s_k(q + 1, N, E)) / M
        best = -1; args = []
        for A in binary_allocs(N, M):
            cols = A.sum(axis=0)
            val = sum(s_k(int(c), N, E) for c in cols) / M
            if val > best + 1e-12:
                best = val; args = []
            if val >= best - 1e-12:
                args.append(A)
        balanced = all(np.all(A.sum(axis=1) == 1) and set(A.sum(axis=0)).issubset({q, q + 1}) and int((A.sum(axis=0) == q + 1).sum()) == r for A in args)
        check(f"tau=0 binary optimum (N,M)=({N},{M}) t={t}: value and balanced maximizers", abs(best - target) < 1e-12 and balanced, f"best={best:.10f} target={target:.10f} #max={len(args)}")
# fractional grid confirmation for (3,2) and (4,3)
def rows_grid(M, G):
    return np.array([[k / G for k in ks] for ks in itertools.product(range(G + 1), repeat=M) if sum(ks) <= G])
def boltz_rows(X, c):
    Z = c * X; Z = Z - Z.max(axis=-1, keepdims=True); W = np.exp(Z)
    return (X * W).sum(-1) / W.sum(-1)
for (N, M, G) in [(3, 2, 12), (4, 3, 4), (2, 3, 10)]:
    rows = rows_grid(M, G); K = len(rows)
    q, r = divmod(N, M)
    for t in [0.7, 3.0]:
        E = math.exp(t)
        target = ((M - r) * s_k(q, N, E) + r * s_k(q + 1, N, E)) / M
        best = -1; nonpure_best = -1
        for idx in itertools.product(range(K), repeat=N):
            A = rows[list(idx)]
            val = boltz_rows(A.T, t).mean()
            pure = bool(np.all(np.isin(A, [0.0, 1.0])) and np.all(A.sum(axis=1) == 1))
            best = max(best, val)
            if not pure:
                nonpure_best = max(nonpure_best, val)
        check(f"tau=0 grid (N,M)=({N},{M}) G={G} t={t}: max = target, fractional strictly below", abs(best - target) < 1e-12 and nonpure_best < target - 1e-12, f"best={best:.10f} best fractional={nonpure_best:.10f}")
# exceptions: N = 1 and t = 0
check("N=1: every full-budget row gives 1/M", all(abs(np.mean([x for x in row]) - 1 / 3) < 1e-15 for row in [[1, 0, 0], [0.5, 0.5, 0], [1 / 3] * 3]))
check("t=0: objective is total effort/(NM)", abs(boltz_rows(np.array([[0.2, 0.5, 0.3], [0.4, 0.1, 0.5]]).T, 0.0).mean() - 2 / 6) < 1e-15)

print()
print("FAILURES:", FAILS if FAILS else "none")
