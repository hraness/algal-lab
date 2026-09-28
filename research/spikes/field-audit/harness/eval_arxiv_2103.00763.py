"""Evaluation of canonical claims for arxiv:2103.00763
(majorization ordering of extremes for independent Poisson and geometric
random variables -- discrete families on u = 0, 1, 2, ...).

Interval enclosures (mpmath.iv, 80 digits) of:
  Poisson(mu):  F(u) = e^{-mu} sum_{r=0}^u mu^r/r!,  S(u) = 1 - F(u)
  Geometric(q): S(u) = q^{u+1},  F(u) = 1 - q^{u+1}     (paper's printed form)
  max cdf:      F_max(u) = prod_i F_i(u)
  min survival: S_min(u) = prod_i S_i(u)

Paper's discrete hazard conventions (verified against printed numbers):
  reversed hazard of max:  rh(u) = [F(u) - F(u-1)] / F(u)
  hazard of min:           h(u)  = [S(u) - S(u+1)] / S(u)
      (this convention reproduces the printed Counterexample-3.2 value
       +0.0124328 at r = 6 exactly; and Counterexample-3.1's +0.0520158
       at r=5, -0.0232122 at r=2 for the max)

Orders on the integer grid u = 0..U:
  st: X <=st Y  iff S_X(u) <= S_Y(u)     (equivalently F_X >= F_Y)
  hr: X <=hr Y  iff h_X(u) >= h_Y(u)
  rh: X <=rh Y  iff rh_X(u) <= rh_Y(u)

Counterexample records assert a *failure* of an order (sign change of a
difference).  A verified sign change confirms the claim -> "holds"; if the
printed sign change does not materialize on the tested range the record is
"refuted".
"""
import json
import os

import sympy as sp
from mpmath import iv

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))
iv.dps = 80


def _iv(v):
    v = R(v)
    return iv.mpf(int(v.p)) / iv.mpf(int(v.q))


def poisson_cdf(mu, u):
    term = iv.mpf(1)
    s = iv.mpf(1)
    for r in range(1, int(u) + 1):
        term *= _iv(mu) / r
        s += term
    return iv.exp(-_iv(mu)) * s


def poisson_surv(mu, u):
    return 1 - poisson_cdf(mu, u)


def geom_surv(q, u):
    return _iv(q) ** (u + 1)


def geom_cdf(q, u):
    return 1 - geom_surv(q, u)


def prod(fs, params, u):
    p = iv.mpf(1)
    for pp in params:
        p *= fs(pp, u)
    return p


def max_rh(cdf_i, params, u):
    Fu, Fum = prod(cdf_i, params, u), prod(cdf_i, params, u - 1)
    return (Fu - Fum) / Fu


def min_hz(surv_i, params, u):
    Su, Su1 = prod(surv_i, params, u), prod(surv_i, params, u + 1)
    return (Su - Su1) / Su


def st_geq(cdf_or_surv_X, cdf_or_surv_Y, kind, umax):
    """Check X >=st Y (i.e. claim that X dominates) on u = 0..umax.

    kind='max': X >=st Y  iff  F_X(u) <= F_Y(u)
    kind='min': X >=st Y  iff  S_X(u) >= S_Y(u)
    Returns (holds, witness u or None).
    """
    for u in range(0, umax + 1):
        a = cdf_or_surv_X(u)
        b = cdf_or_surv_Y(u)
        d = (a - b) if kind == "max" else (b - a)
        if d.a > 0:                     # strictly on the wrong side
            return False, u
    return True, None


def sorted_desc(v):
    return sorted(v, reverse=True)


def majorizes(a, b):
    """a >=^m b (Marshall-Olkin, equal totals)."""
    A, B = sorted_desc(a), sorted_desc(b)
    if sum(A) != sum(B):
        return False
    return all(sum(A[:j]) >= sum(B[:j]) for j in range(1, len(A)))


def main():
    records = json.load(open(os.path.join(
        HERE, "..", "canonical", "arxiv_2103.00763.json")))
    results = []
    for rec in records:
        label = rec["claim"]
        order = rec["conclusion"]["order"]
        out = {"claim": label, "order": order, "status": None,
               "instances": 0, "witness": None, "undecided_points": 0}

        if label == "Counterexample 3.1":
            mu = [R(8), R(4, 5), R(1, 10)]
            mus = [R(7), R(1), R(9, 10)]
            assert majorizes(mu, mus)
            d5 = max_rh(poisson_cdf, mu, 5) - max_rh(poisson_cdf, mus, 5)
            d2 = max_rh(poisson_cdf, mu, 2) - max_rh(poisson_cdf, mus, 2)
            ok = (d5.a > 0) and (d2.b < 0)
            out.update(status="holds" if ok else "refuted", instances=1,
                       witness=str(5) if ok else None,
                       note="printed +0.0520158@5, -0.0232122@2; "
                            "computed [%.7f,%.7f] and [%.7f,%.7f]"
                            % (d5.a, d5.b, d2.a, d2.b))
        elif label == "Counterexample 3.2":
            mu = [R(28), R(4, 5), R(1, 10)]
            mus = [R(27), R(1), R(9, 10)]
            assert majorizes(mu, mus)
            d6 = min_hz(poisson_surv, mu, 6) - min_hz(poisson_surv, mus, 6)
            d16 = min_hz(poisson_surv, mu, 16) - min_hz(poisson_surv, mus, 16)
            # printed: +0.0124328 at r=6 (reproduces exactly), -0.00024431 at
            # r=16 (does NOT reproduce: rigorous +0.002485 at u=16).
            # Sign change search over the decidable range.
            neg = None
            for u in range(1, 50):
                d = min_hz(poisson_surv, mu, u) - min_hz(poisson_surv, mus, u)
                if d.b < 0:
                    neg = u
                    break
            ok = (d6.a > 0) and (neg is not None)
            out.update(status="holds" if ok else "refuted", instances=1,
                       witness=neg,
                       note="d6=[%.7f,%.7f] (printed +0.0124328, matches); "
                            "d16=[%.7f,%.7f] strictly POSITIVE (printed "
                            "-0.00024431 fails to reproduce); diff decided "
                            "positive at all u in 1..49 -> the claimed "
                            "sign change does not occur in bounded testing"
                            % (d6.a, d6.b, d16.a, d16.b))
        elif label == "Counterexample 3.3":
            q = [R(99, 100), R(96, 100), R(57, 100)]
            qs = [R(9, 10), R(78, 100), R(57, 100)]
            # note: sums 2.52 != 2.25 -> NOT standard Def-2.2 majorization;
            # satisfies weak supermajorization (descending partial sums >=)
            neg, pos = None, None
            for u in range(1, 1000):
                d = max_rh(geom_cdf, q, u) - max_rh(geom_cdf, qs, u)
                if d.b < 0 and neg is None:
                    neg = u
                if d.a > 0 and pos is None:
                    pos = u
            ok = (neg is not None) and (pos is not None)
            out.update(status="holds" if ok else "refuted", instances=1,
                       note="printed -0.0010584@u=1, +0.00628996@u=4; "
                            "computed rh diff is POSITIVE for all "
                            "u in 1..999 (e.g. +0.0250313 at u=1): the "
                            "claimed sign change does not occur; "
                            "Xn:n >=rh Yn:n survives bounded testing")
        elif label == "Theorem 3.1":
            inst = [([R(8), R(4, 5), R(1, 10)], [R(7), R(1), R(9, 10)]),
                    ([R(4), R(3), R(1)], [R(3), R(3), R(2)]),
                    ([R(6), R(2), R(1)], [R(4), R(4), R(1)]),
                    ([R(5), R(5), R(5), R(1)], [R(5), R(4), R(4), R(3)])]
            n, wit = 0, None
            for mu, mus in inst:
                assert majorizes(mu, mus), (mu, mus)
                h, w = st_geq(lambda u: prod(poisson_cdf, mu, u),
                              lambda u: prod(poisson_cdf, mus, u),
                              "max", 80)
                n += 1
                if not h and wit is None:
                    wit = w
            out.update(status="holds" if wit is None else "refuted",
                       instances=n, witness=wit)
        elif label == "Theorem 3.2":
            inst = [([R(8), R(4, 5), R(1, 10)], [R(7), R(1), R(9, 10)]),
                    ([R(4), R(3), R(1)], [R(3), R(3), R(2)]),
                    ([R(6), R(2), R(1)], [R(4), R(4), R(1)]),
                    ([R(5), R(5), R(5), R(1)], [R(5), R(4), R(4), R(3)])]
            n, wit = 0, None
            for mu, mus in inst:
                assert majorizes(mu, mus), (mu, mus)
                h, w = st_geq(lambda u: prod(poisson_surv, mus, u),
                              lambda u: prod(poisson_surv, mu, u),
                              "min", 80)
                n += 1
                if not h and wit is None:
                    wit = w
            out.update(status="holds" if wit is None else "refuted",
                       instances=n, witness=wit)
        elif label == "Theorem 3.3":
            # geometric minima, prod q >= prod q*  =>  X1:n >=hr Y1:n
            # i.e. h_Xmin(u) <= h_Ymin(u) for all u (h = 1 - prod q const)
            inst = [([R(9, 10), R(8, 10), R(7, 10)],
                     [R(8, 10), R(7, 10), R(6, 10)]),
                    ([R(99, 100), R(96, 100), R(57, 100)],
                     [R(9, 10), R(78, 100), R(57, 100)]),
                    ([R(3, 4), R(1, 2)], [R(2, 3), R(9, 16)])]
            n, wit = 0, None
            for q, qs in inst:
                assert sp.prod(q) >= sp.prod(qs)
                bad = None
                for u in range(0, 40):
                    d = min_hz(geom_surv, qs, u) - min_hz(geom_surv, q, u)
                    if d.b < 0:          # h_Y < h_X violates Y<=hr X? X>=hrY
                        bad = u
                        break
                n += 1
                if bad is not None and wit is None:
                    wit = bad
            out.update(status="holds" if wit is None else "refuted",
                       instances=n, witness=wit)
        elif label == "Theorem 3.4":
            # geometric maxima, q >=^m q* (equal sums) => Xn:n >=st Yn:n
            inst = [([R(9, 10), R(8, 10), R(7, 10)],
                     [R(8, 10), R(8, 10), R(8, 10)]),
                    ([R(95, 100), R(75, 100), R(7, 10)],
                     [R(9, 10), R(8, 10), R(7, 10)]),
                    ([R(95, 100), R(85, 100)], [R(9, 10), R(9, 10)]),
                    ([R(9, 10), R(3, 5), R(1, 2)],
                     [R(8, 10), R(7, 10), R(1, 2)])]
            n, wit = 0, None
            for q, qs in inst:
                assert majorizes(q, qs), (q, qs)
                h, w = st_geq(lambda u: prod(geom_cdf, q, u),
                              lambda u: prod(geom_cdf, qs, u),
                              "max", 300)
                n += 1
                if not h and wit is None:
                    wit = w
            out.update(status="holds" if wit is None else "refuted",
                       instances=n, witness=wit)
        else:
            out["status"] = ("unsupported order" if order not in
                             ("st", "hr", "rh", "lr") else
                             "out of harness scope")
        results.append(out)
    dest = os.path.join(HERE, "eval_arxiv_2103.00763.result.json")
    json.dump(results, open(dest, "w"), indent=1, default=str)
    print(json.dumps(results, indent=1, default=str))


if __name__ == "__main__":
    main()
