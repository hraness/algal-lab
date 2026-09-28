"""Evaluation of canonical claims for doi:10.2991/jsta.2017.16.4.2 (MOKw-G).

Family: Marshall-Olkin-Kumaraswamy-G, survival
  S(t) = alpha * [1 - G(t)^a]^b / (1 - abar * [1 - G(t)^a]^b),  abar = 1 - alpha
with baseline cdf G (paper eq. (7)/(8): F = 1 - u^b/(1-abar u^b),
S = alpha u^b/(1 - abar u^b), u = 1 - G^a).

Theorem 1: X ~ MOKwG(alpha1), Y ~ MOKwG(alpha2), alpha1 < alpha2, common
(a, b, G) => X <=lr, <=hr, <=rh(=rhr), <=st Y. Baselines instantiated with the
paper's special cases: MOKw-E (G = 1 - exp(-lam t)) and MOKw-W
(G = 1 - exp(-lam t^beta)).
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_mokw(alpha, a, b, G):
    u = 1 - G ** R(a)
    return R(alpha) * u ** R(b) / (1 - (1 - R(alpha)) * u ** R(b))


def baseline_exp(lam):
    return 1 - sp.exp(-R(lam) * x)


def baseline_weibull(lam, beta):
    return 1 - sp.exp(-R(lam) * x ** R(beta))


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "doi_10.2991_jsta.2017.16.4.2.json")))
    # instances: (alpha1, alpha2, a, b, baseline-cdf-expr)
    cases = []
    for G in [baseline_exp(1), baseline_exp(2), baseline_weibull(1, 2),
              baseline_weibull(1, R(1, 2))]:
        for a, b in [(R(1), R(1)), (R(2), R(3)), (R(1, 2), R(2))]:
            for a1, a2 in [(R(1, 4), R(1, 2)), (R(1, 2), R(9, 10)),
                           (R(1, 2), R(2))]:
                cases.append((a1, a2, a, b, G))
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
        for a1, a2, a, b, G in cases:
            assert a1 < a2
            X = Closed(S_mokw(a1, a, b, G))
            Y = Closed(S_mokw(a2, a, b, G))
            h, w, u = cf.check(order, X, Y)   # X <=order Y ?
            n += 1
            und += u
            if not h and wit is None:
                wit = w
        out.update(instances=n, undecided_points=und,
                   witness=None if wit is None else str(wit),
                   status="holds" if wit is None else "refuted")
        results.append(out)
    dest = os.path.join(HERE, "eval_doi_10.2991_jsta.2017.16.4.2.result.json")
    json.dump(results, open(dest, "w"), indent=1)
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
