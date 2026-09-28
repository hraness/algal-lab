"""Evaluator for arXiv:2402.02945 (Archimax copulas, order statistics).

Archimax copula C(u) = phi(l_A(psi(u))).  For Gumbel-Hougaard stdf
l(x) = (sum x_i^t)^{1/t}, the symmetric point gives n*A_n = n^{1/t}.

Homogeneous U(0,1) margins:
  GH generator phi=e^{-t^{1/th}}, psi(u)=(-log u)^th:
     F_{k:k}(x)   = x^{k^{1/th^2}}
     F_{k-1:k}(x) = k x^{(k-1)^{1/th^2}} - (k-1) x^{k^{1/th^2}}
  Lomax survival copula phi=(1+t)^{-th}, psi(u)=u^{-1/th}-1, GH stdf:
     S_{1:n}(x) = (1 + n^{1/th}((1-x)^{-1/th}-1))^{-th}
     S_{2:n}(x) = n (1 + (n-1)^{1/th}((1-x)^{-1/th}-1))^{-th}
                  - (n-1)(1 + n^{1/th}((1-x)^{-1/th}-1))^{-th}
For Thm 3.1 / Cor 3.1 the independence generators phi1=phi2=e^{-t}
satisfy all copula conditions with A=1, reducing the PHR model to
independent products F_n:n = prod(1-Bbar^{a_i}).
"""
import json
import auditlib as A
import sympy as sp

x = A.x
e = A.e


def gh_fmax(k, th):
    return x ** (A.R(k) ** (1 / A.R(th) ** 2))


def gh_fsecond(n, th):
    return (n * x ** (A.R(n - 1) ** (1 / A.R(th) ** 2))
            - (n - 1) * x ** (A.R(n) ** (1 / A.R(th) ** 2)))


def lomax_smin(n, th):
    t = A.R(th)
    return (1 + A.R(n) ** (1 / t) * ((1 - x) ** (-1 / t) - 1)) ** (-t)


def lomax_ssecond(n, th):
    t = A.R(th)
    u = (1 - x) ** (-1 / t) - 1
    return (n * (1 + A.R(n - 1) ** (1 / t) * u) ** (-t)
            - (n - 1) * (1 + A.R(n) ** (1 / t) * u) ** (-t))


def test(order, SA, SB):
    return A.check_dist(order, A.C(SA, 0, 1), A.C(SB, 0, 1))


def main():
    claims = json.load(open("../canonical/arxiv_2402.02945.json"))
    out = []

    def add(recd, status, instances=0, witness=None, undecided=0, note=None):
        out.append(A.rec(recd, status, instances=instances, witness=witness,
                         undecided=undecided, note=note))

    for recd in claims:
        c = recd["claim"]
        order = recd["conclusion"]["order"]
        if (order not in ("st", "hr", "rh", "lr")
                and c not in ("Corollary 4.1", "Corollary 5.1")):
            add(recd, "unsupported order")
            continue

        if c in ("Corollary 3.1", "Theorem 3.1"):
            B = e ** (-x)
            res = []
            # this paper: b ~^w a iff smallest-j sums of b >= a's
            for alpha, beta in [([1, 4], [2, 3]), ([1, 2, 7], [3, 4, 5])]:
                assert A.weak_super(alpha, beta)
                FX = sp.prod([1 - B ** A.R(a) for a in alpha])
                FY = sp.prod([1 - B ** A.R(a) for a in beta])
                h, w, u = A.check_dist("st", A.C(1 - FY), A.C(1 - FX))
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]),
                note="independence generators phi1=phi2=e^{-t} satisfy all "
                     "copula conditions (psi2 o phi1 = id); "
                     "beta ~^w alpha (smallest sums beta >= alpha).")

        elif c == "Example 4.1(i)":
            res = []
            for SA, SB in [(1 - gh_fsecond(4, 4), 1 - gh_fmax(4, 4)),
                           (1 - gh_fmax(4, 4), 1 - gh_fmax(5, 4))]:
                h, w, u = test("rh", SA, SB)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]),
                note="GH theta=4; X3:4<=rh X4:4<=rh X5:5.")

        elif c == "Example 4.1(ii)":
            res = []
            for SA, SB in [(1 - gh_fsecond(4, 8), 1 - gh_fmax(4, 8)),
                           (1 - gh_fmax(4, 8), 1 - gh_fmax(5, 8))]:
                h, w, u = test("hr", SA, SB)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]))

        elif c == "Example 4.1(iii)":
            res = []
            for SA, SB in [(1 - gh_fsecond(4, 5), 1 - gh_fmax(4, 5)),
                           (1 - gh_fmax(4, 5), 1 - gh_fmax(5, 5))]:
                h, w, u = test("lr", SA, SB)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]))

        elif c == "Example 5.1(i)":
            res = []
            for SA, SB in [(lomax_smin(5, 4), lomax_smin(4, 4)),
                           (lomax_smin(4, 4), lomax_ssecond(4, 4))]:
                h, w, u = test("hr", SA, SB)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]))

        elif c == "Example 5.1(ii)":
            res = []
            for SA, SB in [(lomax_smin(5, 8), lomax_smin(4, 8)),
                           (lomax_smin(4, 8), lomax_ssecond(4, 8))]:
                h, w, u = test("rh", SA, SB)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]))

        elif c == "Example 5.1(iii)":
            res = []
            for SA, SB in [(lomax_smin(5, 5), lomax_smin(4, 5)),
                           (lomax_smin(4, 5), lomax_ssecond(4, 5))]:
                h, w, u = test("lr", SA, SB)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]))

        elif c == "Theorem 4.1(i)":
            res = []
            for SA, SB in [(1 - gh_fsecond(4, 4), 1 - gh_fmax(4, 4)),
                           (1 - gh_fmax(4, 4), 1 - gh_fmax(5, 4))]:
                h, w, u = test("rh", SA, SB)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]),
                note="GH theta=4 satisfies t phi'/phi decreasing.")

        elif c == "Theorem 4.1(ii)":
            res = []
            for SA, SB in [(1 - gh_fsecond(4, 8), 1 - gh_fmax(4, 8)),
                           (1 - gh_fmax(4, 8), 1 - gh_fmax(5, 8))]:
                h, w, u = test("hr", SA, SB)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]),
                note="GH theta=8 satisfies t phi'/(1-phi) increasing.")

        elif c == "Theorem 4.1(iii)":
            res = []
            for SA, SB in [(1 - gh_fsecond(4, 5), 1 - gh_fmax(4, 5)),
                           (1 - gh_fmax(4, 5), 1 - gh_fmax(5, 5))]:
                h, w, u = test("lr", SA, SB)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]),
                note="GH theta=5 satisfies t phi''/phi' decreasing.")

        elif c == "Theorem 5.1(i)":
            res = []
            for SA, SB in [(lomax_smin(5, 4), lomax_smin(4, 4)),
                           (lomax_smin(4, 4), lomax_ssecond(4, 4))]:
                h, w, u = test("hr", SA, SB)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]))

        elif c == "Theorem 5.1(ii)":
            res = []
            for SA, SB in [(lomax_smin(5, 8), lomax_smin(4, 8)),
                           (lomax_smin(4, 8), lomax_ssecond(4, 8))]:
                h, w, u = test("rh", SA, SB)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]))

        elif c == "Theorem 5.1(iii)":
            res = []
            for SA, SB in [(lomax_smin(5, 5), lomax_smin(4, 5)),
                           (lomax_smin(4, 5), lomax_ssecond(4, 5))]:
                h, w, u = test("lr", SA, SB)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]))

        elif c == "Corollary 4.1":
            # chain X_{n-1:n} <= X_{n:n} <= X_{n+1:n+1} in rh, hr, lr;
            # Archimedean case: GH theta=4
            res = []
            for order2 in ("rh", "hr", "lr"):
                g = gh_fsecond(4, 4)
                for SA, SB in [(1 - gh_fsecond(4, 4), 1 - gh_fmax(4, 4)),
                               (1 - gh_fmax(4, 4), 1 - gh_fmax(5, 4))]:
                    h, w, u = test(order2, SA, SB)
                    res.append((order2, h, w))
            ok = all(r[1] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(f"{r[0]}:{'ok' if r[1] else 'fail '+str(r[2])}"
                          for r in res),
                note="Archimedean special case tested with GH theta=4; "
                     "EV-copula case shares the same order-statistic form.")

        elif c == "Corollary 5.1":
            res = []
            for order2 in ("hr", "rh", "lr"):
                for SA, SB in [(lomax_smin(5, 4), lomax_smin(4, 4)),
                               (lomax_smin(4, 4), lomax_ssecond(4, 4))]:
                    h, w, u = test(order2, SA, SB)
                    res.append((order2, h, w))
            ok = all(r[1] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(f"{r[0]}:{'ok' if r[1] else 'fail '+str(r[2])}"
                          for r in res),
                note="Archimedean survival copula case tested with Lomax "
                     "generator theta=4 + GH stdf.")

        else:
            add(recd, "unsupported order", note=f"no encoding for {c!r}")

    A.emit("eval_arxiv_2402.02945.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
