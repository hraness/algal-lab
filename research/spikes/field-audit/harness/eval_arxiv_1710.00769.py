"""Evaluation of canonical claims for arxiv:1710.00769
(location-scale families; series/parallel systems under majorization).

LS(lambda, sigma, F): S_i(t) = Fbar((t - lambda_i)/sigma_i) for t > lambda_i
(baseline hazard r(u) = f(u)/Fbar(u) of F).

Scope decisions:
  * Theorems 1-5, 16-18, Lemma 6: Archimedean-copula DEPENDENT components
    (or a copula concordance claim) -> out of harness scope.
  * Theorems 8, 9, 10, 14: order = R-hr (ageing-faster) -> unsupported order.
  * Theorem 11: printed hypotheses include 'ur(u) decreasing AND concave';
    a positive concave decreasing function on (0,inf) cannot exist
    (concave + decreasing must cross zero), so hypotheses are internally
    inconsistent -> ambiguous hypotheses.
  * Theorem 12: 'ur increasing and convex with r decreasing': impossible --
    for convex g=u r with g(0)=0, g(u)/u is nondecreasing, so r cannot
    decrease -> ambiguous hypotheses.
  * Theorem 15 (lr): pairs 'r increasing' with 'u^2 r' decreasing'; since
    u^2 r'(0) = 0, decreasing makes u^2 r' <= 0 i.e. r' <= 0 everywhere --
    inconsistent -> ambiguous hypotheses.
  * Theorems 6, 7 (hr) and 13 (hr): testable variants with consistent
    hypotheses (see code).

Grids: locations shift component supports; tests run on t > max(locations)
(bounded test; noted).
"""
import json
import os

import sympy as sp

import closedform as cf
import syscomp as sc
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))

u_ = sp.Symbol('u', positive=True)


def pareto_surv():
    """Fbar(u) = 1/(1+u):  r = 1/(1+u); ur = u/(1+u) concave increasing."""
    return 1 / (1 + u_)


def weibull32_surv():
    """Fbar(u) = exp(-(2/3) u^{3/2}): r = u^{1/2}; ur = u^{3/2} convex."""
    return sp.exp(-R(2, 3) * u_ ** R(3, 2))


def dhr_surv():
    """Fbar(u) = exp(-2 u^{1/2}): r = u^{-1/2} decreasing; u^2 r' decreasing."""
    return sp.exp(-2 * u_ ** R(1, 2))


def S_ls(Fbar_u, lam, sig):
    """Survival of LS(lam,sig,F) at variable x, valid for x > lam."""
    return Fbar_u.subs(u_, (x - R(lam)) / R(sig))


def submajorizes(a, b):
    """a <=w b: descending partial sums of a <= those of b."""
    A, B = sorted(a, reverse=True), sorted(b, reverse=True)
    return all(sum(A[:k]) <= sum(B[:k]) for k in range(1, len(A) + 1))


def supermajorizes(a, b):
    """a >=w b: ascending partial sums of a >= those of b."""
    A, B = sorted(a), sorted(b)
    return all(sum(A[:k]) >= sum(B[:k]) for k in range(1, len(A) + 1))


def majorizes(a, b):
    """a >=^m b (Marshall-Olkin): descending partials of a dominate."""
    A, B = sorted(a, reverse=True), sorted(b, reverse=True)
    return sum(A) == sum(B) and all(
        sum(A[:k]) >= sum(B[:k]) for k in range(1, len(A)))


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "arxiv_1710.00769.json")))
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

        if label == "Theorem 6":
            # variant (i): ur concave (Pareto baseline, both sides F=G);
            # (1/sigma) <=^m (1/xi) -> X1:n <=hr Y1:n.
            Fb = pareto_surv()
            # (1/sig) <=^m (1/xi): 1/xi vector majorizes 1/sig.
            insts = [([R(1), R(1, 2)], [R(1, 2), R(1, 2)],   # lam, sigma
                      [R(1), R(1, 2)], [R(1), R(1, 3)]),    # same lam, xi
                     ([R(2), R(1), R(1, 2)], [R(1, 2), R(1, 2), R(1, 2)],
                      [R(2), R(1), R(1, 2)], [R(1), R(1, 2), R(1, 3)]),
                     # E+ (ascending) reading: all vectors ascending
                     ([R(1, 2), R(1)], [R(1, 2), R(1, 2)],
                      [R(1, 2), R(1)], [R(1, 3), R(1)]),
                     ([R(1, 2), R(1), R(2)], [R(1, 2), R(1, 2), R(1, 2)],
                      [R(1, 2), R(1), R(2)], [R(1, 3), R(1, 2), R(1)])]
            for lam, sig, mu, xi in insts:
                rsig = [1 / s for s in sig]
                rxi = [1 / s for s in xi]
                assert majorizes(rxi, rsig), (rsig, rxi)
                lo = max(lam + mu) + R(1, 10 ** 6)
                hi = lo + R(30)
                SX = Closed(sc.series([S_ls(Fb, l, s)
                                       for l, s in zip(lam, sig)]), lo=lo, hi=hi)
                SY = Closed(sc.series([S_ls(Fb, l, s)
                                       for l, s in zip(mu, xi)]), lo=lo, hi=hi)
                h, w, u = cf.check("hr", SX, SY)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            out.update(status="holds" if wit is None else "refuted",
                       note="variant (i) tested: ur concave via Pareto "
                            "baseline, F=G (X<=hrY with equality); "
                            "(1/sig) <=^m (1/xi)")
        elif label == "Theorem 7":
            # variant (i): ur convex (Weibull-3/2 baseline); (1/sig) >=^m (1/xi)
            Fb = weibull32_surv()
            insts = [([R(1), R(1, 2)], [R(1), R(1, 3)],
                      [R(1), R(1, 2)], [R(1, 2), R(1, 2)]),
                     ([R(2), R(1), R(1, 2)], [R(1), R(1, 2), R(1, 3)],
                      [R(2), R(1), R(1, 2)], [R(1, 2), R(1, 2), R(1, 2)]),
                     # E+ (ascending) reading: all vectors ascending
                     ([R(1, 2), R(1)], [R(1, 3), R(1)],
                      [R(1, 2), R(1)], [R(1, 2), R(1, 2)]),
                     ([R(1, 2), R(1), R(2)], [R(1, 3), R(1, 2), R(1)],
                      [R(1, 2), R(1), R(2)], [R(1, 2), R(1, 2), R(1, 2)])]
            for lam, sig, mu, xi in insts:
                rsig = [1 / s for s in sig]
                rxi = [1 / s for s in xi]
                assert majorizes(rsig, rxi), (rsig, rxi)  # (1/sig) >=^m (1/xi)
                lo = max(lam + mu) + R(1, 10 ** 6)
                hi = lo + R(30)
                SX = Closed(sc.series([S_ls(Fb, l, s)
                                       for l, s in zip(lam, sig)]), lo=lo, hi=hi)
                SY = Closed(sc.series([S_ls(Fb, l, s)
                                       for l, s in zip(mu, xi)]), lo=lo, hi=hi)
                h, w, u = cf.check("hr", SX, SY)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            out.update(status="holds" if wit is None else "refuted",
                       note="variant (i) tested: ur convex via "
                            "Fbar=e^{-(2/3)u^1.5}; (1/sig) >=^m (1/xi)")
        elif label == "Theorem 13":
            # two consistent branches:
            #  A: r increasing & u^2 r' increasing (baseline r=sqrt(u)),
            #     lambda <=w mu
            #  B: r decreasing & u^2 r' decreasing (baseline r=u^{-1/2}),
            #     lambda >=w mu
            FbA, FbB = weibull32_surv(), dhr_surv()
            instsA = [([R(1), R(1)], [R(2), R(1)]),          # lam <=w mu
                      ([R(2), R(1)], [R(3), R(2)]),
                      ([R(1), R(1), R(1)], [R(2), R(1), R(1)])]
            instsB = [([R(2), R(1)], [R(1), R(1)]),          # lam >=w mu
                      ([R(3), R(2)], [R(2), R(1)]),
                      ([R(2), R(1), R(1)], [R(1), R(1), R(1)])]
            for lam, mu in instsA:
                assert submajorizes(lam, mu)
                lo = max(lam + mu) + R(1, 10 ** 6)
                hi = lo + R(30)
                SX = Closed(sc.series([S_ls(FbA, l, 1) for l in lam]), lo=lo, hi=hi)
                SY = Closed(sc.series([S_ls(FbA, m, 1) for m in mu]), lo=lo, hi=hi)
                h, w, u = cf.check("hr", SX, SY)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            for lam, mu in instsB:
                assert supermajorizes(lam, mu)
                lo = max(lam + mu) + R(1, 10 ** 6)
                hi = lo + R(30)
                SX = Closed(sc.series([S_ls(FbB, l, 1) for l in lam]), lo=lo, hi=hi)
                SY = Closed(sc.series([S_ls(FbB, m, 1) for m in mu]), lo=lo, hi=hi)
                h, w, u = cf.check("hr", SX, SY)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            out.update(status="holds" if wit is None else "refuted",
                       note="consistent branches tested: (IHR,u2r' inc,"
                            " lam<=w mu) and (DHR,u2r' dec, lam>=w mu); "
                            "grid restricted to t > max locations")
        elif label in ("Theorem 11", "Theorem 12", "Theorem 15"):
            out["status"] = "ambiguous hypotheses"
            out["note"] = {
                "Theorem 11": "ur(u) 'decreasing and concave' impossible for "
                              "a positive function on (0,inf)",
                "Theorem 12": "ur increasing+convex with r decreasing "
                              "impossible (convex g=u*r through the origin "
                              "has g/u nondecreasing)",
                "Theorem 15": "'r increasing' paired with 'u^2 r' "
                              "decreasing' inconsistent: u^2 r'(0)=0 "
                              "decreasing forces r'<=0",
            }[label]
        elif label == "Lemma 6 (Li and Fang)":
            out["status"] = "out of harness scope"
            out["note"] = "pointwise copula concordance order"
        else:
            out["status"] = "out of harness scope"
            out["note"] = "Archimedean copula (dependent components)"
        out.update(instances=n, undecided_points=und)
        if wit is not None and out["witness"] is None:
            out["witness"] = str(wit)
        results.append(out)
    dest = os.path.join(HERE, "eval_arxiv_1710.00769.result.json")
    json.dump(results, open(dest, "w"), indent=1, default=str)
    print(json.dumps(results, indent=1, default=str))


if __name__ == "__main__":
    main()
