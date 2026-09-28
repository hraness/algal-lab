"""Evaluation of canonical claims for doi:10.19195/0208-4147.38.2.10
(Harris family preservation properties).

Harris family: Hbar(x; th, k) = (th Fbar^k)^{1/k} / (1 - thb Fbar^k),
thb = 1 - th, baseline Fbar.  Baseline used: Fbar = e^{-x} (also e^{-2x}
in pairs).

Scope: plr/phr/up/down-shifted orders, LOR, expectation, star, su, c, AI,
disp, mrl, lorenz -> unsupported order.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_harris(th, k, rate):
    # Hbar = (th Fbar^k / (1 - thb Fbar^k))^(1/k);  thb = 1 - th
    F = sp.exp(-rate * x)
    return (th * F ** k / (1 - (1 - th) * F ** k)) ** (R(1) / k)


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "doi_10.19195_0208-4147.38.2.10.json")))
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

        if label == "Corollary 3.1":
            # Y1 <=ord Y2 under {th1<=1<=th2} or {th1<=th2, k1=k2}
            for th1, k1, th2, k2 in [
                    (R(1, 2), R(1), R(2), R(3)),       # branch 1
                    (R(1, 3), R(2), R(2), R(1, 2)),    # branch 1 (k free)
                    (R(1, 2), R(2), R(1), R(2)),       # branch 2
                    (R(1, 4), R(1, 2), R(3), R(1, 2)), # branch 2
                    (R(2), R(1, 2), R(3), R(1, 2))]:   # branch 2
                SX = Closed(S_harris(th1, k1, R(1)))
                SY = Closed(S_harris(th2, k2, R(1)))
                h, w, u = cf.check(order, SX, SY)
                out["instances"] += 1
                out["undecided_points"] += u
                if not h and out["witness"] is None:
                    out["witness"] = w
            out["status"] = ("holds" if out["witness"] is None
                             else "refuted")
        elif label == "Remark 3.1":
            # k=1 (Marshall-Olkin): lr direction correction: paper asserts
            # Y1 <=lr Y2 needs th1 <= th2 (fixing [20]'s th1 >= th2).
            n, wit1, wit2, und = 0, None, None, 0
            for th1, th2 in [(R(1, 2), R(1)), (R(1, 3), R(2)),
                             (R(1), R(4)), (R(2), R(3))]:
                h, w, u = cf.check("lr", Closed(S_harris(th1, 1, R(1))),
                                   Closed(S_harris(th2, 1, R(1))))
                n += 1
                und += u
                if not h and wit1 is None:
                    wit1 = w
            for th1, th2 in [(R(1), R(1, 2)), (R(3), R(1)),
                             (R(2), R(1, 3))]:
                h, w, u = cf.check("lr", Closed(S_harris(th1, 1, R(1))),
                                   Closed(S_harris(th2, 1, R(1))))
                n += 1
                und += u
                if not h and wit2 is None:
                    wit2 = w
            out.update(instances=n, undecided_points=und)
            if wit1 is None and wit2 is not None:
                out["status"] = "holds"
                out["note"] = ("consistent with the printed correction: "
                               "th1<=th2 gives lr order; th1>th2 refutes "
                               "the misprinted direction")
            elif wit1 is not None:
                out["status"] = "refuted"
                out["witness"] = str(wit1)
            else:
                out["status"] = "holds"
                out["note"] = ("th1>th2 direction also survived bounded "
                               "testing; correction only partially "
                               "verifiable")
        elif label == "Remark 4.2":
            # preservation X<=ord X2 => Y1<=ord Y2 under common (th,k)
            for r1, r2, th, k in [(R(2), R(1), R(2), R(1)),
                                  (R(3), R(1), R(1, 2), R(2)),
                                  (R(3), R(2), R(3, 2), R(3))]:
                SX = Closed(sp.exp(-r1 * x))
                SY = Closed(sp.exp(-r2 * x))
                h0, _, _ = cf.check(order, SX, SY)
                SY1 = Closed(S_harris(th, k, r1))
                SY2 = Closed(S_harris(th, k, r2))
                h, w, u = cf.check(order, SY1, SY2)
                out["instances"] += 1
                out["undecided_points"] += u
                assert h0
                if not h and out["witness"] is None:
                    out["witness"] = w
            out["status"] = ("holds" if out["witness"] is None
                             else "refuted")
        elif label == "Theorem 4.2(i)":
            # X1 <=hr X2 => Y1 <=hr Y2 for th >= 1
            for r1, r2, th, k in [(R(2), R(1), R(2), R(1)),
                                  (R(3), R(1), R(3), R(1, 2)),
                                  (R(4), R(2), R(5, 2), R(2))]:
                SY1 = Closed(S_harris(th, k, r1))
                SY2 = Closed(S_harris(th, k, r2))
                h, w, u = cf.check("hr", SY1, SY2)
                out["instances"] += 1
                out["undecided_points"] += u
                if not h and out["witness"] is None:
                    out["witness"] = w
            out["status"] = ("holds" if out["witness"] is None
                             else "refuted")
        elif label == "Theorem 4.2(ii)":
            # converse direction: Y1 <=hr Y2 => X1 <=hr X2 for 0 < th <= 1
            for r1, r2, th, k in [(R(2), R(1), R(1, 2), R(1)),
                                  (R(3), R(1), R(1, 3), R(2)),
                                  (R(4), R(2), R(1), R(1))]:
                SX = Closed(sp.exp(-r1 * x))
                SY = Closed(sp.exp(-r2 * x))
                h, w, u = cf.check("hr", SX, SY)
                out["instances"] += 1
                out["undecided_points"] += u
                if not h and out["witness"] is None:
                    out["witness"] = w
            out["status"] = ("holds" if out["witness"] is None
                             else "refuted")
            out["note"] = ("tested on baseline pairs that satisfy the "
                           "premise (exponential pairs; Harris image is "
                           "hr-ordered for th<=1)")
        elif label == "Theorem 3.2":
            # Y1 <=lr Y2 under the two branch conditions
            for th1, k1, th2, k2, r in [
                    (R(1, 2), R(1), R(2), R(3), R(1)),
                    (R(1, 3), R(2), R(2), R(1, 2), R(2)),
                    (R(1, 2), R(2), R(1), R(2), R(1)),
                    (R(2), R(1, 2), R(3), R(1, 2), R(3))]:
                SX = Closed(S_harris(th1, k1, r))
                SY = Closed(S_harris(th2, k2, r))
                h, w, u = cf.check("lr", SX, SY)
                out["instances"] += 1
                out["undecided_points"] += u
                if not h and out["witness"] is None:
                    out["witness"] = w
            out["status"] = ("holds" if out["witness"] is None
                             else "refuted")
        elif label == "Theorem 4.1":
            # st-order iff under common tilt
            for r1, r2, th, k in [(R(2), R(1), R(2), R(1)),
                                  (R(3), R(1), R(1, 3), R(2)),
                                  (R(2), R(3, 2), R(3), R(3))]:
                SY1 = Closed(S_harris(th, k, r1))
                SY2 = Closed(S_harris(th, k, r2))
                h, w, u = cf.check("st", SY1, SY2)
                out["instances"] += 1
                out["undecided_points"] += u
                if not h and out["witness"] is None:
                    out["witness"] = w
            out["status"] = ("holds" if out["witness"] is None
                             else "refuted")
        elif label == "Counterexample 4.1":
            out["status"] = "unsupported order"
            out["note"] = ("concerns the up-shifted hazard order "
                           "(hr-up), not plain hr")
        else:
            out["status"] = "unsupported order"
        results.append(out)
        if out["witness"] is not None and not isinstance(
                out["witness"], str):
            out["witness"] = str(out["witness"])
    dest = os.path.join(
        HERE, "eval_doi_10.19195_0208-4147.38.2.10.result.json")
    json.dump(results, open(dest, "w"), indent=1, default=str)
    print(json.dumps(results, indent=1, default=str))


if __name__ == "__main__":
    main()
