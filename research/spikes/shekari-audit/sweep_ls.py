"""LS specialization check: Remark 11(I)(i) claims BKB2022 Thm 2 (LS mixtures)
as a special case of Thm 11 via D(1-u;g)=1-u.

For identity distortion D(u)=u, both parts' gamma-conditions hold trivially
(constant in g).  In the LS specialization gamma_i is the component SCALE:
component SF Gbar(t/g_i).  Take exponential baseline and g_i = 1/m_i:
    h_P(t) = sum_i (p_i/g_i) s^{1/g_i} / sum_i p_i s^{1/g_i},   s = e^{-t},
    exponents lam_i = 1/g_i = m_i (integers for A; rational for B=AT).
Evaluate in z = s^{1/L}, L = lcm of denominators of lam*_i = 1/g*_i.
Claim (i): h_A <= h_B on s in (0,1).
"""
import sys
import random
from fractions import Fraction as Fr
from math import gcd

GRID = [Fr(1, 16), Fr(1, 8), Fr(1, 4), Fr(2, 5), Fr(1, 2), Fr(3, 4),
        Fr(7, 8), Fr(15, 16)]


def in_An(row1, row2):
    n = len(row1)
    if not (all(x > 0 for x in row1) and all(Fr(0) < y < Fr(1) for y in row2)):
        return False
    return all((row1[i] - row1[j]) * (row2[i] - row2[j]) <= 0
               for i in range(n) for j in range(n))


def t_transform(row1, row2, i, j, w):
    r1, r2 = list(row1), list(row2)
    for row in (r1, r2):
        ai, aj = row[i], row[j]
        row[i] = w * ai + (1 - w) * aj
        row[j] = (1 - w) * ai + w * aj
    return tuple(r1), tuple(r2)


def hz(p, lam, zv):
    num = sum(pi * li * zv ** li for pi, li in zip(p, lam))
    den = sum(pi * zv ** li for pi, li in zip(p, lam))
    return num / den


def sweep(trials, seed=5):
    rng = random.Random(seed)
    adm = 0
    viol_i = 0
    viol_ii = 0
    ex = None
    ex2 = None
    for _ in range(trials):
        n = 3
        # g_i = 1/m_i scales; A_3 wants (g_i-g_j)(p_i-p_j) <= 0:
        # gamma increasing <=> lam=1/gamma decreasing <=> m decreasing.
        m_sorted_dec = sorted((rng.randint(1, 9) for _ in range(n)), reverse=True)
        p_raw = [Fr(rng.randint(1, 40), 40) for _ in range(n)]
        tot = sum(p_raw)
        order = sorted(range(n), key=lambda i: p_raw[i])  # smallest p first
        gam = [0] * n
        p = [0] * n
        for rank, idx in enumerate(order):  # smallest p gets largest m = smallest gamma
            p[idx] = p_raw[idx] / tot
            gam[idx] = Fr(1, m_sorted_dec[rank])
        gam, p = tuple(gam), tuple(p)
        lam = tuple(1 / g for g in gam)
        if not in_An(gam, p):
            continue
        i, j = rng.sample(range(n), 2)
        w = Fr(rng.randint(1, 19), 20)
        gs, ps = t_transform(gam, p, i, j, w)
        if not in_An(gs, ps) or sum(ps) != 1:
            continue
        lams = tuple(1 / g for g in gs)
        dens = [x.denominator for x in lams]
        L = 1
        for dd in dens:
            L = L * dd // gcd(L, dd)
        if L > 400:
            continue
        adm += 1
        vals = []
        for v in GRID:
            vals.append((v, hz(p, lam, v) - hz(ps, lams, v)))
        s_i = [(v, (dv > 0) - (dv < 0)) for v, dv in vals]
        sgn = {sg for _, sg in s_i} - {0}
        if not sgn:
            continue
        if len(sgn) > 1 or list(sgn)[0] != -1:   # claim (i): h_A <= h_B
            viol_i += 1
            if ex is None:
                ex = (gam, p, gs, ps, (i, j, w), s_i, lam, lams)
        if len(sgn) > 1 or list(sgn)[0] != +1:   # claim (ii): h_A >= h_B
            viol_ii += 1
            if ex2 is None and len(sgn) > 1:
                ex2 = (gam, p, gs, ps, (i, j, w), s_i, lam, lams)
    print("LS-exponential specialization of Thm 11: admissible =", adm)
    print("  claim (i) h_A<=h_B violations:", viol_i)
    print("  claim (ii) h_A>=h_B violations:", viol_ii)
    if ex:
        print("  EX(i):", ex[:5]); print("     grid:", ex[5])
    if ex2:
        print("  EX(ii):", ex2[:5]); print("     grid:", ex2[5])


if __name__ == "__main__":
    sweep(int(sys.argv[1]) if len(sys.argv) > 1 else 20000)
