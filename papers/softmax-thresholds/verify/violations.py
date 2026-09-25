#!/usr/bin/env python3
"""High-precision numerical checks of the explicit interior violations and of
the sufficiency direction (sanity sampling).  These are not exact certificates;
the exact parts of the paper are covered by roots.py and counterexamples.py.
"""
import random
import mpmath as mp

mp.mp.dps = 50
random.seed(20260925)
FAIL = []


def c_n(n):
    return 2 + mp.lambertw(mp.mpf(4) / ((n - 2) * mp.e ** 2)).real


def d_n(n):
    return 2 + mp.lambertw(mp.mpf(2) * (n - 1) / mp.e ** 2).real


def Bmean(tau, v):
    w = [mp.exp(tau * t) for t in v]
    return sum(t * wi for t, wi in zip(v, w)) / sum(w)


def majorizes(x, y, tol=mp.mpf("1e-40")):
    xs, ys = sorted(x, reverse=True), sorted(y, reverse=True)
    if abs(sum(xs) - sum(ys)) > tol:
        return False
    px = py = mp.mpf(0)
    for a, b in zip(xs, ys):
        px += a
        py += b
        if px < py - tol:
            return False
    return True


def box_violation(n, L):
    """Explicit interior violation of Schur-concavity of F = B_{-1} on [0,L]^n."""
    m = n - 2
    cn = c_n(n)
    C = (L + cn) / 2
    s = (L - cn) / 4
    q = mp.exp(-C)
    eta = 1 - 2 * (m + 2 * q) / (m * C)
    assert eta > 0
    z = min(s / 2, mp.sqrt(3 * eta))
    v = [s] * m + [s + C, s + C]
    v2 = [s] * m + [s + C - z, s + C + z]
    assert all(0 < t < L for t in v + v2)
    assert majorizes(v2, v)
    diff = Bmean(-1, v2) - Bmean(-1, v)                 # must be > 0
    bound = m * C * mp.tanh(z / 2) / z - (m + 2 * q)   # must be >= 3 m C eta / 8
    return diff, bound, 3 * m * C * eta / 8


def simplex_negative_violation(n, K):
    m = n - 2
    cn = c_n(n)
    C = (K + 2 * cn) / 4
    s = (K - 2 * C) / n
    q = mp.exp(-C)
    eta = 1 - 2 * (m + 2 * q) / (m * C)
    assert eta > 0 and s > 0
    z = min(C / 2, mp.sqrt(3 * eta))
    v = [s] * m + [s + C, s + C]
    v2 = [s] * m + [s + C - z, s + C + z]
    assert all(t > 0 for t in v + v2)
    assert abs(sum(v) - K) < mp.mpf("1e-40") and abs(sum(v2) - K) < mp.mpf("1e-40")
    assert majorizes(v2, v)
    diff = Bmean(-1, v2) - Bmean(-1, v)                 # must be > 0
    bound = m * C * mp.tanh(z / 2) / z - (m + 2 * q)
    return diff, bound, 3 * m * C * eta / 8


def simplex_positive_violation(n, K):
    delta0 = K * mp.exp(K) / (mp.exp(K) + n - 1) - 2
    assert delta0 > 0
    A = 2 * (n - 1) * (K + 1) + 1
    eps = min(K / (2 * n), delta0 / (2 * A))
    v = [K - (n - 1) * eps] + [eps] * (n - 1)
    z = min(eps / 2, mp.sqrt(3 * delta0 / 2))
    v2 = [K - (n - 1) * eps, eps - z, eps + z] + [eps] * (n - 3)
    assert all(t > 0 for t in v + v2)
    assert majorizes(v2, v)
    Hv = Bmean(1, v)
    assert Hv - eps - 2 >= delta0 / 2 - mp.mpf("1e-45")       # inequality (2)
    diff = Bmean(1, v2) - Hv                                    # must be < 0
    bracket = eps - Hv + z * mp.coth(z / 2)                    # must be <= -delta0/4
    return diff, bracket, -delta0 / 4


def report(name, ok):
    print(f"{name}: {'ok' if ok else 'FAIL'}")
    if not ok:
        FAIL.append(name)


# 1. Explicit interior violations above each cutoff.
for n in (3, 4, 5, 8, 32, 57, 58, 128, 1000):
    for delta in (mp.mpf("1e-9"), mp.mpf("1e-4"), mp.mpf("0.1"), mp.mpf(1), mp.mpf(10)):
        dfb, bnd, low = box_violation(n, c_n(n) + delta)
        report(f"box violation n={n} L=c_n+{delta}", dfb > 0 and bnd >= low > 0)
        dfs, bnd, low = simplex_negative_violation(n, 2 * c_n(n) + delta)
        report(f"simplex negative violation n={n} K=2c_n+{delta}", dfs > 0 and bnd >= low > 0)
        dfp, br, cap = simplex_positive_violation(n, d_n(n) + delta)
        report(f"simplex positive violation n={n} K=d_n+{delta}", dfp < 0 and br <= cap < 0)

# 2. Sufficiency sanity: derivative inequality at random points at and below cutoffs.
def dF(v, i):       # partial of B_{-1}
    S = sum(mp.exp(-t) for t in v)
    return mp.exp(-v[i]) / S * (1 - v[i] + Bmean(-1, v))


def dH(v, i):       # partial of B_{+1}
    Z = sum(mp.exp(t) for t in v)
    return mp.exp(v[i]) / Z * (1 + v[i] - Bmean(1, v))


for n in (3, 4, 8, 32):
    ok = True
    for L in (c_n(n), c_n(n) - mp.mpf("0.05")):
        for _ in range(400):
            v = [mp.mpf(random.random()) * L for _ in range(n)]
            if random.random() < 0.3:
                v[0] = mp.mpf(0)
            if random.random() < 0.3:
                v[1] = L
            i, j = 0, 1
            if v[i] == v[j]:
                continue
            lo, hi = (i, j) if v[i] < v[j] else (j, i)
            ok &= dF(v, lo) > dF(v, hi)
    report(f"box derivative inequality sampled at/below c_n, n={n}", ok)

    ok = True
    K = 2 * c_n(n)
    for _ in range(400):
        w = [mp.mpf(random.random()) for _ in range(n)]
        v = [K * t / sum(w) for t in w]
        lo, hi = (0, 1) if v[0] < v[1] else (1, 0)
        ok &= dF(v, lo) > dF(v, hi)
    # extreme case: two coordinates carry the whole total
    for _ in range(200):
        a = mp.mpf(random.random()) * K
        v = [a, K - a] + [mp.mpf(0)] * (n - 2)
        if v[0] == v[1]:
            continue
        lo, hi = (0, 1) if v[0] < v[1] else (1, 0)
        ok &= dF(v, lo) > dF(v, hi)
    report(f"simplex negative derivative inequality sampled at K=2c_n, n={n}", ok)

    ok = True
    K = d_n(n)
    for _ in range(400):
        w = [mp.mpf(random.random()) ** 3 for _ in range(n)]
        v = [K * t / sum(w) for t in w]
        ok &= Bmean(1, v) <= 2 + mp.mpf("1e-45")
        lo, hi = (0, 1) if v[0] < v[1] else (1, 0)
        ok &= dH(v, hi) > dH(v, lo)
    report(f"simplex positive derivative inequality and H<=2 sampled at K=d_n, n={n}", ok)

# 3. Random majorization pairs (T-transforms) at the cutoffs: ordering holds strictly.
for n in (3, 5, 8):
    ok = True
    L = c_n(n)
    for _ in range(300):
        v = [mp.mpf(random.random()) * L for _ in range(n)]
        i, j = random.sample(range(n), 2)
        if v[i] == v[j]:
            continue
        lam = mp.mpf(random.random())
        w = list(v)
        w[i] = lam * v[i] + (1 - lam) * v[j]
        w[j] = lam * v[j] + (1 - lam) * v[i]
        ok &= Bmean(-1, w) > Bmean(-1, v) or lam in (0, 1)
    report(f"box: random T-transform strictly increases B_-1 at L=c_n, n={n}", ok)

# 4. Just above the cutoffs the m-zero configuration fails for small splits.
for n in (3, 4, 8):
    m = n - 2
    L = c_n(n) + mp.mpf("0.2")
    cc = c_n(n) + mp.mpf("0.1")
    z = mp.mpf("1e-3")
    v = [mp.mpf(0)] * m + [cc, cc]
    v2 = [mp.mpf(0)] * m + [cc - z, cc + z]
    report(f"box: zero-padded split above c_n is a violation, n={n}", Bmean(-1, v2) > Bmean(-1, v))
    v = [mp.mpf(0)] * m + [c_n(n) - mp.mpf("0.1")] * 2
    v2 = [mp.mpf(0)] * m + [c_n(n) - mp.mpf("0.1") - z, c_n(n) - mp.mpf("0.1") + z]
    report(f"box: zero-padded split below c_n is not a violation, n={n}", Bmean(-1, v2) < Bmean(-1, v))

# 5. Dimension-free bound 2 (prior art via Lehmer means): random pairs with tau(b-a) = 2.
ok = True
for n in (3, 5, 20):
    for _ in range(300):
        v = [mp.mpf(random.random()) * 2 for _ in range(n)]
        i, j = random.sample(range(n), 2)
        lam = mp.mpf(random.random())
        w = list(v)
        w[i] = lam * v[i] + (1 - lam) * v[j]
        w[j] = lam * v[j] + (1 - lam) * v[i]
        ok &= Bmean(1, v) >= Bmean(1, w) - mp.mpf("1e-45")
report("dimension-free bound 2 sampled (tau(b-a)=2)", ok)

# 6. The counterexample temperature exceeds the n = 3 cutoffs.
tau = 8 * mp.log(2)
report("8 log 2 > 2 c_3 > d_3 = c_3", tau > 2 * c_n(3) > d_n(3) and abs(d_n(3) - c_n(3)) < mp.mpf("1e-45"))

print("FAILED:", FAIL if FAIL else "none")
raise SystemExit(1 if FAIL else 0)
