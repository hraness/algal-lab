"""Fractional-alpha scan for VKF R1 reconstruction (ag < 1 and half-integers),
60-digit mpmath, mirroring the sibling audit's 'numerical' classification.
Question: is the clean region ag <= 1 or only ag == 1?  (alpha >= gamma with
gamma < 1 permits ag < 1.)
"""
import random
from fractions import Fraction as F
import mpmath as mp
from audit_lib import weak_super, weak_sub

mp.mp.dps = 60

GRID_POS = [mp.mpf(1) / 4, mp.mpf(1) / 2, mp.mpf(1), mp.mpf(2), mp.mpf(3),
            mp.mpf(5), mp.mpf(8), mp.mpf(15)]


def inner_val(p, theta, ag, t):
    tot = mp.mpf(0)
    for pi, th in zip(p, theta):
        thf = mp.mpf(int(th))
        u = thf / (thf + t)   # Lomax
        pif = mp.mpf(int(pi.numerator)) / int(pi.denominator)
        tot += pif * u ** ag
    return tot


def rand_sorted_prob(rng, n, dec=False):
    p = [F(rng.randint(1, 40), 40) for _ in range(n)]
    tot = sum(p)
    return tuple(sorted((pi / tot for pi in p), reverse=dec))


def rand_sorted_ints(rng, n, lo, hi, dec=True):
    return tuple(sorted((F(rng.randint(lo, hi)) for _ in range(n)),
                        reverse=dec))


def audit_R1_frac(trials=8000, seed=21):
    rng = random.Random(seed)
    res = {}
    ex = {}
    for _ in range(trials):
        n = rng.choice([2, 3, 3, 4])
        for pdir, tdir in (("inc", "dec"), ("dec", "inc")):
            p = rand_sorted_prob(rng, n, dec=(pdir == "dec"))
            gam = rng.choice([F(1, 4), F(1, 3), F(1, 2), F(2, 3), F(3, 4),
                              F(1), F(2)])
            # alpha >= gamma, fractional products allowed
            cands = [gam, gam + F(1, 4), gam + F(1, 2), 2 * gam, gam + 1,
                     F(1), F(3, 2), F(2)]
            cands = [a for a in cands if a >= gam]
            alpha = rng.choice(cands)
            ag = mp.mpf(alpha.numerator) / alpha.denominator * \
                mp.mpf(gam.numerator) / gam.denominator
            theta = rand_sorted_ints(rng, n, 1, 9, dec=(tdir == "dec"))
            xi = rand_sorted_ints(rng, n, 1, 9, dec=(tdir == "dec"))
            if not weak_super(list(theta), list(xi)) or theta == xi:
                continue
            dv = [inner_val(p, theta, ag, v) - inner_val(p, xi, ag, v)
                  for v in GRID_POS]
            signs = {1 if d > 0 else (-1 if d < 0 else 0) for d in dv} - {0}
            key = ("ag<1" if ag < 1 else ("ag=1" if ag == 1 else "ag>1"))
            res.setdefault(key, [0, 0])
            res[key][0] += 1
            if len(signs) > 1 or (signs and signs.pop() != 1):
                res[key][1] += 1
                ex.setdefault(key, (p, gam, alpha, theta, xi,
                                    [mp.nstr(d, 6) for d in dv]))
    return res, ex


if __name__ == "__main__":
    res, ex = audit_R1_frac()
    for k in sorted(res):
        print(f"{k}: admissible={res[k][0]} violations={res[k][1]}")
        if res[k][1]:
            print("   ex:", ex[k])
