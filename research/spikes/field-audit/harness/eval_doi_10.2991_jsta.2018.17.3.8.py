"""Evaluator for doi:10.2991/jsta.2018.17.3.8 (GE/ES/Frechet systems, indep.).

Models:
  GE(a,l):  F = (1 - e^{-l x})^a             (series survival = prod(1-F_i))
  ES(a,l):  F = (1 - e^{-l x})^a  [exp baseline]
  Frechet(mu,l,a): F = exp(-((x-mu)/l)^{-a})   (parallel cdf = prod F_i)
  scale family:  F_i = G(l_i x), G = 1-e^{-x^g}

Majorization convention (this paper, Def 2.2):
  x ~_w y  :=  top-j sums of x <= y's      (weak SUBmajorization)
  x ~^w y  :=  bottom-j sums of x >= y's   (weak SUPERmajorization)
  x ~^p y  :=  products of smallest j of x <= y's   (p-larger)
  f-versions apply the same to f(x), f(y) coordinatewise.
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
    """x ~^w y : smallest-j sums of x >= of y."""
    ax, ay = A.asc(x), A.asc(y)
    return all(sum(ax[:j]) >= sum(ay[:j]) for j in range(1, len(x) + 1))


def ge_surv(a, lam):
    """GE survival in z=e^{-x}; integer a, lam."""
    return Dist(sp.expand(1 - (1 - z ** lam) ** a), 0, 1, False)


def ge_series_z(alphas, lams_D2):
    """GE(a, lam_i) series with z=e^{-x/2}, so exponents 2 lam_i integer."""
    survs = [sp.expand(1 - (1 - z ** lam) ** a) for a, lam in zip(alphas, lams_D2)]
    return Dist(sp.expand(sp.prod(survs)), 0, 1, False)


def ge_series_cf(alpha, lams):
    return sp.prod([1 - (1 - e ** (-A.R(l) * x)) ** A.R(alpha) for l in lams])


def frechet_max_surv(mu, lams, alpha, lo=None):
    F = sp.prod([e ** (-((x - mu) / A.R(l)) ** (-A.R(alpha))) for l in lams])
    lo = R_lo = lo if lo is not None else mu
    return A.C(1 - F, lo, sp.oo)


def scale_series_cf(gamma, lams):
    return sp.prod([e ** (-(A.R(l) * x) ** gamma) for l in lams])


def es_series_cf(alpha, lams, Gfun=None):
    return sp.prod([1 - (1 - e ** (-A.R(l) * x)) ** A.R(alpha) for l in lams])


def main():
    claims = json.load(open("../canonical/doi_10.2991_jsta.2018.17.3.8.json"))
    out = []

    def add(recd, status, instances=0, witness=None, undecided=0, note=None):
        out.append(A.rec(recd, status, instances=instances, witness=witness,
                         undecided=undecided, note=note))

    def cf_test(order, SX, SY, lo=0):
        return A.check_dist(order, A.C(SX, lo), A.C(SY, lo))

    for recd in claims:
        c = recd["claim"]
        order = recd["conclusion"]["order"]
        if order not in ("st", "hr", "rh", "lr"):
            add(recd, "unsupported order")
            continue

        if c in ("Corollary 3.6", "Corollary 3.7", "Theorem 3.7(i)",
                 "Theorem 3.7(ii)"):
            add(recd, "out of harness scope",
                note="dependent samples under Archimedean copulas.")

        elif c == "Example 3.1(i)":
            # GE a=2, lam=(4,1/2) vs (2,3): non-ordering; z=e^{-x/2}
            X = ge_series_z([2, 2], [8, 1])
            Y = ge_series_z([2, 2], [4, 6])
            h1, w1 = A.test_rat("st", X, Y)
            h2, w2 = A.test_rat("st", Y, X)
            ok = (not h1) and (not h2)
            add(recd, "holds" if ok else "refuted", 1,
                f"X<=st Y fails z={w1}; Y<=st X fails z={w2}",
                note="exact check: survivals cross, consistent with Fig. 1.")

        elif c == "Corollary 3.1":
            # (1/λ*) ~^w (1/λ): λ*=(1,1), λ=(2,4); claim X* <=rh X
            lam, lams = [2, 4], [1, 1]
            inv_l, inv_ls = [A.R(1) / v for v in lam], [A.R(1) / v for v in lams]
            assert wsup(inv_ls, inv_l)
            h, w, u = cf_test("rh", frechet_max_surv(0, lams, 2).survival,
                              frechet_max_surv(0, lam, 2).survival)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, u, note="alpha=2, mu=0.")

        elif c == "Corollary 3.2(i)":
            # (λ*)^r ~_w λ^r: λ*=(1,2), λ=(2,3), r=1, a=2: claim X* <=rh X
            assert wsub([1, 2], [2, 3])
            h, w, u = cf_test("rh", frechet_max_surv(0, [1, 2], 2).survival,
                              frechet_max_surv(0, [2, 3], 2).survival)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, u)

        elif c == "Corollary 3.2(ii)":
            # (λ*)^r ~^w λ^r: λ*=(3,3), λ=(1,4), r=1, a=1/2: claim X <=rh X*
            assert wsup([3, 3], [1, 4])
            h, w, u = cf_test("rh", frechet_max_surv(0, [1, 4], A.R(1, 2)).survival,
                              frechet_max_surv(0, [3, 3], A.R(1, 2)).survival)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, u)

        elif c == "Corollary 3.3(i)":
            # homogeneous X* scale lam* <= r-th mean of lam; a=2,r=1
            h, w, u = cf_test("rh", frechet_max_surv(0, [2, 2], 2).survival,
                              frechet_max_surv(0, [1, 4], 2).survival)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, u,
                note="lam*=2 <= mean(1,4)=5/2; alpha=2=r? used r=1, alpha=2>r.")

        elif c == "Corollary 3.3(ii)":
            h, w, u = cf_test("rh", frechet_max_surv(0, [1, 2], A.R(1, 2)).survival,
                              frechet_max_surv(0, [2, 2], A.R(1, 2)).survival)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, u,
                note="lam*=2 >= mean(1,2)=3/2; alpha=1/2 <= r=1.")

        elif c == "Corollary 3.4":
            # GE common lam=1; alpha* ~^w alpha: (3,3) vs (1,4); X1:n <=hr X*1:n
            assert wsup([3, 3], [1, 4])
            X = Dist(sp.expand(sp.prod([1 - (1 - z) ** a for a in (1, 4)])), 0, 1, False)
            Y = Dist(sp.expand(sp.prod([1 - (1 - z) ** a for a in (3, 3)])), 0, 1, False)
            h, w = A.test_rat("hr", X, Y)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, note="exact in z=e^{-x}.")

        elif c == "Corollary 3.5":
            # reading A: a=1/2, lam*~^w lam -> X* <=st X ; reading B: a=2,
            # lam* ~_w lam -> X <=st X*
            res = []
            h, w, u = cf_test("st", ge_series_cf(A.R(1, 2), [3, 3]),
                              ge_series_cf(A.R(1, 2), [1, 4]))
            res.append(("A", h, w))
            X = Dist(sp.expand(sp.prod([1 - (1 - z ** l) ** 2 for l in (2, 3)])), 0, 1, False)
            Y = Dist(sp.expand(sp.prod([1 - (1 - z ** l) ** 2 for l in (1, 2)])), 0, 1, False)
            h2, w2 = A.test_rat("st", X, Y)
            res.append(("B", h2, w2))
            ok = all(r[1] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(f"{r[0]}:{'ok' if r[1] else 'fail '+str(r[2])}"
                          for r in res))

        elif "Example 3.1(ii)" in c:
            # case A: (1,5.5) vs (2,3), claim X<=st X* ; case B: (1,2.25) vs
            # (1.1,2.14), claim X*<=st X
            res = []
            if "second case" not in c:
                h, w, u = cf_test("st", ge_series_cf(A.R(3, 5), [1, A.R(11, 2)]),
                                  ge_series_cf(A.R(3, 5), [2, 3]))
                res.append(("A", h, w))
            if "first case" not in c:
                h, w, u = cf_test("st", ge_series_cf(A.R(3, 5), [A.R(11, 10), A.R(107, 50)]),
                                  ge_series_cf(A.R(3, 5), [1, A.R(9, 4)]))
                res.append(("B", h, w))
            ok = all(r[1] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(f"{r[0]}:{'ok' if r[1] else 'fail '+str(r[2])}"
                          for r in res),
                note="printed st directions; case B survivals cross (S_X-S_X* "
                     "changes sign), consistent with the example's purpose: "
                     "p-larger implies neither direction for alpha<1.")

        elif c == "Theorem 3.1(i)":
            res = []
            # reading A: f=1/u decreasing, f-comp increasing; λ*~^wf λ:
            # bottom sums of 1/λ* >= 1/λ:  λ*=(1,1), λ=(2,4)
            h, w, u = cf_test("rh", frechet_max_surv(0, [1, 1], 2).survival,
                              frechet_max_surv(0, [2, 4], 2).survival)
            res.append(("A", h, w))
            # reading B: f=u^2 increasing, f-comp decreasing (a=2 gives const);
            # λ*^2 bottom >= λ^2: λ*=(2,3), λ=(1,2)
            assert wsup([4, 9], [1, 4])
            h, w, u = cf_test("rh", frechet_max_surv(0, [1, 2], 2).survival,
                              frechet_max_surv(0, [2, 3], 2).survival)
            res.append(("B", h, w))
            ok = all(r[1] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(f"{r[0]}:{'ok' if r[1] else 'fail '+str(r[2])}"
                          for r in res))

        elif c == "Theorem 3.1(ii)":
            res = []
            # reading B: f=u^2 inc, comp increasing needs alpha>2: a=3;
            # f(λ) ~_w f(λ*): top sums λ^2 <= λ*^2: λ=(1,2), λ*=(2,3)
            assert wsub([1, 4], [4, 9])
            h, w, u = cf_test("rh", frechet_max_surv(0, [2, 3], 3).survival,
                              frechet_max_surv(0, [1, 2], 3).survival)
            res.append(("B", h, w))
            ok = all(r[1] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(f"{r[0]}:{'ok' if r[1] else 'fail '+str(r[2])}"
                          for r in res),
                note="reading B tested (f=u^2, alpha=3): observed direction is "
                     "X <=rh X*, opposite of printed. Reading A skipped: no "
                     "elementary decreasing f satisfies the printed "
                     "decreasing-composition condition.")

        elif c == "Theorem 3.2":
            # Frechet location mu* ~_w mu (top sums): mu*=(0,1/3) <= mu=(1/5,4/5)
            # common support (4/5, oo); non-dyadic mu avoid the resolvable_top
            # dyadic sample points (frozen harness probes top = 2^k/64).
            mu, mus = [A.R(1, 5), A.R(4, 5)], [0, A.R(1, 3)]
            assert wsub(mus, mu)
            h, w, u = A.check_dist("rh",
                                   A.C(1 - sp.prod([e ** (-(x - A.R(m)) ** (-2)) for m in mus]), A.R(4, 5)),
                                   A.C(1 - sp.prod([e ** (-(x - A.R(m)) ** (-2)) for m in mu]), A.R(4, 5)))
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, u,
                note="location vectors on joint support (4/5,oo); lam=alpha=1... "
                     "lam=1, alpha=2.")

        elif c == "Theorem 3.3(i)":
            res = []
            # reading A: gamma=1/2 baseline (x r inc, x^2 r' dec), lam*~^w lam
            assert wsup([3, 3], [1, 4])
            h, w, u = cf_test("hr", scale_series_cf(A.R(1, 2), [3, 3]),
                              scale_series_cf(A.R(1, 2), [1, 4]))
            res.append(("A", h, w))
            # reading B: gamma=2 baseline (x r inc, x^2 r' inc), lam* ~_w lam;
            # claim X1:n <=hr X*1:n  <=>  h_X >= h_X* : pass (X, X*)
            assert wsub([1, 2], [2, 3])
            h, w, u = cf_test("hr", scale_series_cf(A.R(2), [2, 3]),
                              scale_series_cf(A.R(2), [1, 2]))
            res.append(("B", h, w))
            ok = all(r[1] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(f"{r[0]}:{'ok' if r[1] else 'fail '+str(r[2])}"
                          for r in res),
                note="baseline G=1-e^{-x^gamma}, gamma=1/2 (A) / 2 (B).")

        elif c == "Theorem 3.4":
            # scale family, f=u^2 inc, (f^{-1})' r~(f^{-1}) decreasing (Exp r~);
            # f(λ*) ~^w f(λ): λ*=(3,4), λ=(2,3): 9>=4, 25>=13
            assert wsup([9, 16], [4, 9])
            FX = sp.prod([1 - e ** (-A.R(l) * x) for l in (2, 3)])
            FY = sp.prod([1 - e ** (-A.R(l) * x) for l in (3, 4)])
            # claim: X* <=st X  (printed X >=st X*): test st(X* surv, X surv)
            h, w, u = cf_test("st", 1 - FY, 1 - FX)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, u,
                note="G=Exp baseline, f=u^2, lambda*=(3,4) f-supermajorized "
                     "reading; printed Xn:n >=st X* tested as X* <=st X.")

        elif c == "Theorem 3.5":
            # ES alpha* ~^w alpha, common lam -> X1:n <=hr X*1:n
            assert wsup([3, 3], [1, 4])
            X = Dist(sp.expand(sp.prod([1 - (1 - z) ** a for a in (1, 4)])), 0, 1, False)
            Y = Dist(sp.expand(sp.prod([1 - (1 - z) ** a for a in (3, 3)])), 0, 1, False)
            h, w = A.test_rat("hr", X, Y)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, note="GE baseline lam=1, exact.")

        elif c == "Theorem 3.6":
            res = []
            # reading A: alpha=1/2 (q decreasing), lam* ~^w lam: X* <=st X
            assert wsup([3, 3], [1, 4])
            h, w, u = cf_test("st", ge_series_cf(A.R(1, 2), [3, 3]),
                              ge_series_cf(A.R(1, 2), [1, 4]))
            res.append(("A", h, w))
            # reading B: alpha=2 (q increasing), lam* ~_w lam: X <=st X*
            assert wsub([1, 2], [2, 3])
            X = Dist(sp.expand(sp.prod([1 - (1 - z ** l) ** 2 for l in (2, 3)])), 0, 1, False)
            Y = Dist(sp.expand(sp.prod([1 - (1 - z ** l) ** 2 for l in (1, 2)])), 0, 1, False)
            h2, w2 = A.test_rat("st", X, Y)
            res.append(("B", h2, w2))
            ok = all(r[1] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(f"{r[0]}:{'ok' if r[1] else 'fail '+str(r[2])}"
                          for r in res))

        else:
            add(recd, "unsupported order", note=f"no encoding for {c!r}")

    A.emit("eval_doi_10.2991_jsta.2018.17.3.8.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
