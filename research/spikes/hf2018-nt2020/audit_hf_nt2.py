"""HF/NT audit round 2: report raw sign patterns of htilde_p - htilde_q
under single T-transforms, by class (V/W) and n, both directions.
Integer lambda only (exact polynomial arithmetic)."""
import sys, random, itertools
sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/mixture-audit")
import sympy as sp
from audit_lib import R, in_Vn, in_Wn

s = sp.Symbol("s", positive=True)
GRID = [R(1, 32), R(1, 16), R(1, 8), R(1, 4), R(1, 2),
        R(3, 4), R(7, 8), R(15, 16), R(31, 32)]


def htilde(p, lam, u):
    num = sum(pi * li * u ** int(li) for pi, li in zip(p, lam))
    den = sum(pi * u ** int(li) for pi, li in zip(p, lam))
    return sp.cancel(num / den)


def ttransform(mat2, i, j, om):
    a = [list(r) for r in mat2]
    for r in range(2):
        ai, aj = a[r][i], a[r][j]
        a[r][i] = om * ai + (1 - om) * aj
        a[r][j] = (1 - om) * ai + om * aj
    return a


def scan(cls, n, trials, seed):
    rng = random.Random(seed)
    tally = {"all+": 0, "all-": 0, "zero": 0, "crossing": 0}
    ex_cross = None; ex_plus = None; ex_minus = None
    adm = 0
    for _ in range(trials):
        p = tuple(R(rng.randint(1, 40), 40) for _ in range(n))
        tot = sum(p); p = tuple(pi / tot for pi in p)
        lam = tuple(rng.randint(1, 9) for _ in range(n))
        chk = in_Vn if cls == "V" else in_Wn
        if not chk(list(p), list(lam)):
            continue
        i, j = sorted(rng.sample(range(n), 2))
        om = R(rng.randint(1, 19), 20)
        qg = ttransform([list(p), list(lam)], i, j, om)
        q, gam = qg[0], qg[1]
        if q == list(p) and gam == list(lam):
            continue
        adm += 1
        # d = h_p - h_q = [num_p den_q - num_q den_p] / (den_p den_q);
        # denominator > 0 on (0,1) (sums of positive monomials): sign = num.
        num_p = sum(pi * li * s ** int(li) for pi, li in zip(p, lam))
        den_p = sum(pi * s ** int(li) for pi, li in zip(p, lam))
        num_q = sum(qi * gi * s ** int(gi) for qi, gi in zip(q, gam))
        den_q = sum(qi * s ** int(gi) for qi, gi in zip(q, gam))
        d = sp.expand(num_p * den_q - num_q * den_p)
        vals = [sp.sign(d.subs(s, v)) for v in GRID]
        sset = set(vals) - {0}
        if not sset:
            tally["zero"] += 1
        elif len(sset) > 1:
            tally["crossing"] += 1
            ex_cross = ex_cross or (p, lam, q, gam, i, j, om,
                                    list(zip(GRID, vals)))
        elif sset == {1}:
            tally["all+"] += 1
            ex_plus = ex_plus or (p, lam, q, gam, i, j, om)
        else:
            tally["all-"] += 1
            ex_minus = ex_minus or (p, lam, q, gam, i, j, om)
    return adm, tally, ex_cross, ex_plus, ex_minus


if __name__ == "__main__":
    for cls in ("V", "W"):
        for n in (2, 3, 4):
            adm, tally, xc, xp, xm = scan(cls, n, 4000, 100 + n)
            print(f"cls={cls} n={n} admissible={adm} sign(h_p - h_q): {tally}")
            if xc:
                print("   crossing ex:", xc)
