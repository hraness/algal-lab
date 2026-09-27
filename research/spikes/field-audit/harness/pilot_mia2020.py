"""Pilot tests for doi:10.7153/mia-2020-23-03 (largest claim amounts).

Admissible sub-case used for every theorem: independence copula (it satisfies
C >= v1 v2, d1C >= d2C on v1 <= v2, Schur-concavity, and C <= C* with C* = C),
h(p) = p (differentiable, strictly increasing, concave, with log-concave
inverse), and exponential-type marginals written in s = exp(-t/D):
  scale / PHR with exponential baseline   Fbar(x; lam) = exp(-lam x)
  transmuted exponential (TG, mean 1)     Fbar(x; lam) = e^{-x} (1 - lam (1 - e^{-x})), lam in [-1, 1]
Every model is a polynomial in s, so the harness decides Y* <=st Y exactly.
"""
import json
import random
from fractions import Fraction as Fr

import sympy as sp

from ratdist import Dist, st, z

random.seed(20260927)
ONE, ZERO = sp.Integer(1), sp.Integer(0)
D = 10  # rates are multiples of 1/10


def surv_exp(lam):
    return z ** int(sp.Rational(lam) * D)


def surv_tg(lam):
    e = z ** D                      # e^{-x} with s = e^{-x/D}
    return e * (1 - sp.Rational(lam) * (1 - e))


def largest_claim(survivals, p):
    """Independent occurrences and severities: P(Y > t) = 1 - prod(1 - p_i S_i)."""
    prod = ONE
    for S, pi in zip(survivals, p):
        prod *= 1 - sp.Rational(pi) * S
    return Dist(sp.expand(1 - prod), ZERO, ONE, increasing=False)


def largest_claim_bivariate(survivals, pmf):
    """Bivariate Bernoulli occurrence pmf {(i,j): prob}, independent severities."""
    S1, S2 = survivals
    F1, F2 = 1 - S1, 1 - S2
    cdf = pmf[(0, 0)] + pmf[(1, 0)] * F1 + pmf[(0, 1)] * F2 + pmf[(1, 1)] * F1 * F2
    return Dist(sp.expand(1 - cdf), ZERO, ONE, increasing=False)


def rat(lo, hi, den=10):
    return sp.Rational(random.randint(int(lo * den), int(hi * den)), den)


def opposite(lam, p):
    return (lam[0] - lam[1]) * (p[0] - p[1]) <= 0


def majorized_by(a, b):
    """a is majorized by b (two components)."""
    return sum(a) == sum(b) and min(a) >= min(b)


def weakly_supermajorized_by(a, b):
    """a is weakly supermajorized by b: min(a) >= min(b) and sum(a) >= sum(b)."""
    return min(a) >= min(b) and sum(a) >= sum(b)


def gen_p_pair():
    p = [rat(0.1, 0.9, 20), rat(0.1, 0.9, 20)]
    s, lo = p[0] + p[1], min(p)
    for _ in range(50):
        a = rat(float(lo), float(s - lo), 40)
        q = [a, s - a]
        if majorized_by(q, p):
            return p, q
    return p, list(p)


def gen_lam_pair(lo, hi, den=10):
    lam = [rat(lo, hi, den), rat(lo, hi, den)]
    for _ in range(80):
        cand = [rat(lo, hi, den), rat(lo, hi, den)]
        if weakly_supermajorized_by(cand, lam):
            return lam, cand
    return lam, list(lam)


def theorem_instances(name, marg, lam_range, trials=30):
    rows, refuted = [], None
    tested = 0
    for _ in range(trials * 20):
        if tested >= trials:
            break
        if name in ("3.1",):
            lam = [rat(*lam_range), rat(*lam_range)]
            p, ps = gen_p_pair()
            lam_s = lam
            if not (opposite(lam, p) and opposite(lam, ps)):
                continue
        elif name in ("3.2",):
            lam, lam_s = gen_lam_pair(*lam_range)
            p = [rat(0.1, 0.9, 20), rat(0.1, 0.9, 20)]
            ps = p
            if not (opposite(lam, p) and opposite(lam_s, p)):
                continue
        else:  # 3.3, 3.4, 3.5, 3.6
            lam, lam_s = gen_lam_pair(*lam_range)
            p, ps = gen_p_pair()
            if not (opposite(lam, p) and opposite(lam_s, ps)):
                continue
        Y = largest_claim([marg(l) for l in lam], p)
        Ys = largest_claim([marg(l) for l in lam_s], ps)
        holds, witness = st(Ys, Y)
        tested += 1
        if not holds and refuted is None:
            refuted = {"lam": [str(v) for v in lam], "p": [str(v) for v in p],
                       "lam_star": [str(v) for v in lam_s], "p_star": [str(v) for v in ps], "s0": str(witness)}
    return {"tested": tested, "refuted_example": refuted}


def theorem_lwsai(marg, lam_range, trials=30):
    tested, refuted = 0, None
    for _ in range(trials * 20):
        if tested >= trials:
            break
        lam = sorted([rat(*lam_range), rat(*lam_range)], reverse=True)       # lam1 >= lam2
        s, lo = sum(lam), min(lam)
        a = rat(float(lo), float(s - lo), 10)
        lam_s = sorted([a, s - a], reverse=True)                              # lam* majorized by lam, lam*1 >= lam*2
        if not majorized_by(lam_s, lam):
            continue
        q = [rat(0.02, 0.3, 50) for _ in range(3)]
        p10, p01, p11 = sorted(q[:2]) + [q[2]]                               # p(1,0) <= p(0,1)
        p00 = 1 - p10 - p01 - p11
        if p00 <= 0:
            continue
        pmf = {(0, 0): p00, (1, 0): p10, (0, 1): p01, (1, 1): p11}
        Y = largest_claim_bivariate([marg(l) for l in lam], pmf)
        Ys = largest_claim_bivariate([marg(l) for l in lam_s], pmf)
        holds, witness = st(Ys, Y)
        tested += 1
        if not holds and refuted is None:
            refuted = {"lam": [str(v) for v in lam], "lam_star": [str(v) for v in lam_s],
                       "pmf": {str(k): str(v) for k, v in pmf.items()}, "s0": str(witness)}
    return {"tested": tested, "refuted_example": refuted}


def theorem_componentwise(marg, lam_range, n, trials=20):
    tested, refuted = 0, None
    for _ in range(trials):
        lam = [rat(*lam_range) for _ in range(n)]
        lam_s = [min(l + rat(0, 0.5), sp.Rational(lam_range[1])) for l in lam]
        p = [rat(0.1, 0.9, 20) for _ in range(n)]
        Y = largest_claim([marg(l) for l in lam], p)
        Ys = largest_claim([marg(l) for l in lam_s], p)
        holds, witness = st(Ys, Y)
        tested += 1
        if not holds and refuted is None:
            refuted = {"lam": [str(v) for v in lam], "lam_star": [str(v) for v in lam_s], "p": [str(v) for v in p]}
    return {"tested": tested, "refuted_example": refuted}


if __name__ == "__main__":
    results = {
        "Theorem 3.1 (exponential)": theorem_instances("3.1", surv_exp, (0.1, 3)),
        "Theorem 3.2 (exponential, convex in lam)": theorem_instances("3.2", surv_exp, (0.1, 3)),
        "Theorem 3.3 (exponential)": theorem_instances("3.3", surv_exp, (0.1, 3)),
        "Theorem 3.4 (scale, exponential baseline)": theorem_instances("3.4", surv_exp, (0.1, 3)),
        "Theorem 3.5 (PHR, exponential baseline)": theorem_instances("3.5", surv_exp, (0.1, 3)),
        "Theorem 3.6 (TG, exponential baseline)": theorem_instances("3.6", surv_tg, (-1, 1)),
        "Theorems 3.7-3.9 (LWSAI, exponential)": theorem_lwsai(surv_exp, (0.1, 3)),
        "Theorem 3.10 (LWSAI, TG)": theorem_lwsai(surv_tg, (-1, 1)),
        "Theorems 3.11, 3.13-3.15 (componentwise, exponential, n=3)": theorem_componentwise(surv_exp, (0.1, 3), 3),
        "Theorem 3.16 (componentwise, TG, n=3)": theorem_componentwise(surv_tg, (-1, 1), 3),
    }
    print(json.dumps(results, indent=1))
