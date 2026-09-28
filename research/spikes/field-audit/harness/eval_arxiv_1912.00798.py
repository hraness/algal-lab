"""Evaluation of canonical claims for arxiv:1912.00798 (Masoumifard et al.,
hazard/stochastic comparisons of parallel systems in the exponentiated scale
model F(lam x)^alpha and the two-value scale model F(lam x)).

Families (all elementary):
  PGW(p,q,lam):  S(x) = exp(1 - (1 + (lam x)^p)^(1/q))          x > 0
     (baseline density f = w h, w(x) = x^{p-1},
      h(x) = (p/q)(1+x^p)^{1/q-1} e^{1-(1+x^p)^{1/q}};
      satisfies Lemma-2.1 conditions (a)-(c) for q <= 1 by Lemma 3.1)
  EGG(g,a,a,lam) = exponentiated Weibull (alpha = beta sub-model):
      S(x) = 1 - (1 - exp(-(lam x)^a))^g
     (admissible for Theorem 3.2 / Remark 3.1(ii) since they require a >= b;
      satisfies Lemma-2.1 conditions for a >= b = a by Lemma 3.2)

Direction convention: cf.check(order, A, B) decides A <=_order B.
  "X >=st Y"  -> check("st", Y, X);   "X >=hr Y" -> check("hr", Y, X)
  "Y >=st X"  -> check("st", X, Y);   "Y >=hr X" -> check("hr", X, Y)
For equivalence claims (i)<=>(ii)<=>(iii) the sufficiency direction
(hypothesis (i) holds => order holds) is what can be refuted by a single
point; instances with (i) violated are also run to probe necessity.
Counterexample records assert a *failure* of an order: a strict-enclosure
witness of that failure confirms the printed claim -> status "holds".
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def rat(v):
    """Exactify: pass sympy expressions (e.g. algebraic Pow) through, else Rational."""
    return v if isinstance(v, sp.Basic) else R(v)


def S_pgw(lam, p, q):
    return sp.exp(1 - (1 + (rat(lam) * x) ** R(p)) ** (1 / R(q)))


def S_ew(lam, a, g):
    return 1 - (1 - sp.exp(-(rat(lam) * x) ** R(a))) ** R(g)


def S_exp_scale(lam, alpha, base):
    """Xi ~ F(lam x)^alpha for baseline survival expression base(x)."""
    return 1 - (1 - base.subs(x, R(lam) * x)) ** R(alpha)


def parallel_sf(comp_survivals):
    return 1 - sp.prod([1 - S for S in comp_survivals])


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


def both(order, A, B):
    """check(order,A,B): (holds, witness, undecided); extra precision tier."""
    return cf.check(order, A, B, precisions=(60, 150, 400, 900))


def geom(lams):
    return sp.prod([rat(l) for l in lams]) ** (1 / R(len(lams)))


def wgeom(lams, alphas):
    return sp.prod([rat(l) ** R(a) for l, a in zip(lams, alphas)]) ** (1 / sum(R(a) for a in alphas))


# ---------------------------------------------------------------- Example 3.1
def ex_3_1():
    lams = [R(3, 2), R(2), R(7, 2)]
    lam_gm = geom(lams)          # 10.5^(1/3) ~ 2.189
    lam_am = R(7, 3)             # 2.333
    n, wit, und = 0, None, 0
    for (p, q) in [(R(3, 2), R(4, 5)), (R(4, 5), R(2, 5))]:
        for lam in [lam_gm, lam_am]:           # both satisfy lam >= lam~
            Xn = Closed(parallel_sf([S_pgw(l, p, q) for l in lams]))
            Yn = Closed(parallel_sf([S_pgw(lam, p, q)] * 3))
            h, w, u = both("hr", Yn, Xn)       # decide Y <=hr X i.e. X >=hr Y
            n += 1
            und += u
            if not h and wit is None:
                wit = w
    return n, wit, und


# ---------------------------------------------------------------- Example 4.1
def ex_4_1():
    """Printed claim: X3:3 and Y3:3 not hr-comparable (both directions fail)."""
    lams = [R(1, 10), R(1), R(9)]
    mus = [R(1, 10), R(4), R(6)]
    Xn = Closed(parallel_sf([S_pgw(l, 2, 1) for l in lams]))
    Yn = Closed(parallel_sf([S_pgw(m, 2, 1) for m in mus]))
    h1, w1, u1 = both("hr", Xn, Yn)   # X <=hr Y should FAIL
    h2, w2, u2 = both("hr", Yn, Xn)   # Y <=hr X should FAIL
    return (w1 is not None) and (w2 is not None), (w1, w2), u1 + u2, 2


# ------------------------------------------------- Lemmas 2.1, 2.3, 4.2, 4.3
def lemma_2_1(order):
    """F(lam_i x)^ai parallel vs common-scale F(lam x)^ai, ai >= 1.
    Baseline = PGW(p, q<=1) and exponentiated-Weibull: both satisfy (a)-(c)."""
    n, wit, und = 0, None, 0
    cases = []
    for base_name, baseF in [("pgw", (R(3, 2), R(4, 5))), ("ew", (R(3, 2),))]:
        for lams, alphas in [([R(3, 2), R(2), R(7, 2)], [R(1), R(3, 2), R(2)]),
                             ([R(1, 2), R(3), R(2)], [R(1), R(1), R(1)])]:
            lw = wgeom(lams, alphas)
            for lam, lam_ok in [(lw, True), (R(6, 5) * lw, True), (R(4, 5) * lw, False)]:
                cases.append((base_name, baseF, lams, alphas, lam, lam_ok))
    for base_name, baseF, lams, alphas, lam, lam_ok in cases:
        if base_name == "pgw":
            p, q = baseF
            compX = [1 - (1 - S_pgw(l, p, q)) ** R(a) for l, a in zip(lams, alphas)]
            compY = [1 - (1 - S_pgw(lam, p, q)) ** R(a) for a in alphas]
        else:
            (a,) = baseF
            compX = [S_ew(l, a, al) for l, al in zip(lams, alphas)]
            compY = [S_ew(lam, a, al) for al in alphas]
        Xn = Closed(parallel_sf(compX))
        Yn = Closed(parallel_sf(compY))
        h, w, u = both(order, Yn, Xn)        # decide X >=order Y
        n += 1
        und += u
        if not h and lam_ok and wit is None:
            wit = w                           # violates sufficiency
        # lam < lamwg with the order failing is consistent with necessity
    return n, wit, und


def lemma_2_3(order):
    """Two-value model: p comps at lam, n-p at lam* vs p at mu, n-p at mu*,
    lam <= mu <= mu* <= lam*, (i) p-larger product condition. PGW baseline."""
    n, wit, und = 0, None, 0
    # (lam, lam*, p, n, mu, mu*) tuples satisfying all hypotheses
    insts = [
        (R(1), R(4), 1, 3, R(2), R(3)),      # products: (1,1,4) vs (2,2,3)
        (R(1), R(9, 2), 2, 4, R(3, 2), R(4)),  # (1,1,9/2,9/2) vs (3/2,3/2,4,4)
        (R(1, 2), R(5), 1, 3, R(1), R(3)),   # check (i) below
        (R(1), R(4), 1, 3, R(5, 2), R(16, 5)),  # (i) fails -> probe necessity
    ]
    for (p, q) in [(R(3, 2), R(4, 5)), (R(1), R(1, 2))]:
        for lam, ls, p_, n_, mu, ms in insts:
            assert lam <= mu <= ms <= ls
            v = sorted([lam] * p_ + [ls] * (n_ - p_))
            w_ = sorted([mu] * p_ + [ms] * (n_ - p_))
            cond_i = all(sp.prod(v[:j]) <= sp.prod(w_[:j]) for j in range(1, n_ + 1))
            Xn = Closed(parallel_sf([S_pgw(t, p, q) for t in [lam] * p_ + [ls] * (n_ - p_)]))
            Yn = Closed(parallel_sf([S_pgw(t, p, q) for t in [mu] * p_ + [ms] * (n_ - p_)]))
            h, w, u = both(order, Yn, Xn)
            n += 1
            und += u
            if not h and cond_i and wit is None:
                wit = w
    return n, wit, und


def lemma_4_2():
    """hazard of Xn:n increasing in lam in (0, lam*]: for lam_a <= lam_b <= lam*,
    Xn:n(lam_a) >=hr Xn:n(lam_b). PGW baseline q <= 1."""
    n, wit, und = 0, None, 0
    for (p, q) in [(R(3, 2), R(4, 5)), (R(1), R(1, 2))]:
        for (lam_a, lam_b, ls, p_, n_) in [(R(1, 2), R(1), R(2), 1, 3),
                                         (R(1), R(3, 2), R(2), 2, 4),
                                         (R(1, 4), R(7, 4), R(2), 1, 3)]:
            assert lam_a <= lam_b <= ls
            Xa = Closed(parallel_sf([S_pgw(t, p, q) for t in [lam_a] * p_ + [ls] * (n_ - p_)]))
            Xb = Closed(parallel_sf([S_pgw(t, p, q) for t in [lam_b] * p_ + [ls] * (n_ - p_)]))
            h, w, u = both("hr", Xb, Xa)     # decide Xa >=hr Xb i.e. Xb <=hr Xa
            n += 1
            und += u
            if not h and wit is None:
                wit = w
    return n, wit, und


def lemma_4_3():
    """hazard of Xn:n increasing in lam for homogeneous F(lam x)^alpha, a>=1."""
    n, wit, und = 0, None, 0
    for (p, q) in [(R(3, 2), R(4, 5)), (R(1), R(1, 2))]:
        for alpha in [R(1), R(3, 2), R(2)]:
            for (lam, mu) in [(R(1), R(2)), (R(1, 2), R(3))]:
                assert lam <= mu
                Xn = Closed(parallel_sf([1 - (1 - S_pgw(lam, p, q)) ** alpha] * 3))
                Yn = Closed(parallel_sf([1 - (1 - S_pgw(mu, p, q)) ** alpha] * 3))
                h, w, u = both("hr", Yn, Xn)  # decide X >=hr Y (h_X <= h_Y)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
    return n, wit, und


# ------------------------------------------------------- Remarks, Theorems
def remark_3_1_i():
    """PGW: r_{Xn:n}(x) <= r_{Yn:n}(x; geom-mean) — i.e. X >=hr Y at lam = lam~."""
    n, wit, und = 0, None, 0
    for (p, q) in [(R(3, 2), R(4, 5)), (R(4, 5), R(2, 5)), (R(2), R(1))]:
        for lams in [[R(3, 2), R(2), R(7, 2)], [R(1, 2), R(3), R(2)]]:
            for lam in [geom(lams), R(6, 5) * geom(lams)]:
                Xn = Closed(parallel_sf([S_pgw(l, p, q) for l in lams]))
                Yn = Closed(parallel_sf([S_pgw(lam, p, q)] * len(lams)))
                h, w, u = both("hr", Yn, Xn)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
    return n, wit, und


def remark_3_1_ii():
    """EGG version: alpha=beta exponentiated-Weibull sub-model, gi >= 1."""
    n, wit, und = 0, None, 0
    for a in [R(1), R(3, 2), R(2)]:
        for lams, gs in [([R(3, 2), R(2), R(7, 2)], [R(1), R(3, 2), R(2)]),
                         ([R(1, 2), R(3), R(2)], [R(1), R(1), R(1)])]:
            lw = wgeom(lams, gs)
            for lam in [lw, R(6, 5) * lw]:
                Xn = Closed(parallel_sf([S_ew(l, a, g) for l, g in zip(lams, gs)]))
                Yn = Closed(parallel_sf([S_ew(lam, a, g) for g in gs]))
                h, w, u = both("hr", Yn, Xn)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
    return n, wit, und


def theorem_3_1(order):
    n, wit, und = 0, None, 0
    for (p, q) in [(R(3, 2), R(4, 5)), (R(4, 5), R(2, 5)), (R(2), R(1)), (R(3), R(1, 2))]:
        for lams in [[R(3, 2), R(2), R(7, 2)], [R(1, 2), R(3), R(2)],
                     [R(1, 4), R(5, 4)]]:
            lg = geom(lams)
            for lam in [lg, R(11, 10) * lg]:
                Xn = Closed(parallel_sf([S_pgw(l, p, q) for l in lams]))
                Yn = Closed(parallel_sf([S_pgw(lam, p, q)] * len(lams)))
                h, w, u = both(order, Yn, Xn)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
    return n, wit, und


def theorem_3_2(order):
    n, wit, und = 0, None, 0
    for a in [R(1), R(3, 2), R(2)]:          # alpha = beta; condition a >= b met
        for lams, gs in [([R(3, 2), R(2), R(7, 2)], [R(1), R(3, 2), R(2)]),
                         ([R(1, 2), R(3), R(2)], [R(1), R(1), R(1)]),
                         ([R(1, 4), R(5, 4)], [R(2), R(3)])]:
            lw = wgeom(lams, gs)
            for lam in [lw, R(6, 5) * lw]:
                Xn = Closed(parallel_sf([S_ew(l, a, g) for l, g in zip(lams, gs)]))
                Yn = Closed(parallel_sf([S_ew(lam, a, g) for g in gs]))
                h, w, u = both(order, Yn, Xn)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
    return n, wit, und


def theorem_4_1(order):
    """Multiple-outlier PGW: n1 at lam1, n2 at lam2 vs n1 at lam*1, n2 at lam*2;
    lam1 <= lam*1 <= lam*2 <= lam2 and p-larger product condition."""
    n, wit, und = 0, None, 0
    insts = [
        (R(1), R(4), R(2), R(3), 2, 1),      # X:(1,1,4) Y:(2,2,3)
        (R(1, 2), R(5), R(3, 2), R(3), 1, 2),  # X:(1/2,5,5) Y:(3/2,3,3)
        (R(1), R(4), R(3, 2), R(7, 2), 2, 1),  # probe: cond (i)? checked below
    ]
    for (p, q) in [(R(3, 2), R(4, 5)), (R(2), R(1)), (R(1), R(1, 2))]:
        for l1, l2, m1, m2, n1, n2 in insts:
            assert l1 <= m1 <= m2 <= l2
            v = sorted([l1] * n1 + [l2] * n2)
            w_ = sorted([m1] * n1 + [m2] * n2)
            cond_i = all(sp.prod(v[:j]) <= sp.prod(w_[:j]) for j in range(1, n1 + n2 + 1))
            Xn = Closed(parallel_sf([S_pgw(t, p, q) for t in [l1] * n1 + [l2] * n2]))
            Yn = Closed(parallel_sf([S_pgw(t, p, q) for t in [m1] * n1 + [m2] * n2]))
            h, w, u = both(order, Yn, Xn)
            n += 1
            und += u
            if not h and cond_i and wit is None:
                wit = w
    return n, wit, und


def lemma_2_2():
    """lam <= mu <= mu* <= lam*, lam^p lam*^(n-p) = mu^p mu*^(n-p) => X >=hr Y."""
    n, wit, und = 0, None, 0
    insts = [
        (R(1), R(4), 1, 2, R(3, 2), R(8, 3)),   # 1*4 = 4 = (3/2)(8/3)
        (R(1), R(8), 1, 2, R(2), R(4)),          # 1*8 = 8 = 2*4
        (R(1, 2), R(4), 2, 4, R(1), R(2)),       # (1/2)^2 4^2 = 4 = 1*2^2? 1*4=4 yes
    ]
    for (p, q) in [(R(3, 2), R(4, 5)), (R(1), R(1, 2))]:
        for lam, ls, p_, n_, mu, ms in insts:
            assert lam <= mu <= ms <= ls
            assert lam ** p_ * ls ** (n_ - p_) == mu ** p_ * ms ** (n_ - p_)
            Xn = Closed(parallel_sf([S_pgw(t, p, q) for t in [lam] * p_ + [ls] * (n_ - p_)]))
            Yn = Closed(parallel_sf([S_pgw(t, p, q) for t in [mu] * p_ + [ms] * (n_ - p_)]))
            h, w, u = both("hr", Yn, Xn)
            n += 1
            und += u
            if not h and wit is None:
                wit = w
    return n, wit, und


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "arxiv_1912.00798.json")))
    results = []
    for recd in canon:
        label, order = recd["claim"], recd["conclusion"]["order"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        if label == "Example 3.1":
            n_, w, u = ex_3_1()
        elif label == "Example 4.1":
            ok, (w1, w2), u, n_ = ex_4_1()
            results.append(rec(recd, "holds" if ok else "refuted",
                               instances=n_, witness=w2 if w2 is not None else w1,
                               undecided=u))
            continue
        elif label == "Lemma 2.1":
            n_, w, u = lemma_2_1(order)
        elif label == "Lemma 2.3":
            n_, w, u = lemma_2_3(order)
        elif label == "Lemma 4.2":
            n_, w, u = lemma_4_2()
        elif label == "Lemma 4.3":
            n_, w, u = lemma_4_3()
        elif label == "Remark 3.1(i)":
            n_, w, u = remark_3_1_i()
        elif label == "Remark 3.1(ii)":
            n_, w, u = remark_3_1_ii()
        elif label == "Theorem 3.1":
            n_, w, u = theorem_3_1(order)
        elif label == "Theorem 3.2":
            n_, w, u = theorem_3_2(order)
        elif label == "Theorem 4.1":
            n_, w, u = theorem_4_1(order)
        elif label == "Lemma 2.2":
            n_, w, u = lemma_2_2()
        else:
            results.append(rec(recd, "out of harness scope"))
            continue
        results.append(rec(recd, "holds" if w is None else "refuted",
                           instances=n_, witness=w, undecided=u))
    out = os.path.join(HERE, "eval_arxiv_1912.00798.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
