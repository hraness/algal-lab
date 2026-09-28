"""Evaluation of canonical claims for doi:10.37119/jpss2023.v21i1.637 (MWU).

Modified weighted uniform MWU(a, lam):
  f(x) = lam(a+1)(1 - lam x)^a,  0 <= x <= 1/lam;
  S(x) = (1 - lam x)^{a+1}.

Theorem 1(i):  a1 < a2, common lam => X <=lr/hr/st Y.
Theorem 1(ii): a1 = a2, lam2 > lam1 => X <=lr/hr/st Y.
  (Supports differ; comparison encoded on the shared interior (0, 1/lam2),
   where any violation already refutes the order.)
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_mwu(a, lam):
    return (1 - R(lam) * x) ** (R(a) + 1)


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


def part_i(order):
    n, wit, und = 0, None, 0
    for (a1, a2, lam) in [(R(0), R(1), R(1)), (R(1, 2), R(2), R(2)),
                          (R(1), R(3), R(1, 2)), (R(2), R(5, 2), R(3)),
                          (R(0), R(1, 3), R(1, 4))]:
        assert a1 < a2
        X = Closed(S_mwu(a1, lam), 0, 1 / lam)
        Y = Closed(S_mwu(a2, lam), 0, 1 / lam)
        h, w, u = cf.check(order, X, Y)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def part_ii(order):
    n, wit, und = 0, None, 0
    for (a, l1, l2) in [(R(1), R(1), R(2)), (R(2), R(1, 2), R(1)),
                        (R(0), R(1), R(3)), (R(1, 2), R(2), R(5, 2)),
                        (R(3), R(1, 3), R(1, 2))]:
        assert l2 > l1
        hi = 1 / l2          # smaller support end; X's own support extends further
        X = Closed(S_mwu(a, l1), 0, hi)
        Y = Closed(S_mwu(a, l2), 0, hi)
        h, w, u = cf.check(order, X, Y)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.37119_jpss2023.v21i1.637.json")))
    results = []
    for recd in canon:
        order = recd["conclusion"]["order"]
        label = recd["claim"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        if "(1)(i)" in label:
            n_, w, u = part_i(order)
        elif "(1)(ii)" in label:
            n_, w, u = part_ii(order)
        else:
            results.append(rec(recd, "out of harness scope"))
            continue
        results.append(rec(recd, "holds" if w is None else "refuted",
                           instances=n_, witness=w, undecided=u))
    out = os.path.join(HERE, "eval_doi_10.37119_jpss2023.v21i1.637.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
