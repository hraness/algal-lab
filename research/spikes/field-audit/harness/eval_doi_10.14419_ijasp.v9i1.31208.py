"""Evaluation of canonical claims for doi:10.14419/ijasp.v9i1.31208 (APTQLD).

Quasi-Lindley baseline (Eq. 2): G(x) = 1 - (beta+1+th x) e^{-th x}/(beta+1).
Alpha-power transform (Eq. 3): F(x) = (a^{G(x)} - 1)/(a - 1), a>0, a!=1.
  S(x) = (a - a^{G(x)})/(a - 1).

Theorem 2: a1 < a2, common beta, theta => X1 <=lr X2 (=> hr, mrl, st).
Definitions records describe the order definitions/implication chain only.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_aptqld(a, b, th):
    a, b, th = R(a), R(b), R(th)
    G = 1 - (b + 1 + th * x) * sp.exp(-th * x) / (b + 1)
    return (a - a ** G) / (a - 1)


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


CASES = [  # (a1, a2, beta, theta), a1<a2, a!=1
    (R(2), R(3), R(1), R(1)),
    (R(1, 2), R(2), R(1, 2), R(2)),
    (R(3, 2), R(5), R(0), R(1, 2)),
    (R(2), R(4), R(3), R(1, 4)),
    (R(1, 4), R(1, 2), R(2), R(3)),
]


def run(order):
    n, wit, und = 0, None, 0
    for a1, a2, b, th in CASES:
        X1 = Closed(S_aptqld(a1, b, th))
        X2 = Closed(S_aptqld(a2, b, th))
        h, w, u = cf.check(order, X1, X2)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.14419_ijasp.v9i1.31208.json")))
    results = []
    for recd in canon:
        order = recd["conclusion"]["order"]
        label = recd["claim"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        if "definitions" in label:
            results.append(rec(recd, "out of harness scope"))
            continue
        n_, w, u = run(order)
        results.append(rec(recd, "holds" if w is None else "refuted",
                           instances=n_, witness=w, undecided=u))
    out = os.path.join(HERE, "eval_doi_10.14419_ijasp.v9i1.31208.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
