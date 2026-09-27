"""Controls C1 and C2 for the closed-form certificate type (protocol amendment 3).

Run: /Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python controls_closed.py
"""
import json
import sys

import sympy as sp

from closedform import Closed, check, x

R = sp.Rational


def gamma_int(shape):
    return Closed(sp.exp(-x) * sum(x ** j / sp.factorial(j) for j in range(shape)))


def weibull(shape, scale):
    return Closed(sp.exp(-(x / scale) ** shape))


def lfr(alpha, beta):
    return Closed(sp.exp(-alpha * x - beta * x ** 2 / 2))


def lomax(a):
    return Closed((1 + x) ** (-a))


C1 = [
    ("gamma shape 2 vs 3", gamma_int(2), gamma_int(3), "lr"),
    ("Weibull shape 2, scale 1 vs 2", weibull(2, 1), weibull(2, 2), "lr"),
    ("linear failure rate, alpha 2 vs 1, beta 1", lfr(2, 1), lfr(1, 1), "lr"),
    ("Lomax a=3 vs a=2", lomax(3), lomax(2), "lr"),
    ("gamma shape 2 vs 3, hazard", gamma_int(2), gamma_int(3), "hr"),
    ("Weibull shape 2, scale 1 vs 2, hazard", weibull(2, 1), weibull(2, 2), "hr"),
    ("Lomax a=3 vs a=2, usual", lomax(3), lomax(2), "st"),
    ("linear failure rate, alpha 2 vs 1, usual", lfr(2, 1), lfr(1, 1), "st"),
]
C2 = [("flipped: " + n, Y, X, o) for n, X, Y, o in C1] + [
    ("Weibull shape 1 vs 2, usual (survivals cross at 1)", weibull(1, 1), weibull(2, 1), "st"),
    ("Weibull shape 2 vs 1, usual (survivals cross at 1)", weibull(2, 1), weibull(1, 1), "st"),
]


def run(claims, expect):
    rows = []
    for name, X, Y, order in claims:
        holds, witness, undecided = check(order, X, Y)
        rows.append({"claim": name, "order": order, "holds_on_grid": holds,
                     "witness": None if witness is None else str(witness),
                     "undecided_points": undecided, "as_expected": holds == expect})
    return rows


if __name__ == "__main__":
    c1, c2 = run(C1, True), run(C2, False)
    report = {"C1": c1, "C2": c2, "C1_all_hold": all(r["as_expected"] for r in c1),
              "C2_refuted": sum(r["as_expected"] for r in c2), "C2_total": len(c2)}
    json.dump(report, sys.stdout, indent=1)
    print()
    sys.exit(0 if report["C1_all_hold"] and report["C2_refuted"] >= 0.9 * len(c2) else 1)
