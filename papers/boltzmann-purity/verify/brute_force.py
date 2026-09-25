"""Brute-force checks of the nested Boltzmann allocation model.

Independent of any repository code.  Uses only numpy and the standard library.

Model.  A is an N x M matrix with nonnegative entries and row sums at most one.
Task scores S_j = B_t(A_{:,j}) over all N agents, reward R = B_tau(S) over all
M tasks, where B_c(x) = sum_i x_i e^{c x_i} / sum_i e^{c x_i}.

Checks performed (each prints PASS/FAIL):
  1. Positive temperatures: the maximum over a fine fractional grid (slack
     rows included) equals the maximum over pure allocations, and every grid
     point within 1e-9 of the maximum is pure.  Random-restart projected
     gradient ascent finds no better point and every run that reaches the
     maximum ends at a pure matrix.
  2. Nonpositive inner temperature: the grid maximum equals the homogeneous
     optimum (sigma(tau,M) for tau>0, 1/M for tau<=0).
  3. Square instances with t>0, tau<=0: the grid maximum is sigma(t,n) and is
     attained on the grid exactly at permutation matrices.
  4. Two agents, two tasks: grid maximum equals sigma(max{t,tau,0},2) for
     temperature pairs of every sign pattern; maximizer table for t,tau>0.
  5. Two agents, M tasks: pure maximum equals max{H,D} and the maximizer
     counts M(M-1), M^2, M follow the crossover tau_*(t,M).
  6. Three agents, three tasks: pure maximum equals max{P,Q,H} with the
     five-row classification and counts 6/24/18/21/3.
"""
import itertools
import json
import math
import sys
import numpy as np

rng = np.random.default_rng(20260925)
RESULTS = {}
FAILS = []


def check(name, ok, detail=""):
    tag = "PASS" if ok else "FAIL"
    print(f"{tag} {name} {detail}")
    if not ok:
        FAILS.append(name)


def boltz_rows(X, c):
    """Boltzmann mean of each row of X (shape (..., n)) at temperature c."""
    Z = c * X
    Z = Z - Z.max(axis=-1, keepdims=True)
    W = np.exp(Z)
    return (X * W).sum(-1) / W.sum(-1)


def reward_batch(A, t, tau):
    """A has shape (B, N, M).  Returns rewards of shape (B,)."""
    S = boltz_rows(np.swapaxes(A, 1, 2), t)  # (B, M)
    return boltz_rows(S, tau)


def sigma(c, n):
    return math.exp(c) / (math.exp(c) + n - 1)


def grid_rows(M, G):
    """All rows k/G with k in Z_{>=0}^M and sum k <= G (slack allowed)."""
    rows = []
    for ks in itertools.product(range(G + 1), repeat=M):
        if sum(ks) <= G:
            rows.append([k / G for k in ks])
    return np.array(rows)


def pure_rows(M):
    return np.eye(M)


def is_pure(A, tol=1e-12):
    return bool(np.all(np.abs(A.max(axis=1) - 1.0) < tol) and np.all(np.abs(A.sum(axis=1) - 1.0) < tol))


def enumerate_max(rows, N, t, tau, chunk=200000):
    """Maximum of R over all N-tuples of the given rows.  Returns
    (max value, list of argmax index tuples within 1e-9, best non-pure value)."""
    K = len(rows)
    total = K ** N
    best = -1.0
    best_nonpure = -1.0
    argmax = []
    for start in range(0, total, chunk):
        idx = np.arange(start, min(start + chunk, total))
        digits = np.zeros((len(idx), N), dtype=np.int64)
        rem = idx.copy()
        for r in range(N - 1, -1, -1):
            digits[:, r] = rem % K
            rem //= K
        A = rows[digits]  # (B, N, M)
        R = reward_batch(A, t, tau)
        pure = np.all(np.abs(A.max(axis=2) - 1.0) < 1e-12, axis=1)
        m = R.max()
        if m > best + 1e-9:
            best = m
            argmax = []
        if m >= best - 1e-9:
            sel = np.nonzero(R >= best - 1e-9)[0]
            argmax.extend([tuple(digits[s]) for s in sel])
        if (~pure).any():
            best_nonpure = max(best_nonpure, R[~pure].max())
    # prune argmax to the final tolerance band
    return best, argmax, best_nonpure


def project_row(x):
    """Euclidean projection onto {x >= 0, sum x <= 1}."""
    y = np.maximum(x, 0.0)
    if y.sum() <= 1.0:
        return y
    # project onto the unit simplex
    u = np.sort(x)[::-1]
    css = np.cumsum(u)
    rho = np.nonzero(u * np.arange(1, len(x) + 1) > (css - 1))[0][-1]
    theta = (css[rho] - 1) / (rho + 1)
    return np.maximum(x - theta, 0.0)


def grad_R(A, t, tau):
    """Analytic gradient dR/dA via the identity dR/da_ij = W_j p_ij h_ij."""
    N, M = A.shape
    E = np.exp(t * (A - A.max(axis=0, keepdims=True)))
    p = E / E.sum(axis=0, keepdims=True)
    S = (A * p).sum(axis=0)
    h = 1.0 + t * (A - S[None, :])
    F = np.exp(tau * (S - S.max()))
    P = F / F.sum()
    R = (S * P).sum()
    W = P * (1.0 + tau * (S - R))
    return W[None, :] * p * h, R


def project_rows(X):
    """Euclidean projection of every row of X (shape (B, N, M)) onto
    {x >= 0, sum x <= 1}, vectorized."""
    Y = np.maximum(X, 0.0)
    over = Y.sum(-1) > 1.0
    if not over.any():
        return Y
    U = -np.sort(-X, axis=-1)
    css = np.cumsum(U, axis=-1)
    k = np.arange(1, X.shape[-1] + 1)
    cond = U * k > (css - 1.0)
    rho = cond.shape[-1] - 1 - np.argmax(cond[..., ::-1], axis=-1)
    theta = (np.take_along_axis(css, rho[..., None], axis=-1)[..., 0] - 1.0) / (rho + 1)
    Z = np.maximum(X - theta[..., None], 0.0)
    return np.where(over[..., None], Z, Y)


def grad_R_batch(A, t, tau):
    """Analytic gradient of R for a batch A of shape (B, N, M)."""
    E = np.exp(t * (A - A.max(axis=1, keepdims=True)))
    p = E / E.sum(axis=1, keepdims=True)
    S = (A * p).sum(axis=1)                      # (B, M)
    h = 1.0 + t * (A - S[:, None, :])
    F = np.exp(tau * (S - S.max(axis=1, keepdims=True)))
    P = F / F.sum(axis=1, keepdims=True)
    R = (S * P).sum(axis=1)                      # (B,)
    W = P * (1.0 + tau * (S - R[:, None]))
    return W[:, None, :] * p * h, R


def ascent(A0, t, tau, iters=600):
    """Projected gradient ascent with per-run adaptive steps.  A0 has shape
    (B, N, M).  Returns the end points, their rewards and the norm of the
    projected gradient step at the end (a stationarity measure)."""
    A = A0.copy()
    B = A.shape[0]
    step = np.full(B, 0.5)
    _, R = grad_R_batch(A, t, tau)
    for _ in range(iters):
        g, R = grad_R_batch(A, t, tau)
        A_new = project_rows(A + step[:, None, None] * g)
        R_new = reward_batch(A_new, t, tau)
        acc = R_new >= R
        A = np.where(acc[:, None, None], A_new, A)
        step = np.where(acc, np.minimum(step * 1.2, 4.0), step * 0.5)
        step = np.maximum(step, 1e-14)
    g, R = grad_R_batch(A, t, tau)
    stat = np.abs(project_rows(A + 1e-3 * g) - A).max(axis=(1, 2)) / 1e-3
    return A, R, stat


def random_feasible(N, M):
    A = rng.random((N, M))
    scale = rng.random((N, 1)) * 1.2  # some rows with slack, some over budget
    A = A / A.sum(axis=1, keepdims=True) * scale
    return np.array([project_row(A[i]) for i in range(N)])


# ---------------------------------------------------------------------------
# 1. Purity at positive temperatures
# ---------------------------------------------------------------------------
print("=== 1. Purity for t, tau > 0 ===")
GRIDS = {(2, 2): 20, (2, 3): 10, (3, 2): 10, (3, 3): 6, (2, 4): 8, (4, 2): 6, (4, 3): 4, (3, 4): 4}
NRESTART, NITER = 40, 1500
TEMPS = [(0.5, 0.5), (1.0, 1.0), (2.0, 1.0), (1.0, 3.0), (3.0, 0.25), (0.1, 0.1), (5.0, 5.0), (8.0, 1.0), (1.0, 8.0)]
purity_summary = {}
for (N, M), G in GRIDS.items():
    rows = grid_rows(M, G)
    for (t, tau) in TEMPS:
        best, argmax, best_nonpure = enumerate_max(rows, N, t, tau)
        A_star = rows[list(argmax[0])]
        pure_best = max(reward_batch(np.eye(M)[list(c)][None], t, tau)[0] for c in itertools.product(range(M), repeat=N))
        all_pure = all(is_pure(rows[list(ix)]) for ix in argmax)
        # random restarts of projected gradient ascent (vectorized).  The
        # landscape has non-global local maxima (for example matrices with an
        # empty row at large temperatures, which are KKT points of the
        # constrained problem), so not every run reaches the global maximum.
        # The checks are: no run exceeds the pure maximum, and every run that
        # reaches the maximum (within 1e-7) ends at a pure matrix.  The number
        # of runs reaching the maximum and the number of stationary runs ending
        # at non-pure matrices (all with a slack row, i.e. a row sum below one)
        # are reported for information.
        starts = np.stack([random_feasible(N, M) for _ in range(NRESTART)])
        A_end, R_end, stat = ascent(starts, t, tau, iters=NITER)
        pure_end = np.array([is_pure(A_end[b], 1e-6) for b in range(NRESTART)])
        best_found = R_end.max()
        near = R_end >= pure_best - 1e-7
        stationary = stat < 1e-7
        nonpure_stat = stationary & ~pure_end
        slack_rows = np.array([(A_end[b].sum(1) < 1 - 1e-6).any() for b in range(NRESTART)])
        ok = (abs(best - pure_best) < 1e-12 and all_pure and best_nonpure < pure_best - 1e-12
              and best_found <= pure_best + 1e-9 and pure_end[near].all())
        check(f"purity N={N} M={M} t={t} tau={tau}", ok,
              f"grid max={best:.12f} pure max={pure_best:.12f} best fractional={best_nonpure:.12f} "
              f"gap={pure_best-best_nonpure:.3e} ascent best={best_found:.12f} runs at max={int(near.sum())}/{NRESTART} "
              f"stationary non-pure runs={int(nonpure_stat.sum())} (with slack row={int((nonpure_stat & slack_rows).sum())})")
        purity_summary[f"{N}x{M} t={t} tau={tau}"] = {"grid_G": G, "max": best, "best_fractional": best_nonpure,
                                                    "restarts_at_max": int(near.sum())}
RESULTS["purity"] = purity_summary

# ---------------------------------------------------------------------------
# 2. Nonpositive inner temperature: no heterogeneity gain
# ---------------------------------------------------------------------------
print("=== 2. t <= 0: grid maximum equals the homogeneous optimum ===")
for (N, M), G in [((2, 2), 20), ((3, 2), 10), ((2, 3), 10), ((3, 3), 6), ((4, 3), 4)]:
    rows = grid_rows(M, G)
    for (t, tau) in [(0.0, 1.0), (-1.0, 2.0), (-3.0, 0.5), (0.0, 0.0), (-1.0, -1.0), (-2.0, 0.0), (0.0, -3.0), (-0.5, 4.0)]:
        best, argmax, _ = enumerate_max(rows, N, t, tau)
        hom = sigma(tau, M) if tau > 0 else 1.0 / M
        # the grid contains the homogeneous optimizer only if G is divisible by M for tau<=0
        ok = best <= hom + 1e-12 and (best >= hom - 1e-12 if (tau > 0 or G % M == 0) else True)
        check(f"t<=0 N={N} M={M} t={t} tau={tau}", ok, f"grid max={best:.12f} hom={hom:.12f}")

# ---------------------------------------------------------------------------
# 3. Square instances, t > 0, tau <= 0: permutation optimum sigma(t,n)
# ---------------------------------------------------------------------------
print("=== 3. N=M=n, t>0, tau<=0: maximum sigma(t,n) at permutations only ===")
for n, G in [(2, 20), (3, 6)]:
    rows = grid_rows(n, G)
    for (t, tau) in [(1.0, 0.0), (2.0, -1.0), (0.3, -5.0), (5.0, -0.1)]:
        best, argmax, best_nonpure = enumerate_max(rows, n, t, tau)
        perms = [rows[list(ix)] for ix in argmax]
        all_perm = all(is_pure(A) and np.all(A.sum(axis=0) == 1.0) for A in perms)
        ok = abs(best - sigma(t, n)) < 1e-12 and all_perm and len(argmax) == math.factorial(n)
        check(f"square n={n} t={t} tau={tau}", ok, f"max={best:.12f} sigma={sigma(t,n):.12f} #argmax={len(argmax)}")

# ---------------------------------------------------------------------------
# 4. Two agents, two tasks: exact solution for every sign pattern
# ---------------------------------------------------------------------------
print("=== 4. 2x2 exact solution ===")
rows22 = grid_rows(2, 40)
for (t, tau) in [(1.0, 0.5), (0.5, 1.0), (1.0, 1.0), (2.0, -1.0), (-1.0, 2.0), (-1.0, -1.0), (0.0, 0.0), (3.0, 3.0), (0.2, 0.7)]:
    best, argmax, _ = enumerate_max(rows22, 2, t, tau)
    target = sigma(max(t, tau, 0.0), 2)
    mats = [rows22[list(ix)] for ix in argmax]
    detail = f"max={best:.12f} target={target:.12f} #argmax={len(argmax)}"
    ok = abs(best - target) < 1e-12
    if t > 0 and tau > 0:
        perms = sum(1 for A in mats if is_pure(A) and np.all(A.sum(axis=0) == 1.0))
        conc = sum(1 for A in mats if is_pure(A) and np.any(A.sum(axis=0) == 2.0))
        if t > tau:
            ok = ok and perms == 2 and conc == 0 and len(mats) == 2
        elif tau > t:
            ok = ok and conc == 2 and perms == 0 and len(mats) == 2
        else:
            ok = ok and conc == 2 and perms == 2 and len(mats) == 4
        detail += f" perms={perms} conc={conc}"
    check(f"2x2 t={t} tau={tau}", ok, detail)

# closed form R = 1/2 + g_t(d) + g_tau(u) on full-budget rows
def g(c, z):
    return z * math.tanh(c * z)
maxerr = 0.0
for _ in range(2000):
    a, b = rng.random(), rng.random()
    t, tau = rng.normal() * 3, rng.normal() * 3
    A = np.array([[a, 1 - a], [b, 1 - b]])
    R = reward_batch(A[None], t, tau)[0]
    u, d = (a + b - 1) / 2, (a - b) / 2
    maxerr = max(maxerr, abs(R - (0.5 + g(t, d) + g(tau, u))))
check("2x2 closed form R = 1/2 + g_t(d) + g_tau(u)", maxerr < 1e-12, f"max error {maxerr:.2e}")

# ---------------------------------------------------------------------------
# 5. Two agents, M tasks: max{H, D} and maximizer counts
# ---------------------------------------------------------------------------
print("=== 5. 2 x M pure classification ===")
def two_agent_HD(t, tau, M):
    E = math.exp(t)
    b = E / (E + 1)
    H = math.exp(tau) / (math.exp(tau) + M - 1)
    D = 2 * b * math.exp(tau * b) / (2 * math.exp(tau * b) + M - 2)
    return H, D

def crossover(t, M):
    # unique root of D(tau) = H(tau) in tau > 0, by bisection on [t, t + log(M-1)] (M>2) or exactly t (M=2)
    if M == 2:
        return t
    lo, hi = t, t + math.log(M - 1)
    for _ in range(200):
        mid = (lo + hi) / 2
        H, D = two_agent_HD(t, mid, M)
        if D > H:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

for M in [2, 3, 4, 6]:
    for t in [0.3, 1.0, 2.5]:
        ts = crossover(t, M)
        Hlo, Dlo = two_agent_HD(t, ts - 1e-9, M) if M > 2 else (None, None)
        ok_bounds = (ts == t) if M == 2 else (t < ts < t + math.log(M - 1))
        for tau, expect in [(0.5 * ts, "sep"), (ts, "tie"), (ts + 0.5, "conc")]:
            H, D = two_agent_HD(t, tau, M)
            pure = {}
            for c in itertools.product(range(M), repeat=2):
                pure[c] = reward_batch(np.eye(M)[list(c)][None], t, tau)[0]
            best = max(pure.values())
            arg = [c for c, v in pure.items() if v >= best - 1e-9]
            nsep = sum(1 for c in arg if c[0] != c[1])
            nconc = sum(1 for c in arg if c[0] == c[1])
            if expect == "sep":
                ok = abs(best - D) < 1e-12 and nsep == M * (M - 1) and nconc == 0
            elif expect == "conc":
                ok = abs(best - H) < 1e-12 and nconc == M and nsep == 0
            else:
                ok = abs(H - D) < 1e-8 and nconc == M and nsep == M * (M - 1)
            check(f"2x{M} t={t} tau={tau:.6f} ({expect})", ok and ok_bounds,
                  f"H={H:.10f} D={D:.10f} max={best:.10f} #sep={nsep} #conc={nconc} tau*={ts:.8f}")
# the 2x3 matched-temperature certificate 1/150 at t = tau = log 2
t = tau = math.log(2)
H, D = two_agent_HD(t, tau, 3)
check("2x3 matched log2 gain > 1/150", D - H > 1 / 150, f"D-H={D-H:.10f} 1/150={1/150:.10f}")

# ---------------------------------------------------------------------------
# 6. Three agents, three tasks: full phase table
# ---------------------------------------------------------------------------
print("=== 6. 3 x 3 phase table ===")
def three_PQH(t, tau):
    E = math.exp(t)
    a = 2 * E / (2 * E + 1)
    b = E / (E + 2)
    P = b
    Q = (a * math.exp(tau * a) + b * math.exp(tau * b)) / (math.exp(tau * a) + math.exp(tau * b) + 1)
    H = math.exp(tau) / (math.exp(tau) + 2)
    return P, Q, H, a, b

def occupancy_type(c):
    counts = sorted([c.count(j) for j in range(3)], reverse=True)
    return tuple(counts)

for t in [0.25, math.log(2), 1.0, 3.0]:
    E = math.exp(t)
    a = 2 * E / (2 * E + 1)
    ell = math.log((2 * E + 1) / 3) / a
    # u(t): root of Q = H in (t, t + log 4)
    lo, hi = t, t + math.log(4)
    for _ in range(200):
        mid = (lo + hi) / 2
        P, Q, H, _, _ = three_PQH(t, mid)
        if Q > H:
            lo = mid
        else:
            hi = mid
    u = (lo + hi) / 2
    ok_thr = 0 < ell < t < u < t + math.log(4)
    table = [(0.5 * ell, {(1, 1, 1): 6}), (ell, {(1, 1, 1): 6, (2, 1, 0): 18}), (0.5 * (ell + u), {(2, 1, 0): 18}),
             (u, {(2, 1, 0): 18, (3, 0, 0): 3}), (u + 1.0, {(3, 0, 0): 3}), (t, {(2, 1, 0): 18})]
    for tau, expect in table:
        pure = {}
        for c in itertools.product(range(3), repeat=3):
            pure[c] = reward_batch(np.eye(3)[list(c)][None], t, tau)[0]
        best = max(pure.values())
        arg = [c for c, v in pure.items() if v >= best - 1e-8]
        counts = {}
        for c in arg:
            counts[occupancy_type(c)] = counts.get(occupancy_type(c), 0) + 1
        P, Q, H, _, _ = three_PQH(t, tau)
        ok = counts == expect and abs(best - max(P, Q, H)) < 1e-12
        check(f"3x3 t={t:.6f} tau={tau:.6f}", ok and ok_thr, f"counts={counts} expected={expect} ell={ell:.6f} u={u:.6f}")
    # certificates at matched t = tau
    if abs(t - math.log(2)) < 1e-15:
        P, Q, H, _, _ = three_PQH(t, t)
        check("3x3 matched log2 gain > 1/295", Q - H > 1 / 295, f"gain={Q-H:.10f}")

print()
print("FAILURES:", FAILS if FAILS else "none")
json.dump(RESULTS, open(sys.argv[1] if len(sys.argv) > 1 else "/dev/null", "w"), indent=1)
