"""High-precision checks (mpmath, 50 digits) of the remaining printed examples of
doi:10.7153/mia-2020-23-03, whose marginals or copulas have no rational form.
Verdicts use a grid of 400 points; a difference is counted only if it exceeds
1e-30, far above the working precision.
"""
import json

from mpmath import exp, gammainc, log, mp, mpf

mp.dps = 50
TOL = mpf(10) ** -30


def fgm(theta):
    return lambda u, v: u * v * (1 + theta * (1 - u) * (1 - v))


def gumbel(theta):
    return lambda u, v: exp(-(((-log(u)) ** theta + (-log(v)) ** theta) ** (1 / theta))) if u > 0 and v > 0 else mpf(0)


def frank(theta, *us):
    num = 1
    for u in us:
        num *= exp(-theta * u) - 1
    return -log(1 + num / (exp(-theta) - 1) ** (len(us) - 1)) / theta


def two_claims(F1, F2, p1, p2, C):
    """P(Y > t) for Y = max(I1 X1, I2 X2), independent Bernoulli occurrences."""
    return lambda t: 1 - ((1 - p1) * (1 - p2) + p1 * (1 - p2) * F1(t) + (1 - p1) * p2 * F2(t) + p1 * p2 * C(F1(t), F2(t)))


def three_claims_frank(Fs, ps, theta):
    import itertools
    def surv(t):
        F = [f(t) for f in Fs]
        cdf = mpf(0)
        for mask in itertools.product([0, 1], repeat=3):
            w = 1
            for i, m in enumerate(mask):
                w *= ps[i] if m else 1 - ps[i]
            active = [F[i] for i in range(3) if mask[i]]
            if not active:
                c = 1
            elif len(active) == 1:
                c = active[0]
            else:
                c = frank(theta, *active)
            cdf += w * c
        return 1 - cdf
    return surv


def compare(Sstar, S, grid):
    diffs = [(t, S(t) - Sstar(t)) for t in grid]            # Y* <=st Y  iff  S - S* >= 0
    neg = [t for t, d in diffs if d < -TOL]
    pos = [t for t, d in diffs if d > TOL]
    return {"Ystar_le_st_Y_on_grid": not neg, "Y_le_st_Ystar_on_grid": not pos,
            "first_violation_of_Ystar_le_Y": None if not neg else mp.nstr(neg[0], 8),
            "cross": bool(neg) and bool(pos)}


grid = [mpf(k) / 20 for k in range(1, 401)]
gamma_cdf = lambda shape, rate: (lambda t: gammainc(shape, 0, rate * t, regularized=True))
out = {}

# Examples 3.1 and 3.2: Gamma(0.8, rate lam_i), FGM theta = 0.5, h(p) = p.
C = fgm(mpf("0.5"))
F = lambda lam: gamma_cdf(mpf("0.8"), mpf(lam))
out["Example 3.1 (printed: Y* <=st Y)"] = compare(
    two_claims(F("0.4"), F("0.6"), mpf("0.026"), mpf("0.024"), C),
    two_claims(F("0.26"), F("0.74"), mpf("0.03"), mpf("0.02"), C), grid)
out["Example 3.2 (printed: survivals cross)"] = compare(
    two_claims(F("0.4"), F("0.6"), mpf("0.028"), mpf("0.022"), C),
    two_claims(F("0.26"), F("0.74"), mpf("0.02"), mpf("0.03"), C), grid)

# Example 3.4: transmuted exponential TE(3, lam), Gumbel-Hougaard theta = 10, h(p) = sqrt(p).
TE = lambda lam: (lambda t: 1 - exp(-t / 3) * (1 - mpf(lam) * (1 - exp(-t / 3))))
G = gumbel(mpf(10))
out["Example 3.4 (printed: Y* <=st Y)"] = compare(
    two_claims(TE("0.1"), TE("0.4"), mpf("0.0676"), mpf("0.0576"), G),
    two_claims(TE("0.6"), TE("-0.2"), mpf("0.04"), mpf("0.09"), G), grid)

# Example 3.7: Weibull(shape 3, rate lam_i), trivariate Frank theta = 0.6, three independent occurrences.
W = lambda lam: (lambda t: 1 - exp(-(mpf(lam) * t) ** 3))
out["Example 3.7 (printed: Y* <=st Y)"] = compare(
    three_claims_frank([W("0.51"), W("0.7"), W("0.33")], [mpf("0.01"), mpf("0.02"), mpf("0.07")], mpf("0.6")),
    three_claims_frank([W("0.5"), W("0.7"), W("0.3")], [mpf("0.01"), mpf("0.02"), mpf("0.07")], mpf("0.6")), grid)

print(json.dumps(out, indent=1))
