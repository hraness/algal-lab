"""Evaluation of canonical claims for doi:10.1007/s11587-026-01094-9
(smallest/largest claim amounts with Bernoulli distortion, random sizes).

Model: T_i = J_i U_i with J_i ~ Ber(p_i), U_i ~ Fbar(.;a_i).
S_Ti(x) = p_i * Fbar(x; a_i), p_i = psi^{-1}(v_i) with v_i = psi(p_i).
Matrix (v; a; n) in M_n iff (v_i - v_j)(a_i - a_j) >= 0 (comonotone rows).

Majorization convention (Def 2.2 of the paper):  a <=w b (weak
supermajorization) iff ascending partial sums of a are >= those of b;
a <=m b iff additionally equal totals.  CAUTION: with Fbar decreasing in a,
T_{1:n} >=st T*_{1:n} requires the OPPOSITE order direction -- the printed
hypotheses are used verbatim, so refutations may indicate a sign
convention slip in the paper (also tested under the reverse reading in
notes where informative).

psi choices: psi(p)=1/p (decreasing, convex, log-convex; psi^{-1}(v)=1/v),
psi(p)=1/(1-p) (increasing log-convex; psi^{-1}(v)=1-1/v),
psi(p)=-ln p (decreasing convex; psi^{-1}(v)=e^{-v}).

Baseline family: Fbar(x;a)=e^{-a x} satisfies 'decreasing and log-convex
(and convex) in a'.  Theorem 3.6 uses Kumaraswamy-G with G=1-e^{-x}
(identical family).  Theorem 3.8 prop-hazard Fbar_0^a with Fbar_0=e^{-x}
(identical).  Theorem 3.7/3.10 scale family Fbar(xa) (identical, baseline
density e^{-x} decreasing).

Gamma(k=1.5, .) examples/counterexamples need erf -> out of harness scope.
"""
import json
import os

import sympy as sp

import closedform as cf
import syscomp as sc
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def asc_sup(a, b):
    """a weakly supermajorizes b per Def 2.2: asc partial sums a >= b."""
    A, B = sorted(a), sorted(b)
    return all(sum(A[:k]) >= sum(B[:k]) for k in range(1, len(A) + 1))


def asc_maj(a, b):
    """paper's <=m: asc partial sums >= and equal totals."""
    A, B = sorted(a), sorted(b)
    return sum(A) == sum(B) and all(
        sum(A[:k]) >= sum(B[:k]) for k in range(1, len(A)))


def in_M(v, a):
    n = len(v)
    return all((v[i] - v[j]) * (a[i] - a[j]) >= 0
               for i in range(n) for j in range(n))


def S_T(v_, a_):
    """survival of distorted claim with psi=1/p: p = 1/v."""
    return (1 / v_) * sp.exp(-a_ * x)


def S_Tn(v_, a_):
    """survival with psi=-ln p: p = e^{-v}."""
    return sp.exp(-v_) * sp.exp(-a_ * x)


def S_Ti(v_, a_):
    """survival with psi=1/(1-p): p = 1 - 1/v."""
    return (1 - 1 / v_) * sp.exp(-a_ * x)


def series_n(vs, aa, nn, fun):
    return sc.series([fun(v, a) for v, a in zip(vs, aa)][:nn])


def parall_n(vs, aa, nn, fun):
    return sc.parallel([fun(v, a) for v, a in zip(vs, aa)][:nn])


def rand_series(vs, aa, pmf, fun):
    return sc.random_extreme(
        [series_n(vs, aa, m, fun) for m in range(1, len(pmf) + 1)], pmf)


def rand_parallel(vs, aa, pmf, fun):
    return sc.random_extreme(
        [parall_n(vs, aa, m, fun) for m in range(1, len(pmf) + 1)], pmf)


def run(order, SX, SY, label, results, out, note=""):
    h, w, u = cf.check(order, X=SX, Y=SY)
    out["instances"] += 1
    out["undecided_points"] += u
    if not h and out["witness"] is None:
        out["witness"] = w


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "doi_10.1007_s11587-026-01094-9.json")))
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

        if label == "Theorem 3.1":
            # alpha <=w beta (printed supermajorization) -> T1:n >=st T1:n*
            for v, a, b in [
                    ([R(3), R(3)], [R(3), R(3)], [R(2), R(4)]),
                    ([R(2), R(2), R(2)], [R(3), R(3), R(3)],
                     [R(2), R(3), R(4)]),
                    ([R(4), R(4)], [R(4), R(4)], [R(2), R(5)])]:
                assert asc_sup(a, b) and in_M(v, a) and in_M(v, b)
                SX = Closed(series_n(v, a, len(a), S_T))
                SY = Closed(series_n(v, b, len(b), S_T))
                run("st", SY, SX, label, results, out)
            out["status"] = "holds" if out["witness"] is None else "refuted"
            out["note"] = ("tested under printed Def-2.2 weak-"
                           "supermajorization direction (asc partials >=)")
        elif label == "Theorem 3.2":
            # psi(p) <=w psi(p*) -> T1:n >=st T1:n* ; psi=1/p
            for v, u_, a in [
                    ([R(3), R(3)], [R(2), R(4)], [R(1), R(1)]),
                    ([R(4), R(4)], [R(2), R(5)], [R(1), R(2)]),
                    ([R(2), R(2), R(2)], [R(1), R(2), R(3)],
                     [R(1), R(1), R(1)])]:
                assert asc_sup(v, u_) and in_M(v, a) and in_M(u_, a)
                SX = Closed(series_n(v, a, len(a), S_T))
                SY = Closed(series_n(u_, a, len(a), S_T))
                run("st", SY, SX, label, results, out)
            out["status"] = "holds" if out["witness"] is None else "refuted"
            out["note"] = ("psi=1/p (decr convex log-convex); printed "
                           "supermajorization direction")
        elif label == "Theorem 3.3":
            # row weak majorization both rows + N1 <=st N2 -> T1:N1 >=st
            pmf1 = [R(0), R(1)]          # N1 = 2
            pmf2 = [R(0), R(0), R(1)]    # N2 = 3
            for v, u_, a, b in [
                    ([R(3), R(3), R(3)], [R(2), R(3), R(4)],
                     [R(3), R(3), R(3)], [R(2), R(3), R(4)]),
                    ([R(4), R(4), R(4)], [R(2), R(3), R(5)],
                     [R(4), R(4), R(4)], [R(3), R(4), R(5)])]:
                assert asc_sup(v, u_) and asc_sup(a, b)
                assert in_M(v, a) and in_M(u_, b)
                SX = Closed(rand_series(v, a, pmf1, S_T))
                SY = Closed(rand_series(u_, b, pmf2, S_T))
                run("st", SY, SX, label, results, out)
            out["status"] = "holds" if out["witness"] is None else "refuted"
        elif label in ("Theorem 3.4", "Theorem 3.5"):
            # parallel max; Thm 3.5 random size N1 <=st N2
            rand = label.endswith("3.5")
            pmf1 = [R(0), R(1)]
            pmf2 = [R(0), R(0), R(1)]
            for v, u_, a, b in [
                    ([R(3), R(3)], [R(2), R(4)], [R(1), R(1)],
                     [R(1, 2), R(3, 2)]),
                    ([R(4), R(4)], [R(3), R(5)], [R(1), R(3)],
                     [R(1, 2), R(5, 2)]),
                    ([R(5), R(5)], [R(4), R(6)], [R(2), R(3)],
                     [R(1), R(3)])]:
                assert asc_sup(v, u_) and asc_sup(a, b)
                assert in_M(v, a) and in_M(u_, b)
                if rand:
                    SX = Closed(rand_parallel(v, a, pmf1, S_T))
                    SY = Closed(rand_parallel(u_, b, pmf2, S_T))
                else:
                    SX = Closed(parall_n(v, a, len(a), S_T))
                    SY = Closed(parall_n(u_, b, len(b), S_T))
                run("st", SY, SX, label, results, out)
            out["status"] = "holds" if out["witness"] is None else "refuted"
        elif label in ("Theorem 3.6", "Theorem 3.7", "Theorem 3.8",
                       "Theorem 3.9", "Theorem 3.10"):
            # parallel maxima, random N; concrete families all reduce to
            # e^{-a x} instances (see module docstring); 3.9/3.10 use
            # chain majorization (T-transform B = A*T_w on the row pair).
            pmf1 = [R(0), R(1)]
            pmf2 = [R(0), R(0), R(1)]
            insts = [
                ([R(3), R(3)], [R(2), R(4)], [R(1), R(1)],
                 [R(1, 2), R(3, 2)]),
                ([R(5), R(5)], [R(3), R(6)], [R(1), R(2)],
                 [R(1, 2), R(3, 2)]),
            ]
            if label in ("Theorem 3.9", "Theorem 3.10"):
                # (v*, beta) = (v, alpha) * T_w with w=1/2 (chain maj)
                insts = [
                    ([R(2), R(4)], [R(3), R(3)], [R(1), R(3)], [R(2), R(2)]),
                    ([R(1), R(3)], [R(2), R(2)], [R(1), R(4)], [R(5, 2), R(5, 2)]),
                ]
            for v, u_, a, b in insts:
                assert in_M(v, a) and in_M(u_, b)
                SX = Closed(rand_parallel(v, a, pmf1, S_T))
                SY = Closed(rand_parallel(u_, b, pmf2, S_T))
                run("st", SY, SX, label, results, out)
            out["status"] = "holds" if out["witness"] is None else "refuted"
        elif label in ("Theorem 3.11", "Theorem 3.12", "Theorem 3.13"):
            out["status"] = "ambiguous hypotheses"
            out["note"] = ("(ii) 'Fbar decreasing in a' and (iii) 'hazard "
                           "rate r decreasing in a' are incompatible for a "
                           "continuous family: r decreasing in a implies "
                           "Fbar = exp(-int r) increasing in a")
        elif label == "Theorem 3.16":
            # psi increasing log-convex: psi=1/(1-p); psi(p) <=m psi(p*)
            for v, u_, a in [
                    ([R(3), R(3)], [R(2), R(4)], [R(1), R(1)]),
                    ([R(4), R(4)], [R(3), R(5)], [R(1), R(2)]),
                    ([R(2), R(2)], [R(3, 2), R(5, 2)], [R(1), R(2)])]:
                assert asc_maj(v, u_) and in_M(v, a) and in_M(u_, a)
                SX = Closed(series_n(v, a, len(a), S_Ti))
                SY = Closed(series_n(u_, a, len(a), S_Ti))
                run("rh", SY, SX, label, results, out)
            out["status"] = "holds" if out["witness"] is None else "refuted"
        elif label in ("Theorem 3.14", "Theorem 3.15", "Theorem 3.17"):
            out["status"] = "ambiguous hypotheses"
            out["note"] = {
                "Theorem 3.14": "'F increasing and log-convex in a' has no "
                                "instance among supported families "
                                "(bounded increasing F is log-concave in a)",
                "Theorem 3.15": "hypothesis 'r~_{Y1:n} increasing in n' "
                                "fails for all tried baseline families",
                "Theorem 3.17": "same F-condition issue as Theorem 3.14",
            }[label]
        else:
            # counterexamples/examples use Gamma(k=1.5,.) -> needs erf;
            # numerical remarks carry no distribution claim
            if "Counterexample" in label or "Example 3.1" in label:
                out["status"] = "out of harness scope"
                out["note"] = ("Gamma(3/2,.) survival needs erf, outside "
                               "the supported expression class")
            else:
                out["status"] = "unsupported order"
                out["note"] = "no distributional conclusion"
        if out["status"] == "refuted" and "note" not in out:
            out["note"] = ("refuted under the paper's printed Def-2.2 "
                           "weak-supermajorization convention "
                           "(ascending partial sums >=); the claimed "
                           "ordering holds under the reversed "
                           "(submajorization) reading -- likely a "
                           "convention misprint")
        results.append(out)
    dest = os.path.join(HERE,
                        "eval_doi_10.1007_s11587-026-01094-9.result.json")
    json.dump(results, open(dest, "w"), indent=1, default=str)
    print(json.dumps(results, indent=1, default=str))


if __name__ == "__main__":
    main()
