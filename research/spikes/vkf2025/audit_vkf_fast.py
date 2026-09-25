"""Fast Fraction-arithmetic scan for VKF-reconstructed claims.

inner(t) = sum p_i * Gbar(t/theta_i)^{ag}; grid of rational t;
compare inner_U vs inner_V exactly. Violations handed to sympy/Sturm.
"""
import random
from fractions import Fraction as F
from audit_lib import weak_super, weak_sub, p_larger

GRID_POS = [F(1, 4), F(1, 2), F(1), F(2), F(3), F(5), F(8), F(15)]
GRID_01 = [F(1, 8), F(1, 4), F(1, 2), F(3, 4), F(7, 8), F(15, 16)]


def inner_val(p, theta, ag, t, base):
    """Exact Fraction value of inner at rational t."""
    tot = F(0)
    for pi, th in zip(p, theta):
        if base == "lomax":
            u = F(th) / (F(th) + t)
        else:  # power2, t < min theta
            u = 1 - (t / F(th)) ** 2
        tot += pi * u ** ag
    return tot


def diff_signs(p, theta, xi, ag, base):
    grid = GRID_POS if base == "lomax" else GRID_01
    return [(v, (inner_val(p, theta, ag, v, base)
                 - inner_val(p, xi, ag, v, base)))
            for v in grid]


def rand_sorted_prob(rng, n, dec=False):
    p = [F(rng.randint(1, 40), 40) for _ in range(n)]
    tot = sum(p)
    p = [pi / tot for pi in p]
    return tuple(sorted(p, reverse=dec))


def rand_sorted_ints(rng, n, lo, hi, dec=True):
    return tuple(sorted((F(rng.randint(lo, hi)) for _ in range(n)),
                        reverse=dec))


def audit_R1(trials, seed=5):
    rng = random.Random(seed)
    res = {}
    ex = {}
    for _ in range(trials):
        n = rng.choice([2, 3, 3, 4])
        for pdir, tdir in (("inc", "dec"), ("dec", "inc")):
            p = rand_sorted_prob(rng, n, dec=(pdir == "dec"))
            gam = rng.choice([F(1, 2), F(1), F(2), F(3), F(5)])
            cands = [gam, gam + F(1, 2), 2 * gam, gam + 3, F(2), F(4)]
            cands = [a for a in cands
                     if a >= gam and (a * gam).denominator == 1]
            if not cands:
                continue
            alpha = rng.choice(cands)
            ag = int(alpha * gam)
            theta = rand_sorted_ints(rng, n, 1, 9, dec=(tdir == "dec"))
            xi = rand_sorted_ints(rng, n, 1, 9, dec=(tdir == "dec"))
            if not weak_super(list(theta), list(xi)) or theta == xi:
                continue
            for base in ("lomax", "power2"):
                if base == "power2" and min(min(theta), min(xi)) <= 1:
                    continue
                dv = diff_signs(p, theta, xi, ag, base)
                signs = {1 if d > 0 else (-1 if d < 0 else 0)
                         for _, d in dv} - {0}
                key = (n, pdir, tdir, base, "ag>1" if ag > 1 else "ag<=1")
                res.setdefault(key, [0, 0])
                res[key][0] += 1
                if len(signs) > 1 or (signs and signs.pop() != 1):
                    res[key][1] += 1
                    ex.setdefault(key, (p, gam, alpha, theta, xi,
                                        [(str(v), str(d)) for v, d in dv]))
    return res, ex


def audit_R3(trials, seed=9):
    rng = random.Random(seed)
    res = {"p_sub": [0, 0], "p_super": [0, 0]}
    ex = {}
    for _ in range(trials):
        n = 3
        p = rand_sorted_prob(rng, n)
        q = rand_sorted_prob(rng, n)
        theta = rand_sorted_ints(rng, n, 1, 9)
        xi = rand_sorted_ints(rng, n, 1, 9)
        gam = rng.choice([F(1, 2), F(1), F(2), F(3)])
        cands = [gam, gam + 1, 2 * gam, F(1, 2), F(1), F(2)]
        cands = [a for a in cands if (a * gam).denominator == 1]
        alpha = rng.choice(cands)
        ag = int(alpha * gam)
        if not weak_super(list(theta), list(xi)) or theta == xi:
            continue
        dv = [(v, (inner_val(p, theta, ag, v, "lomax")
                   - inner_val(q, xi, ag, v, "lomax"))) for v in GRID_POS]
        signs = {1 if d > 0 else (-1 if d < 0 else 0) for _, d in dv} - {0}
        viol = len(signs) > 1 or (signs and signs.pop() != 1)
        if weak_sub(list(p), list(q)):
            res["p_sub"][0] += 1
            if viol:
                res["p_sub"][1] += 1
                ex.setdefault("p_sub", (p, q, gam, alpha, theta, xi,
                                        [(str(v), str(d)) for v, d in dv]))
        if weak_super(list(p), list(q)):
            res["p_super"][0] += 1
            if viol:
                res["p_super"][1] += 1
                ex.setdefault("p_super", (p, q, gam, alpha, theta, xi,
                                          [(str(v), str(d)) for v, d in dv]))
    return res, ex


if __name__ == "__main__":
    import sys
    tr = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    res, ex = audit_R1(tr)
    print("== R1 (VKF 3.1(i) recon: alpha >= gamma) ==")
    for k in sorted(res, key=str):
        print(f"  {k}: admissible={res[k][0]} violations={res[k][1]}")
        if res[k][1]:
            print(f"     ex: {ex[k]}")
    sys.stdout.flush()
    res3, ex3 = audit_R3(tr)
    print("== R3 (VKF 3.10 recon, alpha>0) ==", res3)
    for k, v in ex3.items():
        print("   ex", k, v)
