"""Evaluation of canonical claims for doi:10.1007/s41060-022-00369-2 (PEL).

Family: Power exponentiated Lindley PEL(v, q, alpha), x > 0:
  G(x) = 1 - exp(-q x)(1+q+qx)/(1+q)           (Lindley baseline cdf)
  F(x) = (v^{G(x)^alpha} - 1)/(v - 1)
  S(x) = (v - v^{G(x)^alpha})/(v - 1),  v > 0, v != 1, q, alpha > 0.

Theorem 3.10.1: v1 <= v2, q1 <= q2, alpha1 <= alpha2 => Y >=lr X (and
hr, mrl, st via implication chain). We check X <=order Y.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_pel(v, q, alpha):
    v, q, alpha = R(v), R(q), R(alpha)
    G = 1 - sp.exp(-q * x) * (1 + q + q * x) / (1 + q)
    return (v - v ** (G ** alpha)) / (v - 1)


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "doi_10.1007_s41060-022-00369-2.json")))
    cases = [
        # (v1,q1,a1) vs (v2,q2,a2): all componentwise <=
        (R(2), R(1), R(1), R(3), R(2), R(2)),
        (R(2), R(1, 2), R(1, 2), R(3), R(1), R(1)),
        (R(1, 2), R(1), R(1), R(2, 3), R(2), R(2)),   # both v<1
        (R(1, 2), R(1), R(1), R(3), R(3, 2), R(2)),   # v1<1<v2
        (R(3), R(3), R(3), R(4), R(4), R(4)),          # equal-free strict
    ]
    results = []
    for rec in records:
        order = rec["conclusion"]["order"]
        out = {"claim": rec["claim"], "order": order, "status": None,
               "instances": 0, "witness": None, "undecided_points": 0}
        if order not in ("st", "hr", "rh", "lr"):
            out["status"] = "unsupported order"
            results.append(out)
            continue
        n, wit, und = 0, None, 0
        for v1, q1, a1, v2, q2, a2 in cases:
            assert v1 <= v2 and q1 <= q2 and a1 <= a2
            X = Closed(S_pel(v1, q1, a1))
            Y = Closed(S_pel(v2, q2, a2))
            h, w, u = cf.check(order, X, Y)
            n += 1
            und += u
            if not h and wit is None:
                wit = w
        out.update(instances=n, undecided_points=und,
                   witness=None if wit is None else str(wit),
                   status="holds" if wit is None else "refuted")
        results.append(out)
    dest = os.path.join(HERE, "eval_doi_10.1007_s41060-022-00369-2.result.json")
    json.dump(results, open(dest, "w"), indent=1)
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
