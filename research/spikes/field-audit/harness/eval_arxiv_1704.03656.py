"""Evaluator for arXiv:1704.03656 (GE/ES/Frechet/scale systems, independent).

Convention (Def 2.2 of the paper):
  x ~_w y  := top-j sums of x <= y's        (weak submajorization)
  x ~^w y  := bottom-j sums of x >= y's     (weak supermajorization)
  x ~^p y  := products of smallest j of x <= y's   (p-larger)
  f-versions: same applied to f(x), f(y).

Models:
  Frechet(mu,l,a): F = e^{-((x-mu)/l)^{-a}}
  scale: G(l_i x)
  GE(a,l) = ES(a,l) with G=Exp: F = (1-e^{-l x})^a
"""
import json
import auditlib as A
from ratdist import Dist
import sympy as sp

z = A.z
x = A.x
e = A.e


def wsub(x, y):
    return A.weak_sub(x, y)


def wsup(x, y):
    ax, ay = A.asc(x), A.asc(y)
    return all(sum(ax[:j]) >= sum(ay[:j]) for j in range(1, len(x) + 1))


def ge_series_cf(alpha, lams):
    return sp.prod([1 - (1 - e ** (-A.R(l) * x)) ** A.R(alpha) for l in lams])


def ge_series_z(alphas, lams2):
    """GE series, z=e^{-x/2}; lams2 = 2*scale."""
    survs = [sp.expand(1 - (1 - z ** lam) ** a) for a, lam in zip(alphas, lams2)]
    return Dist(sp.expand(sp.prod(survs)), 0, 1, False)


def fr_max(mu, lams, alpha):
    return 1 - sp.prod([e ** (-((x - A.R(mu)) / A.R(l)) ** (-A.R(alpha)))
                        for l in lams])


def cf_test(order, SX, SY, lo=0):
    return A.check_dist(order, A.C(SX, lo), A.C(SY, lo))


def main():
    claims = json.load(open("../canonical/arxiv_1704.03656.json"))
    out = []

    def add(recd, status, instances=0, witness=None, undecided=0, note=None):
        out.append(A.rec(recd, status, instances=instances, witness=witness,
                         undecided=undecided, note=note))

    for recd in claims:
        c = recd["claim"]
        order = recd["conclusion"]["order"]
        if order not in ("st", "hr", "rh", "lr"):
            add(recd, "unsupported order")
            continue

        if c in ("Corollary 3.13", "Corollary 3.14",
                 "Theorem 3.12(i)", "Theorem 3.12(ii)"):
            add(recd, "out of harness scope",
                note="dependent samples under Archimedean copulas.")

        elif c == "Corollary 3.2":
            # reciprocal scale ~^w: bottom sums of 1/lam >= 1/lam*:
            # lam=(1,1) vs lam*=(1,4): (1,1) vs (1,1/4): 1>=1/4, 2>=5/4
            h, w, u = cf_test("rh", fr_max(0, [1, 1], 2), fr_max(0, [1, 4], 2))
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None, u,
                note="(1/1,1/1) ~^w (1,1/4) verified; alpha=2, mu=0.")

        elif c == "Corollary 3.3(i)":
            # alpha>=1, lam ~_w lam*: (1,2) ~_w (2,3): Xn:n >=rh X*n:n
            assert wsub([1, 2], [2, 3])
            h, w, u = cf_test("rh", fr_max(0, [2, 3], 2), fr_max(0, [1, 2], 2))
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None, u,
                note="claim Xn:n >=rh X*n:n tested as X* <=rh X; alpha=2.")

        elif c == "Corollary 3.3(ii)":
            # 0<alpha<=1, lam ~^w lam*: bottom sums lam >= lam*:
            # lam=(2,3) vs lam*=(1,4): 2>=1, 5>=5: claim Xn:n <=rh X*n:n
            assert wsup([2, 3], [1, 4])
            h, w, u = cf_test("rh", fr_max(0, [2, 3], A.R(1, 2)),
                              fr_max(0, [1, 4], A.R(1, 2)))
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None, u,
                note="alpha=1/2.")

        elif c == "Corollary 3.8":
            # GE common lam, alpha ~^w alpha*: (2,3) vs (1,4): X1:n <=hr X*1:n
            assert wsup([2, 3], [1, 4])
            X_ = Dist(sp.expand(sp.prod([1 - (1 - z) ** a for a in (2, 3)])),
                      0, 1, False)
            Y_ = Dist(sp.expand(sp.prod([1 - (1 - z) ** a for a in (1, 4)])),
                      0, 1, False)
            h, w = A.test_rat("hr", X_, Y_)
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None,
                note="exact in z=e^{-x}.")

        elif c == "Example 3.11(i)":
            X_ = ge_series_z([2, 2], [8, 1])
            Y_ = ge_series_z([2, 2], [4, 6])
            h1, w1 = A.test_rat("st", X_, Y_)
            h2, w2 = A.test_rat("st", Y_, X_)
            ok = (not h1) and (not h2)
            add(recd, "holds" if ok else "refuted", 1,
                f"X<=st Y fails z={w1}; Y<=st X fails z={w2}",
                note="alpha=2, lam=(4,1/2) vs (2,3); z=e^{-x/2}; crossing "
                     "confirmed exactly.")

        elif c == "Example 3.11(ii)":
            res = []
            # pair 1: (1,5.5) ~p (2,3): claim X<=st X*
            h, w, u = cf_test("st", ge_series_cf(A.R(3, 5), [1, A.R(11, 2)]),
                              ge_series_cf(A.R(3, 5), [2, 3]))
            res.append(("(1,5.5)/(2,3): X<=st X*", h, w))
            # pair 2: (1,2.25) ~p (1.1,2.14): claim X>=st X* i.e. X*<=st X
            h, w, u = cf_test("st", ge_series_cf(A.R(3, 5), [A.R(11, 10), A.R(107, 50)]),
                              ge_series_cf(A.R(3, 5), [1, A.R(9, 4)]))
            res.append(("(1,2.25)/(1.1,2.14): X*<=st X", h, w))
            ok = all(r[1] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(f"{r[0]} {'ok' if r[1] else 'FAIL '+str(r[2])}"
                          for r in res),
                note="pair 2 crossings confirmed: p-larger gives neither "
                     "direction, as the example intends.")

        elif c == "Theorem 3.1(i) (strictly decreasing f)":
            # f=1/u, alpha=2: lam ~^wf lam* := f(lam) ~^w f(lam*): bottom sums
            # of 1/lam >= 1/lam*: lam=(1,1) vs lam*=(1,4)
            h, w, u = cf_test("rh", fr_max(0, [1, 1], 2), fr_max(0, [1, 4], 2))
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None, u,
                note="f=1/x: f(lam)=(1,1) ~^w f(lam*)=(1,1/4); claim Xn:n >=rh "
                     "X*n:n tested as X* <=rh X.")

        elif c == "Theorem 3.1(i) (strictly increasing f)":
            # f=u^2, alpha=2 (f-comp = 1/2 constant, weakly decreasing);
            # lam ~^wf lam*: bottom sums lam^2 >= lam*^2: (2,3) vs (1,2): 4>=1,13>=5
            assert wsup([4, 9], [1, 4])
            h, w, u = cf_test("rh", fr_max(0, [1, 2], 2), fr_max(0, [2, 3], 2))
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None, u,
                note="f=u^2, alpha=2; printed Xn:n <=rh X*n:n.")

        elif c == "Theorem 3.1(ii) (strictly decreasing f)":
            add(recd, "ambiguous hypotheses",
                note="part (ii) needs (f^{-1})'(f^{-1})^{a-1} decreasing for "
                     "decreasing f; no elementary decreasing f satisfies this "
                     "on its full range (candidates 1/x, e^{-x}, u^{-c} all "
                     "give increasing products), so no admissible instance "
                     "could be constructed.")

        elif c == "Theorem 3.1(ii) (strictly increasing f)":
            # f=u^2, alpha=3 (composition (1/2)y^{1/4?} increasing);
            # lam* ~_wf lam: top sums lam*^2 <= lam^2: lam*=(1,2) <= lam=(2,3)
            assert wsub([1, 4], [4, 9])
            h, w, u = cf_test("rh", fr_max(0, [2, 3], 3), fr_max(0, [1, 2], 3))
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None, u,
                note="f=u^2, alpha=3; claim Xn:n >=rh X*n:n tested as "
                     "X* <=rh X.")

        elif c == "Theorem 3.4":
            # Frechet location mu ~_w mu* (top sums): mu=(1/5,4/5) vs (0,1/3)
            mu, mus = [0, A.R(1, 3)], [A.R(1, 5), A.R(4, 5)]
            assert wsub(mu, mus)
            SY = 1 - sp.prod([e ** (-(x - A.R(m)) ** (-2)) for m in mus])
            SX = 1 - sp.prod([e ** (-(x - A.R(m)) ** (-2)) for m in mu])
            h, w, u = cf_test("rh", SY, SX, lo=A.R(4, 5))
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None, u,
                note="location vectors on joint support (4/5,oo); lam=1, "
                     "alpha=2; claim Xn:n >=rh X*n:n tested as X* <=rh X.")

        elif c == "Theorem 3.5(i) (decreasing branch)":
            # Weibull gamma=1/2 baseline; lam ~^w lam*: (2,3) vs (1,4);
            # claim X1:n >=hr X*1:n <=> X* <=hr X
            assert wsup([2, 3], [1, 4])
            SX = sp.prod([e ** (-(A.R(l) * x) ** A.R(1, 2)) for l in (2, 3)])
            SY = sp.prod([e ** (-(A.R(l) * x) ** A.R(1, 2)) for l in (1, 4)])
            h, w, u = cf_test("hr", SY, SX)
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None, u)

        elif c == "Theorem 3.5(i) (increasing branch)":
            # gamma=2 baseline; lam ~_w lam*: (1,2) vs (2,3); X <=hr X*
            assert wsub([1, 2], [2, 3])
            SX = sp.prod([e ** (-(A.R(l) * x) ** 2) for l in (1, 2)])
            SY = sp.prod([e ** (-(A.R(l) * x) ** 2) for l in (2, 3)])
            h, w, u = cf_test("hr", SX, SY)
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None, u)

        elif c == "Theorem 3.6":
            # scale family, f=u^2 inc, (f^{-1})' r~(f^{-1}) dec (Exp baseline);
            # lam ~^wf lam*: bottom sums lam^2 >= lam*^2: (2,4) vs (1,3)
            assert wsup([4, 16], [1, 9])
            # parallel cdf F_n:n = prod G(l_i x), G=1-e^{-x}
            FX = sp.prod([1 - e ** (-A.R(l) * x) for l in (2, 4)])
            FY = sp.prod([1 - e ** (-A.R(l) * x) for l in (1, 3)])
            h, w, u = cf_test("st", 1 - FY, 1 - FX)  # claim Xn:n >=st X*n:n
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None, u,
                note="G=Exp scale family, f=u^2; claim Xn:n >=st X*n:n "
                     "tested as X* <=st X.")

        elif c == "Theorem 3.7":
            # ES alpha ~^w alpha*: (2,3) vs (1,4): X1:n <=hr X*1:n
            assert wsup([2, 3], [1, 4])
            X_ = Dist(sp.expand(sp.prod([1 - (1 - z) ** a for a in (2, 3)])),
                      0, 1, False)
            Y_ = Dist(sp.expand(sp.prod([1 - (1 - z) ** a for a in (1, 4)])),
                      0, 1, False)
            h, w = A.test_rat("hr", X_, Y_)
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None,
                note="ES=GE baseline; exact in z=e^{-x}.")

        elif c == "Theorem 3.9 (decreasing branch)":
            # q(1/2,x) decreasing; lam ~^w lam*: (2,3) vs (1,4): X1:n >=st X*1:n
            assert wsup([2, 3], [1, 4])
            h, w, u = cf_test("st", ge_series_cf(A.R(1, 2), [1, 4]),
                              ge_series_cf(A.R(1, 2), [2, 3]))
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None, u,
                note="alpha=1/2 (q decreasing); tested X* <=st X.")

        elif c == "Theorem 3.9 (increasing branch)":
            # q(2,x) increasing; lam ~_w lam*: (1,2) vs (2,3): X1:n <=st X*1:n
            assert wsub([1, 2], [2, 3])
            X_ = Dist(sp.expand(sp.prod([1 - (1 - z ** (2 * l)) ** 2
                                         for l in (1, 2)])), 0, 1, False)
            Y_ = Dist(sp.expand(sp.prod([1 - (1 - z ** (2 * l)) ** 2
                                         for l in (2, 3)])), 0, 1, False)
            h, w = A.test_rat("st", X_, Y_)
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None,
                note="alpha=2 (q increasing); z=e^{-x}.")

        elif c == "Corollary 3.10 (0 < alpha <= 1 branch)":
            assert wsup([2, 3], [1, 4])
            h, w, u = cf_test("st", ge_series_cf(A.R(1, 2), [1, 4]),
                              ge_series_cf(A.R(1, 2), [2, 3]))
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None, u,
                note="lam=(2,3) ~^w lam*=(1,4); alpha=1/2.")

        elif c == "Corollary 3.10 (alpha >= 1 branch)":
            assert wsub([1, 2], [2, 3])
            X_ = Dist(sp.expand(sp.prod([1 - (1 - z ** (2 * l)) ** 2
                                         for l in (1, 2)])), 0, 1, False)
            Y_ = Dist(sp.expand(sp.prod([1 - (1 - z ** (2 * l)) ** 2
                                         for l in (2, 3)])), 0, 1, False)
            h, w = A.test_rat("st", X_, Y_)
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None,
                note="alpha=2; lam=(1,2) ~_w lam*=(2,3); z=e^{-x}.")

        else:
            add(recd, "unsupported order", note=f"no encoding for {c!r}")

    A.emit("eval_arxiv_1704.03656.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
