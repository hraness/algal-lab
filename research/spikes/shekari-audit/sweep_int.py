"""Fast exact sweep, integer gammas only: u^{g_i} is a Fraction power => pure
fractions.Fraction arithmetic.  Evaluates htilde_A - htilde_B on the grid
exactly without sympy.
"""
import sys
import random
from fractions import Fraction as Fr

GRID = [Fr(1, 16), Fr(1, 8), Fr(1, 4), Fr(2, 5), Fr(1, 2), Fr(3, 4),
        Fr(7, 8), Fr(15, 16)]


def htilde_at(p, g, uv):
    num = sum(pi * gi * uv ** gi for pi, gi in zip(p, g))
    den = sum(pi * uv ** gi for pi, gi in zip(p, g))
    return num / den


def t_transform(row1, row2, i, j, w):
    r1, r2 = list(row1), list(row2)
    for row in (r1, r2):
        ai, aj = row[i], row[j]
        row[i] = w * ai + (1 - w) * aj
        row[j] = (1 - w) * ai + w * aj
    return tuple(r1), tuple(r2)


def in_An(row1, row2):
    n = len(row1)
    if not (all(x > 0 for x in row1) and all(Fr(0) < y < Fr(1) for y in row2)):
        return False
    return all((row1[i] - row1[j]) * (row2[i] - row2[j]) <= 0
               for i in range(n) for j in range(n))


def sweep(trials, seed=11):
    rng = random.Random(seed)
    res = {f"n{n}_{p}": [0, 0] for n in (2, 3, 4) for p in ("i", "ii")}
    ex = {}
    for _ in range(trials):
        n = rng.choice([2, 3, 4])
        gam_sorted = sorted(rng.randint(1, 12) for _ in range(n))
        p_raw = [Fr(rng.randint(1, 40), 40) for _ in range(n)]
        tot = sum(p_raw)
        order = sorted(range(n), key=lambda i: -p_raw[i])
        gam = [0] * n
        p = [0] * n
        for rank, idx in enumerate(order):
            p[idx] = p_raw[idx] / tot
            gam[idx] = gam_sorted[rank]
        gam, p = tuple(gam), tuple(p)
        if not in_An(gam, p):
            continue
        i, j = rng.sample(range(n), 2)
        w = Fr(rng.randint(1, 19), 20)
        gs, ps = t_transform(gam, p, i, j, w)
        if not in_An(gs, ps) or sum(ps) != 1:
            continue
        # gam integers; gs may be halves/quarters -> subsample exponents to
        # keep Fraction powers exact: gs rational -> u^{gs} not rational.
        # Evaluate at u = v^L trick would be needed; instead only accept
        # draws where all gs denominators divide a power structure handled
        # by evaluating at u in a transformed variable. Simplest: restrict
        # to integer-valued gs? T-transform gives rationals.  Use sympy-free
        # approach: evaluate d(u) = htilde_A - htilde_B at u = w0^(1/L)? No.
        # Instead evaluate the difference as a rational function in z = u^{1/L}
        # at z-grid points z = v (v in GRID), i.e. u = v^L.  u^g = v^{Lg}.
        from math import gcd
        dens = [x.denominator for x in gs]
        L = 1
        for dd in dens:
            L = L * dd // gcd(L, dd)
        vals = []
        for v in GRID:
            num_a = sum(pi * gi * v ** (L * gi) for pi, gi in zip(p, gam))
            den_a = sum(pi * v ** (L * gi) for pi, gi in zip(p, gam))
            num_b = sum(pi * gi * v ** (L * gi) for pi, gi in zip(ps, gs))
            den_b = sum(pi * v ** (L * gi) for pi, gi in zip(ps, gs))
            dv = num_a / den_a - num_b / den_b
            vals.append((v, (dv > 0) - (dv < 0)))
        signs = {sg for _, sg in vals} - {0}
        if not signs:
            continue
        for part, claimed in (("i", -1), ("ii", +1)):
            key = f"n{n}_{part}"
            res[key][0] += 1
            if len(signs) > 1 or list(signs)[0] != claimed:
                res[key][1] += 1
                ex.setdefault(key, (gam, p, gs, ps, (i, j, w), vals))
    return res, ex


if __name__ == "__main__":
    tr = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    res, ex = sweep(tr)
    print("=== Thm 11 under PHR (u=v^L parametrization): admissible/violating ===")
    for k, v in res.items():
        print(f"  {k}: admissible={v[0]}  violating={v[1]}")
    for k, v in ex.items():
        print("VIOL", k, ":", v[:5])
        print("      grid(z):", v[5])
