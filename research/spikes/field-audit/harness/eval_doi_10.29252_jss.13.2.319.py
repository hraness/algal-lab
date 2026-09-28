"""Evaluator for doi:10.29252/jss.13.2.319 (GLFR series/parallel systems).

GLFR(alpha, beta, lam): F(x) = (1 - e^{-(alpha x + beta x^2/2)})^lam,
x > 0.  Series min survival prod(1-F_i); parallel max cdf prod F_i.

Majorization here: "a majorizes b on D+" = top sums of a >= b's, equal
totals (both vectors descending).  "unordered majorization" (uo): partial
sums in the listed order.  "weighted majorization w.r.t. weights lam on
D_n^pi": printed example satisfies equality of totals and smaller partial
sums for the alpha side: sum_{i<=k} lam_{pi_i} a_{pi_i} <= ... nu.
"""
import json
import auditlib as A
import sympy as sp

x = A.x
e = A.e


def F_i(a, b, l):
    return (1 - e ** (-(A.R(a) * x + A.R(b) * x ** 2 / 2))) ** A.R(l)


def series_surv(ps):
    return sp.prod([1 - F_i(*p) for p in ps])


def parallel_cdf(ps):
    return sp.prod([F_i(*p) for p in ps])


def test(SA, SB):
    return A.check_dist("st", A.C(SA), A.C(SB))


def main():
    claims = json.load(open("../canonical/doi_10.29252_jss.13.2.319.json"))
    out = []

    def add(recd, status, instances=0, witness=None, undecided=0, note=None):
        out.append(A.rec(recd, status, instances=instances, witness=witness,
                         undecided=undecided, note=note))

    for recd in claims:
        c = recd["claim"]
        order = recd["conclusion"]["order"]
        if order != "st":
            add(recd, "unsupported order")
            continue

        if c.startswith("Example 1"):
            # Thm 7 instance: lam=(1,2,3), gamma=(2,2.5,1.5), alpha=(2,3,4),
            # nu=(1,2,5), pi=(3,2,1), common beta=1. Claim X3:3 >=st Y3:3.
            beta = 1
            PX = [(a, beta, l) for a, l in zip((2, 3, 4), (1, 2, 3))]
            PY = [(n, beta, g) for n, g in zip((1, 2, 5), (2, A.R(5, 2), A.R(3, 2)))]
            SX = 1 - parallel_cdf(PX)
            SY = 1 - parallel_cdf(PY)
            h, w, u = test(SY, SX)  # X >=st Y
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None, u,
                note="printed numbers; weighted maj: pi=(3,2,1): "
                     "lam_pi a_pi = 12,6,2 partials <= 15,4,1; uo: "
                     "gamma partials 2,4.5,6 >= 1,3,6. "
                     "FY-FX < 0 at x=1/2,1,2 (e.g. -0.3507 at x=1): the "
                     "printed ordering is reversed throughout the interior.")

        elif c == "Theorem 1 (قضیه ١)":
            # alpha ~m nu on D+, beta ~m mu on D+, common lam>=1;
            # claim Y_{1:n} >=st X_{1:n}
            res = []
            for al, nu, be, mu, l in [([3, 2, 1], [2, 2, 2], [4, 2, 1], [3, 3, 1], 2),
                                      ([5, 3, 1], [4, 3, 2], [3, 1], [2, 2], A.R(3, 2))]:
                assert A.majorized(nu, al) and A.majorized(mu, be)
                PX = [(a, b, l) for a, b in zip(al, be)]
                PY = [(n, m, l) for n, m in zip(nu, mu)]
                SX, SY = series_surv(PX), series_surv(PY)
                h, w, uu = test(SX, SY)   # X_{1:n} <=st Y_{1:n}
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]),
                note="alpha ~m nu, beta ~m mu on D+, lam>=1; claim "
                     "Y_{1:n} >=st X_{1:n}.")

        elif c == "Theorem 2 (قضیه ٢)":
            # alpha ~m nu D+; (lam-1) ~m (gamma-1) on E+ (ascending);
            # claim Y_{1:n} >=st X_{1:n}
            res = []
            for al, nu, lm, gm in [([3, 2, 1], [2, 2, 2],
                                    [2, 3, 4], [A.R(5, 2), 3, A.R(7, 2)]),
                                   ([4, 3, 1], [3, 3, 2],
                                    [A.R(3, 2), 2, A.R(5, 2)], [2, 2, 2])]:
                assert A.majorized(nu, al)
                lm1 = [l - 1 for l in lm]
                gm1 = [g - 1 for g in gm]
                assert A.majorized(gm1, lm1)
                assert A.asc(lm1) == list(lm1)  # E+ ascending
                PX = [(a, 1, l) for a, l in zip(al, lm)]
                PY = [(n, 1, g) for n, g in zip(nu, gm)]
                SX, SY = series_surv(PX), series_surv(PY)
                h, w, uu = test(SX, SY)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]),
                note="common beta=1; lam-1 ~m gamma-1 on E+.")

        elif c == "Theorem 3 (قضیه ٣)":
            res = []
            for be, mu, lm, gm in [([4, 2, 1], [3, 3, 1],
                                    [2, 3, 4], [A.R(5, 2), 3, A.R(7, 2)]),
                                   ([5, 3, 1], [4, 3, 2],
                                    [3, 4], [A.R(7, 2), A.R(7, 2)])]:
                assert A.majorized(mu, be)
                lm1 = [l - 1 for l in lm]
                gm1 = [g - 1 for g in gm]
                assert A.majorized(gm1, lm1)
                PX = [(1, b, l) for b, l in zip(be, lm)]
                PY = [(1, m, g) for m, g in zip(mu, gm)]
                SX, SY = series_surv(PX), series_surv(PY)
                h, w, uu = test(SX, SY)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]),
                note="common alpha=1; beta ~m mu on D+, lam-1 ~m gamma-1 E+.")

        elif c == "Theorem 4 (قضیه ۴)":
            # alpha ~m nu, beta ~m mu on D+, common lam; X_{n:n} >=st Y_{n:n}
            res = []
            for al, nu, be, mu, l in [([3, 2, 1], [2, 2, 2], [4, 2, 1], [3, 3, 1], A.R(1, 2)),
                                      ([5, 3], [4, 4], [3, 1], [2, 2], 3)]:
                assert A.majorized(nu, al) and A.majorized(mu, be)
                PX = [(a, b, l) for a, b in zip(al, be)]
                PY = [(n, m, l) for n, m in zip(nu, mu)]
                SX = 1 - parallel_cdf(PX)
                SY = 1 - parallel_cdf(PY)
                h, w, uu = test(SY, SX)   # X_{n:n} >=st Y_{n:n}
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]),
                note="no lam>=1 restriction per canonical; lam=1/2 and 3 "
                     "tested.")

        elif c == "Theorem 5 (قضیه ۵)":
            res = []
            for al, nu, lm, gm in [([3, 2, 1], [2, 2, 2],
                                    [1, 2, 4], [2, 3, 2]),
                                   ([4, 3, 1], [3, 3, 2],
                                    [1, 3], [A.R(3, 2), A.R(5, 2)])]:
                assert A.majorized(nu, al) and A.majorized(gm, lm)
                assert A.asc(lm) == list(lm)
                PX = [(a, 1, l) for a, l in zip(al, lm)]
                PY = [(n, 1, g) for n, g in zip(nu, gm)]
                SX = 1 - parallel_cdf(PX)
                SY = 1 - parallel_cdf(PY)
                h, w, uu = test(SY, SX)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]),
                note="common beta=1; lam ~m gamma on E+. Instance 2 "
                     "(alpha=(4,3,1),nu=(3,3,2),lam=(1,3),gamma=(3/2,5/2)) "
                     "has FY-FX<0 at x=1/10 and x=1: claim fails.")

        elif c == "Theorem 6 (قضیه ۶)":
            res = []
            for be, mu, lm, gm in [([4, 2, 1], [3, 3, 1],
                                    [1, 2, 4], [2, 3, 2]),
                                   ([5, 3, 1], [4, 3, 2],
                                    [1, 3], [A.R(3, 2), A.R(5, 2)])]:
                assert A.majorized(mu, be) and A.majorized(gm, lm)
                assert A.asc(lm) == list(lm)
                PX = [(1, b, l) for b, l in zip(be, lm)]
                PY = [(1, m, g) for m, g in zip(mu, gm)]
                SX = 1 - parallel_cdf(PX)
                SY = 1 - parallel_cdf(PY)
                h, w, uu = test(SY, SX)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]),
                note="common alpha=1. Instance 2 (beta=(5,3,1),mu=(4,3,2),"
                     "lam=(1,3),gamma=(3/2,5/2)) has FY-FX<0 at interior "
                     "points 1e-4, 1/10: claim fails.")

        elif c == "Theorem 7 (قضیه ٧)":
            # same instance as Example 1 (which applies this theorem)
            beta = 1
            PX = [(a, beta, l) for a, l in zip((2, 3, 4), (1, 2, 3))]
            PY = [(n, beta, g) for n, g in zip((1, 2, 5), (2, A.R(5, 2), A.R(3, 2)))]
            SX = 1 - parallel_cdf(PX)
            SY = 1 - parallel_cdf(PY)
            h, w, u = test(SY, SX)
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None, u,
                note="Example-1 instance: weighted partial sums of "
                     "lam_pi*alpha_pi <= nu side; gamma uo-majorizes lam.")

        elif c == "Theorem 8 (قضیه ٨)":
            # beta weighted-majorizes mu w.r.t. lam on D_n^pi; gamma uo ~ lam.
            # Constructed: pi=(2,1), n=2, lam=(1,2): lam_pi=(2,1);
            # beta=(5,1/2): beta_pi=(1/2,5): weighted partials 1,6;
            # mu=(4,1): mu_pi=(1,4): weighted partials 2,6 -> 1<=2,6=6.
            # gamma uo-majorizes lam=(1,2): gamma=(3/2,3/2): 1.5>=1,3=3.
            alpha = 1
            PX = [(alpha, b, l) for b, l in zip((5, A.R(1, 2)), (1, 2))]
            PY = [(alpha, m, g) for m, g in zip((4, 1), (A.R(3, 2), A.R(3, 2)))]
            SX = 1 - parallel_cdf(PX)
            SY = 1 - parallel_cdf(PY)
            h, w, u = test(SY, SX)
            add(recd, "holds" if h else "refuted", 1, str(w) if w else None, u,
                note="constructed n=2 instance with pi=(2,1): weighted "
                     "partials 1,6 <= 2,6; gamma=(3/2,3/2) uo-maj (1,2).")

        else:
            add(recd, "unsupported order", note=f"no encoding for {c!r}")

    A.emit("eval_doi_10.29252_jss.13.2.319.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
