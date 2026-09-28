"""Evaluation of canonical claims for doi:10.5539/ijsp.v10n3p8 (LFP).

Lehmann type II Frechet-Poisson LFP(alpha, nu, gamma, omega):
  Frechet baseline G(x) = exp(-gamma x^{-omega});
  FP cdf  H(x) = (1 - exp(-nu G(x)))/(1 - exp(-nu));
  LFP: F = 1 - (1 - H)^alpha  =>
  S(x; a, v, g, w) = ((exp(-v G(x)) - exp(-v))/(1 - exp(-v)))^a.

Unnumbered Section-3.7 theorem: alpha1 < alpha2 and nu1 < nu2 =>
X <=lr Z (=> hr, rh, st per the printed chain). The 'definitions'
record is a definition/implication-chain statement, not a model claim.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_lfp(a, v, g, w):
    G = sp.exp(-R(g) * x ** (-R(w)))
    H = (1 - sp.exp(-R(v) * G)) / (1 - sp.exp(-R(v)))
    return (1 - H) ** R(a)


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


CASES = [  # (a1,a2,v1,v2,g,w), a1<a2, v1<v2
    (R(1), R(2), R(1), R(2), R(1), R(1)),
    (R(1, 2), R(1), R(1, 2), R(3, 2), R(2), R(3)),
    (R(2), R(5), R(1, 3), R(1), R(1, 2), R(1, 2)),
    (R(1), R(3), R(2), R(4), R(3), R(2)),
]


def run(order):
    n, wit, und = 0, None, 0
    for a1, a2, v1, v2, g, w in CASES:
        X = Closed(S_lfp(a1, v1, g, w))
        Z = Closed(S_lfp(a2, v2, g, w))
        h, wt, u = cf.check(order, X, Z)
        n += 1
        und += u
        if not h and wit is None:
            wit = wt
    return n, wit, und


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.5539_ijsp.v10n3p8.json")))
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
    out = os.path.join(HERE, "eval_doi_10.5539_ijsp.v10n3p8.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
