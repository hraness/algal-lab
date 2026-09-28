"""Evaluation of canonical claims for doi:10.3390/fractalfract9060388
(extropy paper; stochastic-order applications).

Families needed:
  Gamma(a, rate 1):  S(x) = e^{-x} (1 + x + ... + x^{a-1}/(a-1)!) for integer
     shape a; for general a, upper incomplete gamma -- use integer shapes.
     S(x) = e^{-x} sum_{k=0}^{a-1} x^k/k!  (Erlang)
  Weibull(a):        S(x) = exp(-x^a)
  Uniform(0,b):      S(x) = 1 - x/b on [0,b]

Claims:
  Corollary 1 parts 1-2: 'for general st-ordered marginals, order stats /
     record values inherit st' -- quantification over all marginals; the
     kth-order-statistic part is instantiated with concrete families
     (exponential vs st-larger exponential, uniform), record values are a
     dependent/non-elementary composition -> partly tested, partly scope.
  Remark 6 gamma:  a1* < a2* => Y(a1*) <=lr Y(a2*) and <=st.
  Remark 6 Weibull: disp part unsupported; st part a1 < a2 =>
     Y(a1) >=st Y(a2)  (suspect: unit-scale Weibull survivals cross at x=1).
  Example 3: uniform(0,b1) <=st uniform(0,b2) for b1 <= b2 -- supports differ;
     compare on the common convention S1(x) <= S2(x) for all x>0.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_gamma_int(a):
    """Erlang/Gamma(integer a, rate 1) survival."""
    a = int(a)
    return sp.exp(-x) * sum(x ** k / sp.factorial(k) for k in range(a))


def S_weibull(a):
    return sp.exp(-x ** R(a))


def S_uniform(b):
    return 1 - x / R(b)


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "doi_10.3390_fractalfract9060388.json")))
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
        if label == "Corollary 1, part 1":
            # st is preserved under order statistics: instantiate with
            # Exp(1) <=st Exp(1/2) (S_e1 <= S_e1/2) and check kth stats.
            for n_, k_ in [(3, 1), (3, 2), (3, 3), (5, 3)]:
                SXc = [sp.exp(-x)] * n_          # Exp(1)
                SYc = [sp.exp(-x / 2)] * n_      # Exp(1/2), stoch. larger
                F = lambda Ss, kk, nn: 1 - sum(  # P(X_{k:n} > x)
                    sp.binomial(nn, j) * (1 - Ss) ** j * Ss ** (nn - j)
                    for j in range(kk, nn + 1))
                import syscomp as sc
                Sx = sc.order_stat(SXc, k_, n_)
                Sy = sc.order_stat(SYc, k_, n_)
                h, w, u = cf.check("st", Closed(Sx), Closed(Sy))
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            out.update(status="holds" if wit is None else "refuted")
        elif label == "Corollary 1, part 2":
            out["status"] = "out of harness scope"
            out["note"] = ("record values (dependent composition, not a "
                           "product/mixture of independent survivals)")
        elif label in ("Remark 6 (gamma example, lr part)",
                       "Remark 6 (gamma family)"):
            for a1, a2 in [(1, 2), (1, 4), (2, 3), (2, 5)]:
                X_ = Closed(S_gamma_int(a1))
                Y_ = Closed(S_gamma_int(a2))
                h, w, u = cf.check("lr", X_, Y_)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            out.update(status="holds" if wit is None else "refuted")
        elif label == "Remark 6 (gamma example, st part)":
            for a1, a2 in [(1, 2), (1, 4), (2, 3), (2, 5)]:
                X_ = Closed(S_gamma_int(a1))
                Y_ = Closed(S_gamma_int(a2))
                h, w, u = cf.check("st", X_, Y_)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            out.update(status="holds" if wit is None else "refuted")
        elif label == "Remark 6 (Weibull example, st part)":
            # claim Y(a1) >=st Y(a2), a1 < a2  <=> check("st", Y(a2), Y(a1))
            for a1, a2 in [(1, 2), (1, 3), (2, 3), (R(1, 2), R(3, 2))]:
                X_ = Closed(S_weibull(a2))   # larger shape
                Y_ = Closed(S_weibull(a1))   # smaller shape; claim: Y_ >=st X_
                h, w, u = cf.check("st", X_, Y_)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            out.update(status="holds" if wit is None else "refuted")
        elif label == "Example 3":
            # Uniform(0,b1) <=st Uniform(0,b2), b1 <= b2.
            # closedform requires shared support: compare on (0, b1] with the
            # uniform(0,b2) expression (valid there since x/b2 < 1).
            for b1, b2 in [(1, 2), (R(1, 2), R(3))]:
                X_ = Closed(S_uniform(b1), lo=0, hi=b1)
                Y_ = Closed(S_uniform(b2), lo=0, hi=b1)
                h, w, u = cf.check("st", X_, Y_)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            out.update(status="holds" if wit is None else "refuted",
                       note="supports differ; compared on (0,b1] (on "
                            "(b1,b2] S_X=0 <= S_Y trivially)")
        else:
            out["status"] = "out of harness scope"
        out.update(instances=n, undecided_points=und,
                   witness=None if wit is None else str(wit))
        results.append(out)
    dest = os.path.join(HERE, "eval_doi_10.3390_fractalfract9060388.result.json")
    json.dump(results, open(dest, "w"), indent=1)
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
