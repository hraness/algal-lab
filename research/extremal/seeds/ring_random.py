# Seed program: random search over reversal-symmetric dyadic ring loading instances (integer scoring inside, exact fraction strings out).
PARAMS = {"trials": 20, "denominator": 16, "mutations": 3}

import random
from itertools import product


def alpha(u, v):
    m = len(u)
    best = None
    for bits in range(1 << m):
        z = [v[i] if bits >> i & 1 else -u[i] for i in range(m)]
        total = sum(z)
        worst, prefix = 0, 0
        for k in range(m - 1):
            prefix += z[k]
            worst = max(worst, abs(2 * prefix - total))
            if best is not None and worst >= best:
                break
        if best is None or worst < best:
            best = worst
    return best


def construct(parameters, seed):
    m = parameters["m"]
    rng = random.Random(seed)
    den = max(2, int(PARAMS["denominator"]))
    # integer numerators in units of 1/den; v_i = u_{m-1-i} (reversal symmetry)
    u = [rng.randint(0, den) for _ in range(m)]
    for i in range(m):
        if u[i] + u[m - 1 - i] > den:
            u[i] = den - u[m - 1 - i]
    best_u, best_val = u[:], alpha(u, u[::-1])
    for _ in range(max(1, int(PARAMS["trials"]))):
        cand = best_u[:]
        for _ in range(max(1, int(PARAMS["mutations"]))):
            i = rng.randrange(m)
            cand[i] = max(0, min(den, cand[i] + rng.choice((-2, -1, 1, 2))))
            if cand[i] + cand[m - 1 - i] > den:
                cand[i] = den - cand[m - 1 - i]
        val = alpha(cand, cand[::-1])
        if val > best_val:
            best_u, best_val = cand, val
    return {"pairs": [[f"{best_u[i]}/{den}", f"{best_u[m - 1 - i]}/{den}"] for i in range(m)]}
