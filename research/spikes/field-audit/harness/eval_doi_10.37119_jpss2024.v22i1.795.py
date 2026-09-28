"""Evaluation of canonical claims for doi:10.37119/jpss2024.v22i1.795 (MGGD).

Mixture of Gompertz and gamma (MGGD), paper Eq. (2):
  F(x;eta,beta) = [1 - exp(-(eta/beta)(e^{beta x} - 1))]/(1+beta)
                  + beta [1 - (1 + eta x + eta^2 x^2/2) e^{-eta x}]/(1+beta)
i.e. Gompertz component weight 1/(1+beta), Gamma(3,eta) weight beta/(1+beta):
  S(x;eta,beta) = [exp(-(eta/beta)(e^{beta x}-1))
                   + beta (1 + eta x + eta^2 x^2/2) e^{-eta x}] / (1+beta)

Claim (Section 10, unnumbered): eta < psi and beta < delta => X <=lr Y.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_mggd(eta, beta):
    e, b = R(eta), R(beta)
    gomp = sp.exp(-(e / b) * (sp.exp(b * x) - 1))
    gam = b * (1 + e * x + (e * x) ** 2 / 2) * sp.exp(-e * x)
    return (gomp + gam) / (1 + b)


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


def theorem_lr():
    n, wit, und = 0, None, 0
    cases = [  # (eta, beta, psi, delta) with eta<psi, beta<delta
        (R(1, 2), R(1, 2), R(1), R(1)),
        (R(1), R(1), R(2), R(3)),
        (R(1, 4), R(1, 3), R(1, 2), R(2)),
        (R(2), R(1, 2), R(3), R(1)),
        (R(1, 3), R(2), R(1, 2), R(3)),
    ]
    for e1, b1, e2, b2 in cases:
        X = Closed(S_mggd(e1, b1))
        Y = Closed(S_mggd(e2, b2))
        h, w, u = cf.check("lr", X, Y)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.37119_jpss2024.v22i1.795.json")))
    results = []
    for recd in canon:
        order = recd["conclusion"]["order"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        if "Section 10" in recd["claim"]:
            n_, w, u = theorem_lr()
            results.append(rec(recd, "holds" if w is None else "refuted",
                               instances=n_, witness=w, undecided=u))
        else:
            results.append(rec(recd, "out of harness scope"))
    out = os.path.join(HERE, "eval_doi_10.37119_jpss2024.v22i1.795.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
