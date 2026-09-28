"""Evaluate canonical claims of arxiv_2604.26026 (transformation model, copulas).

Margins X_i ~ T(alpha_i, F) coupled by Archimedean copulas; X-side generator
psi1 (inverse phi1), Y-side generator psi2 (inverse phi2):
    cdf(X_{n:n})  = phi2( sum_i psi2( F_i(x) ) )        [F_i = margin cdf]
    surv(X_{1:n}) = phi1( sum_i psi1( S_i(x) ) )        [S_i = margin surv]

Transformations:
    Te(beta,F) = 1-(1-F)^beta   (PHR; increasing in beta)  -> surv F^beta
    Tc(beta,F) = F^beta         (PRHR; decreasing in beta) -> cdf F^beta
    To(beta,F) = beta F^2/(beta F^2+(1-F)^2)  (odds-MO with theta=2;
                                               increasing in beta)

Copula pairs used (all satisfy the printed super-additivity/monotonicity
requirements):
    indep:   psi=-log u, phi=e^{-t}        (completely monotone -> d-monotone)
    clayton1: psi=u^{-1}-1, phi=(1+t)^{-1} (completely monotone)
    gumbel2: psi=(-ln u)^2, phi=e^{-sqrt(t)} (completely monotone)
    amh12:   psi=log((1.5-0.5u)/u), phi=0.5/(e^t-0.5)

'phi2 o psi1 super-additive' is satisfied by psi1=indep + psi2 in {clayton1,
gumbel2, amh} (Example 2.5) and by psi1=psi2 (identity composition).

k-out-of-n statistics are tested under psi=indep (admissible: indep is
completely monotone, hence d-monotone for every d), where the distribution
of X_{n-k:n} has the elementary-symmetric closed form.
"""
import json, os, itertools
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "arxiv_2604.26026.json")
OUT = os.path.join(HERE, "eval_arxiv_2604.26026.result.json")
R = sp.Rational


def genpair(name):
    if name == "indep":
        return (lambda u: -sp.log(u), lambda t: sp.exp(-t))
    if name == "clayton1":
        return (lambda u: u**-1 - 1, lambda t: (1 + t) ** (-1))
    if name == "gumbel2":
        return (lambda u: (sp.log(u)) ** 2, lambda t: sp.exp(-sp.sqrt(t)))
    if name == "amh12":
        return (lambda u: sp.log((R(3, 2) - R(1, 2) * u) / u),
                lambda t: R(1, 2) / (sp.exp(t) - R(1, 2)))
    raise ValueError(name)


def comp(x_, vs, cop):   # phi( sum psi(v_i) )
    psi, phi = genpair(cop)
    t = sp.Integer(0)
    for v in vs:
        t += psi(v)
    return phi(t)


FB = (1 + x) ** (-1)      # baseline survival (Pareto-1)


def margin_surv(a, T):
    if T == "te":
        return FB ** a                      # 1 - Te = F^a
    if T == "tc":
        return 1 - (1 - FB) ** a            # 1 - Tc = 1 - F^a
    if T == "to":
        F = 1 - FB
        g = a * F ** 2 / (a * F ** 2 + FB ** 2)
        return 1 - g
    raise ValueError(T)


def margin_cdf(a, T):
    return 1 - margin_surv(a, T)


def max_sf(aa, T, cop):
    return 1 - comp(x, [margin_cdf(a, T) for a in aa], cop)


def min_sf(aa, T, cop):
    return comp(x, [margin_surv(a, T) for a in aa], cop)


def os_sf(aa, T, cop, ksmall):
    """Survival of k-th smallest under independence."""
    if cop != "indep":
        raise ValueError("os only under independence")
    ss = [margin_surv(a, T) for a in aa]
    n = len(ss); m = n - ksmall + 1   # need at least n-ksmall+1 exceeding
    tot = sp.Integer(0)
    for j in range(m, n + 1):
        e = sp.Integer(0)
        for S in itertools.combinations(range(n), j):
            p = sp.Integer(1)
            for i in S:
                p *= ss[i]
            e += p
        tot += (-1) ** (j - m) * sp.binomial(j - 1, m - 1) * e
    return tot


COP2 = ["indep", "clayton1", "gumbel2"]
COP12 = [("indep", "clayton1"), ("indep", "gumbel2"), ("clayton1", "indep")]


def pairs(claim):
    """-> list of (tag, S_left, S_right)."""
    key = claim.lower()
    out = []
    ab_le = [([R(1,2), R(4,5)], [R(7,10), R(1)]),
             ([R(1,2), R(4,5), R(1)], [R(7,10), R(9,10), R(3,2)])]
    ab_maj = [([R(3,10), R(1), R(17,10)], [R(6,10), R(1), R(4,5)]),   # a ~<m b
              ([R(2,5), R(9,10), R(1)], [R(3,5), R(8,10), R(4,5)])]
    maj_xy = [([R(3,10), R(1), R(17,10)], [R(6,10), R(1), R(4,5)])]  # a ~<m b

    def mx(aa, T):  return max_sf(aa, T, "gumbel2")
    def mn(aa, T):  return min_sf(aa, T, "clayton1")

    def mx_cop(aa, T, cop): return max_sf(aa, T, cop)
    def mn_cop(aa, T, cop): return min_sf(aa, T, cop)

    # ---------- generic Section-3 claims ----------
    if key.startswith("theorem 3.1(1)") or key.startswith("corollary 3.4"):
        # T increasing (te), alpha_i<=beta_i: Xn:n(a)>=st Yn:n(b): pair (SY,SX)
        for (aa, bb) in ab_le:
            out.append(("st", mx(bb, "te"), mx(aa, "te")))
            out.append(("st", mx_cop(bb, "te", "clayton1"), mx_cop(aa, "te", "clayton1")))
        return out
    if key.startswith("theorem 3.1(2)"):
        # T decreasing (tc), alpha<=beta: X <=st Y
        for (aa, bb) in ab_le:
            out.append(("st", mx(aa, "tc"), mx(bb, "tc")))
        return out
    if key.startswith("theorem 3.3") or key.startswith("example 3.5"):
        # alpha ~>^m beta (X alpha, Y beta); claim X >=st Y; T inc (te)
        for (bb, aa) in [([R(6,10), R(1), R(4,5)], [R(3,10), R(1), R(17,10)])]:
            for cop in ("clayton1", "gumbel2", "amh12"):
                out.append(("st", mx_cop(bb, "te", cop), mx_cop(aa, "te", cop)))
        return out
    if key.startswith("theorem 3.7(1)"):
        # T decreasing (tc): X1:n(a) <=st Y1:n(b), alpha<=beta
        for (aa, bb) in ab_le:
            out.append(("st", mn(aa, "tc"), mn(bb, "tc")))
        return out
    if key.startswith("theorem 3.7(2)"):
        for (aa, bb) in ab_le:
            out.append(("st", mn(bb, "te"), mn(aa, "te")))
        return out
    if key.startswith("theorem 3.8") or key.startswith("corollary 3.9"):
        # beta ~>^m alpha: X1:n(a) <=st Y1:n(b), te
        for (aa, bb) in [([R(6,10), R(1), R(4,5)], [R(3,10), R(1), R(17,10)])]:
            for cop in ("clayton1", "gumbel2", "amh12"):
                out.append(("st", mn_cop(aa, "te", cop), mn_cop(bb, "te", cop)))
        return out
    if key.startswith("corollary 3.6") or key.startswith("corollary 3.10"):
        # a=0.5,b=2,c=3,n=3: q=floor((c-na)/(b-a))=1, eta=c-qb-(n-q-1)a=0.5
        # alpha* = (a, eta, b) = (0.5, 0.5, 2) -- most-spread vertex of A;
        # alphabar = (c/n,...) = (1,1,1) -- least spread.
        a, b, c, n = R(1, 2), R(2), R(3), 3
        astar = [R(1,2), R(1,2), R(2)]; abar = [R(1)] * n
        amid = [R(3,5), R(6,5), R(6,5)]  # in [a,b]^3, sum 3
        sysc = (lambda aa_, T_: mx_cop(aa_, T_, "clayton1")) \
            if "corollary 3.6" in key else (lambda aa_, T_: mn_cop(aa_, T_, "clayton1"))
        sysg = (lambda aa_, T_: mx_cop(aa_, T_, "gumbel2")) \
            if "corollary 3.6" in key else (lambda aa_, T_: mn_cop(aa_, T_, "amh12"))
        for sysf in (sysc, sysg):
            if "corollary 3.6" in key:
                out.append(("st", sysf(amid, "te"), sysf(astar, "te")))
                out.append(("st", sysf(abar, "te"), sysf(amid, "te")))
            else:
                out.append(("st", sysf(astar, "te"), sysf(amid, "te")))
                out.append(("st", sysf(amid, "te"), sysf(abar, "te")))
        return out
    if key.startswith("theorem 3.16"):
        # n-k:n under independence; (1) T inc -> >=st ; (2) T dec -> <=st
        k = 1; aa = [R(1,2), R(4,5), R(1)]; bb = [R(7,10), R(9,10), R(3,2)]
        T = "te" if "(1)" in key else "tc"
        SA = os_sf(aa, T, "indep", 2); SB = os_sf(bb, T, "indep", 2)
        return [("st", SB, SA) if T == "te" else ("st", SA, SB)]
    if "example 3.17" in key:
        # claim: no ordering; use two alpha-vectors under Clayton
        a1 = [R(1), R(5,2), R(4)]; a2 = [R(2), R(2), R(3)]
        return [("none", max_sf(a1, "te", "clayton1"), max_sf(a2, "te", "clayton1"))]
    # ---------- Section 4 propositions ----------
    if key.startswith("proposition 4.1") and "4.1(" not in key and \
            not key.startswith(("proposition 4.10", "proposition 4.11",
                                "proposition 4.14", "proposition 4.15",
                                "proposition 4.16")):
        # te margins, a_i <= b_i: Xn:n(a) >=st Yn:n(b), phi2 o psi1 superadd
        for (c1, c2) in [("indep", "clayton1"), ("indep", "gumbel2")]:
            for (aa, bb) in ab_le:
                out.append(("st", mx_cop(bb, "te", c2), mx_cop(aa, "te", c1)))
        return out
    if key.startswith("proposition 4.10"):
        # To margins, alpha<=beta: X >=st Y
        for (aa, bb) in ab_le:
            out.append(("st", mx_cop(bb, "to", "clayton1"), mx_cop(aa, "to", "indep")))
        return out
    if key.startswith("proposition 4.11") or key.startswith("proposition 4.7"):
        # alpha ⪰m beta -> X >=st Y; te margins
        for (aa, bb) in maj_xy:   # aa more spread = alpha
            out.append(("st", mx_cop(bb, "te", "gumbel2"), mx_cop(aa, "te", "indep")))
        return out
    if key.startswith("proposition 4.2"):
        for (aa, bb) in maj_xy:
            out.append(("st", mx_cop(bb, "te", "gumbel2"), mx_cop(aa, "te", "indep")))
        return out
    if key.startswith("proposition 4.3"):
        # tc? te; X1:n(a) >=st Y1:n(b) with alpha<=beta; phi1 o psi2 superadd
        for (aa, bb) in ab_le:
            out.append(("st", mn_cop(bb, "te", "indep"), mn_cop(aa, "te", "clayton1")))
        return out
    if key.startswith("proposition 4.4"):
        # X1:n <=st Y1:n; beta ⪰m alpha; te
        for (aa, bb) in maj_xy:
            out.append(("st", mn_cop(aa, "te", "indep"), mn_cop(bb, "te", "clayton1")))
        return out
    if key.startswith("proposition 4.8"):
        # X1:n(a) <=st Y1:n(b); a<=b; te
        for (aa, bb) in ab_le:
            out.append(("st", mn_cop(aa, "te", "indep"), mn_cop(bb, "te", "gumbel2")))
        return out
    if key.startswith("proposition 4.14"):
        for (aa, bb) in ab_le:
            out.append(("st", mn_cop(bb, "to", "clayton1"), mn_cop(aa, "to", "indep")))
        return out
    if key.startswith("proposition 4.15"):
        for (aa, bb) in maj_xy:
            out.append(("st", mn_cop(aa, "to", "clayton1"), mn_cop(bb, "to", "indep")))
        return out
    if key.startswith("proposition 4.5") or key.startswith("proposition 4.9") or \
            key.startswith("proposition 4.16"):
        # Xn-k:n(a) vs Xn-k:n(b) with a_i<=b_i; independence copula
        aa = [R(1,2), R(4,5), R(1)]; bb = [R(7,10), R(9,10), R(3,2)]
        T = "te"
        SA = os_sf(aa, T, "indep", 2); SB = os_sf(bb, T, "indep", 2)
        if key.startswith("proposition 4.9"):
            SAt = os_sf(aa, "tc", "indep", 2); SBt = os_sf(bb, "tc", "indep", 2)
            return [("st", SAt, SBt)]
        return [("st", SB, SA)]
    if key.startswith("proposition 4.6"):
        # tc margins, a<=b: X <=st Y
        for (aa, bb) in ab_le:
            out.append(("st", mx_cop(aa, "tc", "indep"), mx_cop(bb, "tc", "gumbel2")))
        return out
    if key.startswith("theorem 3.7") or key.startswith("corollary 3.9"):
        return out
    return out


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
        dirn = str(c.get("direction") or "").lower()
        crossing = ("no st" in dirn or "neither" in dirn or "refuted" in dirn
                    or "cross" in dirn or "no st order" in dirn
                    or "not monotone" in dirn)
        ps = pairs(claim)
        inst = 0; wit = None; und = 0; allhold = True
        if not ps:
            out.append(dict(claim=claim, order=order,
                            status="out of harness scope", instances=0,
                            witness=None, undecided_points=0))
            continue
        for (tag, SA, SB) in ps:
            A, B = Closed(SA), Closed(SB)
            if crossing or tag == "none":
                ok1, w1, u1 = cf.check(order, A, B)
                ok2, w2, u2 = cf.check(order, B, A)
                und += u1 + u2; inst += 1
                if ok1 or ok2:
                    allhold = None
                else:
                    wit = wit or str(w1)
            else:
                ok, w, u = cf.check(order, A, B)
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
        print(o["claim"], "|", o["order"], "|", o["status"], "| inst",
              o["instances"], "| wit", o["witness"])


if __name__ == "__main__":
    go()
