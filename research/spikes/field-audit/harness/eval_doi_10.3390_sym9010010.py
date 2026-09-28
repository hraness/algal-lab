"""Evaluation of canonical claims for doi:10.3390/sym9010010 (Frechet systems).

Frechet(mu, theta, alpha): F(x) = exp(-theta^alpha (x-mu)^{-alpha}), x > mu.
Location mu = 0 throughout (common mu cancels in the orderings).
  parallel max: F_{n:n} = exp(-(sum theta_i^alpha) x^{-alpha})
  series min:   S_{1:n} = prod(1 - exp(-theta_i^alpha x^{-alpha}))

Theorem 1:  shape vectors alpha ~m alpha* (common theta) =>
            X_{n:n} >=st Y_{n:n} and X_{1:n} <=st Y_{1:n}.
Theorem 2:  (1/theta_i) weak-upper-majorizes (1/theta*_i) (paper Def. 2(2))
            => X_{n:n} >=rh Y_{n:n}.
Lemma 5:    0 < alpha <= 1, theta ~m theta* => X_{1:n} <=lr Y_{1:n}.
Theorem 3:  sum theta_i^alpha >= sum theta*_i^alpha => X_{n:n} >=lr Y_{n:n}.
Theorem 4:  theta = (prod theta_i)^{1/n} => X_{n:n} >=lr Y_{n:n}.
Theorem 5:  X heterogeneous theta_i vs homogeneous theta*:
   (1) theta*^alpha = (1/n) sum theta_i^alpha => X_{1:n} <=lr Y_{1:n};
   (2) 0<alpha<=1, theta* = arithmetic mean => X_{1:n} <=lr Y_{1:n}.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def rat(v):
    return v if isinstance(v, sp.Basic) else R(v)


def S_fre(t, a):
    return 1 - sp.exp(-rat(t) ** R(a) * x ** (-R(a)))


def F_fre(t, a):
    return sp.exp(-rat(t) ** R(a) * x ** (-R(a)))


def parallel_S(ts, a):
    """Survival of max of independent Fre(ts_i, a): 1 - prod F_i."""
    return 1 - sp.prod([F_fre(t, a) for t in ts])


def series_S(ts, a):
    return sp.prod([S_fre(t, a) for t in ts])


def parallel_S_shape(t, alphas):
    return 1 - sp.prod([F_fre(t, a) for a in alphas])


def series_S_shape(t, alphas):
    return sp.prod([S_fre(t, a) for a in alphas])


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


def maj(a, b):
    """a majorizes b: sorted-desc partial sums >=, equal totals."""
    a, b = sorted(a, reverse=True), sorted(b, reverse=True)
    return sum(a) == sum(b) and all(
        sum(a[:k]) >= sum(b[:k]) for k in range(len(a)))


def weak_upper(a, b):
    """a weakly upper-majorizes b (paper Def. 2(2)): ascending partial sums
    of a <= those of b and total a <= total b."""
    a, b = sorted(a), sorted(b)
    return sum(a) <= sum(b) and all(
        sum(a[:k]) <= sum(b[:k]) for k in range(1, len(a)))


def theorem_1_parallel():
    """alpha ~m alpha* => X_{n:n} >=st Y_{n:n} (test Y <=st X)."""
    n, wit, und = 0, None, 0
    cases = [  # (alphas, alpha*s, theta)
        ([R(3), R(1)], [R(2), R(2)], R(1)),
        ([R(4), R(2), R(1)], [R(3), R(5, 2), R(3, 2)], R(2)),
        ([R(1), R(1), R(4)], [R(2), R(2), R(2)], R(1)),
        ([R(1, 2), R(2)], [R(1), R(3, 2)], R(3)),
    ]
    for al, al2, th in cases:
        assert maj(al, al2)
        X = Closed(parallel_S_shape(th, al))
        Y = Closed(parallel_S_shape(th, al2))
        h, w, u = cf.check("st", Y, X)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def theorem_1_series():
    """alpha ~m alpha* => X_{1:n} <=st Y_{1:n}."""
    n, wit, und = 0, None, 0
    cases = [
        ([R(3), R(1)], [R(2), R(2)], R(1)),
        ([R(4), R(2), R(1)], [R(3), R(5, 2), R(3, 2)], R(2)),
        ([R(1), R(1), R(4)], [R(2), R(2), R(2)], R(1)),
    ]
    for al, al2, th in cases:
        assert maj(al, al2)
        X = Closed(series_S_shape(th, al))
        Y = Closed(series_S_shape(th, al2))
        h, w, u = cf.check("st", X, Y)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def theorem_2():
    """(1/th_i) weakly upper-majorizes (1/th*_i) => X_{n:n} >=rh Y_{n:n}."""
    n, wit, und = 0, None, 0
    cases = [  # (thetas, theta*s, alpha)
        ([R(2), R(3), R(6)], [R(2), R(2), R(2)], R(1)),      # recip (1/6,1/3,1/2) vs (1/2,1/2,1/2): w.u.m. holds
        ([R(3), R(4), R(4)], [R(2), R(3), R(3)], R(2)),      # recip asc (1/4,1/4,1/3) vs (1/3,1/3,1/2)
        ([R(4), R(4), R(2)], [R(3), R(3), R(3)], R(1, 2)),   # recip (1/4,1/4,1/2) vs (1/3,1/3,1/3)
    ]
    for ts, tss, a in cases:
        assert weak_upper([1 / t for t in ts], [1 / t for t in tss]), (ts, tss)
        X = Closed(parallel_S(ts, a))
        Y = Closed(parallel_S(tss, a))
        h, w, u = cf.check("rh", Y, X)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def lemma_5():
    """0 < alpha <= 1, theta ~m theta* => X_{1:n} <=lr Y_{1:n}."""
    n, wit, und = 0, None, 0
    cases = [
        ([R(1), R(3)], [R(2), R(2)], R(1)),
        ([R(1), R(2), R(6)], [R(2), R(3), R(4)], R(1)),
        ([R(1), R(1), R(4)], [R(2), R(2), R(2)], R(1)),
        ([R(1), R(64)], [R(16), R(49)], R(1, 2)),   # majorized, all squares
        ([R(4), R(81)], [R(36), R(49)], R(1, 2)),
    ]
    for ts, tss, a in cases:
        assert maj(list(ts), list(tss))
        assert all((t ** a).is_Rational for t in list(ts) + list(tss))
        X = Closed(series_S(ts, a))
        Y = Closed(series_S(tss, a))
        h, w, u = cf.check("lr", X, Y)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def theorem_3():
    n, wit, und = 0, None, 0
    cases = [
        ([R(1), R(2), R(4)], [R(2), R(2), R(3)], R(1)),   # 7 vs 7 alpha=1
        ([R(1), R(2), R(6)], [R(2), R(3), R(3)], R(1)),   # 9 vs 8
        ([R(1), R(4), R(4)], [R(2), R(3), R(3)], R(2)),   # 9 vs 4+9+9=22? 1+16+16=33 vs 4+9+9=22
        ([R(4), R(1), R(1)], [R(2), R(2), R(1)], R(1, 2)),# 2+1+1 vs 2sqrt2+1
    ]
    for ts, tss, a in cases:
        assert sum(t ** a for t in ts) >= sum(t ** a for t in tss)
        X = Closed(parallel_S(ts, a))
        Y = Closed(parallel_S(tss, a))
        h, w, u = cf.check("lr", Y, X)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def theorem_4():
    """theta = geometric mean of theta_i => X_{n:n} >=lr Y_{n:n}.
    Instances chosen so that both the geometric mean and every theta_i^alpha
    remain rational (interval evaluator handles rationals only)."""
    n, wit, und = 0, None, 0
    for ts, a in [([R(1), R(1), R(8)], R(1)), ([R(1), R(4), R(16)], R(1)),
                  ([R(1), R(8), R(64)], R(2)), ([R(1), R(3), R(9)], R(2)),
                  ([R(1), R(4), R(16)], R(1, 2)), ([R(1), R(2), R(32)], R(1))]:
        gm = sp.prod([R(t) for t in ts]) ** (1 / R(len(ts)))
        assert gm.is_Rational and all((t ** a).is_Rational for t in ts)
        X = Closed(parallel_S(ts, a))
        Y = Closed(parallel_S([gm] * len(ts), a))
        h, w, u = cf.check("lr", Y, X)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def series_S_eff(ss, a):
    """Series system with per-component effective scales s_i = theta_i^alpha."""
    return sp.prod([1 - sp.exp(-R(s) * x ** (-R(a))) for s in ss])


def theorem_5(part):
    n, wit, und = 0, None, 0
    cases = [
        ([R(1), R(2), R(4)], R(1)),
        ([R(1), R(4), R(9)], R(1)),
        ([R(1), R(4), R(9)], R(1, 2)),
        ([R(1), R(2), R(3)], R(2)),
    ] if part == 1 else [
        ([R(1), R(2), R(4)], R(1)),
        ([R(1), R(4), R(9)], R(1)),
        ([R(1), R(25), R(49)], R(1, 2)),      # mean=25 -> sqrt = 5
        ([R(1), R(4), R(4), R(16)], R(1, 2)), # mean=25/4 -> 5/2
    ]
    for ts, a in cases:
        effs = [R(t) ** a for t in ts]
        assert all(s.is_Rational for s in effs)
        if part == 1:
            s_star = sum(effs) / len(effs)          # theta*^alpha = mean of theta_i^alpha
        else:
            t_star = sum(R(t) for t in ts) / len(ts)  # arithmetic mean theta*
            s_star = t_star ** a
            assert s_star.is_Rational
            assert a <= 1
        X = Closed(series_S_eff(effs, a))
        Y = Closed(series_S_eff([s_star] * len(effs), a))
        h, w, u = cf.check("lr", X, Y)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.3390_sym9010010.json")))
    results = []
    for recd in canon:
        order = recd["conclusion"]["order"]
        label = recd["claim"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        if label == "Theorem 2":
            n_, w, u = theorem_2()
        elif label == "Lemma 5":
            n_, w, u = lemma_5()
        elif "parallel" in label:
            n_, w, u = theorem_1_parallel()
        elif "series" in label:
            n_, w, u = theorem_1_series()
        elif label == "Theorem 3":
            n_, w, u = theorem_3()
        elif label == "Theorem 4":
            n_, w, u = theorem_4()
        elif label == "Theorem 5(1)":
            n_, w, u = theorem_5(1)
        elif label == "Theorem 5(2)":
            n_, w, u = theorem_5(2)
        else:
            results.append(rec(recd, "out of harness scope"))
            continue
        results.append(rec(recd, "holds" if w is None else "refuted",
                           instances=n_, witness=w, undecided=u))
    out = os.path.join(HERE, "eval_doi_10.3390_sym9010010.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
