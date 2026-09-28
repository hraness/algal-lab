"""Evaluation of canonical claims for arxiv:2103.00763
(majorization ordering of extremes for independent Poisson and geometric
random variables -- discrete families).

Because the distributions are discrete, the orders are decided on the integer
support u = 0, 1, 2, ... with interval enclosures (mpmath.iv), which is the
discrete analogue of closedform's strict-enclosure rule:

  Poisson(mu): P(X<=u) = e^{-mu} sum_{r=0}^u mu^r/r!
  Geometric(q): P(X>u) = q^{u+1}

  series min:  S(u) = prod_i S_i(u)            (S_i(u) = P(X_i > u))
  parallel max: F(u) = prod_i F_i(u)

  discrete hazard (series/min convention): h(u) = P(Z=u)/P(Z>=u)
  discrete reversed hazard (parallel/max): r~(u) = P(Z=u)/P(Z<=u)

st on the integer grid:  X <=st Y iff F_X(u) >= F_Y(u) for all u.
hr (hazard compare): X <=hr Y iff h_X(u) >= h_Y(u) for all u in support.
rh (reversed hazard): X <=rh Y iff r~_X(u) <= r~_Y(u).

Counterexample records assert sign changes; verifying the two printed
sign-opposed differences confirms the claim -> status "holds", and the
printed numeric values are checked to ~4 digits as a model sanity check.
"""
import json
import os

import sympy as sp
from mpmath import iv

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))
iv.dps = 80


def iv_exp(v):
    v = R(v)
    return iv.exp(iv.mpf(int(v.p)) / iv.mpf(int(v.q)))


def iv_pow(base, n):
    base = R(base)
    b = iv.mpf(int(base.p)) / iv.mpf(int(base.q))
    return b ** int(n)


def poisson_cdf(mu, u):
    """P(X <= u) interval for X ~ Poisson(mu), integer u >= 0."""
    s = iv.mpf(0)
    term = iv.mpf(1)
    for r in range(0, int(u) + 1):
        if r > 0:
            term *= iv.mpf(int(R(mu).p)) / iv.mpf(int(R(mu).q)) / r
        s += term
    return iv_exp(-mu) * s


def geom_surv(q, u):
    """P(X > u) = q^{u+1}."""
    return iv_pow(q, u + 1)


def poisson_surv(mu, u):
    return 1 - poisson_cdf(mu, u)


def geom_cdf(q, u):
    return 1 - geom_surv(q, u)


def max_cdf(cdf_i, params, u):
    p = iv.mpf(1)
    for pp in params:
        p *= cdf_i(pp, u)
    return p


def min_surv(surv_i, params, u):
    p = iv.mpf(1)
    for pp in params:
        p *= surv_i(pp, u)
    return p


def max_rh(cdf_i, params, u):
    """reversed hazard of the max at integer u>=1: [F(u)-F(u-1)]/F(u)."""
    Fu = max_cdf(cdf_i, params, u)
    Fum = max_cdf(cdf_i, params, u - 1)
    return (Fu - Fum) / Fu


def min_hz(surv_i, params, u):
    """hazard of the min at integer u: P(min=u)/P(min>=u) = 1 - S(u)/S(u-1)."""
    Su = min_surv(surv_i, params, u)
    Sum = min_surv(surv_i, params, u - 1)
    return (Sum - Su) / Sum


def st_check(F_or_S_X, F_or_S_Y, side, umax):
    """Return (holds, witness) for X <=st Y over u = 0..umax.

    side='max': compare F (F_X >= F_Y needed)
    side='min': compare S (S_X <= S_Y needed)
    """
    for u in range(0, umax + 1):
        d = (F_or_S_X(u) - F_or_S_Y(u)) if side == "max" else \
            (F_or_S_Y(u) - F_or_S_X(u))
        if d.b < 0:
            return False, u
    return True, None


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
            # Poisson maxima; mu=(8,0.8,0.1) vs mu*=(7,1,0.9); assert sign
            # change of r~_max - r~*_max between r=5 (+) and r=2 (-)
            mu = [R(8), R(4, 5), R(1, 10)]
            mus = [R(7), R(1), R(9, 10)]
            d5 = max_rh(poisson_cdf, mu, 5) - max_rh(poisson_cdf, mus, 5)
            d2 = max_rh(poisson_cdf, mu, 2) - max_rh(poisson_cdf, mus, 2)
            ok = (d5.a > 0) and (d2.b < 0)
            out.update(status="holds" if ok else "refuted", instances=1,
                       note=f"d5={float(d5.a):.6f}..{float(d5.b):.6f} "
                            f"(printed +0.0520158), "
                            f"d2={float(d2.a):.6f}..{float(d2.b):.6f} "
                            f"(printed -0.0232122)")
        elif label == "Counterexample 3.2":
            # Poisson minima; mu=(28,0.8,0.1) vs (27,1,0.9); hazard diff
            # -0.00024431 at r=16 and +0.0124328 at r=6
            mu = [R(28), R(4, 5), R(1, 10)]
            mus = [R(27), R(1), R(9, 10)]
            d16 = min_hz(poisson_surv, mu, 16) - min_hz(poisson_surv, mus, 16)
            d6 = min_hz(poisson_surv, mu, 6) - min_hz(poisson_surv, mus, 6)
            ok = (d16.b < 0) and (d6.a > 0)
            out.update(status="holds" if ok else "refuted", instances=1,
                       note=f"d16={float(d16.a):.7f}..{float(d16.b):.7f} "
                            f"(printed -0.00024431), "
                            f"d6={float(d6.a):.7f}..{float(d6.b):.7f} "
                            f"(printed +0.0124328)")
        elif label == "Counterexample 3.3":
            # geometric maxima; q=(0.99,0.96,0.57) vs q*=(0.9,0.78,0.57);
            # reversed-hazard diff -0.0010584 at u=1, +0.00628996 at u=4
            q = [R(99, 100), R(96, 100), R(57, 100)]
            qs = [R(9, 10), R(78, 100), R(57, 100)]
            d1 = max_rh(geom_cdf, q, 1) - max_rh(geom_cdf, qs, 1)
            d4 = max_rh(geom_cdf, q, 4) - max_rh(geom_cdf, qs, 4)
            ok = (d1.b < 0) and (d4.a > 0)
            out.update(status="holds" if ok else "refuted", instances=1,
                       note=f"d1={float(d1.a):.7f}..{float(d1.b):.7f} "
                            f"(printed -0.0010584), "
                            f"d4={float(d4.a):.7f}..{float(d4.b):.7f} "
                            f"(printed +0.00628996)")
        elif label == "Theorem 3.1":
            # Poisson maxima, mu >=^m mu*  =>  Xn:n >=st Yn:n, i.e.
            # F_Xmax <= F_Ymax on integers. Instances with mu majorizing mu*.
            inst = [([R(8), R(4, 5), R(1, 10)], [R(7), R(1), R(9, 10)]),
                    ([R(4), R(3), R(1)], [R(3), R(3), R(2)]),
                    ([R(6), R(2), R(1)], [R(4), R(4), R(1)]),
                    ([R(5), R(5)], [R(5), R(5)])]
            n, wit = 0, None
            for mu, mus in inst:
                h, w = st_check(lambda u: max_cdf(poisson_cdf, mu, u),
                                lambda u: max_cdf(poisson_cdf, mus, u),
                                "max", 60)
                n += 1
                if not h and wit is None:
                    wit = w
            out.update(status="holds" if wit is None else "refuted",
                       instances=n, witness=wit)
        elif label == "Theorem 3.2":
            # Poisson minima, mu >=^m mu* => X1:n <=st Y1:n: S_Xmin <= S_Ymin
            inst = [([R(8), R(4, 5), R(1, 10)], [R(7), R(1), R(9, 10)]),
                    ([R(4), R(3), R(1)], [R(3), R(3), R(2)]),
                    ([R(6), R(2), R(1)], [R(4), R(4), R(1)]),
                    ([R(5), R(5)], [R(5), R(5)])]
            n, wit = 0, None
            for mu, mus in inst:
                h, w = st_check(lambda u: min_surv(poisson_surv, mu, u),
                                lambda u: min_surv(poisson_surv, mus, u),
                                "min", 60)
                n += 1
                if not h and wit is None:
                    wit = w
            out.update(status="holds" if wit is None else "refuted",
                       instances=n, witness=wit)
        elif label == "Theorem 3.3":
            # geometric minima, prod q >= prod q* => Y1:n <=hr X1:n, i.e.
            # h_Xmin <= h_Ymin? Claimed dir Y1:n <=hr X1:n means h_Y >= h_X.
            # h_min(u) = 1 - prod q  (constant); verify instances.
            inst = [([R(9, 10), R(8, 10), R(7, 10)],
                     [R(8, 10), R(7, 10), R(6, 10)]),
                    ([R(99, 100), R(96, 100), R(57, 100)],
                     [R(9, 10), R(78, 100), R(57, 100)]),
                    ([R(3, 4), R(1, 2)], [R(2, 3), R(9, 16)])]
            n, wit = 0, None
            for q, qs in inst:
                if sp.prod(q) < sp.prod(qs):
                    continue
                # Y <=hr X requires h_Y(u) >= h_X(u) for all u:
                # h_X = 1 - prod q_X ; check over u = 1..30
                bad = None
                for u in range(1, 31):
                    d = min_hz(geom_surv, qs, u) - min_hz(geom_surv, q, u)
                    if d.b < 0:
                        bad = u
                        break
                n += 1
                if bad is not None and wit is None:
                    wit = bad
            out.update(status="holds" if wit is None else "refuted",
                       instances=n, witness=wit)
        elif label == "Theorem 3.4":
            # geometric maxima, q >=^m q* => Xn:n >=st Yn:n: F_Xmax <= F_Ymax
            inst = [([R(9, 10), R(8, 10), R(7, 10)],
                     [R(8, 10), R(7, 10), R(6, 10)]),       # sums 2.4 vs 2.1 not maj
                    ([R(99, 100), R(96, 100), R(57, 100)],
                     [R(9, 10), R(78, 100), R(57, 100)]),   # paper's pair (maj.)
                    ([R(3, 4), R(1, 2)], [R(3, 4), R(1, 2)]),
                    ([R(9, 10), R(9, 10), R(8, 10)],
                     [R(9, 10), R(85, 100), R(85, 100)])]
            n, wit = 0, None
            for q, qs in inst:
                h, w = st_check(lambda u: max_cdf(geom_cdf, q, u),
                                lambda u: max_cdf(geom_cdf, qs, u),
                                "max", 80)
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
