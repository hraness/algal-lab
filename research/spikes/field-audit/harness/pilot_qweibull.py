"""Pilot tests for doi:10.1017/s0269964826100199 (q-Weibull extremes).

q-Weibull survival S(t) = [1 - (1-q) lam t^b]^{(2-q)/(1-q)}; for 0 < q < 1 the
support is [0, (lam (1-q))^{-1/b}] and comparisons run on (0, D) with D the
smallest support end, as in the paper. Independent components throughout.
Theorems are tested with the closed-form interval checker on random admissible
instances (b = 1); printed examples are checked at the printed parameters,
both directions, so "not comparable" claims need both directions to fail.
"""
import json
import random

import sympy as sp

import closedform as cf

random.seed(31337)
R, x = sp.Rational, cf.x


def S(q, lam, b):
    q, lam, b = R(q), R(lam), R(b)
    return (1 - (1 - q) * lam * x ** b) ** ((2 - q) / (1 - q))


def support_end(q, lams, b):
    q, b = R(q), R(b)
    if q > 1:
        return sp.oo
    return min((R(l) * (1 - q)) ** (-1 / b) for l in lams)


def system(q_list, lam_list, b_list, kind, hi):
    Ss = [S(q, l, b) for q, l, b in zip(q_list, lam_list, b_list)]
    surv = sp.Mul(*Ss) if kind == "series" else 1 - sp.Mul(*[1 - s for s in Ss])
    return cf.Closed(surv, 0, hi)


def rational_hi(hi):
    """Closed-form grid needs a rational end; shrink an irrational end slightly."""
    if hi == sp.oo:
        return hi
    return sp.Rational(sp.floor(hi * 10 ** 6), 10 ** 6)


def both(order, X, Y):
    h1, w1, u1 = cf.check(order, X, Y)
    h2, w2, u2 = cf.check(order, Y, X)
    return {"X_le_Y": h1, "Y_le_X": h2, "w": None if h1 else str(w1), "w_rev": None if h2 else str(w2), "undecided": u1 + u2}


def weak_sub(a, b):
    A, B = sorted(a), sorted(b)
    return all(sum(A[j:]) <= sum(B[j:]) for j in range(len(A)))


def weak_super(a, b):
    A, B = sorted(a), sorted(b)
    return all(sum(A[:j]) >= sum(B[:j]) for j in range(1, len(A) + 1))


def lam_vec(n=3):
    return [R(random.randint(1, 12), 4) for _ in range(n)]


def theorem(name, order, q, rule, kind, direction, trials=20):
    tested, refuted = 0, None
    for _ in range(trials * 60):
        if tested >= trials:
            break
        lam, lam_s = lam_vec(), lam_vec()
        if not rule(lam, lam_s):
            continue
        hi = rational_hi(support_end(q, lam + lam_s, 1))
        U = system([q] * 3, lam, [1] * 3, kind, hi)
        V = system([q] * 3, lam_s, [1] * 3, kind, hi)
        X, Y = (V, U) if direction == "V<=U" else (U, V)
        holds, witness, _ = cf.check(order, X, Y)
        tested += 1
        if not holds and refuted is None:
            refuted = {"q": str(q), "lam": [str(v) for v in lam], "lam_star": [str(v) for v in lam_s], "witness": str(witness)}
    return {"tested": tested, "refuted_example": refuted}


def example(q_pair, lam_pair, b_pair, kind, order):
    """q_pair etc.: ((U values), (V values)); returns both-direction verdicts on (0, D)."""
    (qU, qV), (lU, lV), (bU, bV) = q_pair, lam_pair, b_pair
    ends = [support_end(q, [l], b) for q, l, b in zip(list(qU) + list(qV), list(lU) + list(lV), list(bU) + list(bV))]
    hi = rational_hi(min(ends))
    U = system(qU, lU, bU, kind, hi)
    V = system(qV, lV, bV, kind, hi)
    out = both(order, U, V)
    out["interval_end"] = str(hi)
    return out


if __name__ == "__main__":
    half, three_halves = R(1, 2), R(3, 2)
    res = {
        "Theorem 3.1(1): series hr, lam weakly submajorized by lam*, q=1/2 (V <=hr U)": theorem("3.1(1)", "hr", half, weak_sub, "series", "V<=U"),
        "Theorem 3.1(2): series hr, lam weakly supermajorized by lam*, q=3/2 (U <=hr V)": theorem("3.1(2)", "hr", three_halves, weak_super, "series", "U<=V"),
        "Theorem 3.10(1): parallel st, lam weakly supermajorized by lam*, q=1/2 (U <=st V)": theorem("3.10(1)", "st", half, weak_super, "parallel", "U<=V"),
        "Theorem 3.10(2): parallel st, lam weakly supermajorized by lam*, q=3/2 (U <=st V)": theorem("3.10(2)", "st", three_halves, weak_super, "parallel", "U<=V"),
    }
    ex = {}
    same2 = lambda v: (v, v)
    # U has the unstarred parameters, V the starred ones.
    ex["3.2 q<1 (printed V <=hr U)"] = example(same2(("0.5", "0.5")), (("0.5", "1.5"), ("0.3", "1.8")), same2(("0.5", "0.5")), "series", "hr")
    ex["3.2 q>1 (printed U <=hr V)"] = example(same2(("1.5", "1.5")), (("0.6", "1.5"), ("0.3", "1.7")), same2(("0.5", "0.5")), "series", "hr")
    ex["3.3 q<1 (printed: no lr order)"] = example(same2(("0.5", "0.5")), (("0.5", "1.5"), ("0.3", "1.7")), same2(("0.5", "0.5")), "series", "lr")
    ex["3.3 q>1 (printed: no lr order)"] = example(same2(("1.5", "1.5")), (("0.5", "1.5"), ("0.3", "1.7")), same2(("2", "2")), "series", "lr")
    ex["3.5 q<1 (printed V <=hr U)"] = example((("0.3", "0.5"), ("0.1", "0.6")), same2(("0.5", "0.5")), same2(("2", "2")), "series", "hr")
    ex["3.5 q>1 (printed V <=hr U)"] = example((("1.3", "1.5"), ("1.1", "1.6")), same2(("0.5", "0.5")), same2(("2", "2")), "series", "hr")
    ex["3.6 q<1 (printed: no lr order)"] = example((("0.2", "0.7"), ("0.1", "0.8")), same2(("0.5", "0.5")), same2(("2", "2")), "series", "lr")
    ex["3.6 q>1 (printed: no lr order)"] = example((("1.2", "1.7"), ("1.1", "1.8")), same2(("0.5", "0.5")), same2(("2", "2")), "series", "lr")
    ex["3.8 q<1 (printed V <=st U)"] = example(same2(("0.5", "0.5")), same2(("1", "1")), (("0.5", "1.5"), ("0.3", "1.7")), "series", "st")
    ex["3.8 q>1 (printed V <=st U)"] = example(same2(("1.5", "1.5")), same2(("0.5", "0.5")), (("0.5", "1.5"), ("0.3", "1.7")), "series", "st")
    ex["3.9 q<1 (printed: no hr order)"] = example(same2(("0.3", "0.3")), same2(("0.5", "0.5")), (("0.5", "0.5"), ("0.3", "0.7")), "series", "hr")
    ex["3.9 q>1 (printed: no hr order)"] = example(same2(("1.3", "1.3")), same2(("0.5", "0.5")), (("0.5", "0.5"), ("0.3", "0.7")), "series", "hr")
    ex["3.11 q<1 (printed U <=st V)"] = example(same2(("0.5", "0.5")), (("0.5", "1.5"), ("0.3", "1.6")), same2(("0.5", "0.5")), "parallel", "st")
    ex["3.11 q>1 (printed U <=st V)"] = example(same2(("1.5", "1.5")), (("0.5", "1.5"), ("0.3", "1.6")), same2(("0.5", "0.5")), "parallel", "st")
    print(json.dumps({"theorems": res, "examples": ex}, indent=1))
