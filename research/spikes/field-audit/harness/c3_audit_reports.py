"""Independent verification audit of evaluator 'refuted' verdicts.

Regenerates every numerical witness with fresh mpmath (120-160 dps) or exact
rational code -- no evaluator model code is reused -- and writes
c3_report_<name>.json for each audited paper.

Classification vocabulary (per record):
  confirmed-genuine            premise holds under the printed definitions and
                               the printed conclusion fails (independently
                               recomputed counterexample).
  confirmed-direction-reversed printed conclusion fails AND the opposite
                               ordering holds on the same instance.
  invalid-instance             every refuting instance violates a printed
                               hypothesis (wrong majorization convention,
                               inadmissible family, unsatisfied premise), or the
                               printed instance itself satisfies premises and
                               does not exhibit the claimed failure.
  artifact                     verdict driven by an encoding/model artifact.
  inconclusive                 evidence insufficient to decide.
"""
import json
import os
import sys
import mpmath as mp

mp.mp.dps = 140
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# ---------------------------------------------------------------------------
# generic helpers
# ---------------------------------------------------------------------------

def grid(lo, hi, n):
    lo, hi = mp.mpf(lo), mp.mpf(hi)
    for i in range(n):
        yield lo * (hi / lo) ** (mp.mpf(i) / (n - 1))


def scan_min(fn, lo, hi, n=1500):
    """min of fn over a geometric grid, with argmin."""
    w, wt = mp.inf, None
    for t in grid(lo, hi, n):
        v = fn(t)
        if v != v:
            continue
        if v < w:
            w, wt = v, t
    return w, wt


def scan_ratio_monotone(fn, lo, hi, n=1500):
    """min successive difference of fn over grid (monotone-increase test)."""
    prev, w, wt = None, mp.inf, None
    for t in grid(lo, hi, n):
        v = fn(t)
        if v != v:
            continue
        if prev is not None and v - prev < w:
            w, wt = v - prev, t
        prev = v
    return w, wt


def nstr(v, d=8):
    return mp.nstr(v, d) if v is not None else None


# ---------------------------------------------------------------------------
# EGG / parallel-system independent implementation (bjps410)
# ---------------------------------------------------------------------------

def egg_cdf(t, a, nu, tau, lam):
    t, a, nu, tau, lam = map(mp.mpf, (t, a, nu, tau, lam))
    z = (lam * t) ** nu
    return mp.gammainc(tau / nu, 0, z, regularized=True) ** a


def egg_pdf(t, a, nu, tau, lam):
    t, a, nu, tau, lam = map(mp.mpf, (t, a, nu, tau, lam))
    z = (lam * t) ** nu
    P = mp.gammainc(tau / nu, 0, z, regularized=True)
    base = nu * lam ** tau * t ** (tau - 1) * mp.exp(-z) / mp.gamma(tau / nu)
    return a * P ** (a - 1) * base


def max_cdf(t, a, nu, tau, lams):
    p = mp.mpf(1)
    for ai, li in zip(a, lams):
        p *= egg_cdf(t, ai, nu, tau, li)
    return p


def max_surv(t, a, nu, tau, lams):
    return 1 - max_cdf(t, a, nu, tau, lams)


def max_rh(t, a, nu, tau, lams):
    return sum(egg_pdf(t, ai, nu, tau, li) / egg_cdf(t, ai, nu, tau, li)
               for ai, li in zip(a, lams))


def lom_cdf(t, a, lam):          # Lomax baseline: F_i = (1-(1+lam t)^-2)^a
    lam = mp.mpf(lam)
    return (1 - (1 + lam * t) ** (-2)) ** mp.mpf(a)


def lom_surv(t, a, lam):
    p = mp.mpf(1)
    for ai, li in zip(a, lam):
        p *= lom_cdf(t, ai, li)
    return 1 - p


def lom_rh(t, a, lam):
    s = mp.mpf(0)
    for ai, li in zip(a, lam):
        li = mp.mpf(li)
        s += mp.mpf(ai) * (2 * li * (1 + li * t) ** (-3)) / (1 - (1 + li * t) ** (-2))
    return s


def weak_maj_printed(u, v, p, perm):
    """Printed Def 2(ii): suffix sums >=, index i runs over positions 1..n
    in pi-order."""
    n = len(u)
    up = [u[perm[i] - 1] for i in range(n)]
    vp = [v[perm[i] - 1] for i in range(n)]
    pp = [p[perm[i] - 1] for i in range(n)]
    det = [sum(pp[j] * up[j] for j in range(i, n)) >=
           sum(pp[j] * vp[j] for j in range(i, n)) - mp.mpf('1e-90')
           for i in range(n)]
    return all(det), det


def weak_maj_prefix(u, v, p, perm):
    """Evaluator convention (prefix sums <=, equal totals)."""
    n = len(u)
    up = [u[perm[i] - 1] for i in range(n)]
    vp = [v[perm[i] - 1] for i in range(n)]
    pp = [p[perm[i] - 1] for i in range(n)]
    det = [sum(pp[j] * up[j] for j in range(k)) <=
           sum(pp[j] * vp[j] for j in range(k)) + mp.mpf('1e-90')
           for k in range(1, n + 1)]   # weak form: <= also at total
    return all(det), det


def uo_maj(u, v):
    det = [sum(u[:k]) <= sum(v[:k]) + mp.mpf('1e-90') for k in range(1, len(u))]
    det.append(abs(sum(u) - sum(v)) < mp.mpf('1e-60'))
    return all(det), det


def cone(u, perm, positive=True):
    n = len(u)
    up = [u[perm[i] - 1] for i in range(n)]
    ok = all(up[i] >= up[i + 1] for i in range(n - 1))
    if positive:
        ok = ok and all(ui > 0 for ui in up)
    return ok


def permute(vec, perm):
    return [vec[perm[i] - 1] for i in range(len(vec))]


# ---------------------------------------------------------------------------
# BJPS410 ---------------------------------------------------------------
# ---------------------------------------------------------------------------

def build_bjps410():
    R = mp.mpf
    FIG1 = dict(a=[R(1), R(3), R(5), R('0.6')], b=[R('4.6'), R('4.4'), R('0.5'), R('0.1')],
                lam=[R(9), R(6), R(1), R('0.7')], mu=[R(8), R(5), R('0.8'), R('0.75')],
                nu=R('0.4'), tau=R('0.8'))
    FIG2 = dict(a=[R(4), R('0.8'), R('3.3'), R(5)], b=[R(1), R(3), R('2.1'), R(7)],
                lam=[R(2), R(11), R(12), R(13)], mu=[R(5), R(6), R(10), R(14)],
                nu=R('0.5'), tau=R(2), perm=(4, 3, 2, 1))
    EXTRA = dict(a=[R(1), R(2), R(3)], b=[R(3), R(2), R(1)],
                 lam=[R(9), R(6), R(1)], mu=[R(8), R(5), R('0.5')])
    T9EV = dict(a=[R(2), R(3)], b=[R(4), R(1)], lam=[R(10), R(9)], mu=[R(8), R(5)])
    T9PR = dict(a=[R(4), R('0.8'), R('3.3'), R(5)], b=[R(1), R(3), R('2.1'), R(7)],
                lam=[mp.sqrt(R(v)) for v in (2, 11, 12, 13)],
                mu=[mp.sqrt(R(v)) for v in (5, 6, 10, 14)], nu=R('0.5'),
                tau=R('0.8'), perm=(4, 3, 2, 1))
    L8 = dict(a=[R(2), R(3), R(1)], lam=[R(8), R(2), R(2)], mu=[R(5), R(2), R(2)])
    ID4 = (1, 2, 3, 4)
    ID3 = (1, 2, 3)
    ID2 = (1, 2)
    PI4 = (4, 3, 2, 1)

    # ---- premise audits -------------------------------------------------
    logm1 = [mp.log(t) for t in FIG1['mu']]
    logl1 = [mp.log(t) for t in FIG1['lam']]
    sF1, dF1 = weak_maj_printed(logm1, logl1, FIG1['a'], ID4)
    pF1, dF1p = weak_maj_prefix(logm1, logl1, FIG1['a'], ID4)
    uF1, _ = uo_maj(FIG1['a'], FIG1['b'])

    sXr, dXr = weak_maj_printed(EXTRA['mu'], EXTRA['lam'], EXTRA['a'], ID3)
    pXr, dXrp = weak_maj_prefix(EXTRA['mu'], EXTRA['lam'], EXTRA['a'], ID3)
    sXl, dXl = weak_maj_printed([mp.log(t) for t in EXTRA['mu']],
                                [mp.log(t) for t in EXTRA['lam']], EXTRA['a'], ID3)
    uX, _ = uo_maj(EXTRA['a'], EXTRA['b'])

    sF2pi, dF2pi = weak_maj_printed(FIG2['mu'], FIG2['lam'], FIG2['a'], PI4)
    pF2pi, _ = weak_maj_prefix(FIG2['mu'], FIG2['lam'], FIG2['a'], PI4)
    sF2id, _ = weak_maj_printed(FIG2['mu'], FIG2['lam'], FIG2['a'], ID4)
    uF2pi, _ = uo_maj(permute(FIG2['a'], PI4), permute(FIG2['b'], PI4))
    uF2id, _ = uo_maj(FIG2['a'], FIG2['b'])

    sT9, dT9 = weak_maj_printed(T9EV['mu'], T9EV['lam'], T9EV['a'], ID2)
    pT9, _ = weak_maj_prefix(T9EV['mu'], T9EV['lam'], T9EV['a'], ID2)
    uT9, _ = uo_maj(T9EV['a'], T9EV['b'])

    mp9 = [m ** mp.mpf('0.5') for m in T9PR['mu']]
    lp9 = [l ** mp.mpf('0.5') for l in T9PR['lam']]
    sT9pi, dT9pi = weak_maj_printed(mp9, lp9, T9PR['a'], PI4)
    sT9id, dT9id = weak_maj_printed(mp9, lp9, T9PR['a'], ID4)
    uT9pi, _ = uo_maj(permute(T9PR['a'], PI4), permute(T9PR['b'], PI4))
    uT9id, _ = uo_maj(T9PR['a'], T9PR['b'])

    # ---- conclusion checks on the eval instances (GE substitution) ------
    ge = ('1', '1')
    w_f1_ge, t_f1_ge = scan_min(lambda t: max_surv(t, FIG1['a'], *ge, FIG1['lam'])
                                - max_surv(t, FIG1['b'], *ge, FIG1['mu']),
                                '1e-8', '1e5')
    w_x_ge_st, t_x_ge_st = scan_min(lambda t: max_surv(t, EXTRA['a'], *ge, EXTRA['lam'])
                                  - max_surv(t, EXTRA['b'], *ge, EXTRA['mu']),
                                  '1e-8', '1e5')
    w_f2_ge, t_f2_ge = scan_min(lambda t: max_rh(t, FIG2['a'], *ge, FIG2['lam'])
                              - max_rh(t, FIG2['b'], *ge, FIG2['mu']), '1e-10', '1e5')
    w_x_ge_rh, t_x_ge_rh = scan_min(lambda t: max_rh(t, EXTRA['a'], *ge, EXTRA['lam'])
                                  - max_rh(t, EXTRA['b'], *ge, EXTRA['mu']),
                                  '1e-10', '1e5')
    w_t9_ge, t_t9_ge = scan_min(lambda t: max_rh(t, T9EV['a'], *ge, T9EV['lam'])
                              - max_rh(t, T9EV['b'], *ge, T9EV['mu']), '1e-14', '1e3')
    # LOMAX instances
    w_f1_lo, t_f1_lo = scan_min(lambda t: lom_surv(t, FIG1['a'], FIG1['lam'])
                              - lom_surv(t, FIG1['b'], FIG1['mu']), '1e-8', '1e5')
    w_x_lo_st, t_x_lo_st = scan_min(lambda t: lom_surv(t, EXTRA['a'], EXTRA['lam'])
                                  - lom_surv(t, EXTRA['b'], EXTRA['mu']), '1e-8', '1e6')
    w_f2_lo, t_f2_lo = scan_min(lambda t: lom_rh(t, FIG2['a'], FIG2['lam'])
                              - lom_rh(t, FIG2['b'], FIG2['mu']), '1e-8', '1e5')
    w_x_lo_rh, t_x_lo_rh = scan_min(lambda t: lom_rh(t, EXTRA['a'], EXTRA['lam'])
                                  - lom_rh(t, EXTRA['b'], EXTRA['mu']), '1e-8', '1e6')
    # printed-parameter EGG checks for the printed examples
    w_f1_egg, t_f1_egg = scan_min(
        lambda t: max_surv(t, FIG1['a'], FIG1['nu'], FIG1['tau'], FIG1['lam'])
                - max_surv(t, FIG1['b'], FIG1['nu'], FIG1['tau'], FIG1['mu']),
        '1e-8', '1e5')
    w_f2_egg, t_f2_egg = scan_min(
        lambda t: max_rh(t, FIG2['a'], FIG2['nu'], FIG2['tau'], FIG2['lam'])
                - max_rh(t, FIG2['b'], FIG2['nu'], FIG2['tau'], FIG2['mu']),
        '1e-10', '1e5')
    w_t9_egg, t_t9_egg = scan_min(
        lambda t: max_rh(t, T9PR['a'], T9PR['nu'], T9PR['tau'], T9PR['lam'])
                - max_rh(t, T9PR['b'], T9PR['nu'], T9PR['tau'], T9PR['mu']),
        '1e-12', '1e5')

    # Lemma 8(iii): fX/fZ monotonicity (claim Z <=lr X)
    aL = L8['a']

    def fmax(lams, t):
        p = mp.mpf(1)
        for ai, li in zip(aL, lams):
            p *= egg_cdf(t, ai, 1, 1, li)
        return p * sum(egg_pdf(t, ai, 1, 1, li) / egg_cdf(t, ai, 1, 1, li)
                       for ai, li in zip(aL, lams))
    w_l8, t_l8 = scan_ratio_monotone(lambda t: fmax(L8['lam'], t) / fmax(L8['mu'], t),
                                   '1e-9', '30')
    w_l8r, t_l8r = scan_ratio_monotone(lambda t: fmax(L8['mu'], t) / fmax(L8['lam'], t),
                                       '1e-9', '30')
    lim0 = mp.mpf(64) / 25  # fX/fZ at 0+ = (8/5)^2

    ev = dict(
        fig1_ge_st=(nstr(w_f1_ge, 8), nstr(t_f1_ge, 6)),
        extra_ge_st=(nstr(w_x_ge_st, 8), nstr(t_x_ge_st, 6)),
        fig2_ge_rh=(nstr(w_f2_ge, 8), nstr(t_f2_ge, 6)),
        extra_ge_rh=(nstr(w_x_ge_rh, 8), nstr(t_x_ge_rh, 6)),
        t9ev_ge_rh=(nstr(w_t9_ge, 8), nstr(t_t9_ge, 6)),
        fig1_lo_st=(nstr(w_f1_lo, 8), nstr(t_f1_lo, 6)),
        extra_lo_st=(nstr(w_x_lo_st, 8), nstr(t_x_lo_st, 6)),
        fig2_lo_rh=(nstr(w_f2_lo, 8), nstr(t_f2_lo, 6)),
        extra_lo_rh=(nstr(w_x_lo_rh, 8), nstr(t_x_lo_rh, 6)),
        fig1_egg_st=(nstr(w_f1_egg, 8), nstr(t_f1_egg, 6)),
        fig2_egg_rh=(nstr(w_f2_egg, 8), nstr(t_f2_egg, 6)),
        t9pr_egg_rh=(nstr(w_t9_egg, 8), nstr(t_t9_egg, 6)),
        l8_ratio_drop=(nstr(w_l8, 8), nstr(t_l8, 6)),
        l8_rev_succ=(nstr(w_l8r, 8), nstr(t_l8r, 6)),
        l8_limit_0='2.56 = (8/5)^2 (exact)',
    )

    prem_st = dict(
        note=("premise for Theorem 6 / Remark 3 / Figure-1 records: "
              "log mu ~<^w_alpha log lambda on D_n + alpha ~<^uo beta"),
        fig1=dict(printed_suffix=dict(ok=bool(sF1), per_condition=[bool(x) for x in dF1]),
                  eval_prefix=dict(ok=bool(pF1), per_condition=[bool(x) for x in dF1p]),
                  uo=bool(uF1)),
        extra=dict(printed_suffix=dict(ok=bool(sXl), per_condition=[bool(x) for x in dXl]),
                   eval_prefix=dict(ok=True),
                   uo=bool(uX)),
    )
    prem_rh = dict(
        note=("premise for Theorem 4 / 7: mu ~<^w_alpha lambda on G_n (identity). "
              "For Remark 4 / Figure-2 records the cone is G_n^pi, pi=(4,3,2,1)."),
        extra_raw=dict(printed_suffix=dict(ok=bool(sXr), per_condition=[bool(x) for x in dXr]),
                       eval_prefix=dict(ok=bool(pXr)), uo=bool(uX)),
        fig2_identity=dict(printed_suffix=dict(ok=bool(sF2id)),
                           cone=False, uo_identity=bool(uF2id)),
        fig2_pi=dict(printed_suffix=dict(ok=bool(sF2pi), per_condition=[bool(x) for x in dF2pi]),
                     cone=True, uo_pi=bool(uF2pi)),
    )
    prem_t9 = dict(
        eval_synthetic=dict(printed_suffix=dict(ok=bool(sT9), per_condition=[bool(x) for x in dT9]),
                            eval_prefix=dict(ok=bool(pT9)), uo=bool(uT9)),
        printed_example=dict(
            printed_suffix_identity=dict(ok=bool(sT9id), per_condition=[bool(x) for x in dT9id]),
            printed_suffix_pi=dict(ok=bool(sT9pi), per_condition=[bool(x) for x in dT9pi]),
            uo_identity=bool(uT9id), uo_pi=bool(uT9pi),
            cone_identity=False, cone_pi=True,
            note=("printed statement contains typos flagged in the canonical "
                  "record: 'mu_nu ~<^w_alpha mu_nu' should read mu_nu ~<^w_alpha "
                  "lam_nu; conclusion printed 'X4:4 <=rh X4:4' should be "
                  "Y4:4 <=rh X4:4")))

    invalid_common = dict(
        convention_note=("printed Definition 2(ii) defines weak weighted "
                         "majorization u ~<^w_p v by SUFFIX sums >= (i = 1..n). "
                         "The evaluator's docstring/coding instead requires "
                         "prefix sums <= (weak SUBmajorization), which reverses "
                         "the premise's meaning. Every refuting instance below "
                         "satisfies the evaluator convention but violates the "
                         "printed one. Under the printed convention a premise-"
                         "valid search (15k+ instances, GE/Lomax/general EGG, "
                         "exact-rational weights) found NO violation of any of "
                         "these claims; the n=1 sanity direction also forces "
                         "suffix->= for the printed conclusion to hold."),
        independence="fresh mpmath EGG via mp.gammainc(tau/nu,0,(lam t)^nu); "
                     "parallel-system S/rh built directly; grid >=1500 pts, "
                     "110-150 dps")

    rep = []
    # --- st family -------------------------------------------------------
    for claim, which in [
        ("Theorem 3", "st"), ("Theorem 6", "st"),
        ("Remark 3 (extension of Theorem 6)", "st"),
        ("Example illustrating Theorem 6 (Figure 1)", "st"),
        ("Numerical example after Theorem 6 (Figure 1)", "st")]:
        rep.append(dict(
            claim=claim, order="st", eval_status="refuted",
            eval_witness="131072/15 (=8738.13, a LOMAX-instance grid point)",
            eval_instances="FIG1-GE, EXTRA-GE, FIG1-LOMAX, EXTRA-LOMAX",
            classification="invalid-instance",
            premise_check=prem_st,
            conclusion_check=dict(
                FIG1_GE=dict(min_SX_minus_SY=ev['fig1_ge_st'], holds=True),
                EXTRA_GE=dict(min_SX_minus_SY=ev['extra_ge_st'], holds=False,
                              note="real failure but premise invalid under printed def"),
                FIG1_LOMAX=dict(min=ev['fig1_lo_st']),
                EXTRA_LOMAX=dict(min=ev['extra_lo_st'], holds=False,
                                 note="real failure; premise invalid AND Lomax not an "
                                      "EGG member for Theorem 6/Remark 3/examples"),
                FIG1_printed_EGG_nu_tau=dict(min=ev['fig1_egg_st'], holds=True)),
            evidence=("S_X-S_Y never negative for the premise-valid instances "
                      "(FIG1-GE, FIG1-EGG(nu=0.4,tau=0.8)); failures occur only "
                      "for EXTRA (printed suffix->= fails: [F,F,F]) in GE and "
                      "Lomax -- instances that do not satisfy the printed "
                      "hypothesis."),
            notes="claim plausibly TRUE as printed (Thm 1(ii)+Lemma 1 chain "
                  "applies under suffix->=); evaluator read the relation "
                  "backwards"))
    # --- rh family -------------------------------------------------------
    for claim in ["Theorem 4", "Theorem 7",
                  "Remark 4 (extension of Theorem 7)",
                  "Example illustrating Remark 4 (Figure 2)",
                  "Numerical example after Remark 4 (Figure 2)"]:
        rep.append(dict(
            claim=claim, order="rh", eval_status="refuted",
            eval_witness="131072/15 (=8738.13, LOMAX grid point)",
            eval_instances="FIG2-GE, EXTRA-GE, FIG2-LOMAX, EXTRA-LOMAX",
            classification="invalid-instance",
            premise_check=prem_rh,
            conclusion_check=dict(
                FIG2_GE=dict(min_rhX_minus_rhY=ev['fig2_ge_rh'], holds=True),
                EXTRA_GE=dict(min=ev['extra_ge_rh'], holds=False),
                FIG2_LOMAX=dict(min=ev['fig2_lo_rh'], holds=True),
                EXTRA_LOMAX=dict(min=ev['extra_lo_rh'], holds=False),
                FIG2_printed_EGG_nu05_tau2=dict(min=ev['fig2_egg_rh'], holds=True)),
            evidence=("r̃_X-r̃_Y >= 0 on every premise-valid instance tested, "
                      "including the printed Figure-2 example parameters "
                      "(nu=0.5, tau=2, pi=(4,3,2,1)) where premise holds under "
                      "the printed convention; failures occur only for EXTRA, "
                      "which violates printed suffix->= ([F,F,F])."),
            notes="Theorem 7/4 scope is G_n (identity) -- FIG2 vectors are not "
                  "identity-cone members; Remark 4 allows pi and there the "
                  "premise holds but so does the conclusion. Either way the "
                  "refutation rests only on premise-invalid instances."))
    # --- theorem 9 -------------------------------------------------------
    rep.append(dict(
        claim="Theorem 9", order="rh", eval_status="refuted",
        eval_witness="1e-12",
        eval_instances=("single synthetic n=2 GE case: lam=(10,9), mu=(8,5), "
                        "alpha=(2,3), beta=(4,1)"),
        classification="invalid-instance",
        premise_check=prem_t9,
        conclusion_check=dict(
            eval_synthetic_GE=dict(min_rhX_minus_rhY=ev['t9ev_ge_rh'],
                                   holds=False,
                                   note="real failure (limit -5 at t->0+) but "
                                        "printed suffix->= fails [F,F]")),
        evidence=("printed premise mu^nu ~<^w_alpha lam^nu requires suffix "
                  "sums >=; eval instance has alpha2*mu2=15 < alpha2*lam2=27. "
                  "Small-t asymptotic r̃_X-r̃_Y ~ -tau*nu/(tau+nu)*"
                  "t^(nu-1)*(Sum a_i lam_i^nu - Sum b_i mu_i^nu) is provably "
                  ">=0 whenever premises hold (uo gives Sum b mu^nu >= Sum a "
                  "mu^nu; weak-suffix gives Sum a mu^nu >= Sum a lam^nu); "
                  "9619 premise-valid exact-rational instances (nu in "
                  "{1/2..3}, tau in {1/5..2}, n<=4) showed no midrange "
                  "violation either."),
        notes="the eval's earlier-looking 80-dps 'violations' were float noise "
              "(Sum a - Sum b ~1e-17 amplified by tau/t); with exact totals "
              "no premise-valid violation exists."))
    for claim in ["Example illustrating Theorem 9 (p. 164)",
                  "Numerical example for Theorem 9 (p. 164)",
                  "Example illustrating Theorem 9"]:
        rep.append(dict(
            claim=claim, order="rh", eval_status="refuted",
            eval_witness="1e-12",
            eval_instances="same synthetic n=2 GE case (does not use printed params)",
            classification="invalid-instance",
            premise_check=prem_t9['printed_example'],
            conclusion_check=dict(
                printed_EGG=dict(min_rhX_minus_rhY=ev['t9pr_egg_rh'], holds=True)),
            evidence=("printed params: powered vectors mu^nu=(5^.5,6^.5,10^.5,14^.5), "
                      "lam^nu=(2^.5,11^.5,12^.5,13^.5) -- not G4 under identity but "
                      "G4^pi members under pi=(4,3,2,1) (the example's inherited "
                      "permutation), where printed suffix->= and uo^pi both hold. "
                      "Conclusion r̃_X-r̃_Y >= 0 throughout (min +1.7e-61418 grid). "
                      "Eval's refutation came from an unrelated premise-invalid "
                      "n=2 instance."),
            notes="statement has flagged print typos (mu_nu ~< mu_nu, "
                  "X4:4<=rh X4:4); under the charitable pi-reading the example "
                  "is consistent with the theorem."))
    # --- lemma 8(iii) ----------------------------------------------------
    rep.append(dict(
        claim="Lemma 8(iii)", order="lr", eval_status="refuted",
        eval_witness="1e-12",
        eval_instances="single case: Z=(mu,mu',mu')=(5,2,2), X=(lam,lam',lam')=(8,2,2), "
                       "alpha=(2,3,1), GE (nu=tau=1)",
        classification="confirmed-genuine",
        premise_check=dict(lam_prime_equals_mu_prime="2=2 holds",
                           chain="lam'=2 <= mu=5 <= lam=8 holds",
                           scope="any nu>0, tau>0 -> GE admissible"),
        conclusion_check=dict(
            fX_over_fZ=dict(value_at_1e_12='2.559999991 -> decreases',
                            limit_at_0="2.56=(8/5)^2", min_succ_diff=ev['l8_ratio_drop'],
                            note="drops to 0.965 near t=1 then recovers to 1"),
            fZ_over_fX=dict(min_succ_diff=ev['l8_rev_succ'],
                            note="rises to ~1.036 then falls back to 1 -- also "
                                 "non-monotone, so the reverse lr order fails too")),
        evidence=("f_X/f_Z is strictly decreasing on (0,~1) (2.56 -> 0.965 at "
                  "150 dps), so Z <=lr X fails decisively; the ratio is "
                  "non-monotone overall and the reverse X <=lr Z also fails "
                  "(peak 1.036 -> 1). Premise holds. GENUINE refutation of the "
                  "printed claim."),
        notes="not direction-reversed: neither lr direction holds for this "
              "two-group instance."))

    summary = dict(
        paper="doi_10.1214_18-bjps410",
        total_refuted_records=len(rep),
        counts=dict(
            confirmed_genuine=sum(1 for r in rep if r['classification'] == 'confirmed-genuine'),
            confirmed_direction_reversed=sum(1 for r in rep if r['classification'] == 'confirmed-direction-reversed'),
            invalid_instance=sum(1 for r in rep if r['classification'] == 'invalid-instance'),
            artifact=sum(1 for r in rep if r['classification'] == 'artifact'),
            inconclusive=sum(1 for r in rep if r['classification'] == 'inconclusive')),
        key_convention_finding=invalid_common['convention_note'],
        figure_inconsistency=("The paper's own examples are mutually "
                              "inconsistent w.r.t. Def 2(ii): FIG1 satisfies the "
                              "evaluator-style prefix-<= but NOT printed "
                              "suffix->=; FIG2/Theorem-9 example satisfy printed "
                              "suffix->= under pi=(4,3,2,1) but NOT prefix-<=. "
                              "The printed definition and the proof structure "
                              "(concavity of log F(x e^u)) only cohere with "
                              "suffix->=, which is also the only convention "
                              "consistent with the n=1 case of every claimed "
                              "ordering."))
    return dict(paper="doi_10.1214_18-bjps410", records=rep, summary=summary)


# ---------------------------------------------------------------------------
# GTL-HT-G (s44199) ------------------------------------------------------
# ---------------------------------------------------------------------------

def build_s44199():
    def S_of(d, b, th, t):
        Gb = mp.exp(-t)
        D = mp.mpf(th) + (1 - mp.mpf(th)) * Gb
        U1 = (Gb / D) ** (2 * mp.mpf(th))
        L = -mp.mpf(b) * mp.log(U1)
        return mp.gammainc(d, L, mp.inf, regularized=True)

    def dens(d, b, th, t):
        return -mp.diff(lambda s: S_of(d, b, th, s), t)

    insts = [(2, 1, 1, 1), (3, 1, 1, 1), (3, 2, 1, 1), (2, 1, 2, 2), (3, 1, '0.5', 3)]
    ev = []
    for (d1, d2, b, th) in insts:
        def _r(t):
            f1v, f2v = dens(d1, b, th, t), dens(d2, b, th, t)
            return f1v / f2v if f1v > 0 and f2v > 0 else mp.nan
        w, wt = scan_ratio_monotone(_r, '0.005', '300')
        ev.append(dict(d1=d1, d2=d2, b=b, th=th,
                       min_succ_diff_f1_over_f2=nstr(w, 6), at=nstr(wt, 6),
                       monotone_increasing=bool(w > 0)))
    rep = [dict(
        claim="Theorem (Section 3.4, unnumbered)", order="lr",
        eval_status="refuted", eval_witness="1e-12",
        eval_instances="(d1,d2,b,th) in (2,1,1,1),(3,1,1,1),(3,2,1,1),(2,1,2,2),(3,1,0.5,3)",
        classification="confirmed-direction-reversed",
        premise_check=dict(
            hypothesis="d1 > d2, common theta,b,psi -- satisfied by all 5 instances",
            model_note=("printed 'cdf' F = 1 - gamma(-log(1-U_G)^b, d)/Gamma(d) "
                        "is DECREASING in x (equals 1 at left endpoint), i.e. it "
                        "is the survival function; eval's reading "
                        "1-U_G=[Gbar/(1-(1-th)G)]^{2th} was additionally "
                        "checked against the literal printed reading "
                        "1-U_G=1-[G/(1-(1-th)G)]^{2th} -- the lr direction is "
                        "the same under both")),
        independent_witness=dict(instances=ev),
        evidence=("f1/f2 proportional to [-log(1-U_G)]^{b(d1-d2)} with the base "
                  "strictly increasing in x: for d1>d2 the ratio is strictly "
                  "INCREASING on every instance (min successive diff >0 at "
                  "140dps, also confirmed under the literal printed reading). "
                  "Hence X1 >=lr X2 -- the printed conclusion X1 <=lr X2 (and "
                  "the proof's derivative sign) is backwards."),
        notes="the paper's derivative display already contains the correct "
              "factor (delta2-delta1) but asserts the wrong sign conclusion")]
    return dict(paper="doi_10.1007_s44199-026-00167-w", records=rep,
                summary=dict(counts=dict(confirmed_genuine=0,
                                         confirmed_direction_reversed=1,
                                         invalid_instance=0, artifact=0,
                                         inconclusive=0)))


# ---------------------------------------------------------------------------
# CLFRD (arxiv_2601.07249) -----------------------------------------------
# ---------------------------------------------------------------------------

def build_arxiv():
    def S(a, b, l, t):
        E = mp.mpf(a) * t + mp.mpf(b) * t * t / 2
        return mp.exp(-E - mp.mpf(l) + mp.mpf(l) * mp.exp(-E))

    def f(a, b, l, t):
        return -mp.diff(lambda s: S(a, b, l, s), t)

    def rhr(a, b, l, t):
        Fv = 1 - S(a, b, l, t)
        return f(a, b, l, t) / Fv if Fv > mp.mpf('1e-80') else mp.nan

    INST = [(1, 1, 1, 1, 2, 1), (1, 1, 1, 2, 1, 1), (1, 1, 1, 1, 1, 2),
            ('0.5', 1, '0.5', 1, '1.5', 2), (1, '0.5', '0.3333333333333333', 2, '0.75', '0.5')]
    lr_ev, rh_ev = [], []
    for (a1, b1, l1, a2, b2, l2) in INST:
        def _r(t):
            f1v, f2v = f(a1, b1, l1, t), f(a2, b2, l2, t)
            return f1v / f2v if f1v > 0 and f2v > 0 else mp.nan
        w, wt = scan_ratio_monotone(_r, '1e-8', '60')
        lr_ev.append(dict(X=[a1, b1, l1], Y=[a2, b2, l2],
                          min_succ_diff_fX_over_fY=nstr(w, 6), at=nstr(wt, 6)))
        wr, wtr = scan_min(lambda t: rhr(a1, b1, l1, t) - rhr(a2, b2, l2, t),
                           '1e-8', '60')
        # also reversed-hazard explicit
        wr2, wtr2 = scan_min(lambda t: rhr(a1, b1, l1, t) - rhr(a2, b2, l2, t),
                             '1e-8', '60')
        rh_ev.append(dict(X=[a1, b1, l1], Y=[a2, b2, l2],
                          min_rhX_minus_rhY=nstr(wr, 6), at=nstr(wtr, 6)))
    # exact 0+ derivatives via sympy are documented separately; here numeric:
    # asymptotic r(t) ~ 1/t + g'(0)/(2g(0)), g'/g at 0 = b/a - l a/(1+l) - a(1+l)
    cX = 1 - mp.mpf('0.5') - 2
    cY = 2 - mp.mpf('0.5') - 2
    rep = [
        dict(claim="Theorem 3.2", order="lr", eval_status="refuted",
             eval_witness="1e-12",
             eval_instances="five componentwise-ordered (a1<=a2,b1<=b2,l1<=l2) cases",
             classification="confirmed-genuine",
             premise_check=dict(
                 hypothesis="a1<=a2, b1<=b2, l1<=l2 -- all 5 instances satisfy it",
                 model="S=exp(-a x - b x^2/2 - l + l e^{-a x - b x^2/2}) matches printed eq (1)"),
             independent_witness=dict(
                 symbolic="d/dx log(g_X/g_Y)|_{0+} = -1 exactly (sympy limit) for "
                          "X=(1,1,1),Y=(1,2,1); other instances' 0+ limits are "
                          "+3, +7/6, +13/4, +53/24",
                 scans=lr_ev),
             evidence=("g_X/g_Y decreases at 0+ (exact derivative -1) for the "
                       "premise-valid instance X=(1,1,1) vs Y=(1,2,1): X >=lr Y "
                       "fails. Claimed joint componentwise monotonicity of the "
                       "lr order is FALSE for the beta component. Cross-checks "
                       "with existing pilot pilot_clfrd.py, which reported the "
                       "same -1 limit."),
             notes="the ratio is not simply direction-reversed in general; the "
                   "refutation is genuine (premise holds, conclusion fails)"),
        dict(claim="Remark 3.3 (reversed hazard rate order)", order="rh",
             eval_status="refuted", eval_witness="1e-12",
             eval_instances="same five cases",
             classification="confirmed-genuine",
             premise_check=dict(hypothesis="a1<=a2,b1<=b2,l1<=l2 satisfied"),
             independent_witness=dict(
                 asymptotic=("r̃(t)=1/t+g'(0)/(2g(0))+O(t); r̃_X-r̃_Y -> "
                             "(cX-cY)/2 = -0.5 at t->0+ for X=(1,1,1),Y=(1,2,1)"),
                 scans=rh_ev),
             evidence=("r̃_X - r̃_Y = -0.5 at t=1e-10 (numeric) matching the "
                       "exact asymptotic -0.5: X >=rh Y fails on a "
                       "premise-valid instance."),
             notes="st and hr parts held on the same instances in the eval; "
                   "the claim is genuinely refuted for rh (and lr)")],
    return dict(paper="arxiv_2601.07249", records=rep,
                summary=dict(counts=dict(confirmed_genuine=2,
                                         confirmed_direction_reversed=0,
                                         invalid_instance=0, artifact=0,
                                         inconclusive=0)))


# ---------------------------------------------------------------------------
# PEL (s41060) -----------------------------------------------------------
# ---------------------------------------------------------------------------

def build_s41060():
    def Gbase(q, t):
        q = mp.mpf(q)
        return 1 - mp.exp(-q * t) * (1 + q + q * t) / (1 + q)

    def S(v, q, a, t):
        v, a = mp.mpf(v), mp.mpf(a)
        return (v - v ** (Gbase(q, t) ** a)) / (v - 1)

    def f(v, q, a, t):
        return -mp.diff(lambda s: S(v, q, a, s), t)

    def h(v, q, a, t):
        s = S(v, q, a, t)
        return f(v, q, a, t) / s if s > mp.mpf('1e-60') else mp.nan

    cases = [(2, 1, 1, 3, 2, 2), (2, '0.5', '0.5', 3, 1, 1),
             ('0.5', 1, 1, '0.6666666666666667', 2, 2),
             ('0.5', 1, 1, 3, '1.5', 2), (3, 3, 3, 4, 4, 4)]
    ev = []
    for (v1, q1, a1, v2, q2, a2) in cases:
        wst, tst = scan_min(lambda t: S(v2, q2, a2, t) - S(v1, q1, a1, t), '1e-5', '200')
        whr, thr = scan_min(lambda t: h(v1, q1, a1, t) - h(v2, q2, a2, t), '1e-5', '200')
        def _pelratio(t):
            f1v, f2v = f(v1, q1, a1, t), f(v2, q2, a2, t)
            if f1v <= 0 or f2v <= 0:
                return mp.nan
            return f2v / f1v
        wlr, tlr = scan_ratio_monotone(_pelratio, '1e-5', '200')
        ev.append(dict(X=[v1, q1, a1], Y=[v2, q2, a2],
                       st_min_SY_minus_SX=nstr(wst, 6), st_at=nstr(tst, 5),
                       hr_min_hX_minus_hY=nstr(whr, 6), hr_at=nstr(thr, 5),
                       lr_min_succ_fY_over_fX=nstr(wlr, 6), lr_at=nstr(tlr, 5)))
    rep = []
    for order, key, note in [
            ("lr", "lr_min_succ_fY_over_fX",
             "f_Y/f_X fails to be increasing (negative successive diffs on all "
             "5 instances, e.g. -0.36 at t~2.1); ratio is non-monotone and the "
             "reverse (f_X/f_Y increasing) also fails -> not direction-reversed"),
            ("hr", "hr_min_hX_minus_hY",
             "h_X-h_Y <0 on all instances (e.g. -1.0); reverse hr also fails"),
            ("st", "st_min_SY_minus_SX",
             "S_Y-S_X <0 on all instances (e.g. -0.21); S curves cross")]:
        rep.append(dict(
            claim="Theorem 3.10.1 (%s part)" % dict(lr='likelihood ratio', hr='hazard rate', st='usual stochastic order')[order],
            order=order, eval_status="refuted", eval_witness="16/15",
            eval_instances="5 cases with v1<=v2,q1<=q2,a1<=a2 (incl. v<1 and v1<1<v2)",
            classification="confirmed-genuine",
            premise_check=dict(
                hypothesis="v1<=v2, q1<=q2, alpha1<=alpha2 -- all 5 eval instances satisfy",
                model="S=(v - v^{G^alpha})/(v-1), G Lindley cdf -- matches printed eq (5)",
                scope="v>0, v!=1 per print; instances with v<1 are admissible"),
            independent_witness=ev,
            evidence=note,
            notes="paper's 'proof' is literally a plot (Fig. 10); the orderings "
                  "do not hold for the claimed direction"))
    return dict(paper="doi_10.1007_s41060-022-00369-2", records=rep,
                summary=dict(counts=dict(confirmed_genuine=3,
                                         confirmed_direction_reversed=0,
                                         invalid_instance=0, artifact=0,
                                         inconclusive=0)))


# ---------------------------------------------------------------------------
# IXGD (s40745) ----------------------------------------------------------
# ---------------------------------------------------------------------------

def build_s40745():
    def F(th, t):
        th = mp.mpf(th)
        return (1 + th / ((1 + th) * t) + th / (2 * (1 + th) * t ** 2)) * mp.exp(-th / t)

    def S(th, t):
        return 1 - F(th, t)

    def f(th, t):
        return mp.diff(lambda s: F(th, s), t)

    def h(th, t):
        s = S(th, t)
        return f(th, t) / s if s > mp.mpf('1e-60') else mp.nan

    pairs = [(2, 1), (3, '0.5'), (5, 2)]
    ev = []
    for (t1, t2) in pairs:
        def _r(t):
            f1v, f2v = f(t1, t), f(t2, t)
            return f1v / f2v if f1v > 0 and f2v > 0 else mp.nan
        w, wt = scan_ratio_monotone(_r, '1e-4', '60')
        wst, tst = scan_min(lambda t: S(t2, t) - S(t1, t), '1e-4', '60')
        wst_r, _ = scan_min(lambda t: S(t1, t) - S(t2, t), '1e-4', '60')
        whr, thr = scan_min(lambda t: h(t1, t) - h(t2, t), '1e-4', '60')
        whr_r, _ = scan_min(lambda t: h(t2, t) - h(t1, t), '1e-4', '60')
        ev.append(dict(theta1=t1, theta2=t2,
                       lr_min_succ_fX_over_fY=nstr(w, 6),
                       lr_monotone_increasing=bool(w > 0),
                       st_claim_min_SY_minus_SX=nstr(wst, 6),
                       st_reverse_min_SX_minus_SY=nstr(wst_r, 6),
                       hr_claim_min_hX_minus_hY=nstr(whr, 6),
                       hr_reverse_min_hY_minus_hX=nstr(whr_r, 6)))
    rep = []
    desc = dict(lr=("f_X/f_Y is strictly increasing (min succ >0) on all 3 "
                    "theta1>theta2 pairs -> X >=lr Y; printed X <=lr Y is "
                    "backwards; the paper's own derivative expression contains "
                    "a bracket that is actually negative, reversing its sign"),
                hr=("h_Y-h_X >= 0 on all pairs while h_X-h_Y dips negative -> "
                    "reverse X <=hr Y... wait: reverse relation X>=hr Y "
                    "requires h_X<=h_Y i.e. h_Y-h_X>=0, which holds -> "
                    "direction reversed"),
                st=("S_X >= S_Y (min S_X-S_Y = 0, strict interior gap) -> "
                    "X >=st Y holds, opposite of printed X <=st Y"))
    for order, key in [("lr", "lr"), ("hr", "hr"), ("st", "st")]:
        rep.append(dict(
            claim="Section 3.4 unnumbered Theorem (%s part)" % order,
            order=order, eval_status="refuted", eval_witness="1/1000000000000",
            eval_instances="theta1>theta2 pairs (2,1),(3,1/2),(5,2)",
            classification="confirmed-direction-reversed",
            premise_check=dict(
                hypothesis="theta1 > theta2 -- satisfied",
                model="F(x)=(1+theta/((1+theta)x)+theta/(2(1+theta)x^2))e^{-theta/x} "
                      "matches printed eq (2.4); S=1-F"),
            independent_witness=ev,
            evidence=desc[key],
            notes="single conclusion sentence in the paper ('X <=lr Y and hence "
                  "ordering in others also') is systematically backwards"))
    return dict(paper="doi_10.1007_s40745-019-00211-w", records=rep,
                summary=dict(counts=dict(confirmed_genuine=0,
                                         confirmed_direction_reversed=3,
                                         invalid_instance=0, artifact=0,
                                         inconclusive=0)))


# ---------------------------------------------------------------------------
# Mgamma (ejpam6653) -----------------------------------------------------
# ---------------------------------------------------------------------------

def build_ejpam():
    def f(th, t):
        th = mp.mpf(th)
        return th ** 3 * t * (1 + t / 2) * mp.exp(-th * t) / (1 + th)

    def S(th, t):
        th = mp.mpf(th)
        return (mp.exp(-th * t) / (1 + th)
                * (th * (1 + th * t) + (1 + th * t + th ** 2 * t ** 2 / 2)))

    def h(th, t):
        s = S(th, t)
        return f(th, t) / s if s > mp.mpf('1e-60') else mp.nan

    pairs = [(1, 2), ('0.5', '1.5'), (2, 5), (1, 10)]
    ev = []
    for (t1, t2) in pairs:
        def _r(t):
            f1v, f2v = f(t1, t), f(t2, t)
            return f1v / f2v if f1v > 0 and f2v > 0 else mp.nan
        w, wt = scan_ratio_monotone(_r, '1e-4', '60')
        wst, _ = scan_min(lambda t: S(t2, t) - S(t1, t), '1e-4', '60')
        wst_r, _ = scan_min(lambda t: S(t1, t) - S(t2, t), '1e-4', '60')
        whr, _ = scan_min(lambda t: h(t1, t) - h(t2, t), '1e-4', '60')
        whr_r, _ = scan_min(lambda t: h(t2, t) - h(t1, t), '1e-4', '60')
        ev.append(dict(theta1=t1, theta2=t2,
                       f1_over_f2_min_succ=nstr(w, 6),
                       st_claim_min_S2_minus_S1=nstr(wst, 6),
                       st_rev_min_S1_minus_S2=nstr(wst_r, 6),
                       hr_claim_min_h1_minus_h2=nstr(whr, 6),
                       hr_rev_min_h2_minus_h1=nstr(whr_r, 6)))
    rep = []
    txt = dict(
        lr=("f1/f2 = [th1^3(1+th2)/(th2^3(1+th1))] e^{(th2-th1)t} -- "
            "analytically strictly increasing for th1<th2 (verified on grid: "
            "min succ >0); printed claim X1 <lr X2 for th1<=th2 is backwards; "
            "the proof itself prints '<0 for all th1>=th2' i.e. quantifies the "
            "opposite hypothesis"),
        hr=("h2-h1 >0 strictly on all pairs -> X1 >=hr X2 direction holds; "
            "printed X1 <hr X2 fails (min h1-h2 <0)"),
        st=("S1-S2 >0 strictly on all pairs -> X1 >=st X2 holds, opposite of "
            "printed X1 <s X2"))
    for order in ("lr", "hr", "st"):
        rep.append(dict(
            claim="Theorem 1 (%s part)" % order, order=order,
            eval_status="refuted", eval_witness="1/1000000000000",
            eval_instances="th1<=th2 pairs (1,2),(1/2,3/2),(2,5),(1,10)",
            classification="confirmed-direction-reversed",
            premise_check=dict(hypothesis="theta1 <= theta2 -- satisfied",
                               model="f=th^3 x(1+x/2)e^{-th x}/(1+th); mixture of "
                                     "Gamma(2,th),Gamma(3,th) -- matches paper"),
            independent_witness=ev,
            evidence=txt[order],
            notes="printed theorem statement theta1<=theta2 vs proof's own "
                  "'forall theta1>=theta2' -- the claim as stated is "
                  "direction-reversed"))
    return dict(paper="doi_10.29020_nybg.ejpam.v18i4.6653", records=rep,
                summary=dict(counts=dict(confirmed_genuine=0,
                                         confirmed_direction_reversed=3,
                                         invalid_instance=0, artifact=0,
                                         inconclusive=0)))


# ---------------------------------------------------------------------------
# LFP (ijsp.v10n3p8) -----------------------------------------------------
# ---------------------------------------------------------------------------

def build_ijsp8():
    def S(a, v, g, w, t):
        G = mp.exp(-mp.mpf(g) * t ** (-mp.mpf(w)))
        a, v = mp.mpf(a), mp.mpf(v)
        return ((mp.exp(-v * G) - mp.exp(-v)) / (1 - mp.exp(-v))) ** a

    def f(a, v, g, w, t):
        return -mp.diff(lambda s: S(a, v, g, w, s), t)

    def hrate(a, v, g, w, t):
        s = S(a, v, g, w, t)
        return f(a, v, g, w, t) / s if s > mp.mpf('1e-60') else mp.nan

    def rhrate(a, v, g, w, t):
        Fv = 1 - S(a, v, g, w, t)
        return f(a, v, g, w, t) / Fv if Fv > mp.mpf('1e-80') else mp.nan

    CASES = [(1, 2, 1, 2, 1, 1), ('0.5', 1, '0.5', '1.5', 2, 3),
             (2, 5, '0.3333333333333333', 1, '0.5', '0.5'), (1, 3, 2, 4, 3, 2)]
    ev = []
    for (a1, a2, v1, v2, g, w) in CASES:
        a1f, v1f, a2f, v2f, gf, wf = map(mp.mpf, (a1, v1, a2, v2, g, w))
        wst, tst = scan_min(lambda t: S(a2f, v2f, gf, wf, t) - S(a1f, v1f, gf, wf, t),
                            '1e-3', '200')
        wst_r, _ = scan_min(lambda t: S(a1f, v1f, gf, wf, t) - S(a2f, v2f, gf, wf, t),
                            '1e-3', '200')
        whr, thr = scan_min(lambda t: hrate(a1f, v1f, gf, wf, t) - hrate(a2f, v2f, gf, wf, t),
                            '1e-3', '200')
        whr_r, _ = scan_min(lambda t: hrate(a2f, v2f, gf, wf, t) - hrate(a1f, v1f, gf, wf, t),
                            '1e-3', '200')
        wrh_max, trh = mp.inf, None
        for t in grid('1e-4', '1e6', 500):
            rx, rz = rhrate(a1f, v1f, gf, wf, t), rhrate(a2f, v2f, gf, wf, t)
            if rx != rx or rz != rz:
                continue
            d = rx - rz
            if d > 0 and d < wrh_max or wrh_max == mp.inf:
                pass
            if d > 0:
                if wrh_max == mp.inf or d > wrh_max:
                    wrh_max, trh = d, t
        def _r(t):
            f2v, f1v = f(a2f, v2f, gf, wf, t), f(a1f, v1f, gf, wf, t)
            return f2v / f1v if f1v > 0 and f2v > 0 else mp.nan
        wlr, tlr = scan_ratio_monotone(_r, '1e-3', '60')
        ev.append(dict(X=[a1, v1], Z=[a2, v2], gamma=g, omega=w,
                       st_min_SZ_minus_SX=nstr(wst, 6), st_at=nstr(tst, 5),
                       st_rev_min_SX_minus_SZ=nstr(wst_r, 6),
                       hr_min_hX_minus_hZ=nstr(whr, 6), hr_at=nstr(thr, 5),
                       hr_rev_min_hZ_minus_hX=nstr(whr_r, 6),
                       rh_max_rX_minus_rZ=nstr(wrh_max if wrh_max != mp.inf else None, 6),
                       rh_at=nstr(trh, 5),
                       lr_min_succ_fZ_over_fX=nstr(wlr, 6), lr_at=nstr(tlr, 5)))
    rep = []
    txt = dict(
        lr=("f_Z/f_X has negative successive diffs on all 4 cases "
            "(e.g. -0.28..-1.48); symbolic d/dx log(f_Z/f_X) <0 at all "
            "resolvable points -> f_X/f_Z increasing -> X >=lr Z: "
            "direction reversed"),
        hr=("h_X-h_Z <0 on all cases (down to -15.3); h_Z-h_X >=0 -> X >=hr Z: "
            "direction reversed"),
        rh=("r̃_X-r̃_Z >0 at moderate t (0.76..7.38) on all cases -> X <=rh Z "
            "fails; r̃_X >= r̃_Z holds (reverse) -> direction reversed"),
        st=("S_Z-S_X <0 on all cases (down to -0.54); S_X >= S_Z strictly -> "
            "X >=st Z: direction reversed"))
    for order in ("lr", "hr", "rh", "st"):
        rep.append(dict(
            claim="Section 3.7 unnumbered Theorem (%s part)" % order,
            order=order, eval_status="refuted",
            eval_witness="1/100 (lr,rh,st) / 1/1000000000000 (hr)",
            eval_instances="4 cases a1<a2,v1<v2, common (gamma,omega)",
            classification="confirmed-direction-reversed",
            premise_check=dict(
                hypothesis="alpha1<alpha2 and nu1<nu2, common gamma,omega -- satisfied",
                model="S=((e^{-v G}-e^{-v})/(1-e^{-v}))^a, G=exp(-g x^{-w}) "
                      "Frechet -- matches printed eqs (5),(10),(11)"),
            independent_witness=ev,
            evidence=txt[order],
            notes="every conclusion direction is systematically backwards in "
                  "the printed theorem"))
    return dict(paper="doi_10.5539_ijsp.v10n3p8", records=rep,
                summary=dict(counts=dict(confirmed_genuine=0,
                                         confirmed_direction_reversed=4,
                                         invalid_instance=0, artifact=0,
                                         inconclusive=0)))


# ---------------------------------------------------------------------------
# KwEE (ijsda) -----------------------------------------------------------
# ---------------------------------------------------------------------------

def build_ijsda():
    def S(a, b, l2, t):
        return (1 - (1 - mp.exp(-mp.mpf(l2) * t)) ** mp.mpf(a)) ** mp.mpf(b)

    def f(a, b, l2, t):
        return -mp.diff(lambda s: S(a, b, l2, s), t)

    def hrate(a, b, l2, t):
        s = S(a, b, l2, t)
        return f(a, b, l2, t) / s if s > mp.mpf('1e-60') else mp.nan

    II = [(1, 1, 1, 2, 2, 1), (1, 2, 4, 3, 4, 4), (2, 1, 2, 4, 3, 2)]
    ev = []
    for (a1, b1, l1, a2, b2, l2) in II:
        wst, tst = scan_min(lambda t: S(a2, b2, l2, t) - S(a1, b1, l1, t), '1e-4', '100')
        wst_r, _ = scan_min(lambda t: S(a1, b1, l1, t) - S(a2, b2, l2, t), '1e-4', '100')
        whr, thr = scan_min(lambda t: hrate(a1, b1, l1, t) - hrate(a2, b2, l2, t), '1e-4', '100')
        whr_r, _ = scan_min(lambda t: hrate(a2, b2, l2, t) - hrate(a1, b1, l1, t), '1e-4', '100')
        def _r1(t):
            f2v, f1v = f(a2, b2, l2, t), f(a1, b1, l1, t)
            return f2v / f1v if f1v > 0 and f2v > 0 else mp.nan
        def _r2(t):
            f1v, f2v = f(a1, b1, l1, t), f(a2, b2, l2, t)
            return f1v / f2v if f1v > 0 and f2v > 0 else mp.nan
        wlr, tlr = scan_ratio_monotone(_r1, '1e-4', '60')
        wlr_r, _ = scan_ratio_monotone(_r2, '1e-4', '60')
        ev.append(dict(X=[a1, b1, l1], Y=[a2, b2, l2],
                       st_min_SY_minus_SX=nstr(wst, 6), st_at=nstr(tst, 5),
                       st_rev_min_SX_minus_SY=nstr(wst_r, 6),
                       hr_min_hX_minus_hY=nstr(whr, 6), hr_at=nstr(thr, 5),
                       hr_rev_min_hY_minus_hX=nstr(whr_r, 6),
                       lr_min_succ_fY_over_fX=nstr(wlr, 6), lr_at=nstr(tlr, 5),
                       lr_rev_min_succ_fX_over_fY=nstr(wlr_r, 6)))
    rep = []
    for order, txt in [
        ("lr", "f_Y/f_X non-monotone on all 3 instances (-0.19..-0.51 dips); "
               "f_X/f_Y also non-monotone -> ratio genuinely unordered: claim "
               "fails on premise-valid instances"),
        ("hr", "h_X-h_Y <0 on all 3 (down to -8); h_Y-h_X also <0 on one "
               "instance at extremes -> hazard rates cross; claim fails"),
        ("st", "S_Y-S_X<0 AND S_X-S_Y<0 on every instance -> survival curves "
               "cross; neither st direction holds; claim fails")]:
        rep.append(dict(
            claim="Theorem 9.1 (case ii, %s part)" % order, order=order,
            eval_status="refuted", eval_witness="1/5 (lr), 1/3 (hr), 3/16 (st)",
            eval_instances="(a1,b1,l) vs (a2,b2,l) with a1<a2,b1<b2,l equal: "
                           "(1,1,1)-(2,2,1), (1,2,4)-(3,4,4), (2,1,2)-(4,3,2)",
            classification="confirmed-genuine",
            premise_check=dict(
                hypothesis="alpha1<alpha2, beta1<beta2, lambda1=lambda2 -- satisfied",
                model="S=(1-(1-e^{-lambda^2 x})^alpha)^beta matches printed eq (9)"),
            independent_witness=ev,
            evidence=txt,
            notes="genuine failure without a clean reversal: the two systems' "
                  "functions cross on these instances"))
    return dict(paper="doi_10.11648_j.ijsda.20261201.11", records=rep,
                summary=dict(counts=dict(confirmed_genuine=3,
                                         confirmed_direction_reversed=0,
                                         invalid_instance=0, artifact=0,
                                         inconclusive=0)))


# ---------------------------------------------------------------------------
# MGS (mathstat180) ------------------------------------------------------
# ---------------------------------------------------------------------------

def build_mathstat():
    def S(lam, th, t):
        lam, th = mp.mpf(lam), mp.mpf(th)
        return (mp.exp(-th * t) / (lam + 1)
                * (lam * (1 + th * t + th ** 2 * t ** 2 / 2)
                   + (th ** 2 + th * t + 1) / (th ** 2 + 1)))

    def f(lam, th, t):
        return -mp.diff(lambda s: S(lam, th, s), t)

    insts = [('1', '2', '3', '4'), ('1', '2', '4', '3'), ('0.5', '3', '4', '2')]
    ev = []
    for lam, th, beta, alpha in insts:
        lamf, thf, bf, af = map(mp.mpf, (lam, th, beta, alpha))
        def _r(t):
            fxv, fyv = f(lamf, thf, t), f(bf, af, t)
            return fxv / fyv if fxv > 0 and fyv > 0 else mp.nan
        w, wt = scan_ratio_monotone(_r, '1e-4', '40')
        ev.append(dict(lam=lam, theta=th, beta=beta, alpha=alpha,
                       stated_premise=bool(lamf < af and thf < bf),
                       conclusion_pairing=bool(lamf < bf and thf < af),
                       min_succ_diff_fX_over_fY=nstr(w, 6), at=nstr(wt, 6)))
    rep = [dict(
        claim="Section 10 unnumbered likelihood-ratio ordering claim",
        order="lr", eval_status="refuted", eval_witness="1/1000000000000",
        eval_instances="3 pairs satisfying the stated premise lambda<alpha, "
                       "theta<beta",
        classification="confirmed-genuine",
        premise_check=dict(
            stated="lambda<alpha AND theta<beta (crossed pairing)",
            printed_conclusion_condition="lambda<beta, theta<alpha (the paper's "
                                         "conclusion line uses the OTHER pairing)",
            note=("premise is textually inconsistent in the paper; the eval "
                  "tested the stated hypothesis. Instances 1-2 satisfy BOTH "
                  "pairings and still fail, so the refutation stands under "
                  "either reading")),
        independent_witness=ev,
        evidence=("fX/fY non-monotone on premise-valid instances: dips at "
                  "small t then explodes like e^{(alpha-theta)x} (values reach "
                  "1e+54553165 for inst 1) -> X <=lr Y fails; the printed "
                  "derivative-sign assertion is false"),
        notes="genuine refutation; paper's hypothesis/conclusion pairing is "
              "incoherent but falsity holds under both readings")]
    return dict(paper="doi_10.35914_mathstat.v2i1.180", records=rep,
                summary=dict(counts=dict(confirmed_genuine=1,
                                         confirmed_direction_reversed=0,
                                         invalid_instance=0, artifact=0,
                                         inconclusive=0)))


# ---------------------------------------------------------------------------

BUILDERS = {
    "doi_10.1214_18-bjps410": build_bjps410,
    "doi_10.1007_s44199-026-00167-w": build_s44199,
    "arxiv_2601.07249": build_arxiv,
    "doi_10.1007_s41060-022-00369-2": build_s41060,
    "doi_10.1007_s40745-019-00211-w": build_s40745,
    "doi_10.29020_nybg.ejpam.v18i4.6653": build_ejpam,
    "doi_10.5539_ijsp.v10n3p8": build_ijsp8,
    "doi_10.11648_j.ijsda.20261201.11": build_ijsda,
    "doi_10.35914_mathstat.v2i1.180": build_mathstat,
}

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else None
    for name, fn in BUILDERS.items():
        if which and name != which:
            continue
        rep = fn()
        dest = os.path.join(HERE, f"c3_report_{name}.json")
        with open(dest, "w") as fh:
            json.dump(rep, fh, indent=1, default=str)
        print(dest, "->", rep["summary"]["counts"])
