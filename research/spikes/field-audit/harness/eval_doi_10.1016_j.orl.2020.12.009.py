"""Evaluator for doi:10.1016/j.orl.2020.12.009 (PO systems, Archimedean copulas).

PO(Fbar, a) marginal:  S_a = a Fbar/(1-(1-a)Fbar),  F_a = F/(a+(1-a)F).
Series under survival copula generator phi (psi=phi^{-1}):
    S_{1:n} = phi( sum_i psi(S_{a_i}) ).
Parallel:  F_{n:n} = phi( sum_i psi(F_{a_i}) ).

Generators used (all from the paper or classical):
  IND   phi=e^{-t}, psi=-log            (log-linear, superadditive identity)
  CLAY  phi=(1+t)^{-1}, psi=u^{-1}-1    (Clayton theta=1; phi(1-phi)/phi'=-t
                                        which is decreasing and linear, so the
                                        Theorem 3.3/4.2 conditions hold)
  GB    phi=e^{(1-e^t)/th}, psi=log(1-th log u)   (Gumbel-Barnett)
  TI    phi=(2/(1+e^t))^{1/a}, psi=log(2 u^{-a} - 1)
  LT    phi=log(e+t)^{-1/a}, psi=e^{u^{-a}}-e
  LA    phi=th/log(t+e^th), psi=e^{th/u}-e^th

Independence satisfies the conditions of Theorems 3.1,3.2,4.1,5.1,5.2
(phi log-convex/log-concave: linear boundary; composition superadditive:
identity).  Theorem 3.3/4.2 need phi(1-phi)/phi' decreasing convex/concave:
Clayton theta=1 gives -t (linear).
"""
import json
import auditlib as A
import sympy as sp

x = A.x
e = A.e


def po_S(Fbar, a):
    return A.R(a) * Fbar / (1 - (1 - A.R(a)) * Fbar)


def po_F(F, a):
    return F / (A.R(a) + (1 - A.R(a)) * F)


# generator pairs (phi(t), psi(u)) as lambdas on sympy expressions
def gen_ind():
    return (lambda t: e ** (-t), lambda u: -sp.log(u))


def gen_clay1():
    return gen_clay(1)


def gen_clay(th):
    """Clayton phi=(1+th t)^{-1/th}; psi(u)=(u^{-th}-1)/th."""
    return (lambda t: (1 + A.R(th) * t) ** (-1 / A.R(th)),
            lambda u: (u ** (-A.R(th)) - 1) / A.R(th))


def gen_gb(th):
    return (lambda t: e ** ((1 - e ** t) / A.R(th)),
            lambda u: sp.log(1 - A.R(th) * sp.log(u)))


def gen_ti(a):
    return (lambda t: (2 / (1 + e ** t)) ** (1 / A.R(a)),
            lambda u: sp.log(2 * u ** (-A.R(a)) - 1))


def gen_lt(a):
    return (lambda t: sp.log(e + t) ** (-1 / A.R(a)),
            lambda u: e ** (u ** (-A.R(a))) - e)


def gen_la(th):
    return (lambda t: A.R(th) / sp.log(t + e ** A.R(th)),
            lambda u: e ** (A.R(th) / u) - e ** A.R(th))


def series_surv(Fbar, alphas, gen):
    phi, psi = gen
    return phi(sum(psi(po_S(Fbar, a)) for a in alphas))


def parallel_cdf(F, alphas, gen):
    phi, psi = gen
    return phi(sum(psi(po_F(F, a)) for a in alphas))


def parallel_surv(Fbar, alphas, gen):
    return 1 - parallel_cdf(1 - Fbar, alphas, gen)


def shocked_series(Fbar, alphas, gen, p):
    return A.R(sp.prod([A.R(pi) for pi in p])) * series_surv(Fbar, alphas, gen)


def run(order, SX_expr, SY_expr, lo=0, hi=sp.oo):
    X = A.C(SX_expr, lo, hi)
    Y = A.C(SY_expr, lo, hi)
    return A.check_dist(order, X, Y)


def both(order, SX, SY):
    return run(order, SX, SY), run(order, SY, SX)


def main():
    claims = json.load(open("../canonical/doi_10.1016_j.orl.2020.12.009.json"))
    out = []
    ind = gen_ind()
    clay = gen_clay1()

    def add(recd, status, instances=0, witness=None, undecided=0, note=None):
        out.append(A.rec(recd, status, instances=instances, witness=witness,
                         undecided=undecided, note=note))

    def batch(recd, order, insts):
        """insts: list of (SX_expr, SY_expr). holds iff all hold."""
        n = und = 0
        wit = None
        for SX, SY in insts:
            h, w, u = run(order, SX, SY)
            n += 1
            und += u
            if not h and wit is None:
                wit = w
        add(recd, "holds" if wit is None else "refuted", n,
            str(wit) if wit is not None else None, und)

    for recd in claims:
        c = recd["claim"]
        order = recd["conclusion"]["order"]
        if order not in ("st", "hr", "rh", "lr"):
            add(recd, "unsupported order")
            continue

        if c == "Counterexample 3.1":
            # no st order: series, Fbar=e^{-x^1.5}, a=(2,3,5.5) ~^p b=(2.5,3.5,3.8)
            Fbar = e ** (-x ** A.R(3, 2))
            SX = series_surv(Fbar, [2, 3, A.R(11, 2)], gen_ti(A.R(9, 10)))
            SY = series_surv(Fbar, [A.R(5, 2), A.R(7, 2), A.R(19, 5)],
                             gen_gb(A.R(3, 10)))
            (h1, w1, u1), (h2, w2, u2) = both("st", SX, SY)
            ok = (not h1) and (not h2)
            add(recd, "holds" if ok else "refuted", 1,
                f"X<=st Y fails x={w1}; Y<=st X fails x={w2}")

        elif c.startswith("Counterexample 3.2"):
            Fbar = e ** (-(A.R(1, 2) * x) ** 2)
            a = [A.R(1, 5), A.R(2, 5), A.R(3, 5)]
            b = [A.R(35, 100), A.R(55, 100), A.R(95, 100)]
            results = []
            if "case (a)" in c:
                gens = [gen_lt(A.R(1, 10))]
            elif "case (b)" in c or "phi(1-phi)/phi'" in c:
                gens = [gen_ti(A.R(1, 5))]
            else:
                gens = [gen_lt(A.R(1, 10)), gen_ti(A.R(1, 5))]
            for g in gens:
                SX = series_surv(Fbar, a, g)
                SY = series_surv(Fbar, b, g)
                (h1, w1, u1), (h2, w2, u2) = both("hr", SX, SY)
                results.append((not h1, not h2, w1, w2))
            ok = all(r[0] or r[1] for r in results)  # ordering fails (some dir)
            add(recd, "holds" if ok else "refuted", len(gens),
                "; ".join(f"fwd fail x={r[2]}, rev fail x={r[3]}"
                          for r in results))

        elif c.startswith("Counterexample 4.1"):
            F = 1 - e ** (-x ** A.R(1, 2))
            a = [A.R(9, 10), A.R(29, 20), A.R(43, 20)]
            b = [A.R(6, 5), A.R(39, 20), A.R(53, 20)]
            if "case (a)" in c:
                gens = [(gen_la(A.R(9, 10)), gen_gb(A.R(8)))]
            elif "case (b)" in c or "superadditive" in c:
                gens = [(gen_gb(A.R(9, 10)), gen_ti(A.R(1, 5)))]
            else:
                gens = [(gen_la(A.R(9, 10)), gen_gb(A.R(8))),
                        (gen_gb(A.R(9, 10)), gen_ti(A.R(1, 5)))]
            results = []
            for g1, g2 in gens:
                SX = parallel_surv(1 - F, a, g1)
                SY = parallel_surv(1 - F, b, g2)
                (h1, w1, u1), (h2, w2, u2) = both("st", SX, SY)
                results.append((not h1, not h2, w1, w2))
            ok = all(r[0] and r[1] for r in results)
            add(recd, "holds" if ok else "refuted", len(gens),
                "; ".join(f"fwd fail x={r[2]}, rev fail x={r[3]}"
                          for r in results))

        elif c.startswith("Counterexample 4.2"):
            F = 1 - e ** (-x ** 3)
            a = [A.R(1, 5), A.R(3, 5), A.R(3, 2), A.R(7, 2)]
            b = [A.R(4, 5), A.R(9, 10), A.R(9, 2), A.R(11, 2)]
            if "case (a)" in c:
                gens = [gen_clay(A.R(1, 5))]   # phi=(1/(ax+1))^{1/a}, a=0.2
            elif "case (b)" in c or "phi(1-phi)/phi'" in c:
                gens = [gen_ti(A.R(1, 5))]     # phi=(2/(1+e^x))^{1/a}, a=0.2
            else:
                gens = [gen_clay(A.R(1, 5)), gen_ti(A.R(1, 5))]
            results = []
            for g in gens:
                SX = parallel_surv(1 - F, a, g)
                SY = parallel_surv(1 - F, b, g)
                (h1, w1, u1), (h2, w2, u2) = both("rh", SX, SY)
                results.append((not h1, not h2, w1, w2))
            ok = all(r[0] or r[1] for r in results)
            add(recd, "holds" if ok else "refuted", len(gens),
                "; ".join(f"fwd fail x={r[2]}, rev fail x={r[3]}"
                          for r in results))

        elif c == "Corollary 3.1":  # same copula log-convex, p-larger -> st series
            Fbar = e ** (-x)
            insts = [(series_surv(Fbar, [1, 2, 6], ind),
                      series_surv(Fbar, [2, 3, 4], ind)),
                     (series_surv(Fbar, [A.R(1, 2), 2, 8], ind),
                      series_surv(Fbar, [1, 2, 4], ind))]
            assert A.p_larger([1, 2, 6], [2, 3, 4])
            batch(recd, "st", insts)

        elif c == "Corollary 3.2":  # same copula, weak supermaj -> st series
            Fbar = e ** (-x)
            insts = [(series_surv(Fbar, [1, 2, 6], ind),
                      series_surv(Fbar, [2, 3, 4], ind)),
                     (series_surv(Fbar, [1, 2, 6], clay),
                      series_surv(Fbar, [2, 3, 4], clay))]
            assert A.weak_super([1, 2, 6], [2, 3, 4])
            batch(recd, "st", insts)

        elif c == "Corollary 3.3":  # hr series vs homogeneous alpha>=AM
            Fbar = e ** (-x)
            insts = [(series_surv(Fbar, [1, 2, 6], clay),
                      series_surv(Fbar, [3, 3, 3], clay)),
                     (series_surv(Fbar, [1, 3, 8], clay),
                      series_surv(Fbar, [4, 4, 4], clay))]
            batch(recd, "hr", insts)

        elif c == "Corollary 4.1":  # st parallel, log-concave phi, weak supermaj
            Fbar = e ** (-x)
            insts = [(parallel_surv(Fbar, [1, 2, 6], ind),
                      parallel_surv(Fbar, [2, 3, 4], ind)),
                     (parallel_surv(Fbar, [1, 2, 6], clay),
                      parallel_surv(Fbar, [2, 3, 4], clay))]
            batch(recd, "st", insts)

        elif c == "Corollary 5.1":  # shocked series st, p-larger + prod p<=prod q
            Fbar = e ** (-x)
            insts = [(shocked_series(Fbar, [1, 2, 6], ind, [A.R(1, 2)] * 3),
                      shocked_series(Fbar, [2, 3, 4], ind, [A.R(3, 4)] * 3))]
            batch(recd, "st", insts)

        elif c == "Corollary 5.2":  # shocked series st, weak supermaj + shocks
            Fbar = e ** (-x)
            insts = [(shocked_series(Fbar, [1, 2, 6], ind, [A.R(1, 2)] * 3),
                      shocked_series(Fbar, [2, 3, 4], ind, [A.R(3, 4)] * 3)),
                     (shocked_series(Fbar, [1, 2, 6], clay, [A.R(1, 2)] * 3),
                      shocked_series(Fbar, [2, 3, 4], clay, [A.R(3, 4)] * 3))]
            batch(recd, "st", insts)

        elif c == "Theorem 3.1":  # st series, p-larger, log-convex+superadditive
            Fbar = e ** (-x)
            insts = [(series_surv(Fbar, [1, 2, 6], ind),
                      series_surv(Fbar, [2, 3, 4], ind)),
                     (series_surv(Fbar, [1, 2, 4], ind),
                      series_surv(Fbar, [2, 2, 3], ind))]
            batch(recd, "st", insts)

        elif c == "Theorem 3.2":  # st series, weak supermaj + superadditive
            Fbar = e ** (-x)
            insts = [(series_surv(Fbar, [1, 2, 6], ind),
                      series_surv(Fbar, [2, 3, 4], ind)),
                     (series_surv(Fbar, [1, 2, 6], clay),
                      series_surv(Fbar, [2, 3, 4], clay))]
            batch(recd, "st", insts)

        elif c == "Theorem 3.3":  # hr series, same copula, weak supermaj
            Fbar = e ** (-x)
            insts = [(series_surv(Fbar, [1, 2, 6], clay),
                      series_surv(Fbar, [2, 3, 4], clay)),
                     (series_surv(Fbar, [1, 3, 5], clay),
                      series_surv(Fbar, [2, 3, 4], clay))]
            batch(recd, "hr", insts)

        elif c == "Theorem 4.1":  # st parallel, weak supermaj + superadditive
            Fbar = e ** (-x)
            insts = [(parallel_surv(Fbar, [1, 2, 6], ind),
                      parallel_surv(Fbar, [2, 3, 4], ind)),
                     (parallel_surv(Fbar, [1, 2, 6], clay),
                      parallel_surv(Fbar, [2, 3, 4], clay))]
            batch(recd, "st", insts)

        elif c == "Theorem 4.2":  # rh parallel, same copula, weak supermaj
            Fbar = e ** (-x)
            insts = [(parallel_surv(Fbar, [1, 2, 6], clay),
                      parallel_surv(Fbar, [2, 3, 4], clay)),
                     (parallel_surv(Fbar, [1, 3, 5], clay),
                      parallel_surv(Fbar, [2, 3, 4], clay))]
            batch(recd, "rh", insts)

        elif c == "Theorem 5.1":  # shocked series st
            Fbar = e ** (-x)
            insts = [(shocked_series(Fbar, [1, 2, 6], ind, [A.R(1, 2)] * 3),
                      shocked_series(Fbar, [2, 3, 4], ind, [A.R(3, 4)] * 3))]
            batch(recd, "st", insts)

        elif c == "Theorem 5.2":
            Fbar = e ** (-x)
            insts = [(shocked_series(Fbar, [1, 2, 6], ind, [A.R(1, 3)] * 3),
                      shocked_series(Fbar, [2, 3, 4], ind, [A.R(1, 2)] * 3))]
            batch(recd, "st", insts)

        elif c == "Theorem 5.3":  # shocked series hr
            Fbar = e ** (-x)
            insts = [(shocked_series(Fbar, [1, 2, 6], clay, [A.R(1, 3)] * 3),
                      shocked_series(Fbar, [2, 3, 4], clay, [A.R(1, 2)] * 3))]
            batch(recd, "hr", insts)

        else:
            add(recd, "unsupported order", note=f"no encoding for {c!r}")

    A.emit("eval_doi_10.1016_j.orl.2020.12.009.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
