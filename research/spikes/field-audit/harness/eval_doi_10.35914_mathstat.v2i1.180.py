"""Evaluation of canonical claims for doi:10.35914/mathstat.v2i1.180 (MGSD paper).

Family: MGS(lambda, theta), mixture of Gamma(3, theta) and Shanker(theta):
  f(x; lam, th) = th^2/(lam+1) * (lam*th*x^2/2 + (th+x)/(th^2+1)) * exp(-th x)
  S(x; lam, th) = exp(-th x)/(lam+1) * [lam*(1 + th x + th^2 x^2/2)
                                        + (th^2 + th x + 1)/(th^2 + 1)]

Claim: X ~ MGS(lam, th) <=lr Y ~ MGS(beta, alpha). Printed hypothesis is the
crossed pairing lam < alpha, th < beta; the printed conclusion condition is
lam < beta, th < alpha. We test instances satisfying BOTH pairings as well as
instances satisfying only the stated one.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_mgs(lam, th):
    lam, th = R(lam), R(th)
    return (sp.exp(-th * x) / (lam + 1)
            * (lam * (1 + th * x + th ** 2 * x ** 2 / 2)
               + (th ** 2 + th * x + 1) / (th ** 2 + 1)))


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "doi_10.35914_mathstat.v2i1.180.json")))
    results = []
    for rec in records:
        order = rec["conclusion"]["order"]
        out = {"claim": rec["claim"], "order": order, "status": None,
               "instances": 0, "witness": None, "undecided_points": 0}
        if order != "lr":
            out["status"] = "unsupported order"
            results.append(out)
            continue
        # Instances: (lam, th) for X, (beta, alpha) for Y.
        # inst1 satisfies both pairings (lam<alpha & th<beta AND lam<beta & th<alpha)
        # inst2 satisfies stated pairing only (lam<alpha, th<beta) but lam>beta, th>alpha
        # inst3 satisfies stated pairing with th>alpha crossed the other way
        instances = [
            (R(1), R(2), R(3), R(4)),      # lam=1,th=2 ; beta=3,alpha=4: both pairings
            (R(1), R(2), R(4), R(3)),      # lam=1<alpha=3, th=2<beta=4; th=2<alpha=3, lam<beta
            (R(1, 2), R(3), R(4), R(2)),   # lam=.5<alpha=2, th=3<beta=4; but th>alpha
            (R(2), R(5), R(3), R(6)),      # lam=2<alpha=6, th=5>beta=3? no: th<beta fails
        ]
        n, wit, und = 0, None, 0
        for lam, th, beta, alpha in instances[:3]:
            if not (lam < alpha and th < beta):
                continue
            X = Closed(S_mgs(lam, th))
            Y = Closed(S_mgs(beta, alpha))
            h, w, u = cf.check("lr", X, Y)   # decides X <=lr Y
            n += 1
            und += u
            if not h and wit is None:
                wit = w
        out["instances"] = n
        out["undecided_points"] = und
        out["witness"] = None if wit is None else str(wit)
        out["status"] = "holds" if wit is None else "refuted"
        results.append(out)
    dest = os.path.join(HERE, "eval_doi_10.35914_mathstat.v2i1.180.result.json")
    json.dump(results, open(dest, "w"), indent=1)
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
