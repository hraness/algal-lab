"""Evaluation of canonical claims for doi:10.3390/math9233069 (MEG).

Modified exponentiated (of exponential) MEG(eta, beta):
  F(x) = ((1 + G(x))^beta - 1)/(2^beta - 1),  G(x) = 1 - e^{-eta x}
  S(x) = (2^beta - (2 - e^{-eta x})^beta)/(2^beta - 1).

Corollary 1: beta2 > beta1 => X <=hr Y, X <=st Y.
Corollary 3: X_{r:n} <=st Y_{r:n} for every r (iid samples).
Proposition 3: beta2 > beta1 => X <=lr Y.
Corollary 2 / Proposition 4: Poisson-mixture of MEG — discrete mixture
  distributions, no continuous survival encoding -> out of harness scope.
"""
import json
import os

import sympy as sp

import closedform as cf
import syscomp
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_meg(eta, beta):
    e, b = R(eta), R(beta)
    return (2 ** b - (2 - sp.exp(-e * x)) ** b) / (2 ** b - 1)


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


CASES = [  # (eta, b1, b2), b1 < b2
    (R(1), R(1), R(2)),
    (R(2), R(1, 2), R(1)),
    (R(1, 2), R(2), R(3)),
    (R(3), R(1), R(3, 2)),
    (R(1), R(3, 2), R(4)),
]


def run_simple(order):
    n, wit, und = 0, None, 0
    for e, b1, b2 in CASES:
        X = Closed(S_meg(e, b1))
        Y = Closed(S_meg(e, b2))
        h, w, u = cf.check(order, X, Y)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def corollary_3():
    """X_{r:n} <=st Y_{r:n} for every r; test r=1..n for n=2,3 and a few (r,n)."""
    n, wit, und = 0, None, 0
    for e, b1, b2 in CASES[:3]:
        SX, SY = S_meg(e, b1), S_meg(e, b2)
        for (r_, n_) in [(1, 2), (2, 2), (1, 3), (2, 3), (3, 3)]:
            Xo = Closed(syscomp.order_stat([SX] * n_, r_, n_))
            Yo = Closed(syscomp.order_stat([SY] * n_, r_, n_))
            h, w, u = cf.check("st", Xo, Yo)
            n += 1
            und += u
            if not h and wit is None:
                wit = w
    return n, wit, und


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.3390_math9233069.json")))
    results = []
    for recd in canon:
        order = recd["conclusion"]["order"]
        label = recd["claim"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        if label.startswith("Corollary 1"):
            n_, w, u = run_simple(order)
        elif label == "Corollary 3":
            n_, w, u = corollary_3()
        elif label == "Proposition 3":
            n_, w, u = run_simple("lr")
        elif label.startswith("Corollary 2") or label == "Proposition 4":
            results.append(rec(recd, "out of harness scope"))
            continue
        else:
            results.append(rec(recd, "out of harness scope"))
            continue
        results.append(rec(recd, "holds" if w is None else "refuted",
                           instances=n_, witness=w, undecided=u))
    out = os.path.join(HERE, "eval_doi_10.3390_math9233069.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
