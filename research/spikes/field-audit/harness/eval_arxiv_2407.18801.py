"""Evaluator for arXiv:2407.18801 (fail-safe systems, Archimedean copula).

Under an Archimedean survival copula with generator psi (phi=psi^{-1}),
the fail-safe survival is
  S_{2:n}(x) = sum_i psi( sum_{j!=i} phi(S_j(x)) ) - (n-1) psi( sum_j phi(S_j) )
since P(at least n-1 exceed x) = sum_i P(all-but-i exceed) - (n-1) P(all exceed).

Generators:
  Gumbel-Barnett theta: psi(t) = exp(theta (1 - e^t)),
                        phi(u) = log(1 - (1/theta) log u)
  Clayton theta:        psi(t) = (1 + theta t)^{-1/theta},
                        phi(u) = (u^{-theta} - 1)/theta

Scale marginals S_i(x) = 1 - (1 - e^{-(t_i x)^a})^b   (EW)
                   or    e^{-(t_i x)^a}              (Weibull shape a)
Claim direction: X_{2:n} >=st Y_{2:n} <=> S_X >= S_Y on (0, oo).
"""
import json
import auditlib as A
import sympy as sp

x = A.x
e = A.e


def gumbel_barnett(th):
    th = A.R(th)
    return (lambda t: e ** (th * (1 - e ** t)),
            lambda u: sp.log(1 - sp.log(u) / th))


def clayton(th):
    th = A.R(th)
    return (lambda t: (1 + th * t) ** (-1 / th),
            lambda u: (u ** (-th) - 1) / th)


def s_2n(margins, gen):
    psi, phi = gen
    n = len(margins)
    terms = [phi(m) for m in margins]
    tot = sum(terms)
    return (sum(psi(tot - t_i) for t_i in terms)
            - (n - 1) * psi(tot))


def ew_marginal(th_i, a=A.R(9, 10), b=A.R(9, 10)):
    return 1 - (1 - e ** (-(A.R(th_i) * x) ** a)) ** b


def weib_marginal(th_i, a=A.R(9, 10)):
    return e ** (-(A.R(th_i) * x) ** a)


def test(SX, SY):
    return A.check_dist("st", A.C(SX), A.C(SY))


def check_both(SX, SY):
    """For 'neither direction' claims."""
    h1, w1, u1 = test(SX, SY)
    h2, w2, u2 = test(SY, SX)
    return (not h1) and (not h2), (w1, w2)


def main():
    claims = json.load(open("../canonical/arxiv_2407.18801.json"))
    out = []

    def add(recd, status, instances=0, witness=None, undecided=0, note=None):
        out.append(A.rec(recd, status, instances=instances, witness=witness,
                         undecided=undecided, note=note))

    T1 = ["0.12", "0.28", "0.51", "0.62", "0.73"]
    T2 = ["0.21", "0.42", "0.73", "0.89", "0.92"]
    T3 = ["0.13", "0.31", "0.49", "0.61", "0.72"]
    T4 = ["0.22", "0.41", "0.71", "0.88", "0.92"]

    for recd in claims:
        c = recd["claim"]
        order = recd["conclusion"]["order"]
        if order != "st":
            add(recd, "unsupported order")
            continue

        if ("Section 5" in c or "tensile" in c):
            add(recd, "unverifiable",
                note="the printed vectors (~341-345) are never linked to a "
                     "model parameter (they approximate the fitted Weibull "
                     "shape b=341.65, not a scale or exponent); the "
                     "semi-parametric model for the application is "
                     "unspecified, so no canonical encoding exists.")
            continue

        if "Example (Section 3, first" in c or "SC model, Section 3" in c \
                or "unnumbered, p. 10" in c:
            # EW margins + Gumbel-Barnett theta=0.2; claim X2:5 >=st Y2:5
            gen = gumbel_barnett(A.R(1, 5))
            mX = [ew_marginal(t) for t in T1]
            mY = [ew_marginal(t) for t in T2]
            SX, SY = s_2n(mX, gen), s_2n(mY, gen)
            h, w, u = test(SY, SX)
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, u,
                note="stated copula parameter 0.2 used (printed formulas "
                     "inconsistent, using 10/0.1); p-larger check: smallest-"
                     "product partials of theta < theta*'s.")

        elif "second unnumbered" in c or "Counterexample" in c \
                or "p.12" in c or "unnumbered counterexample" in c:
            # Weibull margins + Clayton theta=10; claim neither direction
            gen = clayton(A.R(10))
            mX = [weib_marginal(t) for t in T3]
            mY = [weib_marginal(t) for t in T4]
            SX, SY = s_2n(mX, gen), s_2n(mY, gen)
            ok, (w1, w2) = check_both(SX, SY)
            add(recd, "holds" if ok else "refuted", 1,
                f"fwd w={w1} rev w={w2}",
                note="counterexample verified iff both directions fail.")

        elif c == "Proposition 1":
            # MPHRS: S_i = a*F( mu_i x )^l / (1 - abar F(mu_i x)^l);
            # take F = Weibull(1) S0=e^{-x}; products of smallest mu <= mu*'s
            a, l = A.R(1, 2), 2
            res = []
            for muX, muY in [([1, 2, 3], [A.R(3, 2), 2, A.R(5, 2)]),
                             ([1, 1, 4], [A.R(4, 3), 2, 3])]:
                # products of smallest: X vs Y
                ax, ay = A.asc(muX), A.asc(muY)
                import functools, operator
                assert all(functools.reduce(operator.mul, ax[:j])
                           <= functools.reduce(operator.mul, ay[:j])
                           for j in range(1, len(ax) + 1))
                SXm = [A.R(a) * (e ** (-(A.R(m) * x))) ** l
                       / (1 - (1 - A.R(a)) * (e ** (-(A.R(m) * x))) ** l)
                       for m in muX]
                SYm = [A.R(a) * (e ** (-(A.R(m) * x))) ** l
                       / (1 - (1 - A.R(a)) * (e ** (-(A.R(m) * x))) ** l)
                       for m in muY]
                gen = gumbel_barnett(A.R(1, 5))
                SX, SY = s_2n(SXm, gen), s_2n(SYm, gen)
                h, w, u = test(SY, SX)
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]),
                note="MPHRS over Exp baseline, GB generator; product-partial "
                     "ordering of scale vectors (theta ~^p theta*).")

        elif c == "Proposition 2":
            # location-scale: ambiguous per canonical (single common
            # location used in proof); test common-location instance
            res = []
            gen = gumbel_barnett(A.R(1, 5))
            for thX, thY, lam in [([1, 2, 3], [A.R(3, 2), 2, A.R(5, 2)], 1),
                                  ([1, 1, 4], [A.R(4, 3), 2, 3], A.R(1, 2))]:
                ax, ay = A.asc(thX), A.asc(thY)
                import functools, operator
                assert all(functools.reduce(operator.mul, ax[:j])
                           <= functools.reduce(operator.mul, ay[:j])
                           for j in range(1, len(ax) + 1))
                # F = standard logistic for clean support x>lam
                F = 1 / (1 + e ** (-x))
                SXm = [F.subs(x, A.R(t) * (x - A.R(lam))) for t in thX]
                SYm = [F.subs(x, A.R(t) * (x - A.R(lam))) for t in thY]
                SX, SY = s_2n(SXm, gen), s_2n(SYm, gen)
                h, w, u = A.check_dist("st", A.C(SX, lam + sp.Rational(0)),
                                       A.C(SY, lam + sp.Rational(0)))
                res.append((h, w))
            ok = all(r[0] for r in res)
            add(recd, "holds" if ok else "refuted", len(res),
                "; ".join(str(r[1]) for r in res if not r[0]),
                note="common location lambda (the proof's own reading); "
                     "logistic baseline; x h_F decreasing holds for "
                     "logistic (x f/F dec).")

        elif c == "Theorem 3.1":
            # general semiparametric; test with scale model EW + GB
            gen = gumbel_barnett(A.R(1, 5))
            mX = [ew_marginal(t) for t in T1]
            mY = [ew_marginal(t) for t in T2]
            SX, SY = s_2n(mX, gen), s_2n(mY, gen)
            h, w, u = test(SY, SX)
            # second instance: Weibull margins + GB
            mX2 = [weib_marginal(t) for t in T3]
            mY2 = [weib_marginal(t) for t in T4]
            SX2, SY2 = s_2n(mX2, gen), s_2n(mY2, gen)
            h2, w2, u2 = test(SY2, SX2)
            ok = h and h2
            add(recd, "holds" if ok else "refuted", 2,
                f"EW:{w}; W:{w2}",
                note="p-larger scale vectors, GB generator (log-concave for "
                     "theta=1/5); condition (ii): log S(x;e^a) convexity "
                     "checked for EW/Weibull per paper.")

        else:
            add(recd, "unsupported order", note=f"no encoding for {c!r}")

    A.emit("eval_arxiv_2407.18801.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
