"""Printed counterexamples of arxiv:2103.00763 (Poisson and geometric extremes).

The paper gives no formula for its discrete hazard and reversed hazard rates,
so the two standard discrete conventions are evaluated for each:
  hazard            h(r) = P(Z = r) / P(Z >= r)      or  P(Z = r) / P(Z > r)
  reversed hazard   rt(r) = P(Z = r) / P(Z <= r)     or  P(Z = r) / P(Z < r)
80-digit arithmetic, with Poisson tails summed directly to avoid cancellation.
"""
import json

from mpmath import exp, factorial, inf, mp, mpf, nsum

mp.dps = 80


def poisson_cdf(mu, r):
    return sum(exp(-mu) * mu ** j / factorial(j) for j in range(r + 1)) if r >= 0 else mpf(0)


def max_cdf(mus, r):
    out = mpf(1)
    for mu in mus:
        out *= poisson_cdf(mu, r)
    return out


def poisson_sf(mu, r):
    """P(X > r) as a direct tail sum; 1 - cdf cancels catastrophically for small mu."""
    return nsum(lambda j: exp(-mu) * mu ** j / factorial(j), [r + 1, inf])


def min_surv(mus, r):          # P(min > r)
    out = mpf(1)
    for mu in mus:
        out *= poisson_sf(mu, r)
    return out


def geom_surv(q, u):           # P(X > u) = q^{u+1}
    return q ** (u + 1)


def geo_max_cdf(qs, u):
    out = mpf(1)
    for q in qs:
        out *= 1 - geom_surv(q, u) if u >= 0 else 0
    return out if u >= 0 else mpf(0)


def rev_hazards(cdf, r):
    pmf = cdf(r) - cdf(r - 1)
    return {"pmf/P(<=r)": pmf / cdf(r), "pmf/P(<r)": pmf / cdf(r - 1) if cdf(r - 1) > 0 else None}


def hazards(surv, r):          # surv(r) = P(Z > r)
    pmf = surv(r - 1) - surv(r)
    return {"pmf/P(>=r)": pmf / surv(r - 1), "pmf/P(>r)": pmf / surv(r)}


def diff(a, b):
    return {k: (None if a[k] is None or b[k] is None else mp.nstr(a[k] - b[k], 9)) for k in a}


mu, mus = [mpf(8), mpf("0.8"), mpf("0.1")], [mpf(7), mpf(1), mpf("0.9")]
out = {"Counterexample 3.1 (printed r=5: 0.0520158, r=2: -0.0232122), rh of maxima": {
    r: diff(rev_hazards(lambda k: max_cdf(mu, k), r), rev_hazards(lambda k: max_cdf(mus, k), r)) for r in (2, 5)}}
mu, mus = [mpf(28), mpf("0.8"), mpf("0.1")], [mpf(27), mpf(1), mpf("0.9")]
out["Counterexample 3.2 (printed r=16: -0.00024431, r=6: 0.0124328), hazard of minima"] = {
    r: diff(hazards(lambda k: min_surv(mu, k), r), hazards(lambda k: min_surv(mus, k), r)) for r in (6, 16)}
q, qs = [mpf("0.99"), mpf("0.96"), mpf("0.57")], [mpf("0.9"), mpf("0.78"), mpf("0.57")]
out["Counterexample 3.3 (printed u=1: -0.0010584, u=4: 0.00628996), rh of geometric maxima"] = {
    u: diff(rev_hazards(lambda k: geo_max_cdf(q, k), u), rev_hazards(lambda k: geo_max_cdf(qs, k), u)) for u in (1, 4)}
out["Counterexample 3.2 sign of hazard difference, r = 1..40 (standard definition)"] = "".join(
    "+" if hazards(lambda k: min_surv(mu, k), r)["pmf/P(>=r)"] > hazards(lambda k: min_surv(mus, k), r)["pmf/P(>=r)"] else "-"
    for r in range(1, 41))
out["Counterexample 3.3 majorization check"] = {"sum q": mp.nstr(sum(q), 6), "sum q*": mp.nstr(sum(qs), 6)}
print(json.dumps(out, indent=1, default=str))
