"""Evaluation of canonical claims for doi:10.46939/j.sci.arts-26.1-a05 (UTPA).

Unit two-parameter Aradhana distribution on (0,1):
  f(x) = th^3 (a - ln x)^2 x^{th-1} / (th^2 a^2 + 2 th a + 2)
Survival (X = e^{-Y}, Y two-parameter Aradhana):
  S(x) = x^th [th^2 (a - ln x)^2 + 2 th (a - ln x) + 2] / (th^2 a^2 + 2 th a + 2)

Theorem 1:   th1 < th2 => X <=lr Y.
Corollary 1: same hypotheses => X <=hr Y, X <=mrl Y, X <=st Y.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_utpa(a, th):
    """P(X > x) for X = e^{-Y}:  S_X(x) = 1 - F_Y(-ln x)."""
    a, th = R(a), R(th)
    D = th ** 2 * a ** 2 + 2 * th * a + 2
    return 1 - x ** th * (th ** 2 * (a - sp.log(x)) ** 2 + 2 * th * (a - sp.log(x)) + 2) / D


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


CASES = [  # (alpha, th1, th2), th1 < th2
    (R(1), R(1), R(2)),
    (R(2), R(1, 2), R(1)),
    (R(1, 2), R(1), R(3)),
    (R(3), R(1, 3), R(1, 2)),
    (R(1), R(2), R(5)),
]


def run(order):
    n, wit, und = 0, None, 0
    for a, t1, t2 in CASES:
        X = Closed(S_utpa(a, t1), 0, 1)
        Y = Closed(S_utpa(a, t2), 0, 1)
        h, w, u = cf.check(order, X, Y)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.46939_j.sci.arts-26.1-a05.json")))
    results = []
    for recd in canon:
        order = recd["conclusion"]["order"]
        label = recd["claim"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        if label == "Theorem 1" or label.startswith("Corollary 1"):
            n_, w, u = run(order)
        else:
            results.append(rec(recd, "out of harness scope"))
            continue
        results.append(rec(recd, "holds" if w is None else "refuted",
                           instances=n_, witness=w, undecided=u))
    out = os.path.join(HERE, "eval_doi_10.46939_j.sci.arts-26.1-a05.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
