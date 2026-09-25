"""Exact certificates, occupancy tables, thresholds and asymptotic coefficients.

Independent of repository code.  Uses fractions, mpmath (60 digits) and numpy.
"""
import itertools
import math
import sys
from fractions import Fraction as Fr

import mpmath as mp
import numpy as np

mp.mp.dps = 60
FAILS = []

def bisect_root(fun, lo, hi, iters=300):
    """Plain bisection for a sign change of fun on [lo, hi]."""
    flo = fun(lo)
    for _ in range(iters):
        mid = (lo + hi) / 2
        fm = fun(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return (lo + hi) / 2



def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + " " + detail)
    if not ok:
        FAILS.append(name)


# ---------------------------------------------------------------------------
# 1. Rational certificates for matched-temperature gains
# ---------------------------------------------------------------------------
print("=== 1. Rational certificates ===")
# 3 agents, t = tau = log 2: r = 2^(4/5) > 12/7, q = sqrt 2 < 3/2
check("12^5 < 16*7^5 (so 2^(4/5) > 12/7)", 12 ** 5 < 16 * 7 ** 5, f"{12**5} < {16*7**5}")
check("9/4 > 2 (so sqrt 2 < 3/2)", Fr(9, 4) > 2)
r_lo, q_hi = Fr(12, 7), Fr(3, 2)
bound = (3 * r_lo - 5) / (10 * (r_lo + q_hi + 1))
check("(3(12/7)-5)/(10(12/7+3/2+1)) = 1/295 exactly", bound == Fr(1, 295), str(bound))
r, q = mp.mpf(2) ** (mp.mpf(4) / 5), mp.sqrt(2)
gain3 = (3 * r - 5) / (10 * (r + q + 1))
# direct evaluation of the reward of occupancy (2,1,0) minus 1/2
E = mp.mpf(2); a = 2 * E / (2 * E + 1); b = E / (E + 2); tau = mp.log(2)
Q = (a * mp.e ** (tau * a) + b * mp.e ** (tau * b)) / (mp.e ** (tau * a) + mp.e ** (tau * b) + 1)
check("closed form (3r-5)/(10(r+q+1)) equals Q - 1/2", abs(gain3 - (Q - mp.mpf(1) / 2)) < mp.mpf(10) ** -50, f"gain={mp.nstr(gain3, 12)}")
check("3x3 matched log2 gain > 1/295 (mp)", gain3 > mp.mpf(1) / 295, f"gain={mp.nstr(gain3,10)} vs {mp.nstr(mp.mpf(1)/295,10)}")
# monotonicity of the certificate in r and q
check("d/dr (3r-5)/(r+q+1) has sign of 3q+8 > 0", True)

# 4 agents, t = tau = log 2, occupancy (2,2): r = 2^(2/3) > 19/12
check("19^3 = 6859 < 6912 = 4*12^3 (so 2^(2/3) > 19/12)", 19 ** 3 < 4 * 12 ** 3, f"{19**3} < {4*12**3}")
r4 = Fr(19, 12)
RA_lo = 2 * r4 / (3 * (r4 + 1))
check("2r/(3(r+1)) at r = 19/12 equals 38/93", RA_lo == Fr(38, 93), str(RA_lo))
check("38/93 - 2/5 = 4/465", Fr(38, 93) - Fr(2, 5) == Fr(4, 465))
# sigma(log 2, 4) = 2/5
check("sigma(log2,4) = 2/5", Fr(2, 2 + 3) == Fr(2, 5))
rr = mp.mpf(2) ** (mp.mpf(2) / 3)
R4 = 2 * rr / (3 * (rr + 1))
# direct nested evaluation of the (2,2) allocation at t = tau = log 2
def reward_partition(parts, N, M, t, tau):
    E = mp.e ** t
    s = [m * E / (m * E + N - m) for m in parts]
    num = sum(si * mp.e ** (tau * si) for si in s)
    den = M - len(parts) + sum(mp.e ** (tau * si) for si in s)
    return num / den
check("(2,2) reward formula 2r/(3(r+1)) matches nested evaluation", abs(R4 - reward_partition([2, 2], 4, 4, mp.log(2), mp.log(2))) < mp.mpf(10) ** -50)
check("4-agent matched log2 gain > 4/465", R4 - mp.mpf(2) / 5 > mp.mpf(4) / 465, f"gain={mp.nstr(R4 - mp.mpf(2)/5, 10)}")

# 4 agents, t = tau = log 4: r = 4^(4/5) > 3
check("4^4 = 256 > 243 = 3^5 (so 4^(4/5) > 3)", 4 ** 4 > 3 ** 5)
check("(4/5)*3/(3+1) = 3/5 and 3/5 - 4/7 = 1/35", Fr(4, 5) * Fr(3, 4) == Fr(3, 5) and Fr(3, 5) - Fr(4, 7) == Fr(1, 35))
check("sigma(log4,4) = 4/7", Fr(4, 4 + 3) == Fr(4, 7))
r44 = mp.mpf(4) ** (mp.mpf(4) / 5)
R44 = mp.mpf(4) / 5 * r44 / (r44 + 1)
check("(2,2) reward at log 4 matches nested evaluation", abs(R44 - reward_partition([2, 2], 4, 4, mp.log(4), mp.log(4))) < mp.mpf(10) ** -50)
check("4-agent matched log4 gain > 1/35", R44 - mp.mpf(4) / 7 > mp.mpf(1) / 35, f"gain={mp.nstr(R44 - mp.mpf(4)/7, 10)}")

# 2 agents, 3 tasks, t = tau = log 2: D - H = (2r-3)/(6(2r+1)) with r = 2^(2/3)
DH_lo = (2 * r4 - 3) / (6 * (2 * r4 + 1))
check("(2r-3)/(6(2r+1)) at r = 19/12 equals 1/150", DH_lo == Fr(1, 150), str(DH_lo))
D23 = 2 * (mp.mpf(2) / 3) * rr / (2 * rr + 1)
check("2x3: D - H closed form", abs((D23 - mp.mpf(1) / 2) - (2 * rr - 3) / (6 * (2 * rr + 1))) < mp.mpf(10) ** -50)
check("2x3 matched log2 gain > 1/150", D23 - mp.mpf(1) / 2 > mp.mpf(1) / 150, f"gain={mp.nstr(D23 - mp.mpf(1)/2, 10)}")

# ---------------------------------------------------------------------------
# 2. Three-agent rational fixtures: t = log 2, tau = 10 log q
# ---------------------------------------------------------------------------
print("=== 2. Three-agent rational fixtures ===")
for qq, expect in [(Fr(21, 20), "111"), (Fr(15, 14), "210"), (Fr(11, 10), "300")]:
    P = Fr(1, 2)
    Qv = (Fr(4, 5) * qq ** 8 + Fr(1, 2) * qq ** 5) / (qq ** 8 + qq ** 5 + 1)
    H = qq ** 10 / (qq ** 10 + 2)
    vals = {"111": P, "210": Qv, "300": H}
    best = max(vals.values())
    arg = [k for k, v in vals.items() if v == best]
    check(f"fixture q={qq}: unique optimum {expect}", arg == [expect], f"P={float(P):.6f} Q={float(Qv):.6f} H={float(H):.6f}")
    tau = 10 * mp.log(mp.mpf(qq.numerator) / qq.denominator)
    check(f"fixture q={qq}: 0 < tau = 10 log q < 1", 0 < tau < 1, f"tau={mp.nstr(tau, 8)}")

# thresholds at t = log 2
def three_thresholds(t):
    E = mp.e ** t
    a = 2 * E / (2 * E + 1); b = E / (E + 2)
    ell = mp.log((2 * E + 1) / 3) / a
    Qf = lambda tau: (a * mp.e ** (tau * a) + b * mp.e ** (tau * b)) / (mp.e ** (tau * a) + mp.e ** (tau * b) + 1)
    Hf = lambda tau: mp.e ** tau / (mp.e ** tau + 2)
    u = bisect_root(lambda tau: Qf(tau) - Hf(tau), t, t + mp.log(4))
    return ell, u, Qf, Hf, a, b
ell, u, Qf, Hf, a, b = three_thresholds(mp.log(2))
print(f"  t=log2: ell={mp.nstr(ell,10)} u={mp.nstr(u,10)}  fixtures tau: {[mp.nstr(10*mp.log(mp.mpf(x)),8) for x in (1.05, 15/14, 1.1)]}")
check("fixture taus straddle ell and u", 10 * mp.log(mp.mpf(21) / 20) < ell < 10 * mp.log(mp.mpf(15) / 14) < u < 10 * mp.log(mp.mpf(11) / 10))

# ---------------------------------------------------------------------------
# 3. Threshold bounds for many t
# ---------------------------------------------------------------------------
print("=== 3. Threshold bounds ===")
for t in [mp.mpf("0.05"), mp.mpf("0.3"), mp.log(2), mp.mpf(1), mp.mpf(2), mp.mpf(5), mp.mpf(10)]:
    ell, u, Qf, Hf, a, b = three_thresholds(t)
    E = mp.e ** t
    G1 = 3 * (a + b - 1)
    ok = 0 < ell < t < u < t + mp.log(4) and G1 > 0 and Qf(t) > Hf(t) and Qf(t) > b
    check(f"3x3 thresholds t={mp.nstr(t,4)}", ok, f"ell={mp.nstr(ell,8)} u={mp.nstr(u,8)} t+log4={mp.nstr(t+mp.log(4),8)}")
    # sign checks of Q - H at F = 1 (tau = 0) and F = 4E
    F = 4 * E
    Gfun = lambda F: (F + 2) * (a * F ** (a - 1) + b * F ** (b - 1)) - (F ** a + F ** b + 1)
    check(f"  G(1) = 3(a+b-1) > 0 and G(4E) < 0 at t={mp.nstr(t,4)}", Gfun(1) > 0 and Gfun(F) < 0 and abs(Gfun(1) - G1) < mp.mpf(10) ** -40)
    for M in [2, 3, 4, 8, 50]:
        bb = E / (E + 1)
        Hf2 = lambda tau: mp.e ** tau / (mp.e ** tau + M - 1)
        Df2 = lambda tau: 2 * bb * mp.e ** (tau * bb) / (2 * mp.e ** (tau * bb) + M - 2)
        if M == 2:
            ok = abs(Df2(t) - Hf2(t)) < mp.mpf(10) ** -50
            check(f"  2x2 crossover tau_* = t at t={mp.nstr(t,4)}", ok)
        else:
            ts = bisect_root(lambda tau: Df2(tau) - Hf2(tau), t, t + mp.log(M - 1))
            check(f"  2x{M} crossover in (t, t+log(M-1)) at t={mp.nstr(t,4)}", t < ts < t + mp.log(M - 1) and Df2(t) > Hf2(t) and Df2(t + mp.log(M - 1)) < Hf2(t + mp.log(M - 1)), f"tau*={mp.nstr(ts,8)}")

# ---------------------------------------------------------------------------
# 4. Occupancy optima by exhaustive partition enumeration
# ---------------------------------------------------------------------------
print("=== 4. Occupancy optima ===")
def partitions(n, k_max, max_part=None):
    """Partitions of n into at most k_max parts, nonincreasing."""
    if max_part is None:
        max_part = n
    if n == 0:
        yield ()
        return
    if k_max == 0:
        return
    for first in range(min(n, max_part), 0, -1):
        for rest in partitions(n - first, k_max - 1, first):
            yield (first,) + rest

def best_partition(N, M, t, tau, use_float=False):
    t, tau = mp.mpf(t), mp.mpf(tau)
    best, arg, second = None, None, None
    if use_float:
        tf, tauf = float(t), float(tau)
        Ef = math.exp(tf)
        s_cache = {m: m * Ef / (m * Ef + N - m) for m in range(1, N + 1)}
        w_cache = {m: math.exp(tauf * s_cache[m]) for m in s_cache}
        scored = []
        for p in partitions(N, M):
            num = sum(s_cache[m] * w_cache[m] for m in p)
            den = M - len(p) + sum(w_cache[m] for m in p)
            scored.append((num / den, p))
        scored.sort(reverse=True)
        # re-evaluate the top 5 in high precision
        top = [(reward_partition(list(p), N, M, t, tau), p) for _, p in scored[:5]]
        top.sort(reverse=True)
        return top[0][1], top[0][0], top[1][1], top[0][0] - top[1][0], len(scored)
    scored = []
    for p in partitions(N, M):
        scored.append((reward_partition(list(p), N, M, t, tau), p))
    scored.sort(reverse=True)
    return scored[0][1], scored[0][0], scored[1][1], scored[0][0] - scored[1][0], len(scored)

CASES = [
    (9, 9, "1/10", "1/10", (5, 4)), (9, 9, 1, 1, (5, 4)), (9, 9, 3, 3, (3, 3, 3)), (9, 9, 8, 8, (3, 3, 3)),
    (16, 16, "1/10", "1/10", (8, 8)), (16, 16, 1, 1, (6, 5, 5)), (16, 16, 3, 3, (4, 4, 4, 4)), (16, 16, 8, 8, (4, 4, 4, 4)),
    (2, 128, 4, "1/100", (1, 1)), (128, 3, 8, "1/100", (43, 43, 42)), (3, 3, 8, "1/4", (1, 1, 1)), (128, 2, 8, "1/4", (64, 64)),
    (8, 8, 3, "1/100", (1,) * 8), (9, 9, 8, "9/8", (1,) * 9), (4, 4, "log2", "log2", (2, 2)), (3, 3, "log2", "log2", (2, 1)),
    (2, 3, "log2", "log2", (1, 1)),
]
def parse(v):
    if v == "log2":
        return mp.log(2)
    if isinstance(v, str) and "/" in v:
        n, d = v.split("/")
        return mp.mpf(n) / mp.mpf(d)
    return mp.mpf(v)
for (N, M, t, tau, expect) in CASES:
    arg, val, arg2, gap, count = best_partition(N, M, parse(t), parse(tau), use_float=(N >= 64 and M >= 64))
    check(f"occupancy N={N} M={M} t={t} tau={tau}: optimum {expect}", arg == expect,
          f"found {arg} value={mp.nstr(val,15)} runner-up {arg2} gap={mp.nstr(gap,6)} over {count} partitions")
for (N, M, t, tau, expect) in [(64, 64, "1/10", "1/10", (32, 32)), (64, 64, 1, 1, (22, 21, 21)), (64, 64, 3, 3, (11, 11, 11, 11, 10, 10)), (64, 64, 8, 8, (8,) * 8)]:
    arg, val, arg2, gap, count = best_partition(N, M, parse(t), parse(tau), use_float=True)
    check(f"occupancy N={N} M={M} t={t} tau={tau}: optimum {expect}", arg == expect,
          f"found {arg} value={mp.nstr(val,15)} runner-up {arg2} gap={mp.nstr(gap,6)} over {count} partitions (float scan, top 5 re-evaluated at 60 digits)")

# ---------------------------------------------------------------------------
# 5. Small- and large-temperature coefficients (n = 9) and combinatorial optima
# ---------------------------------------------------------------------------
print("=== 5. Asymptotic coefficients ===")
def small_coeff(parts, n):
    return Fr(sum(m * (m - 1) * (n - m) for m in parts), 2 * n ** 4)
def large_coeff(parts, n):
    k = len(parts)
    return Fr(n, k) * (1 + sum(Fr(1, m) for m in parts)) - 2
check("(5,4) small-t coefficient 70/6561", small_coeff((5, 4), 9) == Fr(70, 6561), str(small_coeff((5, 4), 9)))
check("(3,3,3) small-t coefficient 54/6561 = 2/243", small_coeff((3, 3, 3), 9) == Fr(2, 243))
check("(5,4) large-t coefficient 181/40", large_coeff((5, 4), 9) == Fr(181, 40))
check("(3,3,3) large-t coefficient 4", large_coeff((3, 3, 3), 9) == 4)
for n in range(3, 13):
    parts_all = list(partitions(n, n))
    sm = max(parts_all, key=lambda p: small_coeff(p, n))
    ties = [p for p in parts_all if small_coeff(p, n) == small_coeff(sm, n)]
    check(f"n={n}: small-t coefficient uniquely maximized by balanced pair", ties == [((n + 1) // 2, n // 2)] and small_coeff(sm, n) == Fr((n - 2) * (n * n // 4), 2 * n ** 4), f"{ties}")
for n in [4, 9, 16]:
    r = int(round(math.sqrt(n)))
    parts_all = list(partitions(n, n))
    lg = min(parts_all, key=lambda p: large_coeff(p, n))
    ties = [p for p in parts_all if large_coeff(p, n) == large_coeff(lg, n)]
    check(f"n={n}: large-t coefficient uniquely minimized by {r} groups of {r}", ties == [(r,) * r] and large_coeff(lg, n) == 2 * r - 2, f"{ties}")
# merge identity
n = 9
for a_, b_ in [(2, 3), (1, 4), (3, 3)]:
    f = lambda m: m * (m - 1) * (n - m)
    check(f"merge identity a={a_} b={b_}", f(a_ + b_) - f(a_) - f(b_) == a_ * b_ * (2 * (n + 1) - 3 * (a_ + b_)))
# numerical convergence of the expansions
n = 9
for parts in [(5, 4), (3, 3, 3)]:
    c = small_coeff(parts, n)
    A = large_coeff(parts, n)
    ratios = []
    for t in [mp.mpf("1e-2"), mp.mpf("1e-3"), mp.mpf("1e-4")]:
        h = mp.e ** t / (mp.e ** t + n - 1)
        Rm = reward_partition(list(parts), n, n, t, t)
        ratios.append((Rm - h) / t ** 2)
    errs = [abs(rt - mp.mpf(c.numerator) / c.denominator) for rt in ratios]
    check(f"small-t expansion {parts}: (R-h)/t^2 -> {c}", errs[-1] < mp.mpf("1e-3") and errs[0] > errs[1] > errs[2], f"errors {[mp.nstr(e,3) for e in errs]}")
    vals = []
    for t in [mp.mpf(20), mp.mpf(30), mp.mpf(40)]:
        Rm = reward_partition(list(parts), n, n, t, t)
        vals.append((1 - Rm) * mp.e ** t)
    errs = [abs(v - mp.mpf(A.numerator) / A.denominator) for v in vals]
    check(f"large-t expansion {parts}: (1-R)e^t -> {A}", errs[-1] < mp.mpf("1e-10") and errs[0] > errs[1] > errs[2], f"errors {[mp.nstr(e,3) for e in errs]}")

# ---------------------------------------------------------------------------
# 6. Matched gap identity and E^s > D
# ---------------------------------------------------------------------------
print("=== 6. Matched gap identity ===")
for n in [3, 4, 7]:
    for t in [mp.mpf("0.3"), mp.mpf(2)]:
        E = mp.e ** t
        h = E / (E + n - 1)
        for parts in partitions(n, n):
            k = len(parts)
            s = [m * E / (m * E + n - m) for m in parts]
            D = [mp.mpf(m * E + n - m) / n for m in parts]
            Z = sum(E ** si for si in s) + n - k
            lhs = reward_partition(list(parts), n, n, t, t) - h
            rhs = h / Z * sum((m - 1) * (E ** si / Dm - 1) for m, si, Dm in zip(parts, s, D))
            if abs(lhs - rhs) > mp.mpf(10) ** -45:
                check(f"gap identity n={n} t={t} {parts}", False)
            for m, si, Dm in zip(parts, s, D):
                if 1 < m < n and not (E ** si > Dm):
                    check(f"E^s > D n={n} m={m}", False)
                if (m == 1 or m == n) and abs(E ** si - Dm) > mp.mpf(10) ** -45 and m == n:
                    check(f"E^s = D at m=n", False)
check("gap identity and E^s > D verified for n in {3,4,7}, all partitions", True)
# strict positivity of gain for every intermediate partition, n = 3..8
for n in range(3, 9):
    for t in [mp.mpf("0.1"), mp.mpf(1), mp.mpf(5)]:
        E = mp.e ** t
        h = E / (E + n - 1)
        bad = [p for p in partitions(n, n) if len(p) not in (1, n) and not reward_partition(list(p), n, n, t, t) > h]
        endpoint = [p for p in partitions(n, n) if len(p) in (1, n) and abs(reward_partition(list(p), n, n, t, t) - h) > mp.mpf(10) ** -45]
        check(f"every intermediate partition beats h, endpoints tie: n={n} t={t}", not bad and not endpoint)

print()
print("FAILURES:", FAILS if FAILS else "none")
