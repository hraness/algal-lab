"""Evaluate canonical claims of doi_10.66224/jss.20.1.06 (Persian SAH paper).

Component marginal (Scale-Additive-Hazard), support x >= max(a_i, 1) when the
baseline is Fbar(x) = 1/x:
    S_i(x) = Fbar^{a_i}(x / a_i) * e^{-theta_i x}
Shock margins:  v_i(x) = p_i S_i(x)   (survival of I_{p_i} X_i, i.e. of
'component present'),  w_i(x) = 1 - v_i(x) (its cdf).

Archimedean copula with forward generator psi (psi:(0,1]->[0,inf), decreasing)
and inverse phi = psi^{-1}:
    S_{min}(x) = phi( sum_i psi(v_i) )
    S_{max}(x) = 1 - phi( sum_i psi(w_i) )
Encodable generator pairs:
    indep:   psi = -log u,               phi = e^{-t}
    AMH(d):  psi = log((1-d+d u)/u),     phi = (1-d)/(e^t - d),   d in (0,1)
    ex5gen:  psi = log((2-u)/u),         phi = 2/(1+e^t)
The printed generator conditions are evaluated on these directly:
    'phi log-convex'     holds for indep (linear) and AMH phi;
    'phi log-concave'    holds for indep and ex5gen;
    "u psi'(1-u) decreasing"  holds for AMH d in (0,1) and indep;
    "u psi'(u) increasing"    holds for AMH (it is (d-1)/(1-d+d u));
    'psi_2 o phi_1 super-additive'  holds when C1 = C2 (identity);
    'phi(1-phi)/phi' decreasing and concave'  fails for ALL three encodable
        generators (it is convex)  -> Theorem 4 out of harness scope.

Baseline marginal conditions on f(a) = log Fbar^a(x/a):
    increasing & log-convex  -> Fbar = 1/x on [1,inf): f = a log(a/x),
                                 f' = log(a/x)+1 >= 0 on a >= x, f''=1/a > 0
    increasing & log-concave -> Fbar = exp(-x^5):  f = -x^5/a^4
    decreasing               -> Fbar = (1+x)^{-2}: f = -2a log(1+x/a)

'a <^w b' = weak supermajorization (ascending partial sums of a >= b's, the
superscript-w convention verified in the canonical for Example 1);
'a <_w b' = weak submajorization (descending partial sums of a <= b's).
"""
import json, os
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.66224_jss.20.1.06.json")
OUT = os.path.join(HERE, "eval_doi_10.66224_jss.20.1.06.result.json")
R = sp.Rational


# ---------- copulas ----------
def phi_psi(name):
    if name == "indep":
        return (lambda u: -sp.log(u), lambda t: sp.exp(-t))
    if name == "amh":
        d = R(4, 5)
        return (lambda u: sp.log((1 - d + d * u) / u),
                lambda t: (1 - d) / (sp.exp(t) - d))
    if name == "ex5":
        return (lambda u: sp.log((2 - u) / u), lambda t: 2 / (1 + sp.exp(t)))
    raise ValueError(name)


def marg(a, th, Fbar):
    return Fbar.subs(x, x / a) ** a * sp.exp(-th * x)


def series_sf(ps, as_, ths, Fbar, cop):
    psi, phi = phi_psi(cop)
    V = sp.Integer(0)
    for p, a, t in zip(ps, as_, ths):
        V += psi(p * marg(a, t, Fbar))
    return phi(V)


def parallel_sf(ps, as_, ths, Fbar, cop):
    psi, phi = phi_psi(cop)
    V = sp.Integer(0)
    for p, a, t in zip(ps, as_, ths):
        V += psi(1 - p * marg(a, t, Fbar))
    return 1 - phi(V)


PARX = 1 / x                     # Fbar = 1/x, x >= max(a_i,1)
WB5 = sp.exp(-x**5)              # increasing & log-concave in alpha, x >= 0
EXP = sp.exp(-x)                 # constant in alpha (vacuous-weak admissible)
PAR2 = (1 + x) ** (-2)           # decreasing in alpha


def pairs_for(r):
    """-> (list of (S_left, S_right, lo), direction_note).

    S_left <=st S_right is the printed claim.
    """
    claim = r["claim"]
    P = lambda v: [R(vv) for vv in v]

    if claim == "Example 1" or claim == "Theorem 2":
        # parallel, a <^w l.  Printed Ex1: a=(37,24,5), l=(7,4,2), AMH(0.8),
        # Fbar = 1/x, p=(0.72,0.18,0.02), theta unspecified -> small equal.
        out = []
        for (av, lv, pv, cop) in [
                ([37,24,5], [7,4,2], [.72,.18,.02], "amh"),          # printed
                ([37,24,5], [7,4,2], [.72,.18,.02], "indep"),
                ([5,7,9],    [3,5,11], [.5,.5,.5],    "amh"),
                ([5,7,9],    [3,5,11], [.5,.5,.5],    "indep")]:
            n = len(av); th = [R(1,10)]*n
            lo = max([R(1)] + av + lv)
            SX = parallel_sf(P(pv), P(av), th, PARX, cop)
            SY = parallel_sf(P(pv), P(lv), th, PARX, cop)
            out.append((SX, SY, lo))
        return out
    if claim == "Theorem 1":
        # parallel; h(p) <^w h(q), h increasing convex.  Equal totals under
        # majorization h(p)=p^2 is hard; use coordinatewise p >= q (asc sums
        # then satisfy the superscript-w relation automatically).
        out = []
        for (pv, qv, cop) in [
                ([.4,.5,.6], [.3,.4,.5], "amh"),
                ([.4,.5,.6], [.3,.4,.5], "indep"),
                ([.6,.7,.8,.9], [.5,.6,.7,.8], "amh"),
                ([.6,.7,.8,.9], [.5,.6,.7,.8], "indep")]:
            n = len(pv); av = [R(3)]*n; th = [R(1,10)]*n
            lo = R(3)
            SX = parallel_sf(P(pv), av, th, PARX, cop)
            SY = parallel_sf(P(qv), av, th, PARX, cop)
            out.append((SX, SY, lo))
        return out
    if claim == "Theorem 3" or claim == "Theorem 9":
        # parallel; copulas on both sides (same copula -> super-additive ok);
        # Thm9 asks phi_1 log-concave -> use indep/ex5gen.
        cps = ["indep", "ex5"] if claim == "Theorem 9" else ["amh", "indep"]
        out = []
        for cop in cps:
            for (av, lv, pv) in [([5,7,9],[3,5,11],[.5,.5,.5]),
                                 ([37,24,5],[7,4,2],[.7,.2,.1])]:
                n = len(av); th = [R(1,10)]*n
                lo = max([R(1)] + av + lv)
                out.append((parallel_sf(P(pv), P(av), th, PARX, cop),
                            parallel_sf(P(pv), P(lv), th, PARX, cop), lo))
        return out
    if claim == "Example 5" or claim == "Theorem 8":
        # series; a <^w l; phi log-concave (indep/ex5); baseline incr &
        # log-concave in alpha -> Weibull-5.
        out = []
        for cop in ["indep", "ex5"]:
            for (av, lv, pv, tv) in [
                    ([5,7,9], [3,5,11], [.5,.5,.5], [.1,.1,.1]),
                    ([6,7,8,9], [4,5,7,11], [.6,.6,.6,.6], [.2,.2,.2,.2]),
                    ([5,8], [3,11], [.5,.5], [.1,.1])]:
                n = len(av)
                out.append((series_sf(P(pv), P(av), P(tv), WB5, cop),
                            series_sf(P(pv), P(lv), P(tv), WB5, cop), R(0)))
        return out
    if claim == "Theorem 5(a)":
        # series; theta <^w eta (supermaj); increasing-in-alpha baseline 1/x.
        out = []
        for cop in ["indep", "amh"]:
            for (tv, ev) in [([.3,.4,.5],[.1,.4,.6]),     # asc sums t >= e
                             ([.4,.5,.6,.7],[.2,.4,.6,.8])]:
                n = len(tv); av = [R(3)]*n; pv = P([.5]*n)
                out.append((series_sf(pv, av, P(tv), PARX, cop),
                            series_sf(pv, av, P(ev), PARX, cop), R(3)))
        return out
    if claim == "Theorem 5(b)":
        # series; theta <_w eta (SUBmaj, desc sums <=); claim Y <=st X:
        # X has theta, Y has eta.  We return (SX, SY) but flag direction
        # via a tag consumed in go().
        out = []
        for cop in ["indep", "ex5"]:
            for (tv, ev) in [([.1,.2,.3],[.15,.25,.35]),
                             ([.2,.3,.4],[.3,.4,.5])]:
                n = len(tv); av = [R(3)]*n; pv = P([.5]*n)
                out.append(("rev", series_sf(pv, av, P(tv), PARX, cop),
                            series_sf(pv, av, P(ev), PARX, cop), R(3)))
        return out
    if claim == "Theorem 6(a)":
        # series; decreasing-in-alpha baseline (Pareto); theta <^w eta supermaj
        out = []
        for cop in ["indep", "amh"]:
            for (tv, ev) in [([.3,.4,.5],[.1,.4,.6]),
                             ([.4,.5,.6,.7],[.2,.4,.6,.8]),
                             ([R(8,10000),R(10,10000),R(12,10000)],
                              [R(5,10000),R(10,10000),R(15,10000)])]:
                n = len(tv); av = [R(2)]*n; pv = P([.9]*n)
                out.append((series_sf(pv, av, P(tv), PAR2, cop),
                            series_sf(pv, av, P(ev), PAR2, cop), R(0)))
        return out
    if claim == "Theorem 6(b)":
        out = []
        for cop in ["indep", "ex5"]:
            for (tv, ev) in [([.1,.2,.3],[.15,.25,.35]),
                             ([.2,.3,.4],[.3,.4,.5])]:
                n = len(tv); av = [R(2)]*n; pv = P([.9]*n)
                out.append(("rev", series_sf(pv, av, P(tv), PAR2, cop),
                            series_sf(pv, av, P(ev), PAR2, cop), R(0)))
        return out
    if "Section 6.2" in claim:
        tv = [R(8,10000),R(10,10000),R(12,10000)]
        ev = [R(5,10000),R(10,10000),R(15,10000)]
        av = [R(2)]*3; pv = P([.92]*3)
        return [(series_sf(pv, av, tv, PAR2, "indep"),
                 series_sf(pv, av, ev, PAR2, "indep"), R(0))]
    if claim == "Theorem 7":
        # series; h decreasing (h=1/t), h(p) <^w h(q): choose q coordinatewise
        # smaller than p -> 1/q asc sums larger -> h(p) <^w h(q) holds.
        # claim: X^q_{1:n} <=st X^p_{1:n}  -> left is the q-system.
        out = []
        for cop in ["indep", "amh"]:
            for (pv, qv) in [([.5,.6,.7],[.3,.4,.5]),
                             ([.6,.7,.8],[.4,.5,.6])]:
                n = len(pv); av = [R(2)]*n; tv = [R(1,10)]*n
                Sq = series_sf(P(qv), av, tv, EXP, cop)
                Sp = series_sf(P(pv), av, tv, EXP, cop)
                out.append((Sq, Sp, R(0)))
        return out
    if claim == "Example 4":
        # hr ordering fails when condition (d) fails.  Every encodable
        # generator violates (d); test whether the failure reproduces.
        out = []
        for cop in ["indep", "amh"]:
            for (av, lv) in [([4,4,3,3],[5,4,3,2]), ([5,4,3,2],[6,5,2,1])]:
                n = len(av); pv = P([.5]*n); tv = [R(1,10)]*n
                lo = max([R(1)] + av + lv)
                SX = parallel_sf(pv, P(av), tv, PARX, cop)
                SY = parallel_sf(pv, P(lv), tv, PARX, cop)
                out.append(("hr-fails", SX, SY, lo))
        return out
    if claim in ("Example 2", "Example 3"):
        return "violating-copula"
    if claim == "Theorem 4":
        return "no-copula"
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
        res = pairs_for(r)
        inst = 0; wit = None; und = 0; allhold = True
        if res == "violating-copula":
            out.append(dict(claim=claim, order=order, status="out of harness scope",
                            instances=0, witness=None, undecided_points=0,
                            note="counterexample premise is a copula violating "
                                 "u psi'(1-u) decreasing -- no encodable "
                                 "Archimedean generator violates it"))
            continue
        if res == "no-copula":
            out.append(dict(claim=claim, order=order, status="out of harness scope",
                            instances=0, witness=None, undecided_points=0,
                            note="no encodable Archimedean generator satisfies "
                                 "phi(1-phi)/phi' decreasing AND concave"))
            continue
        if not res:
            out.append(dict(claim=claim, order=order, status="out of harness scope",
                            instances=0, witness=None, undecided_points=0,
                            note="unhandled claim"))
            continue
        for item in res:
            rev = False
            if item and item[0] == "rev":
                _, SX, SY, lo = item; rev = True
            elif item and item[0] == "hr-fails":
                _, SX, SY, lo = item
                ok1, w1, u1 = cf.check("hr", Closed(SX, lo=lo), Closed(SY, lo=lo))
                ok2, w2, u2 = cf.check("hr", Closed(SY, lo=lo), Closed(SX, lo=lo))
                inst += 1; und += u1 + u2
                if ok1 or ok2:
                    # ordering existed on an admissible violating instance;
                    # the claimed non-ordering cannot be reproduced -> the
                    # printed example is copula-specific, not refutable
                    # through our generators.
                    allhold = None
                else:
                    wit = wit or str(w1)
                continue
            else:
                SX, SY, lo = item
            A, B = (SY, SX) if rev else (SX, SY)
            ok, w, u = cf.check(order, Closed(A, lo=lo), Closed(B, lo=lo))
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
