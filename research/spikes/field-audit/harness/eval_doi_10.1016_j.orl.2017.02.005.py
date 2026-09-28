"""Evaluation of canonical claims for doi:10.1016/j.orl.2017.02.005
(log-Lindley parallel systems).

LL(sigma, lam): f(x) = s^2/(1+lam s) (lam - ln x) x^{s-1}, 0 < x < 1.
F(x) = x^s (1 + lam s - s ln x)/(1 + lam s);   S = 1 - F.
Largest order statistic F_{n:n} = prod_i F_i.

Theorem 3.1: sigma >=^m theta, sigma,theta,lam all in D+ or all in E+
             => X_{n:n} >=rh Y_{n:n}  (test Y <=rh X).
Theorem 3.2: sigma common, lam >=^m delta, orderings opposite
             => X_{n:n} <=rh Y_{n:n}  (test X <=rh Y).
Theorem 3.3: as 3.1 plus lam_i sigma_i > 1/2 => X >=lr Y (test Y <=lr X).
Theorem 3.4: multiple-outlier shapes => X_{n:n} >=lr Y_{n:n}.
Theorem 3.5: as 3.2 => X_{n:n} <=lr Y_{n:n}  (test X <=lr Y).
Counterexamples: records assert a failure; finding a strict-enclosure
witness of the failure confirms the printed claim -> 'holds'.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def F_ll(s, lam):
    s, lam = R(s), R(lam)
    return x ** s * (1 + lam * s - s * sp.log(x)) / (1 + lam * s)


def S_ll(s, lam):
    return 1 - F_ll(s, lam)


def F_max(params):
    """cdf of max of independent LL(s_i, lam_i) on (0,1)."""
    return sp.prod([F_ll(s, l) for s, l in params])


def dist_max(params):
    return Closed(1 - F_max(params), 0, 1)


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


def maj(a, b):
    """a majorizes b: sorted-desc partial sums >=, equal totals."""
    a, b = sorted(a, reverse=True), sorted(b, reverse=True)
    return (sum(a) == sum(b)
            and all(sum(a[:k]) >= sum(b[:k]) for k in range(len(a))))


def theorem_3_1():
    """sigma ~m theta, all vectors same order class => X_{n:n} >=rh Y_{n:n}."""
    n, wit, und = 0, None, 0
    cases = [  # (sigma, theta, lam)
        # all E+ (nondecreasing)
        ([R(1), R(2), R(4)], [R(3, 2), R(2), R(7, 2)], [R(1), R(2), R(3)]),
        # all D+ (nonincreasing)
        ([R(4), R(2), R(1)], [R(7, 2), R(2), R(3, 2)], [R(3), R(2), R(1)]),
        ([R(1), R(1), R(5)], [R(1), R(2), R(4)], [R(1, 2), R(2), R(4)]),  # E+
        ([R(5), R(1), R(1)], [R(4), R(2), R(1)], [R(4), R(2), R(1, 2)]),  # D+
    ]
    for sig, th, lam in cases:
        assert maj(list(sig), list(th))
        X = dist_max(list(zip(sig, lam)))
        Y = dist_max(list(zip(th, lam)))
        h, w, u = cf.check("rh", Y, X)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def theorem_3_2():
    """lam ~m delta, sigma ordered oppositely => X_{n:n} <=rh Y_{n:n}."""
    n, wit, und = 0, None, 0
    cases = [  # (sigma, lam, delta)
        ([R(1), R(2), R(4)], [R(4), R(3), R(1)], [R(3), R(3), R(2)]),  # sig E+, lam/del D+
        ([R(4), R(2), R(1)], [R(1), R(2), R(4)], [R(1), R(3), R(3)]),  # sig D+, lam/del E+
        ([R(1), R(1), R(5)], [R(4), R(2), R(1)], [R(3), R(2), R(2)]),  # E+ vs D+
        ([R(5), R(1), R(1)], [R(1), R(3), R(4)], [R(2), R(3), R(3)]),  # D+ vs E+
    ]
    for sig, lam, dl in cases:
        assert maj(list(lam), list(dl))
        X = dist_max(list(zip(sig, lam)))
        Y = dist_max(list(zip(sig, dl)))
        h, w, u = cf.check("rh", X, Y)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def theorem_3_3():
    """As 3.1 with lam_i sigma_i > 1/2 => X_{n:n} >=lr Y_{n:n}."""
    n, wit, und = 0, None, 0
    cases = [
        ([R(1), R(2), R(4)], [R(3, 2), R(2), R(7, 2)], [R(1), R(2), R(3)]),
        ([R(4), R(2), R(1)], [R(7, 2), R(2), R(3, 2)], [R(3), R(2), R(1)]),
        ([R(1), R(1), R(5)], [R(1), R(2), R(4)], [R(1), R(2), R(3)]),
    ]
    for sig, th, lam in cases:
        assert maj(list(sig), list(th))
        assert all(l * s > R(1, 2) for s, l in zip(sig, lam))
        assert all(l * t > R(1, 2) for t, l in zip(th, lam))
        X = dist_max(list(zip(sig, lam)))
        Y = dist_max(list(zip(th, lam)))
        h, w, u = cf.check("lr", Y, X)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def theorem_3_4():
    """Multiple-outlier: n1 at (sig,lam), n2 at (sig*,lam*) vs (th,..);
    shape vector majorization + consistent triple ordering => X >=lr Y."""
    n, wit, und = 0, None, 0
    cases = [  # (sig, sig*, th, th*, lam, lam*, n1, n2)
        (R(3), R(1), R(5, 2), R(2), R(2), R(1), 2, 1),   # X:(3,3,1) Y:(5/2,5/2,2)
        (R(1), R(4), R(3, 2), R(15, 4), R(1), R(2), 1, 2),  # X:(1,4,4) Y:(3/2,15/4,15/4)
        (R(4), R(2), R(7, 2), R(5, 2), R(3), R(2), 2, 2),# X:(4,4,2,2) Y:(7/2,7/2,5/2,5/2)
    ]
    for sig, sigs, th, ths, lam, lams, n1, n2 in cases:
        vs = [sig] * n1 + [sigs] * n2
        ws = [th] * n1 + [ths] * n2
        assert maj(vs, ws)
        assert (sig >= sigs and th >= ths and lam >= lams) or \
               (sig <= sigs and th <= ths and lam <= lams)
        X = dist_max([(sig, lam)] * n1 + [(sigs, lams)] * n2)
        Y = dist_max([(th, lam)] * n1 + [(ths, lams)] * n2)
        h, w, u = cf.check("lr", Y, X)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def theorem_3_5():
    """As 3.2 => X_{n:n} <=lr Y_{n:n}."""
    n, wit, und = 0, None, 0
    cases = [
        ([R(1), R(2), R(4)], [R(4), R(3), R(1)], [R(3), R(3), R(2)]),
        ([R(4), R(2), R(1)], [R(1), R(2), R(4)], [R(1), R(3), R(3)]),
    ]
    for sig, lam, dl in cases:
        assert maj(list(lam), list(dl))
        X = dist_max(list(zip(sig, lam)))
        Y = dist_max(list(zip(sig, dl)))
        h, w, u = cf.check("lr", X, Y)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def counterexample_3_1():
    """Printed claim: rh fails (F3:3/G3:3 non-monotone). Confirm by finding
    a witness against X >=rh Y, i.e. Y <=rh X fails."""
    sig = [R(1), R(1), R(5)]
    th = [R(1), R(2), R(4)]
    lam = [R(4), R(3), R(1, 5)]
    assert maj(sig, th)
    X = dist_max(list(zip(sig, lam)))
    Y = dist_max(list(zip(th, lam)))
    h, w, u = cf.check("rh", Y, X)   # expect failure -> w not None
    return w is not None, w, u, 1


def counterexample_3_2():
    """sigma=(2,3,5): printed F/G decreasing => X <=rh Y fails. Confirm witness.
    sigma=(0.1,3,5): printed increasing => consistent (probe, no witness expected)."""
    lam = [R(1, 10), R(3, 10), R(41, 10)]
    dl = [R(1, 5), R(3, 10), R(4)]
    assert maj(lam, dl)
    res = []
    for sig in ([R(2), R(3), R(5)], [R(1, 10), R(3), R(5)]):
        X = dist_max(list(zip(sig, lam)))
        Y = dist_max(list(zip(sig, dl)))
        h, w, u = cf.check("rh", X, Y)
        res.append((h, w, u))
    # first must fail (witness), second is a consistency probe
    return res[0][1] is not None and res[1][0], res[0][1], res[0][2] + res[1][2], 2


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.1016_j.orl.2017.02.005.json")))
    results = []
    for recd in canon:
        order = recd["conclusion"]["order"]
        label = recd["claim"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        if label == "Counterexample 3.1":
            ok, w, u, n_ = counterexample_3_1()
            results.append(rec(recd, "holds" if ok else "refuted",
                               instances=n_, witness=w, undecided=u))
            continue
        if label == "Counterexample 3.2":
            ok, w, u, n_ = counterexample_3_2()
            results.append(rec(recd, "holds" if ok else "refuted",
                               instances=n_, witness=w, undecided=u))
            continue
        fn = {"Theorem 3.1": theorem_3_1, "Theorem 3.2": theorem_3_2,
              "Theorem 3.3": theorem_3_3, "Theorem 3.4": theorem_3_4,
              "Theorem 3.5": theorem_3_5}.get(label)
        if fn is None:
            results.append(rec(recd, "out of harness scope"))
            continue
        n_, w, u = fn()
        results.append(rec(recd, "holds" if w is None else "refuted",
                           instances=n_, witness=w, undecided=u))
    out = os.path.join(HERE, "eval_doi_10.1016_j.orl.2017.02.005.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
