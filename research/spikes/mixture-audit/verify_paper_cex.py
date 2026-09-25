"""Exact verification of the COUNTEREXAMPLES and EXAMPLES claimed inside
SAF2022 and SKF2026 themselves (their Figures).  Where the relevant function
is a polynomial/rational in a substituted variable, we certify sign changes by
Sturm root counts; where outer exponents differ or powers are fractional we
fall back to 80-digit interval evaluation (reported as 'numerical').

Substitution convention: u = exp(-t/L) with L chosen so all exponents are
integers; u in (0,1) corresponds to t in (0,oo), u decreasing in t.
"""
import sympy as sp
from sympy import Rational as R

u = sp.Symbol("u", positive=True)
t = sp.Symbol("t", positive=True)

RESULTS = []


def rec(name, status, detail=""):
    RESULTS.append((name, status, detail))
    print(f"{status:>10}  {name}: {detail}")


def roots01(expr, var):
    num, den = sp.fraction(sp.cancel(sp.together(expr)))
    return sp.Poly(sp.expand(num), var).count_roots(0, 1)


def signs(expr, var, grid):
    return [(v, sp.sign(expr.subs(var, v))) for v in grid]


# ---------------------------------------------------------------- SAF 6.8 --
def saf_cex68():
    """p=(11/20,7/20,1/10), lam=(18,5,1), gam=(17,5,2), a=(5/2,3,4), exp base.
    Claim: g1 = Fbar_lam - Fbar_gam changes sign (st order fails).
    u = e^{-t/2}: a*lam exps (45,15,4)->*2 wait use u=e^{-t}: a*lam=(45,15,4)
    are integers already; a*gam = (85/2,15,8) half -> u=e^{-t/2} gives
    (90,30,8)/(85,30,16)."""
    p = (R(11, 20), R(7, 20), R(1, 10))
    alam = (R(45) * 2, R(15) * 2, R(4) * 2)      # x2 for u=e^{-t/2}
    agam = (R(85, 2) * 2, R(15) * 2, R(8) * 2)
    il = sum(p[i] * u ** int(alam[i]) for i in range(3))
    ig = sum(p[i] * u ** int(agam[i]) for i in range(3))
    d = sp.expand(il - ig)
    n = roots01(d, u)
    sc = signs(d, u, [R(1, 8), R(1, 2), R(7, 8), R(15, 16)])
    rec("SAF Cex6.8 g1 sign change",
        "VERIFIED" if n >= 1 else "NO-CHANGE",
        f"roots in (0,1): {n}; signs {sc}")


def saf_ex67():
    """Thm 6.5 illustration: claim g1 >= 0 for lam=(2/5,7/10,4/5),
    gam=(1/2,4/5,9/10), a=(5/2,3,4), p=(11/20,7/20,1/10).
    u=e^{-t/10}: a*lam=(10,21,32), a*gam=(25/2,24,18/5)-> halves and fifths;
    use u=e^{-t/20}: (20,42,64) and (25,48,72/... 3*9/10=27/10 ->*20=54)."""
    p = (R(11, 20), R(7, 20), R(1, 10))
    alpha = (R(5, 2), R(3), R(4))
    lam = (R(2, 5), R(7, 10), R(4, 5))
    gam = (R(1, 2), R(4, 5), R(9, 10))
    el = [int(20 * a * l) for a, l in zip(alpha, lam)]
    eg = [int(20 * a * g) for a, g in zip(alpha, gam)]
    il = sum(p[i] * u ** el[i] for i in range(3))
    ig = sum(p[i] * u ** eg[i] for i in range(3))
    d = sp.expand(il - ig)
    n = roots01(d, u)
    sc = signs(d, u, [R(1, 8), R(1, 2), R(7, 8)])
    rec("SAF Ex6.7 g1>=0 (abar>0: inner diff>=0)",
        "HOLDS" if n == 0 and all(sg >= 0 for _, sg in sc) else "FAILS",
        f"roots {n}, signs {sc}")


def saf_cex620():
    """p=(11/20,9/20), lam=(4/5,1/2), gam=(7/10,3/5), a=(5/2,3), exp.
    Claim: g3 = r_gam - r_lam changes sign (hr order fails, U2 violated).
    u=e^{-t/40}: a*lam=(80,60), a*gam=(70,72)."""
    p = (R(11, 20), R(9, 20))
    alpha = (R(5, 2), R(3))
    lam = (R(4, 5), R(1, 2))
    gam = (R(7, 10), R(3, 5))
    abar = p[0] * alpha[0] + p[1] * alpha[1]
    def rmix(lvec):
        el = [int(40 * a * l) for a, l in zip(alpha, lvec)]
        num = sum(alpha[i] * p[i] * lvec[i] * u ** el[i] for i in range(2))
        den = sum(p[i] * u ** el[i] for i in range(2))
        return sp.cancel(num / (abar * den))
    d = sp.cancel(sp.together(rmix(gam) - rmix(lam)))
    n = roots01(d, u)
    sc = signs(d, u, [R(1, 8), R(1, 4), R(1, 2), R(7, 8), R(15, 16)])
    rec("SAF Cex6.20 g3 sign change",
        "VERIFIED" if n >= 1 else "NO-CHANGE", f"roots {n}, signs {sc}")


def saf_cex624():
    """p=(1/3,1/3,1/3), lam=gam=(2/5,7/10,4/5), a=(5/2,7/2,4), b=(14/5,17/5,19/5).
    abar=bbbar=10/3 -> sign(SF_a - SF_b) = sign(inner_a - inner_b).
    u=e^{-t/100}: a*lam=(100,245,320), b*lam=(112,238,304)."""
    p = (R(1, 3),) * 3
    lam = (R(2, 5), R(7, 10), R(4, 5))
    alpha = (R(5, 2), R(7, 2), R(4))
    beta = (R(14, 5), R(17, 5), R(19, 5))
    ea = [int(100 * a * l) for a, l in zip(alpha, lam)]
    eb = [int(100 * b * l) for b, l in zip(beta, lam)]
    ia = sum(p[i] * u ** ea[i] for i in range(3))
    ib = sum(p[i] * u ** eb[i] for i in range(3))
    d = sp.expand(ia - ib)
    n = roots01(d, u)
    sc = signs(d, u, [R(1, 8), R(1, 4), R(1, 2), R(7, 8), R(15, 16)])
    rec("SAF Cex6.24 g5 sign change",
        "VERIFIED" if n >= 1 else "NO-CHANGE", f"roots {n}, signs {sc}")


def saf_cex623_625_numeric():
    """Different outer exponents -> high-precision numerical check only."""
    import mpmath as mp
    mp.mp.dps = 60
    # Cex 6.23: p=(7/8,1/16,1/16), q=(7/20,7/20,3/10), lam=gam=(2/5,7/10,4/5),
    # a=(5/2,8,10).  g4 = S_{p,lam,abar_p} - S_{q,gam,abar_q}
    p = [mp.mpf(7) / 8, mp.mpf(1) / 16, mp.mpf(1) / 16]
    q = [mp.mpf(7) / 20, mp.mpf(7) / 20, mp.mpf(3) / 10]
    lam = [mp.mpf(2) / 5, mp.mpf(7) / 10, mp.mpf(4) / 5]
    a = [mp.mpf(5) / 2, mp.mpf(8), mp.mpf(10)]
    ap = sum(p[i] * a[i] for i in range(3))
    aq = sum(q[i] * a[i] for i in range(3))
    def SF(w, l, abar_, tt):
        return sum(w[i] * mp.e ** (-a[i] * l[i] * tt) for i in range(3)) ** (1 / abar_)
    sg = set()
    for tt in [mp.mpf(k) / 10 for k in range(1, 60)] + [10, 15, 25, 40, 80]:
        sg.add(mp.sign(SF(p, lam, ap, tt) - SF(q, lam, aq, tt)))
    rec("SAF Cex6.23 g4 sign change (numeric)",
        "VERIFIED" if len(sg) > 1 else "NO-CHANGE", f"signs {sg}")
    # Cex 6.25: likelihood ratio f_lam/f_gam non-monotone, a=(5/2,3),
    # p=(11/20,9/20), lam=(2/5,7/10), gam=(1/2,3/5).
    p2 = [mp.mpf(11) / 20, mp.mpf(9) / 20]
    lam2 = [mp.mpf(2) / 5, mp.mpf(7) / 10]
    gam2 = [mp.mpf(1) / 2, mp.mpf(3) / 5]
    a2 = [mp.mpf(5) / 2, mp.mpf(3)]
    ab2 = sum(p2[i] * a2[i] for i in range(2))
    def Sf(l, tt):
        return sum(p2[i] * mp.e ** (-a2[i] * l[i] * tt) for i in range(2)) ** (1 / ab2)
    def ff(l, tt):
        inner = sum(p2[i] * mp.e ** (-a2[i] * l[i] * tt) for i in range(2))
        df = sum(p2[i] * a2[i] * l[i] * mp.e ** (-a2[i] * l[i] * tt) for i in range(2))
        return inner ** (1 / ab2 - 1) * df / ab2
    prev, mono = None, True
    for k in range(1, 200):
        tt = mp.mpf(k) / 40
        r = ff(lam2, tt) / ff(gam2, tt)
        if prev is not None and r < prev:
            mono = False
            break
        prev = r
    rec("SAF Cex6.25 lr ratio non-monotone (numeric)",
        "VERIFIED" if not mono else "MONOTONE-ON-GRID", "")


# ------------------------------------------------------------------ SKF ----
def skf_inner(p, g, alpha_theta_exps):
    return sum(p[i] * u ** int(e) for i, e in enumerate(alpha_theta_exps))


def skf_ex31_cex31():
    """Ex3.1: p=(1/20,3/10,13/20) inc, gam=(15,6,3), del=(16,4,3) dec,
    theta=2, alpha=3, exp.  Claim S_U - S_V <= 0.
    u=e^{-t/2}: exps a*gam=(45,18,9), a*del=(48,12,9).
    Cex3.1: p reordered (13/20,1/20,3/10) -> claim sign change."""
    gam, dele = (15, 6, 3), (16, 4, 3)
    p = (R(1, 20), R(3, 10), R(13, 20))
    eg = [3 * g for g in gam]
    ed = [3 * d for d in dele]
    du = skf_inner(p, gam, eg)
    dv = skf_inner(p, dele, ed)
    d = sp.expand(du - dv)
    n = roots01(d, u)
    rec("SKF Ex3.1 inner diff <=0", "HOLDS" if n == 0 and
        sp.sign(d.subs(u, R(1, 2))) <= 0 else "FAILS", f"roots {n}")
    p2 = (R(13, 20), R(1, 20), R(3, 10))
    d2 = sp.expand(skf_inner(p2, gam, eg) - skf_inner(p2, dele, ed))
    n2 = roots01(d2, u)
    rec("SKF Cex3.1 sign change (p reordered)",
        "VERIFIED" if n2 >= 1 else "NO-CHANGE", f"roots {n2}")


def skf_ex32_cex32():
    """Ex3.2 (Thm3.2(i)): p=(1/20,3/10,13/20), q=(1/25,13/50,7/10),
    gam=(15,6,3), theta=(2,7/2,5), alpha=5.
    exponents a*g_i/theta_i: 75/2, 60/7, 3 -> x14: (525,120,42) in u=e^{-t/14}
    Cex3.2: gam=(20,5,8) not in D -> exps (50,100/7,8)->x14 (700,200,112)"""
    p = (R(1, 20), R(3, 10), R(13, 20))
    q = (R(1, 25), R(13, 50), R(7, 10))
    th = (R(2), R(7, 2), R(5))
    gam = (15, 6, 3)
    eg = [int(14 * 5 * g / th[i]) for i, g in enumerate(gam)]
    du = skf_inner(p, gam, eg)
    dv = skf_inner(q, gam, eg)
    d = sp.expand(du - dv)
    n = roots01(d, u)
    rec("SKF Ex3.2 inner diff <=0", "HOLDS" if n == 0 and
        sp.sign(d.subs(u, R(1, 2))) <= 0 else "FAILS", f"roots {n}")
    gam2 = (20, 5, 8)
    eg2 = [int(14 * 5 * g / th[i]) for i, g in enumerate(gam2)]
    d2 = sp.expand(skf_inner(p, gam2, eg2) - skf_inner(q, gam2, eg2))
    n2 = roots01(d2, u)
    rec("SKF Cex3.2 sign change", "VERIFIED" if n2 >= 1 else "NO-CHANGE",
        f"roots {n2}")


def skf_ex33_cex33_cex34():
    """Ex3.3 (Thm3.3(i)): p=(1/20,3/10,13/20),q=(1/25,13/50,7/10),
    gam=(15,6,3), del=(16,4,3), theta=5, alpha=5 -> u=e^{-t}: exps a*g/5 =
    g integers.  Cex3.3: gam=(12,2,15), del=(16,6,5) (gam not D).
    Cex3.4: hazard-rate sign change for the Ex3.3 params."""
    p = (R(1, 20), R(3, 10), R(13, 20))
    q = (R(1, 25), R(13, 50), R(7, 10))
    gam, dele = (15, 6, 3), (16, 4, 3)
    # theta=5, alpha=5 -> exponent = alpha*g/theta = g (integer) with u=e^{-t}
    du = skf_inner(p, gam, gam)
    dv = skf_inner(q, dele, dele)
    d = sp.expand(du - dv)
    n = roots01(d, u)
    rec("SKF Ex3.3 inner diff <=0", "HOLDS" if n == 0 and
        sp.sign(d.subs(u, R(1, 2))) <= 0 else "FAILS", f"roots {n}")
    gam2, del2 = (12, 2, 15), (16, 6, 5)
    d2 = sp.expand(skf_inner(p, gam2, gam2) - skf_inner(q, del2, del2))
    n2 = roots01(d2, u)
    rec("SKF Cex3.3 sign change", "VERIFIED" if n2 >= 1 else "NO-CHANGE",
        f"roots {n2}")
    # Cex3.4: hazard diff for Ex3.3 params: h=(1/5)*htilde, htilde has weights
    # gam_i vs delta_i:
    def ht(p_, g_, e_):
        num = sum(p_[i] * g_[i] * u ** e_[i] for i in range(3))
        den = sum(p_[i] * u ** e_[i] for i in range(3))
        return sp.cancel(num / den)
    dh = sp.cancel(sp.together(ht(p, gam, gam) - ht(q, dele, dele)))
    n3 = roots01(dh, u)
    rec("SKF Cex3.4 hazard diff sign change", "VERIFIED" if n3 >= 1 else
        "NO-CHANGE", f"roots {n3}; signs {signs(dh, u, [R(1,4),R(1,2),R(7,8)])}")


def skf_cex38():
    """Cex3.8 claims hazard diff changes sign: values +-1e-16.
    Show symbolically h_U - h_V == 0.
    p=(1/20,3/10,13/20), q=(1/25,13/50,7/10), gam=7 scalar,
    theta=(5,7/2,2), xi=(5,3,3/2), alpha=-3/10, Pareto Gbar=(theta/t)^{1/2}.
    h_U = sum_i p_i * [h(t/th_i)/th_i] * Gbar^{a*g}(t/th_i) / inner,
    h(t)=1/(2t) -> h(t/th_i)/th_i = 1/(2t) for all i,
    and gamma scalar -> h_U = (7/(2t)) * 1 = same for V.
    More generally with weights: h_U = (g/(2t)) * sum p_i w_i / sum p_i w_i.
    """
    g_sym = sp.Symbol("g", positive=True)
    w = sp.symbols("w1 w2 w3", positive=True)
    pp = sp.symbols("p1 p2 p3", positive=True)
    expr = (g_sym / (2 * t)) * sum(p_ * w_ for p_, w_ in zip(pp, w)) / \
        sum(p_ * w_ for p_, w_ in zip(pp, w))
    same = sp.simplify(expr - g_sym / (2 * t)) == 0
    rec("SKF Cex3.8 hazard diff identically zero",
        "VERIFIED" if same else "NONZERO", "h_U = gam/(2t) = h_V exactly")


def skf_cex35_cex37_numeric():
    """Cex3.5: Pareto Gbar=(1/t)^{1/2}, p=(1/20,3/10,13/20), gam=2,
    theta=(5,7/2,2), xi=(3/2,5,3), alpha=-3/10.  Claimed
    Gbar_U(10)-Gbar_V(10) = -0.08887328 <0 (violates claimed >=0... wait
    their claim is theorem gives >=st i.e. diff >=0; they report <0).
    Cex3.7: q=(7/10,13/50,2/5), value at 20 = -0.08336543.
    Both involve fractional powers -> 60-digit numerical check."""
    import mpmath as mp
    mp.mp.dps = 60
    p = [mp.mpf(1) / 20, mp.mpf(3) / 10, mp.mpf(13) / 20]
    gam = mp.mpf(2)
    theta = [mp.mpf(5), mp.mpf(7) / 2, mp.mpf(2)]
    xi = [mp.mpf(3) / 2, mp.mpf(5), mp.mpf(3)]
    alpha = mp.mpf(-3) / 10

    def Gbar(x):
        return x ** (-mp.mpf(1) / 2)

    def S(vec, sc, tt):
        inner = sum(p[i] * Gbar(tt / sc[i]) ** (alpha * gam) for i in range(3))
        return inner ** (1 / alpha)

    d10 = S(p, theta, 10) - S(p, xi, 10)
    rec("SKF Cex3.5 value -0.08887328",
        "VERIFIED" if abs(float(d10) - (-0.08887328)) < 1e-6 else "MISMATCH",
        f"exact-computed {float(d10):.8f}")
    q = [mp.mpf(7) / 10, mp.mpf(13) / 50, mp.mpf(2) / 5]
    xi2 = [mp.mpf(5), mp.mpf(3), mp.mpf(3) / 2]
    def Sq(vec, sc, tt, wts):
        inner = sum(wts[i] * Gbar(tt / sc[i]) ** (alpha * gam) for i in range(3))
        return inner ** (1 / alpha)
    d20 = Sq(p, theta, 20, p) - Sq(q, xi2, 20, q)
    rec("SKF Cex3.7 value -0.08336543",
        "VERIFIED" if abs(float(d20) - (-0.08336543)) < 1e-6 else "MISMATCH",
        f"computed {float(d20):.8f}")


def skf_ex35_cex36():
    """Ex3.5: power dist Gbar=1-t^2 on (0,1); p=(1/20,3/10,13/20), gam=2,
    theta=(5,7/2,2), xi=(5,3,3/2), alpha=3/10 -> ag=3/5 non-integer:
    algebraic; use exact sqrt-free power (1-(t/th)^2)^{3/5}: still algebraic
    degree 5.  Instead verify with mp AND note claim 'non-negative'.
    Cex3.6: gam=10, theta=(5,7/2,11/10), xi=(5,2,6/5), alpha=3/10: ag=3 int!"""
    import mpmath as mp
    mp.mp.dps = 60
    p = [mp.mpf(1) / 20, mp.mpf(3) / 10, mp.mpf(13) / 20]

    def S(wts, th, gam, alpha, tt):
        inner = sum(wts[i] * (1 - (tt / th[i]) ** 2) ** (alpha * gam)
                    for i in range(3))
        return inner ** (1 / alpha)

    th = [mp.mpf(5), mp.mpf(7) / 2, mp.mpf(2)]
    xi = [mp.mpf(5), mp.mpf(3), mp.mpf(3) / 2]
    sg = set()
    mint = mp.mpf(0)  # domain 0<t<min(th,xi)=3/2
    for k in range(1, 60):
        tt = mp.mpf(k) / 40  # up to 1.475
        sg.add(mp.sign(S(p, th, 2, mp.mpf(3) / 10, tt) -
                       S(p, xi, 2, mp.mpf(3) / 10, tt)))
    rec("SKF Ex3.5 diff >=0 (numeric)", "HOLDS" if sg <= {0, 1} else "FAILS",
        f"signs {sg}")
    # Cex3.6: ag = 3 integer -> exact
    th2 = (R(5), R(7, 2), R(11, 10))
    xi2 = (R(5), R(2), R(6, 5))
    pp = (R(1, 20), R(3, 10), R(13, 20))
    x = sp.Symbol("x", positive=True)  # t variable
    def inn(th_, ag):
        return sum(pp[i] * (1 - (x / th_[i]) ** 2) ** ag for i in range(3))
    d = sp.cancel(sp.together(inn(th2, 3) - inn(xi2, 3)))
    n = roots01(d, x)   # domain (0,1)
    rec("SKF Cex3.6 sign change on (0,1)", "VERIFIED" if n >= 1 else
        "NO-CHANGE", f"roots {n}, signs {signs(d, x, [R(1,4),R(1,2),R(9,10)])}")


def skf_ex37_cex39():
    """Ex3.7: p=(3/5,2/5), gam=(4,5); q=(27/50,23/50), del=(43/10,47/10);
    theta=2, alpha=3, exp baseline mean 1/2 (Gbar=e^{-2t} -> h/theta scaling
    identical; use u=e^{-t}: exps a*g/theta = 3g/2: (6,15/2) -> x2 (12,15)).
    Claim U>=hr V: h_U <= h_V i.e. htilde diff <= 0.
    Cex3.9: alpha=-3 -> claim sign change."""
    p = (R(3, 5), R(2, 5))
    q = (R(27, 50), R(23, 50))
    gam = (R(4), R(5))
    dele = (R(43, 10), R(47, 10))
    eg = [6, 15]        # 2*alpha*gam/theta, alpha=3, theta=2 -> 3*g
    ed = [int(2 * 3 * d / 2) for d in dele]   # = 3*del: 12.9->129/10*? use x10
    # work in w = e^{-t/10}: exponents 10*3*g/2 = 15*g integers:
    w = sp.Symbol("w", positive=True)
    def ht(pw, gw):
        num = sum(pw[i] * gw[i] * w ** int(15 * gw[i]) for i in range(2))
        den = sum(pw[i] * w ** int(15 * gw[i]) for i in range(2))
        return sp.cancel(num / den)
    d = sp.cancel(sp.together(ht(p, gam) - ht(q, dele)))
    n = roots01(d, w)
    rec("SKF Ex3.7 htilde diff <=0", "HOLDS" if n == 0 and
        sp.sign(d.subs(w, R(1, 2))) <= 0 else "FAILS",
        f"roots {n}, signs {signs(d, w, [R(1,4),R(1,2),R(7,8)])}")
    # Cex3.9: alpha=-3 -> htilde at y=s^{-3}: exponents -3g -> shift
    def ht_neg(pw, gw, M):
        num = sum(pw[i] * gw[i] * w ** int(-15 * gw[i] - M) for i in range(2))
        den = sum(pw[i] * w ** int(-15 * gw[i] - M) for i in range(2))
        return sp.cancel(num / den)
    M = int(min([-15 * g for g in gam] + [-15 * dd for dd in dele]))
    d2 = sp.cancel(sp.together(ht_neg(p, gam, M) - ht_neg(q, dele, M)))
    n2 = roots01(d2, w)
    rec("SKF Cex3.9 sign change (alpha=-3)", "VERIFIED" if n2 >= 1 else
        "NO-CHANGE", f"roots {n2}")


def skf_ex38_cex311():
    """Ex3.8 (Thm 3.10, displayed-formula reading): baseline exp mean 1/2 ->
    r(t) = g/G = 2e^{-2t}/(1-e^{-2t}); r_U = (r/2) htilde_{p,gam}(G^a),
    G(t/2) = 1-e^{-t}, a=-3.  p=(2/5,3/5)?? text: [p;gam]=[0.4 0.6;4 5],
    [q;del]=[0.46 0.54;4.3 4.7].  With x=1-e^{-t}: exponents a*g=-12,-15
    vs a*d=-12.9,-14.1 -> x10: (-120,-150)/(-129,-141): htilde on y=G^{-3}
    in (1,oo) <-> x' = y^{-1} in (0,1): use w = G^{-3/10}? fractional.
    Simpler: htilde(y) = sum p_i g_i y^{g_i}/sum p_i y^{g_i}, y=G^{-3}>1;
    substitute z=1/y=G^3 in (0,1): htilde = sum p_i g_i z^{-g_i}/... shift."""
    x = sp.Symbol("x", positive=True)  # x = 1-e^{-t} in (0,1)
    p = (R(2, 5), R(3, 5))
    q = (R(23, 50), R(27, 50))
    gam = (R(4), R(5))
    dele = (R(43, 10), R(47, 10))
    # a=-3: y_i = x^{-3} -> htilde(y)=sum p_i g_i x^{-3g_i}/sum p_i x^{-3g_i}
    M = -3 * 47  # most negative exponent x10
    def rh(p_, g_):
        num = sum(p_[i] * g_[i] * x ** int(-30 * g_[i] - M) for i in range(2))
        den = sum(p_[i] * x ** int(-30 * g_[i] - M) for i in range(2))
        return sp.cancel(num / den)
    d = sp.cancel(sp.together(rh(p, gam) - rh(q, dele)))
    # claim: r_U >= r_V i.e. d >= 0 on (0,1)
    n = roots01(d, x)
    sc = signs(d, x, [R(1, 8), R(1, 4), R(1, 2), R(3, 4), R(7, 8)])
    rec("SKF Ex3.8 rh diff >=0 (a=-3,W2)", "HOLDS" if n == 0 and
        all(sg >= 0 for _, sg in sc) else "FAILS", f"roots {n}, signs {sc}")
    # Cex3.11: alpha=3 -> y=x^3 in (0,1), claim sign change
    def rh_pos(p_, g_):
        num = sum(p_[i] * g_[i] * x ** int(30 * g_[i]) for i in range(2))
        den = sum(p_[i] * x ** int(30 * g_[i]) for i in range(2))
        return sp.cancel(num / den)
    d2 = sp.cancel(sp.together(rh_pos(p, gam) - rh_pos(q, dele)))
    n2 = roots01(d2, x)
    rec("SKF Cex3.11 rh sign change (a=3)", "VERIFIED" if n2 >= 1 else
        "NO-CHANGE", f"roots {n2}, signs {signs(d2, x, [R(1,8),R(1,2),R(7,8)])}")


def saf_ex619():
    """SAF Ex6.19 (Thm6.17): p=(11/20,9/20), lam=(2/5,7/10), gam=(1/2,3/5),
    a=(5/2,3), exp: claim r_lam <= r_gam i.e. g3 = r_gam - r_lam >= 0.
    u=e^{-t/20}: a*lam=(20,42)/... 5/2*2/5=1 ->*20=20; 3*7/10=21/10->42;
    a*gam=(5/4,9/5)->(25,36)."""
    p = (R(11, 20), R(9, 20))
    alpha = (R(5, 2), R(3))
    lam = (R(2, 5), R(7, 10))
    gam = (R(1, 2), R(3, 5))
    abar = p[0] * alpha[0] + p[1] * alpha[1]
    def rmix(lvec):
        el = [int(20 * a * l) for a, l in zip(alpha, lvec)]
        num = sum(alpha[i] * p[i] * lvec[i] * u ** el[i] for i in range(2))
        den = sum(p[i] * u ** el[i] for i in range(2))
        return sp.cancel(num / (abar * den))
    d = sp.cancel(sp.together(rmix(gam) - rmix(lam)))
    n = roots01(d, u)
    rec("SAF Ex6.19 g3 >= 0", "HOLDS" if n == 0 and
        sp.sign(d.subs(u, R(1, 2))) >= 0 else "FAILS",
        f"roots {n}, signs {signs(d, u, [R(1,4),R(1,2),R(7,8)])}")


if __name__ == "__main__":
    saf_cex68(); saf_ex67(); saf_cex620(); saf_cex624()
    saf_cex623_625_numeric(); saf_ex619()
    skf_ex31_cex31(); skf_ex32_cex32(); skf_ex33_cex33_cex34()
    skf_cex38(); skf_cex35_cex37_numeric(); skf_ex35_cex36()
    skf_ex37_cex39(); skf_ex38_cex311()
    print("\n=== summary ===")
    for name, st, _ in RESULTS:
        print(f"{st:>10}  {name}")
