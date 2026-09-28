"""Evaluator for arXiv:1704.06329 (ENH systems, independent maxima/minima).

ENH(alpha, lam, beta): F(x) = [1 - e^{1-(1+lam x)^alpha}]^beta, x>=0.
Independent components; X_{n:n} cdf = prod F_i; X_{1:n} survival = prod S_i.
Dependent-sample records (Archimedean copula claims) are out of harness scope.
"""
import json
import auditlib as A
import sympy as sp

x = A.x
e = A.e


def enh_cdf(alpha, lam, beta):
    return (1 - e ** (1 - (1 + A.R(lam) * x) ** A.R(alpha))) ** A.R(beta)


def max_surv(params):
    return 1 - sp.prod([enh_cdf(*p) for p in params])


def min_surv(params):
    return sp.prod([1 - enh_cdf(*p) for p in params])


def run(order, PX, PY, stat="max"):
    SX = max_surv(PX) if stat == "max" else min_surv(PX)
    SY = max_surv(PY) if stat == "max" else min_surv(PY)
    return A.check_dist(order, A.C(SX), A.C(SY))


def main():
    claims = json.load(open("../canonical/arxiv_1704.06329.json"))
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

        if c in ("Corollary 3.11", "Corollary 3.12", "Theorem 3.10"):
            add(recd, "out of harness scope",
                note="dependent samples under Archimedean copulas; joint law "
                     "cannot be reduced to a univariate survival test here.")

        elif c == "Theorem 3.2":  # shape vectors, weak supermaj, max st
            insts = [([(2, 1, 1), (3, 1, 1)], [(A.R(5, 2), 1, 1)] * 2),
                     # X alpha=(2,3) weakly supermaj by alpha*=(2.5,2.5)
                     ([(1, 2, 2), (4, 2, 2)], [(2, 2, 2), (3, 2, 2)])]
            insts = []
            for a_vec, a_star in [([A.R(2), A.R(3)], [A.R(5, 2), A.R(5, 2)]),
                                  ([A.R(1), A.R(2), A.R(4)],
                                   [A.R(2), A.R(2), A.R(3)])]:
                assert A.weak_super(a_vec, a_star)
                insts.append(([(a, 1, 1) for a in a_vec],
                              [(a, 1, 1) for a in a_star]))
            n = und = 0
            wit = None
            for PX, PY in insts:
                # Xn:n >=st X*n:n <=> X* <=st X
                h, w, u = run("st", PY, PX)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            add(recd, "holds" if wit is None else "refuted", n,
                str(wit) if wit is not None else None, und)

        elif c == "Theorem 3.3":  # coordinatewise alpha
            insts = [([(1, 1, 2), (2, 1, 2)], [(2, 1, 2), (3, 1, 2)]),
                     ([(A.R(1, 2), 2, 1), (1, 2, 1)], [(1, 2, 1), (2, 2, 1)])]
            n = und = 0
            wit = None
            for PX, PY in insts:
                h, w, u = run("st", PY, PX)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            add(recd, "holds" if wit is None else "refuted", n,
                str(wit) if wit is not None else None, und)

        elif c == "Theorem 3.4":  # scale vectors, alpha<=1, weak supermaj
            insts = []
            for l_vec, l_star in [([A.R(1), A.R(2)], [A.R(3, 2), A.R(3, 2)]),
                                  ([A.R(1), A.R(2), A.R(4)],
                                   [A.R(2), A.R(2), A.R(3)])]:
                assert A.weak_super(l_vec, l_star)
                insts.append(([(A.R(1, 2), l, 1) for l in l_vec],
                              [(A.R(1, 2), l, 1) for l in l_star]))
            n = und = 0
            wit = None
            for PX, PY in insts:
                h, w, u = run("st", PY, PX)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            add(recd, "holds" if wit is None else "refuted", n,
                str(wit) if wit is not None else None, und,
                note="alpha=1/2 <= 1; common beta=1.")

        elif c == "Theorem 3.5":  # coordinatewise lambda
            insts = [([(A.R(1, 2), 1, 1), (A.R(1, 2), 2, 1)],
                      [(A.R(1, 2), 2, 1), (A.R(1, 2), 3, 1)]),
                     ([(1, 1, 2), (1, 2, 2)], [(1, 2, 2), (1, 4, 2)])]
            n = und = 0
            wit = None
            for PX, PY in insts:
                h, w, u = run("st", PY, PX)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            add(recd, "holds" if wit is None else "refuted", n,
                str(wit) if wit is not None else None, und)

        elif c == "Theorem 3.6":  # lr iff sum beta >= sum beta*
            res = []
            # iff: test both directions
            for bX, bY in [([2, 3], [1, 2]), ([1, 2, 2], [1, 1, 1])]:
                PX = [(2, 1, b) for b in bX]
                PY = [(2, 1, b) for b in bY]
                h, w, u = run("lr", PY, PX)  # X >=lr X* <=> X* <=lr X
                res.append(("fwd", h, w))
            for bX, bY in [([1, 2], [2, 3]), ([1, 1], [1, 2, 1])]:
                PX = [(2, 1, b) for b in bX]
                PY = [(2, 1, b) for b in bY]
                h, w, u = run("lr", PY, PX)  # sum smaller -> must fail
                res.append(("rev", not h, w))
            ok = all(r[1] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(f"{r[0]}: {'ok' if r[1] else 'FAIL at '+str(r[2])}"
                          for r in res),
                note="iff: tested sufficiency (larger beta-sum) and failure "
                     "for smaller beta-sum.")

        else:
            add(recd, "unsupported order", note=f"no encoding for {c!r}")

    A.emit("eval_arxiv_1704.06329.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
