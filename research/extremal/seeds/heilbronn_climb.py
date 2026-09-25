# Seed program: random points in the unit square, hill-climbed on the smallest triangle area; output truncated decimals.
PARAMS = {"restarts": 3, "steps": 400, "step_size": 0.05, "decimals": 15}

import random
from itertools import combinations


def min_area(pts):
    best = None
    for (ax, ay), (bx, by), (cx, cy) in combinations(pts, 3):
        area = abs((bx - ax) * (cy - ay) - (cx - ax) * (by - ay)) / 2
        if best is None or area < best:
            best = area
    return best


def construct(parameters, seed):
    n = parameters["n"]
    rng = random.Random(seed)
    best_pts, best_val = None, -1.0
    for _ in range(max(1, int(PARAMS["restarts"]))):
        pts = [(rng.random(), rng.random()) for _ in range(n)]
        val = min_area(pts)
        step = float(PARAMS["step_size"])
        for _ in range(max(1, int(PARAMS["steps"]))):
            i = rng.randrange(n)
            x = min(1.0, max(0.0, pts[i][0] + rng.gauss(0, step)))
            y = min(1.0, max(0.0, pts[i][1] + rng.gauss(0, step)))
            trial = pts[:]
            trial[i] = (x, y)
            v = min_area(trial)
            if v > val:
                pts, val = trial, v
            else:
                step = max(1e-4, step * 0.995)
        if val > best_val:
            best_pts, best_val = pts, val
    d = max(1, min(30, int(PARAMS["decimals"])))
    scale = 10 ** d
    return {"points": [[f"{int(x * scale) / scale:.{d}f}", f"{int(y * scale) / scale:.{d}f}"] for x, y in best_pts]}
