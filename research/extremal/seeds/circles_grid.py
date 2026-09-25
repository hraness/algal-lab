# Seed program: circles on a jittered grid, radii shrunk to exact feasibility. PARAMS is the genome.
PARAMS = {"columns": 5, "jitter": 0.02, "shrink": 0.98}

from fractions import Fraction
import random


def construct(parameters, seed):
    n = parameters["n"]
    rng = random.Random(seed)
    cols = max(1, int(PARAMS["columns"]))
    rows = -(-n // cols)
    cell_w, cell_h = Fraction(1, cols), Fraction(1, rows)
    r = min(cell_w, cell_h) / 2 * Fraction(str(round(float(PARAMS["shrink"]), 4)))
    circles = []
    for i in range(n):
        cx = cell_w * (i % cols) + cell_w / 2
        cy = cell_h * (i // cols) + cell_h / 2
        jitter = Fraction(str(round(rng.uniform(-1, 1) * float(PARAMS["jitter"]), 4)))
        cx = min(max(cx + jitter, r), 1 - r)
        circles.append([str(cx), str(cy), str(r)])
    return {"circles": circles}
