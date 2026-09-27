"""Protocol controls C1 (known true) and C2 (planted false), run through the harness.

C1: 20 instances of standard results, each a strict ordering.
C2: 18 direction flips of strict C1 instances (false because the original is
    strict), plus both directions of the certified CERT F instance from the
    cluster audit (research/spikes/cluster-expand/memo.md), where the density
    ratio of two exponential mixtures rises then falls, so neither mixture is
    likelihood-ratio smaller.

Run: /Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python controls.py
"""
import json
import sys

import sympy as sp

from ratdist import ORDERS, Dist, exp_mixture, order_statistic_exponentials, z

R = sp.Rational
ONE, ZERO = sp.Integer(1), sp.Integer(0)


def on_unit(survival):
    """A distribution on (0, 1) written in z = t."""
    return Dist(sp.expand(survival), ZERO, ONE, increasing=True)


def power_function(a):
    return on_unit(1 - z ** a)


def beta_one(b):
    return on_unit((1 - z) ** b)


def kumaraswamy(a, b):
    return on_unit((1 - z ** a) ** b)


def uniform_order_statistic(k, n):
    """P(U_{k:n} > t) = P(fewer than k of n uniforms are <= t)."""
    return on_unit(sum(sp.binomial(n, j) * z ** j * (1 - z) ** (n - j) for j in range(k)))


def exp1(rate, D=1):
    return exp_mixture([1], [rate], D)


def os_exp(rates, k, D=1):
    return order_statistic_exponentials(rates, k, D)


C1 = [
    ("exponential rates 2 vs 1", "Shaked-Shanthikumar 2007, exponential family", exp1(2), exp1(1), "lr"),
    ("exponential rates 3 vs 3/2", "Shaked-Shanthikumar 2007, exponential family", exp1(3, 2), exp1(R(3, 2), 2), "hr"),
    ("series systems, rate sums 5 vs 4", "minimum of exponentials is exponential", os_exp([1, 4], 1), os_exp([2, 2], 1), "lr"),
    ("maxima (2,2) vs (1,3)", "Pledger-Proschan 1971", os_exp([2, 2], 2), os_exp([1, 3], 2), "st"),
    ("2nd of 3, (3,3,3) vs (1,2,6)", "Pledger-Proschan 1971", os_exp([3, 3, 3], 2), os_exp([1, 2, 6], 2), "st"),
    ("maxima of 3, (3,3,3) vs (1,2,6)", "Pledger-Proschan 1971", os_exp([3, 3, 3], 3), os_exp([1, 2, 6], 3), "st"),
    ("maxima of 3, (2,2,5) vs (1,2,6)", "Pledger-Proschan 1971", os_exp([2, 2, 5], 3), os_exp([1, 2, 6], 3), "st"),
    ("maxima of 3, (3,3,3) vs (1,2,6), hazard", "Dykstra-Kochar-Rojo 1997", os_exp([3, 3, 3], 3), os_exp([1, 2, 6], 3), "hr"),
    ("maxima of 2, (2,2) vs (1,3), hazard", "Boland-El-Neweihi-Proschan 1994", os_exp([2, 2], 2), os_exp([1, 3], 2), "hr"),
    ("Exp(3) vs mixture of Exp(1), Exp(3)", "mixture hazard lies between component hazards",
     exp1(3), exp_mixture([R(1, 2), R(1, 2)], [1, 3], 1), "hr"),
    ("mixture of Exp(1), Exp(3) vs Exp(1)", "mixture hazard lies between component hazards",
     exp_mixture([R(1, 2), R(1, 2)], [1, 3], 1), exp1(1), "hr"),
    ("mixtures of Exp(2), Exp(1) with weights 3/4 vs 1/4", "lr-ordered mixing of an lr-ordered family",
     exp_mixture([R(3, 4), R(1, 4)], [2, 1], 1), exp_mixture([R(1, 4), R(3, 4)], [2, 1], 1), "lr"),
    ("power function a=2 vs a=3", "power-function family", power_function(2), power_function(3), "lr"),
    ("Beta(1,3) vs Beta(1,2)", "beta family", beta_one(3), beta_one(2), "lr"),
    ("uniform order statistics 1:3 vs 2:3", "order statistics are lr-increasing in rank",
     uniform_order_statistic(1, 3), uniform_order_statistic(2, 3), "lr"),
    ("uniform order statistics 2:3 vs 3:3", "order statistics are lr-increasing in rank",
     uniform_order_statistic(2, 3), uniform_order_statistic(3, 3), "lr"),
    ("uniform order statistics 2:4 vs 2:3", "X_{k:n+1} <=lr X_{k:n}",
     uniform_order_statistic(2, 4), uniform_order_statistic(2, 3), "lr"),
    ("Kumaraswamy (1,2) vs (2,2)", "survival (1-t^a)^b increases in a", kumaraswamy(1, 2), kumaraswamy(2, 2), "st"),
    ("power function a=2 vs a=3, reversed hazard", "lr implies rh", power_function(2), power_function(3), "rh"),
    ("Beta(1,3) vs Beta(1,2), hazard", "lr implies hr", beta_one(3), beta_one(2), "hr"),
]

# CERT F instance: p=(1/8,29/72,17/36), lambda=(9,5,4); q=(2/9,11/36,17/36), gamma=(38/5,32/5,4).
CERT_F_P = exp_mixture([R(1, 8), R(29, 72), R(17, 36)], [9, 5, 4], 5)
CERT_F_Q = exp_mixture([R(2, 9), R(11, 36), R(17, 36)], [R(38, 5), R(32, 5), 4], 5)

C2 = [("flipped: " + name, source, Y, X, order) for name, source, X, Y, order in C1[:18]] + [
    ("CERT F mixtures, p vs q", "cluster audit CERT F (Sturm certificate)", CERT_F_P, CERT_F_Q, "lr"),
    ("CERT F mixtures, q vs p", "cluster audit CERT F (Sturm certificate)", CERT_F_Q, CERT_F_P, "lr"),
]


def run(claims, expect_hold):
    rows = []
    for name, source, X, Y, order in claims:
        holds, witness = ORDERS[order](X, Y)
        rows.append({"claim": name, "source": source, "order": order, "holds": holds,
                     "witness": None if witness is None else str(witness),
                     "as_expected": holds == expect_hold})
    return rows


def main():
    c1, c2 = run(C1, True), run(C2, False)
    report = {"C1_known_true": c1, "C2_planted_false": c2,
              "C1_all_hold": all(r["as_expected"] for r in c1),
              "C2_refuted": sum(r["as_expected"] for r in c2), "C2_total": len(c2)}
    json.dump(report, sys.stdout, indent=1)
    print()
    return 0 if report["C1_all_hold"] and report["C2_refuted"] >= 0.9 * len(c2) else 1


if __name__ == "__main__":
    sys.exit(main())
