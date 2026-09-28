"""Evaluator for doi:10.2298/FIL2104315D -- stochastic comparisons of largest
claim amounts (parallel systems) under the exponentiated location-scale (ELS)
model with Bernoulli claim indicators.

Model: Xi ~ F^{alpha_i}((x - lambda_i)/theta_i), x > lambda_i.
Ui = Ji Xi, Ji ~ Bernoulli(p_i).  Largest claim Un:n has df
    F_U(t) = prod_i [1 - p_i (1 - F^{alpha_i}((t - lam_i)/theta_i))],
    t > max_i lam_i.
(The psi-transform only enters the majorization premises:
 psi^{-1}(psi(p_i)) = p_i in the df.)

Baselines:
  GLFR05: F = 1 - exp(-sqrt(y))          (a=1,b=0,d=1/2; paper: C1-C4)
  MOQL:   Marshall-Olkin extended quasi Lindley, a=1/10,b=-9/10,d=4/5
          (paper: C1-C8)
  LOM5:   F = 1 - (1+5y)^{-1/5}          (Counterexample 3.3 baseline)
  POW5:   F = 1 - (1+y^5)^{-4}           (Counterexamples 3.1/3.2)

Weak-supermajorization convention used by this paper (Ex. 5.1): ascending
partial sums of a >= those of b.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))
y = sp.Symbol("y", positive=True)


def GLFR05(yy):
    return 1 - sp.exp(-sp.sqrt(yy))


def MOQL(yy):
    a, b, d = R(1, 10), R(-9, 10), R(4, 5)
    q_ = (b + 1 + d * yy) / (b + 1) * sp.exp(-d * yy)
    return (1 - q_) / (1 - (1 - a) * q_)


def LOM5(yy):
    return 1 - (1 + 5 * yy) ** R(-1, 5)


def POW5(yy):
    return 1 - (1 + yy ** 5) ** (-4)


def DEC1(yy):
    """baseline on y>=1 with r(y) = 2/y + 1/y^2: satisfies
    (C1) r dec, (C2) yr dec, (C4) r'/r inc, (C5) yr convex,
    (C7) y^2(yr)' = -1 constant (nondecreasing), (C8) r convex.
    Fbar = y^{-2} e^{1/y - 1}, F(1)=0, Fbar(infty)=0."""
    return 1 - yy ** (-2) * sp.exp(1 / yy - 1)


def DEC2(yy):
    """second baseline y>=1, r(y) = 2/y + 1/y^3: satisfies
    (C1),(C2),(C4),(C5),(C8) as well.
    Fbar = y^{-2} e^{(1/y^2 - 1)/2}."""
    return 1 - yy ** (-2) * sp.exp((1 / yy ** 2 - 1) / 2)


def claim_df(probs, alps, lams, ths, base):
    """cdf of Un:n, valid for t > max(lams)."""
    F = R(1)
    for p_, a_, l_, t_ in zip(probs, alps, lams, ths):
        F *= 1 - p_ * (1 - base((x - l_) / t_) ** a_)
    return F


def robust_check(order, X, Y, precisions=(60, 150, 400)):
    """cf.check with per-point exception tolerance: grid points whose
    interval evaluation raises (negative-base powers near support edges,
    underflow in tails) are counted undecided instead of crashing."""
    assert X.lo == Y.lo and X.hi == Y.hi
    if order == "st":
        E = Y.survival - X.survival
    elif order == "hr":
        E = X.density * Y.survival - Y.density * X.survival
    elif order == "rh":
        E = Y.density * (1 - X.survival) - X.density * (1 - Y.survival)
    else:
        E = sp.diff(Y.density, x) * X.density \
            - Y.density * sp.diff(X.density, x)
    und = 0
    try:
        points = cf.grid(X.lo, X.hi, (X.survival, Y.survival))
    except Exception:
        points = cf.grid(X.lo, X.hi, ())
    for point in points:
        decided = False
        for dps in precisions:
            cf.iv.dps = dps
            try:
                value = cf.iv_eval(E, point)
            except Exception:
                continue
            if value.b < 0:
                return False, point, und
            if value.a >= 0:
                decided = True
                break
        und += not decided
    return True, None, und


def ck(order, prU, aU, lU, tU, prV, aV, lV, tV, base, direction="U>=V",
       extra_lo=None):
    """Build Closed objects on common support and check the order.
    direction 'U>=V' means claim is U >=order V, i.e. check(V, U)."""
    lo = max(max(lU), max(lV))
    if base in (DEC1, DEC2):
        # baseline support begins at y=1 -> t >= lam_i + th_i
        lo = max([l_ + t_ for l_, t_ in zip(lU, tU)]
                 + [l_ + t_ for l_, t_ in zip(lV, tV)])
    if extra_lo:
        lo = max(lo, extra_lo)
    FU = claim_df(prU, aU, lU, tU, base)
    FV = claim_df(prV, aV, lV, tV, base)
    DU, DV = Closed(1 - FU, lo), Closed(1 - FV, lo)
    if direction == "U>=V":
        return robust_check(order, DV, DU)
    return robust_check(order, DU, DV)


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


def Tswap(w, i, j, n):
    """n x n T-transform matrix w I + (1-w) P swapping cols i,j."""
    M_ = sp.zeros(n)
    for r_ in range(n):
        for c_ in range(n):
            if r_ == c_ and r_ not in (i, j):
                M_[r_, c_] = 1
            elif (r_, c_) in [(i, i), (j, j)]:
                M_[r_, c_] = w
            elif (r_, c_) in [(i, j), (j, i)]:
                M_[r_, c_] = 1 - w
    return M_


def chain(rows, mats):
    """D = C * T1 * T2 * ... ; C given as list of row-lists -> returns
    transformed row-lists."""
    C = sp.Matrix(rows)
    for Tw in mats:
        C = C * Tw
    return [list(row) for row in C.tolist()]


def wsup_paper(a, b):
    """a weakly supermajorizes b, paper's convention: ascending partial
    sums of a >= those of b."""
    a, b = sorted(a), sorted(b)
    return all(sum(a[:k]) >= sum(b[:k]) for k in range(1, len(a) + 1))


def plarger_recip(a, b):
    """1/a p-larger 1/b: ascending partial products of 1/a >= of 1/b.
    Equivalent: asc products of a <= b."""
    a, b = sorted(a), sorted(b)
    return all(sp.prod(a[:k]) <= sp.prod(b[:k])
               for k in range(1, len(a) + 1))


def run(order, cases, direction="U>=V"):
    n, wit, und = 0, None, 0
    for case in cases:
        h, w_, u_ = ck(order, *case[:8], case[8],
                       direction=direction,
                       extra_lo=case[9] if len(case) > 9 else None)
        n += 1; und += u_
        if not h and wit is None:
            wit = w_
    return n, wit, und


# ======================================================================
# Concrete instances.  Every record: list of (pU,aU,lU,tU, pV,aV,lV,tV,
# base[,lo]) -- parameters are the ACTUAL probabilities/params entering
# the df; psi-values determine them through p = psi^{-1}(w).
# ======================================================================
G = GLFR05
MQL = MOQL
L5 = LOM5
P5 = POW5


def theorem_3_1i():
    """psi=p^2 (C9), theta=delta scalar; (psi_p,lam;2) in M2 chain-maj.
    T_{1/2} full averaging."""
    p = [R(1, 2), R(9, 10)]                     # psi(p) = (1/4, 81/100)
    lam = [R(2, 5), R(6, 5)]
    wq, mu = chain([[R(1, 4), R(81, 100)], lam],
                   [Tswap(R(1, 2), 0, 1, 2)])
    q = [sp.sqrt(wq[0]), sp.sqrt(wq[1])]
    return run("st", [
        (p, [R(1, 2)] * 2, lam, [R(1)] * 2,
         q, [R(1, 2)] * 2, mu, [R(1)] * 2, G),
        (p, [R(4, 5)] * 2, lam, [R(1)] * 2,
         q, [R(4, 5)] * 2, mu, [R(1)] * 2, L5),
    ])


def theorem_3_1ii():
    """psi=-ln p (C10), lam=mu scalar; (psi_p,1/theta;2) in M2."""
    wp = [R(51, 100), R(120, 100)]    # psi(p): asc
    p = [sp.exp(-wp[0]), sp.exp(-wp[1])]
    ith = [R(1, 2), R(7, 5)]          # asc -> co-monotone with wp
    wq, idel = chain([wp, ith], [Tswap(R(1, 2), 0, 1, 2)])
    q = [sp.exp(-wq[0]), sp.exp(-wq[1])]
    lam = [R(1, 2)] * 2
    return run("st", [
        (p, [R(1, 2)] * 2, lam, [1 / a_ for a_ in ith],
         q, [R(1, 2)] * 2, lam, [1 / a_ for a_ in idel], G),
        (p, [R(3, 4)] * 2, lam, [1 / a_ for a_ in ith],
         q, [R(3, 4)] * 2, lam, [1 / a_ for a_ in idel], L5),
    ])


def theorem_3_2i():
    """n=3 version of Thm 3.1(i): one T-transform on cols (0,1)."""
    wp = [R(9, 100), R(25, 100), R(64, 100)]   # psi(p)=p^2 asc
    p = [sp.sqrt(w_) for w_ in wp]
    lam = [R(1, 5), R(7, 10), R(3, 2)]
    wq, mu = chain([wp, lam], [Tswap(R(1, 2), 0, 1, 3)])
    q = [sp.sqrt(w_) for w_ in wq]
    return run("st", [
        (p, [R(1, 2)] * 3, lam, [R(1)] * 3,
         q, [R(1, 2)] * 3, mu, [R(1)] * 3, G),
        (p, [R(9, 10)] * 3, lam, [R(1)] * 3,
         q, [R(9, 10)] * 3, mu, [R(1)] * 3, L5),
    ])


def theorem_3_2ii():
    """n=3 version of Thm 3.1(ii), psi=-ln p."""
    wp = [R(1, 5), R(3, 5), R(13, 10)]
    p = [sp.exp(-w_) for w_ in wp]
    ith = [R(2, 5), R(9, 10), R(8, 5)]
    wq, idel = chain([wp, ith], [Tswap(R(1, 2), 1, 2, 3)])
    q = [sp.exp(-w_) for w_ in wq]
    lam = [R(1, 2)] * 3
    return run("st", [
        (p, [R(1, 2)] * 3, lam, [1 / a_ for a_ in ith],
         q, [R(1, 2)] * 3, lam, [1 / a_ for a_ in idel], G),
        (p, [R(4, 5)] * 3, lam, [1 / a_ for a_ in ith],
         q, [R(4, 5)] * 3, lam, [1 / a_ for a_ in idel], L5),
    ])


def theorem_3_3i():
    """Two different-structure T-transforms."""
    wp = [R(9, 100), R(25, 100), R(64, 100)]
    p = [sp.sqrt(w_) for w_ in wp]
    lam = [R(1, 5), R(7, 10), R(3, 2)]
    wq, mu = chain([wp, lam], [Tswap(R(3, 5), 0, 1, 3),
                               Tswap(R(3, 5), 1, 2, 3)])
    q = [sp.sqrt(w_) for w_ in wq]
    return run("st", [
        (p, [R(1, 2)] * 3, lam, [R(1)] * 3,
         q, [R(1, 2)] * 3, mu, [R(1)] * 3, G),
    ])


def theorem_3_3ii():
    wp = [R(1, 5), R(3, 5), R(13, 10)]
    p = [sp.exp(-w_) for w_ in wp]
    ith = [R(2, 5), R(9, 10), R(8, 5)]
    wq, idel = chain([wp, ith], [Tswap(R(3, 5), 0, 1, 3),
                                 Tswap(R(3, 5), 1, 2, 3)])
    q = [sp.exp(-w_) for w_ in wq]
    lam = [R(1, 2)] * 3
    return run("st", [
        (p, [R(1, 2)] * 3, lam, [1 / a_ for a_ in ith],
         q, [R(1, 2)] * 3, lam, [1 / a_ for a_ in idel], G),
    ])


def theorem_3_4i():
    return "SCOPE"
def theorem_3_4i_vacuous():
    """n=2, alpha=1, theta=delta scalar, p=q scalar; (lam,1/th) in Q2
    (trivially, since 1/th constant); lam >> mu via T_{1/2}."""
    lam = [R(2, 5), R(6, 5)]
    mu, _ = chain([lam, [R(1)] * 2], [Tswap(R(1, 2), 0, 1, 2)])
    p = [R(7, 10)] * 2
    return run("rh", [
        (p, [R(1)] * 2, lam, [R(1)] * 2,
         p, [R(1)] * 2, mu, [R(1)] * 2, MQL),
        (p, [R(1)] * 2, lam, [R(2)] * 2,
         p, [R(1)] * 2, mu, [R(2)] * 2, G),
    ])


def theorem_3_4ii():
    """(lam,psi_p) in M2, chain maj; psi=p^2; needs C1,C8 baseline."""
    wp = [R(1, 4), R(81, 100)]
    p = [sp.sqrt(w_) for w_ in wp]
    lam = [R(2, 5), R(6, 5)]
    wq, mu = chain([wp, lam], [Tswap(R(1, 2), 0, 1, 2)])
    q = [sp.sqrt(w_) for w_ in wq]
    return run("rh", [
        (p, [R(1)] * 2, lam, [R(1)] * 2,
         q, [R(1)] * 2, mu, [R(1)] * 2, L5),
        (p, [R(1)] * 2, lam, [R(1)] * 2,
         q, [R(1)] * 2, mu, [R(1)] * 2, MQL),
    ])


def theorem_3_4iii():
    """lam=mu scalar; (1/th, psi_p) in Q2 (antitone)."""
    wp = [R(64, 100), R(16, 100)]     # psi_p desc
    p = [sp.sqrt(w_) for w_ in wp]
    ith = [R(1), R(5, 3)]             # asc -> antitone vs wp
    wq, idel = chain([wp, ith], [Tswap(R(1, 2), 0, 1, 2)])
    q = [sp.sqrt(w_) for w_ in wq]
    lam = [R(1)] * 2
    return run("rh", [
        (p, [R(1)] * 2, lam, [1 / a_ for a_ in ith],
         q, [R(1)] * 2, lam, [1 / a_ for a_ in idel], DEC1),
        (p, [R(1)] * 2, lam, [1 / a_ for a_ in ith],
         q, [R(1)] * 2, lam, [1 / a_ for a_ in idel], DEC2),
    ])


def theorem_3_5i():
    return "SCOPE"


def theorem_3_5ii():
    wp = [R(9, 100), R(25, 100), R(64, 100)]
    p = [sp.sqrt(w_) for w_ in wp]
    lam = [R(1, 5), R(7, 10), R(3, 2)]
    wq, mu = chain([wp, lam], [Tswap(R(1, 2), 0, 2, 3)])
    q = [sp.sqrt(w_) for w_ in wq]
    return run("rh", [
        (p, [R(1)] * 3, lam, [R(1)] * 3,
         q, [R(1)] * 3, mu, [R(1)] * 3, L5),
        (p, [R(1)] * 3, lam, [R(1)] * 3,
         q, [R(1)] * 3, mu, [R(1)] * 3, DEC1),
    ])


def theorem_3_5iii():
    wp = [R(81, 100), R(36, 100), R(4, 100)]   # psi_p desc
    p = [sp.sqrt(w_) for w_ in wp]
    ith = [R(1), R(7, 5), R(9, 5)]             # asc -> antitone
    wq, idel = chain([wp, ith], [Tswap(R(1, 2), 0, 2, 3)])
    q = [sp.sqrt(w_) for w_ in wq]
    lam = [R(1)] * 3
    return run("rh", [
        (p, [R(1)] * 3, lam, [1 / a_ for a_ in ith],
         q, [R(1)] * 3, lam, [1 / a_ for a_ in idel], DEC1),
    ])


def theorem_3_6i():
    return "SCOPE"


def theorem_3_6ii():
    wp = [R(9, 100), R(25, 100), R(64, 100)]
    p = [sp.sqrt(w_) for w_ in wp]
    lam = [R(1, 5), R(7, 10), R(3, 2)]
    wq, mu = chain([wp, lam],
                   [Tswap(R(3, 5), 0, 1, 3), Tswap(R(3, 5), 1, 2, 3)])
    q = [sp.sqrt(w_) for w_ in wq]
    return run("rh", [
        (p, [R(1)] * 3, lam, [R(1)] * 3,
         q, [R(1)] * 3, mu, [R(1)] * 3, L5),
    ])


def theorem_3_6iii():
    wp = [R(81, 100), R(36, 100), R(4, 100)]
    p = [sp.sqrt(w_) for w_ in wp]
    ith = [R(1), R(7, 5), R(9, 5)]
    wq, idel = chain([wp, ith],
                     [Tswap(R(3, 5), 0, 1, 3), Tswap(R(3, 5), 1, 2, 3)])
    q = [sp.sqrt(w_) for w_ in wq]
    lam = [R(1)] * 3
    return run("rh", [
        (p, [R(1)] * 3, lam, [1 / a_ for a_ in ith],
         q, [R(1)] * 3, lam, [1 / a_ for a_ in idel], DEC1),
        (p, [R(1)] * 3, lam, [1 / a_ for a_ in ith],
         q, [R(1)] * 3, lam, [1 / a_ for a_ in idel], DEC2),
    ])


def corollary_3_1i():
    return theorem_3_2i()


def corollary_3_1ii():
    return theorem_3_2ii()


def corollary_3_2i():
    return "SCOPE"


def corollary_3_2ii():
    return theorem_3_5ii()


def corollary_3_2iii():
    return theorem_3_5iii()


def theorem_4_1():
    """alpha >>w beta (asc partials >=), p desc vs alpha asc (opposite
    ordering); claim U <=st V."""
    alp = [R(1), R(3), R(5)]
    bet = [R(1, 2), R(7, 2), R(4)]
    assert wsup_paper(alp, bet)
    p = [R(9, 10), R(6, 10), R(3, 10)]          # desc vs alp asc
    lam = [R(1)] * 3
    n, wit, und = 0, None, 0
    for th in ([R(1)] * 3, [R(2)] * 3):
        h, w_, u_ = ck("st", p, alp, lam, th, p, bet, lam, th,
                       G, direction="U<=V")
        n += 1; und += u_
        if not h and wit is None:
            wit = w_
    return n, wit, und


def theorem_4_2():
    """shared alpha,theta,lam; psi(p) >>w psi(q); claim U >=st V.
    psi=p^2 convex increasing; all vectors similarly ordered (E+)."""
    wp = [R(25, 100), R(49, 100), R(81, 100)]
    wq = [R(16, 100), R(36, 100), R(64, 100)]
    assert wsup_paper(wp, wq)      # componentwise >= implies it
    p = [sp.sqrt(w_) for w_ in wp]
    q = [sp.sqrt(w_) for w_ in wq]
    lam = [R(1), R(2), R(3)]
    th = [R(1), R(2), R(3)]
    alp = [R(1, 2), R(7, 10), R(9, 10)]
    n, wit, und = 0, None, 0
    for base in (G, MQL):
        h, w_, u_ = ck("st", p, alp, lam, th, q, alp, lam, th, base)
        n += 1; und += u_
        if not h and wit is None:
            wit = w_
    return n, wit, und


def theorem_4_3i():
    """1/th p-larger 1/del <=> asc partial products th <= del;
    alpha<=1 shared, p=q, lam=mu, all vectors similarly ordered."""
    cases = [
        ([R(1), R(3), R(5)], [R(2), R(3), R(6)]),   # asc prod: 1,3,15 <= 2,6,36
        ([R(1), R(2), R(8)], [R(2), R(4), R(4)]),   # 1,2,16 <= 2,8,32
    ]
    n, wit, und = 0, None, 0
    lam = [R(1), R(3, 2), R(2)]
    p = [R(2, 10), R(5, 10), R(8, 10)]
    for th, dl in cases:
        assert plarger_recip(th, dl)
        h, w_, u_ = ck("st", p, [R(1, 2)] * 3, lam, th,
                       p, [R(1, 2)] * 3, lam, dl, DEC1)
        n += 1; und += u_
        if not h and wit is None:
            wit = w_
    return n, wit, und


def theorem_4_3ii():
    return "SCOPE"


def theorem_4_4():
    """lam >>w mu (asc partials >=), all vectors desc (D+), common
    alpha<=1, theta=delta, p=q.  Includes Example 5.1 values."""
    cases = [
        ([R(1), R(5, 2), R(5)], [R(1, 2), R(2), R(3)]),   # Ex 5.1
        ([R(1), R(3), R(6)], [R(1, 2), R(5, 2), R(4)]),
    ]
    n, wit, und = 0, None, 0
    p = [R(2, 10), R(8, 10), R(9, 10)]
    th = [R(2), R(5), R(9)]
    for lam, mu in cases:
        assert wsup_paper(lam, mu)
        h, w_, u_ = ck("st", p, [R(1)] * 3, lam, th,
                       p, [R(1)] * 3, mu, th, DEC1)
        n += 1; und += u_
        if not h and wit is None:
            wit = w_
    return n, wit, und


def theorem_4_5i():
    """all three hetero; 1/th p-larger 1/del + psi_p >>w psi_q + lam >>w mu;
    psi=p^2; all asc."""
    th, dl = [R(1), R(3), R(5)], [R(2), R(3), R(6)]
    lam, mu = [R(1), R(3), R(6)], [R(1, 2), R(5, 2), R(4)]
    wp, wq = [R(25, 100), R(49, 100), R(81, 100)], \
             [R(16, 100), R(36, 100), R(64, 100)]
    assert plarger_recip(th, dl) and wsup_paper(wp, wq) \
        and wsup_paper(lam, mu)
    p = [sp.sqrt(w_) for w_ in wp]
    q = [sp.sqrt(w_) for w_ in wq]
    return run("st", [
        (p, [R(1, 2)] * 3, lam, th, q, [R(1, 2)] * 3, mu, dl, DEC1),
    ])


def theorem_4_5ii():
    """reciprocal majorization on scales + same rest."""
    th, dl = [R(3), R(5), R(7)], [R(2), R(4), R(6)]
    lam, mu = [R(1), R(3), R(6)], [R(1, 2), R(5, 2), R(4)]
    wp, wq = [R(25, 100), R(49, 100), R(81, 100)], \
             [R(16, 100), R(36, 100), R(64, 100)]
    p = [sp.sqrt(w_) for w_ in wp]
    q = [sp.sqrt(w_) for w_ in wq]
    return "SCOPE"


def theorem_4_6():
    """k-th order stat, common scalars lam,th and transformed prob v;
    alpha ordinary-majorizes beta; claim U_{k:n} <=st V_{k:n}.
    n=3, k=2: F_{2:3} = F1F2+F1F3+F2F3 - 2 F1F2F3 (non-identical)."""
    v_ = R(1, 2)
    alp = [R(2), R(4), R(6)]
    bet = [R(3), R(4), R(5)]
    assert sum(alp) == sum(bet) and sorted(alp, reverse=True)[0] >= \
        sorted(bet, reverse=True)[0]

    def df_k2(a_vec, lamv, thv):
        Fs = [v_ * (G((x - lamv) / thv) ** a_) + (1 - v_) for a_ in a_vec]
        # F_{U_i} = 1 - v (1-F^a); above expression = 1 - v(1-F^a) == F_Ui
        return (Fs[0] * Fs[1] + Fs[0] * Fs[2] + Fs[1] * Fs[2]
                - 2 * Fs[0] * Fs[1] * Fs[2])

    FU = df_k2(alp, R(1), R(2))
    FV = df_k2(bet, R(1), R(2))
    DU = Closed(1 - FU, R(1)); DV = Closed(1 - FV, R(1))
    # claim U_{k:n} <=st V_{k:n}
    h, w_, u_ = cf.check("st", DU, DV)
    return 1, w_, u_


def theorem_4_7():
    return "SCOPE"
def theorem_4_7_vacuous():
    """lam >>w mu, alpha=1, p=q, th=del, all asc; baseline MOQL
    (paper: C2-C4)."""
    cases = [
        ([R(1), R(5, 2), R(5)], [R(1, 2), R(2), R(3)]),
        ([R(1), R(3), R(6)], [R(1, 2), R(5, 2), R(4)]),
    ]
    n, wit, und = 0, None, 0
    p = [R(2, 10), R(8, 10), R(9, 10)]
    th = [R(2), R(5), R(9)]
    for lam, mu in cases:
        assert wsup_paper(lam, mu)
        h, w_, u_ = ck("rh", p, [R(1)] * 3, lam, th,
                       p, [R(1)] * 3, mu, th, MQL)
        n += 1; und += u_
        if not h and wit is None:
            wit = w_
    return n, wit, und


def theorem_4_8i():
    """1/th >>w 1/del (asc partials of 1/th >= of 1/del, i.e. asc partials
    th <= del), alpha=1, common lam,p."""
    cases = [
        ([R(1), R(3), R(5)], [R(2), R(3), R(6)]),
        ([R(1), R(2), R(8)], [R(2), R(4), R(4)]),
    ]
    n, wit, und = 0, None, 0
    lam = [R(1), R(3, 2), R(2)]
    p = [R(2, 10), R(5, 10), R(8, 10)]
    for th, dl in cases:
        assert plarger_recip(th, dl)
        h, w_, u_ = ck("rh", p, [R(1)] * 3, lam, th,
                       p, [R(1)] * 3, lam, dl, DEC1)
        n += 1; und += u_
        if not h and wit is None:
            wit = w_
    return n, wit, und


def theorem_4_8ii():
    """1/th >>rm 1/del -- encode componentwise th >= del."""
    cases = [
        ([R(2), R(4), R(6)], [R(1), R(3), R(5)]),
        ([R(3), R(5), R(7)], [R(2), R(4), R(6)]),
    ]
    return "SCOPE"


def theorem_4_9i():
    """componentwise th>=del, lam>=mu, p>=q, alpha=1."""
    return run("rh", [
        ([R(3, 10), R(6, 10), R(9, 10)], [R(1)] * 3,
         [R(1), R(2), R(3)], [R(2), R(3), R(4)],
         [R(2, 10), R(5, 10), R(8, 10)], [R(1)] * 3,
         [R(1, 2), R(1), R(2)], [R(1), R(2), R(3)], DEC1),
        ([R(4, 10), R(7, 10)], [R(1)] * 2,
         [R(1), R(2)], [R(2), R(4)],
         [R(2, 10), R(5, 10)], [R(1)] * 2,
         [R(1, 2), R(3, 2)], [R(1), R(3)], DEC2),
    ])


def theorem_4_9ii():
    """same but common scalar alpha < 1."""
    return run("rh", [
        ([R(3, 10), R(6, 10), R(9, 10)], [R(1, 2)] * 3,
         [R(1), R(2), R(3)], [R(2), R(3), R(4)],
         [R(2, 10), R(5, 10), R(8, 10)], [R(1, 2)] * 3,
         [R(1, 2), R(1), R(2)], [R(1), R(2), R(3)], DEC1),
    ])


def theorem_4_10():
    """alpha<=1 scalar, th=delta, lam=mu, all asc; psi_p >>w psi_q;
    psi=p^2."""
    wp = [R(25, 100), R(49, 100), R(81, 100)]
    wq = [R(16, 100), R(36, 100), R(64, 100)]
    assert wsup_paper(wp, wq)
    p = [sp.sqrt(w_) for w_ in wp]
    q = [sp.sqrt(w_) for w_ in wq]
    lam = [R(1), R(2), R(3)]
    th = [R(1), R(2), R(3)]
    return run("rh", [
        (p, [R(1, 2)] * 3, lam, th, q, [R(1, 2)] * 3, lam, th, DEC1),
    ])


def theorem_4_11i():
    th, dl = [R(1), R(3), R(5)], [R(2), R(3), R(6)]
    lam, mu = [R(1), R(3), R(6)], [R(1, 2), R(5, 2), R(4)]
    wp, wq = [R(25, 100), R(49, 100), R(81, 100)], \
             [R(16, 100), R(36, 100), R(64, 100)]
    p = [sp.sqrt(w_) for w_ in wp]
    q = [sp.sqrt(w_) for w_ in wq]
    return run("rh", [
        (p, [R(1)] * 3, lam, th, q, [R(1)] * 3, mu, dl, DEC1),
    ])


def theorem_4_11ii():
    th, dl = [R(3), R(5), R(7)], [R(2), R(4), R(6)]
    lam, mu = [R(1), R(3), R(6)], [R(1, 2), R(5, 2), R(4)]
    wp, wq = [R(25, 100), R(49, 100), R(81, 100)], \
             [R(16, 100), R(36, 100), R(64, 100)]
    p = [sp.sqrt(w_) for w_ in wp]
    q = [sp.sqrt(w_) for w_ in wq]
    return "SCOPE"


def corollary_5_1():
    return "AMBIG"


def corollary_5_2():
    return "AMBIG"


def corollary_5_3():
    """MO quasi-Lindley, psi=p^2, n=2, theta=delta scalar; Example 5.2
    values: lam=(5,6.1), mu=(5.44,5.66), th=0.01, alpha=0.52,
    psi(p)=(0.2,0.5), psi(q)=(0.32,0.38)."""
    p = [sp.sqrt(R(2, 10)), sp.sqrt(R(1, 2))]
    q = [sp.sqrt(R(32, 100)), sp.sqrt(R(38, 100))]
    return "AMBIG"


def corollary_5_4():
    """MO quasi-Lindley, psi=e^p; Thm 4.11(i) conditions."""
    th, dl = [R(1), R(3), R(5)], [R(2), R(3), R(6)]
    lam, mu = [R(1), R(4), R(7)], [R(2), R(4), R(6)]
    wp = [R(11, 10), R(3, 2), R(2)]      # w = e^p in (1,e)
    wq = [R(6, 5), R(7, 5), R(8, 5)]
    p = [sp.log(w_) for w_ in wp]        # p = ln w
    q = [sp.log(w_) for w_ in wq]
    return "AMBIG"


def example_5_1():
    lam = [R(1), R(5, 2), R(5)]
    mu = [R(1, 2), R(2), R(3)]
    p = [R(2, 10), R(8, 10), R(9, 10)]
    th = [R(2), R(5), R(9)]
    return run("rh", [
        (p, [R(1)] * 3, lam, th, p, [R(1)] * 3, mu, th, G),
    ])


def example_5_2():
    """printed concrete claim U2:2 >=st V2:2 -- tested as stated
    (premise (C1) on MOQL actually fails; the concrete conclusion
    is what is tested)."""
    p = [sp.sqrt(R(2, 10)), sp.sqrt(R(1, 2))]
    q = [sp.sqrt(R(32, 100)), sp.sqrt(R(38, 100))]
    return run("st", [
        (p, [R(52, 100)] * 2, [R(5), R(61, 10)], [R(1, 100)] * 2,
         q, [R(52, 100)] * 2, [R(544, 100), R(566, 100)],
         [R(1, 100)] * 2, MQL),
    ])


def remark_3_1():
    """psi=e^{-p}, common lam=mu scalar; T_{1/2} averaging of
    (psi_p, 1/th) rows. p=(0.5,0.9), 1/th=(0.7,0.6)."""
    p = [R(1, 2), R(9, 10)]
    wp = [sp.exp(-p[0]), sp.exp(-p[1])]
    ith = [R(7, 10), R(6, 10)]
    wq, idel = chain([wp, ith], [Tswap(R(1, 2), 0, 1, 2)])
    q = [-sp.log(w_) for w_ in wq]     # psi^{-1}(w) = -ln w
    lam = [R(9, 10)] * 2
    return run("st", [
        (p, [R(1, 100)] * 2, lam, [1 / a_ for a_ in ith],
         q, [R(1, 100)] * 2, lam, [1 / a_ for a_ in idel], P5),
        (p, [R(1, 2)] * 2, lam, [1 / a_ for a_ in ith],
         q, [R(1, 2)] * 2, lam, [1 / a_ for a_ in idel], G),
    ])


def counterexample_3_1():
    """Paper's instance: F=1-(1+t^5)^{-4}, psi=1-p^3 (violates C10).
    Claim: U2:2 >=st V2:2 FAILS (F-G changes sign)."""
    p = [R(2, 10) ** (R(1) / 3), R(1, 2) ** (R(1) / 3)]
    q = [R(32, 100) ** (R(1) / 3), R(38, 100) ** (R(1) / 3)]
    lam = [R(9, 10)] * 2
    ith = [R(7, 10), R(6, 10)]
    idel = [R(66, 100), R(64, 100)]
    al = [R(1, 100)] * 2
    th = [1 / a_ for a_ in ith]
    dl = [1 / a_ for a_ in idel]
    # claim is failure of st: a witness of check(st, V, U) confirms it
    h, w_, u_ = ck("st", p, al, lam, th, q, al, lam, dl, P5)
    return 1, w_, u_


def counterexample_3_2():
    """psi=-ln p; (psi_p,1/th) not in M2; F-G changes sign."""
    p = [sp.exp(-R(23, 100)), sp.exp(-R(69, 100))]
    q = [sp.exp(-R(644, 1000)), sp.exp(-R(276, 1000))]
    lam = [R(9, 10)] * 2
    th = [1 / R(5, 10), 1 / R(3, 10)]
    dl = [1 / R(32, 100), 1 / R(48, 100)]
    al = [R(1, 100)] * 2
    h, w_, u_ = ck("st", p, al, lam, th, q, al, lam, dl, P5)
    if w_ is None:
        # grid too coarse for the ~1e-5 crossing near t=1.6-1.9;
        # probe the printed witness point directly
        FU = claim_df(p, al, lam, th, P5)
        FV = claim_df(q, al, lam, dl, P5)
        DU = Closed(1 - FU, R(9, 10)); DV = Closed(1 - FV, R(9, 10))
        E = DU.survival - DV.survival     # S_U - S_V; printed F-G>0 -> E<0
        for pt in (R(17, 10), R(18, 10), R(2)):
            for dps in (60, 150, 400):
                cf.iv.dps = dps
                try:
                    vv = cf.iv_eval(E, pt)
                except Exception:
                    continue
                if vv.b < 0:
                    return 1, pt, u_
                break
    return 1, w_, u_


def counterexample_3_3():
    """psi=1-p^2 (violates C9); baseline LOM5; claim U2:2 not >=rh V2:2."""
    p = [sp.sqrt(R(2, 10)), sp.sqrt(R(3, 10))]
    q = [sp.sqrt(R(23, 100)), sp.sqrt(R(27, 100))]
    lam = [R(9, 10), R(6, 10)]
    mu = [R(81, 100), R(69, 100)]
    th = [R(1, 2)] * 2
    al = [R(1)] * 2
    h, w_, u_ = ck("rh", p, al, lam, th, q, al, mu, th, L5)
    return 1, w_, u_


def main():
    canon = json.load(open(os.path.join(
        HERE, "..", "canonical", "doi_10.2298_fil2104315d.json")))
    fn_map = {
        "Theorem 3.1(i)": ("st", theorem_3_1i, "pos"),
        "Theorem 3.1(ii)": ("st", theorem_3_1ii, "pos"),
        "Theorem 3.2(i)": ("st", theorem_3_2i, "pos"),
        "Theorem 3.2(ii)": ("st", theorem_3_2ii, "pos"),
        "Theorem 3.3(i)": ("st", theorem_3_3i, "pos"),
        "Theorem 3.3(ii)": ("st", theorem_3_3ii, "pos"),
        "Theorem 3.4(i)": ("rh", theorem_3_4i, "pos"),
        "Theorem 3.4(ii)": ("rh", theorem_3_4ii, "pos"),
        "Theorem 3.4(iii)": ("rh", theorem_3_4iii, "pos"),
        "Theorem 3.5(i)": ("rh", theorem_3_5i, "pos"),
        "Theorem 3.5(ii)": ("rh", theorem_3_5ii, "pos"),
        "Theorem 3.5(iii)": ("rh", theorem_3_5iii, "pos"),
        "Theorem 3.6(i)": ("rh", theorem_3_6i, "pos"),
        "Theorem 3.6(ii)": ("rh", theorem_3_6ii, "pos"),
        "Theorem 3.6(iii)": ("rh", theorem_3_6iii, "pos"),
        "Corollary 3.1(i)": ("st", corollary_3_1i, "pos"),
        "Corollary 3.1(ii)": ("st", corollary_3_1ii, "pos"),
        "Corollary 3.2(i)": ("rh", corollary_3_2i, "pos"),
        "Corollary 3.2(ii)": ("rh", corollary_3_2ii, "pos"),
        "Corollary 3.2(iii)": ("rh", corollary_3_2iii, "pos"),
        "Theorem 4.1": ("st", theorem_4_1, "pos"),
        "Theorem 4.2": ("st", theorem_4_2, "pos"),
        "Theorem 4.3(i)": ("st", theorem_4_3i, "pos"),
        "Theorem 4.3(ii)": ("st", theorem_4_3ii, "pos"),
        "Theorem 4.4": ("st", theorem_4_4, "pos"),
        "Theorem 4.5(i)": ("st", theorem_4_5i, "pos"),
        "Theorem 4.5(ii)": ("st", theorem_4_5ii, "pos"),
        "Theorem 4.6": ("st", theorem_4_6, "pos"),
        "Theorem 4.7": ("rh", theorem_4_7, "pos"),
        "Theorem 4.8(i)": ("rh", theorem_4_8i, "pos"),
        "Theorem 4.8(ii)": ("rh", theorem_4_8ii, "pos"),
        "Theorem 4.9(i)": ("rh", theorem_4_9i, "pos"),
        "Theorem 4.9(ii)": ("rh", theorem_4_9ii, "pos"),
        "Theorem 4.10": ("rh", theorem_4_10, "pos"),
        "Theorem 4.11(i)": ("rh", theorem_4_11i, "pos"),
        "Theorem 4.11(ii)": ("rh", theorem_4_11ii, "pos"),
        "Corollary 5.1": ("st", corollary_5_1, "pos"),
        "Corollary 5.2": ("rh", corollary_5_2, "pos"),
        "Corollary 5.3": ("st", corollary_5_3, "pos"),
        "Corollary 5.4": ("rh", corollary_5_4, "pos"),
        "Example 5.1": ("rh", example_5_1, "pos"),
        "Example 5.2": ("st", example_5_2, "pos"),
        "Remark 3.1": ("st", remark_3_1, "pos"),
        "Remark 3.1 (lower bound application of Theorem 3.1(ii))":
            ("st", remark_3_1, "pos"),
        "Counterexample 3.1": ("st", counterexample_3_1, "neg"),
        "Counterexample 3.2": ("st", counterexample_3_2, "neg"),
        "Counterexample 3.3": ("rh", counterexample_3_3, "neg"),
    }
    results = []
    for recd in canon:
        order = recd["conclusion"]["order"]
        label = recd["claim"]
        if label not in fn_map:
            results.append(rec(recd, "unsupported order" if order not in
                               ("st", "hr", "rh", "lr")
                               else "out of harness scope"))
            continue
        _, fn, sense = fn_map[label]
        out_ = fn()
        if out_ == "SCOPE":
            results.append(rec(recd, "out of harness scope"))
            continue
        if out_ == "AMBIG":
            results.append(rec(recd, "ambiguous hypotheses"))
            continue
        n_, w, u = out_
        if sense == "pos":
            results.append(rec(recd, "holds" if w is None else "refuted",
                               instances=n_, witness=w, undecided=u))
        else:  # negative claim: a witness confirms it
            results.append(rec(recd, "holds" if w is not None else "refuted",
                               instances=n_, witness=w, undecided=u))
    out = os.path.join(
        HERE, "eval_doi_10.2298_fil2104315d.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"],
              "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
