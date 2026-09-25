# Seed program: interval plus random extras, hill-climbed on the sum-difference ratio (float inside, exact ints out).
PARAMS = {"base_low": -40, "base_high": 30, "extras": 8, "spread": 120, "steps": 150}

import math
import random


def score(a):
    a = list(a)
    n = len(a)
    sums = {x + y for x in a for y in a}
    diffs = {x - y for x in a for y in a}
    if len(diffs) <= n:
        return -1.0
    return math.log(len(sums) / n) / math.log(len(diffs) / n)


def construct(parameters, seed):
    rng = random.Random(seed)
    a = set(range(int(PARAMS["base_low"]), int(PARAMS["base_high"]) + 1))
    for _ in range(max(0, int(PARAMS["extras"]))):
        a.add(rng.randint(int(PARAMS["base_high"]), int(PARAMS["base_high"]) + int(PARAMS["spread"])))
    best, best_score = set(a), score(a)
    for _ in range(max(1, int(PARAMS["steps"]))):
        cand = set(best)
        if rng.random() < 0.5 and len(cand) > 3:
            cand.discard(rng.choice(sorted(cand)))
        else:
            cand.add(rng.randint(int(PARAMS["base_low"]) - int(PARAMS["spread"]), int(PARAMS["base_high"]) + int(PARAMS["spread"])))
        s = score(cand)
        if s > best_score:
            best, best_score = cand, s
    return {"set": sorted(best)}
