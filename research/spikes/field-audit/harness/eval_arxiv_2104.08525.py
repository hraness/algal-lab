"""Evaluator for arxiv:2104.08525 (ELS exponentiated location-scale model,
second-order statistics of fail-safe systems) ->
harness/eval_arxiv_2104.08525.result.json.

Model.  Xi ~ ELS(lambda_i, theta_i, alpha; Fb): F_Xi(x) = [Fb((x-lambda_i)/theta_i)]^alpha.
Second-order statistic (fail-safe system), independent components (eq. (3.1)):
    S_{X2:n}(x) = sum_l prod_{k!=l} S_k - (n-1) prod_k S_k
which is P(at most one component has failed); syscomp.order_stat(S,2,n).
Comparisons run on the common domain x > max_i (loc_i + scale_i*w0) where w0
is the baseline's left support endpoint (paper's own convention, x > max lam_i
when w0 = 0).

Baselines used, each satisfying its printed hypothesis (derivations in notes):
  pareto2 : S_b = w^-2, w>=1        w rb(w) = 2 (decreasing; weakly)
  pareto32: S_b = w^(-3/2), w>=1    rb=3/(2w) decr, convex; rb/rtb = w^(3/2)-1
                                    incr, convex; [rb/rtb]'' = (3/4)w^(-1/2) decr
  burr    : S_b = (1+w^(1/2))^-2, w>0   rb = 1/(sqrt(w)(1+sqrt(w))) decr (c<=1)
  pgw     : S_b = exp(1-(1+w^(1/2))^(1/2)), w>0  rb decr for c<=k, c<1
  ltw     : S_b = exp(1-w^a), w>=1    rb = a w^(a-1) decr for a<=1
  remark31: S_b = 2/(w+1), w>=1     wrb = w/(w+1) incr, concave;
                                    rb/rtb = (w-1)/2 incr, concave;
                                    w[rb/rtb]' = w/2 convex
  thm38   : S_b = w/(2w-1)^2, w>=1  rb = (2w+1)/(w(2w-1)) decr;
                                    w^2 rb' = -(4w^2+4w-1)/(2w-1)^2 incr
                                    (since (4w^2+4w-1)/(2w-1)^2 has derivative
                                     -16w/(2w-1)^3 < 0);
                                    rb/rtb = 4w + 1/w - 5 incr, convex;
                                    w^2[rb/rtb]'' = 2/w decr
  defect  : S_b = exp(1/w - 1), w>=1  rb = 1/w^2; w^2 rb = 1 constant (decr).

IMPORTANT DEFECTIVE-BASELINE CAVEAT.  Theorems 3.5, 3.6(ii) and Corollary 3.4
require "w^2 rb(w) decreasing in w > 0".  For ANY continuous proper lifetime
distribution on any support this is impossible: w^2 rb <= c forces
rb(w) <= c/w^2, hence int rb < oo, hence S(inf) = exp(-int rb) > 0.  The only
models satisfying the printed hypothesis are defective (improper).  The
concrete instance used here (S_b = exp(1/w - 1), missing mass 1 - e^{-1} at
infinity) satisfies the hypothesis literally; the order expressions are still
evaluated rigorously.  This is reported as a hypothesis-vacuity finding, not
treated as weakening.

Claims with an Archimedean copula (Theorems 3.10-3.18, Examples 3.4, 3.6,
Counterexamples 3.1, 3.2) are out of harness scope per the task instructions;
Example 3.5 is tested because its printed generator psi(x)=e^{-x} IS the
independence copula, so the printed model is literally independent.
"""
import json
import os

import sympy as sp

import closedform as cf
import syscomp as sc

R, x = sp.Rational, cf.x
w = sp.Symbol("w", positive=True)

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "arxiv_2104.08525.json")
OUT = os.path.join(HERE, "eval_arxiv_2104.08525.result.json")

BASELINES = {
    "pareto2": (w ** R(-2), R(1)),
    "pareto32": (w ** R(-3, 2), R(1)),
    "burr": ((1 + w ** R(1, 2)) ** R(-2), R(0)),
    "pgw": (sp.exp(1 - (1 + w ** R(1, 2)) ** R(1, 2)), R(0)),
    "ltw": (sp.exp(1 - w ** R(3, 25)), R(1)),
    "remark31": (R(2) / (w + 1), R(1)),
    "thm38": (w / (2 * w - 1) ** 2, R(1)),
    "defect": (sp.exp(1 / w - 1), R(1)),
}


def els_sys(base, lams, ths, alpha, lo):
    """Survival of X_{2:n} for ELS(loc lams, scale ths, exp alpha)."""
    Sb, w0 = BASELINES[base]
    Ss = [1 - (1 - Sb.subs(w, (x - R(l)) / R(t))) ** R(alpha)
          for l, t in zip(lams, ths)]
    start = max(R(l) + R(t) * w0 for l, t in zip(lams, ths))
    return Ss, start


def sys2(Ss):
    return sc.order_stat(Ss, 2, len(Ss))


def build(base, lams, ths, alpha):
    Ss, start = els_sys(base, lams, ths, alpha, None)
    return sys2(Ss), start


# ----------------------------------------------------- majorization ---------

def w_sub(a, b):
    """a weakly submajorized by b (a <=_w b): upper partial sums a <= b."""
    A, B = sorted(a), sorted(b)
    return all(sum(A[j:]) <= sum(B[j:]) for j in range(len(A)))


def w_sup(a, b):
    """a weakly supermajorized by b (a <=^w b): lower partial sums a >= b."""
    A, B = sorted(a), sorted(b)
    return all(sum(A[:j]) >= sum(B[:j]) for j in range(1, len(A) + 1))


def maj(a, b):
    return sum(a) == sum(b) and w_sup(a, b)


def recip_sup(th, de):
    """1/theta >=^w 1/delta (supermaj): lower partial sums of 1/delta's
    (reciprocals of largest delta) >= those of 1/theta."""
    return w_sup([1 / R(t) for t in de], [1 / R(t) for t in th])


def recip_rm(th, de):
    """1/theta >=^rm 1/delta: delta weakly submajorized by theta
    (upper partial sums of delta <= theta's)."""
    return w_sub(de, th)


def in_Iplus(v):
    return all(v[i] <= v[i + 1] for i in range(len(v) - 1)) and v[0] > 0


def in_Dplus(v):
    return all(v[i] >= v[i + 1] for i in range(len(v) - 1)) and v[-1] > 0


def mono(v):
    return in_Iplus(v) or in_Dplus(v)


def resolve_hi(SX, SY, lo):
    """Grid top: first dyadic point above lo where both survivals < 1e-25,
    else 1e5.  Only probes x > lo (the model is only valid there), and a
    finite hi makes closedform skip resolvable_top, which would otherwise
    probe dyadic points below lo where (x - lam)^-2 poles."""
    from mpmath import mp, mpf
    mp.dps = 60
    fx = sp.lambdify(x, SX, modules="mpmath")
    fy = sp.lambdify(x, SY, modules="mpmath")
    tiny = mpf(10) ** -25
    t = sp.Rational(lo) + 1
    while t < 10 ** 5:
        try:
            if abs(fx(mpf(t))) < tiny and abs(fy(mpf(t))) < tiny:
                return t
        except Exception:
            pass
        t *= 2
    return sp.Rational(10 ** 5)


def run(order, SX, SY, lo, note):
    hi = resolve_hi(SX, SY, lo)
    X = cf.Closed(SX, lo, hi)
    Y = cf.Closed(SY, lo, hi)
    h, wit, und = cf.check(order, X, Y)
    return {"holds": h, "witness": None if h else str(wit), "undecided": und,
            "notes": note}


def aggregate(label, order, results):
    ref = [r for r in results if not r["holds"]]
    out = {"claim": label, "order": order,
           "status": "refuted" if ref else "holds",
           "instances": len(results),
           "witness": ref[0]["witness"] if ref else None,
           "undecided_points": sum(r["undecided"] for r in results)}
    notes = [r["notes"] for r in results if r.get("notes")]
    if ref and ref[0].get("notes"):
        notes = [ref[0]["notes"]] + notes
    if notes:
        out["notes"] = " | ".join(dict.fromkeys(notes))
    return out


def fixed(label, order, status, notes):
    return {"claim": label, "order": order, "status": status,
            "instances": 0, "witness": None, "undecided_points": 0,
            "notes": notes}


# ------------------------------------------------------------ tests ---------

DEFECT_NOTE = ("satisfied literally on the defective baseline S_b=e^{1/w-1} "
               "(w^2 rb = 1 constant, S_b(inf)=e^{-1}>0); no proper continuous "
               "baseline can satisfy w^2 rb decreasing in w>0 -- hypothesis is "
               "unsatisfiable for proper lifetimes")


def cor31():
    """Cor 3.1: X~ELS(mu_m 1n, th, a), Y~ELS(mu vec, th, a), mu in I+, mu_n<=1,
    w rb decr (Pareto a=2); conclusion Y_{2:n} <=st X_{2:n}."""
    res = []
    for (mu, ths, alpha) in [
            ([R(1, 4), R(1, 2), R(3, 4)], [R(1)] * 3, R(1, 5)),
            ([R(1, 2), R(1), R(1)], [R(1, 2), R(3, 4), R(1)], R(1, 2)),
            ([R(1, 4), R(1, 2)], [R(1)] * 2, R(1))]:
        mum = max((1 + m) / 2 for m in mu)
        mid = [(1 + m) / 2 for m in mu]
        assert in_Iplus(mu) and mu[-1] <= 1
        assert w_sub(mu, mid) and w_sub(mid, [mum] * len(mu))
        SX, lx = build("pareto2", [mum] * len(mu), ths, alpha)
        SY, ly = build("pareto2", mu, ths, alpha)
        res.append(run("st", SY, SX, max(lx, ly),
                       f"mu={mu},mum={mum},th={ths},a={alpha},Pareto(w^-2)"))
    return res


def cor32():
    """Cor 3.2: Thm 3.1 setup (th=delta, a<=1, w rb decr), Y scalar mu,
    n mu <= sum lambda_i; X_{2:n} >=st Y_{2:n}."""
    res = []
    for (lam, mu, ths, alpha) in [
            ([R(2), R(3), R(7)], R(4), [R(1, 2), R(3, 4), R(1)], R(1, 2)),
            ([R(1), R(2), R(6)], R(3), [R(1)] * 3, R(1)),
            ([R(1, 2), R(1), R(3, 2)], R(1), [R(2)] * 3, R(1, 5))]:
        assert w_sub([mu] * len(lam), lam) and len(lam) * mu <= sum(lam)
        assert in_Iplus(lam) or in_Dplus(lam)
        SX, lx = build("pareto2", lam, ths, alpha)
        SY, ly = build("pareto2", [mu] * len(lam), ths, alpha)
        res.append(run("st", SY, SX, max(lx, ly),
                       f"lam={lam},mu={mu},th={ths},a={alpha},Pareto(w^-2)"))
    return res


def cor33():
    """Cor 3.3: common lambda vec, X scale th vec, Y scalar th, n/th >= sum 1/th_i;
    w rb decr; X_{2:n} >=st Y_{2:n}."""
    res = []
    for (lam, ths, th0, alpha) in [
            ([R(2), R(3), R(5)], [R(2), R(3), R(6)], R(3), R(1, 2)),
            ([R(1), R(1), R(1)], [R(1), R(2), R(3)], R(18, 11), R(1)),
            ([R(1), R(2), R(3)], [R(1), R(1), R(4)], R(4, 3), R(1, 5))]:
        assert len(ths) / th0 >= sum(1 / R(t) for t in ths)
        assert mono(ths)
        SX, lx = build("pareto2", lam, ths, alpha)
        SY, ly = build("pareto2", lam, [th0] * len(ths), alpha)
        res.append(run("st", SY, SX, max(lx, ly),
                       f"lam={lam},th={ths},th*={th0},a={alpha},Pareto(w^-2)"))
    return res


def cor34():
    """Cor 3.4: lam=mu common, a<=1, th vec vs scalar delta, n delta <= sum th_i;
    w^2 rb decr (defective baseline); X_{2:n} >=st Y_{2:n}."""
    res = []
    for (lam, ths, de, alpha) in [
            ([R(2), R(3), R(5)], [R(1), R(2), R(3)], R(2), R(1, 2)),
            ([R(1), R(2), R(3)], [R(2), R(3), R(6)], R(11, 3), R(1)),
            ([R(1), R(1), R(1)], [R(1), R(1), R(1)], R(1), R(1, 5))]:
        assert len(ths) * de <= sum(ths) and alpha <= 1
        assert mono(lam) and mono(ths)
        SX, lx = build("defect", lam, ths, alpha)
        SY, ly = build("defect", lam, [de] * len(ths), alpha)
        res.append(run("st", SY, SX, max(lx, ly),
                       f"lam={lam},th={ths},de={de},a={alpha}; {DEFECT_NOTE}"))
    return res


def cor35():
    """Cor 3.5: a=1, lam in I+/D+, Y scalar lam = mean; Pareto a=3/2 satisfies
    rb decr convex, rb/rtb incr convex, [rb/rtb]'' decr; X_{2:n} <=hr Y_{2:n}."""
    res = []
    for (lam, lams, th0) in [
            ([R(1), R(2), R(6)], R(3), R(1)),
            ([R(2), R(3), R(4)], R(3), R(2)),
            ([R(6), R(2), R(1)], R(3), R(1, 2)),
            ([R(1), R(1), R(1)], R(1), R(1))]:
        assert mono(lam) and sum(lam) / len(lam) == lams
        SX, lx = build("pareto32", lam, [th0] * len(lam), 1)
        SY, ly = build("pareto32", [lams] * len(lam), [th0] * len(lam), 1)
        res.append(run("hr", SX, SY, max(lx, ly),
                       f"lam={lam},lam*={lams},th={th0},a=1,Pareto(w^-3/2)"))
    return res


def cor36():
    """Cor 3.6: a=1, th vec vs scalar th (1/th = mean of 1/th_i); Remark 3.1
    baseline (w-1)/(w+1); X_{2:n} >=hr Y_{2:n}."""
    res = []
    for (lam0, ths) in [
            (R(2), [R(2), R(3), R(6)]),
            (R(1), [R(1), R(3), R(6)]),
            (R(1), [R(1), R(1), R(1)]),
            (R(3), [R(4), R(3), R(2)])]:
        th0 = len(ths) / sum(1 / R(t) for t in ths)   # harmonic mean
        assert mono(ths)
        SX, lx = build("remark31", [lam0] * len(ths), ths, 1)
        SY, ly = build("remark31", [lam0] * len(ths), [th0] * len(ths), 1)
        res.append(run("hr", SY, SX, max(lx, ly),
                       f"lam={lam0},th={ths},th*={th0},a=1,Fb=(w-1)/(w+1)"))
    return res


def ex31():
    """Example 3.1: Pareto Fb=1-w^-2, th=de=(0.5,0.7,0.9), lam=(5,7,9),
    mu=(2,4,7), a=0.2; X_{2:3} >=st Y_{2:3}."""
    lam, mu, ths, alpha = [R(5), R(7), R(9)], [R(2), R(4), R(7)], \
        [R(1, 2), R(7, 10), R(9, 10)], R(1, 5)
    assert w_sub(mu, lam) and in_Iplus(lam) and in_Iplus(mu)
    SX, lx = build("pareto2", lam, ths, alpha)
    SY, ly = build("pareto2", mu, ths, alpha)
    return [run("st", SY, SX, max(lx, ly), "printed instance")]


def ex32():
    """Example 3.2: Burr c=1/2,k=2, lam=(7,9,11), mu=(3,5,8), a=0.2, th=2;
    X_{2:3} >=st Y_{2:3}."""
    lam, mu, ths, alpha = [R(7), R(9), R(11)], [R(3), R(5), R(8)], [R(2)] * 3, R(1, 5)
    assert w_sub(mu, lam) and in_Iplus(lam) and in_Iplus(mu)
    SX, lx = build("burr", lam, ths, alpha)
    SY, ly = build("burr", mu, ths, alpha)
    return [run("st", SY, SX, max(lx, ly), "printed instance")]


def ex33():
    """Example 3.3: power-gen-Weibull c=1/2,k=2, lam=mu=2 scalar, th=(5,6,7),
    de=(2,3,4), a=0.6; X_{2:3} >=st Y_{2:3}."""
    ths, de, alpha = [R(5), R(6), R(7)], [R(2), R(3), R(4)], R(3, 5)
    assert recip_sup(ths, de) and in_Iplus(ths) and in_Iplus(de)
    SX, lx = build("pgw", [R(2)] * 3, ths, alpha)
    SY, ly = build("pgw", [R(2)] * 3, de, alpha)
    return [run("st", SY, SX, max(lx, ly), "printed instance")]


def ex35():
    """Example 3.5: generator psi=e^{-x} == independence; lower-truncated
    Weibull a=0.12, lam=5, th=(4.5,6.5,7.5), de=(2.5,3.5,4), a=0.9."""
    ths, de, alpha = [R(9, 2), R(13, 2), R(15, 2)], [R(5, 2), R(7, 2), R(4)], R(9, 10)
    assert recip_sup(ths, de) and in_Iplus(ths) and in_Iplus(de)
    SX, lx = build("ltw", [R(5)] * 3, ths, alpha)
    SY, ly = build("ltw", [R(5)] * 3, de, alpha)
    return [run("st", SY, SX, max(lx, ly),
                "printed instance; psi=e^{-x} is exactly the independence "
                "copula so the printed model is independent")]


def thm31():
    """Thm 3.1: th=delta, a<=1, lam,th,mu in I+ or D+, w rb decr (Pareto2),
    lam >=_w mu; X_{2:n} >=st Y_{2:n}."""
    res = []
    for (lam, mu, ths, alpha, cls) in [
            ([R(5), R(7), R(9)], [R(2), R(4), R(7)], [R(1, 2), R(3, 4), R(1)], R(1, 5), "I"),
            ([R(9), R(7), R(5)], [R(7), R(4), R(2)], [R(1), R(3, 4), R(1, 2)], R(1, 2), "D"),
            ([R(1), R(2), R(6)], [R(1), R(1), R(1)], [R(1)] * 3, R(1), "I"),
            ([R(1), R(2), R(4), R(8)], [R(1), R(1), R(1), R(1)], [R(1)] * 4, R(1, 2), "I")]:
        assert w_sub(mu, lam) and alpha <= 1
        assert (in_Iplus(lam) and in_Iplus(mu) and in_Iplus(ths)) if cls == "I" \
            else (in_Dplus(lam) and in_Dplus(mu) and in_Dplus(ths))
        SX, lx = build("pareto2", lam, ths, alpha)
        SY, ly = build("pareto2", mu, ths, alpha)
        res.append(run("st", SY, SX, max(lx, ly),
                       f"lam={lam},mu={mu},th={ths},a={alpha},cls={cls}"))
    return res


def thm32():
    """Thm 3.2: scalar th=delta, a<=1, lam,mu mono, rb decr, lam >=_w mu;
    Burr c=1/2 k=2 (rb decr for c<=1) and Pareto2."""
    res = []
    for (base, lam, mu, th0, alpha) in [
            ("burr", [R(7), R(9), R(11)], [R(3), R(5), R(8)], R(2), R(1, 5)),
            ("burr", [R(2), R(3), R(4)], [R(1), R(2), R(3)], R(1), R(1, 2)),
            ("burr", [R(4), R(3), R(2)], [R(3), R(2), R(1)], R(3), R(1)),
            ("pareto2", [R(1), R(2), R(6)], [R(1), R(1), R(1)], R(3, 2), R(1))]:
        assert w_sub(mu, lam) and alpha <= 1 and mono(lam) and mono(mu)
        ths = [th0] * len(lam)
        SX, lx = build(base, lam, ths, alpha)
        SY, ly = build(base, mu, ths, alpha)
        res.append(run("st", SY, SX, max(lx, ly),
                       f"{base},lam={lam},mu={mu},th={th0},a={alpha}"))
    return res


def thm33():
    """Thm 3.3: lam=mu common vec, a<=1, 1/th >=^w 1/de, w rb decr (Pareto2);
    X_{2:n} >=st Y_{2:n}."""
    res = []
    for (lam, ths, de, alpha, cls) in [
            ([R(2), R(3), R(5)], [R(5), R(6), R(7)], [R(2), R(3), R(4)], R(1, 2), "I"),
            ([R(1), R(1), R(1)], [R(2), R(3), R(6)], [R(1), R(2), R(3)], R(1), "I"),
            ([R(3), R(2), R(1)], [R(7), R(6), R(5)], [R(4), R(3), R(2)], R(1, 5), "D")]:
        assert recip_sup(ths, de) and alpha <= 1
        assert (in_Iplus(lam) and in_Iplus(ths) and in_Iplus(de)) if cls == "I" \
            else (in_Dplus(lam) and in_Dplus(ths) and in_Dplus(de))
        SX, lx = build("pareto2", lam, ths, alpha)
        SY, ly = build("pareto2", lam, de, alpha)
        res.append(run("st", SY, SX, max(lx, ly),
                       f"lam={lam},th={ths},de={de},a={alpha},cls={cls}"))
    return res


def thm34():
    """Thm 3.4: lam=mu scalar, a<=1, 1/th >=^w 1/de, rb decr (Burr);
    X_{2:n} >=st Y_{2:n}."""
    res = []
    for (lam0, ths, de, alpha) in [
            (R(2), [R(5), R(6), R(7)], [R(2), R(3), R(4)], R(1, 2)),
            (R(1), [R(2), R(4), R(8)], [R(1), R(2), R(3)], R(1)),
            (R(2), [R(3), R(4), R(6)], [R(2), R(3), R(4)], R(1, 5)),
            (R(1), [R(8), R(4), R(2)], [R(4), R(3), R(2)], R(1, 2))]:
        assert recip_sup(ths, de) and alpha <= 1
        assert mono(ths) and mono(de)
        lam = [lam0] * len(ths)
        SX, lx = build("burr", lam, ths, alpha)
        SY, ly = build("burr", lam, de, alpha)
        res.append(run("st", SY, SX, max(lx, ly),
                       f"lam={lam0},th={ths},de={de},a={alpha},Burr"))
    return res


def thm35():
    """Thm 3.5: lam=mu vec, a<=1, 1/th >=^rm 1/de (i.e. de <=_w th upper sums),
    w^2 rb decr (defective); X_{2:n} >=st Y_{2:n}."""
    res = []
    for (lam, ths, de, alpha) in [
            ([R(2), R(3), R(5)], [R(1), R(1), R(28)], [R(10), R(10), R(10)], R(1, 2)),
            ([R(1), R(1), R(1)], [R(2), R(3), R(6)], [R(3), R(3), R(4)], R(1)),
            ([R(3), R(2), R(1)], [R(8), R(3), R(1)], [R(4), R(4), R(4)], R(1, 5))]:
        assert recip_rm(ths, de) and alpha <= 1
        assert mono(lam) and mono(ths) and mono(de)
        assert (in_Iplus(lam) and in_Iplus(ths) and in_Iplus(de)) or \
            (in_Dplus(lam) and in_Dplus(ths) and in_Dplus(de))
        SX, lx = build("defect", lam, ths, alpha)
        SY, ly = build("defect", lam, de, alpha)
        res.append(run("st", SY, SX, max(lx, ly),
                       f"lam={lam},th={ths},de={de},a={alpha}; {DEFECT_NOTE}"))
    return res


def thm36i():
    """Thm 3.6(i): lam >=_w mu and 1/th >=^w 1/de, w rb decr (Pareto2)."""
    res = []
    for (lam, mu, ths, de, alpha, cls) in [
            ([R(5), R(7), R(9)], [R(2), R(4), R(7)], [R(5), R(6), R(7)],
             [R(2), R(3), R(4)], R(1, 2), "I"),
            ([R(9), R(7), R(5)], [R(7), R(4), R(2)], [R(9), R(8), R(6)],
             [R(5), R(4), R(3)], R(1, 5), "D")]:
        assert w_sub(mu, lam) and recip_sup(ths, de) and alpha <= 1
        assert (in_Iplus(lam) and in_Iplus(mu) and in_Iplus(ths) and in_Iplus(de)) \
            or (in_Dplus(lam) and in_Dplus(mu) and in_Dplus(ths) and in_Dplus(de))
        SX, lx = build("pareto2", lam, ths, alpha)
        SY, ly = build("pareto2", mu, de, alpha)
        res.append(run("st", SY, SX, max(lx, ly),
                       f"lam={lam},mu={mu},th={ths},de={de},a={alpha},cls={cls}"))
    return res


def thm36ii():
    """Thm 3.6(ii): lam >=_w mu and 1/th >=^rm 1/de, w^2 rb decr (defective)."""
    res = []
    for (lam, mu, ths, de, alpha) in [
            ([R(5), R(7), R(9)], [R(2), R(4), R(7)], [R(1), R(2), R(3)],
             [R(2), R(2), R(2)], R(1, 2)),
            ([R(9), R(7), R(5)], [R(7), R(4), R(2)], [R(4), R(3), R(2)],
             [R(3), R(3), R(3)], R(1, 5))]:
        assert w_sub(mu, lam) and recip_rm(ths, de) and alpha <= 1
        assert (in_Iplus(lam) and in_Iplus(mu) and in_Iplus(ths) and in_Iplus(de)) \
            or (in_Dplus(lam) and in_Dplus(mu) and in_Dplus(ths) and in_Dplus(de))
        SX, lx = build("defect", lam, ths, alpha)
        SY, ly = build("defect", mu, de, alpha)
        res.append(run("st", SY, SX, max(lx, ly),
                       f"lam={lam},mu={mu},th={ths},de={de},a={alpha}; {DEFECT_NOTE}"))
    return res


def thm37():
    """Thm 3.7: a=1, scalar th, lam >=^m mu, Pareto a=3/2 (rb decr convex,
    rb/rtb incr convex, [rb/rtb]'' decr); X_{2:n} <=hr Y_{2:n}."""
    res = []
    for (lam, mu, th0, cls) in [
            ([R(1), R(2), R(6)], [R(3), R(3), R(3)], R(1), "I"),
            ([R(6), R(2), R(1)], [R(3), R(3), R(3)], R(1), "D"),
            ([R(1), R(1), R(10)], [R(4), R(4), R(4)], R(1, 2), "I"),
            ([R(1), R(2), R(9)], [R(4), R(4), R(4)], R(2), "I")]:
        assert maj(mu, lam)   # mu <=^m lam i.e. lam >=^m mu
        assert (in_Iplus(lam) and in_Iplus(mu)) if cls == "I" \
            else (in_Dplus(lam) and in_Dplus(mu))
        SX, lx = build("pareto32", lam, [th0] * len(lam), 1)
        SY, ly = build("pareto32", mu, [th0] * len(lam), 1)
        res.append(run("hr", SX, SY, max(lx, ly),
                       f"lam={lam},mu={mu},th={th0},a=1,cls={cls}"))
    return res


def thm38():
    """Thm 3.8: a=1, common th vec, lam >=^m mu; custom baseline
    S_b = w/(2w-1)^2 satisfying the four printed conditions; X_{2:n} <=hr Y."""
    res = []
    for (lam, mu, ths, cls) in [
            ([R(1), R(2), R(6)], [R(3), R(3), R(3)], [R(1), R(1), R(1)], "I"),
            ([R(1), R(2), R(6)], [R(3), R(3), R(3)], [R(2), R(3), R(4)], "I"),
            ([R(6), R(2), R(1)], [R(3), R(3), R(3)], [R(3, 2), R(1), R(1, 2)], "D"),
            ([R(1), R(1), R(10)], [R(4), R(4), R(4)], [R(1), R(2), R(3)], "I")]:
        assert maj(mu, lam) and alpha_cls(lam, mu, ths, cls)
        SX, lx = build("thm38", lam, ths, 1)
        SY, ly = build("thm38", mu, ths, 1)
        res.append(run("hr", SX, SY, max(lx, ly),
                       f"lam={lam},mu={mu},th={ths},cls={cls}"))
    return res


def alpha_cls(lam, mu, ths, cls):
    ok = (in_Iplus(lam) and in_Iplus(mu) and in_Iplus(ths)) if cls == "I" \
        else (in_Dplus(lam) and in_Dplus(mu) and in_Dplus(ths))
    return ok


def thm39():
    """Thm 3.9: a=1, scalar lam, 1/th >=^m 1/de (equal sums + lower partial
    sums of 1/de >= 1/th's); Remark 3.1 baseline; X_{2:n} >=hr Y_{2:n}."""
    res = []
    for (lam0, ths, de, cls) in [
            (R(2), [R(2), R(3), R(6)], [R(3), R(3), R(3)], "I"),
            (R(1), [R(1), R(3), R(6)], [R(2), R(2), R(2)], "I"),
            (R(2), [R(1), R(2), R(6)], [R(6, 5), R(2), R(3)], "I"),
            (R(1), [R(6), R(3), R(1)], [R(2), R(2), R(2)], "D")]:
        ri, rj = [1 / R(t) for t in ths], [1 / R(d) for d in de]
        assert maj(rj, ri)          # 1/de <=^m 1/th i.e. 1/th >=^m 1/de
        assert (in_Iplus(ths) and in_Iplus(de)) if cls == "I" \
            else (in_Dplus(ths) and in_Dplus(de))
        lam = [lam0] * len(ths)
        SX, lx = build("remark31", lam, ths, 1)
        SY, ly = build("remark31", lam, de, 1)
        res.append(run("hr", SY, SX, max(lx, ly),
                       f"lam={lam0},th={ths},de={de},cls={cls},Fb=(w-1)/(w+1)"))
    return res


TESTS = {
    "Corollary 3.1": ("st", cor31),
    "Corollary 3.2": ("st", cor32),
    "Corollary 3.3": ("st", cor33),
    "Corollary 3.4": ("st", cor34),
    "Corollary 3.5": ("hr", cor35),
    "Corollary 3.6": ("hr", cor36),
    "Example 3.1": ("st", ex31),
    "Example 3.2": ("st", ex32),
    "Example 3.3": ("st", ex33),
    "Example 3.5": ("st", ex35),
    "Theorem 3.1": ("st", thm31),
    "Theorem 3.2": ("st", thm32),
    "Theorem 3.3": ("st", thm33),
    "Theorem 3.4": ("st", thm34),
    "Theorem 3.5": ("st", thm35),
    "Theorem 3.6(i)": ("st", thm36i),
    "Theorem 3.6(ii)": ("st", thm36ii),
    "Theorem 3.7": ("hr", thm37),
    "Theorem 3.8": ("hr", thm38),
    "Theorem 3.9": ("hr", thm39),
}

COPULA = {"Theorem 3.10", "Theorem 3.11", "Theorem 3.12", "Theorem 3.13",
          "Theorem 3.14", "Theorem 3.15(i)", "Theorem 3.15(ii)",
          "Theorem 3.16(i)", "Theorem 3.16(ii)", "Theorem 3.17",
          "Theorem 3.18", "Counterexample 3.1", "Counterexample 3.2",
          "Example 3.4", "Example 3.6"}


def main():
    data = json.load(open(CANON))
    out = []
    for rec in data:
        label, order = rec["claim"], rec["conclusion"]["order"]
        if order not in ("st", "hr", "rh", "lr"):
            out.append(fixed(label, order, "unsupported order",
                             "harness supports st/hr/rh/lr only"))
            continue
        if label in COPULA:
            out.append(fixed(label, order, "out of harness scope",
                             "Archimedean-copula model / dependent "
                             "components; outside the independent-system "
                             "harness"))
            continue
        o, fn = TESTS[label]
        assert o == order, (label, o, order)
        print(f"[eval] {label}", flush=True)
        out.append(aggregate(label, order, fn()))
    json.dump(out, open(OUT, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
