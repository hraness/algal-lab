"""Evaluator for arXiv:2503.21275 ("Errors due to departure from independence
in series/parallel systems" — Bhattacharjee & co.).

Reads canonical/arxiv_2503.21275.json and produces
harness/eval_arxiv_2503.21275.result.json.

The paper's dependent-vs-independent comparisons are expressed as closed-form
survival functions F̄_D(t) / F̄_I(t) for each multivariate family (MOME, MGI,
MOMW, multivariate Lee, Lu-Bhattacharyya-I/Crowder, FGMW), so every st/hr/rh/lr
claim is checkable directly by closedform.check on the printed system
survivals.  Sign-of-relative-error claims are evaluated on the same scaled
rational grid via closedform.iv_eval (an interval enclosure strictly on the
wrong side is a rigorous refutation witness; 'holds' means survived bounded
testing, never proved).

Unsupported orders (mrl, ageing: AI, ageing: AF) are recorded as
'unsupported order' without testing.
"""

import json
import os

import sympy as sp
from mpmath import iv

import closedform as cf
from closedform import x

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "arxiv_2503.21275.json")
OUT = os.path.join(HERE, "eval_arxiv_2503.21275.result.json")

t = x  # time symbol used by closedform


# ----------------------------------------------------------------------------
# harness helpers
# ----------------------------------------------------------------------------

def closed(surv, hi=sp.oo):
    return cf.Closed(surv, hi=hi)


def order_check(order, SA, SB, hi=sp.oo):
    """closedform check of `SA <=order SB` on t in (0, hi)."""
    return cf.check(order, closed(SA, hi), closed(SB, hi))


def expr_geq(expr, hi=sp.oo, survivals=()):
    """Is expr >= 0 at every grid point in (0, hi)?  Same discipline as
    closedform.check: increasing iv precision, strict negative enclosure is a
    rigorous witness, stragglers are undecided."""
    survs = list(survivals) or [expr]
    pts = cf.grid(0, hi, survs)
    undecided = 0
    for prec in (60, 150, 400):
        iv.dps = prec
        pending = []
        for pt in pts:
            try:
                e = cf.iv_eval(expr, pt)
            except (ValueError, ZeroDivisionError):
                undecided += 1
                continue
            if e.b < 0:                      # strict negative enclosure
                return False, pt, undecided
            if not (e.a >= 0):
                pending.append(pt)
        if not pending:
            return True, None, undecided
        pts = pending
    return True, None, undecided + len(pending)


def wjson(w):
    """Witness to JSON: exact rational string when available."""
    if w is None:
        return None
    if isinstance(w, sp.Rational):
        return f"t = {w.p}/{w.q} (~{float(w):.6g})"
    return str(w)


def combine(results):
    """results: list of dicts {holds, witness, undecided}.  One record per
    claim is produced at the end; a single strict refutation suffices."""
    holds = True
    witness = None
    undec = 0
    for r in results:
        undec += r["undecided"]
        if not r["holds"]:
            holds = False
            if witness is None:
                witness = wjson(r["witness"])
    return {"holds": holds, "witness": witness, "undecided": undec,
            "instances": len(results)}


def oc(order, SA, SB, hi=sp.oo):
    h, w, u = order_check(order, SA, SB, hi=hi)
    return {"holds": h, "witness": w, "undecided": u}


def sg(expr, hi=sp.oo, survivals=()):
    h, w, u = expr_geq(expr, hi=hi, survivals=survivals)
    return {"holds": h, "witness": w, "undecided": u}


# ----------------------------------------------------------------------------
# model builders (all survivals as sympy expressions in t)
# ----------------------------------------------------------------------------

def mome_series(lams, joint_rates):
    """MOME series: F̄_D = exp(-(sum lams + sum joint_rates) t),
    F̄_I = exp(-(sum lams) t)   [paper's lambda_i marginal convention]."""
    lamD = sum(lams) + sum(joint_rates)
    lamI = sum(lams)
    return sp.exp(-R(lamD) * t), sp.exp(-R(lamI) * t)


def mgi_series(a):
    """MGI: F̄_D = exp(-sum a_k t^k), F̄_I = exp(-a_1 t), a_k >= 0."""
    expo = sum(R(ak) * t ** i for i, ak in enumerate(a, start=1))
    return sp.exp(-expo), sp.exp(-R(a[0]) * t)


def momw_series(lams, alphas, pair_rates_list, triple_rate=R(0)):
    """MOMW: F̄_D = exp(-(sum lam_i t^al_i + B(t))) with B the interaction sum,
    F̄_I = exp(-sum lam_i t^al_i). pair_rates_list: [(i, j, rate)]."""
    base = sum(R(l) * t ** R(a) for l, a in zip(lams, alphas))
    B = sp.Integer(0)
    n = len(lams)
    for (i, j, r_) in pair_rates_list:
        B += R(r_) * t ** max(alphas[i], alphas[j])
    if triple_rate and n >= 3:
        B += triple_rate * t ** max(alphas)
    return sp.exp(-(base + B)), sp.exp(-base)


def lee_series(lamL, mu, alpha):
    """Multivariate Lee, common alpha: F̄_D = exp(-lamL t^alpha),
    F̄_I = exp(-mu t^alpha), lamL >= mu."""
    return sp.exp(-R(lamL) * t ** R(alpha)), sp.exp(-R(mu) * t ** R(alpha))


def crowder_series(lams, alphas, m, delta):
    """LB-I / Crowder series survival from the printed joint SF:
    F̄_D = exp(-sum lam_i t^al_i + delta * (sum lam_i^(1/m) t^(al_i/m))^m),
    F̄_I = exp(-sum lam_i t^al_i)."""
    base = sum(R(l) * t ** R(a) for l, a in zip(lams, alphas))
    inner = sum(R(l) ** R(1, m) * t ** (R(a) / m) for l, a in zip(lams, alphas))
    return sp.exp(-base + R(delta) * inner ** R(m)), sp.exp(-base)


def fgmw_series(lams, alphas, gamma):
    """FGMW series: F̄_D = prod(S_i) * (1 + gamma * prod(1 - S_i)),
    S_i = exp(-lam_i t^alpha_i); F̄_I = prod(S_i)."""
    S = [sp.exp(-R(l) * t ** R(a)) for l, a in zip(lams, alphas)]
    prodS = sp.Integer(1)
    prodC = sp.Integer(1)
    for s_i in S:
        prodS *= s_i
        prodC *= (1 - s_i)
    return sp.expand(prodS * (1 + R(gamma) * prodC)), sp.expand(prodS)


def fgmw_parallel(lams, alphas, gamma):
    """FGMW parallel as printed in 4.3.2:
    F̄_D^P = theta + (-1)^{n-1} prod(S_i) * gamma * prod(1 - S_i),
    F̄_I^P = theta = 1 - prod(1 - S_i)."""
    S = [sp.exp(-R(l) * t ** R(a)) for l, a in zip(lams, alphas)]
    prodS = sp.Integer(1)
    prodC = sp.Integer(1)
    for s_i in S:
        prodS *= s_i
        prodC *= (1 - s_i)
    theta = 1 - prodC
    n = len(lams)
    SDp = theta + (-1) ** (n - 1) * prodS * R(gamma) * prodC
    return sp.expand(SDp), sp.expand(theta)


def fgm2(gamma, lams=(1, 1), alphas=(1, 1)):
    """Two-component FGM with true marginals for Prop 2.1/2.2 tests.
    Returns (S_joint_diag, prod_Smarg, S_dep_par, S_ind_par)."""
    S = [sp.exp(-R(l) * t ** R(a)) for l, a in zip(lams, alphas)]
    S1, S2 = S
    Sjoint = S1 * S2 * (1 + R(gamma) * (1 - S1) * (1 - S2))
    prodS = S1 * S2
    Fjoint = (1 - S1) * (1 - S2) * (1 + R(gamma) * S1 * S2)
    SDpar = 1 - Fjoint
    SIpar = 1 - (1 - S1) * (1 - S2)
    return sp.expand(Sjoint), sp.expand(prodS), sp.expand(SDpar), sp.expand(SIpar)


def weib(lam, k):
    return sp.exp(-R(lam) * t ** R(k))


def expo(lam):
    return sp.exp(-R(lam) * t)


# ----------------------------------------------------------------------------
# per-claim tests
# ----------------------------------------------------------------------------

def test_corollary_21():
    """ESr <= (>=) 0 on [0, t0]  =>  ESF >= (<=) 0 on [0, t0].
    For each instance we (1) verify the premise on (0, t0] via the hr check and
    (2) check the concluded st direction on (0, t0]."""
    res = []
    # (a) r_D = 2t <= 1 = r_I on (0, 1/2]; premise ESr<=0; predict ESF>=0.
    SD, SI, t0 = weib(1, 2), expo(1), R(1, 2)
    prem = cf.check("hr", closed(SI, t0), closed(SD, t0))     # r_D<=r_I ?
    assert prem[0], "premise instance (a) does not satisfy ESr<=0 on (0,1/2]"
    res.append(oc("st", SI, SD, hi=t0))                      # ESF>=0 ?
    # (b) r_D = 1 <= 1/(2 sqrt t) = r_I on (0, 1/4]; predict ESF>=0.
    SD, SI, t0 = expo(1), weib(1, R(1, 2)), R(1, 4)
    prem = cf.check("hr", closed(SI, t0), closed(SD, t0))
    assert prem[0], "premise instance (b) does not satisfy ESr<=0 on (0,1/4]"
    res.append(oc("st", SI, SD, hi=t0))
    # (c) ESr>=0 on (0,1/2]: r_D = 2t >= 8 t^3 = r_I; predict ESF<=0.
    SD, SI, t0 = weib(1, 2), weib(2, 4), R(1, 2)
    prem = cf.check("hr", closed(SD, t0), closed(SI, t0))     # r_D>=r_I ?
    assert prem[0], "premise instance (c) does not satisfy ESr>=0 on (0,1/2]"
    res.append(oc("st", SD, SI, hi=t0))                      # ESF<=0 ?
    return combine(res)


def test_prop_22():
    """n = 2: sign(E^F_series) = -sign(E^F_parallel), i.e. product <= 0."""
    res = []
    # FGM-2, gamma = +1/2 and -1/2
    for gam in (R(1, 2), R(-1, 2)):
        Sjoint, prodS, SDpar, SIpar = fgm2(gam)
        Dser = Sjoint - prodS
        Dpar = SDpar - SIpar
        res.append(sg(-(Dser * Dpar), survivals=[Sjoint, prodS, SDpar]))
    # MOME-2 with true marginals: S_joint = exp(-(l1+l2+l12) t),
    # marginals exp(-(l_i + l12) t).
    l1, l2, l12 = R(1), R(1), R(1, 2)
    Sjoint = expo(l1 + l2 + l12)
    prodS = expo(l1 + l12) * expo(l2 + l12)          # exp(-3t)
    # parallel: S^P(t) = 1 - F_joint(t,t);  F_joint = 1 - S1 - S2 + S_joint
    SDpar = expo(l1 + l12) + expo(l2 + l12) - Sjoint  # 2 e^{-1.5t} - e^{-2.5t}
    SIpar = 2 * expo(l1 + l12) - prodS                # 2 e^{-1.5t} - e^{-3t}
    Dser = Sjoint - prodS
    Dpar = SDpar - SIpar
    res.append(sg(-(Dser * Dpar), survivals=[Sjoint, prodS, SDpar]))
    return combine(res)


def test_prop_23():
    """ESr one-sided on [0, inf) => same-direction ESF sign on [0, inf)."""
    res = []
    # (a) Exp(1) vs Exp(2): r_D=1 <= r_I=2 => ESF>=0.
    SD, SI = expo(1), expo(2)
    prem = order_check("hr", SI, SD)
    assert prem[0]
    res.append(oc("st", SI, SD))
    # (b) Exp(2) vs Exp(1): ESr>=0 => ESF<=0.
    SD, SI = expo(2), expo(1)
    prem = order_check("hr", SD, SI)
    assert prem[0]
    res.append(oc("st", SD, SI))
    # (c) Weibull(1,2) vs Weibull(2,2): 2t <= 4t => ESF>=0.
    SD, SI = weib(1, 2), weib(2, 2)
    prem = order_check("hr", SI, SD)
    assert prem[0]
    res.append(oc("st", SI, SD))
    # (d) Weibull(2,2) vs Weibull(1,2): ESr>=0 => ESF<=0.
    SD, SI = weib(2, 2), weib(1, 2)
    prem = order_check("hr", SD, SI)
    assert prem[0]
    res.append(oc("st", SD, SI))
    return combine(res)


def test_remark_st():
    """TD <=st (>=st) TI  iff  OA (UA) in SF: error sign <-> order check
    consistency at every grid point (the iff is definitional)."""
    res = []
    # MOME-2: TD <=st TI strictly, ESF<0 (OA): sign(SI - SD) >= 0 must hold.
    SD, SI = mome_series([1, 1], [R(1, 2)])
    res.append(sg(SI - SD, survivals=[SD, SI]))
    # FGM-2 gamma=+1/2: TD >=st TI, UA: sign(SD - SI) >= 0.
    SD, SI, _, _ = fgm2(R(1, 2))
    res.append(sg(SD - SI, survivals=[SD, SI]))
    # FGM-2 gamma=-1/2: TD <=st TI, OA.
    SD, SI, _, _ = fgm2(R(-1, 2))
    res.append(sg(SI - SD, survivals=[SD, SI]))
    return combine(res)


def test_remark_hr():
    """TD <=fr TI iff UA in FR: sign(r_D - r_I) consistency (definitional)."""
    res = []
    # MOME-2: r_D = 5/2 >= 2 = r_I: UA in FR <=> TD <=fr TI.
    SD, SI = mome_series([1, 1], [R(1, 2)])
    res.append(oc("hr", SD, SI))
    # FGM-2 gamma=+1/2: r_D <= r_I (OA in FR) <=> TD >=fr TI.
    SD, SI, _, _ = fgm2(R(1, 2))
    res.append(oc("hr", SI, SD))
    # FGM-2 gamma=-1/2: r_D >= r_I (UA) <=> TD <=fr TI.
    SD, SI, _, _ = fgm2(R(-1, 2))
    res.append(oc("hr", SD, SI))
    return combine(res)


def test_remark_rh():
    """TD <=rfr TI iff OA in RFR: mu_D <= mu_I <-> rh order (definitional);
    exercised on dependent/independent model pairs."""
    res = []
    # MOME-2: mu_D = l_D/(exp(l_D t)-1) <= mu_I <=> TD <=rfr TI.
    for lams, joints in [([1, 1], [R(1, 2)]),
                         ([1, 1, 1], [R(1, 4), R(1, 8), R(1, 8), R(1, 16)])]:
        SD, SI = mome_series(lams, joints)
        res.append(oc("rh", SD, SI))
    # Weibull(2,2) vs Weibull(1,2): mu_D <= mu_I too.
    res.append(oc("rh", weib(2, 2), weib(1, 2)))
    return combine(res)


def mome_family(order):
    res = []
    for lams, joints in [([1, 1], [R(1, 2)]),
                         ([1, 1, 1], [R(1, 4), R(1, 8), R(1, 8), R(1, 16)])]:
        SD, SI = mome_series(lams, joints)
        res.append(oc(order, SD, SI))
    return res


def mgi_family(order):
    res = []
    for a in ([R(1), R(1, 2), R(1, 4)], [R(2), R(1), R(1, 2)]):
        SD, SI = mgi_series(a)
        res.append(oc(order, SD, SI))
    return res


def momw_family(order):
    res = []
    SD, SI = momw_series([1, 1], [1, 2], [(0, 1, R(1, 2))])
    res.append(oc(order, SD, SI))
    SD, SI = momw_series([1, 1, 1], [1, 2, 2],
                         [(0, 1, R(1, 2)), (0, 2, R(1, 4))],
                         triple_rate=R(1, 8))
    res.append(oc(order, SD, SI))
    return res


def lee_family(order):
    res = []
    SD, SI = lee_series(R(5, 2), 2, 2)     # alpha=2
    res.append(oc(order, SD, SI))
    SD, SI = lee_series(R(7, 2), 3, R(1, 2))  # alpha=1/2
    res.append(oc(order, SD, SI))
    return res


def test_crowder_st():
    """sign(E^F) = sign(delta): delta>0 => TD >=st TI ; delta<0 => TD <=st TI."""
    res = []
    SDp, SI = crowder_series([1, 1], [1, 1], 2, R(1, 4))   # exp(-t) vs exp(-2t)
    res.append(oc("st", SI, SDp))                          # UA
    SDn, SI = crowder_series([1, 1], [1, 1], 2, R(-1, 4))  # exp(-3t)
    res.append(oc("st", SDn, SI))                          # OA
    SDp, SI = crowder_series([1, 1], [2, 2], 2, R(1, 8))   # exp(-3t^2/2)
    res.append(oc("st", SI, SDp))
    SDn, SI = crowder_series([1, 1], [2, 2], 2, R(-1, 8))  # exp(-5t^2/2)
    res.append(oc("st", SDn, SI))
    return combine(res)


def test_fgmw_series_sf():
    """sign(E^F) = sign(gamma); printed bound E^F <= gamma when gamma > 0
    (and E^F >= gamma when gamma < 0)."""
    res = []
    for lams, gam in [([1, 1], R(1, 2)), ([1, 1], R(-1, 2)),
                      ([1, 2], R(1, 3)), ([1, 2], R(-1, 3)),
                      ([1, 1], R(1, 4))]:
        SD, SI = fgmw_series(lams, [1] * len(lams), gam)
        if gam > 0:
            res.append(oc("st", SI, SD))        # UA
        else:
            res.append(oc("st", SD, SI))        # OA
        # printed bound E^F <=(>=) gamma for gamma >=(<=) 0:
        # E^F = gamma*prod(1-S_i); gamma>0: gamma - E^F >= 0 ;
        # gamma<0: E^F - gamma >= 0.
        S = [sp.exp(-R(l) * t) for l in lams]
        prodC = sp.Integer(1)
        for s_i in S:
            prodC *= (1 - s_i)
        if gam > 0:
            res.append(sg(gam - gam * prodC, survivals=[SD, SI]))
        else:
            res.append(sg(gam * prodC - gam, survivals=[SD, SI]))
    return combine(res)


def test_fgmw_series_fr():
    """sign(E^r) = -sign(gamma): gamma>0 => r_D<=r_I (TD>=fr TI);
    gamma<0 => r_D>=r_I (TD<=fr TI)."""
    res = []
    for lams, gam in [([1, 1], R(1, 2)), ([1, 1], R(-1, 2)),
                      ([1, 2], R(1, 3)), ([1, 2], R(-1, 3))]:
        SD, SI = fgmw_series(lams, [1] * len(lams), gam)
        if gam > 0:
            res.append(oc("hr", SI, SD))        # TI <=hr TD
        else:
            res.append(oc("hr", SD, SI))
    return combine(res)


FGMW_PAR_INSTANCES = [
    # (n, gamma)
    (2, R(1, 2)), (2, R(-1, 2)), (3, R(1, 2)), (3, R(-1, 2)),
]


def _fgmw_par(n, gam):
    return fgmw_parallel([1] * n, [1] * n, gam)


def test_fgmw_par_sf():
    """E^F >= 0 iff gamma*(-1)^{n-1} >= 0  (UA <=> TD >=st TI)."""
    res = []
    for n, gam in FGMW_PAR_INSTANCES:
        SDp, SIp = _fgmw_par(n, gam)
        pos = (gam > 0) == (n % 2 == 1)         # sign(gamma)*(-1)^{n-1} >= 0
        if pos:
            res.append(oc("st", SIp, SDp))      # UA: TD >=st TI
        else:
            res.append(oc("st", SDp, SIp))      # OA: TD <=st TI
    return combine(res)


def test_fgmw_par_fr():
    """E^r <= 0 (r_D <= r_I, TD >=fr TI) iff (gamma>0 & n odd) or
    (gamma<0 & n even); complementary cases give r_D >= r_I (TD <=fr TI)."""
    res = []
    for n, gam in FGMW_PAR_INSTANCES:
        SDp, SIp = _fgmw_par(n, gam)
        leq = ((gam > 0) and (n % 2 == 1)) or ((gam < 0) and (n % 2 == 0))
        if leq:
            res.append(oc("hr", SIp, SDp))      # r_D <= r_I
        else:
            res.append(oc("hr", SDp, SIp))
    return combine(res)


def test_fgmw_par_rh():
    """E^mu <= 0 (mu_D <= mu_I) iff (gamma>0 & n even) or (gamma<0 & n odd);
    complementary cases give mu_D >= mu_I."""
    res = []
    for n, gam in FGMW_PAR_INSTANCES:
        SDp, SIp = _fgmw_par(n, gam)
        leq = ((gam > 0) and (n % 2 == 0)) or ((gam < 0) and (n % 2 == 1))
        if leq:
            res.append(oc("rh", SDp, SIp))      # mu_D <= mu_I
        else:
            res.append(oc("rh", SIp, SDp))
    return combine(res)


def test_prop_21():
    """Orthant-dependence sign <-> SF-error sign for series and parallel.
    For n=2 the PUOD deviation S_joint - prod S_i IS the series error
    numerator, and S_Dp - S_Ip = -(F_joint - F1 F2) = -(S_joint - prod S_i).
    Verified pairing (canonical direction field): PUOD <=> ESF >= 0 (UA) for
    series; PLOD <=> EPF <= 0 (OA) for parallel.  The printed series pairing
    'OA <-> PUOD' is reversed, as flagged by canonical ambiguity."""
    res = []
    for gam in (R(1, 2), R(-1, 2)):
        Sjoint, prodS, SDpar, SIpar = fgm2(gam)
        # series: PUOD iff E^F >= 0 (UA) -- same expression, so check the
        # asserted sign on the grid.
        dev = Sjoint - prodS                      # sign = orthant-dep sign
        if gam > 0:
            res.append(sg(dev, survivals=[Sjoint, prodS]))     # PUOD -> UA
        else:
            res.append(sg(-dev, survivals=[Sjoint, prodS]))    # NUOD -> OA
        # parallel: PLOD iff EPF <= 0 (OA): EPF_num = -dev.
        res.append(sg(-(dev * (SDpar - SIpar)), survivals=[Sjoint, prodS]))
    # MOME-2 with true marginals: PUOD deviation >= 0 and series UA match.
    l12 = R(1, 2)
    Sjoint = expo(2 + l12)                    # exp(-5t/2)
    prodS = expo(1 + l12) * expo(1 + l12)     # exp(-3t) true-marginal product
    res.append(sg(Sjoint - prodS, survivals=[Sjoint, prodS]))
    return combine(res)


# ----------------------------------------------------------------------------
# dispatch
# ----------------------------------------------------------------------------

TESTS = {
    "Corollary 2.1": test_corollary_21,
    "Proposition 2.2": test_prop_22,
    "Proposition 2.3": test_prop_23,
    "Remark 2.2(i) — usual stochastic order equivalence": test_remark_st,
    "Remark 2.2(i) — FR order equivalence": test_remark_hr,
    "Remark 2.2(i) — RFR order equivalence": test_remark_rh,
    "Section 3.1.2 result — FR order (MOME series system)":
        lambda: combine(mome_family("hr")),
    "Section 3.1.2 result — LR ordering (MOME series system)":
        lambda: combine(mome_family("lr")),
    "Section 3.1.2 result — RFR order (MOME series system)":
        lambda: combine(mome_family("rh")),
    "Section 3.1.2 result — ST order (MOME series system)":
        lambda: combine(mome_family("st")),
    "Section 3.1.3 result — FR order (MGI series system)":
        lambda: combine(mgi_family("hr")),
    "Section 3.1.3 result — ST order (MGI series system)":
        lambda: combine(mgi_family("st")),
    "Section 3.2.2 result — FR order (MOMW series system)":
        lambda: combine(momw_family("hr")),
    "Section 3.2.2 result — ST order (MOMW series system)":
        lambda: combine(momw_family("st")),
    "Section 3.2.4 result — lr order (multivariate Lee series system)":
        lambda: combine(lee_family("lr")),
    "Section 3.2.4 result — hr order (multivariate Lee series system)":
        lambda: combine(lee_family("hr")),
    "Section 3.2.4 result — st order (multivariate Lee series system)":
        lambda: combine(lee_family("st")),
    "Section 3.2.4 result — rhr order (multivariate Lee series system)":
        lambda: combine(lee_family("rh")),
    "Section 3.2.5 result — error signs (Lu–Bhattacharyya I / Crowder-type series system)":
        test_crowder_st,
    "Section 3.2.6 result — SF error sign (FGMW series system)":
        test_fgmw_series_sf,
    "Section 3.2.6 result — FR error sign (FGMW series system)":
        test_fgmw_series_fr,
    "Section 4.3.2 result — SF error sign (FGMW parallel system)":
        test_fgmw_par_sf,
    "Section 4.3.2 result — FR error sign (FGMW parallel system)":
        test_fgmw_par_fr,
    "Section 4.3.2 result — RFR error sign (FGMW parallel system)":
        test_fgmw_par_rh,
    "Proposition 2.1": test_prop_21,
    "Section 3.2.5 result: error signs for Crowder/Lu-Bhattacharyya-I series system":
        test_crowder_st,
    "Section 3.2.6 result: error signs for FGMW series system":
        test_fgmw_series_sf,
    "Section 4.3.2 result: error signs for FGMW parallel system":
        test_fgmw_par_sf,
}

NOTES = {
    "Proposition 2.1": ("Series half verified with the mathematically correct "
                        "pairing: PUOD <=> ESF>=0 (UA), matching the canonical "
                        "direction field. The printed 'OA(UA) <-> PUOD(NUOD)' "
                        "pairing is reversed relative to this; parallel half "
                        "(OA <-> PLOD) verified as printed."),
    "Section 3.2.5 result — error signs (Lu–Bhattacharyya I / Crowder-type series system)":
        ("Encoded F̄_D = exp(-Σλ_i t^αi + δ(Σλ_i^{1/m} t^{αi/m})^m) per the "
         "printed joint SF (δ>0 shrinks the exponent only through the w(t) "
         "term); valid parameter window δ(Σλ^{1/m})^m <= Σλ respected."),
}


def main():
    records = json.load(open(CANON))
    out = []
    for rec in records:
        label = rec["claim"]
        order = rec["conclusion"]["order"]
        entry = {"claim": label, "order": order}
        if order not in ("st", "hr", "rh", "lr"):
            entry.update({"status": "unsupported order", "instances": 0,
                          "witness": None, "undecided_points": 0})
        elif label in TESTS:
            r = TESTS[label]()
            entry.update({"status": "holds" if r["holds"] else "refuted",
                          "instances": r["instances"],
                          "witness": r["witness"],
                          "undecided_points": r["undecided"]})
        else:
            entry.update({"status": "out of harness scope", "instances": 0,
                          "witness": None, "undecided_points": 0})
        if label in NOTES:
            entry["note"] = NOTES[label]
        out.append(entry)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    for e in out:
        print(f'{e["status"]:22} {e["order"]:10} {e["claim"][:70]}')
    print("wrote", OUT)


if __name__ == "__main__":
    main()
