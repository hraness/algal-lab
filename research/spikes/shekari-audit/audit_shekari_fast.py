"""Fast exact sweep for Shekari et al. 2026 Thm 11 under PHR distortion.

htilde_{p,g}(u) = sum p_i g_i u^{g_i} / sum p_i u^{g_i}  evaluated exactly:
for rational g_i = a_i/b and grid point u = c/d, evaluate sum p_i g_i u^{g_i}
as a Fraction via common-denominator exponentiation:  write g_i = e_i/E
(E = lcm of denominators), u = c/d  ->  u^{g_i} = (c/d)^{e_i/E} is NOT
rational unless E=1.  So instead evaluate at u = (c/d)^E, i.e. choose grid
points that are perfect E-th powers, OR clear denominators: the comparison
htilde_A(u) vs htilde_B(u) at rational u with rational exponents is exact via
sympy Rational ** Rational (returns rational**rational as exact Pow; sign via
sp.sign).  To keep it fast we evaluate with fractions.Fraction only when all
exponents are integral; otherwise use sympy exact eval per point (still much
faster than building the symbolic difference).
"""
import sys
import random
from fractions import Fraction as Fr
from math import gcd
import sympy as sp
from sympy import Rational as R

u = sp.Symbol("u", positive=True)
GRID = [R(1, 16), R(1, 8), R(1, 4), R(2, 5), R(1, 2), R(3, 4), R(7, 8), R(15, 16)]


def htilde_at(p, g, uv):
    """Exact value of htilde_{p,g}(uv) for rational uv, rational g (sympy)."""
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
    if not (all(x > 0 for x in row1) and all(R(0) < y < R(1) for y in row2)):
        return False
    return all((row1[i] - row1[j]) * (row2[i] - row2[j]) <= 0
               for i in range(n) for j in range(n))


def sweep(trials=20000, seed=11):
    rng = random.Random(seed)
    res = {"n2_i": [0, 0], "n2_ii": [0, 0], "n3_i": [0, 0], "n3_ii": [0, 0],
           "n4_i": [0, 0], "n4_ii": [0, 0]}
    ex = {}
    for _ in range(trials):
        n = rng.choice([2, 3, 4])
        gam_sorted = sorted(R(rng.randint(1, 12), rng.choice([1, 1, 1, 2]))
                            for _ in range(n))
        p_raw = [R(rng.randint(1, 40), 40) for _ in range(n)]
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
        w = R(rng.randint(1, 19), 20)
        gs, ps = t_transform(gam, p, i, j, w)
        if not in_An(gs, ps) or sum(ps) != 1:
            continue
        # signs of d(u) = htilde_A - htilde_B on the grid, exact
        vals = []
        for v in GRID:
            dv = htilde_at(p, gam, v) - htilde_at(ps, gs, v)
            vals.append((v, sp.sign(dv)))
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
    print("=== Thm 11 under PHR: admissible/violating ===")
    for k, v in res.items():
        print(f"  {k}: admissible={v[0]}  violating={v[1]}")
    for k, v in ex.items():
        print("VIOL", k, ":", v[:5])
        print("      grid:", v[5])
