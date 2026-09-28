"""Evaluator for doi:10.52547/jsri.16.1.101 (Bashkar 2019, generalized modified
Weibull order statistics) -> harness/eval_doi_10.52547_jsri.16.1.101.result.json.

Model.  GMW(alpha, gamma, lam, beta):
    F(x) = (1 - exp(-alpha x^gamma e^{lam x}))^beta,  x >= 0,
S_i = 1 - F_i.  Series survival = prod S_i; parallel survival = 1 - prod F_i.
All testable claims have independent components; every claim whose hypotheses
involve an Archimedean copula generator (Theorems 11-17, Corollary 1) is
marked out of harness scope per the task instructions.

Majorization conventions follow the paper's Definition 2:
  x <=_w y  weak submajorization : upper partial sums of sorted x <= y's
  x <=^w y  weak supermajorization: lower partial sums of sorted x >= y's
  x <=^m y  majorization         : equal sums + lower partial sums x >= y's
  x >=^p y  p-larger (Def. 3)    : products of smallest components x <= y's
  x <=^p y  p-smaller            : products of smallest components x >= y's

Every concrete instance is asserted against all printed hypotheses
(majorization relation, monotonicity class E+/D+, parameter ranges) before
the order check runs.  Directions are taken from the canonical records, which
match the printed conclusions.
"""
import json
import os

import sympy as sp

import closedform as cf
import syscomp as sc

R, x = sp.Rational, cf.x

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.52547_jsri.16.1.101.json")
OUT = os.path.join(HERE, "eval_doi_10.52547_jsri.16.1.101.result.json")


# ----------------------------------------------------------------- model ----

def comp_F(a, g, l, b):
    """GMW component CDF."""
    u = R(a) * x ** R(g) * sp.exp(R(l) * x)
    return (1 - sp.exp(-u)) ** R(b)


def comp_S(a, g, l, b):
    return 1 - comp_F(a, g, l, b)


def system(comps, kind):
    """comps: list of (alpha, gamma, lam, beta)."""
    if kind == "series":
        return cf.Closed(sc.series([comp_S(*c) for c in comps]), 0, sp.oo)
    return cf.Closed(sc.parallel([comp_S(*c) for c in comps]), 0, sp.oo)


# ----------------------------------------------------- majorization, D2 -----

def w_sub(a, b):
    A, B = sorted(a), sorted(b)
    return all(sum(A[j:]) <= sum(B[j:]) for j in range(len(A)))


def w_sup(a, b):
    A, B = sorted(a), sorted(b)
    return all(sum(A[:j]) >= sum(B[:j]) for j in range(1, len(A) + 1))


def maj(a, b):
    return sum(a) == sum(b) and w_sup(a, b)


def p_larger(a, b):
    """a >=^p b : products of smallest components of a <= b's."""
    A, B = sorted(a), sorted(b)
    pa = pb = R(1)
    for j in range(len(A)):
        pa *= A[j]
        pb *= B[j]
        if pa > pb:
            return False
    return True


def p_smaller(a, b):
    return p_larger(b, a)


def in_Dplus(v):
    return all(v[i] >= v[i + 1] for i in range(len(v) - 1)) and v[-1] > 0


def in_Eplus(v):
    return all(v[i] <= v[i + 1] for i in range(len(v) - 1)) and v[0] > 0


# ---------------------------------------------------------------- helpers ---

def run(label, order, SX, SY, note):
    h, w, und = cf.check(order, SX, SY)
    return {"holds": h, "witness": None if h else str(w), "undecided": und,
            "notes": note}


def aggregate(label, order, results):
    ref = [r for r in results if not r["holds"]]
    out = {"claim": label, "order": order,
           "status": "refuted" if ref else "holds",
           "instances": len(results),
           "witness": ref[0]["witness"] if ref else None,
           "undecided_points": sum(r["undecided"] for r in results)}
    notes = [r["notes"] for r in results if r.get("notes")]
    if notes:
        out["notes"] = " | ".join(dict.fromkeys(notes))
    return out


def fixed(label, order, status, notes):
    return {"claim": label, "order": order, "status": status,
            "instances": 0, "witness": None, "undecided_points": 0,
            "notes": notes}


def v1(alpha, beta, g, l):
    """System spec helper: components share g, l, b; alpha per component."""
    return [(R(a), R(g), R(l), R(beta)) for a in alpha]


def vbeta(beta, a, g, l):
    return [(R(a), R(g), R(l), R(b)) for b in beta]


def vlam(lam, a, g, b):
    return [(R(a), R(g), R(l), R(b)) for l in lam]


def vab(alpha, beta, g, l):
    return [(R(a), R(g), R(l), R(b)) for a, b in zip(alpha, beta)]


# ----------------------------------------------------------- claim tests ----

def example1():
    # printed: a=(0.1,4,6) <=^w a*=(0.1,1,8), g=2, l=1.2, b=0.5; X3:3 <=rh X*
    a, as_ = [R(1, 10), R(4), R(6)], [R(1, 10), R(1), R(8)]
    assert w_sup(a, as_)
    X, Y = system(v1(a, "0.5", "2", "1.2"), "parallel"), \
        system(v1(as_, "0.5", "2", "1.2"), "parallel")
    return [run("X<=rhX*", "rh", X, Y, f"a={a},a*={as_},g=2,l=6/5,b=1/2")]


def example2i():
    # a=(5,2,0.2) <=_w a*=(8,3,0.3), b=1.3>=1, g=1.3, l=1.6; X1:3 >=st X*
    a, as_ = [R(5), R(2), R(1, 5)], [R(8), R(3), R(3, 10)]
    assert w_sub(a, as_)
    X, Y = system(v1(a, "1.3", "1.3", "1.6"), "series"), \
        system(v1(as_, "1.3", "1.3", "1.6"), "series")
    return [run("X*<=stX", "st", Y, X, f"a={a},a*={as_},g=13/10,l=8/5,b=13/10")]


def example2ii():
    # a=(0.2,4,9) <=^w a*=(0.1,1,6), b=0.3<=1, g=1.3, l=1.6; X1:3 <=st X*
    a, as_ = [R(1, 5), R(4), R(9)], [R(1, 10), R(1), R(6)]
    assert w_sup(a, as_)
    X, Y = system(v1(a, "0.3", "1.3", "1.6"), "series"), \
        system(v1(as_, "0.3", "1.3", "1.6"), "series")
    return [run("X<=stX*", "st", X, Y, f"a={a},a*={as_},g=13/10,l=8/5,b=3/10")]


def example3():
    # p-order counterexample, b=0.5,g=2,l=3.
    # case (A): a=(2,3) <=^p a*=(1,5.5) (i.e. a* >=^p a); printed X1:2 >=st X*.
    # case (B): a=(1.1,6) <=^p a*=(1,2.25); printed X1:2 <=st X*.
    res = []
    for a, as_, direction in [([R(2), R(3)], [R(1), R(11, 2)], "X*<=stX"),
                              ([R(11, 10), R(6)], [R(1), R(9, 4)], "X<=stX*")]:
        assert p_smaller(a, as_), (a, as_)
        X, Y = system(v1(a, "0.5", "2", "3"), "series"), \
            system(v1(as_, "0.5", "2", "3"), "series")
        first, second = (Y, X) if direction == "X*<=stX" else (X, Y)
        res.append(run(direction, "st", first, second,
                       f"case: a={a},a*={as_},b=1/2,g=2,l=3"))
    return res


def thm1():
    # a <=^w a* (supermaj) => Xn:n <=rh X*n:n
    res = []
    for (a, as_, g, l, b) in [
            ([R(1, 10), R(4), R(6)], [R(1, 10), R(1), R(8)], R(2), R(6, 5), R(1, 2)),
            ([R(1), R(3), R(5)], [R(1, 2), R(5, 2), R(6)], R(1), R(1, 4), R(2)),
            ([R(1, 2), R(2)], [R(1, 4), R(2)], R(3, 2), R(1, 2), R(3, 2)),
            ([R(2), R(5), R(9)], [R(1), R(2), R(10)], R(1), R(0), R(4))]:
        assert w_sup(a, as_), (a, as_)
        X, Y = system(v1(a, b, g, l), "parallel"), system(v1(as_, b, g, l), "parallel")
        res.append(run("X<=rhX*", "rh", X, Y, f"a={a},a*={as_},g={g},l={l},b={b}"))
    return res


def thm2():
    # a_i <= a*_i componentwise => Xn:n >=rh X*n:n
    res = []
    for (a, as_, g, l, b) in [
            ([R(1), R(2), R(3)], [R(2), R(4), R(5)], R(2), R(6, 5), R(1, 2)),
            ([R(1, 2), R(1)], [R(1), R(3, 2)], R(1), R(1, 4), R(3)),
            ([R(2), R(3), R(4)], [R(5, 2), R(7, 2), R(9, 2)], R(3, 2), R(0), R(1))]:
        assert all(ai <= asi for ai, asi in zip(a, as_))
        X, Y = system(v1(a, b, g, l), "parallel"), system(v1(as_, b, g, l), "parallel")
        res.append(run("X*<=rhX", "rh", Y, X, f"a={a},a*={as_},g={g},l={l},b={b}"))
    return res


def thm3():
    # a <=^w a* supermaj, b in E+, a,a* in D+ => Xn:n <=rh X*n:n
    res = []
    for (a, as_, beta, g, l) in [
            ([R(6), R(4), R(1)], [R(8), R(2), R(1)], [R(1, 2), R(1), R(3, 2)], R(2), R(6, 5)),
            ([R(5), R(3), R(1)], [R(6), R(2), R(1)], [R(1), R(2), R(3)], R(1), R(1, 4)),
            ([R(9), R(5), R(2)], [R(10), R(2), R(1)], [R(1), R(1), R(2)], R(3, 2), R(0))]:
        assert in_Dplus(a) and in_Dplus(as_) and in_Eplus(beta)
        assert w_sup(a, as_), (a, as_)
        X, Y = system(vab(a, beta, g, l), "parallel"), system(vab(as_, beta, g, l), "parallel")
        res.append(run("X<=rhX*", "rh", X, Y,
                       f"a={a},a*={as_},b={beta},g={g},l={l}"))
    return res


def thm4():
    # a_i >= a*_i and b_i <= b*_i => Xn:n <=rh X*n:n
    res = []
    for (a, as_, beta, bs, g, l) in [
            ([R(3), R(2), R(5)], [R(2), R(1), R(4)], [R(1), R(1), R(2)],
             [R(2), R(3), R(4)], R(2), R(1, 2)),
            ([R(4), R(3)], [R(2), R(1)], [R(1, 2), R(1)], [R(1), R(2)], R(1), R(0)),
            ([R(6), R(4), R(2)], [R(5), R(3), R(1)], [R(3), R(2), R(1)],
             [R(4), R(5), R(2)], R(3, 2), R(1, 4))]:
        assert all(ai >= asi for ai, asi in zip(a, as_))
        assert all(bi <= bsi for bi, bsi in zip(beta, bs))
        X, Y = system(vab(a, beta, g, l), "parallel"), system(vab(as_, bs, g, l), "parallel")
        res.append(run("X<=rhX*", "rh", X, Y,
                       f"a={a},a*={as_},b={beta},b*={bs},g={g},l={l}"))
    return res


def thm5i():
    # b <=^m b*, b,b* in D+, a in E+ => Xn:n <=rh X*n:n
    res = []
    for (beta, bs, alpha, g, l) in [
            ([R(3), R(3), R(2)], [R(4), R(3), R(1)], [R(1, 2), R(1), R(3, 2)], R(2), R(6, 5)),
            ([R(4), R(2), R(1)], [R(5), R(1), R(1)], [R(1, 4), R(1, 2), R(1)], R(1), R(1, 4)),
            ([R(3), R(2), R(1)], [R(4), R(1), R(1)], [R(1), R(2), R(3)], R(3, 2), R(0))]:
        assert maj(beta, bs) and in_Dplus(beta) and in_Dplus(bs) and in_Eplus(alpha)
        X, Y = system(vab(alpha, beta, g, l), "parallel"), system(vab(alpha, bs, g, l), "parallel")
        res.append(run("X<=rhX*", "rh", X, Y,
                       f"a={alpha},b={beta},b*={bs},g={g},l={l}"))
    return res


def thm5ii():
    # b <=^m b*, b,b*,a all in D+ => Xn:n >=rh X*n:n
    res = []
    for (beta, bs, alpha, g, l) in [
            ([R(3), R(3), R(2)], [R(4), R(3), R(1)], [R(3), R(2), R(1)], R(2), R(6, 5)),
            ([R(4), R(2), R(1)], [R(5), R(1), R(1)], [R(4), R(2), R(1)], R(1), R(1, 4)),
            ([R(5), R(3), R(1)], [R(6), R(2), R(1)], [R(6), R(3), R(1)], R(3, 2), R(0))]:
        assert maj(beta, bs) and in_Dplus(beta) and in_Dplus(bs) and in_Dplus(alpha)
        X, Y = system(vab(alpha, beta, g, l), "parallel"), system(vab(alpha, bs, g, l), "parallel")
        res.append(run("X*<=rhX", "rh", Y, X,
                       f"a={alpha},b={beta},b*={bs},g={g},l={l}"))
    return res


def thm6i():
    # b <=_w b* (submaj), b,b* in D+, a in E+ => Xn:n <=rh X*n:n
    res = []
    for (beta, bs, alpha, g, l) in [
            ([R(3), R(2), R(2)], [R(4), R(3), R(1)], [R(1, 2), R(1), R(3, 2)], R(2), R(6, 5)),
            ([R(3), R(2), R(1)], [R(4), R(3), R(1)], [R(1, 4), R(1, 2), R(1)], R(1), R(1, 4)),
            ([R(4), R(3), R(1)], [R(5), R(4), R(1)], [R(1), R(2), R(2)], R(3, 2), R(0))]:
        assert w_sub(beta, bs) and in_Dplus(beta) and in_Dplus(bs) and in_Eplus(alpha), (beta, bs, alpha)
        X, Y = system(vab(alpha, beta, g, l), "parallel"), system(vab(alpha, bs, g, l), "parallel")
        res.append(run("X<=rhX*", "rh", X, Y,
                       f"a={alpha},b={beta},b*={bs},g={g},l={l}"))
    return res


def thm6ii():
    # b <=^w b* (supermaj), b,b*,a in D+ => Xn:n >=rh X*n:n
    res = []
    for (beta, bs, alpha, g, l) in [
            ([R(4), R(3), R(1)], [R(4), R(2), R(1)], [R(3), R(2), R(1)], R(2), R(6, 5)),
            ([R(5), R(3), R(1)], [R(5), R(2), R(1)], [R(4), R(2), R(1)], R(1), R(1, 4)),
            ([R(6), R(4), R(1)], [R(6), R(3), R(1)], [R(5), R(4), R(2)], R(3, 2), R(0))]:
        assert w_sup(beta, bs) and in_Dplus(beta) and in_Dplus(bs) and in_Dplus(alpha), (beta, bs, alpha)
        X, Y = system(vab(alpha, beta, g, l), "parallel"), system(vab(alpha, bs, g, l), "parallel")
        res.append(run("X*<=rhX", "rh", Y, X,
                       f"a={alpha},b={beta},b*={bs},g={g},l={l}"))
    return res


def thm7i():
    # a <=_w a* (submaj), b >= 1 => X1:n >=st X*1:n
    res = []
    for (a, as_, b, g, l) in [
            ([R(5), R(2), R(1, 5)], [R(8), R(3), R(3, 10)], R(13, 10), R(13, 10), R(8, 5)),
            ([R(2), R(3), R(4)], [R(3), R(4), R(6)], R(2), R(1), R(1, 4)),
            ([R(1), R(2)], [R(2), R(3)], R(1), R(3, 2), R(0)),
            ([R(4), R(2), R(1)], [R(5), R(3), R(3)], R(3), R(1), R(1, 2))]:
        assert w_sub(a, as_) and b >= 1, (a, as_, b)
        X, Y = system(v1(a, b, g, l), "series"), system(v1(as_, b, g, l), "series")
        res.append(run("X*<=stX", "st", Y, X, f"a={a},a*={as_},b={b},g={g},l={l}"))
    return res


def thm7ii():
    # a <=^w a* (supermaj), 0 < b <= 1 => X1:n <=st X*1:n
    res = []
    for (a, as_, b, g, l) in [
            ([R(1, 5), R(4), R(9)], [R(1, 10), R(1), R(6)], R(3, 10), R(13, 10), R(8, 5)),
            ([R(1), R(4), R(6)], [R(1, 2), R(3, 2), R(8)], R(1, 2), R(1), R(1, 4)),
            ([R(2), R(5)], [R(1), R(4)], R(1), R(3, 2), R(0)),
            ([R(1), R(2), R(8)], [R(1, 2), R(1), R(6)], R(3, 4), R(1), R(1, 2))]:
        assert w_sup(a, as_) and b <= 1, (a, as_, b)
        X, Y = system(v1(a, b, g, l), "series"), system(v1(as_, b, g, l), "series")
        res.append(run("X<=stX*", "st", X, Y, f"a={a},a*={as_},b={b},g={g},l={l}"))
    return res


def thm8():
    # b >=^w b* i.e. b* <=^w b (lower partial sums b* >= b) => X1:n <=hr X*1:n
    res = []
    for (beta, bs, a, g, l) in [
            ([R(1), R(2), R(4)], [R(2), R(3), R(5)], R(1, 2), R(2), R(0)),
            ([R(1, 2), R(1), R(2)], [R(1), R(3, 2), R(5, 2)], R(1), R(3, 2), R(1, 4)),
            ([R(1), R(1), R(2)], [R(2), R(2), R(3)], R(3, 4), R(1), R(1, 2))]:
        assert w_sup(bs, beta), (beta, bs)
        X, Y = system(vbeta(beta, a, g, l), "series"), system(vbeta(bs, a, g, l), "series")
        res.append(run("X<=hrX*", "hr", X, Y,
                       f"a={a},b={beta},b*={bs},g={g},l={l}"))
    return res


def thm9():
    # lam <=^w lam* (supermaj) => Xn:n <=st X*n:n
    res = []
    for (lam, ls, a, g, b) in [
            ([R(2), R(3), R(5)], [R(1), R(2), R(6)], R(1), R(2), R(2)),
            ([R(1), R(2), R(4)], [R(1, 2), R(1), R(5)], R(1, 2), R(1), R(1, 2)),
            ([R(3), R(4)], [R(2), R(5)], R(3, 4), R(3, 2), R(1))]:
        assert w_sup(lam, ls), (lam, ls)
        X, Y = system(vlam(lam, a, g, b), "parallel"), system(vlam(ls, a, g, b), "parallel")
        res.append(run("X<=stX*", "st", X, Y,
                       f"a={a},l={lam},l*={ls},g={g},b={b}"))
    return res


def thm10():
    # lam <=_w lam* (submaj), b >= 1 => X1:n >=st X*1:n
    res = []
    for (lam, ls, a, g, b) in [
            ([R(1), R(2), R(3)], [R(2), R(3), R(4)], R(1), R(1), R(2)),
            ([R(1, 2), R(1), R(2)], [R(1), R(3, 2), R(3)], R(1, 2), R(3, 2), R(1)),
            ([R(2), R(3)], [R(4), R(5)], R(2), R(2), R(3))]:
        assert w_sub(lam, ls) and b >= 1, (lam, ls, b)
        X, Y = system(vlam(lam, a, g, b), "series"), system(vlam(ls, a, g, b), "series")
        res.append(run("X*<=stX", "st", Y, X,
                       f"a={a},l={lam},l*={ls},g={g},b={b}"))
    return res


TESTS = {
    "Example 1": ("rh", example1),
    "Example 2(i)": ("st", example2i),
    "Example 2(ii)": ("st", example2ii),
    "Example 3": ("st", example3),
    "Theorem 1": ("rh", thm1),
    "Theorem 2": ("rh", thm2),
    "Theorem 3": ("rh", thm3),
    "Theorem 4": ("rh", thm4),
    "Theorem 5(i)": ("rh", thm5i),
    "Theorem 5(ii)": ("rh", thm5ii),
    "Theorem 6(i)": ("rh", thm6i),
    "Theorem 6(ii)": ("rh", thm6ii),
    "Theorem 7(i)": ("st", thm7i),
    "Theorem 7(ii)": ("st", thm7ii),
    "Theorem 8": ("hr", thm8),
    "Theorem 9": ("st", thm9),
    "Theorem 10": ("st", thm10),
}

COPULA = {"Theorem 11", "Theorem 12", "Theorem 13", "Theorem 14",
          "Theorem 15(i)", "Theorem 15(ii)", "Theorem 16(i)", "Theorem 16(ii)",
          "Theorem 17", "Corollary 1"}


def main():
    data = json.load(open(CANON))
    out = []
    for rec in data:
        label, order = rec["claim"], rec["conclusion"]["order"]
        if order not in ("st", "hr", "rh", "lr"):
            out.append(fixed(label, order, "unsupported order",
                             "harness supports st/hr/rh/lr only"))
            continue
        if label in COPULA:
            out.append(fixed(label, order, "out of harness scope",
                             "Archimedean-copula model; outside the "
                             "independent-system harness"))
            continue
        o, fn = TESTS[label]
        assert o == order, (label, o, order)
        print(f"[eval] {label}", flush=True)
        out.append(aggregate(label, order, fn()))
    json.dump(out, open(OUT, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
