"""Evaluate canonical claims of doi_10.1186/s13660-024-03201-6 (Archimedean OS).

X_i ~ F(.;lambda_i), joint law: Archimedean copula C(u) = phi(sum psi(u_i))
with psi the generator (decreasing, (0,1]->[0,inf)) and phi = psi^{-1}.
    cdf(X_{n:n})  = phi( sum_i psi(F_i(x)) )   =>  S_max = 1 - that
    surv(X_{1:n}) = phi( sum_i psi(Fbar_i(x)) )   (same generator pair, used
    as survival copula -- reduces to the product copula under independence)

Copula instances (printed examples use them):
    indep:   psi=-log u, phi=e^{-t};  u psi'(u) = -1 const;
    gumbel2: psi=(-ln u)^2, phi=e^{-sqrt(t)};  u psi'(u) = -4 ln u increasing;
    clayton1: psi=1/u-1, phi=1/(1+t);  u psi'(u) = -1/u increasing;
    amh(-.2): psi=log((1.2-0.2u)/u), phi=(1.2)/(e^t+0.2); u psi' decreasing.

Marginal families:
    rate-exp:   F = 1-e^{-lambda x}: increasing & log-concave in lambda;
    scale-exp:  F = 1-e^{-x/lambda}: decreasing & log-concave in lambda;
    rate-exp for min theorems:  Fbar = e^{-lambda x}: decreasing &
                (weakly) log-convex in lambda;
    pareto:     Fbar = (1+lambda x)^{-1}: decreasing & log-convex in lambda.
"""
import json, os
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.1186_s13660-024-03201-6.json")
OUT = os.path.join(HERE, "eval_doi_10.1186_s13660-024-03201-6.result.json")
R = sp.Rational

L = sp.Symbol("l", positive=True)


def phi_psi(name):
    if name == "indep":
        return (lambda u: -sp.log(u), lambda t: sp.exp(-t))
    if name == "gumbel2":
        return (lambda u: (-sp.log(u)) ** 2, lambda t: sp.exp(-sp.sqrt(t)))
    if name == "clayton1":
        return (lambda u: 1 / u - 1, lambda t: 1 / (1 + t))
    if name == "amh":
        th = R(-1, 5)
        return (lambda u: sp.log((1 - th + th * u) / u),
                lambda t: (1 - th) / (sp.exp(t) - th))
    raise ValueError(name)


def rate_cdf(lam):    # F = 1 - e^{-lam x}, increasing & log-concave in lam
    return 1 - sp.exp(-lam * x)


def inv_cdf(lam):     # F = e^{-lam^2/x}: decreasing & log-concave in lam
    return sp.exp(-lam**2 / x)


def inv_cdf_cvx(lam): # F = e^{-sqrt(lam)/x}: decreasing & log-convex in lam
    return sp.exp(-sp.sqrt(lam) / x)


def rate_sf(lam):     # Fbar = e^{-lam x}, decreasing & log-linear in lam
    return sp.exp(-lam * x)


def pareto_sf(lam):   # Fbar = (1+lam x)^{-1}, decreasing & log-convex in lam
    return (1 + lam * x) ** (-1)


def scale_sf_c(lam):  # Fbar = e^{-x/lam^2}: increasing & log-concave in lam
    return sp.exp(-x / lam**2)


def max_sf(ls, Fi, cop):
    psi, phi = phi_psi(cop)
    V = sp.Integer(0)
    for l in ls:
        V += psi(Fi(l))
    return 1 - phi(V)


def min_sf(ls, SFi, cop):
    psi, phi = phi_psi(cop)
    V = sp.Integer(0)
    for l in ls:
        V += psi(SFi(l))
    return phi(V)


def instances(claim):
    """-> list of (S_left, S_right) in printed order left <=order right,
    or 'both' list for counterexamples (test both directions)."""
    if claim in ("Theorem 3.1", "Example 3.2", "Example 3.5"):
        # Xn:n <=st Yn:n: F incr+log-concave (rate-exp), u psi' increasing
        # (gumbel2 printed for Ex3.2, clayton1 for Ex3.5), l <^m l*
        data = [([R(2),R(3),R(4)], [R(1),R(3),R(5)], "gumbel2"),   # printed Ex3.2
                ([R(2),R(3),R(4)], [R(1),R(3),R(5)], "clayton1"),
                ([R(2),R(4),R(5)], [R(1),R(3),R(7)], "clayton1"),  # printed Ex3.5
                ([R(2),R(4),R(5)], [R(1),R(3),R(7)], "indep")]
        return [("st", max_sf(a, rate_cdf, cop), max_sf(b, rate_cdf, cop))
                for (a, b, cop) in data]
    if claim == "Counterexample 3.3":
        # same but F log-convex in lambda; claim: NO st ordering.
        data = [([R(2),R(3),R(4)], [R(1),R(3),R(5)], "gumbel2", 2)]
        return [("none", max_sf(a, inv_cdf_cvx, cop),
                 max_sf(b, inv_cdf_cvx, cop)) for (a, b, cop, _) in data]
    if claim in ("Proposition 3.4", "Counterexample 3.6"):
        # F decreasing+log-concave in lam (scale-exp); u psi' decreasing (amh<0)
        data = [([R(1),R(2),R(4)], [R(2),R(3),R(5)], "amh"),   # printed Ex3.8-ish
                ([R(1),R(2),R(4)], [R(2),R(3),R(5)], "indep"),
                ([R(1),R(3),R(5)], [R(2),R(4),R(6)], "amh")]
        tag = "st" if claim == "Proposition 3.4" else "none"
        return [(tag, max_sf(a, inv_cdf, cop), max_sf(b, inv_cdf, cop))
                for (a, b, cop) in data]
    if claim in ("Theorem 3.7", "Example 3.8", "Counterexample 3.9"):
        # F decreasing+log-concave; u psi' decreasing; l <_w l* (submaj)
        data = [([R(1),R(2),R(4)], [R(2),R(3),R(5)], "amh"),   # printed Ex3.8
                ([R(1),R(2),R(4)], [R(2),R(3),R(5)], "indep"),
                ([R(1),R(2),R(3)], [R(1),R(2),R(4)], "amh")]
        tag = "st" if claim != "Counterexample 3.9" else "none"
        if claim == "Counterexample 3.9":
            data = [([R(1),R(2),R(4)], [R(2),R(3),R(5)], "amh"),
                    ([R(1),R(2),R(4)], [R(2),R(3),R(5)], "indep")]
            # F log-convex in lambda variant -> pareto-type cdf family
            return [(tag, max_sf(a, inv_cdf_cvx, cop), max_sf(b, inv_cdf_cvx, cop))
                    for (a, b, cop) in data]
        return [(tag, max_sf(a, inv_cdf, cop), max_sf(b, inv_cdf, cop))
                for (a, b, cop) in data]
    if claim in ("Theorem 4.1", "Example 4.2", "Counterexample 4.3"):
        # X1:n <=st Y1:n; Fbar decreasing & log-convex in lam (rate-exp/Pareto);
        # u psi' decreasing (amh); l <^m l*
        data = [([R(2),R(3),R(4)], [R(1),R(3),R(5)], "amh"),
                ([R(2),R(3),R(4)], [R(1),R(3),R(5)], "indep"),
                ([R(2),R(4),R(5)], [R(1),R(3),R(7)], "amh")]
        if claim == "Counterexample 4.3":
            return [("none", min_sf(a, pareto_sf, cop), min_sf(b, pareto_sf, cop))
                    for (a, b, cop) in data]
        return [("st", min_sf(a, rate_sf, cop), min_sf(b, rate_sf, cop))
                for (a, b, cop) in data]
    if claim in ("Theorem 4.4", "Example 4.5", "Counterexample 4.6"):
        # claim Y1:n <=st X1:n ; Fbar-side family incr+log-concave in lam
        # (scale-exp survival e^{-x/l} is increasing & log-concave in l);
        # u psi' increasing; l <^m l*.  Return (SY, SX).
        data = [([R(3),R(4),R(5)], [R(2),R(4),R(6)], "gumbel2"),  # printed Ex4.5
                ([R(3),R(4),R(5)], [R(2),R(4),R(6)], "clayton1"),
                ([R(3),R(4),R(5)], [R(2),R(4),R(6)], "indep")]
        if claim == "Counterexample 4.6":
            return [("none", min_sf(b, pareto_sf, cop), min_sf(a, pareto_sf, cop))
                    for (a, b, cop) in data]
        return [("st", min_sf(b, scale_sf_c, cop), min_sf(a, scale_sf_c, cop))
                for (a, b, cop) in data]
    return []





def go():
    recs = json.load(open(CANON))
    out = []
    for r in recs:
        c = r.get("conclusion") or {}
        order = c.get("order")
        claim = r["claim"]
        if order not in ("st", "hr", "rh", "lr"):
            out.append(dict(claim=claim, order=order, status="unsupported order",
                            instances=0, witness=None, undecided_points=0))
            continue
        pairs = instances(claim)
        inst = 0; wit = None; und = 0; allhold = True
        for (tag, SA, SB) in pairs:
            if tag == "none":
                # claim asserts NO ordering: both directions must fail
                ok1, w1, u1 = cf.check(order, Closed(SA), Closed(SB))
                ok2, w2, u2 = cf.check(order, Closed(SB), Closed(SA))
                inst += 1; und += u1 + u2
                if ok1 or ok2:
                    allhold = None
                else:
                    wit = wit or str(w1)
                continue
            ok, w, u = cf.check(order, Closed(SA), Closed(SB))
            inst += 1; und += u
            if not ok:
                allhold = False; wit = str(w)
        status = "holds" if allhold else "refuted"
        if allhold is None:
            status = "out of harness scope"
        out.append(dict(claim=claim, order=order, status=status,
                        instances=inst, witness=wit, undecided_points=und))
    json.dump(out, open(OUT, "w"), indent=1)
    for o in out:
        print(o["claim"], "|", o["order"], "|", o["status"], "| inst", o["instances"],
              "| wit", o["witness"])


if __name__ == "__main__":
    go()
