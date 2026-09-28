"""Evaluation of canonical claims for doi:10.1239/jap.1429282609
(Torrado-Kochar: Weibull parallel systems).

W(alpha, lam): f(t) = a lam (lam t)^{a-1} e^{-(lam t)^a};
F_lam(t) = 1 - e^{-(lam t)^a}, S_lam = e^{-(lam t)^a}.
Parallel system: F_{n:n} = prod (1 - e^{-(lam_i t)^a}).
(lam*x)^a keeps a rational-exponent Pow over a Mul base -> iv_eval OK.

Majorization convention (paper Def. 2.2 / canonical): lam majorized by theta
<= equal sums and ascending partial sums of lam >= theta's (theta more
dispersed). Ageing records (rhr ratio monotonicity claims) are skipped
("unsupported order").
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_wei(lam, a):
    return sp.exp(-(R(lam) * x) ** R(a))


def F_wei(lam, a):
    return 1 - S_wei(lam, a)


def dmax(lams, a):
    return Closed(1 - sp.prod([F_wei(l, a) for l in lams]))


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


def maj_by(lam, th):
    """lam majorized by theta per printed Def 2.2: equal sums, ascending
    partial sums of lam >= those of theta."""
    l_, t_ = sorted(lam), sorted(th)
    return sum(l_) == sum(t_) and all(
        sum(l_[:k]) >= sum(t_[:k]) for k in range(1, len(l_)))


def th_rh():   # Theorem 4.1 / Corollary 4.2: X^lam <=rh X^theta
    n, wit, und = 0, None, 0
    cases = [  # (lam, theta, alpha)
        ([R(2), R(3), R(4)], [R(1), R(4), R(4)], R(1)),
        ([R(2), R(3), R(4)], [R(1), R(4), R(4)], R(1, 2)),
        ([R(2), R(2), R(4)], [R(1), R(3), R(4)], R(1)),    # sums 8
        ([R(2), R(4)], [R(1), R(5)], R(1, 2)),
        ([R(3), R(3), R(3), R(3)], [R(2), R(2), R(4), R(4)], R(1)),
        ([R(2), R(3), R(4)], [R(1), R(4), R(4)], R(9, 10)),
    ]
    for lam, th, a in cases:
        assert maj_by(lam, th) and a <= 1
        X, Y = dmax(lam, a), dmax(th, a)
        h, w, u = cf.check("rh", X, Y)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def th_4_4():
    """n=2: lam majorized by theta, 0<a<=1 => X <=lr Y."""
    n, wit, und = 0, None, 0
    cases = [
        ([R(2), R(4)], [R(1), R(5)], R(1)),
        ([R(2), R(4)], [R(1), R(5)], R(1, 2)),
        ([R(2), R(3)], [R(1), R(4)], R(1)),
        ([R(3), R(4)], [R(2), R(5)], R(4, 5)),
        ([R(2), R(4)], [R(1), R(5)], R(9, 10)),
    ]
    for lam, th, a in cases:
        assert maj_by(lam, th) and a <= 1
        X, Y = dmax(lam, a), dmax(th, a)
        h, w, u = cf.check("lr", X, Y)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def th_4_7():
    """Multiple-outlier majorized scale vectors, a<=1 => X <=lr Y."""
    n, wit, und = 0, None, 0
    cases = [  # (p, l1, q, l2, th1, th2, alpha)
        (2, R(4), 1, R(2), R(5), R(1), R(1)),      # X:(4,4,2) Y:(5,5,1) sums 10/11 -> not equal
        (1, R(4), 2, R(2), R(6), R(1), R(1)),      # X:(4,2,2) Y:(6,1,1) sums 8
        (2, R(3), 2, R(1), R(4), R(1), R(1, 2)),   # X:(3,3,1,1) Y:(4,4,1,1)?? sums 8/10
    ]
    # rebuild satisfying equal sums explicitly
    cases = []
    for p, l1, q, l2, t1, t2 in [(2, R(4), 1, R(2), R(5), R(2)),
                                 (1, R(4), 2, R(2), R(6), R(1)),
                                 (2, R(3), 2, R(2), R(4), R(1)),
                                 (2, R(5), 1, R(1), R(6), R(1))]:
        xs = [l1] * p + [l2] * q
        ys = [t1] * p + [t2] * q
        if sum(xs) == sum(ys) and all(sum(sorted(xs)[:k]) >= sum(sorted(ys)[:k])
                                      for k in range(1, len(xs))):
            cases.append((p, l1, q, l2, t1, t2))
    assert cases
    alphas = [R(1), R(1, 2), R(9, 10)]
    for p, l1, q, l2, t1, t2 in cases:
        for a in alphas:
            X = dmax([l1] * p + [l2] * q, a)
            Y = dmax([t1] * p + [t2] * q, a)
            h, w, u = cf.check("lr", X, Y)
            n += 1
            und += u
            if not h and wit is None:
                wit = w
    return n, wit, und


def th_4_9():
    """X=(l1,l) vs Y=(l1*,l), l1* = min => X <=lr Y, any alpha."""
    n, wit, und = 0, None, 0
    cases = [  # (l1, l, l1*, alpha), l1* <= min(l, l1)
        (R(3), R(1), R(1), R(1)),
        (R(4), R(2), R(1), R(2)),
        (R(3), R(4), R(1, 2), R(3, 10)),
        (R(5), R(3), R(2), R(13, 10)),
        (R(2), R(5), R(1), R(3)),
    ]
    for l1, l, ls, a in cases:
        assert ls <= min(l, l1)
        X, Y = dmax([l1, l], a), dmax([ls, l], a)
        h, w, u = cf.check("lr", X, Y)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def th_4_11():
    """theta1 <= lam1 <= lam2 <= theta2 and (lam) weakly majorized by (theta)
    => X <=lr Y, a<=1."""
    n, wit, und = 0, None, 0
    cases = [  # (lam1, lam2, th1, th2, alpha)
        (R(2), R(3), R(1), R(4), R(1)),
        (R(2), R(3), R(1), R(4), R(1, 2)),
        (R(2), R(5), R(1), R(6), R(1)),
        (R(3), R(5), R(2), R(6), R(4, 5)),
    ]
    for l1, l2, t1, t2, a in cases:
        assert t1 <= l1 <= l2 <= t2
        # weak majorization: ascending partial sums of lam >= theta's
        assert l1 >= t1 and l1 + l2 >= t1 + t2
        X, Y = dmax([l1, l2], a), dmax([t1, t2], a)
        h, w, u = cf.check("lr", X, Y)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def th_4_13():
    """Multiple-outlier: X=(l1*p, l*q) vs Y=(l1**p, l*q), l1*<=min => lr."""
    n, wit, und = 0, None, 0
    cases = [  # (p, l1, q, l, l1*, alpha)
        (2, R(3), 1, R(2), R(1), R(1)),
        (1, R(4), 2, R(2), R(1), R(2)),
        (2, R(5), 2, R(3), R(2), R(3, 10)),
        (3, R(2), 1, R(1), R(1, 2), R(13, 10)),
        (2, R(4), 2, R(4), R(2), R(5)),
    ]
    for p, l1, q, l, ls, a in cases:
        assert ls <= min(l, l1)
        X = dmax([l1] * p + [l] * q, a)
        Y = dmax([ls] * p + [l] * q, a)
        h, w, u = cf.check("lr", X, Y)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def example_4_5():
    """Printed: alpha=2, lam=(3/2,2), theta=(1,5/2): X NOT <=lr Y.
    Confirm by a strict witness against X <=lr Y."""
    X = dmax([R(3, 2), R(2)], R(2))
    Y = dmax([R(1), R(5, 2)], R(2))
    h, w, u = cf.check("lr", X, Y)
    return w is not None, w, u, 1


def example_4_10():
    """Printed: lam=1/5, l1=7/2, l1*=2 (violates min condition) =>
    X NOT <=lr Y for alpha=0.3 and alpha=1.3."""
    res = []
    for a in (R(3, 10), R(13, 10)):
        X = dmax([R(7, 2), R(1, 5)], a)
        Y = dmax([R(2), R(1, 5)], a)
        h, w, u = cf.check("lr", X, Y)
        res.append((w is not None, w, u))
    return all(r[0] for r in res), res[0][1], sum(r[2] for r in res), 2


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.1239_jap_1429282609.json")))
    results = []
    for recd in canon:
        order = recd["conclusion"]["order"]
        label = recd["claim"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        if label in ("Corollary 4.2", "Theorem 4.1"):
            n_, w, u = th_rh()
        elif label == "Theorem 4.4":
            n_, w, u = th_4_4()
        elif label == "Theorem 4.7":
            n_, w, u = th_4_7()
        elif label == "Theorem 4.9":
            n_, w, u = th_4_9()
        elif label == "Theorem 4.11":
            n_, w, u = th_4_11()
        elif label == "Theorem 4.13":
            n_, w, u = th_4_13()
        elif label == "Example 4.5":
            ok, w, u, n_ = example_4_5()
            results.append(rec(recd, "holds" if ok else "refuted",
                               instances=n_, witness=w, undecided=u))
            continue
        elif label == "Example 4.10":
            ok, w, u, n_ = example_4_10()
            results.append(rec(recd, "holds" if ok else "refuted",
                               instances=n_, witness=w, undecided=u))
            continue
        else:
            results.append(rec(recd, "out of harness scope"))
            continue
        results.append(rec(recd, "holds" if w is None else "refuted",
                           instances=n_, witness=w, undecided=u))
    out = os.path.join(HERE, "eval_doi_10.1239_jap_1429282609.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
