"""Evaluation of canonical claims for doi:10.1080/02331888.2017.1353516
(Kw-G series systems; smallest order statistics).

Kw-G(alpha, beta, F): survival S(x) = (1 - F(x)^alpha)^beta.
Series system (minimum): S_{1:n} = prod_i (1 - F_i^{a_i})^{b_i}.

Single-parent theorems use F = uniform (F(x)=x on (0,1)).
Two-parent theorems use F1=x, F2=x^2 on (0,1) [st: X2 larger], or
F1=Exp(2), F2=Exp(1) on (0,oo) [powered-hr condition: (1-F2^s)/(1-F1^s)
= 1/(1+e^{-sx}) increasing for all s>0].
Counterexample 4.1 uses the paper's own Weibull parents.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_series(params, F):
    """prod (1 - F^{a_i})^{b_i}; params = [(a_i, b_i)]; F sympy cdf."""
    return sp.prod([(1 - F ** R(a)) ** R(b) for a, b in params])


def dist(params, F, lo=0, hi=1):
    return Closed(S_series(params, F), lo, hi)


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


def noninc(v):
    return all(v[i] >= v[i + 1] for i in range(len(v) - 1))


def nondec(v):
    return all(v[i] <= v[i + 1] for i in range(len(v) - 1))


def maj(a, b):
    """a majorizes b (equal sums, descending partial sums >=)."""
    a, b = sorted(a, reverse=True), sorted(b, reverse=True)
    return sum(a) == sum(b) and all(
        sum(a[:k]) >= sum(b[:k]) for k in range(len(a)))


def check_cases(order, ucases, vcases, lo=0, hi=1, rev=False):
    n, wit, und = 0, None, 0
    for U, V, FU, FV in zip(ucases, vcases):
        Du = dist(U, FU, lo, hi)
        Dv = dist(V, FV, lo, hi)
        a, b = (Dv, Du) if rev else (Du, Dv)
        h, w, u = cf.check(order, a, b)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


Fx = x
F2x = x ** 2
Fexp2 = 1 - sp.exp(-2 * x)
Fexp1 = 1 - sp.exp(-x)
Fexphalf = 1 - sp.exp(-x / 2)


def theorem_3_1():
    """alpha ~w gamma (use equal-sum majorization), alpha,gamma noninc,
    beta nondec => U <=hr V."""
    cases = [
        ([(R(4), R(1)), (R(2), R(2)), (R(1), R(3))],
         [(R(3), R(1)), (R(2), R(2)), (R(2), R(3))]),
        ([(R(5), R(1)), (R(1), R(2))],
         [(R(4), R(1)), (R(2), R(2))]),
        ([(R(3), R(1)), (R(2), R(1)), (R(1), R(2))],
         [(R(5, 2), R(1)), (R(2), R(1)), (R(3, 2), R(2))]),
    ]
    n, wit, und = 0, None, 0
    for U, V in cases:
        al = [p[0] for p in U]; ga = [p[0] for p in V]
        be = [p[1] for p in U]
        assert noninc(al) and noninc(ga) and nondec(be) and maj(al, ga)
        h, w, u = cf.check("hr", dist(U, Fx), dist(V, Fx))
        n += 1; und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def theorem_3_2(part):
    """(i): beta ~m delta nondec, alpha noninc => U <=hr V.
    (ii): both vectors nonincreasing => U >=hr V."""
    if part == 1:
        cases = [  # alpha common noninc; beta,delta nondec; beta ~m delta
            ([(R(3), R(1)), (R(2), R(2)), (R(1), R(4))],
             [(R(3), R(1)), (R(2), R(3)), (R(1), R(3))]),   # beta=(1,2,4) delta=(1,3,3)
            ([(R(4), R(1)), (R(2), R(2))],
             [(R(4), R(1)), (R(2), R(2))]),                # beta=(1,2) delta=(1,2)? need spread
        ]
        # replace second: beta=(1,3), delta=(2,2)
        cases[1] = ([(R(4), R(1)), (R(2), R(3))],
                    [(R(4), R(2)), (R(2), R(2))])
        n, wit, und = 0, None, 0
        for U, V in cases:
            be = [p[1] for p in U]; de = [p[1] for p in V]
            al = [p[0] for p in U]
            assert nondec(be) and nondec(de) and noninc(al) and maj(be, de)
            h, w, u = cf.check("hr", dist(U, Fx), dist(V, Fx))
            n += 1; und += u
            if not h and wit is None:
                wit = w
        return n, wit, und
    else:
        cases = [  # beta,delta nonincreasing, beta ~m delta, alpha common noninc
            ([(R(3), R(4)), (R(2), R(2)), (R(1), R(1))],
             [(R(3), R(3)), (R(2), R(3)), (R(1), R(1))]),
            ([(R(4), R(3)), (R(2), R(1))],
             [(R(4), R(2)), (R(2), R(2))]),
        ]
        n, wit, und = 0, None, 0
        for U, V in cases:
            be = [p[1] for p in U]; de = [p[1] for p in V]
            al = [p[0] for p in U]
            assert noninc(be) and noninc(de) and noninc(al) and maj(be, de)
            h, w, u = cf.check("hr", dist(V, Fx), dist(U, Fx))
            n += 1; und += u
            if not h and wit is None:
                wit = w
        return n, wit, und


def theorem_3_3(part):
    """(i): beta weakly submajorizes delta (tail sums >=), beta,delta nondec,
    alpha noninc => U <=hr V.
    (ii): beta weakly supermajorizes delta (ascending partial sums <=),
    both noninc => U >=hr V."""
    if part == 1:
        pairs = [  # (beta-vector asc, delta-vector asc): tail sums beta >= delta
            ([R(1), R(2), R(5)], [R(1), R(2), R(3)]),
            ([R(1), R(3), R(6)], [R(2), R(3), R(4)]),
        ]
        n, wit, und = 0, None, 0
        for be, de in pairs:
            assert all(sum(sorted(be, reverse=True)[:k]) >= sum(sorted(de, reverse=True)[:k])
                       for k in range(1, len(be) + 1))
            al = sorted([R(3), R(2), R(1)], reverse=True)
            U = list(zip(al, be)); V = list(zip(al, de))
            h, w, u = cf.check("hr", dist(U, Fx), dist(V, Fx))
            n += 1; und += u
            if not h and wit is None:
                wit = w
        return n, wit, und
    else:
        pairs = [
            ([R(5), R(2), R(1)], [R(3), R(3), R(2)]),  # noninc; asc partials: (1,3,8) <= (2,5,8)
            ([R(4), R(2), R(1)], [R(3), R(3), R(2)]),  # asc (1,3,7) <= (2,5,8)? no: total 7<8 ok for supermaj
        ]
        n, wit, und = 0, None, 0
        for be, de in pairs:
            assert noninc(be) and noninc(de)
            ba, da = sorted(be), sorted(de)
            assert all(sum(ba[:k]) <= sum(da[:k]) for k in range(1, len(ba) + 1))
            al = [R(3), R(2), R(1)]
            U = list(zip(al, be)); V = list(zip(al, de))
            h, w, u = cf.check("hr", dist(V, Fx), dist(U, Fx))
            n += 1; und += u
            if not h and wit is None:
                wit = w
        return n, wit, und


def theorem_3_4():
    """Multiple-outlier: n1 (al,be) vs (ga,be), n2 (al*,be*) vs (ga*,be*);
    al>al*, ga>ga*, be<be*, alpha-block ~m gamma-block => U <=lr V."""
    n, wit, und = 0, None, 0
    cases = [  # (al, al*, be, be*, ga, ga*, n1, n2)
        (R(3), R(1), R(1), R(2), R(5, 2), R(2), 2, 1),      # (3,3,1) vs (5/2,5/2,2)
        (R(4), R(2), R(1), R(3), R(7, 2), R(3), 2, 1),      # (4,4,2) vs (7/2,7/2,3)
        (R(3), R(1), R(2), R(4), R(5, 2), R(3, 2), 2, 2),  # (3,3,1,1) vs (5/2,5/2,3/2,3/2)
    ]
    for al, als, be, bes, ga, gas, n1, n2 in cases:
        vb = [al] * n1 + [als] * n2
        vg = [ga] * n1 + [gas] * n2
        assert al > als and ga > gas and be < bes
        assert maj(vb, vg)
        U = [(al, be)] * n1 + [(als, bes)] * n2
        V = [(ga, be)] * n1 + [(gas, bes)] * n2
        h, w, u = cf.check("lr", dist(U, Fx), dist(V, Fx))
        n += 1; und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def theorem_3_5(part):
    """Block beta-vector ~m block delta-vector.
    (i) al>al*, be>be*, de<de* => U >=lr V.
    (ii) al>al*, be<be*, de<de* => U <=lr V."""
    if part == 1:
        cases = [  # (al, al*, be, be*, de, de*, n1, n2)
            (R(3), R(1), R(3), R(1), R(2), R(3), 2, 1),  # beta (3,3,1) vs delta (2,2,3)
            (R(4), R(1), R(2), R(1), R(1), R(2), 2, 2),  # (2,2,1,1) vs (1,1,2,2)
        ]
    else:
        cases = [
            (R(3), R(1), R(1), R(3), R(3, 2), R(2), 2, 1),  # beta (1,1,3) vs delta (3/2,3/2,2)
            (R(4), R(1), R(1), R(3), R(2), R(5, 2), 1, 2),  # beta (1,3,3) vs delta (2,5/2,5/2)
        ]
    n, wit, und = 0, None, 0
    for al, als, be, bes, de, des, n1, n2 in cases:
        vb = [be] * n1 + [bes] * n2
        vd = [de] * n1 + [des] * n2
        assert al > als
        assert (be > bes if part == 1 else be < bes)
        assert de < des
        assert maj(vb, vd), (vb, vd)
        U = [(al, be)] * n1 + [(als, bes)] * n2
        V = [(al, de)] * n1 + [(als, des)] * n2
        a, b = (dist(V, Fx), dist(U, Fx)) if part == 1 else (dist(U, Fx), dist(V, Fx))
        h, w, u = cf.check("lr", a, b)
        n += 1; und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def theorem_4_1():
    """U~Kw-G(al_i,be_i,F1), V~Kw-G(ga_i,be_i,F2), F1>=F2 (X1 st-smaller),
    al ~m ga, al,ga noninc, be nondec => U <=st V."""
    n, wit, und = 0, None, 0
    cases = [
        ([(R(4), R(1)), (R(2), R(2)), (R(1), R(3))],
         [(R(3), R(1)), (R(2), R(2)), (R(2), R(3))]),
        ([(R(3), R(1)), (R(1), R(2))],
         [(R(2), R(1)), (R(2), R(2))]),
    ]
    for U, V in cases:
        al = [p[0] for p in U]; ga = [p[0] for p in V]
        assert noninc(al) and noninc(ga) and maj(al, ga)
        h, w, u = cf.check("st", dist(U, Fx), dist(V, F2x))
        n += 1; und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def theorem_4_2(part):
    """Common alpha; beta ~m delta.
    (i) beta,delta nondec, F1>=F2 => U <=st V.
    (ii) beta,delta noninc, F1<=F2 => U >=st V."""
    n, wit, und = 0, None, 0
    if part == 1:
        cases = [
            ([(R(3), R(1)), (R(2), R(2)), (R(1), R(4))],
             [(R(3), R(1)), (R(2), R(3)), (R(1), R(3))], Fx, F2x),
            ([(R(4), R(1)), (R(2), R(3))],
             [(R(4), R(2)), (R(2), R(2))], Fx, F2x),
        ]
        for U, V, FU, FV in cases:
            be = [p[1] for p in U]; de = [p[1] for p in V]
            assert nondec(be) and nondec(de) and maj(be, de)
            h, w, u = cf.check("st", dist(U, FU), dist(V, FV))
            n += 1; und += u
            if not h and wit is None:
                wit = w
    else:
        cases = [
            ([(R(3), R(4)), (R(2), R(2)), (R(1), R(1))],
             [(R(3), R(3)), (R(2), R(3)), (R(1), R(1))], F2x, Fx),
            ([(R(4), R(3)), (R(2), R(1))],
             [(R(4), R(2)), (R(2), R(2))], F2x, Fx),
        ]
        for U, V, FU, FV in cases:
            be = [p[1] for p in U]; de = [p[1] for p in V]
            assert noninc(be) and noninc(de) and maj(be, de)
            h, w, u = cf.check("st", dist(V, FV), dist(U, FU))
            n += 1; und += u
            if not h and wit is None:
                wit = w
    return n, wit, und


def theorem_4_3():
    """Powered-hr parent condition holds for F1=Exp(2), F2=Exp(1);
    al ~m ga => U <=hr V."""
    n, wit, und = 0, None, 0
    cases = [
        ([(R(4), R(1)), (R(2), R(2)), (R(1), R(3))],
         [(R(3), R(1)), (R(2), R(2)), (R(2), R(3))]),
        ([(R(3), R(1)), (R(1), R(2))],
         [(R(2), R(1)), (R(2), R(2))]),
    ]
    for U, V in cases:
        al = [p[0] for p in U]; ga = [p[0] for p in V]
        assert noninc(al) and noninc(ga) and maj(al, ga)
        h, w, u = cf.check("hr", dist(U, Fexp2, 0, sp.oo),
                             dist(V, Fexp1, 0, sp.oo))
        n += 1; und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def theorem_4_4(part):
    """(i) beta,delta nondec, X1 hr-smaller (F1=Exp(2)) => U <=hr V.
    (ii) beta,delta noninc, X1 hr-larger (F1=Exp(1/2) vs F2=Exp(1)) => U >=hr V."""
    n, wit, und = 0, None, 0
    if part == 1:
        cases = [
            ([(R(3), R(1)), (R(2), R(2)), (R(1), R(4))],
             [(R(3), R(1)), (R(2), R(3)), (R(1), R(3))]),
        ]
        for U, V in cases:
            be = [p[1] for p in U]; de = [p[1] for p in V]
            assert nondec(be) and nondec(de) and maj(be, de)
            h, w, u = cf.check("hr", dist(U, Fexp2, 0, sp.oo),
                                 dist(V, Fexp1, 0, sp.oo))
            n += 1; und += u
            if not h and wit is None:
                wit = w
    else:
        cases = [
            ([(R(3), R(4)), (R(2), R(2)), (R(1), R(1))],
             [(R(3), R(3)), (R(2), R(3)), (R(1), R(1))]),
        ]
        for U, V in cases:
            be = [p[1] for p in U]; de = [p[1] for p in V]
            assert noninc(be) and noninc(de) and maj(be, de)
            h, w, u = cf.check("hr", dist(V, Fexp1, 0, sp.oo),
                                 dist(U, Fexphalf, 0, sp.oo))
            n += 1; und += u
            if not h and wit is None:
                wit = w
    return n, wit, und


def counterexample_3_1():
    """Claim: no lr ordering (g1:3/h1:3 non-monotone). Confirm via witnesses
    against both directions. Parent F = uniform."""
    U = [(R(62, 10), R(1)), (R(41, 10), R(2)), (R(2), R(3))]
    V = [(R(52, 10), R(1)), (R(51, 10), R(2)), (R(2), R(3))]
    DU, DV = dist(U, Fx), dist(V, Fx)
    h1, w1, u1 = cf.check("lr", DU, DV)
    h2, w2, u2 = cf.check("lr", DV, DU)
    # printed claim is "no lr ordering": must fail in BOTH directions
    return (w1 is not None) and (w2 is not None), \
        w1 if w1 is not None else w2, u1 + u2, 2


def counterexample_3_2():
    """Two parameter assignments; claim: lr fails (non-monotone ratio)."""
    al = [R(5), R(1), R(1, 100)]
    res = []
    for be, de in [([R(5, 1000), R(4, 1000), R(1, 1000)],
                    [R(45, 10000), R(45, 10000), R(1, 1000)]),
                   ([R(3, 1000), R(4, 1000), R(5, 1000)],
                    [R(35, 10000), R(35, 10000), R(5, 1000)])]:
        U = list(zip(al, be)); V = list(zip(al, de))
        h1, w1, u1 = cf.check("lr", dist(U, Fx), dist(V, Fx))
        h2, w2, u2 = cf.check("lr", dist(V, Fx), dist(U, Fx))
        # "non-monotone ratio" => lr fails in both directions
        res.append((w1 is not None and w2 is not None,
                    w1 if w1 is not None else w2, u1 + u2))
    return all(r[0] for r in res), \
        next((r[1] for r in res if r[1] is not None), None), \
        sum(r[2] for r in res), 4


def counterexample_4_1():
    """Claim: U1:n <=hr V1:n still holds with the printed params
    (alpha=(1.99,0.01), gamma=(1.98,0.02), beta=(1,2)) under Weibull parents
    F1=1-e^{-3x^4.4}, F2=1-e^{-0.2x^0.4}. Confirmation = check holds."""
    F1 = 1 - sp.exp(-3 * x ** R(44, 10))
    F2 = 1 - sp.exp(-R(1, 5) * x ** R(2, 5))
    U = [(R(199, 100), R(1)), (R(1, 100), R(2))]
    V = [(R(198, 100), R(1)), (R(2, 100), R(2))]
    h, w, u = cf.check("hr", dist(U, F1, 0, sp.oo), dist(V, F2, 0, sp.oo))
    return w is None, w, u, 1


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.1080_02331888.2017.1353516.json")))
    results = []
    for recd in canon:
        order = recd["conclusion"]["order"]
        label = recd["claim"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        fn = {
            "Theorem 3.1": theorem_3_1,
            "Theorem 3.2(i)": lambda: theorem_3_2(1),
            "Theorem 3.2(ii)": lambda: theorem_3_2(2),
            "Theorem 3.3(i)": lambda: theorem_3_3(1),
            "Theorem 3.3(ii)": lambda: theorem_3_3(2),
            "Theorem 3.4": theorem_3_4,
            "Theorem 3.5(i)": lambda: theorem_3_5(1),
            "Theorem 3.5(ii)": lambda: theorem_3_5(2),
            "Theorem 4.1": theorem_4_1,
            "Theorem 4.2": lambda: theorem_4_2(1),
            "Theorem 4.2(ii)": lambda: theorem_4_2(2),
            "Theorem 4.3": theorem_4_3,
            "Theorem 4.4": lambda: theorem_4_4(1),
            "Theorem 4.4(ii)": lambda: theorem_4_4(2),
        }.get(label)
        if label == "Counterexample 3.1":
            ok, w, u, n_ = counterexample_3_1()
        elif label == "Counterexample 3.2":
            ok, w, u, n_ = counterexample_3_2()
        elif label == "Counterexample 4.1":
            ok, w, u, n_ = counterexample_4_1()
        elif fn is None:
            results.append(rec(recd, "out of harness scope"))
            continue
        else:
            n_, w, u = fn()
            results.append(rec(recd, "holds" if w is None else "refuted",
                               instances=n_, witness=w, undecided=u))
            continue
        results.append(rec(recd, "holds" if ok else "refuted",
                           instances=n_, witness=w, undecided=u))
    out = os.path.join(HERE, "eval_doi_10.1080_02331888.2017.1353516.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
