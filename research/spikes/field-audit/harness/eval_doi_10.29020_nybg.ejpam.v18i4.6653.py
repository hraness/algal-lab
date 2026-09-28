"""Evaluation of canonical claims for doi:10.29020/nybg.ejpam.v18i4.6653
(Mgamma / M distribution).

Family: M(theta), mixture of Gamma(2,th) and Gamma(3,th):
  f(x) = th^3 x (1 + x/2) exp(-th x) / (1 + th),  x > 0
  S(x) = exp(-th x)/(1+th) * [th(1 + th x) + (1 + th x + th^2 x^2/2)]

Claimed (as printed): th1 <= th2 => X1 <=lr/hr/st/cx X2.
Canonical ambiguity: the proof quantifies the derivative 'for all th1 >= th2'
(the opposite direction).  We test the printed statement hypothesis th1 <= th2.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_mgamma(th):
    th = R(th)
    return (sp.exp(-th * x) / (1 + th)
            * (th * (1 + th * x) + (1 + th * x + th ** 2 * x ** 2 / 2)))


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "doi_10.29020_nybg.ejpam.v18i4.6653.json")))
    pairs = [(R(1), R(2)), (R(1, 2), R(3, 2)), (R(2), R(5)), (R(1), R(10))]
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
        for t1, t2 in pairs:
            assert t1 <= t2
            X = Closed(S_mgamma(t1))
            Y = Closed(S_mgamma(t2))
            h, w, u = cf.check(order, X, Y)
            n += 1
            und += u
            if not h and wit is None:
                wit = w
        out.update(instances=n, undecided_points=und,
                   witness=None if wit is None else str(wit),
                   status="holds" if wit is None else "refuted")
        results.append(out)
    dest = os.path.join(
        HERE, "eval_doi_10.29020_nybg.ejpam.v18i4.6653.result.json")
    json.dump(results, open(dest, "w"), indent=1)
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
