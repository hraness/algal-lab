"""Evaluate canonical claims of doi_10.3934/math.2024434 (MPHRS / MPRHRS).

Marginals:
  MPHRS(a_i, th_i, la_i; Fbar):   surv_i(x) = a_i Fbar(x*th_i)^{la_i}
                                          / (1 - ab_i Fbar(x*th_i)^{la_i})
  MPRHRS(a_i, th_i, be_i; F):     cdf_i(x)  = a_i F(x*th_i)^{be_i}
                                          / (1 - ab_i F(x*th_i)^{be_i})
with ab_i = 1 - a_i.

The joint law is an Archimedean copula C_psi; instantiating psi(t) = e^{-t}
(the product copula, whose generator is log-concave -- all copula hypotheses
in the theorems are satisfied) reduces the second-order-statistic formulas to
the standard independent-sample expressions:
    S_{2:n} = sum_i prod_{j != i} surv_j - (n-1) prod_j surv_j
    F_{n-1:n} = sum_i prod_{j != i} H_j - (n-1) prod_j H_j

Hypotheses: Fbar1 <= Fbar2 or >= Fbar2 pointwise; weak supermajorization
(theta ~<^w eta via ascending partial sums, the convention the printed
examples satisfy); 0 < alpha <= 1; baselines exponential/Weibull.
"""
import json, os
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.3934_math.2024434.json")
OUT = os.path.join(HERE, "eval_doi_10.3934_math.2024434.result.json")
R = sp.Rational

import itertools


def mphrs_surv(a, th, la, Fbar):
    Fb = Fbar.subs(x, th * x)
    return a * Fb**la / (1 - (1 - a) * Fb**la)


def mprhrs_cdf(a, th, be, F):
    Fv = F.subs(x, th * x)
    return a * Fv**be / (1 - (1 - a) * Fv**be)


def os2_sf(survs):
    """S_{2:n} for independent components."""
    n = len(survs)
    expr = sp.Integer(0)
    for i in range(n):
        expr += sp.prod([survs[j] for j in range(n) if j != i])
    expr -= (n - 1) * sp.prod(survs)
    return sp.expand(expr)


def osnm1_cdf(cdfs):
    """F_{n-1:n} for independent components."""
    n = len(cdfs)
    expr = sp.Integer(0)
    for i in range(n):
        expr += sp.prod([cdfs[j] for j in range(n) if j != i])
    expr -= (n - 1) * sp.prod(cdfs)
    return sp.expand(expr)


EXPS = lambda k: sp.exp(-k * x)          # Fbar / F baselines


def mphrs_second(parsX, parsY, Fb1, Fb2):
    SX = os2_sf([mphrs_surv(*p, Fb1) for p in parsX])
    SY = os2_sf([mphrs_surv(*p, Fb2) for p in parsY])
    return SX, SY


def mprhrs_nm1(parsX, parsY, F1, F2):
    SX = 1 - osnm1_cdf([mprhrs_cdf(*p, F1) for p in parsX])
    SY = 1 - osnm1_cdf([mprhrs_cdf(*p, F2) for p in parsY])
    return SX, SY


def pairs_for(r):
    """Return (kind, swap, pairs).  pairs = (SX, SY); swap=True means the
    claimed order is Y-side <=order X-side."""
    claim = r["claim"]
    swap = False
    pairs = []
    # ---------- MPHRS, X_{2:n} ----------
    if claim in ("Theorem 1", "Corollary 1", "Corollary 2", "Theorem 2",
                 "Example 1", "Example 3", "Example 3 (counterexample to p-large replacement)"):
        pass
    if "Theorem 1" == claim:
        # X MPHRS(avec; th1; la1; Fb1) vs Y MPHRS(bvec; th1; la1; Fb2),
        # Fb1 >= Fb2,  a ~<^w b  =>  X2:n >=st Y2:n
        swap = True
        for (av, bv) in [([R(5,10),R(6,10),R(7,10),R(8,10)], [R(1,10),R(2,10),R(3,10),R(4,10)]),
                         ([R(3,5),R(7,10),R(4,5),R(9,10)],   [R(1,5),R(3,10),R(2,5),R(1,2)]),
                         ([R(1,2),R(1,2),R(1,2),R(1,2)],   [R(1,4),R(1,4),R(1,4),R(1,4)])]:
            th = [R(1)] * 4; la = [R(1)] * 4
            SX, SY = mphrs_second(list(zip(av, th, la)), list(zip(bv, th, la)),
                                  EXPS(1), EXPS(2))
            pairs.append((SX, SY))
    elif "Corollary 1" == claim:
        # common tilt a >= mean(a_i): same construction with bv = const.
        swap = True
        for (av, a) in [([R(2,10),R(3,10),R(4,10),R(5,10)], R(1,2)),
                        ([R(1,5),R(1,5),R(2,5),R(2,5)],   R(1,2))]:
            th = [R(1)] * 4; la = [R(1)] * 4; bv = [a] * 4
            SX, SY = mphrs_second(list(zip(av, th, la)), list(zip(bv, th, la)),
                                  EXPS(1), EXPS(2))
            pairs.append((SX, SY))
    elif "Theorem 2" == claim or "Example 1" == claim:
        # shared tilt a=0.2, shared la=0.2, th ~<^w eta, Fb1 <= Fb2
        cases = [([R(6,10),R(7,10),R(8,10),R(9,10)], [R(2,10),R(3,10),R(5,10),R(7,10)],
                  R(1,5), R(1,5), EXPS(3), EXPS(2)),   # printed Example 1
                 ([R(2),R(3),R(4)], [R(1),R(3),R(5)], R(1,3), R(1,2),
                  EXPS(2), EXPS(1)),
                 ([R(3),R(5),R(7),R(9)], [R(1),R(4),R(5),R(7)], R(1,2), R(1),
                  EXPS(2), (1+x)**(-2))]  # Fb2 Pareto (decreasing hr), Fb1<=Fb2
        for (th, et, a, la, Fb1, Fb2) in cases:
            n = len(th)
            SX, SY = mphrs_second([(a, t, la) for t in th],
                                  [(a, t, la) for t in et], Fb1, Fb2)
            pairs.append((SX, SY))
    elif "Corollary 2" == claim:
        # common scale theta >= mean(theta_i); claim X2:n <=st Y2:n
        for (th, t0) in [([R(6,10),R(7,10),R(8,10),R(9,10)], R(1)),
                         ([R(1,5),R(2,5),R(3,5)], R(1))]:
            n = len(th); a = R(1,3); la = R(1)
            SX, SY = mphrs_second([(a, t, la) for t in th],
                                  [(a, t0, la)] * n, EXPS(3), EXPS(2))
            pairs.append((SX, SY))
    # ---------- MPRHRS, X_{n-1:n} ----------
    elif "Theorem 3" == claim:
        # la >=w mu (supermaj): Xn-1:n >=st Yn-1:n ; F1 <= F2
        swap = True
        for (lv, mv) in [([R(2),R(3),R(4)], [R(1),R(3),R(5)]),
                         ([R(2),R(3),R(4),R(5)], [R(1),R(3),R(4),R(6)]),
                         ([R(3,2),R(3,2),R(3,2)], [R(1,2),R(3,2),R(1)])]:
            F1 = 1 - sp.exp(-x/2); F2 = 1 - sp.exp(-x)   # F1 <= F2
            th = [R(1)] * len(lv); a = [R(1,2)] * len(lv)
            SX, SY = mprhrs_nm1(list(zip(a, th, lv)), list(zip(a, th, mv)), F1, F2)
            pairs.append((SX, SY))
    elif "Corollary 3" == claim:
        # X has lambda-vector, Y scalar lambda >= mean; claim Xn-1:n >=st Y
        swap = True
        for (lv, l0) in [([R(2),R(3),R(4)], R(4)),
                         ([R(1,2),R(1),R(3,2)], R(2)),
                         ([R(1),R(2),R(3),R(4)], R(5))]:
            F1 = 1 - sp.exp(-x/2); F2 = 1 - sp.exp(-x)   # F1 <= F2
            n = len(lv); th = [R(1)]*n; a = [R(1,2)]*n
            SX, SY = mprhrs_nm1(list(zip(a, th, lv)),
                                [(R(1,2), R(1), l0)]*n, F1, F2)
            pairs.append((SX, SY))
    elif "Theorem 4" == claim or "Corollary 4" == claim or "Example 2" == claim:
        # a ~<^w b, F1 >= F2 => Xn-1:n <=st Yn-1:n
        for (av, bv) in [([R(5,10),R(6,10),R(7,10),R(8,10)], [R(1,10),R(2,10),R(3,10),R(4,10)]),
                         ([R(6,10),R(7,10),R(8,10),R(8,10)], [R(3,10),R(4,10),R(5,10),R(6,10)]),  # printed Ex.2
                         ([R(3,5),R(7,10),R(4,5)], [R(1,5),R(3,10),R(2,5)])]:
            th = [R(1,10)] * len(av); be = [R(1,2)] * len(av)
            SX, SY = mprhrs_nm1(list(zip(av, th, be)), list(zip(bv, th, be)),
                                1 - sp.exp(-3*x), 1 - sp.exp(-2*x))   # F1 >= F2
            pairs.append((SX, SY))
    elif "Example 3" in claim:
        # MPRHRS n=3, a=(3,4,5), b=(2,4.8,6), F1=F2=1-e^{-x}, th=la=1:
        # claim: NO st ordering in either direction.
        av = [R(3), R(4), R(5)]; bv = [R(2), R(24,5), R(6)]
        th = [R(1)] * 3; be = [R(1)] * 3
        SX, SY = mprhrs_nm1(list(zip(av, th, be)), list(zip(bv, th, be)),
                            1 - sp.exp(-x), 1 - sp.exp(-x))
        # NOTE: X_{2:3} is the middle OS for n=3: use the 2nd-order formula
        SX2 = os2_sf([1 - mprhrs_cdf(*p, 1 - sp.exp(-x)) for p in zip(av, th, be)])
        SY2 = os2_sf([1 - mprhrs_cdf(*p, 1 - sp.exp(-x)) for p in zip(bv, th, be)])
        return "counterexample", swap, [(SX2, SY2)]
    return "normal", swap, pairs


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
        kind, swap, pairs = pairs_for(r)
        inst = 0; wit = None; und = 0; allhold = True
        if kind == "counterexample":
            # claim: neither direction st-orders -> both checks must fail
            for (SX, SY) in pairs:
                ok1, w1, u1 = cf.check(order, Closed(SX), Closed(SY))
                ok2, w2, u2 = cf.check(order, Closed(SY), Closed(SX))
                inst += 1; und += u1 + u2
                if ok1 or ok2:
                    allhold = False   # an ordering exists -> claim wrong
                else:
                    wit = wit or str(w1)
        else:
            for (SX, SY) in pairs:
                A, B = (SY, SX) if swap else (SX, SY)
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
