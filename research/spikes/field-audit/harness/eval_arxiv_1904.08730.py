"""Evaluation of canonical claims for arxiv:1904.08730
(Exponentiated Gumbel type-II order statistics under chain/vector
majorization of parameter matrices).

EG2(theta, phi, alpha):  F(x) = 1 - (1 - e^{-theta x^{-phi}})^alpha,
                        S(x) = (1 - e^{-theta x^{-phi}})^alpha, x > 0.

Key facts used:
  * series (min) survival = prod S_i; parallel (max) survival = 1 - prod(1-S_i)
    (independent components, harness syscomp).
  * For common theta, phi: min survival = (1 - e^{-theta x^{-phi}})^{sum a_i}
    i.e. EG2(theta, phi, sum a_i) -- used by Theorems 3.8/3.10.
  * Sn membership: rows anti-comonotone ((a_i - a_j)(t_i - t_j) <= 0), x>0.
  * Tn membership: same + alpha_i >= 1.
  * Chain majorization A >> B  <=>  B = A*T_{w1}...T_{wk}; T_w^(i,j) mixes
    columns i,j: col_i' = w col_i + (1-w) col_j, col_j' likewise.
"""
import json
import os

import sympy as sp

import closedform as cf
import syscomp as sc
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_eg2(theta, phi, alpha):
    return (1 - sp.exp(-R(theta) * x ** (-R(phi)))) ** R(alpha)


def in_S(mat):
    """mat = ([a_1..a_n], [t_1..t_n]); rows anti-comonotone, all >0."""
    a, t = mat
    n = len(a)
    return all(v > 0 for v in a + t) and all(
        (a[i] - a[j]) * (t[i] - t[j]) <= 0
        for i in range(n) for j in range(n))


def in_T(mat):
    return in_S(mat) and all(v >= 1 for v in mat[0])


def T_transform(mat, i, j, w):
    """B = A*T_w^(i,j): mixes columns i,j with weight w on the diagonal."""
    a, t = [list(r) for r in mat]
    a[i], a[j] = w * a[i] + (1 - w) * a[j], w * a[j] + (1 - w) * a[i]
    t[i], t[j] = w * t[i] + (1 - w) * t[j], w * t[j] + (1 - w) * t[i]
    return (a, t)


def majorizes(u, v):
    U, V = sorted(u, reverse=True), sorted(v, reverse=True)
    return sum(U) == sum(V) and all(
        sum(U[:k]) >= sum(V[:k]) for k in range(1, len(U)))


def sys_min(mat, phi):
    a, t = mat
    return sc.series([S_eg2(ti, phi, ai) for ti, ai in zip(t, a)])


def sys_max(mat, phi):
    a, t = mat
    return sc.parallel([S_eg2(ti, phi, ai) for ti, ai in zip(t, a)])


def run(order, exprX, exprY, tag):
    h, w, u = cf.check(order, Closed(exprX), Closed(exprY))
    return h, w, u


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "arxiv_1904.08730.json")))
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
        note = None

        if label == "Example 3.12":
            # asserts X_{n:n} NOT >=st X*_{n:n} (crossing); common theta=5,
            # alpha=2; phi vs phi*; n=3 parallel systems.
            mX = ([R(2)] * 3, [R(5)] * 3)
            phiX = [R(1, 10), R(114, 100), R(3, 10)]
            phiY = [R(6, 10), R(9, 10), R(4, 100)]
            SX = sc.parallel([S_eg2(5, p, 2) for p in phiX])
            SY = sc.parallel([S_eg2(5, p, 2) for p in phiY])
            # failure of X >=st Y  <=>  witness where S_X - S_Y < 0
            h1, w1, u1 = cf.check("st", Closed(SY), Closed(SX))
            # failure of Y >=st X as well (crossing)?
            h2, w2, u2 = cf.check("st", Closed(SX), Closed(SY))
            n, und = 1, u1 + u2
            if not h1:
                wit, note = w1, "S_X<S_Y at witness confirms X n>=st Y"
                if not h2:
                    note += "; crossing confirmed (also S_Y<S_X at %s)" % w2
                out["status"] = "holds"
            else:
                out["status"] = "refuted"
        elif label == "Example 3.3":
            mA = ([R(54, 100), R(66, 100)], [R(17, 10), R(14, 10)])
            mB = ([R(5, 10), R(7, 10)], [R(18, 10), R(13, 10)])
            assert in_S(mA) and in_S(mB)
            # printed: A = B*T_0.8 (so B >> A per Def 2.5; recorded ambiguity)
            chk = T_transform(mB, 0, 1, R(4, 5))
            assert chk == (mA[0], mA[1])
            n, und = 1, 0
            # conclusion X_{1:2} <=st X*_{1:2} on the printed numbers
            h, w, u = run("st", sys_min(mA, 1), sys_min(mB, 1), label)
            und += u
            if not h:
                wit = w
            out["status"] = "holds" if wit is None else "refuted"
            out["note"] = ("phi=1 used (not printed); hypotheses actually "
                           "satisfied under B>>A (printed direction "
                           "reversed)")
        elif label == "Example 3.4":
            mA = ([R(234, 100), R(226, 100)], [R(132, 100), R(138, 100)])
            mB = ([R(21, 10), R(25, 10)], [R(15, 10), R(12, 10)])
            assert in_T(mA) and in_T(mB)
            chk = T_transform(mB, 0, 1, R(4, 10))
            assert chk == (mA[0], mA[1])   # printed: A = B*T_0.4
            n, und = 1, 0
            # conclusion X_{2:2} >=st X*_{2:2} <=> check S_Amax - S_Bmax >=0
            h, w, u = run("st", sys_max(mB, 1), sys_max(mA, 1), label)
            und += u
            if not h:
                wit = w
            out["status"] = "holds" if wit is None else "refuted"
            out["note"] = "phi=1; T-weight 0.4 (printed 'T0.6' label is a slip)"
        elif label == "Theorem 3.1":
            # A in S2, B = A*T_w ; conclusion X*_{1:2} >=st X_{1:2}
            insts = []
            for A, i, j, w in [
                    (([R(1, 2), R(3, 2)], [R(2), R(1)]), 0, 1, R(3, 4)),
                    (([R(1, 4), R(2)], [R(3), R(1, 2)]), 0, 1, R(1, 2)),
                    (([R(3, 4), R(9, 4)], [R(5, 2), R(7, 4)]), 0, 1, R(2, 3))]:
                B = T_transform(A, i, j, w)
                assert in_S(A)
                insts.append((A, B))
            for A, B in insts:
                for phi in [1, 2]:
                    h, w_, u = run("st", sys_min(A, phi), sys_min(B, phi), label)
                    n += 1
                    und += u
                    if not h and wit is None:
                        wit = w_
            out.update(status="holds" if wit is None else "refuted")
        elif label == "Theorem 3.2":
            # A in T2 (alpha>=1), B = A*T_w ; conclusion X_{2:2} >=st X*_{2:2}
            for A, i, j, w in [
                    (([R(3, 2), R(2)], [R(2), R(1)]), 0, 1, R(3, 4)),
                    (([R(2), R(5)], [R(3), R(1)]), 0, 1, R(1, 2)),
                    (([R(5, 4), R(3)], [R(5, 2), R(2)]), 0, 1, R(1, 4))]:
                B = T_transform(A, i, j, w)
                assert in_T(A) and in_T(B), (A, B)
                for phi in [1, 3]:
                    h, w_, u = run("st", sys_max(B, phi), sys_max(A, phi), label)
                    n += 1
                    und += u
                    if not h and wit is None:
                        wit = w_
            out.update(status="holds" if wit is None else "refuted")
        elif label in ("Theorem 3.5(1)", "Corollary 3.6(1)"):
            # parallel, n>=2, single T (3.5) or same-structure chain (3.6)
            for A, steps in [
                    (([R(1), R(2), R(3)], [R(3), R(2), R(1)]),
                     [(0, 1, R(1, 3))]),
                    (([R(3, 2), R(5, 2), R(4)], [R(4), R(3), R(2)]),
                     [(1, 2, R(1, 4))]),
                    (([R(1), R(2), R(3)], [R(3), R(2), R(1)]),
                     [(0, 1, R(1, 2)), (0, 1, R(1, 4))]),
                    (([R(2), R(3), R(5)], [R(5), R(3), R(2)]),
                     [(0, 1, R(1, 2)), (1, 2, R(1, 5))])]:
                B = A
                for i, j, w in steps:
                    B = T_transform(B, i, j, w)
                assert in_T(A) and in_T(B), (A, B)
                for phi in [1, 2]:
                    h, w_, u = run("st", sys_max(B, phi), sys_max(A, phi), label)
                    n += 1
                    und += u
                    if not h and wit is None:
                        wit = w_
            out.update(status="holds" if wit is None else "refuted")
        elif label in ("Theorem 3.5(2)", "Corollary 3.6(2)"):
            for A, steps in [
                    (([R(1, 2), R(1), R(3, 2)], [R(3), R(2), R(1)]),
                     [(0, 1, R(1, 3))]),
                    (([R(1, 4), R(1), R(7, 4)], [R(7, 2), R(2), R(1)]),
                     [(1, 2, R(1, 4))]),
                    (([R(1, 2), R(1), R(3, 2)], [R(3), R(2), R(1)]),
                     [(0, 1, R(1, 2)), (0, 1, R(1, 4))]),
                    (([R(1, 5), R(1, 2), R(1)], [R(4), R(3), R(2)]),
                     [(0, 1, R(1, 2)), (1, 2, R(3, 4))])]:
                B = A
                for i, j, w in steps:
                    B = T_transform(B, i, j, w)
                assert in_S(A) and in_S(B)
                for phi in [1, 2]:
                    h, w_, u = run("st", sys_min(A, phi), sys_min(B, phi), label)
                    n += 1
                    und += u
                    if not h and wit is None:
                        wit = w_
            out.update(status="holds" if wit is None else "refuted")
        elif label == "Theorem 3.7(1)":
            # chains with DIFFERENT structures; intermediates must be in Tn
            for A, steps in [
                    (([R(1), R(2), R(4)], [R(4), R(2), R(1)]),
                     [(0, 1, R(1, 2)), (1, 2, R(1, 2))]),
                    (([R(1), R(3), R(4)], [R(5), R(3), R(1)]),
                     [(1, 2, R(1, 3)), (0, 2, R(1, 2))])]:
                mats = [A]
                for i, j, w in steps:
                    mats.append(T_transform(mats[-1], i, j, w))
                assert all(in_T(m) for m in mats), mats
                for phi in [1, 2]:
                    h, w_, u = run("st", sys_max(mats[-1], phi),
                                   sys_max(A, phi), label)
                    n += 1
                    und += u
                    if not h and wit is None:
                        wit = w_
            out.update(status="holds" if wit is None else "refuted")
        elif label == "Theorem 3.7(2)":
            for A, steps in [
                    (([R(1, 2), R(1), R(2)], [R(4), R(2), R(1)]),
                     [(0, 1, R(1, 2)), (1, 2, R(1, 2))]),
                    (([R(1, 4), R(1, 2), R(3)], [R(6), R(3), R(2)]),
                     [(1, 2, R(1, 3)), (0, 1, R(1, 2))])]:
                mats = [A]
                for i, j, w in steps:
                    mats.append(T_transform(mats[-1], i, j, w))
                assert all(in_S(m) for m in mats)
                for phi in [1, 2]:
                    h, w_, u = run("st", sys_min(A, phi), sys_min(mats[-1], phi),
                                   label)
                    n += 1
                    und += u
                    if not h and wit is None:
                        wit = w_
            out.update(status="holds" if wit is None else "refuted")
        elif label == "Theorem 3.8":
            # equality in law under common theta, phi: verify st both ways on
            # pairs with equal sums (alpha maj alpha* requires equal sums)
            for aA, aB in [([2, 1], [R(3, 2), R(3, 2)]),
                           ([3, 1, 1], [R(5, 3), R(5, 3), R(5, 3)]),
                           ([4, 2], [3, 3])]:
                assert majorizes(aA, aB) or majorizes(aB, aA)
                for th, ph in [(1, 1), (2, R(3, 2))]:
                    SX = sc.series([S_eg2(th, ph, a) for a in aA])
                    SY = sc.series([S_eg2(th, ph, a) for a in aB])
                    h, w_, u = run("st", SX, SY, label)
                    n += 1
                    und += u
                    if not h and wit is None:
                        wit = w_
            out.update(status="holds" if wit is None else "refuted")
        elif label == "Theorem 3.9":
            # parallel maxima, alpha >=^m alpha*  =>  Xn:n >=rh X*n:n
            for aA, aB in [([2, 1], [R(3, 2), R(3, 2)]),
                           ([3, 1, 1], [R(5, 3), R(5, 3), R(5, 3)]),
                           ([4, 2], [3, 3]),
                           ([R(9, 4), R(3, 4), R(1, 2)],
                            [R(3, 2), R(5, 4), R(3, 4)])]:
                assert majorizes(aA, aB), (aA, aB)
                for th, ph in [(1, 1), (2, 2)]:
                    SX = sc.parallel([S_eg2(th, ph, a) for a in aA])
                    SY = sc.parallel([S_eg2(th, ph, a) for a in aB])
                    # X >=rh Y <=> check("rh", Y, X)
                    h, w_, u = run("rh", SY, SX, label)
                    n += 1
                    und += u
                    if not h and wit is None:
                        wit = w_
            out.update(status="holds" if wit is None else "refuted")
        elif label == "Theorem 3.10":
            # series minima, common theta,phi, sum a <= sum a* =>
            # X1:n <=lr X*1:n ; min survival is EG2(theta,phi,sum a)
            for aA, aB in [([1, 1], [2, 2]),
                           ([1, 2], [2, 5]),
                           ([R(1, 2), R(1, 2), 1], [2, 1, 3])]:
                assert sum(aA) <= sum(aB)
                for th, ph in [(1, 1), (3, 2)]:
                    SX = S_eg2(th, ph, sum(aA))
                    SY = S_eg2(th, ph, sum(aB))
                    h, w_, u = run("lr", SX, SY, label)
                    n += 1
                    und += u
                    if not h and wit is None:
                        wit = w_
            out.update(status="holds" if wit is None else "refuted",
                       note="min reduces to EG2(theta,phi,Sa); density ratio "
                            "f_{Sa*}/f_{Sa} ~ (1-e^{-tx^{-p}})^{Sa*-Sa} is "
                            "DECREASING in x, suggesting the printed "
                            "direction fails")
        elif label == "Theorem 3.11":
            # series minima, common theta,alpha; phi >=^m phi* =>
            # X1:n <=st X*1:n
            for phA, phB in [([2, 1], [R(3, 2), R(3, 2)]),
                             ([3, 1, 1], [R(5, 3), R(5, 3), R(5, 3)]),
                             ([4, 2], [3, 3])]:
                assert majorizes(phA, phB)
                for th, al in [(1, R(1, 2)), (2, 3)]:
                    SX = sc.series([S_eg2(th, p, al) for p in phA])
                    SY = sc.series([S_eg2(th, p, al) for p in phB])
                    h, w_, u = run("st", SX, SY, label)
                    n += 1
                    und += u
                    if not h and wit is None:
                        wit = w_
            out.update(status="holds" if wit is None else "refuted")
        else:
            out["status"] = "out of harness scope"
        out.update(instances=n, undecided_points=und)
        if wit is not None and out["witness"] is None:
            out["witness"] = str(wit)
        if note and "note" not in out:
            out["note"] = note
        results.append(out)
    dest = os.path.join(HERE, "eval_arxiv_1904.08730.result.json")
    json.dump(results, open(dest, "w"), indent=1, default=str)
    print(json.dumps(results, indent=1, default=str))


if __name__ == "__main__":
    main()
