"""Evaluation of canonical claims for doi:10.1080/03610926.2021.1919898
(Gompertz-Makeham lifetimes, Bernoulli random shocks).

GM(a,b,l) survival: Fbar(x) = exp(-l x - (a/b)(e^{b x} - 1)).
Thinned component X_i = I_i U_i:  S_i(x) = p_i Fbar_i(x).

Majorization per the paper's Definition 1:
  a >=^m b : descending partial sums a >= b, equal totals (a majorizes b)
  a >=^w b : ascending partial sums a <= b   (weak supermajorization)
  a >=_w b : tail sums  sum_{i=j..n} a_(i) >= b_(i)  (weak submajorization)
"""
import json
import os

import sympy as sp

import closedform as cf
import syscomp as sc
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def maj(a, b):
    A, B = sorted(a, reverse=True), sorted(b, reverse=True)
    return sum(A) == sum(B) and all(
        sum(A[:k]) >= sum(B[:k]) for k in range(1, len(A)))


def supermaj(a, b):
    """paper's >=^w: ascending partial sums of a <= those of b."""
    A, B = sorted(a), sorted(b)
    return all(sum(A[:k]) <= sum(B[:k]) for k in range(1, len(A) + 1))


def submaj(a, b):
    """paper's >=_w: upper tail sums of a >= those of b."""
    A, B = sorted(a), sorted(b)
    return all(sum(A[k:]) >= sum(B[k:]) for k in range(len(A)))


def desc(v):
    return all(v[i] >= v[i + 1] for i in range(len(v) - 1))


def asc(v):
    return all(v[i] <= v[i + 1] for i in range(len(v) - 1))


def S_gm(a, b, l):
    return sp.exp(-l * x - (a / b) * (sp.exp(b * x) - 1))


def S_thin(p, a, b, l):
    return p * S_gm(a, b, l)


def S_series(Ss):
    return sc.series(Ss)


def S_parallel(Ss):
    return sc.parallel(Ss)


def test(order, SX, SY, out):
    h, w, u = cf.check(order, SX, SY)
    out["instances"] += 1
    out["undecided_points"] += u
    if not h and out["witness"] is None:
        out["witness"] = w


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "doi_10.1080_03610926.2021.1919898.json")))
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

        if "Counterexample 4" in label:
            out["status"] = "out of harness scope"
            out["note"] = "Archimedean copula setup of Theorems 10-13"
        elif "Counterexample 1" in label:
            # part (i): alpha vs alpha*; (ii): beta vs beta*; lr fails
            if "(i)" in label or "part a" in label:
                a1, a2 = [R(1, 10), R(20)], [R(21, 10), R(18)]
                bb = [R(1, 5), R(1, 10)]
                ll = [R(3, 5), R(1, 2)]
                Ss1 = [S_gm(a, b, l) for a, b, l in zip(a1, bb, ll)]
                Ss2 = [S_gm(a, b, l) for a, b, l in zip(a2, bb, ll)]
            else:
                a1 = a2 = [R(20), R(1, 10)]
                bb = [R(4, 5), R(1, 5)]
                bb2 = [R(7, 10), R(3, 10)]
                ll = [R(1, 2), R(3, 5)]
                Ss1 = [S_gm(a, b, l) for a, b, l in zip(a1, bb, ll)]
                Ss2 = [S_gm(a, b, l) for a, b, l in zip(a2, bb2, ll)]
            SX = Closed(S_series(Ss1))
            SY = Closed(S_series(Ss2))
            test("lr", SX, SY, out)
            out["status"] = "holds" if out["witness"] is None else "refuted"
            out["note"] = ("order X1:2 <=lr Y1:2 (the would-be hr "
                           "strengthening); refuted iff E<0 found")
        elif label == "Counterexample 2":
            a1, a2 = [R(1, 5), R(1, 10)], [R(9, 50), R(3, 25)]
            bb = [R(2), R(1)]
            l = R(3, 5)
            SX = Closed(S_parallel([S_gm(a, b, l)
                                    for a, b in zip(a1, bb)]))
            SY = Closed(S_parallel([S_gm(a, b, l)
                                    for a, b in zip(a2, bb)]))
            test("st", SY, SX, out)   # claim would be Xn:n >=st Yn:n
            out["status"] = "holds" if out["witness"] is None else "refuted"
        elif label == "Counterexample 3":
            a1 = a2 = [R(1, 10), R(1, 5)]
            bb = [R(1, 2), R(1)]
            bb2 = [R(5, 8), R(5, 7)]
            l = R(1, 50)
            SX = Closed(S_parallel([S_gm(a, b, l)
                                    for a, b in zip(a1, bb)]))
            SY = Closed(S_parallel([S_gm(a, b, l)
                                    for a, b in zip(a2, bb2)]))
            test("st", SY, SX, out)
            out["status"] = "holds" if out["witness"] is None else "refuted"
        elif label == "Theorem 4 (D+ variant)":
            for a1, a2, bb, ll in [
                    ([R(3), R(1)], [R(2), R(2)], [R(2), R(1)],
                     [R(1, 2), R(1, 4)]),
                    ([R(4), R(1)], [R(3), R(2)], [R(3), R(2)],
                     [R(1, 3), R(1, 5)]),
                    ([R(3), R(2), R(1)], [R(2), R(2), R(2)],
                     [R(2), R(1), R(1)], [R(1, 4)] * 3)]:
                assert maj(a1, a2) and desc(a1) and desc(a2) and desc(bb)
                SX = Closed(S_series([S_gm(a, b, l)
                                      for a, b, l in zip(a1, bb, ll)]))
                SY = Closed(S_series([S_gm(a, b, l)
                                      for a, b, l in zip(a2, bb, ll)]))
                test("hr", SX, SY, out)
            out["status"] = "holds" if out["witness"] is None else "refuted"
        elif label == "Theorem 4 (E+ variant)":
            for a1, a2, bb, ll in [
                    ([R(1), R(3)], [R(2), R(2)], [R(2), R(1)],
                     [R(1, 4), R(1, 2)]),
                    ([R(1), R(4)], [R(2), R(3)], [R(3), R(1)],
                     [R(1, 5), R(1, 3)])]:
                assert maj(a1, a2) and asc(a1) and asc(a2) and desc(bb)
                SX = Closed(S_series([S_gm(a, b, l)
                                      for a, b, l in zip(a1, bb, ll)]))
                SY = Closed(S_series([S_gm(a, b, l)
                                      for a, b, l in zip(a2, bb, ll)]))
                test("hr", SY, SX, out)   # claim >=hr i.e. Y <=hr X
            out["status"] = "holds" if out["witness"] is None else "refuted"
        elif label == "Theorem 5":
            for a, b1, b2, ll in [
                    ([R(2), R(1)], [R(3), R(1)], [R(2), R(2)],
                     [R(1, 2), R(1, 4)]),
                    ([R(3), R(1)], [R(4), R(2)], [R(3), R(3)],
                     [R(1, 3), R(1, 5)]),
                    ([R(1), R(2)], [R(1), R(2)], [R(3, 2), R(3, 2)],
                     [R(1, 4)] * 2)]:
                assert maj(b1, b2)
                SX = Closed(S_series([S_gm(a_, b, l)
                                      for a_, b, l in zip(a, b1, ll)]))
                SY = Closed(S_series([S_gm(a_, b, l)
                                      for a_, b, l in zip(a, b2, ll)]))
                test("hr", SX, SY, out)
            out["status"] = "holds" if out["witness"] is None else "refuted"
        elif label == "Theorem 6":
            for a, bb, l1, l2 in [
                    ([R(2), R(1)], [R(2), R(1)], [R(3), R(1)],
                     [R(2), R(1)]),
                    ([R(1), R(1)], [R(1), R(2)], [R(4), R(1)],
                     [R(2), R(2)])]:
                assert sum(l1) >= sum(l2)
                SX = Closed(S_series([S_gm(a_, b, l)
                                      for a_, b, l in zip(a, bb, l1)]))
                SY = Closed(S_series([S_gm(a_, b, l)
                                      for a_, b, l in zip(a, bb, l2)]))
                test("hr", SX, SY, out)
            out["status"] = "holds" if out["witness"] is None else "refuted"
        elif label in ("Theorem 20 (D+ variant)", "Theorem 20 (E+ variant)"):
            dp = "D+" in label
            insts = ([
                ([R(3), R(1)], [R(2), R(2)], [R(2), R(1)],
                 [R(1, 2), R(1, 4)], [R(1, 2), R(1, 2)],
                 [R(1, 3), R(1, 3)]),
                ([R(4), R(1)], [R(3), R(2)], [R(2), R(1)],
                 [R(1, 3), R(1, 5)], [R(2, 3), R(1, 2)],
                 [R(1, 2), R(1, 2)])] if dp else [
                ([R(1), R(3)], [R(2), R(2)], [R(2), R(1)],
                 [R(1, 4), R(1, 2)], [R(1, 3), R(1, 3)],
                 [R(1, 2), R(1, 2)]),
                ([R(1), R(4)], [R(2), R(3)], [R(2), R(1)],
                 [R(1, 5), R(1, 3)], [R(1, 4), R(1, 2)],
                 [R(1, 2), R(2, 3)])])
            for a1, a2, bb, ll, p, q in insts:
                assert maj(a1, a2) and desc(bb)
                prod_p = p[0] * p[1]
                prod_q = q[0] * q[1]
                if dp:
                    assert desc(a1) and desc(a2) and prod_p >= prod_q
                    SX = Closed(S_series(
                        [S_thin(pi, a, b, l)
                         for pi, a, b, l in zip(p, a1, bb, ll)]))
                    SY = Closed(S_series(
                        [S_thin(qi, a, b, l)
                         for qi, a, b, l in zip(q, a2, bb, ll)]))
                    test("hr", SX, SY, out)
                else:
                    assert asc(a1) and asc(a2) and prod_p <= prod_q
                    SX = Closed(S_series(
                        [S_thin(pi, a, b, l)
                         for pi, a, b, l in zip(p, a1, bb, ll)]))
                    SY = Closed(S_series(
                        [S_thin(qi, a, b, l)
                         for qi, a, b, l in zip(q, a2, bb, ll)]))
                    test("hr", SY, SX, out)
            out["status"] = "holds" if out["witness"] is None else "refuted"
        elif label == "Theorem 21":
            for a, b1, b2, ll, p, q in [
                    ([R(2), R(1)], [R(3), R(1)], [R(2), R(2)],
                     [R(1, 2), R(1, 4)], [R(1, 2), R(1, 2)],
                     [R(1, 3), R(1, 3)]),
                    # all-E+ branch: ascending alpha, beta, lambda
                    ([R(1), R(3)], [R(1), R(3)], [R(2), R(2)],
                     [R(1, 3), R(2, 3)], [R(1, 2), R(1, 2)],
                     [R(1, 3), R(1, 3)])]:
                assert maj(b1, b2)
                assert p[0] * p[1] >= q[0] * q[1]
                assert (desc(a) and desc(b1) and desc(b2)
                        and desc(ll)) or (asc(a) and asc(b1)
                                          and asc(b2) and asc(ll))
                SX = Closed(S_series([S_thin(pi, a_, b, l)
                                      for pi, a_, b, l
                                      in zip(p, a, b1, ll)]))
                SY = Closed(S_series([S_thin(qi, a_, b, l)
                                      for qi, a_, b, l
                                      in zip(q, a, b2, ll)]))
                test("hr", SX, SY, out)
            out["status"] = "holds" if out["witness"] is None else "refuted"
        elif label == "Theorem 22":
            for a, bb, l1, l2, p, q in [
                    ([R(2), R(1)], [R(2), R(1)], [R(3), R(1)], [R(2), R(1)],
                     [R(1, 2), R(1, 2)], [R(1, 3), R(1, 3)]),
                    ([R(1), R(2)], [R(1), R(2)], [R(4), R(2)], [R(2), R(2)],
                     [R(2, 3), R(2, 3)], [R(1, 2), R(1, 2)])]:
                assert sum(l1) >= sum(l2)
                assert p[0] * p[1] >= q[0] * q[1]
                SX = Closed(S_series([S_thin(pi, a_, b, l)
                                      for pi, a_, b, l
                                      in zip(p, a, bb, l1)]))
                SY = Closed(S_series([S_thin(qi, a_, b, l)
                                      for qi, a_, b, l
                                      in zip(q, a, bb, l2)]))
                test("hr", SX, SY, out)
            out["status"] = "holds" if out["witness"] is None else "refuted"
        elif label in ("Theorem 14", "Theorem 15"):
            # thinned parallel maxima; h(p) submajorizes h(p*)
            # h(p)=p^2 increasing convex; h(p) in E+ => p ascending
            insts = ([
                # Thm 14: vector alpha, scalar beta
                ([R(1, 2), R(4, 5)], [R(1, 3), R(2, 3)],
                 [R(2), R(1)], [R(2), R(2)], [R(2), R(1)]),
                ([R(1, 2), R(3, 4)], [R(1, 4), R(1, 2)],
                 [R(3), R(2)], [R(1), R(1)], [R(3), R(1)])]
                if label == "Theorem 14" else [
                # Thm 15: scalar alpha, vector beta
                ([R(1, 2), R(4, 5)], [R(1, 3), R(2, 3)],
                 [R(2), R(2)], [R(2), R(1)], [R(2), R(1)]),
                ([R(1, 2), R(3, 4)], [R(1, 4), R(1, 2)],
                 [R(3), R(3)], [R(2), R(1)], [R(3), R(1)])])
            for p, q, aa, bb, ll in insts:
                hp = [pi ** 2 for pi in p]
                hq = [qi ** 2 for qi in q]
                assert submaj(hp, hq) and asc(hp) and asc(hq)
                assert desc(aa) and desc(ll)
                SX = Closed(S_parallel([S_thin(pi, a, b, l)
                                        for pi, a, b, l
                                        in zip(p, aa, bb, ll)]))
                SY = Closed(S_parallel([S_thin(qi, a, b, l)
                                        for qi, a, b, l
                                        in zip(q, aa, bb, ll)]))
                test("st", SY, SX, out)   # Xn:n >=st Yn:n
            out["status"] = "holds" if out["witness"] is None else "refuted"
            out["note"] = ("h(p)=p^2 (increasing convex); h(p)>=_w h(p*) "
                           "as upper-tail-sums >=")
        elif label == "Theorem 16":
            # common shocks p ascending (h(p) in E+) forces alpha,lambda
            # descending (D+); alpha weakly supermajorized (asc <=)
            pp = [R(1, 2), R(2, 3)]
            for a1, a2, bb, ll in [
                    ([R(4), R(2)], [R(3), R(3)], [R(2), R(1)],
                     [R(1), R(1, 2)]),
                    ([R(4), R(1)], [R(3), R(2)], [R(2), R(1)],
                     [R(1), R(1, 3)])]:
                assert supermaj(a1, a2)
                SX = Closed(S_parallel([S_thin(pi, a, b, l)
                                        for pi, a, b, l
                                        in zip(pp, a1, bb, ll)]))
                SY = Closed(S_parallel([S_thin(pi, a, b, l)
                                        for pi, a, b, l
                                        in zip(pp, a2, bb, ll)]))
                test("st", SY, SX, out)
            out["status"] = "holds" if out["witness"] is None else "refuted"
        elif label == "Theorem 17":
            # common shocks; lambda weakly supermajorized
            pp = [R(1, 2), R(2, 3)]
            for a, bb, l1, l2 in [
                    ([R(2), R(1)], [R(2), R(1)], [R(3), R(1)],
                     [R(2), R(2)]),
                    ([R(3), R(1)], [R(2), R(1)], [R(4), R(1)],
                     [R(3), R(2)])]:
                assert supermaj(l1, l2)
                SX = Closed(S_parallel([S_thin(pi, a_, b, l)
                                        for pi, a_, b, l
                                        in zip(pp, a, bb, l1)]))
                SY = Closed(S_parallel([S_thin(pi, a_, b, l)
                                        for pi, a_, b, l
                                        in zip(pp, a, bb, l2)]))
                test("st", SY, SX, out)
            out["status"] = "holds" if out["witness"] is None else "refuted"
        elif label == "Theorem 18":
            # scalar alpha (duplicated), vector beta; lambda supermajorized
            pp = [R(1, 2), R(2, 3)]
            for a, bb, l1, l2 in [
                    ([R(1), R(1)], [R(2), R(1)], [R(3), R(1)],
                     [R(2), R(2)]),
                    ([R(2), R(2)], [R(2), R(1)], [R(4), R(1)],
                     [R(3), R(2)])]:
                assert supermaj(l1, l2)
                SX = Closed(S_parallel([S_thin(pi, a_, b, l)
                                        for pi, a_, b, l
                                        in zip(pp, a, bb, l1)]))
                SY = Closed(S_parallel([S_thin(pi, a_, b, l)
                                        for pi, a_, b, l
                                        in zip(pp, a, bb, l2)]))
                test("st", SY, SX, out)
            out["status"] = "holds" if out["witness"] is None else "refuted"
        elif label == "Theorem 19":
            # params ascending (E+) -> shocks descending (D+)
            pp = [R(2, 3), R(1, 2)]
            for a, b1, b2, ll in [
                    ([R(1), R(1)], [R(1), R(2)], [R(2), R(3)],
                     [R(1), R(2)]),
                    ([R(2), R(2)], [R(1, 2), R(1)], [R(1), R(3, 2)],
                     [R(1), R(2)])]:
                r1 = [1 / b for b in b1]
                r2 = [1 / b for b in b2]
                assert submaj(r1, r2)
                SX = Closed(S_parallel([S_thin(pi, a_, b, l)
                                        for pi, a_, b, l
                                        in zip(pp, a, b1, ll)]))
                SY = Closed(S_parallel([S_thin(pi, a_, b, l)
                                        for pi, a_, b, l
                                        in zip(pp, a, b2, ll)]))
                test("st", SY, SX, out)
            out["status"] = "holds" if out["witness"] is None else "refuted"
        else:
            out["status"] = "out of harness scope"
            out["note"] = "Archimedean copula dependence"
        results.append(out)
        if out["witness"] is not None:
            out["witness"] = str(out["witness"])
    dest = os.path.join(HERE,
                        "eval_doi_10.1080_03610926.2021.1919898.result.json")
    json.dump(results, open(dest, "w"), indent=1, default=str)
    print(json.dumps(results, indent=1, default=str))


if __name__ == "__main__":
    main()
