"""Printed examples of doi:10.52547/jsri.16.1.101, checked with the closed-form
interval checker (a bounded rigorous search on the grid)."""
import json

import sympy as sp

import closedform as cf

R, x = sp.Rational, cf.x


def system(alphas, g, l, b, kind):
    F = [(1 - sp.exp(-R(a) * x ** R(g) * sp.exp(R(l) * x))) ** R(b) for a in alphas]
    return cf.Closed(1 - sp.Mul(*F) if kind == "parallel" else sp.Mul(*[1 - f for f in F]))


def both(order, X, Y):
    h1, w1, u1 = cf.check(order, X, Y)
    h2, w2, u2 = cf.check(order, Y, X)
    return {"X_le_Y": h1, "witness": None if h1 else str(w1), "Y_le_X": h2, "witness_rev": None if h2 else str(w2), "undecided": u1 + u2}


out = {
    "Example 1 (printed: X_{3:3} <=rh X*_{3:3})": both("rh",
        system(["0.1", 4, 6], 2, "1.2", "0.5", "parallel"), system(["0.1", 1, 8], 2, "1.2", "0.5", "parallel")),
    "Example 2(i) (printed: X*_{1:3} <=st X_{1:3})": both("st",
        system([8, 3, "0.3"], "1.3", "1.6", "1.3", "series"), system([5, 2, "0.2"], "1.3", "1.6", "1.3", "series")),
    "Example 2(ii) (printed: X_{1:3} <=st X*_{1:3})": both("st",
        system(["0.2", 4, 9], "1.3", "1.6", "0.3", "series"), system(["0.1", 1, 6], "1.3", "1.6", "0.3", "series")),
    "Example 3A (printed: X*_{1:2} <=st X_{1:2})": both("st",
        system([1, "5.5"], 2, 3, "0.5", "series"), system([2, 3], 2, 3, "0.5", "series")),
    "Example 3B (printed: X_{1:2} <=st X*_{1:2})": both("st",
        system(["1.1", 6], 2, 3, "0.5", "series"), system([1, "2.25"], 2, 3, "0.5", "series")),
}
print(json.dumps(out, indent=1))
