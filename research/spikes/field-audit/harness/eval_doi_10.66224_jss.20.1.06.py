"""Evaluate canonical claims of doi_10.66224/jss.20.1.06 (Persian SAH paper).

Component marginals under the Scale-Additive-Hazard model:
    S_i(x) = Fbar^{a_i}(x / a_i) * e^{-theta_i x},     Fbar baseline survival.
Portfolios carry independent Bernoulli shocks:  P(I_i X_i > x) = p_i S_i(x).

Archimedean-copula joint law:  X^p_{1:n} survival = psi(sum phi(p_i S_i)),
X^p_{n:n} survival = 1 - phi(sum psi(1 - p_i S_i)).  The independence copula
(phi = e^{-t}, psi = -log) satisfies the printed generator conditions:
phi log-convex AND log-concave (linear log), 1-phi log-concave,
u psi'(1-u) = -u/(1-u) decreasing, u psi'(u) = -1 (weakly increasing),
psi_2 o phi_1 = id super-additive (same copula both sides).  It does NOT
satisfy Theorem 4's 'phi(1-phi)/phi' concave' (it is convex there), so
Theorem 4's hypothesis class is not encodable -> out of scope.

Baseline marginal conditions on f(a) = log Fbar^a(x/a) = -a g(x/a):
  increasing & log-concave in a   <=> g'' > 0   -> Weibull g(v) = v^k, k>1
  decreasing & (log-)convex       <=> g'' < 0   -> Weibull k<1 or Pareto
  increasing & log-convex         -> only weakly satisfiable (g linear, Fbar
                                     = e^{-x}: f constant in a).  Used for
                                     Theorems 1-3 with that caveat.
Concordance sets (A_n anti-monotone, B_n comonotone) are arranged by sorting
vectors consistently; 'a <^w b' = weak supermajorization = ascending partial
sums of a >= those of b (canonical pass-C convention), 'a <_w b' = weak
submajorization (descending partial sums <=).
"""
import json, os
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.66224_jss.20.1.06.json")
OUT = os.path.join(HERE, "eval_doi_10.66224_jss.20.1.06.result.json")
R = sp.Rational


def marg(a, th, Fbar):
    return Fbar.subs(x, x / a) ** a * sp.exp(-th * x)


def series_sf(ps, as_, ths, Fbar):
    s = sp.Integer(1)
    for p, a, t in zip(ps, as_, ths):
        s *= p * marg(a, t, Fbar)
    return s


def parallel_sf(ps, as_, ths, Fbar):
    s = sp.Integer(1)
    for p, a, t in zip(ps, as_, ths):
        s *= 1 - p * marg(a, t, Fbar)
    return 1 - s


EXP = sp.exp(-x)                    # constant in alpha (weakly admissible)
WB5 = sp.exp(-x**5)                 # increasing & log-concave in alpha
PAR = (1 + x) ** (-2)               # decreasing & convex in alpha

def inst_list(spec):
    out = []
    for d in spec:
        yield d


def pairs_for(r):
    c = r.get("conclusion") or {}
    order = c.get("order"); claim = r["claim"]
    if claim in ("Example 1", "Theorem 2", "Theorem 3", "Theorem 9"):
        # parallel: a <^w l  (asc partial sums of alpha >= lambda);
        # claim X^p_{n:n} <=st Y^p_{n:n}
        data = [
            ([R(37),R(24),R(5)], [R(7),R(4),R(2)]),      # printed Example 1
            ([R(3),R(4),R(6)], [R(2),R(3),R(8)]),
            ([R(4),R(5),R(6),R(8)], [R(2),R(4),R(6),R(9)]),
        ]
        out = []
        for (av, lv) in data:
            n = len(av); ps = [R(1,2)]*n; th = [R(1,10)]*n
            SX = parallel_sf(ps, av, th, EXP)
            SY = parallel_sf(ps, lv, th, EXP)
            out.append((SX, SY))
        return out, False
    if claim == "Theorem 1":
        # parallel; h increasing convex (h(t)=t^2); h(p) <^w h(q):
        # choose q coordinatewise <= p (asc sums of h(p) >= h(q) automatic
        # when p asc >= q asc).
        data = [
            ([R(4,10),R(5,10),R(6,10)], [R(3,10),R(4,10),R(5,10)]),
            ([R(6,10),R(7,10),R(8,10),R(9,10)], [R(5,10),R(6,10),R(7,10),R(8,10)]),
        ]
        out = []
        for (pv, qv) in data:
            n = len(pv); av = [R(3),R(2),R(1)][:n] + [R(1)]*(n-3) if n>3 else [R(3),R(2),R(1)]
            th = [R(1),R(1),R(1)][:n] + [R(1)]*(n-3) if n>3 else [R(1),R(1),R(1)]
            SX = parallel_sf(pv, av, th, EXP)
            SY = parallel_sf(qv, av, th, EXP)
            out.append((SX, SY))
        return out, False
    if claim == "Theorem 4":
        return None, None   # hypothesis not encodable (see header)
    if claim == "Example 4":
        # hr ordering fails when the concavity condition is violated:
        # independence copula violates the same condition -> admissible.
        # alpha <^m lambda = alpha majorized by lambda (alpha less spread)
        data = [([R(4),R(4),R(3),R(3)], [R(5),R(4),R(3),R(2)]),
                ([R(5),R(4),R(3),R(2)], [R(6),R(5),R(2),R(1)])]
        out = []
        for (av, lv) in data:
            n = len(av); ps = [R(1,2)]*n; th = [R(1,10)]*n
            SX = parallel_sf(ps, av, th, EXP)
            SY = parallel_sf(ps, lv, th, EXP)
            out.append((SX, SY))
        return out, "hr-fails"
    if claim in ("Example 2", "Example 3"):
        return None, "violating-copula"
    if claim in ("Example 5", "Theorem 8"):
        # series; a <^w l; phi log-concave; baseline incr+log-concave in a:
        # Weibull-5 baseline (printed Example 5 family).
        data = [
            ([R(3),R(4),R(6)], [R(2),R(3),R(8)]),
            ([R(4),R(5),R(6),R(8)], [R(2),R(4),R(6),R(9)]),
            ([R(5),R(6)], [R(3),R(8)]),
        ]
        out = []
        for (av, lv) in data:
            n = len(av); ps = [R(1,2)]*n; th = [R(1,10)]*n
            SX = series_sf(ps, av, th, WB5)
            SY = series_sf(ps, lv, th, WB5)
            out.append((SX, SY))
        return out, False
    if claim == "Theorem 5(a)":
        # series; theta <^w eta (supermaj), alpha same, p same
        data = [
            ([R(1,10),R(2,10),R(3,10)], [R(5,100),R(2,10),R(35,100)]),
            ([R(2,10),R(3,10),R(4,10),R(5,10)], [R(1,10),R(3,10),R(4,10),R(6,10)]),
        ]
        out = []
        for (tv, ev) in data:
            n = len(tv); av = [R(2)]*n; ps = [R(1,2)]*n
            out.append((series_sf(ps, av, tv, EXP), series_sf(ps, av, ev, EXP)))
        return out, False
    if claim == "Theorem 5(b)":
        # weak SUBmajorization theta <_w eta (desc partial sums <=); direction
        # reversed: Y <=st X
        data = [
            ([R(1,10),R(2,10),R(3,10)], [R(5,100),R(2,10),R(35,100)]),
            ([R(1,5),R(3,10),R(2,5)], [R(1,10),R(3,10),R(1,2)]),
        ]
        out = []
        for (tv, ev) in data:
            n = len(tv); av = [R(2)]*n; ps = [R(1,2)]*n
            out.append((series_sf(ps, av, tv, EXP), series_sf(ps, av, ev, EXP)))
        return out, True   # claim is Y <=st X
    if claim == "Theorem 6(a)":
        # baseline decreasing in alpha (Pareto); theta <^w eta
        data = [
            ([R(1,10),R(2,10),R(3,10)], [R(5,100),R(2,10),R(35,100)]),
            ([R(2,10),R(3,10),R(4,10),R(5,10)], [R(1,10),R(3,10),R(4,10),R(6,10)]),
        ]
        out = []
        for (tv, ev) in data:
            n = len(tv); av = [R(2)]*n; ps = [R(1,2)]*n
            out.append((series_sf(ps, av, tv, PAR), series_sf(ps, av, ev, PAR)))
        return out, False
    if claim == "Theorem 6(b)":
        data = [
            ([R(1,10),R(2,10),R(3,10)], [R(5,100),R(2,10),R(35,100)]),
            ([R(1,5),R(3,10),R(2,5)], [R(1,10),R(3,10),R(1,2)]),
        ]
        out = []
        for (tv, ev) in data:
            n = len(tv); av = [R(2)]*n; ps = [R(1,2)]*n
            out.append((series_sf(ps, av, tv, PAR), series_sf(ps, av, ev, PAR)))
        return out, True
    if "Section 6.2" in claim:
        # empirical instance of Theorem 6(a): theta <^w eta, common p,alpha
        tv = [R(8,10000),R(10,10000),R(12,10000)]
        ev = [R(5,10000),R(10,10000),R(15,10000)]
        av = [R(2)]*3; ps = [R(92,100)]*3
        return [(series_sf(ps, av, tv, PAR), series_sf(ps, av, ev, PAR))], False
    if claim == "Theorem 7":
        # series; h decreasing, u h'(u) decreasing; h(p) <^w h(q):
        # h(t) = 1/t decreasing -> h(p) <^w h(q) iff asc sums 1/p >= 1/q
        data = [
            ([R(4,10),R(5,10),R(6,10)], [R(3,10),R(4,10),R(9,10)]),
            ([R(5,10),R(6,10),R(7,10),R(8,10)], [R(4,10),R(6,10),R(7,10),R(9,10)]),
        ]
        out = []
        for (pv, qv) in data:
            n = len(pv); av = [R(2)]*n; th = [R(1,10)]*n
            # claim X^q_{1:n} <=st X^p_{1:n}
            out.append((series_sf(qv, av, th, EXP), series_sf(pv, av, th, EXP)))
        return out, False
    return [], False


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
        pairs, flag = pairs_for(r)
        inst = 0; wit = None; und = 0; allhold = True
        if pairs is None:
            note = ("generator condition not encodable"
                    if flag == "violating-copula" else
                    "only generator satisfying the printed conditions is not encodable")
            out.append(dict(claim=claim, order=order, status="out of harness scope",
                            instances=0, witness=None, undecided_points=0,
                            note=note))
            continue
        for (SX, SY) in pairs:
            if flag == "hr-fails":
                ok1, w1, u1 = cf.check("hr", Closed(SX), Closed(SY))
                ok2, w2, u2 = cf.check("hr", Closed(SY), Closed(SX))
                inst += 1; und += u1 + u2
                if ok1 or ok2:
                    allhold = False
                else:
                    wit = wit or str(w1)
            else:
                A, B = (SY, SX) if flag is True else (SX, SY)
                ok, w, u = cf.check(order, Closed(A), Closed(B))
                inst += 1; und += u
                if not ok:
                    allhold = False; wit = str(w)
        out.append(dict(claim=claim, order=order,
                        status="holds" if allhold else "refuted",
                        instances=inst, witness=wit, undecided_points=und))
    json.dump(out, open(OUT, "w"), indent=1)
    for o in out:
        print(o["claim"], "|", o["order"], "|", o["status"], "| inst", o["instances"],
              "| wit", o["witness"])


if __name__ == "__main__":
    go()
