"""Targeted search: Thm 11(i) violations under PHR in the region where the
paper's gamma-conditions genuinely hold.

For D(u;g)=u^g (PHR), part (i) needs D and -D' decreasing+convex in gamma.
D: dec+convex in g for all u in (0,1).  -D'=-g u^{g-1}: decreasing in g iff
1+g*ln u >=0, convex iff 2+g*ln u>=0 -- i.e. on u >= exp(-1/g) for the
relevant g-range.  So for an instance with gamma-set G, the conditions hold
on u >= exp(-1/max G).

We look for instances where htilde_A(u) - htilde_B(u) > 0 at some u with
u >= exp(-1/gmax) -- i.e. the claimed ordering fails already inside the
region where every hypothesis holds.

Evaluate in z = u^{1/L}, L=lcm(denom(gs)): u-grid points are z^L; we need
z^L >= exp(-1/gmax) i.e. z >= exp(-1/(L*gmax)).
"""
import sys
import random
from fractions import Fraction as Fr
from math import gcd, exp, log

ZGRID = [Fr(1, 4), Fr(2, 5), Fr(1, 2), Fr(3, 5), Fr(7, 10), Fr(3, 4),
         Fr(4, 5), Fr(7, 8), Fr(9, 10), Fr(15, 16), Fr(19, 20), Fr(31, 32)]


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


def sweep(trials, seed=7):
    rng = random.Random(seed)
    found = []
    admissible = 0
    inregion_viol = 0
    gammas = [Fr(1, 4), Fr(1, 3), Fr(1, 2), Fr(2, 3), Fr(3, 4), Fr(1),
              Fr(5, 4), Fr(4, 3), Fr(3, 2), Fr(2), Fr(5, 2), Fr(3), Fr(4)]
    for _ in range(trials):
        n = 3
        gam_sorted = sorted(rng.choice(gammas) for _ in range(n))
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
        admissible += 1
        dens = [x.denominator for x in gs] + [x.denominator for x in gam]
        L = 1
        for dd in dens:
            L = L * dd // gcd(L, dd)
        gmax = max(max(gam), max(gs))
        zthresh = exp(-1.0 / (float(L) * float(gmax)))
        viol_pts = []
        for v in ZGRID:
            num_a = sum(pi * gi * v ** (L * gi) for pi, gi in zip(p, gam))
            den_a = sum(pi * v ** (L * gi) for pi, gi in zip(p, gam))
            num_b = sum(pi * gi * v ** (L * gi) for pi, gi in zip(ps, gs))
            den_b = sum(pi * v ** (L * gi) for pi, gi in zip(ps, gs))
            dv = num_a / den_a - num_b / den_b
            if dv > 0:  # violates claim (i) htilde_A <= htilde_B
                viol_pts.append((v, float(v) >= zthresh))
        if viol_pts:
            if any(ir for _, ir in viol_pts):
                inregion_viol += 1
                if len(found) < 6:
                    found.append((gam, p, gs, ps, (i, j, w), L,
                                  [v for v, ir in viol_pts if ir], gmax))
    print(f"admissible A_3 single-T instances: {admissible}")
    print(f"violations witnessed INSIDE the gamma-condition region: {inregion_viol}")
    for f in found:
        print("  gam=", tuple(str(x) for x in f[0]), " p=", tuple(str(x) for x in f[1]))
        print("   gs=", tuple(str(x) for x in f[2]), " ps=", tuple(str(x) for x in f[3]))
        print("   T cols", f[4], " L=", f[5], " gmax=", f[7],
              " in-region z witnesses:", f[6],
              " (u=z^L >=", round(exp(-1/float(f[7])), 4), ")")


if __name__ == "__main__":
    sweep(int(sys.argv[1]) if len(sys.argv) > 1 else 20000)
