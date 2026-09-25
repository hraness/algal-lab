# Seed program: randomized greedy covering with restarts. PARAMS is the scripted-mutation genome.
PARAMS = {"restarts": 20, "candidates": 40, "bias": 1.0}

from itertools import combinations
import random


def construct(parameters, seed):
    v, k, t = parameters["v"], parameters["k"], parameters["t"]
    rng = random.Random(seed)
    subsets = [sum(1 << p for p in s) for s in combinations(range(v), t)]
    best = None
    for _ in range(max(1, int(PARAMS["restarts"]))):
        uncovered = set(subsets)
        blocks = []
        while uncovered:
            best_block, best_gain = None, -1
            for _ in range(max(1, int(PARAMS["candidates"]))):
                block = rng.sample(range(v), k)
                mask = sum(1 << p for p in block)
                gain = sum(1 for s in uncovered if s & mask == s)
                gain += rng.random() * float(PARAMS["bias"])
                if gain > best_gain:
                    best_block, best_gain, best_mask = block, gain, mask
            blocks.append(sorted(best_block))
            uncovered = {s for s in uncovered if s & best_mask != s}
        if best is None or len(blocks) < len(best):
            best = blocks
    return {"blocks": best}
