"""Evaluation of canonical claims for doi:10.1017/apr.2020.6
(s-iterated ageing classes).

All s-IFR/s-IFRA/DMRL/2-IFRA class-membership claims -> unsupported order.
Proposition 7.1 (st claim): s-iterated tails Tbar_{X,s} >= Tbar_{Y,s}
for X = max{Exp(1),Exp(1)} vs Y = max{Exp(1),Exp(1/lam)}, lam > 1,
tested for s = 1..4 (bounded; the quantifier on s is 'for all s >= 1').
Iterated tails of exponential mixtures stay exponential mixtures.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def iterated_tail(coeff_rates, s):
    """coeff_rates: list of (c_i, a_i) with tail = sum c_i e^{-a_i x};
    s-iteration of the normalized tail."""
    cc = [(c, a) for c, a in coeff_rates]
    for _ in range(s):
        Z = sum(c / a for c, a in cc)
        cc = [(c / (a * Z), a) for c, a in cc]
    return sum(c * sp.exp(-a * x) for c, a in cc)


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "doi_10.1017_apr.2020.6.json")))
    results = []
    for rec in records:
        label = rec["claim"]
        order = rec["conclusion"]["order"]
        out = {"claim": label, "order": order, "status": None,
               "instances": 0, "witness": None, "undecided_points": 0}
        if order != "st":
            out["status"] = "unsupported order"
            results.append(out)
            continue
        # Proposition 7.1: X = max of two Exp(1): S = 2e^{-x} - e^{-2x};
        # Y = max{Exp(1), Exp(1/l)}: S = e^{-x} + e^{-l x} - e^{-(l+1)x}
        for lam in (R(2), R(3), R(3, 2)):
            for s in (1, 2, 3, 4):
                TX = iterated_tail([(R(2), R(1)), (-R(1), R(2))], s - 1)
                TY = iterated_tail([(R(1), R(1)), (R(1), lam),
                                    (-R(1), lam + 1)], s - 1)
                # claim Tbar_{X,s} >= Tbar_{Y,s}: check TY <=st TX
                h, w, u = cf.check("st", Closed(TY), Closed(TX))
                out["instances"] += 1
                out["undecided_points"] += u
                if not h and out["witness"] is None:
                    out["witness"] = str(w)
        out["status"] = "holds" if out["witness"] is None else "refuted"
        out["note"] = ("tested s in {1,2,3,4} -- bounded instances of the "
                       "'for all s >= 1' claim")
        results.append(out)
    dest = os.path.join(HERE, "eval_doi_10.1017_apr.2020.6.result.json")
    json.dump(results, open(dest, "w"), indent=1, default=str)
    print(json.dumps(results, indent=1, default=str))


if __name__ == "__main__":
    main()
