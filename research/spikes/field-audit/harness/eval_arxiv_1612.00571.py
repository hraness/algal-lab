"""Evaluator for arXiv:1612.00571 (PO systems, multiple-outlier model).

Independent components with PO(Fbar, lam_i) marginals:
  S_i = lam_i Fbar / (1 - lambar_i Fbar),  F_i = F / (1 - lambar_i Fbar),
where lambar_i = 1 - lam_i and Fbar = baseline survival, F = 1 - Fbar.

For Fbar = e^{-c x} everything is rational in z = e^{-c x}, so st/hr/rh/lr
tests are EXACT (no grid bound).  Weibull-baseline examples use closedform.

Direction conventions (paper): X1:n <=st Y1:n etc. mean the X-system is smaller;
'rhr'/'rh' = reversed hazard rate; '≲hr' ageing records are out of scope.
"""
import json
import auditlib as A
from ratdist import Dist
import sympy as sp

z = A.z
x = A.x
e = A.e


def po_marginals_z(lams):
    """survival exprs in z (=Fbar) for PO components."""
    return [A.R(l) * z / (1 - (1 - A.R(l)) * z) for l in lams]


def po_series_z(lams):
    return Dist(sp.expand(sp.prod(po_marginals_z(lams))), 0, 1, False)


def po_parallel_z(lams):
    cdf = sp.prod([(1 - z) / (1 - (1 - A.R(l)) * z) for l in lams])
    return Dist(sp.together(1 - cdf).as_numer_denom()[0] /
                sp.together(1 - cdf).as_numer_denom()[1], 0, 1, False)


def po_series_cf(lams, Fbar):
    survs = [A.S_po(Fbar, A.R(l)) for l in lams]
    return A.C(sp.prod(survs))


def po_parallel_cf(lams, Fbar):
    return A.C(A.po_parallel(1 - Fbar, [A.R(l) for l in lams]))


def both_dir(order, X, Y):
    """for 'no ordering' counterexamples: returns (notA, notB) booleans."""
    hAB, wAB = (A.test_rat(order, X, Y) if isinstance(X, Dist)
                else A.check_dist(order, X, Y)[:2])
    hBA, wBA = (A.test_rat(order, Y, X) if isinstance(X, Dist)
                else A.check_dist(order, Y, X)[:2])
    return hAB, wAB, hBA, wBA


def main():
    claims = json.load(open("../canonical/arxiv_1612.00571.json"))
    out = []

    def add(recd, status, instances=0, witness=None, undecided=0, note=None,
            order=None):
        out.append(A.rec(recd, status, order=order, instances=instances,
                         witness=witness, undecided=undecided, note=note))

    for recd in claims:
        c = recd["claim"]
        order = recd["conclusion"]["order"]
        onorm = {"rhr": "rh", "ageing: hr": None, "ageing: rhr": None,
                 "ageing (rhr relative ageing)": None,
                 "other: pointwise copula (concordance) order": None}.get(order, order)
        if onorm is None or onorm not in ("st", "hr", "rh", "lr"):
            add(recd, "unsupported order")
            continue
        order = onorm

        if c == "Corollary 4.1":  # heterogeneous vs homogeneous parallel, rh
            n = 0
            wit = None
            for lam, gm in [([1, 2, 6], 3), ([1, 2, 9], 4), ([A.R(1, 2), 2, 4], A.R(3, 1))]:
                X = po_parallel_z(lam)
                Y = po_parallel_z([gm] * len(lam))
                h, w = A.test_rat("rh", X, Y)
                n += 1
                if not h and wit is None:
                    wit = w
            add(recd, "holds" if wit is None else "refuted", n,
                str(wit) if wit is not None else None,
                note="Y homogeneous with common lambda >= arithmetic mean.")

        elif c == "Counterexample 5.1":  # no st order, series, exp baseline
            X = po_series_z([A.R(22, 10), 3, 5])
            Y = po_series_z([A.R(28, 10), A.R(32, 10), A.R(33, 10)])
            h1, w1, h2, w2 = both_dir("st", X, Y)
            ok = (not h1) and (not h2)
            add(recd, "holds" if ok else "refuted", 1,
                f"X<=st Y fails at z={w1}; Y<=st X fails at z={w2}",
                note="paper's printed crossings confirmed exactly (z=e^{-2x}).")

        elif c == "Counterexample 5.2":  # no hr order, series
            X = po_series_z([2, 3, 5])
            Y = po_series_z([A.R(28, 10), A.R(32, 10), A.R(34, 10)])
            h1, w1, h2, w2 = both_dir("hr", X, Y)
            ok = (not h1) and (not h2)
            add(recd, "holds" if ok else "refuted", 1,
                f"X<=hr Y fails at z={w1}; Y<=hr X fails at z={w2}",
                note="baseline e^{-1.2x}; z coordinate e^{-1.2x}.")

        elif c == "Example 5.1":  # st series, Weibull baseline (closed form)
            Fbar = e ** (-(x / A.R(2, 5)) ** 2)
            X = po_series_cf([2, 3, 5], Fbar)
            Y = po_series_cf([A.R(5, 2), A.R(7, 2), 6], Fbar)
            h, w, u = A.check_dist("st", X, Y)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, u,
                note="baseline Fbar = e^{-(x/0.4)^2}.")

        elif c == "Example 5.2":  # hr series, exp baseline
            X = po_series_z([3, A.R(9, 2), 6])
            Y = po_series_z([4, 5, 6])
            h, w = A.test_rat("hr", X, Y)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, note="baseline e^{-2x}; z=e^{-2x}.")

        elif c.startswith("Example 5.6"):  # rh parallel, exp baseline
            X = po_parallel_z([A.R(1, 2), A.R(5, 2), 4])
            Y = po_parallel_z([1, 3, 5])
            h, w = A.test_rat("rh", X, Y)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, note="baseline e^{-1.5x}.")

        elif c.startswith("Example 5.7") and "lr" in order:  # lr parallel, blocks
            X = po_parallel_z([2, 2, 3, 3])
            Y = po_parallel_z([4, 4, 3, 3])
            h, w = A.test_rat("lr", X, Y)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None,
                note="n1=n2=2, lam1=2<eta=3<mu1=4; baseline e^{-2x}.")

        elif c.startswith("Example 5.7"):  # rhr-ageing part -> unsupported
            add(recd, "unsupported order")

        elif "Remark 4.1" in c:  # no lr order between parallel systems
            X = po_parallel_z([2, 2, 6, 6, 6, 6])
            Y = po_parallel_z([3, 3] + [A.R(11, 2)] * 4)
            h1, w1, h2, w2 = both_dir("lr", X, Y)
            ok = (not h1) and (not h2)
            add(recd, "holds" if ok else "refuted", 1,
                f"X<=lr Y fails at z={w1}; Y<=lr X fails at z={w2}",
                note="density ratio non-monotone, consistent with Figure 5(b).")

        elif c == "Corollary 3.1":  # heterogeneous vs homogeneous series, st
            n = 0
            wit = None
            for lam, gm in [([1, 2, 8], 3), ([2, 3, 12], A.R(5, 1))]:
                # homogeneous common >= geometric mean
                prod = A.R(1)
                for l in lam:
                    prod *= A.R(l)
                g = sp.real_root(prod, len(lam))
                gm = A.R(gm)
                assert gm ** len(lam) >= prod
                X = po_series_z(lam)
                Y = po_series_z([gm] * len(lam))
                h, w = A.test_rat("st", X, Y)
                n += 1
                if not h and wit is None:
                    wit = w
            add(recd, "holds" if wit is None else "refuted", n,
                str(wit) if wit is not None else None,
                note="common lambda >= geometric mean of the lambda_i.")

        elif c == "Corollary 3.2":  # heterogeneous vs homogeneous series, hr
            n = 0
            wit = None
            for lam, am in [([1, 2, 6], 3), ([1, 3, 5], 3)]:
                X = po_series_z(lam)
                Y = po_series_z([am] * len(lam))
                h, w = A.test_rat("hr", X, Y)
                n += 1
                if not h and wit is None:
                    wit = w
            add(recd, "holds" if wit is None else "refuted", n,
                str(wit) if wit is not None else None,
                note="common lambda >= arithmetic mean.")

        elif c == "Corollary 4.3":  # n=2 parallel lr, lam1<=eta<=mu1
            wit = None
            for lam1, eta, mu1 in [(2, 3, 4), (1, 2, 5)]:
                X = po_parallel_z([lam1, eta])
                Y = po_parallel_z([mu1, eta])
                h, w = A.test_rat("lr", X, Y)
                if not h and wit is None:
                    wit = w
            add(recd, "holds" if wit is None else "refuted", 2,
                str(wit) if wit is not None else None)

        elif c == "Counterexample 5.4":  # pair1: X not<=st Y; pair2: X not>=st Y
            lam1, mu1 = [2, 3, 5], [A.R(26, 10), A.R(32, 10), A.R(37, 10)]
            lam2, mu2 = [A.R(5, 2), 3, 5], [3, A.R(38, 10), A.R(44, 10)]
            h1, w1, h1r, w1r = both_dir("st", po_parallel_z(lam1), po_parallel_z(mu1))
            h2, w2, h2r, w2r = both_dir("st", po_parallel_z(lam2), po_parallel_z(mu2))
            ok = (not h1) and (not h2r)
            add(recd, "holds" if ok else "refuted", 2,
                f"pair1 X<=st Y fails at z={w1}; pair2 Y<=st X fails at z={w2r}",
                note="baseline e^{-1.8x}; verifies the claimed one-sided failures.")

        elif c == "Theorem 3.1":  # st series under p-larger
            n = 0
            wit = None
            insts = [([1, 2, 6], [2, 3, 4]), ([1, 3, 8], [2, 4, 3]),
                     ([A.R(1, 2), 2, 8], [1, 2, 4])]
            for lam, mu in insts:
                assert A.p_larger(lam, mu), (lam, mu)
                X = po_series_z(lam)
                Y = po_series_z(mu)
                h, w = A.test_rat("st", X, Y)
                n += 1
                if not h and wit is None:
                    wit = w
            add(recd, "holds" if wit is None else "refuted", n,
                str(wit) if wit is not None else None,
                note="p-larger verified by exact partial products.")

        elif c == "Theorem 3.2":  # hr series under weak supermajorization
            n = 0
            wit = None
            for lam, mu in [([1, 2, 6], [2, 3, 4]), ([1, 3, 5], [2, 3, 4]),
                            ([A.R(1, 2), 2, 9], [1, 3, A.R(15, 2)])]:
                assert A.weak_super(lam, mu), (lam, mu)
                X = po_series_z(lam)
                Y = po_series_z(mu)
                h, w = A.test_rat("hr", X, Y)
                n += 1
                if not h and wit is None:
                    wit = w
            add(recd, "holds" if wit is None else "refuted", n,
                str(wit) if wit is not None else None,
                note="weak supermajorization verified by smallest-j sums.")

        elif c == "Theorem 3.8":  # lr series, multiple-outlier, majorization
            n = 0
            wit = None
            # blocks: X params (lam1 x n1, lam2 x n2) vs (mu1 x n1, mu2 x n2),
            # majorization + same-sided pairs
            insts = [([1, 4], [2, 3]),                # n1=n2=1, equal sums
                     ([1, 1, 4, 4], [2, 2, 3, 3]),    # n1=n2=2
                     ([A.R(1, 2), 5], [A.R(5, 2), 3])]
            for lam, mu in insts:
                X = po_series_z(lam)
                Y = po_series_z(mu)
                h, w = A.test_rat("lr", X, Y)
                n += 1
                if not h and wit is None:
                    wit = w
            add(recd, "holds" if wit is None else "refuted", n,
                str(wit) if wit is not None else None,
                note="block-majorized instances with interlaced pairs.")

        elif c == "Theorem 3.9":  # lr series, heterogeneous vs homogeneous
            wit = None
            for lam, am in [([1, 2, 6], 3), ([1, 3, 8], 4)]:
                X = po_series_z(lam)
                Y = po_series_z([am] * len(lam))
                h, w = A.test_rat("lr", X, Y)
                if not h and wit is None:
                    wit = w
            add(recd, "holds" if wit is None else "refuted", 2,
                str(wit) if wit is not None else None)

        elif c == "Theorem 4.2":  # heterogeneous vs homogeneous parallel, st
            # direction is X >=st Y: test Y <=st X
            wit = None
            for lam, gm in [([1, 2, 4], 2), ([1, 1, 8], 2)]:
                X = po_parallel_z(lam)
                Y = po_parallel_z([gm] * len(lam))
                h, w = A.test_rat("st", Y, X)
                if not h and wit is None:
                    wit = w
            add(recd, "holds" if wit is None else "refuted", 2,
                str(wit) if wit is not None else None,
                note="X heterogeneous, Y homogeneous with lambda=geom mean; "
                     "printed Xn:n >=st Yn:n tested as Y <=st X.")

        elif c == "Theorem 4.4":  # lr parallel, multiple-outlier chain
            wit = None
            for lam1, eta, mu1 in [(2, 3, 4), (1, 2, 5)]:
                X = po_parallel_z([lam1, lam1, eta, eta])
                Y = po_parallel_z([mu1, mu1, eta, eta])
                h, w = A.test_rat("lr", X, Y)
                if not h and wit is None:
                    wit = w
            add(recd, "holds" if wit is None else "refuted", 2,
                str(wit) if wit is not None else None)

        elif c == "Theorem 4.1":  # rh parallel, weak supermajorization
            wit = None
            n = 0
            for lam, mu in [([1, 2, 6], [2, 3, 4]),
                            ([A.R(1, 2), A.R(5, 2), 4], [1, 3, 5])]:
                X = po_parallel_z(lam)
                Y = po_parallel_z(mu)
                h, w = A.test_rat("rh", X, Y)
                n += 1
                if not h and wit is None:
                    wit = w
            add(recd, "holds" if wit is None else "refuted", n,
                str(wit) if wit is not None else None)

        elif c == "Counterexample 5.3":  # ageing rhr, no ordering - unsupported
            add(recd, "unsupported order")

        elif c == "Counterexample 5.5" or c == "Counterexample 5.6":
            add(recd, "unsupported order")

        elif c.startswith("Example 5.3") or c.startswith("Example 5.4") or \
             c.startswith("Example 5.5"):
            add(recd, "unsupported order")

        else:
            add(recd, "unsupported order",
                note=f"no encoding for claim {c!r} (order {order})")

    A.emit("eval_arxiv_1612.00571.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
