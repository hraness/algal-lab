"""Printed examples of doi:10.7153/mia-2020-23-03 that the exact harness can decide.

Pareto(1, lam) marginals, F(x) = 1 - x^{-lam} on x >= 1, written in w = 1/x
(w decreases in x). With a rational copula (AMH, FGM) the largest claim amount's
survival is a rational function of w, so st is decided exactly. Half-integer
rates use w = v^2.

  P(Y <= t) = p00 + p10 F1 + p01 F2 + p11 C(F1, F2)
"""
import json

import sympy as sp

from ratdist import Dist, st, z

R = sp.Rational
ONE, ZERO = sp.Integer(1), sp.Integer(0)


def amh(theta):
    return lambda u, v: u * v / (1 - theta * (1 - u) * (1 - v))


def fgm(theta):
    return lambda u, v: u * v * (1 + theta * (1 - u) * (1 - v))


def largest(lams, pmf, copula, power):
    """power: w = z**power so that every lam * power is an integer."""
    F = [1 - z ** int(R(l) * power) for l in lams]
    cdf = pmf[(0, 0)] + pmf[(1, 0)] * F[0] + pmf[(0, 1)] * F[1] + pmf[(1, 1)] * copula(F[0], F[1])
    return Dist(sp.together(1 - cdf), ZERO, ONE, increasing=False)


def independent_pmf(p1, p2):
    p1, p2 = R(p1), R(p2)
    return {(0, 0): (1 - p1) * (1 - p2), (1, 0): p1 * (1 - p2), (0, 1): (1 - p1) * p2, (1, 1): p1 * p2}


def verdict(Ystar, Y):
    le, w1 = st(Ystar, Y)
    ge, w2 = st(Y, Ystar)
    return {"Ystar_le_st_Y": le, "witness_if_not": None if le else str(w1),
            "Y_le_st_Ystar": ge, "witness_if_not_reverse": None if ge else str(w2)}


if __name__ == "__main__":
    out = {}
    # Example 3.3: AMH theta = 0.3, lam = (4, 2), p = (0.02, 0.06); lam* = (4, 6), p* = (0.0479, 0.0319).
    c = amh(R(3, 10))
    Y = largest([4, 2], independent_pmf("0.02", "0.06"), c, 1)
    Ys = largest([4, 6], independent_pmf("0.0479", "0.0319"), c, 1)
    out["Example 3.3 (printed: Y* <=st Y)"] = verdict(Ys, Y)
    h = lambda p: sp.log(R(p) + 2)
    out["Example 3.3 hypothesis h(p*) majorized by h(p): sums equal?"] = {
        "h(p1)+h(p2) = log(2.02*2.06)": str(R("2.02") * R("2.06")),
        "h(p*1)+h(p*2) = log(2.0479*2.0319)": str(R("2.0479") * R("2.0319")),
        "equal": R("2.02") * R("2.06") == R("2.0479") * R("2.0319")}
    # Examples 3.5 and 3.6: FGM theta = 0.7, pmf p00=.89 p01=.06 p10=.04 p11=.01, lam* = (5.5, 3.5).
    pmf = {(0, 0): R("0.89"), (0, 1): R("0.06"), (1, 0): R("0.04"), (1, 1): R("0.01")}
    c = fgm(R(7, 10))
    Ys = largest([R(11, 2), R(7, 2)], pmf, c, 2)
    out["Example 3.5 (printed: Y* <=st Y), lam = (7, 2)"] = verdict(Ys, largest([7, 2], pmf, c, 2))
    out["Example 3.6 (printed: survivals cross), lam = (2, 7)"] = verdict(Ys, largest([2, 7], pmf, c, 2))
    print(json.dumps(out, indent=1))
