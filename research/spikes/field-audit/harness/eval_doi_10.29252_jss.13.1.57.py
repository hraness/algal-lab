"""Evaluation of canonical claims for doi:10.29252/jss.13.1.57
(Persian paper; Bernoulli-thinned Weibull minima).

Independent case (Thm 3 / Cor 1):  S_{min}(t) = (prod p_i) exp(-t^a sum
lambda_i^a), so Y_{1:n} >=st Y*_{1:n} reduces to a two-term comparison.
Copula-based claims (Archimedean / Gumbel-Hougaard / Clayton) -> out of
harness scope.  disp / cx / star / su orders -> unsupported order.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_min(ps, ls, a):
    prod_p = R(1)
    for p in ps:
        prod_p *= p
    return prod_p * sp.exp(-x ** a * sum(l ** a for l in ls))


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "doi_10.29252_jss.13.1.57.json")))
    results = []
    for rec in records:
        label = rec["claim"]
        order = rec["conclusion"]["order"]
        out = {"claim": label, "order": order, "status": None,
               "instances": 0, "witness": None, "undecided_points": 0}
        if order not in ("st", "hr", "rh", "lr"):
            out["status"] = "unsupported order"
            results.append(out)
            continue
        if any(k in label for k in
               ("Theorem 9", "Theorem 10", "Theorem 6", "Theorem 7")):
            out["status"] = "out of harness scope"
            out["note"] = "claims coupled by a survival copula"
            results.append(out)
            continue
        # Corollary 1 and Theorem 3: independent thinned Weibull minima
        n = wit = und = 0
        wit = None
        for ps, ls, a, qs, ms in [
                # prod p >= prod p*, sum lam^a <= sum lam*^a
                ([R(1, 2), R(1, 2)], [R(1), R(2)], R(2),
                 [R(1, 3), R(1, 2)], [R(2), R(3)]),
                ([R(3, 4), R(3, 4)], [R(1), R(1)], R(3),
                 [R(1, 2), R(1, 2)], [R(1), R(2)]),
                ([R(9, 10), R(9, 10), R(9, 10)], [R(1), R(2), R(3)],
                 R(2), [R(4, 5)] * 3, [R(1), R(2), R(4)]),
                ([R(1, 2), R(1, 2)], [R(1), R(1)], R(1),
                 [R(1, 4), R(1, 4)], [R(1), R(2)])]:
            prod_p = 1
            for p in ps:
                prod_p *= p
            prod_q = 1
            for q in qs:
                prod_q *= q
            assert prod_p >= prod_q
            assert sum(l ** a for l in ls) <= sum(m ** a for m in ms)
            SX = Closed(S_min(ps, ls, a))   # Y_{1:n} (unstarred)
            SY = Closed(S_min(qs, ms, a))   # Y*_{1:n}
            # claim: Y1:n >=st Y*1:n  ->  check("st", SY, SX)
            h, w, u = cf.check("st", SY, SX)
            n += 1
            und += u
            if not h and wit is None:
                wit = w
        out["status"] = "holds" if wit is None else "refuted"
        out.update(instances=n, undecided_points=und)
        if wit is not None:
            out["witness"] = str(wit)
        results.append(out)
    dest = os.path.join(HERE, "eval_doi_10.29252_jss.13.1.57.result.json")
    json.dump(results, open(dest, "w"), indent=1, default=str)
    print(json.dumps(results, indent=1, default=str))


if __name__ == "__main__":
    main()
