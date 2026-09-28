"""Evaluation of canonical claims for doi:10.2991/jsta.d.210607.001 (XLindley).

XLindley(theta): f(x) = th^2 (2 + th + x) e^{-th x}/(1+th)^2.
Integrating: S(x) = e^{-th x} [1 + th x/(1+th)^2].

Theorem 1: th1 >= th2 => X1 <=lr X2, X1 <=hr X2, X1 <=st X2.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_xl(th):
    th = R(th)
    return sp.exp(-th * x) * (1 + th * x / (1 + th) ** 2)


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


def theorem_1(order):
    n, wit, und = 0, None, 0
    for t1, t2 in [(R(2), R(1)), (R(3, 2), R(1, 2)), (R(1), R(1, 4)),
                   (R(5), R(2)), (R(3, 4), R(1, 3))]:
        assert t1 >= t2
        X1 = Closed(S_xl(t1))
        X2 = Closed(S_xl(t2))
        h, w, u = cf.check(order, X1, X2)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.2991_jsta.d.210607.001.json")))
    results = []
    for recd in canon:
        order = recd["conclusion"]["order"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        if recd["claim"].startswith("Theorem 1"):
            n_, w, u = theorem_1(order)
        else:
            results.append(rec(recd, "out of harness scope"))
            continue
        results.append(rec(recd, "holds" if w is None else "refuted",
                           instances=n_, witness=w, undecided=u))
    out = os.path.join(HERE, "eval_doi_10.2991_jsta.d.210607.001.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
