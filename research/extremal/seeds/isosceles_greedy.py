# Seed program: randomized greedy insertion with restarts for isosceles-free grid subsets.
PARAMS = {"restarts": 6, "passes": 2, "shuffle_bias": 1.0}

import random


def construct(parameters, seed):
    n = parameters["n"]
    rng = random.Random(seed)
    cells = [(x, y) for x in range(n) for y in range(n)]
    best = []
    for _ in range(max(1, int(PARAMS["restarts"]))):
        chosen = []
        dist = {}  # point -> set of squared distances to other chosen points
        order = cells[:]
        rng.shuffle(order)
        for _ in range(max(1, int(PARAMS["passes"]))):
            for p in order:
                if p in dist:
                    continue
                ok = True
                own = set()
                for q in chosen:
                    d = (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
                    if d in own or d in dist[q]:
                        ok = False
                        break
                    own.add(d)
                if ok:
                    for q in chosen:
                        dist[q].add((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)
                    dist[p] = own
                    chosen.append(p)
        if len(chosen) > len(best):
            best = chosen
    return {"points": [list(p) for p in best]}
