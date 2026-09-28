"""Evaluation of canonical claims for doi:10.3390/math14173120 (Lomax-Bilal).

LBD(lambda, alpha, theta), paper Eq. (5):
  u = lam/(x+lam), delta = alpha/theta,
  G(x) = 1 - (3 - 2 u^delta) u^{2 delta}  =>  S(x) = u^{2delta}(3 - 2u^delta).

Theorem 6: delta1 < delta2 (common lam) => X2 <=lr X1 (denser delta smaller in lr).
Theorem 7: lam1 < lam2 (common delta)  => X1 <=lr X2.
Both also conclude hr and st; tested as part of the same record instances.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_lbd(lam, alpha, theta):
    u = R(lam) / (x + R(lam))
    d = R(alpha) / R(theta)
    return u ** (2 * d) * (3 - 2 * u ** d)


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


def theorem_6():
    """delta1 < delta2 => X2 <=lr X1, X2 <=hr X1, X2 <=st X1."""
    n, wit, und = 0, None, 0
    cases = [  # (lam, d1, d2) with d1<d2, realized as (alpha,theta) pairs
        (R(1), (R(1), R(2)), (R(1), R(1))),          # d=1/2 vs 1
        (R(2), (R(1), R(3)), (R(2), R(3))),          # 1/3 vs 2/3
        (R(1, 2), (R(2), R(1)), (R(5), R(2))),       # 2 vs 5/2
        (R(3), (R(1), R(4)), (R(1), R(2))),          # 1/4 vs 1/2
        (R(1), (R(3), R(2)), (R(4), R(1))),          # 3/2 vs 4
    ]
    for lam, (a1, t1), (a2, t2) in cases:
        assert a1 / t1 < a2 / t2
        X2 = Closed(S_lbd(lam, a2, t2))
        X1 = Closed(S_lbd(lam, a1, t1))
        for order in ("lr", "hr", "st"):
            h, w, u = cf.check(order, X2, X1)
            n += 1
            und += u
            if not h and wit is None:
                wit = w
    return n, wit, und


def theorem_7():
    """lam1 < lam2 => X1 <=lr X2, X1 <=hr X2, X1 <=st X2."""
    n, wit, und = 0, None, 0
    cases = [
        (R(1), R(2), R(1), R(1)),      # lam1,lam2, alpha, theta (delta=1)
        (R(1, 2), R(1), R(1), R(2)),   # delta=1/2
        (R(1), R(3, 2), R(5), R(2)),   # delta=5/2
        (R(2), R(4), R(1), R(3)),      # delta=1/3
        (R(1, 4), R(3), R(3), R(1)),   # delta=3
    ]
    for l1, l2, a, th in cases:
        assert l1 < l2
        X1 = Closed(S_lbd(l1, a, th))
        X2 = Closed(S_lbd(l2, a, th))
        for order in ("lr", "hr", "st"):
            h, w, u = cf.check(order, X1, X2)
            n += 1
            und += u
            if not h and wit is None:
                wit = w
    return n, wit, und


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.3390_math14173120.json")))
    results = []
    for recd in canon:
        order = recd["conclusion"]["order"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        if recd["claim"] == "Theorem 6":
            n_, w, u = theorem_6()
        elif recd["claim"] == "Theorem 7":
            n_, w, u = theorem_7()
        else:
            results.append(rec(recd, "out of harness scope"))
            continue
        results.append(rec(recd, "holds" if w is None else "refuted",
                           instances=n_, witness=w, undecided=u))
    out = os.path.join(HERE, "eval_doi_10.3390_math14173120.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
