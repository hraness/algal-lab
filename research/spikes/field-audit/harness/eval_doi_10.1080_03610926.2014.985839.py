"""Evaluation of canonical claims for doi:10.1080/03610926.2014.985839
(scale-model parallel systems; Khaledi-Tavangar style results).

Baseline: exponential F(t) = 1 - e^{-t}, r(t) = 1/(e^t - 1), which is
GG(beta=1, alpha=1) and satisfies every printed condition:
  tr(t) = t/(e^t-1) decreasing;
  t^2 r'(t) = -(t/(2 sinh(t/2)))^2 increasing (u/sinh u decreasing);
  tr'(t)/r(t) = 1 - t e^t/(e^t - 1) decreasing.
X_{lam_i} ~ F(lam_i t):  S_i = exp(-lam_i t), F_{n:n} = prod(1 - exp(-lam_i t))
-> polynomial in z = e^{-t/D}: exact checks via ratdist.

Directions (per canonical): Thm 3.1/3.2: X^lam_{n:n} <=rh X^theta_{n:n};
Thm 4.1/4.5: X-side max <=rh Y-side max (ratio r*/r increasing —
additionally the exact ratio monotonicity is checked on the grid);
Cor 4.4, Thm 4.6, 4.7: X <=lr Y.
"""
import json
import os

import sympy as sp

import ratdist as rd
import closedform as cf
from closedform import x, Closed

R = sp.Rational
z = rd.z
HERE = os.path.dirname(os.path.abspath(__file__))


def dist_max_exp(rates, D=4):
    """CDF prod(1 - z^{lam_i D}) -> survival 1 - prod, z = e^{-t/D} decreasing."""
    F = sp.prod([1 - z ** int(R(l) * D) for l in rates])
    return rd.Dist(1 - F, sp.Integer(0), sp.Integer(1), increasing=False)


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


def maj(a, b):
    """b majorizes a: sorted-desc partial sums >=, equal totals."""
    a, b = sorted(a, reverse=True), sorted(b, reverse=True)
    return sum(a) == sum(b) and all(
        sum(a[:k]) <= sum(b[:k]) for k in range(len(a)))


def theorem_3_1_3_2():
    """lam weakly majorized by theta => X^lam_{n:n} <=rh X^theta_{n:n}.
    Equal-sum instances (ordinary majorization => weak, both conventions)."""
    n, wit, und = 0, None, 0
    cases = [
        ([R(3), R(3), R(1)], [R(4), R(2), R(1)]),   # theta more spread
        ([R(1), R(3), R(3)], [R(1), R(1), R(5)]),
        ([R(2), R(2), R(4)], [R(1), R(1), R(6)]),
        ([R(1), R(2), R(5)], [R(1), R(1), R(6)]),   # theta=(6,1,1) vs lam=(5,2,1): 6>=5,7>=7,8=8
        ([R(2), R(3)], [R(1), R(4)]),
        ([R(1), R(2), R(2), R(3)], [R(1), R(1), R(1), R(5)]),
    ]
    for lam, th in cases:
        assert maj(lam, th), (lam, th)
        Xl = dist_max_exp(lam)
        Xt = dist_max_exp(th)
        holds, w = rd.rh(Xl, Xt)
        n += 1
        if not holds and wit is None:
            wit = w
    return n, wit, und


def theorem_4_1():
    """Two-component: {l1,l} vs {l1*,l}, l1* = min => X <=rh Y; also check the
    printed ratio monotonicity r*/r increasing (stronger rh-ratio claim)."""
    n, wit, und = 0, None, 0
    cases = [  # (l1, l, l1*), l1* <= min(l, l1)
        (R(2), R(1), R(1)),
        (R(3), R(2), R(1)),
        (R(3), R(4), R(1, 2)),
        (R(5), R(3), R(2)),
    ]
    for l1, l, ls in cases:
        assert ls <= min(l, l1)
        X = dist_max_exp([l1, l])
        Y = dist_max_exp([ls, l])
        holds, w = rd.rh(X, Y)
        n += 1
        if not holds and wit is None:
            wit = w
        # printed claim: r_Y(t)/r_X(t) increasing in t
        lam1, lam_, lams = map(R, (l1, l, ls))
        rA = lam1 / (sp.exp(lam1 * x) - 1) + lam_ / (sp.exp(lam_ * x) - 1)
        rB = lams / (sp.exp(lams * x) - 1) + lam_ / (sp.exp(lam_ * x) - 1)
        E = sp.diff(rB, x) * rA - rB * sp.diff(rA, x)   # (rB/rA)' * rA^2 >= 0
        from mpmath import iv
        undv = 0
        for pt in cf.grid(0, sp.oo, ()):
            d = False
            for dps in (60, 150, 400):
                iv.dps = dps
                v = cf.iv_eval(E, pt)
                if v.b < 0:
                    if wit is None:
                        wit = pt
                    d = True
                    break
                if v.a >= 0:
                    d = True
                    break
            undv += not d
        und += undv
        n += 1
    return n, wit, und


def theorem_4_5():
    """Multiple-outlier rh version of 4.1."""
    n, wit, und = 0, None, 0
    cases = [  # (p, l1, q, l, l1*)
        (2, R(3), 1, R(2), R(1)),
        (1, R(4), 2, R(2), R(1)),
        (2, R(5), 2, R(3), R(1)),
        (3, R(2), 1, R(1), R(1, 2)),
    ]
    for p, l1, q, l, ls in cases:
        assert ls <= min(l, l1)
        X = dist_max_exp([l1] * p + [l] * q)
        Y = dist_max_exp([ls] * p + [l] * q)
        holds, w = rd.rh(X, Y)
        n += 1
        if not holds and wit is None:
            wit = w
        # ratio monotonicity r_Y/r_X increasing
        lam1, lam_, lams = map(R, (l1, l, ls))
        rA = p * lam1 / (sp.exp(lam1 * x) - 1) + q * lam_ / (sp.exp(lam_ * x) - 1)
        rB = p * lams / (sp.exp(lams * x) - 1) + q * lam_ / (sp.exp(lam_ * x) - 1)
        E = sp.diff(rB, x) * rA - rB * sp.diff(rA, x)
        from mpmath import iv
        for pt in cf.grid(0, sp.oo, ()):
            d = False
            for dps in (60, 150, 400):
                iv.dps = dps
                v = cf.iv_eval(E, pt)
                if v.b < 0:
                    if wit is None:
                        wit = pt
                    d = True
                    break
                if v.a >= 0:
                    d = True
                    break
            if not d:
                und += 1
        n += 1
    return n, wit, und


def corollary_4_4():
    """lam <= min(l1,l2) and lam <= (l1+l2)/2 => X_{2:2} <=lr Y_{2:2}."""
    n, wit, und = 0, None, 0
    cases = [  # (l1, l2, lam)
        (R(2), R(4), R(1)),
        (R(3), R(5), R(3)),          # lam = min
        (R(1), R(3), R(1)),
        (R(2), R(6), R(2)),          # lam = min = (l1+l2)/2 boundary? 2<=4 yes
        (R(3), R(4), R(3)),
    ]
    for l1, l2, lam in cases:
        assert lam <= min(l1, l2) and lam <= (l1 + l2) / 2
        X = dist_max_exp([l1, l2])
        Y = dist_max_exp([lam, lam])
        holds, w = rd.lr(X, Y)
        n += 1
        if not holds and wit is None:
            wit = w
    return n, wit, und


def theorem_4_2():
    """Two-component version: (l1,l) vs (l1*,l), l1*=min => X_{2:2} <=lr Y_{2:2}."""
    n, wit, und = 0, None, 0
    for l1, l, ls in [(R(2), R(1), R(1)), (R(3), R(2), R(1)),
                      (R(3), R(4), R(1, 2)), (R(5), R(3), R(2))]:
        assert ls <= min(l, l1)
        X = dist_max_exp([l1, l])
        Y = dist_max_exp([ls, l])
        holds, w = rd.lr(X, Y)
        n += 1
        if not holds and wit is None:
            wit = w
    return n, wit, und


def theorem_4_6():
    """Multiple-outlier lr version."""
    n, wit, und = 0, None, 0
    for p, l1, q, l, ls in [(2, R(3), 1, R(2), R(1)), (1, R(4), 2, R(2), R(1)),
                            (2, R(5), 2, R(3), R(1)), (3, R(2), 1, R(1), R(1, 2)),
                            (2, R(4), 2, R(4), R(2))]:
        assert ls <= min(l, l1)
        X = dist_max_exp([l1] * p + [l] * q)
        Y = dist_max_exp([ls] * p + [l] * q)
        holds, w = rd.lr(X, Y)
        n += 1
        if not holds and wit is None:
            wit = w
    return n, wit, und


def theorem_4_7():
    """Mixed baselines: outliers F, commons G(=exp rate 2). rF/rG increasing:
    r_F/r_G = (e^{2t}-1)/(e^t-1) = e^t + 1 -- increasing. lam1*=min => lr."""
    n, wit, und = 0, None, 0
    for p, l1, q, l, ls in [(2, R(3), 1, R(2), R(1)), (1, R(4), 2, R(2), R(1)),
                            (2, R(5), 2, R(3), R(1)), (3, R(2), 1, R(1), R(1, 2))]:
        assert ls <= min(l, l1)
        # F comps at rate lam_i, G comps at rate 2*lam (G(t)=1-e^{-2 lam t})
        X = dist_max_exp([l1] * p + [2 * l] * q)
        Y = dist_max_exp([ls] * p + [2 * l] * q)
        holds, w = rd.lr(X, Y)
        n += 1
        if not holds and wit is None:
            wit = w
    return n, wit, und


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.1080_03610926.2014.985839.json")))
    results = []
    for recd in canon:
        order = recd["conclusion"]["order"]
        label = recd["claim"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        fn = {"Theorem 3.1": theorem_3_1_3_2, "Theorem 3.2": theorem_3_1_3_2,
              "Theorem 4.1": theorem_4_1, "Theorem 4.5": theorem_4_5,
              "Corollary 4.4": corollary_4_4, "Theorem 4.2": theorem_4_2,
              "Theorem 4.6": theorem_4_6, "Theorem 4.7": theorem_4_7}.get(label)
        if fn is None:
            results.append(rec(recd, "out of harness scope"))
            continue
        n_, w, u = fn()
        results.append(rec(recd, "holds" if w is None else "refuted",
                           instances=n_, witness=w, undecided=u))
    out = os.path.join(HERE, "eval_doi_10.1080_03610926.2014.985839.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
