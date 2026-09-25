"""Checks for the negative-outer-temperature dichotomy.  Independent of repository code."""
import itertools
import math
import sys
from fractions import Fraction as Fr

import numpy as np

rng = np.random.default_rng(7)
FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + " " + detail)
    if not ok:
        FAILS.append(name)


def boltz_rows(X, c):
    Z = c * X
    Z = Z - Z.max(axis=-1, keepdims=True)
    W = np.exp(Z)
    return (X * W).sum(-1) / W.sum(-1)


def reward_batch(A, t, tau):
    S = boltz_rows(np.swapaxes(A, 1, 2), t)
    return boltz_rows(S, tau)


def scores_batch(A, t):
    return boltz_rows(np.swapaxes(A, 1, 2), t)


def s_k(k, N, E):
    return k * E / (N + k * (E - 1))


# ---------------------------------------------------------------------------
# 1. Lemma: m <= R_tau <= mean and R_tau - m <= (M-1)/(e|tau|)
# ---------------------------------------------------------------------------
print("=== 1. Outer bounds for tau <= 0 ===")
worst = 0.0
ok = True
for _ in range(20000):
    M = int(rng.integers(1, 7))
    g = rng.random(M)
    tau = -rng.random() * 20
    w = np.exp(tau * (g - g.min()))
    R = (g * w).sum() / w.sum()
    m, mean = g.min(), g.mean()
    if not (m - 1e-13 <= R <= mean + 1e-13):
        ok = False
    if M > 1 and R - m > (M - 1) / (math.e * abs(tau)) + 1e-13:
        ok = False
    worst = max(worst, (R - m) * math.e * abs(tau) / max(M - 1, 1))
check("m <= R <= mean and R - m <= (M-1)/(e|tau|) on 20000 random instances", ok, f"max ratio (R-m)e|tau|/(M-1) = {worst:.4f}")
# strictness of the mean bound for tau < 0 with nonconstant g
g = np.array([0.2, 0.7, 0.9]); tau = -2.0
w = np.exp(tau * g); R = (g * w).sum() / w.sum()
check("mean bound strict for tau<0, nonconstant g", R < g.mean() - 1e-6, f"R={R:.6f} mean={g.mean():.6f}")

# ---------------------------------------------------------------------------
# 2. Corollary A (divisible case): grid maxima are exactly the balanced pure allocations
# ---------------------------------------------------------------------------
print("=== 2. Divisible case ===")
def rows_grid(M, G):
    return np.array([[k / G for k in ks] for ks in itertools.product(range(G + 1), repeat=M) if sum(ks) <= G])

def enumerate_all(rows, N, t, tau, chunk=300000):
    K = len(rows); total = K ** N
    best = -1.0; args = []
    for start in range(0, total, chunk):
        idx = np.arange(start, min(start + chunk, total))
        digits = np.zeros((len(idx), N), dtype=np.int64); rem = idx.copy()
        for r in range(N - 1, -1, -1):
            digits[:, r] = rem % K; rem //= K
        A = rows[digits]
        R = reward_batch(A, t, tau)
        m = R.max()
        if m > best + 1e-10:
            best = m; args = []
        if m >= best - 1e-10:
            args.extend([digits[s] for s in np.nonzero(R >= best - 1e-10)[0]])
    return best, [rows[list(a)] for a in args]

def is_balanced_pure(A, q):
    return bool(np.all(np.isin(A, [0.0, 1.0])) and np.all(A.sum(axis=1) == 1) and np.all(A.sum(axis=0) == q))

for (N, M, G) in [(4, 2, 4), (6, 2, 2), (3, 3, 4), (4, 4, 2), (6, 3, 2)]:
    rows = rows_grid(M, G)
    q = N // M
    for t in [0.5, 2.0, 6.0]:
        E = math.exp(t)
        for tau in [0.0, -1.0, -4.0, -16.0]:
            best, mats = enumerate_all(rows, N, t, tau)
            ok = abs(best - s_k(q, N, E)) < 1e-12 and all(is_balanced_pure(A, q) for A in mats) and len(mats) > 0
            check(f"divisible N={N} M={M} G={G} t={t} tau={tau}: max = s_q only at balanced pure", ok, f"max={best:.12f} s_q={s_k(q,N,E):.12f} #argmax={len(mats)}")

# ---------------------------------------------------------------------------
# 3. Theorem B witnesses (exact rational arithmetic with E = 4, entries in {0,1/2,1})
# ---------------------------------------------------------------------------
print("=== 3. Indivisible witnesses ===")
def f_exact(col, E_sqrt):
    # entries in {0, 1/2, 1}; e^{t x} = E_sqrt^{2x}
    num = sum(x * E_sqrt ** int(2 * x) for x in col)
    den = sum(E_sqrt ** int(2 * x) for x in col)
    return Fr(num, den)
E_sqrt = 2  # E = 4
N, M = 3, 2
s1 = Fr(1 * 4, N + 1 * 3)
check("(3,2) E=4: s_1 = 2/3", s1 == Fr(2, 3))
check("(3,2) E=4: t s_1 < 1", float(s1) * math.log(4) < 1, f"t s_1 = {float(s1)*math.log(4):.4f}")
spread = f_exact([Fr(1), Fr(0), Fr(1, 2)], E_sqrt)
check("(3,2) E=4: spread column score 5/7", spread == Fr(5, 7))
delta = spread - s1
check("(3,2) E=4: delta = 1/21 and threshold -42/e", delta == Fr(1, 21) and abs(-2 * (M - 1) / (math.e * float(delta)) - (-42 / math.e)) < 1e-12, f"threshold={-42/math.e:.4f}")
s2 = Fr(2 * 4, N + 2 * 3)
check("(3,2) E=4: tau=0 balanced value 7/9 > 5/7", (s2 + s1) / 2 == Fr(7, 9) and Fr(7, 9) > Fr(5, 7))
# every binary allocation has bottleneck <= s_q (8)
def binary_allocs(N, M):
    choices = [tuple(0 for _ in range(M))] + [tuple(1 if j == k else 0 for j in range(M)) for k in range(M)]
    for rows in itertools.product(choices, repeat=N):
        yield np.array(rows, dtype=float)
for (N, M) in [(3, 2), (5, 2), (5, 3), (4, 3), (2, 3), (7, 3)]:
    q, r = divmod(N, M)
    for t in [0.5, 1.386294361119890, 4.0]:
        E = math.exp(t)
        worst = -1.0
        for A in binary_allocs(N, M):
            worst = max(worst, scores_batch(A[None], t)[0].min())
        check(f"pure bottleneck ceiling (N,M)=({N},{M}) t={t:.3f}: max_pure min-score = s_q", abs(worst - s_k(q, N, E)) < 1e-12, f"{worst:.10f} vs s_q={s_k(q,N,E):.10f}")
# (5,3) witness
N, M = 5, 3
s1 = Fr(4, N + 3)
c1 = f_exact([Fr(1), Fr(1, 2), Fr(0), Fr(0), Fr(0)], E_sqrt)
c2 = f_exact([Fr(1), Fr(1), Fr(0), Fr(0), Fr(0)], E_sqrt)
check("(5,3) E=4: s_1 = 1/2, columns 5/9 and 8/11, delta = 1/18", s1 == Fr(1, 2) and c1 == Fr(5, 9) and c2 == Fr(8, 11) and min(c1, c2) - s1 == Fr(1, 18))
# E = 64 boundary
E_sqrt = 8
N, M = 3, 2
s1 = Fr(64, N + 63)
check("(3,2) E=64: s_1 = 32/33 and t s_1 > 1", s1 == Fr(32, 33) and float(s1) * math.log(64) > 1)
spread = f_exact([Fr(1), Fr(0), Fr(1, 2)], E_sqrt)
check("(3,2) E=64: spread column 68/73 < 32/33", spread == Fr(68, 73) and spread < s1)
# crumb threshold function h(y) at E=4, (3,2): h'(0) > 0
q, Nn = 1, 3
E = 4.0; t = math.log(4)
hprime0 = (q * E + Nn - q) * (1 - t * (q * E / (q * E + Nn - q)))
check("(3,2) E=4: h'(0) = (qE+N-q)(1 - t s_q) > 0", hprime0 > 0, f"h'(0)={hprime0:.4f}")
ys = np.linspace(1e-6, 1, 2000)
hy = ys * (q * E + Nn - q) - q * E * (1 - np.exp(-t * ys))
check("(3,2) E=4: h(y) > 0 on (0,1]", bool(np.all(hy > 0)))
# spread construction for (3,2), (5,3): columns exceed s_q via h(y_j) > 0
# general claim: y* < 1/ceil(M/r) whenever t s_q <= 1; sample random (t, N, M) with t s_q <= 1
ok = True
for _ in range(3000):
    N = int(rng.integers(2, 20)); M = int(rng.integers(2, 12))
    q, r = divmod(N, M)
    if r == 0:
        continue
    t = rng.random() * 6
    E = math.exp(t)
    sq = s_k(q, N, E)
    if t * sq > 1:
        continue
    y = 1 / math.ceil(M / r)
    hval = y * (q * E + N - q) - q * E * (1 - math.exp(-t * y))
    if hval <= 0:
        ok = False
check("h(1/ceil(M/r)) > 0 whenever t s_q <= 1 (random sample)", ok)

# ---------------------------------------------------------------------------
# 4. Finite-tau crossover for (3,2), E = 4: pure vs fractional grid
# ---------------------------------------------------------------------------
print("=== 4. Crossover scan for (3,2), E=4 ===")
N, M = 3, 2
t = math.log(4)
rows = rows_grid(2, 20)
pure_rows = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
scan = {}
for tau in [-16.0, -8.0, -7.0, -6.0, -5.5, -5.0, -4.5, -4.0, -2.0, -1.0, 0.0]:
    best_pure, _ = enumerate_all(pure_rows, N, t, tau)
    best_grid, mats = enumerate_all(rows, N, t, tau)
    frac = best_grid > best_pure + 1e-10
    scan[tau] = (best_pure, best_grid, frac)
    print(f"  tau={tau:6.2f}: best pure={best_pure:.10f} best grid(1/20)={best_grid:.10f} fractional wins={frac}")
check("(3,2) E=4: fractional grid beats every pure allocation at tau <= -6", all(scan[x][2] for x in [-16.0, -8.0, -7.0, -6.0]))
check("(3,2) E=4: pure optimal on the grid at tau >= -5", all(not scan[x][2] for x in [-5.0, -4.5, -4.0, -2.0, -1.0, 0.0]))
check("(3,2) E=4: at tau=-16 (below -42/e) fractional wins", scan[-16.0][2])
# finer scan between -6 and -5 (crossover location, reported only)
for tau in np.linspace(-6.0, -5.0, 11):
    best_pure, _ = enumerate_all(pure_rows, N, t, tau)
    best_grid, _ = enumerate_all(rows, N, t, tau)
    print(f"  tau={tau:7.3f}: pure={best_pure:.10f} grid={best_grid:.10f} diff={best_grid-best_pure:+.3e}")

print()
print("FAILURES:", FAILS if FAILS else "none")
