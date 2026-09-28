"""Evaluator for doi:10.1080/02331888.2020.1722670 (arXiv:1612.00571)
"Reliability study of series and parallel systems ... proportional odds model".

PO(Fbar, lam) component survival:  S_i(x) = lam_i * Fbar(x) / (1 - (1-lam_i)Fbar(x)).
Series (n components):      S_{1:n} = (prod lam_i) Fbar^n / prod(1 - lambar_i Fbar).
Parallel:                   F_{n:n} = F^n / prod(1 - lambar_i Fbar) = prod(F/(1-lambar_i Fbar)).
Multiple-outlier model: parameter vector = (lam1*n1, lam2*n2) blocks.

Records with 'ageing' (relative-ageing ratio) conclusions are unsupported:
the harness supports only ordinary st/hr/rh/lr pointwise/ratio tests.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def series_S(lams, Fb):
    return sp.prod([l * Fb / (1 - (1 - l) * Fb) for l in lams])


def parallel_F(lams, Fb):
    F = 1 - Fb
    return sp.prod([F / (1 - (1 - l) * Fb) for l in lams])


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


def majeq(a, b):
    a, b = sorted(a, reverse=True), sorted(b, reverse=True)
    return sum(a) == sum(b) and all(
        sum(a[:k]) >= sum(b[:k]) for k in range(len(a)))


def wsup(a, b):
    """weak supermajorization in this paper's sense: ascending partial
    sums of a <= those of b (a more spread downward)."""
    a, b = sorted(a), sorted(b)
    return all(sum(a[:k]) <= sum(b[:k]) for k in range(1, len(a) + 1))


def plarger(a, b):
    """p-larger: ascending partial products a <= b."""
    a, b = sorted(a), sorted(b)
    return all(sp.prod(a[:k]) <= sp.prod(b[:k])
               for k in range(1, len(a) + 1))


FEXP2 = sp.exp(-2 * x)
FEXP12 = sp.exp(-R(12, 10) * x)
FEXP15 = sp.exp(-R(15, 10) * x)
FEXP18 = sp.exp(-R(18, 10) * x)
FWB = sp.exp(-(x / R(2, 5)) ** 2)
FN = sp.exp(-x ** 2 / 2)


def batch(order, cases, kind, base):
    """cases: list of (lams_X, lams_Y); test claim X <=order Y once each."""
    n, wit, und = 0, None, 0
    for lx, ly in cases:
        if kind == "series":
            DU = Closed(series_S(lx, base))
            DV = Closed(series_S(ly, base))
        else:
            DU = Closed(1 - parallel_F(lx, base))
            DV = Closed(1 - parallel_F(ly, base))
        h, w_, u_ = cf.check(order, DU, DV)
        n += 1; und += u_
        if not h and wit is None:
            wit = w_
    return n, wit, und


def theorem_3_1():
    """p-larger => X1:n <=st Y1:n.  Paper pair (2,3,5) vs (2.5,3.5,6)
    plus synthetic p-larger pairs."""
    cases = [
        ([R(2), R(3), R(5)], [R(5, 2), R(7, 2), R(6)]),
        ([R(1), R(2), R(6)], [R(2), R(2), R(3)]),
        ([R(1), R(4), R(6)], [R(2), R(3), R(4)]),
        ([R(2), R(8)], [R(3), R(6)]),
    ]
    for lx, ly in cases:
        assert plarger(lx, ly)
    return batch("st", cases, "series", FEXP2)


def theorem_3_2():
    """weak supermajorization => X1:n <=hr Y1:n."""
    cases = [
        ([R(3), R(9, 2), R(6)], [R(4), R(5), R(6)]),       # Example 5.2
        ([R(1), R(2), R(6)], [R(2), R(3), R(4)]),
        ([R(1), R(3), R(8)], [R(2), R(4), R(6)]),
        ([R(1), R(6)], [R(2), R(5)]),
    ]
    for lx, ly in cases:
        assert wsup(lx, ly)
    return batch("hr", cases, "series", FEXP2)


def corollary_3_1():
    """homogeneous level >= geometric mean of hetero vector:
    X1:n <=st Y1:n."""
    cases = [
        ([R(1), R(2), R(8)], [R(3)] * 3),      # geomean (16)^(1/3)=2.52<3
        ([R(1), R(4), R(9)], [R(4)] * 3),      # geomean 36^(1/3)=3.3<4
        ([R(1), R(8)], [R(3)] * 2),            # geomean sqrt8=2.83<3
    ]
    n, wit, und = 0, None, 0
    for lx, ly in cases:
        g = float(sp.N(sp.prod(lx) ** (R(1) / len(lx))))
        assert float(ly[0]) >= g
        DU = Closed(series_S(lx, FEXP2)); DV = Closed(series_S(ly, FEXP2))
        h, w_, u_ = cf.check("st", DU, DV)
        n += 1; und += u_
        if not h and wit is None:
            wit = w_
    return n, wit, und


def corollary_3_2():
    """homogeneous level >= arithmetic mean => X1:n <=hr Y1:n."""
    cases = [
        ([R(1), R(2), R(6)], [R(3)] * 3),
        ([R(1), R(4), R(7)], [R(5)] * 3),
        ([R(2), R(8)], [R(6)] * 2),
    ]
    for lx, ly in cases:
        assert ly[0] >= sum(lx) / len(lx)
    return batch("hr", cases, "series", FEXP2)


def theorem_3_8():
    """Multiple-outlier lr: blocked maj (resp. wmaj) with both level pairs
    in E+ or D+; or interlaced.  Claim X1:n <=lr Y1:n."""
    cases = [  # (lams_X, lams_Y): blocked majorization + ordered blocks
        ([R(1), R(1), R(5), R(5)], [R(2), R(2), R(4), R(4)]),  # both asc
        ([R(5), R(5), R(1), R(1)], [R(4), R(4), R(2), R(2)]),  # both desc
        ([R(1), R(1), R(1), R(6), R(6), R(6)],
         [R(2), R(2), R(2), R(5), R(5), R(5)]),
        # interlaced lambda1<=mu1<=mu2<=lambda2
        ([R(1), R(1), R(4), R(4)], [R(2), R(2), R(3), R(3)]),
        ([R(1), R(1), R(5), R(5)], [R(3), R(3), R(3), R(3)]),
    ]
    n, wit, und = 0, None, 0
    for lx, ly in cases:
        # weak supermajorization (asc partial sums lx <= ly)
        assert wsup(lx, ly)
        DU = Closed(series_S(lx, FEXP2)); DV = Closed(series_S(ly, FEXP2))
        h, w_, u_ = cf.check("lr", DU, DV)
        n += 1; und += u_
        if not h and wit is None:
            wit = w_
    return n, wit, und


def theorem_3_9():
    """hetero vs homogeneous, lambda >= arithmetic mean => X1:n <=lr Y1:n."""
    cases = [
        ([R(1), R(2), R(6)], [R(3)] * 3),
        ([R(1), R(4), R(10)], [R(6)] * 3),
        ([R(2), R(9)], [R(6)] * 2),
    ]
    for lx, ly in cases:
        assert ly[0] >= sum(lx) / len(lx)
    return batch("lr", cases, "series", FEXP2)


def theorem_4_1():
    """weak supermajorization => Xn:n <=rh Yn:n."""
    cases = [
        ([R(1, 2), R(5, 2), R(4)], [R(1), R(3), R(5)]),    # Example 5.6
        ([R(1), R(2), R(6)], [R(2), R(3), R(4)]),
        ([R(1), R(3), R(8)], [R(2), R(4), R(6)]),
        ([R(1), R(6)], [R(2), R(5)]),
    ]
    for lx, ly in cases:
        assert wsup(lx, ly)
    return batch("rh", cases, "parallel", FEXP15)


def theorem_4_2():
    """hetero parallel vs homogeneous at geometric mean: Xn:n >=st Yn:n."""
    cases = [
        # (lambda vector, homogeneous level = exact geometric mean)
        ([R(1), R(1), R(8)], R(2)),      # (8)^(1/3) = 2
        ([R(1), R(4), R(16)], R(4)),     # (64)^(1/3) = 4
        ([R(2), R(8)], R(4)),            # sqrt(16) = 4
        ([R(1), R(1), R(27)], R(3)),     # (27)^(1/3) = 3
    ]
    n, wit, und = 0, None, 0
    for lx, lam in cases:
        assert lam ** len(lx) == sp.prod(lx)     # exact geometric mean
        ly = [lam] * len(lx)
        DU = Closed(1 - parallel_F(lx, FEXP2))
        DV = Closed(1 - parallel_F(ly, FEXP2))
        # claim: X >=st Y -> check st(Y, X) i.e. S_Y <= S_X
        h, w_, u_ = cf.check("st", DV, DU)
        n += 1; und += u_
        if not h and wit is None:
            wit = w_
    return n, wit, und


def corollary_4_1():
    """homogeneous level >= arithmetic mean => Xn:n <=rh Yn:n."""
    cases = [
        ([R(1), R(2), R(6)], [R(3)] * 3),
        ([R(1), R(4), R(7)], [R(5)] * 3),
        ([R(2), R(8)], [R(6)] * 2),
    ]
    for lx, ly in cases:
        assert ly[0] >= sum(lx) / len(lx)
    return batch("rh", cases, "parallel", FEXP2)


def corollary_4_3():
    """n1=n2=1 instance of Theorem 4.4: lam1<=eta<=mu1 => X2:2 <=lr Y2:2."""
    cases = [
        ([R(2), R(3)], [R(4), R(3)]),
        ([R(1), R(2)], [R(3), R(2)]),
        ([R(2), R(5)], [R(6), R(5)]),
    ]
    return batch("lr", cases, "parallel", FEXP2)


def theorem_4_4():
    """Multiple-outlier parallel: lam1 <= eta <= mu1 => Xn:n <=lr Yn:n."""
    cases = [
        ([R(2), R(2), R(3), R(3)], [R(4), R(4), R(3), R(3)]),     # Ex 5.7 vals
        ([R(1), R(1), R(2), R(2)], [R(3), R(3), R(2), R(2)]),
        ([R(2), R(5), R(5), R(5)], [R(6), R(5), R(5), R(5)]),     # n1=1,n2=3
    ]
    return batch("lr", cases, "parallel", FEXP2)


def example_5_1():
    DU = Closed(series_S([R(2), R(3), R(5)], FWB))
    DV = Closed(series_S([R(5, 2), R(7, 2), R(6)], FWB))
    h, w_, u_ = cf.check("st", DU, DV)
    return w_ is None, w_, u_, 1


def example_5_2():
    DU = Closed(series_S([R(3), R(9, 2), R(6)], FEXP2))
    DV = Closed(series_S([R(4), R(5), R(6)], FEXP2))
    h, w_, u_ = cf.check("hr", DU, DV)
    return w_ is None, w_, u_, 1


def example_5_6():
    DU = Closed(1 - parallel_F([R(1, 2), R(5, 2), R(4)], FEXP15))
    DV = Closed(1 - parallel_F([R(1), R(3), R(5)], FEXP15))
    h, w_, u_ = cf.check("rh", DU, DV)
    return w_ is None, w_, u_, 1


def example_5_7_lr():
    """X4:4 <=lr Y4:4 for lam1=2,eta=3,mu1=4, n1=n2=2."""
    DU = Closed(1 - parallel_F([R(2), R(2), R(3), R(3)], FEXP2))
    DV = Closed(1 - parallel_F([R(4), R(4), R(3), R(3)], FEXP2))
    h, w_, u_ = cf.check("lr", DU, DV)
    return w_ is None, w_, u_, 1


def counterexample_5_1():
    """Claimed: survival functions cross (no st order either way)."""
    DU = Closed(series_S([R(11, 5), R(3), R(5)], FEXP2))
    DV = Closed(series_S([R(14, 5), R(16, 5), R(33, 10)], FEXP2))
    h1, w1, u1 = cf.check("st", DU, DV)
    h2, w2, u2 = cf.check("st", DV, DU)
    return (w1 is not None) and (w2 is not None), \
        w1 if w1 is not None else w2, u1 + u2, 2


def counterexample_5_2():
    """Claimed: X1:3 not <=hr Y1:3 (hazard rates cross)."""
    DU = Closed(series_S([R(2), R(3), R(5)], FEXP12))
    DV = Closed(series_S([R(14, 5), R(16, 5), R(17, 5)], FEXP12))
    h, w_, u_ = cf.check("hr", DU, DV)
    return w_ is not None, w_, u_, 1


def counterexample_5_4():
    """Two pairs; case1: X3:3 not <=st Y3:3; case2: X3:3 not >=st Y3:3."""
    DU1 = Closed(1 - parallel_F([R(2), R(3), R(5)], FEXP18))
    DV1 = Closed(1 - parallel_F([R(13, 5), R(16, 5), R(37, 10)], FEXP18))
    h1, w1, u1 = cf.check("st", DU1, DV1)     # X <=st Y should fail
    DU2 = Closed(1 - parallel_F([R(5, 2), R(3), R(5)], FEXP18))
    DV2 = Closed(1 - parallel_F([R(3), R(19, 5), R(22, 5)], FEXP18))
    h2, w2, u2 = cf.check("st", DV2, DU2)     # Y <=st X should fail
    return (w1 is not None) and (w2 is not None), \
        w1 if w1 is not None else w2, u1 + u2, 2


def counterexample_5_3_rh():
    """Record claims no relative rh ageing (unsupported); testable part:
    no plain rh ordering between the two parallel systems either."""
    lx = [R(2), R(2), R(6), R(6), R(6), R(6)]
    ly = [R(3), R(3), R(11, 2), R(11, 2), R(11, 2), R(11, 2)]
    DU = Closed(1 - parallel_F(lx, FEXP2))
    DV = Closed(1 - parallel_F(ly, FEXP2))
    h1, w1, u1 = cf.check("rh", DU, DV)
    h2, w2, u2 = cf.check("rh", DV, DU)
    return (w1 is not None) and (w2 is not None), \
        w1 if w1 is not None else w2, u1 + u2, 2


def remark_4_1():
    """Same instance as Counterexample 5.3: claim no lr ordering either
    way (density ratio non-monotone)."""
    lx = [R(2), R(2), R(6), R(6), R(6), R(6)]
    ly = [R(3), R(3), R(11, 2), R(11, 2), R(11, 2), R(11, 2)]
    DU = Closed(1 - parallel_F(lx, FEXP2))
    DV = Closed(1 - parallel_F(ly, FEXP2))
    h1, w1, u1 = cf.check("lr", DU, DV)
    h2, w2, u2 = cf.check("lr", DV, DU)
    return (w1 is not None) and (w2 is not None), \
        w1 if w1 is not None else w2, u1 + u2, 4


def main():
    canon = json.load(open(os.path.join(
        HERE, "..", "canonical", "doi_10.1080_02331888.2020.1722670.json")))
    results = []
    for recd in canon:
        order = recd["conclusion"]["order"]
        label = recd["claim"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        fn = {
            "Theorem 3.1": theorem_3_1,
            "Theorem 3.2": theorem_3_2,
            "Corollary 3.1": corollary_3_1,
            "Corollary 3.2": corollary_3_2,
            "Theorem 3.8": theorem_3_8,
            "Theorem 3.9": theorem_3_9,
            "Theorem 4.1": theorem_4_1,
            "Theorem 4.2": theorem_4_2,
            "Corollary 4.1": corollary_4_1,
            "Corollary 4.3": corollary_4_3,
            "Theorem 4.4": theorem_4_4,
        }.get(label)
        if fn is not None:
            n_, w, u = fn()
            results.append(rec(recd, "holds" if w is None else "refuted",
                               instances=n_, witness=w, undecided=u))
            continue
        if label == "Example 5.1":
            ok, w, u, n_ = example_5_1()
        elif label == "Example 5.2":
            ok, w, u, n_ = example_5_2()
        elif label == "Example 5.6":
            ok, w, u, n_ = example_5_6()
        elif label == "Example 5.7 — likelihood ratio part":
            ok, w, u, n_ = example_5_7_lr()
        elif label == "Example 5.7" and order == "lr":
            ok, w, u, n_ = example_5_7_lr()
        elif label.startswith("Counterexample 5.1"):
            ok, w, u, n_ = counterexample_5_1()
        elif label.startswith("Counterexample 5.2"):
            ok, w, u, n_ = counterexample_5_2()
        elif label.startswith("Counterexample 5.4"):
            ok, w, u, n_ = counterexample_5_4()
        elif label.startswith("Counterexample 5.3") and order == "rh":
            # claim is about the relative-ageing ratio r~_Y/r~_X
            # (non-monotonicity), not the plain rh order -> unsupported;
            # the 'no lr ordering' half is covered by the Remark 4.1
            # lr records which survive testing.
            results.append(rec(recd, "unsupported order"))
            continue
        elif label.startswith("Remark 4.1"):
            ok, w, u, n_ = remark_4_1()
        else:
            results.append(rec(recd, "out of harness scope"))
            continue
        results.append(rec(recd, "holds" if ok else "refuted",
                           instances=n_, witness=w, undecided=u))
    out = os.path.join(HERE, "eval_doi_10.1080_02331888.2020.1722670.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"],
              "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
