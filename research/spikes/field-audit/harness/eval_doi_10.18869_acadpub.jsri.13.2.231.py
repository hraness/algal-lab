"""Evaluation of canonical claims for doi:10.18869/acadpub.jsri.13.2.231 (TEE).

Family: truncated exponential-exponential TEE(alpha, lam), alpha != 0, lam > 0:
  F(x) = (e^a - e^{a e^{-lam x}})/(e^a - 1)
  S(x) = (e^{a e^{-lam x}} - 1)/(e^a - 1),   x > 0.
e^{rational} enters via sp.E**R(a) so interval evaluation stays exact.

Claims (Section 5, unnumbered):
  alpha parts: a1 < a2, common lam  => Y <=lr/hr/st X.
  lam parts:   lam1 < lam2, common alpha > -1 => Y <=lr/hr/st X.
We check (order, Y, X) for "Y <=order X".
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
E = sp.E
HERE = os.path.dirname(os.path.abspath(__file__))


def S_tee(a, lam):
    a, lam = R(a), R(lam)
    return (E ** (a * sp.exp(-lam * x)) - 1) / (E ** a - 1)


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "doi_10.18869_acadpub.jsri.13.2.231.json")))
    alpha_cases = [   # (alpha1 < alpha2, common lam)
        (R(1, 2), R(1), R(1)),
        (R(1), R(2), R(1, 2)),
        (R(-1), R(1, 2), R(1)),      # alpha1 negative allowed (a != 0)
        (R(-2), R(-1), R(2)),        # both negative
    ]
    lam_cases = [     # (lam1 < lam2, common alpha > -1)
        (R(1), R(2), R(-1, 2)),
        (R(1, 2), R(3, 2), R(1)),
        (R(1), R(3), R(2)),
        (R(2), R(5), R(-9, 10)),
    ]
    results = []
    for rec in records:
        order = rec["conclusion"]["order"]
        label = rec["claim"]
        out = {"claim": label, "order": order, "status": None,
               "instances": 0, "witness": None, "undecided_points": 0}
        if order not in ("st", "hr", "rh", "lr"):
            out["status"] = "unsupported order"
            results.append(out)
            continue
        cases, which = [], ("alpha" if "in α" in label else "lam")
        src = alpha_cases if which == "alpha" else lam_cases
        n, wit, und = 0, None, 0
        for p1, p2, common in src:
            if which == "alpha":
                X = Closed(S_tee(p1, common))
                Y = Closed(S_tee(p2, common))
            else:
                X = Closed(S_tee(common, p1))
                Y = Closed(S_tee(common, p2))
            h, w, u = cf.check(order, Y, X)      # Y <=order X
            n += 1
            und += u
            if not h and wit is None:
                wit = w
        out.update(instances=n, undecided_points=und,
                   witness=None if wit is None else str(wit),
                   status="holds" if wit is None else "refuted")
        results.append(out)
    dest = os.path.join(
        HERE, "eval_doi_10.18869_acadpub.jsri.13.2.231.result.json")
    json.dump(results, open(dest, "w"), indent=1)
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
