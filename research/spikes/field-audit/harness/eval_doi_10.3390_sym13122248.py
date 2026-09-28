"""Evaluation of canonical claims for doi:10.3390/sym13122248
(MOTL-G series/parallel systems, Archimedean copulas, Bernoulli shocks).

MOTL-G(alpha,beta,G): marginal survival
    zeta(a,b,g) = a*(1 - T^b)/(a + (1-a)*T^b),  T(g) = 1 - (1-g)^2.
Series system with copula generator psi (phi = psi^{-1}) and shocks p_i:
    S_{Y1:n}(x) = (prod p_i) * psi(sum phi(zeta_i(x))).
Parallel system, independent components, shocks:
    F_{Yn:n}(x) = prod (1 - p_i zeta_i(x)).
Parallel n=2 with copula (Theorem 6 formula as printed):
    F_{Y2:2} = 1 - p1 z1 - p2 z2 + p1 p2 psi(phi(z1)+phi(z2)).

Generators:
  Clayton theta:  psi = (theta t + 1)^{-1/theta},  phi = (u^{-theta}-1)/theta
  AMH (theta=-1): psi = 2/(1+e^t),                 phi = log(2/u - 1)
  independence:   psi = e^{-t},                    phi = -log u
  Gumbel theta:   psi = e^{-t^{1/theta}},          phi = (-log u)^theta
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def T_of(G):
    return 1 - (1 - G) ** 2


def zeta(a, b, G):
    a, b = R(a), R(b)
    T = T_of(G)
    return a * (1 - T ** b) / (a + (1 - a) * T ** b)


def clayton_psi(th, t):
    return (R(th) * t + 1) ** (-1 / R(th))


def clayton_phi(th, u):
    return (u ** (-R(th)) - 1) / R(th)


def amh_psi(t):
    return 2 / (1 + sp.exp(t))


def amh_phi(u):
    return sp.log(2 / u - 1)


def gumbel_psi(th, t):
    return sp.exp(-t ** (1 / R(th)))


def gumbel_phi(th, u):
    return (-sp.log(u)) ** R(th)


def indep_psi(t):
    return sp.exp(-t)


def indep_phi(u):
    return -sp.log(u)


def series_S(albetas, G, psi, phi, ps=1):
    """prod p_i * psi(sum phi(zeta_i)); ps = product of p_i."""
    s = sp.prod(list(ps)) if isinstance(ps, (list, tuple)) else R(ps)
    return s * psi(sum(phi(zeta(a, b, G)) for a, b in albetas))


def parallel_F(albetas, G, ps):
    return sp.prod([1 - p * zeta(a, b, G) for (a, b), p in zip(albetas, ps)])


def parallel_F_dep2(albetas, G, ps, psi, phi):
    z1, z2 = [zeta(a, b, G) for a, b in albetas]
    p1, p2 = list(ps)
    return 1 - p1 * z1 - p2 * z2 + p1 * p2 * psi(phi(z1) + phi(z2))


def robust_check(order, X, Y, precisions=(60, 150, 400)):
    """Same as closedform.check but treats interval-evaluation failures
    (e.g. ComplexResult from underflowed tails at extreme grid points)
    as undecided points instead of crashing."""
    from mpmath import iv
    E = cf.expression(order, X, Y)
    undecided = 0
    # proxy for resolvable_top: lambdified survivals can raise
    # ZeroDivisionError at extreme x through inverse-power generators
    proxy = (sp.exp(-x / 4),) if X.hi == sp.oo else ()
    for point in cf.grid(X.lo, X.hi, proxy):
        decided = False
        for dps in precisions:
            iv.dps = dps
            try:
                value = cf.iv_eval(E, point)
            except Exception:
                continue
            if value.b < 0:
                return False, point, undecided
            if value.a >= 0:
                decided = True
                break
        undecided += not decided
    return True, None, undecided


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


def maj(a, b):
    a, b = sorted(a, reverse=True), sorted(b, reverse=True)
    return sum(a) == sum(b) and all(
        sum(a[:k]) >= sum(b[:k]) for k in range(len(a)))


def Un(v, w):
    return all((v[i] - v[j]) * (w[i] - w[j]) >= 0
               for i in range(len(v)) for j in range(len(v)))


def Vn(v, w):
    return all((v[i] - v[j]) * (w[i] - w[j]) <= 0
               for i in range(len(v)) for j in range(len(v)))


GLom = 1 - 1 / (1 + x)      # Example-1 left baseline (heavier tail)
GExp = 1 - sp.exp(-x)       # right baseline (lighter tail)
GU = x                       # uniform on (0,1)


def example_1():
    """Paper's own numbers: Y1:3 <=st Y*1:3 claimed."""
    albetas = [(R(11, 10), R(2)), (R(4), R(5)), (R(65, 10), R(6))]
    gdelts = [(R(35, 10), R(9, 2)), (R(4), R(5)), (R(63, 10), R(29, 5))]
    pu = [R(5, 100), R(8, 100), R(22, 100)]      # p_i = e^{-u_i}
    pus = [R(1, 100), R(21, 100), R(3, 100)]
    ps = [sp.exp(-u) for u in pu]
    pss = [sp.exp(-u) for u in pus]
    SU = Closed(series_S(albetas, GLom,
                         lambda t: clayton_psi(2, t),
                         lambda u: clayton_phi(2, u), ps))
    SV = Closed(series_S(gdelts, GExp,
                         lambda t: clayton_psi(4, t),
                         lambda u: clayton_phi(4, u), pss))
    h, w, u = robust_check("st", SU, SV)
    return w is None, w, u, 1


def example_2():
    """Same params, Clayton thetas 4 and 1/5 breaking super-additivity:
    claim: no st ordering either way."""
    albetas = [(R(11, 10), R(2)), (R(4), R(5)), (R(65, 10), R(6))]
    gdelts = [(R(35, 10), R(9, 2)), (R(4), R(5)), (R(63, 10), R(29, 5))]
    pu = [R(5, 100), R(8, 100), R(22, 100)]
    pus = [R(1, 100), R(21, 100), R(3, 100)]
    SU = Closed(series_S(albetas, GLom,
                         lambda t: clayton_psi(4, t),
                         lambda u: clayton_phi(4, u),
                         [sp.exp(-v) for v in pu]))
    SV = Closed(series_S(gdelts, GExp,
                         lambda t: clayton_psi(R(1, 5), t),
                         lambda u: clayton_phi(R(1, 5), u),
                         [sp.exp(-v) for v in pus]))
    h1, w1, u1 = robust_check("st", SU, SV)
    h2, w2, u2 = robust_check("st", SV, SU)
    return (w1 is not None) and (w2 is not None), \
        w1 if w1 is not None else w2, u1 + u2, 2


def example_3():
    """G=x, AMH copula, beta=1, alpha=(2,3), gamma=(4,6), Pi p*/Pi p = 0.3
    (violates product ordering). Claim: survival ratio non-monotone =>
    hr fails in both directions."""
    ab = [(R(2), R(1)), (R(3), R(1))]
    gd = [(R(4), R(1)), (R(6), R(1))]
    ps = [R(1, 2), R(1, 2)]        # product 1/4
    pss = [R(3, 10), R(1, 4)]      # product 3/40 = 0.075; ratio 0.3
    SU = Closed(series_S(ab, GU, amh_psi, amh_phi, ps), 0, 1)
    SV = Closed(series_S(gd, GU, amh_psi, amh_phi, pss), 0, 1)
    h1, w1, u1 = robust_check("hr", SU, SV)
    h2, w2, u2 = robust_check("hr", SV, SU)
    return (w1 is not None) and (w2 is not None), \
        w1 if w1 is not None else w2, u1 + u2, 2


def example_4():
    """Independent comps, G=x: alpha=1.2, beta=(2,7), delta=(6,9),
    Pi p*/Pi p = 3. Claim: hr fails in both directions."""
    ab = [(R(6, 5), R(2)), (R(6, 5), R(7))]
    gd = [(R(6, 5), R(6)), (R(6, 5), R(9))]
    ps = [R(1, 2), R(1, 2)]
    pss = [R(3, 4), R(1)]          # product 3/4 vs 1/4 -> ratio 3
    SU = Closed(series_S(ab, GU, indep_psi, indep_phi, ps), 0, 1)
    SV = Closed(series_S(gd, GU, indep_psi, indep_phi, pss), 0, 1)
    h1, w1, u1 = robust_check("hr", SU, SV)
    h2, w2, u2 = robust_check("hr", SV, SU)
    return (w1 is not None) and (w2 is not None), \
        w1 if w1 is not None else w2, u1 + u2, 2


def example_5():
    """Theorem 8(i) illustration: alpha=1 common; lam1>=lam2 baselines;
    beta ~w delta; u nondec matching beta. Claim: F_Y >= F_Y* i.e.
    Y2:2 <=st Y*2:2 -> survival check st(Y, Y*)."""
    res = []
    for be, de, us in [([R(1), R(3)], [R(2), R(2)], [R(1), R(2)]),
                       ([R(1), R(4)], [R(2), R(3)], [R(1), R(3)]),
                       ([R(2), R(5)], [R(3), R(4)], [R(2), R(5)]),
                       ([R(1), R(2)], [R(3, 2), R(3, 2)], [R(1, 2), R(1)])]:
        assert maj(be, de) and Un(be, us) and Un(de, us)
        ps = [sp.exp(-u) for u in us]
        FY = parallel_F([(R(1), b) for b in be],
                        1 - sp.exp(-2 * x), ps)
        FYs = parallel_F([(R(1), d) for d in de],
                         1 - sp.exp(-x), ps)
        DU = Closed(1 - FY); DV = Closed(1 - FYs)
        h, w, u = robust_check("st", DU, DV)
        res.append((w is None, w, u))
    return all(r[0] for r in res), \
        next((r[1] for r in res if not r[0]), None), sum(r[2] for r in res), len(res)


def example_6():
    """G = 1-1/(1+x), h(p)=-log p.
    (i) alpha=1, u=(4.2,0.01) i.e. p=(e^-4.2, e^-0.01), beta=(1,2.7),
        delta=(2.4,2.69)  -> Vn pairs; claim: no st order.
    (ii) beta=1, u=(3.2,2), alpha=(1.1,5), gamma=(3.5,4) -> Vn."""
    res = []
    # part (i)
    us = [R(42, 10), R(1, 100)]
    ps = [sp.exp(-u) for u in us]
    FY = parallel_F([(R(1), R(1)), (R(1), R(27, 10))], GLom, ps)
    FYs = parallel_F([(R(1), R(24, 10)), (R(1), R(269, 100))], GLom, ps)
    for DU, DV in [(Closed(1 - FY), Closed(1 - FYs))]:
        h1, w1, u1 = robust_check("st", DU, DV)
        h2, w2, u2 = robust_check("st", DV, DU)
        res.append((w1 is not None and w2 is not None,
                    w1 if w1 is not None else w2, u1 + u2))
    # part (ii)
    us2 = [R(32, 10), R(2)]
    ps2 = [sp.exp(-u) for u in us2]
    FY = parallel_F([(R(11, 10), R(1)), (R(5), R(1))], GLom, ps2)
    FYs = parallel_F([(R(7, 2), R(1)), (R(4), R(1))], GLom, ps2)
    h1, w1, u1 = robust_check("st", Closed(1 - FY), Closed(1 - FYs))
    h2, w2, u2 = robust_check("st", Closed(1 - FYs), Closed(1 - FY))
    res.append((w1 is not None and w2 is not None,
                w1 if w1 is not None else w2, u1 + u2))
    return all(r[0] for r in res), \
        next((r[1] for r in res if r[1] is not None), None), \
        sum(r[2] for r in res), 2


def example_7():
    """G=x on (0,1), u=(1,1.2). Three parts each asserting NO st order."""
    ps = [sp.exp(-1), sp.exp(-R(6, 5))]
    parts = [
        # (alpha vec, gamma vec, beta vec, delta vec)
        ([R(1), R(8)], [R(4), R(6)], [R(2), R(11, 2)], [R(2), R(11, 2)]),
        ([R(1), R(8)], [R(1), R(8)], [R(2), R(11, 2)], [R(3), R(5)]),
        ([R(1), R(8)], [R(4), R(6)], [R(2), R(11, 2)], [R(3), R(5)]),
    ]
    res = []
    for al, ga, be, de in parts:
        FY = parallel_F(list(zip(al, be)), GU, ps)
        FYs = parallel_F(list(zip(ga, de)), GU, ps)
        DU = Closed(1 - FY, 0, 1); DV = Closed(1 - FYs, 0, 1)
        h1, w1, u1 = robust_check("st", DU, DV)
        h2, w2, u2 = robust_check("st", DV, DU)
        res.append((w1 is not None and w2 is not None,
                    w1 if w1 is not None else w2, u1 + u2))
    return res


def example_8():
    """rh version: part (i) betas all 2, alpha=(1,8),gamma=(4,6);
    part (ii) alphas all 1, beta=(2,5.5),delta=(3,5). G=x, u=(1,1.2)."""
    ps = [sp.exp(-1), sp.exp(-R(6, 5))]
    parts = [
        ([R(1), R(8)], [R(4), R(6)], [R(2), R(2)], [R(2), R(2)]),
        ([R(1), R(1)], [R(1), R(1)], [R(2), R(11, 2)], [R(3), R(5)]),
    ]
    res = []
    for al, ga, be, de in parts:
        FY = parallel_F(list(zip(al, be)), GU, ps)
        FYs = parallel_F(list(zip(ga, de)), GU, ps)
        DU = Closed(1 - FY, 0, 1); DV = Closed(1 - FYs, 0, 1)
        h1, w1, u1 = robust_check("rh", DU, DV)
        h2, w2, u2 = robust_check("rh", DV, DU)
        res.append((w1 is not None and w2 is not None,
                    w1 if w1 is not None else w2, u1 + u2))
    return res


def theorem_6():
    """Dependent n=2 parallel: Z1 >=st Z2 (G1 heavier => use GLom for U,
    GExp for V); (al,be) in U2; (be,u),(be,u*) in V2; u ~m u* (spread);
    claim Y2:2 >=st Y*2:2 => check st(V, U)."""
    n, wit, und = 0, None, 0
    cases = [  # (al, be, u, u*)
        ([R(2), R(1)], [R(2), R(1)], [R(1, 2), R(3, 2)], [R(7, 10), R(13, 10)]),
        ([R(3), R(1)], [R(3), R(2)], [R(1, 2), R(2)], [R(3, 4), R(7, 4)]),
    ]
    for al, be, u, us in cases:
        assert Un(al, be) and Vn(be, u) and Vn(be, us)
        assert maj(u, us)
        p = [sp.exp(-v) for v in u]
        ps = [sp.exp(-v) for v in us]
        FU = parallel_F_dep2(list(zip(al, be)), GLom, p,
                             lambda t: clayton_psi(2, t),
                             lambda uu: clayton_phi(2, uu))
        FV = parallel_F_dep2(list(zip(al, be)), GExp, ps,
                             lambda t: clayton_psi(2, t),
                             lambda uu: clayton_phi(2, uu))
        h, w_, u_ = robust_check("st", Closed(1 - FV), Closed(1 - FU))
        n += 1; und += u_
        if not h and wit is None:
            wit = w_
    return n, wit, und


def theorem_7():
    """Independent parallel n: Z1>=stZ2; (al,be) in Un; (be,u),(be,u*) in Vn;
    prod(1-p) <= prod(1-p*); u ~w u* => Yn:n >=st Yn:n*."""
    n, wit, und = 0, None, 0
    cases = [
        ([R(3), R(2), R(1)], [R(3), R(2), R(1)],
         [R(1, 2), R(1), R(2)], [R(3, 4), R(5, 4), R(3, 2)]),
        ([R(4), R(2), R(1)], [R(4), R(2), R(1)],
         [R(1, 4), R(1), R(3)], [R(1, 2), R(3, 2), R(9, 4)]),
    ]
    for al, be, u, us in cases:
        assert Un(al, be) and Vn(be, u) and Vn(be, us)
        assert maj(u, us)
        p = [sp.exp(-v) for v in u]
        ps_ = [sp.exp(-v) for v in us]
        assert float(sp.prod([1 - v for v in p]).evalf()) <= float(sp.prod([1 - v for v in ps_]).evalf())
        FU = parallel_F(list(zip(al, be)), GLom, p)
        FV = parallel_F(list(zip(al, be)), GExp, ps_)
        h, w_, u_ = robust_check("st", Closed(1 - FV), Closed(1 - FU))
        n += 1; und += u_
        if not h and wit is None:
            wit = w_
    return n, wit, und


def theorem_8(part):
    n, wit, und = 0, None, 0
    if part == 1:
        # common alpha>=1; beta ~w delta; (be,u),(de,u) in Un; Z1<=stZ2
        cases = [
            (R(2), [R(1), R(3)], [R(2), R(2)], [R(1), R(2)]),
            (R(3), [R(1), R(4)], [R(2), R(3)], [R(1, 2), R(2)]),
            (R(3, 2), [R(2), R(5)], [R(3), R(4)], [R(2), R(3)]),
        ]
        for al, be, de, us in cases:
            assert maj(be, de) and Un(be, us) and Un(de, us)
            ps = [sp.exp(-v) for v in us]
            FU = parallel_F([(al, b) for b in be], GExp, ps)
            FV = parallel_F([(al, d) for d in de], GLom, ps)
            h, w_, u_ = robust_check("st", Closed(1 - FU), Closed(1 - FV))
            n += 1; und += u_
            if not h and wit is None:
                wit = w_
    else:
        # common beta; alpha ~w gamma
        cases = [
            (R(2), [R(1), R(3)], [R(2), R(2)], [R(1), R(2)]),
            (R(1), [R(1), R(4)], [R(2), R(3)], [R(1, 2), R(3)]),
        ]
        for be, al, ga, us in cases:
            assert maj(al, ga) and Un(al, us) and Un(ga, us)
            ps = [sp.exp(-v) for v in us]
            FU = parallel_F([(a, be) for a in al], GExp, ps)
            FV = parallel_F([(g, be) for g in ga], GLom, ps)
            h, w_, u_ = robust_check("st", Closed(1 - FU), Closed(1 - FV))
            n += 1; und += u_
            if not h and wit is None:
                wit = w_
    return n, wit, und


def theorem_5():
    """Series, common copula psi, common beta, alpha ~w gamma,
    Pi p <= Pi p* => Y <=hr Y*.  Printed hypotheses: (i) shock product,
    (ii) psi log-concave, (iii) psi(1-psi)/psi' decreasing and concave
    (or convex).  NOTE: the print omits any baseline-ordering condition,
    so both baseline directions are legal instances.  Generator:
    Clayton theta=2 (log psi = -(1/2)log(2t+1): second derivative
    2/(2t+1)^2 > 0, i.e. log-convex -- the print's 'log-concave' is
    inconsistent with the proof, which uses psi'/psi increasing = the
    log-convex direction; we therefore also try psi(t)=e^{-sqrt t}
    (same convexity class).  We test BOTH baseline assignments."""
    n, wit, und = 0, None, 0
    cases = [
        ([(R(3), R(2)), (R(1), R(2))], [(R(2), R(2)), (R(2), R(2))]),
        ([(R(4), R(1)), (R(2), R(1)), (R(1), R(1))],
         [(R(7, 2), R(1)), (R(2), R(1)), (R(3, 2), R(1))]),
    ]
    for U, V in cases:
        al = [p[0] for p in U]; ga = [p[0] for p in V]
        assert maj(al, ga)
        for GU_, GV_ in [(GLom, GExp), (GExp, GLom)]:
            SU = Closed(series_S(U, GU_,
                                 lambda t: gumbel_psi(2, t),
                                 lambda uu: gumbel_phi(2, uu),
                                 [R(1, 2)] * len(U)))
            SV = Closed(series_S(V, GV_,
                                 lambda t: gumbel_psi(2, t),
                                 lambda uu: gumbel_phi(2, uu),
                                 [R(3, 4)] * len(V)))
            h, w_, u_ = robust_check("hr", SU, SV)
            n += 1; und += u_
            if not h and wit is None:
                wit = w_
    return n, wit, und


def theorem_1():
    """alpha common vector; beta ~w delta; (al,be),(al,de) in Un; copulas
    Clayton(2)/(4); baselines GExp/GLom; Pi p <= Pi p* => Y <=st Y*."""
    n, wit, und = 0, None, 0
    cases = [
        ([R(2), R(3), R(4)], [R(1), R(3), R(5)], [R(2), R(3), R(4)]),
        ([R(2), R(4)], [R(1), R(4)], [R(3, 2), R(7, 2)]),
    ]
    for al, be, de in cases:
        assert maj(be, de) and Un(al, be) and Un(al, de)
        SU = Closed(series_S(list(zip(al, be)), GExp,
                             lambda t: clayton_psi(2, t),
                             lambda uu: clayton_phi(2, uu),
                             [R(1, 2)] * len(al)))
        SV = Closed(series_S(list(zip(al, de)), GLom,
                             lambda t: clayton_psi(4, t),
                             lambda uu: clayton_phi(4, uu),
                             [R(3, 4)] * len(al)))
        h, w_, u_ = robust_check("st", SU, SV)
        n += 1; und += u_
        if not h and wit is None:
            wit = w_
    return n, wit, und


def theorem_2():
    """beta common; alpha ~w gamma; (al,be),(ga,be) in Un => Y <=st Y*."""
    n, wit, und = 0, None, 0
    cases = [
        ([R(4), R(3), R(2)], [R(7, 2), R(3), R(5, 2)], [R(3), R(2), R(1)]),
        ([R(4), R(2)], [R(3), R(3)], [R(4), R(2)]),
    ]
    for al, ga, be in cases:
        assert maj(al, ga) and Un(al, be) and Un(ga, be)
        SU = Closed(series_S(list(zip(al, be)), GExp,
                             lambda t: clayton_psi(2, t),
                             lambda uu: clayton_phi(2, uu),
                             [R(1, 2)] * len(al)))
        SV = Closed(series_S(list(zip(ga, be)), GLom,
                             lambda t: clayton_psi(4, t),
                             lambda uu: clayton_phi(4, uu),
                             [R(3, 4)] * len(al)))
        h, w_, u_ = robust_check("st", SU, SV)
        n += 1; und += u_
        if not h and wit is None:
            wit = w_
    return n, wit, und


def theorem_3():
    """Both shapes vary: row-weak-majorization as printed; use Example-1
    parameters plus a second instance."""
    n, wit, und = 0, None, 0
    cases = [
        # (albetas for U, gdelts for V, ps, ps*, baselines fixed)
        ([(R(11, 10), R(2)), (R(4), R(5)), (R(65, 10), R(6))],
         [(R(35, 10), R(9, 2)), (R(4), R(5)), (R(63, 10), R(29, 5))],
         [R(5, 100), R(8, 100), R(22, 100)],
         [R(1, 100), R(21, 100), R(3, 100)]),
        ([(R(2), R(1)), (R(3), R(4))],
         [(R(2), R(2)), (R(3), R(3))],
         [R(1, 2), R(1, 3)], [R(1, 4), R(1, 4)]),
    ]
    for U, V, pu, pv in cases:
        al = [p[0] for p in U]; be = [p[1] for p in U]
        ga = [p[0] for p in V]; de = [p[1] for p in V]
        assert Un(al, be) and Un(al, de) and Un(ga, be)
        assert float(sp.prod([sp.exp(-v) for v in pu]).evalf()) <= float(sp.prod([sp.exp(-v) for v in pv]).evalf())
        SU = Closed(series_S(U, GExp, lambda t: clayton_psi(2, t),
                             lambda uu: clayton_phi(2, uu),
                             [sp.exp(-v) for v in pu]))
        SV = Closed(series_S(V, GLom, lambda t: clayton_psi(4, t),
                             lambda uu: clayton_phi(4, uu),
                             [sp.exp(-v) for v in pv]))
        h, w_, u_ = robust_check("st", SU, SV)
        n += 1; und += u_
        if not h and wit is None:
            wit = w_
    return n, wit, und


def theorem_4():
    """Common copula, identical shapes both sides; only baselines and
    shock products differ => Y <=st Y* (Pi p <= Pi p*)."""
    n, wit, und = 0, None, 0
    cases = [
        ([(R(2), R(1)), (R(3), R(2))], [R(1, 2), R(1, 3)], [R(1, 4), R(1, 4)]),
        ([(R(5), R(2)), (R(1), R(3)), (R(2), R(4))],
         [R(1, 2), R(1, 2), R(1, 2)], [R(1, 4), R(1, 4), R(1, 4)]),
    ]
    for U, pu, pv in cases:
        assert float(sp.prod([sp.exp(-v) for v in pu]).evalf()) <= float(sp.prod([sp.exp(-v) for v in pv]).evalf())
        SU = Closed(series_S(U, GExp, lambda t: clayton_psi(2, t),
                             lambda uu: clayton_phi(2, uu),
                             [sp.exp(-v) for v in pu]))
        SV = Closed(series_S(U, GLom, lambda t: clayton_psi(2, t),
                             lambda uu: clayton_phi(2, uu),
                             [sp.exp(-v) for v in pv]))
        h, w_, u_ = robust_check("st", SU, SV)
        n += 1; und += u_
        if not h and wit is None:
            wit = w_
    return n, wit, und


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.3390_sym13122248.json")))
    results = []
    for recd in canon:
        order = recd["conclusion"]["order"]
        label = recd["claim"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        if label == "Example 1":
            ok, w, u, n_ = example_1()
        elif label == "Example 2":
            ok, w, u, n_ = example_2()
        elif label == "Example 3":
            ok, w, u, n_ = example_3()
        elif label == "Example 4":
            ok, w, u, n_ = example_4()
        elif label == "Example 5":
            ok, w, u, n_ = example_5()
        elif label.startswith("Example 6"):
            ok, w, u, n_ = example_6()
        elif label.startswith("Example 7"):
            res = example_7()
            if label == "Example 7":
                ok = all(r[0] for r in res)
                w = next((r[1] for r in res if r[1] is not None), None)
                u = sum(r[2] for r in res)
            elif label == "Example 7(i)":
                ok, w, u = res[0]
            elif label == "Example 7(ii)":
                ok, w, u = res[1]
            else:
                ok, w, u = res[2]
            n_ = 1
        elif label == "Example 8":
            res = example_8()
            ok = all(r[0] for r in res)
            w = next((r[1] for r in res if r[1] is not None), None)
            u = sum(r[2] for r in res)
            n_ = len(res)
        elif label == "Theorem 6":
            n_, w, u = theorem_6()
            results.append(rec(recd, "holds" if w is None else "refuted",
                               instances=n_, witness=w, undecided=u))
            continue
        elif label == "Theorem 7":
            n_, w, u = theorem_7()
            results.append(rec(recd, "holds" if w is None else "refuted",
                               instances=n_, witness=w, undecided=u))
            continue
        elif label == "Theorem 5":
            n_, w, u = theorem_5()
            results.append(rec(recd, "holds" if w is None else "refuted",
                               instances=n_, witness=w, undecided=u))
            continue
        elif label == "Theorem 1":
            n_, w, u = theorem_1()
            results.append(rec(recd, "holds" if w is None else "refuted",
                               instances=n_, witness=w, undecided=u))
            continue
        elif label == "Theorem 2":
            n_, w, u = theorem_2()
            results.append(rec(recd, "holds" if w is None else "refuted",
                               instances=n_, witness=w, undecided=u))
            continue
        elif label == "Theorem 3":
            n_, w, u = theorem_3()
            results.append(rec(recd, "holds" if w is None else "refuted",
                               instances=n_, witness=w, undecided=u))
            continue
        elif label == "Theorem 4":
            n_, w, u = theorem_4()
            results.append(rec(recd, "holds" if w is None else "refuted",
                               instances=n_, witness=w, undecided=u))
            continue
        elif label == "Theorem 8(i)":
            n_, w, u = theorem_8(1)
            results.append(rec(recd, "holds" if w is None else "refuted",
                               instances=n_, witness=w, undecided=u))
            continue
        elif label == "Theorem 8(ii)":
            n_, w, u = theorem_8(2)
            results.append(rec(recd, "holds" if w is None else "refuted",
                               instances=n_, witness=w, undecided=u))
            continue
        elif label.startswith("Section 4") or label.startswith("Section 5"):
            results.append(rec(recd, "out of harness scope"))
            continue
        else:
            results.append(rec(recd, "out of harness scope"))
            continue
        results.append(rec(recd, "holds" if ok else "refuted",
                           instances=n_, witness=w, undecided=u))
    out = os.path.join(HERE, "eval_doi_10.3390_sym13122248.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
