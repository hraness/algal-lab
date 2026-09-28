"""Evaluation of canonical claims for arxiv:1905.00425
(order statistics of independent Gumbel components under majorization of
location vectors).

Gumbel(mu, sigma): F(x) = exp(-e^{-(x-mu)/sigma}) = exp(-e^{(mu-x)/sigma}),
                   S(x) = 1 - exp(-e^{(mu-x)/sigma}),  x in R, sigma > 0.
Since lo is finite in the harness, tests run on [-LO, top] with LO = 80:
for x <= -80 and |mu| <= ~30, e^{(mu-x)/sigma} >= e^{50} so S(x) = 1 - tiny --
all compared survivals are identical up to ~e^{-e^50}; the grid region covers
every numerically relevant point (bounded testing).

Corollaries 3.3/3.5 involve an additive common shock T shared by all
components (dependence) -> out of harness scope.
Theorem 3.6: disp and LU orders -> unsupported.
"""
import json
import os

import sympy as sp

import closedform as cf
import syscomp as sc
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))
LO = -80


def S_gum(mu, sigma):
    return 1 - sp.exp(-sp.exp((R(mu) - x) / R(sigma)))


def majorizes(a, b):
    A, B = sorted(a, reverse=True), sorted(b, reverse=True)
    return sum(A) == sum(B) and all(
        sum(A[:k]) >= sum(B[:k]) for k in range(1, len(A)))


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "arxiv_1905.00425.json")))
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
        n, wit, und = 0, None, 0
        if label == "Theorem 3.1":
            # mu_i >= mu*_i => Xn:n >=lr Yn:n  (check("lr", Y, X): E=fX FY - fY FX)
            for mX, mY, sg in [
                    ([2, 3], [1, 2], 1),
                    ([3, 1, 2], [2, 1, 1], 2),
                    ([4, 3, 5], [1, 3, 2], R(1, 2))]:
                assert all(a >= b for a, b in zip(mX, mY))
                SX = Closed(sc.parallel([S_gum(m, sg) for m in mX]), lo=LO)
                SY = Closed(sc.parallel([S_gum(m, sg) for m in mY]), lo=LO)
                h, w, u = cf.check("lr", SY, SX)   # SY <=lr SX
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            out.update(status="holds" if wit is None else "refuted")
        elif label == "Theorem 3.2":
            # mu >=^m mu* => Xn:n >=rh Yn:n  => check("rh", Ymax, Xmax)
            for mX, mY, sg in [
                    ([3, 1], [2, 2], 1),
                    ([4, 2, 1], [3, 2, 2], 2),
                    ([5, 3, 1], [3, 3, 3], R(1, 2)),
                    ([9, 5, 1], [7, 5, 3], 2)]:
                assert majorizes(mX, mY), (mX, mY)
                SX = Closed(sc.parallel([S_gum(m, sg) for m in mX]), lo=LO)
                SY = Closed(sc.parallel([S_gum(m, sg) for m in mY]), lo=LO)
                h, w, u = cf.check("rh", SY, SX)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            out.update(status="holds" if wit is None else "refuted")
        elif label == "Theorem 3.4":
            # mu >=^m mu* => X1:n <=hr Y1:n  => check("hr", Xmin, Ymin)
            for mX, mY, sg in [
                    ([3, 1], [2, 2], 1),
                    ([4, 2, 1], [3, 2, 2], 2),
                    ([5, 3, 1], [3, 3, 3], R(1, 2)),
                    ([9, 5, 1], [7, 5, 3], 2)]:
                assert majorizes(mX, mY)
                SX = Closed(sc.series([S_gum(m, sg) for m in mX]), lo=LO)
                SY = Closed(sc.series([S_gum(m, sg) for m in mY]), lo=LO)
                h, w, u = cf.check("hr", SX, SY)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            out.update(status="holds" if wit is None else "refuted")
        elif label in ("Corollary 3.3", "Corollary 3.5"):
            out["status"] = "out of harness scope"
            out["note"] = ("common additive shock T shared by all components "
                           "(dependent composition)")
        else:
            out["status"] = "out of harness scope"
        out.update(instances=n, undecided_points=und)
        if wit is not None:
            out["witness"] = str(wit)
        results.append(out)
    dest = os.path.join(HERE, "eval_arxiv_1905.00425.result.json")
    json.dump(results, open(dest, "w"), indent=1, default=str)
    print(json.dumps(results, indent=1, default=str))


if __name__ == "__main__":
    main()
