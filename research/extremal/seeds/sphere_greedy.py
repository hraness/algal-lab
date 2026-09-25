# Seed program: randomized greedy insertion for no-five-on-a-sphere subsets of the n^3 grid.
PARAMS = {"restarts": 3, "candidate_limit": 400}

import random
from itertools import combinations


def det4(m):
    (a, b, c, d), (e, f, g, h), (i, j, k, l), (m0, n0, o, p) = m
    kp_lo = k * p - l * o; jp_ln = j * p - l * n0; jo_kn = j * o - k * n0
    ip_lm = i * p - l * m0; io_km = i * o - k * m0; in_jm = i * n0 - j * m0
    return (a * (f * kp_lo - g * jp_ln + h * jo_kn) - b * (e * kp_lo - g * ip_lm + h * io_km)
            + c * (e * jp_ln - f * ip_lm + h * in_jm) - d * (e * jo_kn - f * io_km + g * in_jm))


def lift(p):
    x, y, z = p
    return (x, y, z, x * x + y * y + z * z)


def can_add(chosen, lifted, p):
    lp = lift(p)
    for quad in combinations(range(len(chosen)), 4):
        rows = [tuple(lifted[i][c] - lp[c] for c in range(4)) for i in quad]
        if det4(rows) == 0:
            return False
    return True


def construct(parameters, seed):
    n = parameters["n"]
    rng = random.Random(seed)
    cells = [(x, y, z) for x in range(n) for y in range(n) for z in range(n)]
    best = []
    for _ in range(max(1, int(PARAMS["restarts"]))):
        order = cells[:]
        rng.shuffle(order)
        chosen, lifted = [], []
        for p in order[: max(1, int(PARAMS["candidate_limit"]))]:
            if can_add(chosen, lifted, p):
                chosen.append(p)
                lifted.append(lift(p))
        if len(chosen) > len(best):
            best = chosen
    return {"points": [list(p) for p in best]}
