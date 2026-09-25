#!/usr/bin/env python3
"""Exact rational counterexamples for the softmax threshold manuscript.

Every quantity here is computed with exact rational arithmetic.  The
temperature tau = 8 log 2 (or its negative) makes every exponential weight
exp(tau x_i) = 2^(8 x_i) rational for inputs on the grid (1/8) Z.
"""
from fractions import Fraction as Fr
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from roots import exp_enclosure  # noqa: E402  (own module, standard library)


def softmax_mean(values, sign):
    """B_tau(values) for tau = sign * 8 log 2, exactly."""
    assert sign in (1, -1)
    weights = []
    for v in values:
        e = sign * 8 * Fr(v)
        assert e.denominator == 1
        e = int(e)
        weights.append(Fr(2 ** e) if e >= 0 else Fr(1, 2 ** (-e)))
    num = sum(Fr(v) * w for v, w in zip(values, weights))
    den = sum(weights)
    return num / den


def majorizes(x, y):
    """x majorizes y: equal totals and dominating decreasing prefix sums."""
    x = sorted((Fr(v) for v in x), reverse=True)
    y = sorted((Fr(v) for v in y), reverse=True)
    if len(x) != len(y) or sum(x) != sum(y):
        return False
    px = py = Fr(0)
    for a, b in zip(x, y):
        px += a
        py += b
        if px < py:
            return False
    return True


def is_permutation(x, y):
    return sorted(Fr(v) for v in x) == sorted(Fr(v) for v in y)


def main():
    report = {}

    # 1. Box / unrestricted claim: [0,1]^3, tau = 8 log 2 > 0.
    x = (Fr(1), Fr(1, 2), Fr(0))
    y = (Fr(1), Fr(1, 4), Fr(1, 4))
    assert majorizes(x, y) and not is_permutation(x, y)
    bx, by = softmax_mean(x, 1), softmax_mean(y, 1)
    assert bx == Fr(88, 91) and by == Fr(43, 44)
    assert bx - by == Fr(-41, 4004) < 0     # Schur-convexity fails for tau > 0
    report["box_positive"] = (str(bx), str(by), str(bx - by))

    # Reflection x -> 1 - x with tau -> -tau: Schur-concavity fails for tau < 0.
    rx = tuple(1 - v for v in x)
    ry = tuple(1 - v for v in y)
    assert majorizes(rx, ry) and not is_permutation(rx, ry)
    brx, bry = softmax_mean(rx, -1), softmax_mean(ry, -1)
    assert brx == 1 - bx and bry == 1 - by
    assert brx - bry == Fr(41, 4004) > 0
    report["box_negative_reflected"] = (str(brx), str(bry), str(brx - bry))

    # Domain match with the ICLR setting: three agents, nonnegative efforts,
    # each row (agent) summing to one, columns given by x and y.
    for col in (x, y):
        rows = [(v, 1 - v) for v in col]
        assert all(0 <= a <= 1 and 0 <= b <= 1 and a + b == 1 for a, b in rows)
        rows3 = [(v, 1 - v, Fr(0)) for v in col]      # N = M = 3 with an idle task
        assert all(sum(r) == 1 for r in rows3)

    # tau (b - a) = 8 log 2 with b - a = 1: certified above every n = 3 cutoff.
    assert exp_enclosure(Fr(3, 5))[1] < 2        # so log 2 > 3/5, 8 log 2 > 24/5
    assert Fr(24, 5) > Fr("4.745713")            # > 2 c_3 > d_3 = c_3

    # 2. Simplex, positive temperature: Delta_3(1), tau = 8 log 2 > d_3.
    u = (Fr(3, 4), Fr(1, 4), Fr(0))
    v = (Fr(3, 4), Fr(1, 8), Fr(1, 8))
    assert majorizes(u, v) and not is_permutation(u, v)
    assert all(t >= 0 for t in u + v) and sum(u) == sum(v) == 1
    bu, bv = softmax_mean(u, 1), softmax_mean(v, 1)
    assert bu == Fr(49, 69) and bv == Fr(97, 136)
    assert bu - bv == Fr(-29, 9384) < 0
    report["simplex_positive"] = (str(bu), str(bv), str(bu - bv))

    # 3. Simplex, negative temperature: Delta_3(1), |tau| = 8 log 2 > 2 c_3.
    p = (Fr(0), Fr(3, 8), Fr(5, 8))
    q = (Fr(0), Fr(1, 2), Fr(1, 2))
    assert majorizes(p, q) and not is_permutation(p, q)
    assert all(t >= 0 for t in p + q) and sum(p) == sum(q) == 1
    bp, bq = softmax_mean(p, -1), softmax_mean(q, -1)
    assert bp == Fr(17, 296) and bq == Fr(1, 18)
    assert bp - bq == Fr(5, 2664) > 0
    report["simplex_negative"] = (str(bp), str(bq), str(bp - bq))

    for k, val in report.items():
        print(f"{k}: B(more spread) = {val[0]}, B(less spread) = {val[1]}, difference = {val[2]}")
    print("all exact counterexample checks passed")


if __name__ == "__main__":
    main()
