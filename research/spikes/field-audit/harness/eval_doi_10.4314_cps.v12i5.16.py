"""Evaluation of canonical claims for doi:10.4314/cps.v12i5.16 (EPAD vs EWD).

EPAD(a,b,th): F1(x) = [1 - (1 + th x^b) exp(-th x^b)]^a   (exponentiated power
             affine / power-Lindley-type cdf)
EWD (a,b,th): G1(x) = [1 - exp(-th x^b)]^a               (exponentiated Weibull)

Prop 2.1: same (a,b,th) => F1 <= G1 pointwise, i.e. EPAD >=st EWD.
Prop 2.2: a1 < a2, common b, th => X1 <=lr X2 (density ratio decreasing).
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_epad(a, b, th):
    return 1 - (1 - (1 + R(th) * x ** R(b)) * sp.exp(-R(th) * x ** R(b))) ** R(a)


def S_ewd(a, b, th):
    return 1 - (1 - sp.exp(-R(th) * x ** R(b))) ** R(a)


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


def prop_2_1():
    """EPAD >=st EWD i.e. EWD <=st EPAD."""
    n, wit, und = 0, None, 0
    for (a, b, th) in [(R(1), R(1), R(1)), (R(2), R(3, 2), R(1, 2)),
                       (R(1, 2), R(2), R(3)), (R(3), R(1, 2), R(2)),
                       (R(5), R(4), R(1, 4))]:
        X = Closed(S_ewd(a, b, th))
        Y = Closed(S_epad(a, b, th))
        h, w, u = cf.check("st", X, Y)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def prop_2_2():
    """a1 < a2, common b, th => EPAD(a1) <=lr EPAD(a2)."""
    n, wit, und = 0, None, 0
    for (a1, a2, b, th) in [(R(1), R(2), R(1), R(1)),
                            (R(1, 2), R(1), R(2), R(3)),
                            (R(1), R(3, 2), R(3, 2), R(1, 2)),
                            (R(2), R(4), R(1, 2), R(2)),
                            (R(1, 3), R(5, 2), R(2), R(1, 4))]:
        X = Closed(S_epad(a1, b, th))
        Y = Closed(S_epad(a2, b, th))
        h, w, u = cf.check("lr", X, Y)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.4314_cps.v12i5.16.json")))
    results = []
    for recd in canon:
        order = recd["conclusion"]["order"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        label = recd["claim"]
        if label.startswith("Proposition 2.1"):
            n_, w, u = prop_2_1()
        elif label == "Proposition 2.2":
            n_, w, u = prop_2_2()
        else:
            results.append(rec(recd, "out of harness scope"))
            continue
        results.append(rec(recd, "holds" if w is None else "refuted",
                           instances=n_, witness=w, undecided=u))
    out = os.path.join(HERE, "eval_doi_10.4314_cps.v12i5.16.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
