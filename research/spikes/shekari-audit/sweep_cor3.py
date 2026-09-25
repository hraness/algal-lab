"""Corollary 3 quick check (PHR, st order, row majorization):
(g,p),(g*,p*) in A_n, g >=^m g*, p >=^m p*  =>  P <=_st Q
i.e. SF_A(u) = sum p_i u^{g_i} >= sum p*_i u^{g*_i} = SF_B(u) on (0,1).
Also Thm 5 spot check (pi majorization, hr) and Thm 1 (p-larger, st).
"""
import random
from fractions import Fraction as Fr
from math import gcd

GRID = [Fr(1, 16), Fr(1, 8), Fr(1, 4), Fr(2, 5), Fr(1, 2), Fr(3, 4),
        Fr(7, 8), Fr(15, 16)]


def inc(v):
    return tuple(sorted(v))


def maj(x, y):   # x >=^m y
    xs, ys = inc(x), inc(y)
    return sum(xs) == sum(ys) and all(sum(xs[:k]) <= sum(ys[:k])
                                      for k in range(1, len(xs)))


def in_An(r1, r2):
    n = len(r1)
    return all((r1[i] - r1[j]) * (r2[i] - r2[j]) <= 0
               for i in range(n) for j in range(n))


def sweep_cor3(trials=40000, seed=13):
    rng = random.Random(seed)
    adm = viol = 0
    ex = None
    for _ in range(trials):
        n = 3
        g1 = sorted(Fr(rng.randint(1, 24), rng.choice([1, 2, 4])) for _ in range(n))
        g2 = sorted(Fr(rng.randint(1, 24), rng.choice([1, 2, 4])) for _ in range(n))
        if sum(g1) != sum(g2) or not maj(g1, g2):
            continue
        pa = [Fr(rng.randint(1, 40)) for _ in range(n)]
        pb = [Fr(rng.randint(1, 40)) for _ in range(n)]
        if sum(pa) == sum(pb):
            if not maj(sorted(pa), sorted(pb)):
                continue
        else:
            continue
        # scale to probabilities; pair: gamma inc <-> pi dec gives A_n
        p1 = tuple(sorted((x / sum(pa) for x in pa), reverse=True))
        p2 = tuple(sorted((x / sum(pb) for x in pb), reverse=True))
        if not (in_An(g1, p1) and in_An(g2, p2)):
            continue
        adm += 1
        dens = [x.denominator for x in g1 + g2]
        L = 1
        for dd in dens:
            L = L * dd // gcd(L, dd)
        bad = None
        for v in GRID:
            dv = sum(pi * v ** (L * gi) for pi, gi in zip(p1, g1)) - \
                 sum(pi * v ** (L * gi) for pi, gi in zip(p2, g2))
            if dv < 0:
                bad = v
                break
        if bad is not None:
            viol += 1
            ex = ex or (g1, p1, g2, p2, bad)
    print("Cor 3 (st, PHR): admissible", adm, "violating", viol, "EX:", ex)


def sweep_thm5(trials=40000, seed=17):
    """Thm 5: (g,p),(g,p*) in A_n, p >=^m p* => (i) P >=_hr Q when
    D and -D' decreasing in g; under PHR htilde compare."""
    rng = random.Random(seed)
    adm = viol = 0
    ex = None
    for _ in range(trials):
        n = 3
        gam = tuple(sorted(Fr(rng.randint(1, 12)) for _ in range(n)))
        pa = [Fr(rng.randint(1, 60)) for _ in range(n)]
        pb = [Fr(rng.randint(1, 60)) for _ in range(n)]
        # p and p* prob vectors both antiordered with gam: gam inc -> p dec
        p1 = tuple(sorted((x / sum(pa) for x in pa), reverse=True))
        p2 = tuple(sorted((x / sum(pb) for x in pb), reverse=True))
        if not (maj(p1, p2)):
            continue
        if not (in_An(gam, p1) and in_An(gam, p2)):
            continue
        adm += 1
        bad = []
        for v in GRID:
            na = sum(pi * gi * v ** gi for pi, gi in zip(p1, gam))
            da = sum(pi * v ** gi for pi, gi in zip(p1, gam))
            nb = sum(pi * gi * v ** gi for pi, gi in zip(p2, gam))
            db = sum(pi * v ** gi for pi, gi in zip(p2, gam))
            dv = na / da - nb / db
            if dv > 0:   # claim (i) P>=hr Q <=> h_P<=h_Q i.e. diff<=0
                bad.append(v)
        if bad:
            viol += 1
            ex = ex or (gam, p1, p2, bad)
    print("Thm 5(i) (hr, pi-maj, PHR): admissible", adm, "violating", viol,
          "EX:", ex)


if __name__ == "__main__":
    sweep_cor3()
    sweep_thm5()
