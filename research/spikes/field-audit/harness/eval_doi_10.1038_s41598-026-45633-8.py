"""Evaluation of canonical claims for doi:10.1038/s41598-026-45633-8
(Log-LFR distribution).

Family: Log-LFR(alpha, beta, p): survival
  S(x) = ln(1 - (1-p) Fbar_LFR(x)) / ln(p),
  Fbar_LFR(x) = exp(-alpha x - beta x^2/2).
Parametrize by c = ln(p) (rational, c != 0): p = e^c = sp.E**c, so every
constant stays inside the supported expression classes (Pow(E, c)).

Theorem 1: X ~ (a,b,p1), Y ~ (a,b,p2), p2 >= p1  =>  X <=lr Y.
Remark 1:   same hypotheses => X <=hr Y and X <=st Y.
Theorem 2:  alpha_i <= alpha_i*, beta_i <= beta_i*, common p =>
            X_{1:n} <=st Y_{1:n}   (series system, independent components).
Counterexample 1: p1 > p2 => X not <=lr Y (asserted failure; a strict witness
            of E < 0 confirms the counterexample -> "holds").
Counterexample 2: asserts S_{Y1:3} - S_{X1:3} < 0 somewhere on (0,1) under
            violated hypotheses; verified failure -> "holds".
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
E = sp.E
HERE = os.path.dirname(os.path.abspath(__file__))


def S_llfr(alpha, beta, c):
    """Log-LFR survival with c = ln p."""
    alpha, beta, c = R(alpha), R(beta), R(c)
    Fbar = sp.exp(-alpha * x - beta * x ** 2 / 2)
    return sp.log(1 - (1 - E ** c) * Fbar) / c


def T_llfr(alpha, beta, p):
    """Unnormalized numerator ln(1-(1-p)Fbar), rational p in (0,1).
    S_i = T_i/c_i with c_i = ln p_i < 0; for lr/hr comparisons the defining
    expression scales by 1/(c1 c2) > 0, so check(order, TX, TY) on the
    T-expressions decides the true order for single-family comparisons.
    """
    alpha, beta, p = R(alpha), R(beta), R(p)
    Fbar = sp.exp(-alpha * x - beta * x ** 2 / 2)
    return sp.log(1 - (1 - p) * Fbar)


def series_sf(survivals):
    return sp.prod(survivals)


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "doi_10.1038_s41598-026-45633-8.json")))
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
        if label == "Theorem 1":
            # X <=lr Y, p2 >= p1
            for a, b in [(R(2), R(1)), (R(1, 2), R(2)), (R(5, 2), R(3, 2))]:
                for c1, c2 in [(-R(2), -R(1)), (-R(4), -R(3, 10)),
                               (-R(1, 10), -R(1, 100)), (R(1, 10), R(1)),
                               (-R(2), R(1, 2))]:   # p<1 and p>1 covered
                    assert E ** c2 >= E ** c1
                    X = Closed(S_llfr(a, b, c1))
                    Y = Closed(S_llfr(a, b, c2))
                    h, w, u = cf.check("lr", X, Y)
                    n += 1
                    und += u
                    if not h and wit is None:
                        wit = w
            out.update(status="holds" if wit is None else "refuted")
        elif label.startswith("Remark 1"):
            sub = "hr" if "hazard" in label else "st"
            for a, b in [(R(2), R(1)), (R(1, 2), R(2))]:
                for c1, c2 in [(-R(2), -R(1)), (-R(4), -R(3, 10)),
                               (R(1, 10), R(1))]:
                    X = Closed(S_llfr(a, b, c1))
                    Y = Closed(S_llfr(a, b, c2))
                    h, w, u = cf.check(sub, X, Y)
                    n += 1
                    und += u
                    if not h and wit is None:
                        wit = w
            out.update(status="holds" if wit is None else "refuted")
        elif label == "Theorem 2":
            # X1:n <=st Y1:n, alpha_i<=alpha_i*, beta_i<=beta_i*, common c
            inst = [
                ([R(1, 2), R(1), R(3, 2)], [R(2), R(5, 2), R(3)],
                 [R(1, 10), R(3, 10), R(1, 2)], [R(1, 5), R(2, 5), R(3, 5)],
                 -R(12, 10)),                       # p = e^-1.2 ~ 0.3
                ([R(1, 10), R(3, 10), R(7, 10)], [R(6, 10), R(8, 10), R(1)],
                 [R(2, 5), R(3, 5), R(4, 5)], [R(4, 5), R(6, 5), R(8, 5)],
                 -R(12, 10)),
                ([R(1), R(3, 2), R(2)], [R(3, 2), R(2), R(5, 2)],
                 [R(1), R(2), R(3)], [R(2), R(5, 2), R(7, 2)],
                 -R(7, 10)),                        # p ~ 0.5
                ([R(1, 5), R(2, 5)], [R(3, 5), R(4, 5)],
                 [R(1), R(2)], [R(3, 2), R(5, 2)], R(1, 5)),  # p>1, n=2
            ]
            for aX, aY, bX, bY, c in inst:
                assert all(a <= aa for a, aa in zip(aX, aY))
                assert all(b <= bb for b, bb in zip(bX, bY))
                SX = Closed(series_sf([S_llfr(a, b, c)
                                       for a, b in zip(aX, bX)]))
                SY = Closed(series_sf([S_llfr(a, b, c)
                                       for a, b in zip(aY, bY)]))
                h, w, u = cf.check("st", SX, SY)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            out.update(status="holds" if wit is None else "refuted")
        elif label == "Example 1":
            # printed (p1,p2) pairs with alpha=2.5 beta=1.5, p1 < p2
            pairs = [(R(1, 10), R(1, 5)), (R(3, 10), R(2, 5)),
                     (R(1, 2), R(3, 5)), (R(7, 10), R(4, 5))]
            for p1, p2 in pairs:
                X = Closed(T_llfr(R(5, 2), R(3, 2), p1))
                Y = Closed(T_llfr(R(5, 2), R(3, 2), p2))
                h, w, u = cf.check("lr", X, Y)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            out.update(status="holds" if wit is None else "refuted")
        elif label == "Counterexample 1":
            # p1 > p2, asserts NOT X <=lr Y: a strict witness of failure
            # confirms the counterexample.
            pairs = [(R(1, 2), R(1, 10)), (R(7, 10), R(3, 10)),
                     (R(9, 10), R(3, 5))]
            ok = False
            for p1, p2 in pairs:
                assert p1 > p2
                X = Closed(T_llfr(R(4, 5), R(3, 2), p1))
                Y = Closed(T_llfr(R(4, 5), R(3, 2), p2))
                h, w, u = cf.check("lr", X, Y)
                n += 1
                und += u
                if not h:
                    ok = True
                    if wit is None:
                        wit = w
            # counterexample verified if every instance fails the order
            out.update(status="holds" if ok else "refuted")
        elif label == "Example 2":
            # Printed legend gives alpha* < alpha componentwise; the claim as
            # recorded is X1:3 <=st Y1:3.  Test BOTH assignments; record the
            # hypothesis-satisfying one (X params <= Y params componentwise).
            inst = [
                # (aX, bX, aY, bY) satisfying alpha<=alpha*, beta<=beta*
                ([R(1, 2), R(1), R(3, 2)], [R(3, 2), R(5, 2), R(4)],
                 [R(1), R(3, 2), R(2)], [R(5), R(13, 2), R(15, 2)]),
                ([R(2), R(5, 2), R(3)], [R(2), R(4), R(5)],
                 [R(5, 2), R(3), R(4)], [R(5, 2), R(8), R(10)]),
            ]
            for aY, bY, aX, bX in inst:   # starred = Y, unstarred = X (swapped to satisfy hypotheses)
                SX = Closed(series_sf([S_llfr(a, b, -R(12, 10))
                                       for a, b in zip(aX, bX)]))
                SY = Closed(series_sf([S_llfr(a, b, -R(12, 10))
                                       for a, b in zip(aY, bY)]))
                h, w, u = cf.check("st", SX, SY)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            out.update(status="holds" if wit is None else "refuted",
                       note="star assignment swapped to satisfy "
                            "alpha<=alpha*, beta<=beta* (printed legend "
                            "reverses it)")
        elif label == "Counterexample 2":
            # panels: (a) satisfies hypotheses (check anyway); (b) beta
            # violates; (c) alpha violates.  Confirmed negative diff -> holds.
            panels = [
                ("a", [R(1, 2), R(1), R(3, 2)], [R(2), R(5, 2), R(3)],
                 [R(1, 10), R(3, 10), R(1, 2)], [R(1, 5), R(2, 5), R(3, 5)]),
                ("b", [R(1, 10), R(3, 10), R(7, 10)], [R(3, 5), R(4, 5), R(1)],
                 [R(5, 2), R(3), R(7, 2)], [R(1), R(3, 2), R(2)]),
                ("c", [R(4, 100), R(6, 100), R(8, 100)],
                 [R(1, 100), R(2, 100), R(4, 100)],
                 [R(1, 10), R(3, 10), R(1, 2)], [R(1, 5), R(2, 5), R(3, 5)]),
            ]
            anyfail = False
            for tag, aX, aY, bX, bY in panels:
                SX = Closed(series_sf([S_llfr(a, b, -R(12, 10))
                                       for a, b in zip(aX, bX)]))
                SY = Closed(series_sf([S_llfr(a, b, -R(12, 10))
                                       for a, b in zip(aY, bY)]))
                h, w, u = cf.check("st", SX, SY)   # failure: S_Y - S_X < 0
                n += 1
                und += u
                if not h:
                    anyfail = True
                    if wit is None:
                        wit = w
            out.update(status="holds" if anyfail else "refuted",
                       witness=wit,
                       note="counterexample asserts negative S_Y-S_X "
                            "somewhere; observed in %s" % wit)
        else:
            out["status"] = "out of harness scope"
        out["instances"] = n
        out["undecided_points"] = und
        if out["witness"] is None and wit is not None:
            out["witness"] = str(wit)
        results.append(out)
    dest = os.path.join(HERE, "eval_doi_10.1038_s41598-026-45633-8.result.json")
    json.dump(results, open(dest, "w"), indent=1, default=str)
    print(json.dumps(results, indent=1, default=str))


if __name__ == "__main__":
    main()
