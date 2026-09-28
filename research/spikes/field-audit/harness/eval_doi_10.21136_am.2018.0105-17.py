"""Evaluation of canonical claims for doi:10.21136/am.2018.0105-17
(Balakrishnan-Haidari-Masoumifard style: order statistics from heterogeneous
new-Pareto NP(alpha, beta) components).

  NP(a, b):  F(x) = (x^a - b^a)/(x^a + b^a),  S(x) = 2 b^a/(x^a + b^a), x > b.
  Minimum (series): S_1:n = prod S_i on x > max b_i.
  Maximum (parallel): S_n:n = 1 - prod F_i on x > max b_i.
All comparisons on the common domain x > max(all b, all b*).

check(order, A, B) decides A <=_order B.
Counterexample records assert the *failure* of a printed ordering; a strict
witness of that failure confirms the printed claim -> status "holds".
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed
from mpmath import iv

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))

# closedform's grid leaves a coverage hole for hi=oo: points lo+1e-k are
# <= lo+0.1, then the span grid starts near lo + top/120 (top ~ 2^16-2^20
# for these slowly-decaying survivals).  Probe the hole explicitly.
PROBES = [R(1, 8), R(1, 4), R(1, 2), R(3, 4), R(1), R(3, 2), R(2), R(3), R(5),
          R(8), R(13), R(21), R(34), R(55), R(89), R(144), R(233), R(377),
          R(610), R(987), R(1597), R(2584), R(4184), R(6765), R(10946),
          R(17711), R(28657), R(46368), R(75025), R(121393), R(196418),
          R(317811), R(514229), R(832040)]


def rat(v):
    return v if isinstance(v, sp.Basic) else R(v)


def S_np(a, b):
    return 2 * rat(b) ** R(a) / (x ** R(a) + rat(b) ** R(a))


def F_np(a, b):
    return (x ** R(a) - rat(b) ** R(a)) / (x ** R(a) + rat(b) ** R(a))


def series_np(a, betas):
    return sp.prod([S_np(a, b) for b in betas])


def parallel_np(a, betas):
    return 1 - sp.prod([F_np(a, b) for b in betas])


def series_np_hetero(ab):       # heterogeneous shapes AND scales
    return sp.prod([S_np(a, b) for a, b in ab])


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


def check(order, SX_expr, SY_expr, lo):
    X, Y = Closed(SX_expr, lo=lo), Closed(SY_expr, lo=lo)
    holds, w, u = cf.check(order, X, Y)
    if w is not None:
        return holds, w, u
    E = cf.expression(order, X, Y)
    for p in PROBES:
        if p <= X.lo:
            continue
        for dps in (150, 400, 900):
            iv.dps = dps
            v = cf.iv_eval(E, p)
            if v.b < 0:
                return False, p, u
            if v.a >= 0:
                break
        else:
            u += 1
    return True, None, u


def sorted_desc(v):
    return sorted(v, reverse=True)


def majorized(a, b):
    """a majorizes b (a ~m b): equal totals, descending partial sums dominate."""
    A, B = sorted_desc(a), sorted_desc(b)
    return sum(a) == sum(b) and all(sum(A[:j]) >= sum(B[:j]) for j in range(1, len(A)))


def weak_lower(a, b):
    """a ~w b: ascending partial sums of a <= b's for j < n and sum a >= sum b."""
    A, B = sorted(a), sorted(b)
    return all(sum(A[:j]) <= sum(B[:j]) for j in range(1, len(A))) and sum(a) >= sum(b)


def componentwise(a, b):
    return all(u >= v for u, v in zip(a, b))


def anti_comonotone(row1, row2):
    return all((row1[i] - row1[j]) * (row2[i] - row2[j]) <= 0
               for i in range(len(row1)) for j in range(len(row1)))


def t_apply(row1, row2, pair, w):
    """One T-transform on the column pair (i,j): c_i' = w c_i + (1-w) c_j."""
    i, j = pair
    r1, r2 = list(row1), list(row2)
    for r in (r1, r2):
        ri, rj = r[i], r[j]
        r[i] = w * ri + (1 - w) * rj
        r[j] = w * rj + (1 - w) * ri
    return r1, r2


# ---------------------------------------------------------------- theorems
def thm_3_1a():
    """alpha >= 1, beta ~m beta* => Xn:n >=st Yn:n; test st(Y, X)."""
    pairs = [([R(1, 10), R(1), R(9)], [R(1, 10), R(4), R(6)]),
             ([R(1), R(2), R(7)], [R(3), R(3), R(4)]),
             ([R(1), R(1), R(8)], [R(2), R(4), R(4)]),
             ([R(1, 2), R(3, 2), R(7)], [R(2), R(5, 2), R(9, 2)])]
    n, wit, und = 0, None, 0
    for alpha in [R(1), R(3, 2), R(2)]:
        for b, bs in pairs:
            assert majorized(b, bs)
            lo = max(b + bs)
            h, w, u = check("st", parallel_np(alpha, bs), parallel_np(alpha, b), lo)
            n += 1; und += u
            if not h and wit is None: wit = w
    return n, wit, und


def thm_3_1b():
    """beta ~m beta*, alpha > 0 => X1:n <=st Y1:n; test st(X, Y)."""
    pairs = [([R(1, 10), R(1), R(9)], [R(1, 10), R(4), R(6)]),
             ([R(1), R(2), R(7)], [R(3), R(3), R(4)]),
             ([R(1), R(1), R(8)], [R(2), R(4), R(4)])]
    n, wit, und = 0, None, 0
    for alpha in [R(4, 5), R(1, 2), R(3, 2)]:
        for b, bs in pairs:
            assert majorized(b, bs)
            lo = max(b + bs)
            h, w, u = check("st", series_np(alpha, b), series_np(alpha, bs), lo)
            n += 1; und += u
            if not h and wit is None: wit = w
    return n, wit, und


def thm_3_2():
    """alpha <= 1, (1/beta) ~m (1/beta*) => X1:n >=st Y1:n; test st(Y, X)."""
    pairs = [([R(2), R(3), R(6)], [R(4), R(4), R(2)]),
             ([R(1), R(4), R(4, 3)], [R(2), R(2), R(1)])]
    n, wit, und = 0, None, 0
    for alpha in [R(1, 2), R(1)]:
        for b, bs in pairs:
            assert majorized([1 / v for v in b], [1 / v for v in bs])
            lo = max(b + bs)
            h, w, u = check("st", series_np(alpha, bs), series_np(alpha, b), lo)
            n += 1; und += u
            if not h and wit is None: wit = w
    return n, wit, und


def thm_3_3a():
    pairs = [([R(2), R(5), R(8)], [R(1), R(4), R(7)]),
             ([R(3), R(3), R(9, 2)], [R(5, 2), R(2), R(4)])]
    n, wit, und = 0, None, 0
    for alpha in [R(1, 2), R(3, 2)]:
        for b, bs in pairs:
            assert componentwise(b, bs)
            lo = max(b + bs)
            h, w, u = check("st", parallel_np(alpha, bs), parallel_np(alpha, b), lo)
            n += 1; und += u
            if not h and wit is None: wit = w
    return n, wit, und


def thm_3_3b():
    """1/b_i >= 1/b*_i (b_i <= b*_i) => Y1:n >=st X1:n; test st(X, Y)."""
    pairs = [([R(1), R(2), R(3)], [R(2), R(4), R(9, 2)]),
             ([R(1, 2), R(3), R(2)], [R(1), R(7, 2), R(3)])]
    n, wit, und = 0, None, 0
    for alpha in [R(1, 2), R(6, 5)]:
        for b, bs in pairs:
            assert all(1 / v >= 1 / w for v, w in zip(b, bs))
            lo = max(b + bs)
            h, w, u = check("st", series_np(alpha, b), series_np(alpha, bs), lo)
            n += 1; und += u
            if not h and wit is None: wit = w
    return n, wit, und


def thm_3_4():
    pairs = [([R(1), R(2), R(9)], [R(2), R(3), R(4)]),
             ([R(1), R(1), R(10)], [R(2), R(2), R(2)]),
             ([R(1, 2), R(1), R(4)], [R(1), R(2), R(5, 2)])]
    n, wit, und = 0, None, 0
    for alpha in [R(1), R(3, 2), R(2)]:
        for b, bs in pairs:
            assert weak_lower(b, bs)
            lo = max(b + bs)
            h, w, u = check("st", parallel_np(alpha, bs), parallel_np(alpha, b), lo)
            n += 1; und += u
            if not h and wit is None: wit = w
    return n, wit, und


def thm_3_5a():
    """0 < alpha <= 1, beta ~m beta* => X1:n >=fr(=hr) Y1:n; test hr(Y, X)."""
    pairs = [([R(1, 10), R(1), R(9)], [R(1, 10), R(4), R(6)]),
             ([R(1), R(2), R(7)], [R(3), R(3), R(4)])]
    n, wit, und = 0, None, 0
    for alpha in [R(1, 2), R(4, 5), R(1)]:
        for b, bs in pairs:
            assert majorized(b, bs)
            lo = max(b + bs)
            h, w, u = check("hr", series_np(alpha, bs), series_np(alpha, b), lo)
            n += 1; und += u
            if not h and wit is None: wit = w
    return n, wit, und


def thm_3_6(which):
    """alpha ~m alpha*; (a) Xn:n >=st Yn:n -> st(Y,X); (b) X1:n <=st Y1:n -> st(X,Y)."""
    pairs = [([R(1, 2), R(2), R(5, 2)], [R(3, 2), R(3, 2), R(2)]),
             ([R(1), R(1), R(4)], [R(2), R(2), R(2)]),
             ([R(1), R(2), R(5)], [R(2), R(3), R(3)])]
    n, wit, und = 0, None, 0
    for beta in [R(1), R(3, 2), R(5, 2)]:
        for a, astar in pairs:
            assert majorized(a, astar)
            lo = beta
            if which == "a":
                h, w, u = check("st",
                                1 - sp.prod([F_np(ai, beta) for ai in astar]),
                                1 - sp.prod([F_np(ai, beta) for ai in a]), lo)
            else:
                h, w, u = check("st",
                                sp.prod([S_np(ai, beta) for ai in a]),
                                sp.prod([S_np(ai, beta) for ai in astar]), lo)
            n += 1; und += u
            if not h and wit is None: wit = w
    return n, wit, und


def thm_3_7():
    """a_i >= a*_i componentwise => X1:n <=hr Y1:n; test hr(X, Y)."""
    pairs = [([R(2), R(3), R(5, 2)], [R(1), R(2), R(3, 2)]),
             ([R(3, 2), R(5)], [R(1, 2), R(4)]),
             ([R(1), R(2), R(4), R(3)], [R(1, 2), R(1), R(7, 2), R(2)])]
    n, wit, und = 0, None, 0
    for beta in [R(1), R(8, 5), R(5, 2)]:
        for a, astar in pairs:
            assert componentwise(a, astar)
            h, w, u = check("hr",
                            sp.prod([S_np(ai, beta) for ai in a]),
                            sp.prod([S_np(ai, beta) for ai in astar]), beta)
            n += 1; und += u
            if not h and wit is None: wit = w
    return n, wit, und


def thm_3_8():
    """alpha ~w alpha* (weak lower) => X1:n <=st Y1:n; test st(X, Y)."""
    pairs = [([R(1, 2), R(1), R(5)], [R(1), R(2), R(3)]),
             ([R(1, 4), R(1), R(4)], [R(1, 2), R(3, 2), R(2)]),
             ([R(1), R(1), R(6)], [R(1), R(3), R(3)])]
    n, wit, und = 0, None, 0
    for beta in [R(1), R(2)]:
        for a, astar in pairs:
            assert weak_lower(a, astar)
            h, w, u = check("st",
                            sp.prod([S_np(ai, beta) for ai in a]),
                            sp.prod([S_np(ai, beta) for ai in astar]), beta)
            n += 1; und += u
            if not h and wit is None: wit = w
    return n, wit, und


def matrix_claims(which):
    """Theorems 3.9/3.10/3.11, Cor 3.2: X1:n <=st Y1:n; test st(X, Y)."""
    insts = []
    if which == "3.9":       # n=2, A in S2, B = A Tw (single)
        A = ((R(3, 2), R(1, 2)), (R(1, 2), R(2)))
        assert anti_comonotone(*A)
        B = t_apply(*A, (0, 1), R(1, 4))
        insts.append((A, B))
        A = ((R(2), R(1, 2)), (R(1, 4), R(3, 2)))
        assert anti_comonotone(*A)
        B = t_apply(*A, (0, 1), R(2, 5))
        insts.append((A, B))
        # two-step chain on S2 matrix (chain majorization, not just one Tw)
        A = ((R(3), R(1)), (R(1, 2), R(5, 2)))
        assert anti_comonotone(*A)
        B1 = t_apply(*A, (0, 1), R(1, 3))
        B2 = t_apply(*B1, (0, 1), R(1, 2))
        insts.append((A, B2))
    elif which == "3.10":    # general n, A in Sn, single Tw
        A = ((R(3), R(3, 2), R(1, 2)), (R(1, 4), R(1), R(2)))
        assert anti_comonotone(*A)
        insts.append((A, t_apply(*A, (0, 2), R(1, 2))))
        insts.append((A, t_apply(*A, (1, 2), R(1, 3))))
        A2 = ((R(5, 2), R(1), R(1, 2), R(1, 4)), (R(1, 4), R(1, 2), R(1), R(3)))
        assert anti_comonotone(*A2)
        insts.append((A2, t_apply(*A2, (2, 3), R(1, 2))))
    elif which == "3.11":    # chain, every intermediate matrix in Sn
        A = ((R(3), R(2), R(1)), (R(1, 2), R(1), R(3)))
        assert anti_comonotone(*A)
        B1 = t_apply(*A, (1, 2), R(1, 2))
        assert anti_comonotone(*B1)
        B2 = t_apply(*B1, (0, 2), R(1, 4))
        assert anti_comonotone(*B2)
        insts.append((A, B2))
        A = ((R(4), R(2), R(1)), (R(1, 4), R(1), R(2)))
        assert anti_comonotone(*A)
        C1 = t_apply(*A, (0, 1), R(1, 2))
        assert anti_comonotone(*C1)
        C2 = t_apply(*C1, (1, 2), R(2, 3))
        assert anti_comonotone(*C2)
        insts.append((A, C2))
    elif which == "cor3.2":  # Sn + same-structure chain (same pair)
        A = ((R(3), R(3, 2), R(1, 2)), (R(1, 4), R(1), R(2)))
        assert anti_comonotone(*A)
        B1 = t_apply(*A, (0, 2), R(1, 3))
        B2 = t_apply(*B1, (0, 2), R(1, 4))   # same pair -> same structure
        insts.append((A, B2))
        A2 = ((R(2), R(1, 2)), (R(1, 3), R(3)))
        assert anti_comonotone(*A2)
        D1 = t_apply(*A2, (0, 1), R(1, 2))
        D2 = t_apply(*D1, (0, 1), R(1, 4))
        insts.append((A2, D2))
    n, wit, und = 0, None, 0
    for (a, b), (as_, bs_) in insts:
        lo = max(list(b) + list(bs_))
        h, w, u = check("st",
                        series_np_hetero(list(zip(a, b))),
                        series_np_hetero(list(zip(as_, bs_))), lo)
        n += 1; und += u
        if not h and wit is None: wit = w
    return n, wit, und


# ---------------------------------------------------------- counterexamples
def counter(kind, alpha, betas, betas_s, order, smaller):
    """Printed claim asserts the ordering `smaller <=order larger-side` FAILS.
    kind: 'ser' series (X1:n) or 'par' parallel (Xn:n). smaller is 'X' or 'Y':
    the side that would be order-smaller in the refuted relation."""
    lo = max(list(betas or []) + list(betas_s or []))
    if kind == "ser":
        Sx, Sy = series_np(alpha, betas), series_np(alpha, betas_s)
    else:
        Sx, Sy = parallel_np(alpha, betas), parallel_np(alpha, betas_s)
    A, B = (Sx, Sy) if smaller == "X" else (Sy, Sx)
    return check(order, A, B, lo)


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.21136_am.2018.0105-17.json")))
    results = []
    for recd in canon:
        label, order = recd["claim"], recd["conclusion"]["order"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        n_, w, u = 0, None, 0
        status = None
        if label == "Theorem 3.1(a)":
            n_, w, u = thm_3_1a()
        elif label == "Theorem 3.1(b)":
            n_, w, u = thm_3_1b()
        elif label == "Theorem 3.2":
            n_, w, u = thm_3_2()
        elif label == "Theorem 3.3(a)":
            n_, w, u = thm_3_3a()
        elif label == "Theorem 3.3(b)":
            n_, w, u = thm_3_3b()
        elif label == "Theorem 3.4":
            n_, w, u = thm_3_4()
        elif label == "Theorem 3.5(a)":
            n_, w, u = thm_3_5a()
        elif label == "Theorem 3.6(a)":
            n_, w, u = thm_3_6("a")
        elif label == "Theorem 3.6(b)":
            n_, w, u = thm_3_6("b")
        elif label == "Theorem 3.7":
            n_, w, u = thm_3_7()
        elif label == "Theorem 3.8":
            n_, w, u = thm_3_8()
        elif label == "Theorem 3.9":
            n_, w, u = matrix_claims("3.9")
        elif label == "Theorem 3.10":
            n_, w, u = matrix_claims("3.10")
        elif label == "Theorem 3.11":
            n_, w, u = matrix_claims("3.11")
        elif label == "Corollary 3.2":
            n_, w, u = matrix_claims("cor3.2")
        elif label == "Counterexample 3.1(i)":   # claims NOT(X >=st Y) -> test Y <=st X
            h, w, u = counter("par", R(3, 2), [R(1), R(8), R(11, 10)],
                              [R(8), R(11, 10), R(4)], "st", "Y")
            n_ = 1
        elif label == "Counterexample 3.1(ii)":  # claims NOT(X >=st Y)
            h, w, u = counter("par", R(4, 5), [R(1, 10), R(1), R(9)],
                              [R(1, 10), R(4), R(6)], "st", "Y")
            n_ = 1
        elif label == "Counterexample 3.2":      # claims NOT(X <=st Y)
            h, w, u = counter("ser", R(1, 2), [R(21, 10), R(1), R(9, 5)],
                              [R(7, 2), R(4, 5), R(9, 10)], "st", "X")
            n_ = 1
        elif label == "Counterexample 3.3":      # claims NOT(X >=st Y)
            h, w, u = counter("par", R(1, 2), [R(1, 5), R(1, 2), R(7, 10)],
                              [R(2, 5), R(3, 10), R(6, 5)], "st", "Y")
            n_ = 1
        elif label == "Counterexample 3.4":      # claims NOT(Y >=st X) -> test X <=st Y
            h, w, u = counter("ser", R(4, 5), [R(6, 5), R(1, 2), R(17, 10)],
                              [R(2, 5), R(4, 5), R(6, 5)], "st", "X")
            n_ = 1
        elif label == "Counterexample 3.5":      # claims NOT(X <=hr Y), common beta
            lo = R(8, 5)
            Sx = sp.prod([S_np(a, lo) for a in [R(3, 5), R(19, 10), R(3, 10), R(9, 5)]])
            Sy = sp.prod([S_np(a, lo) for a in [R(2, 5), R(21, 10), R(4, 5), R(8, 5)]])
            h, w, u = check("hr", Sx, Sy, lo)
            n_ = 1
        elif label == "Counterexample 3.6":      # claims NOT(X <=st Y), hetero 2x2
            lo = max(R(3, 5), R(2, 5), R(23, 50), R(27, 50))
            Sx = series_np_hetero([(R(3, 2), R(3, 5)), (R(4, 5), R(2, 5))])
            Sy = series_np_hetero([(R(101, 100), R(23, 50)), (R(129, 100), R(27, 50))])
            h, w, u = check("st", Sx, Sy, lo)
            n_ = 1
        else:
            results.append(rec(recd, "out of harness scope"))
            continue
        if status is None:
            if label.startswith("Counterexample"):
                # printed claim = "the ordering fails": a strict witness of that
                # failure confirms it; grid-survival leaves it unconfirmed.
                status = "holds" if w is not None else "ambiguous hypotheses"
            else:
                status = "holds" if w is None else "refuted"
        results.append(rec(recd, status, instances=n_, witness=w, undecided=u))
    out = os.path.join(HERE, "eval_doi_10.21136_am.2018.0105-17.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
