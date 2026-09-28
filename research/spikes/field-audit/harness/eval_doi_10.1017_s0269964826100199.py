"""Evaluator for doi:10.1017/s0269964826100199 (q-Weibull extreme order
statistics with random shocks), canonical records ->
harness/eval_doi_10.1017_s0269964826100199.result.json.

Model.  q-Weibull q-W(q, lam, b):  S(t) = [1 - (1-q) lam t^b]^((2-q)/(1-q)),
support [0, (lam(1-q))^{-1/b}] for 0<q<1 and [0, oo) for 1<q<2 (paper eq. (1)).
Systems: series survival = prod S_i; parallel survival = 1 - prod(1 - S_i).
Random shocks (section 5): U_i* = U_i I_i, I_i ~ Bernoulli(p_i), so
S_{U_i*}(t) = p_i S_i(t), t > 0.

Comparisons for 0<q<1 run on the paper's common domain (0, D), D the smallest
support end across all components on both sides (paper text after eq. (5)).
For 1<q<2 the domain is (0, oo); closedform scales its grid.

Every concrete instance is asserted to satisfy the printed hypotheses
(majorization relations, monotonicity classes D+/E+, the product-of-p
conditions, and the order direction of the record) before it is checked.
Copula/Archimedean-generator claims are out of harness scope per the task
instructions.
"""
import json
import os
import random

import sympy as sp

import closedform as cf
import syscomp as sc

random.seed(20260927)
R, x = sp.Rational, cf.x

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.1017_s0269964826100199.json")
OUT = os.path.join(HERE, "eval_doi_10.1017_s0269964826100199.result.json")


# ----------------------------------------------------------------- model ----

def qS(q, lam, b):
    """q-Weibull survival expression."""
    q, lam, b = R(q), R(lam), R(b)
    return (1 - (1 - q) * lam * x ** b) ** ((2 - q) / (1 - q))


def support_end(q, lam, b):
    """End of component support for 0 < q < 1; oo otherwise."""
    q, lam, b = R(q), R(lam), R(b)
    if q > 1:
        return sp.oo
    return (lam * (1 - q)) ** (-1 / b)


def rational_hi(hi):
    """closedform needs a rational grid end; shrink an irrational end."""
    if hi == sp.oo:
        return hi
    return sp.Rational(sp.floor(hi * 10 ** 6), 10 ** 6)


def common_hi(parts, groups):
    """Smallest support end over all components listed, floored."""
    ends = [support_end(q, l, b) for (q, l, b) in
            [t for g in groups for t in g]]
    return rational_hi(min(ends))


def system(comp_list, kind, hi):
    """comp_list: [(q, lam, b, p)]; p = shock probability (1 for no shock)."""
    Ss = [R(p) * qS(q, l, b) for (q, l, b, p) in comp_list]
    surv = sc.series(Ss) if kind == "series" else sc.parallel(Ss)
    return cf.Closed(surv, 0, hi)


def unshocked(comp_list):
    return [(q, l, b, 1) for (q, l, b) in comp_list]


# --------------------------------------------------------- order helpers ----

def inc(v):
    return sorted(v)


def w_sub(a, b):
    """a weakly submajorized by b (a <=_w b): upper partial sums a <= b."""
    A, B = inc(a), inc(b)
    return all(sum(A[j:]) <= sum(B[j:]) for j in range(len(A)))


def w_sup(a, b):
    """a weakly supermajorized by b (a <=^w b): lower partial sums a >= b."""
    A, B = inc(a), inc(b)
    return all(sum(A[:j]) >= sum(B[:j]) for j in range(1, len(A) + 1))


def maj(a, b):
    """a majorized by b (a <=^m b): equal sums + lower partial sums a >= b."""
    return sum(a) == sum(b) and w_sup(a, b)


def geq_w(a, b):
    return w_sub(b, a)


def geq_sup(a, b):
    return w_sup(b, a)


def in_Dplus(v):
    return all(v[i] >= v[i + 1] for i in range(len(v) - 1)) and v[-1] > 0


def in_Eplus(v):
    return all(v[i] <= v[i + 1] for i in range(len(v) - 1)) and v[0] > 0


def monotone(v):
    return in_Dplus(v) or in_Eplus(v)


def check(order, SX, SY):
    """cf.check(order, X, Y) tests X <=_order Y."""
    return cf.check(order, SX, SY)


def run_instance(label, order, SX, SY, notes=""):
    holds, w, und = check(order, SX, SY)
    return {"holds": holds, "witness": None if holds else str(w), "undecided": und, "notes": notes}


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


def both_dirs(label, order, SX, SY, primary="XY"):
    """Counterexample records: the printed claim is non-comparability /
    a stated-direction failure.  Both directions are evaluated."""
    h1, w1, u1 = check(order, SX, SY)
    h2, w2, u2 = check(order, SY, SX)
    fwd_fails = not h1
    rev_fails = not h2
    und = u1 + u2
    if fwd_fails or rev_fails:
        w = w1 if fwd_fails else w2
        note = ("printed non-comparability confirmed: BOTH directions have "
                "rigorous negative witnesses" if (fwd_fails and rev_fails)
                else "printed direction failure confirmed by strict witness "
                     "(reverse direction survived bounded testing)")
        return {"claim": label, "order": order, "status": "holds",
                "instances": 2, "witness": str(w), "undecided_points": und,
                "notes": note}
    return {"claim": label, "order": order, "status": "ambiguous hypotheses",
            "instances": 2, "witness": None, "undecided_points": und,
            "notes": ("printed non-comparability could not be witnessed: both "
                      "directions survived bounded testing (inconclusive, not "
                      "a refutation of the claim)")}


def fixed(label, order, status, notes):
    return {"claim": label, "order": order, "status": status,
            "instances": 0, "witness": None, "undecided_points": 0,
            "notes": notes}


# ------------------------------------------------------------- families -----

def lam_pair(lamU, lamV):
    """[(q,lam,b)] spec for two systems, filled later."""
    return lamU, lamV


def comps_q_lam(q, beta, lams):
    return [(R(q), R(l), R(beta)) for l in lams]


def comps_qvec(lams, beta, qs):
    return [(R(qi), R(lams), R(beta)) for qi in qs]


def comps_bvec(q, lams, betas):
    return [(R(q), R(lams), R(b)) for b in betas]


def shock_comps(base_list, ps):
    return [(q, l, b, R(p)) for (q, l, b), p in zip(base_list, ps)]


# ------------------------------------------------------------ the tests -----

def t31(part):
    """Theorem 3.1: series hr; (1) 0<q<1, lam <=_w lam* => V <=hr U;
    (2) 1<q<2, lam <=^w lam* => U <=hr V."""
    res = []
    insts = ([(R(1, 2), R(1, 2), [R(1, 2), R(3, 2)], [R(3, 10), R(9, 5)]),
              (R(1, 2), R(1, 1), [R(1, 2), R(1), R(3, 2)], [R(2, 5), R(6, 5), R(2)]),
              (R(1, 3), R(2, 1), [R(1, 4), R(1, 2)], [R(1, 4), R(2, 3)]),
              (R(3, 4), R(3, 2), [R(1, 2), R(3, 4), R(1)], [R(2, 5), R(3, 5), R(5, 4)])]
             if part == 1 else
             [(R(3, 2), R(1, 2), [R(3, 5), R(3, 2)], [R(3, 10), R(17, 10)]),
              (R(3, 2), R(1, 1), [R(3, 2), R(2), R(5, 2)], [R(1), R(2), R(3)]),
              (R(6, 5), R(2, 1), [R(1, 2), R(3, 2)], [R(2, 5), R(6, 5)]),
              (R(5, 4), R(3, 2), [R(2), R(5, 2), R(3)], [R(3, 2), R(2), R(5, 2)])])
    for (q, beta, lam, lam_s) in insts:
        if part == 1:
            assert 0 < q < 1 and w_sub(lam, lam_s), (lam, lam_s)
            X, Y, direction = "V", "U", "V<=hr U"
        else:
            assert 1 < q < 2 and w_sup(lam, lam_s), (lam, lam_s)
            X, Y, direction = "U", "V", "U<=hr V"
        cu, cv = comps_q_lam(q, beta, lam), comps_q_lam(q, beta, lam_s)
        hi = common_hi(None, [cu, cv])
        U = system(unshocked(cu), "series", hi)
        V = system(unshocked(cv), "series", hi)
        first, second = (V, U) if part == 1 else (U, V)
        res.append(run_instance(direction, "hr", first, second,
                                f"q={q},b={beta},lam={lam},lam*={lam_s}"))
    return res


def t34(part):
    """Theorem 3.4: series hr heterogeneous q; q <=^w q* => V <=hr U."""
    res = []
    insts = ([(R(1, 2), R(2, 1), [R(3, 10), R(1, 2)], [R(1, 10), R(3, 5)]),
              (R(1, 2), R(1, 1), [R(2, 5), R(1, 2), R(3, 5)], [R(1, 5), R(2, 5), R(9, 10)])]
             if part == 1 else
             [(R(1, 2), R(2, 1), [R(13, 10), R(3, 2)], [R(11, 10), R(8, 5)]),
              (R(1, 2), R(1, 1), [R(6, 5), R(7, 5), R(8, 5)], [R(11, 10), R(6, 5), R(9, 5)])])
    for (lam, beta, qv, qsv) in insts:
        if part == 1:
            assert all(0 < t < 1 for t in qv + qsv) and w_sup(qv, qsv)
        else:
            assert all(1 < t < 2 for t in qv + qsv) and w_sup(qv, qsv)
        cu = comps_qvec(lam, beta, qv)
        cv = comps_qvec(lam, beta, qsv)
        hi = common_hi(None, [cu, cv])
        U = system(unshocked(cu), "series", hi)
        V = system(unshocked(cv), "series", hi)
        res.append(run_instance("V<=hr U", "hr", V, U,
                                f"lam={lam},b={beta},q={qv},q*={qsv}"))
    return res


def t37(part):
    """Theorem 3.7: series st heterogeneous beta; beta <=^m beta* => V <=st U."""
    res = []
    betas = [([R(1, 2), R(3, 2)], [R(3, 10), R(17, 10)]),
             ([R(1, 2), R(1), R(3, 2)], [R(1, 4), R(3, 4), R(2)])]
    qlams = [(R(1, 2), R(1, 1)), (R(1, 3), R(1, 2))] if part == 1 else \
            [(R(3, 2), R(1, 2)), (R(5, 4), R(1, 1))]
    for (bv, bsv) in betas:
        assert maj(bv, bsv)
        for (q, lam) in qlams:
            assert (0 < q < 1) if part == 1 else (1 < q < 2)
            cu = comps_bvec(q, lam, bv)
            cv = comps_bvec(q, lam, bsv)
            hi = common_hi(None, [cu, cv])
            U = system(unshocked(cu), "series", hi)
            V = system(unshocked(cv), "series", hi)
            res.append(run_instance("V<=st U", "st", V, U,
                                    f"q={q},lam={lam},b={bv},b*={bsv}"))
    return res


def t310(part):
    """Theorem 3.10: parallel st; lam <=^w lam* => U <=st V."""
    res = []
    insts = [([R(1, 2), R(3, 2)], [R(3, 10), R(8, 5)]),
             ([R(3, 2), R(2), R(5, 2)], [R(1), R(2), R(3)])]
    qlams = [(R(1, 2), R(1, 2))] if part == 1 else [(R(3, 2), R(1, 2))]
    extra = [(R(1, 3), R(1, 1))] if part == 1 else [(R(6, 5), R(2, 1))]
    for (lam, lam_s) in insts:
        assert w_sup(lam, lam_s), (lam, lam_s)
        for (q, beta) in qlams + extra:
            cu = comps_q_lam(q, beta, lam)
            cv = comps_q_lam(q, beta, lam_s)
            hi = common_hi(None, [cu, cv])
            U = system(unshocked(cu), "parallel", hi)
            V = system(unshocked(cv), "parallel", hi)
            res.append(run_instance("U<=st V", "st", U, V,
                                    f"q={q},b={beta},lam={lam},lam*={lam_s}"))
    return res


WP = {
    # wp : [0,1] -> R+ , convex, differentiable, strictly increasing
    "sq": ("wp(u)=u^2", lambda u: u * u),
    "cu": ("wp(u)=u^3", lambda u: u * u * u),
    "id": ("wp(u)=u", lambda u: u),
}


def shock_parallel_st(q, beta, lam, lam_s, p, ps):
    """Theorem 5.1/5.2 model: F_{U*n:n} = prod (1 - p_i S_i)."""
    cu = shock_comps(comps_q_lam(q, beta, lam), p)
    cv = shock_comps(comps_q_lam(q, beta, lam_s), ps)
    hi = common_hi(None, [[(a, b, c) for (a, b, c, d) in cu],
                          [(a, b, c) for (a, b, c, d) in cv]])
    U = system(cu, "parallel", hi)
    V = system(cv, "parallel", hi)
    return cf.check("st", U, V), hi


def t51(part):
    """Theorem 5.1: parallel st shocks; lam common; wp(p) <=_w wp(p*);
    U*_{n:n} <=st V*_{n:n}.  wp(u)=u^2 and wp(u)=e^u-1 are both convex,
    differentiable and strictly increasing on [0,1]."""
    res = []
    # (lam in D+, p in E+ so that wp(p) in E+) and the alternative alignment.
    cases = [
        # lam (D+), p, p*, wp name
        ([R(3, 2), R(1), R(1, 2)], [R(1, 5), R(2, 5), R(3, 5)],
         [R(3, 10), R(1, 2), R(4, 5)], "sq"),
        ([R(3, 2), R(1), R(1, 2)], [R(1, 5), R(2, 5), R(3, 5)],
         [R(3, 10), R(1, 2), R(4, 5)], "cu"),
        ([R(1, 2), R(1), R(3, 2)], [R(3, 5), R(2, 5), R(1, 5)],
         [R(4, 5), R(1, 2), R(3, 10)], "sq"),   # lam E+, p D+ -> wp(p) D+
    ]
    for (lam, p, ps, wpn) in cases:
        wp = WP[wpn][1]
        u = [wp(R(v)) for v in p]          # u_i = wp(p_i), index-aligned
        us = [wp(R(v)) for v in ps]
        assert monotone(lam) and w_sub(sorted(u), sorted(us)), (lam, p, ps, wpn)
        # antagonistic pairing used in the proof: lam D+ <-> u E+, or
        # lam E+ <-> u D+
        assert (in_Dplus(lam) and in_Eplus(u)) or (in_Eplus(lam) and in_Dplus(u)), (lam, u)
        q = R(1, 2) if part == 1 else R(3, 2)
        for beta in [R(1, 2), R(1)]:
            (h, w, und), hi = shock_parallel_st(q, beta, lam, lam, p, ps)
            res.append({"holds": h, "witness": None if h else str(w), "undecided": und,
                        "notes": f"q={q},b={beta},lam={lam},p={p},p*={ps},wp={wpn},D={hi}"})
    return res


def t52(part):
    """Theorem 5.2: parallel st shocks; common shock vector (p* not stated in
    the relation, the proof uses one u_k sequence); lam <=^w lam*;
    lam,lam* in D+(E+), wp(p) in E+(D+); U*_{n:n} <=st V*_{n:n}."""
    res = []
    cases = [
        ([R(2), R(3, 2), R(1, 2)], [R(17, 10), R(7, 5), R(3, 10)],
         [R(1, 5), R(2, 5), R(3, 5)], "sq"),
        ([R(1, 2), R(3, 2), R(2)], [R(3, 10), R(7, 5), R(17, 10)],
         [R(3, 5), R(2, 5), R(1, 5)], "sq"),
        ([R(2), R(3, 2), R(1, 2)], [R(17, 10), R(7, 5), R(3, 10)],
         [R(1, 5), R(2, 5), R(3, 5)], "cu"),
    ]
    for (lam, lam_s, p, wpn) in cases:
        assert w_sup(lam, lam_s), (lam, lam_s)
        assert (in_Dplus(lam) and in_Dplus(lam_s)) or (in_Eplus(lam) and in_Eplus(lam_s))
        wp = WP[wpn][1]
        u = [wp(R(v)) for v in p]
        assert monotone(u)   # wp(p) in E+ or D+
        q = R(1, 2) if part == 1 else R(3, 2)
        for beta in [R(1, 2), R(2)]:
            (h, w, und), hi = shock_parallel_st(q, beta, lam, lam_s, p, p)
            res.append({"holds": h, "witness": None if h else str(w), "undecided": und,
                        "notes": f"q={q},b={beta},lam={lam},lam*={lam_s},p={p},wp={wpn},D={hi}"})
    return res


def shock_series_hr(q, beta, U, V):
    cu, cv = U, V
    hi = common_hi(None, [[(a, b, c) for (a, b, c, d) in cu],
                          [(a, b, c) for (a, b, c, d) in cv]])
    Uc = system(cu, "series", hi)
    Vc = system(cv, "series", hi)
    return cf.check("hr", Uc, Vc), hi


def t53(part):
    """Theorem 5.3: series hr shocks; prod p <= prod p*; U*_{1:n} <=hr V*_{1:n}.
    (1) lam >=_w lam*; (2) lam <=^w lam*."""
    res = []
    for (p, ps) in [([R(1, 4), R(1, 3), R(1, 2)], [R(1, 2), R(1, 2), R(1, 2)]),
                    ([R(1, 5), R(1, 4)], [R(3, 10), R(2, 5)])]:
        assert sp.prod(p) <= sp.prod(ps)
        insts = ([([R(1, 2), R(1), R(3, 2)], [R(3, 10), R(3, 5), R(9, 10)]),
                  ([R(1, 4), R(1, 2)], [R(1, 5), R(9, 20)])]
                 if part == 1 else
                 [([R(3, 2), R(2), R(5, 2)], [R(1), R(2), R(3)]),
                  ([R(3, 5), R(3, 2)], [R(3, 10), R(17, 10)])])
        for (lam, lam_s) in insts:
            if part == 1:
                assert geq_w(lam, lam_s), (lam, lam_s)
            else:
                assert w_sup(lam, lam_s), (lam, lam_s)
            q = R(1, 2) if part == 1 else R(3, 2)
            for beta in [R(1, 2), R(1)]:
                cu = shock_comps(comps_q_lam(q, beta, lam), p)
                cv = shock_comps(comps_q_lam(q, beta, lam_s), ps)
                (h, w, und), hi = shock_series_hr(q, beta, cu, cv)
                res.append({"holds": h, "witness": None if h else str(w), "undecided": und,
                            "notes": f"q={q},b={beta},lam={lam},lam*={lam_s},p={p},p*={ps},D={hi}"})
    return res


def t54(part):
    """Theorem 5.4: series hr shocks, heterogeneous q; prod p <= prod p*;
    q >=^w q* (i.e. q* <=^w q); U*_{1:n} <=hr V*_{1:n}."""
    res = []
    qcases = ([([R(1, 10), R(3, 5)], [R(3, 10), R(1, 2)]),
               ([R(1, 5), R(1, 2), R(7, 10)], [R(2, 5), R(3, 5), R(4, 5)])]
              if part == 1 else
              [([R(11, 10), R(8, 5)], [R(13, 10), R(3, 2)]),
               ([R(6, 5), R(13, 10), R(17, 10)], [R(13, 10), R(3, 2), R(9, 5)])])
    for (qv, qsv) in qcases:
        assert w_sup(qsv, qv), (qv, qsv)   # q* <=^w q  <=>  q >=^w q*
        for (p, ps) in [([R(1, 4), R(1, 3), R(1, 2)][:len(qv)],
                         [R(1, 2)] * len(qv))]:
            assert sp.prod(p) <= sp.prod(ps)
            q = R(1, 2) if part == 1 else R(3, 2)
            for (lam, beta) in [(R(1, 2), R(1)), (R(2), R(1, 2))]:
                cu = shock_comps(comps_qvec(lam, beta, qv), p)
                cv = shock_comps(comps_qvec(lam, beta, qsv), ps)
                (h, w, und), hi = shock_series_hr(q, beta, cu, cv)
                res.append({"holds": h, "witness": None if h else str(w), "undecided": und,
                            "notes": f"lam={lam},b={beta},q={qv},q*={qsv},p={p},p*={ps},D={hi}"})
    return res


def t55(part):
    """Theorem 5.5: series st shocks, heterogeneous beta; prod p >= prod p*;
    beta <=^m beta*; V*_{1:n} <=st U*_{1:n}."""
    res = []
    betas = [([R(1, 2), R(3, 2)], [R(3, 10), R(17, 10)]),
             ([R(1, 2), R(1), R(3, 2)], [R(1, 4), R(3, 4), R(2)])]
    for (bv, bsv) in betas:
        assert maj(bv, bsv)
        for (p, ps) in [([R(1, 2)] * len(bv), [R(1, 4), R(1, 3), R(1, 2)][:len(bv)])]:
            assert sp.prod(p) >= sp.prod(ps)
            q = R(1, 2) if part == 1 else R(3, 2)
            for lam in [R(1), R(1, 2)]:
                cu = shock_comps(comps_bvec(q, lam, bv), p)
                cv = shock_comps(comps_bvec(q, lam, bsv), ps)
                hi = common_hi(None, [[(a, b, c) for (a, b, c, d) in cu],
                                      [(a, b, c) for (a, b, c, d) in cv]])
                Uc = system(cu, "series", hi)
                Vc = system(cv, "series", hi)
                h, w, und = cf.check("st", Vc, Uc)
                res.append({"holds": h, "witness": None if h else str(w), "undecided": und,
                            "notes": f"q={q},lam={lam},b={bv},b*={bsv},p={p},p*={ps},D={hi}"})
    return res


# ------------------------------------------------------ printed examples ----

def ex(label, order, U_list, V_list, kind, direction):
    """Printed example check on the paper's common domain."""
    assert U_list and V_list
    hi = common_hi(None, [U_list, V_list])
    Uc = system(unshocked(U_list), kind, hi)
    Vc = system(unshocked(V_list), kind, hi)
    first, second = (Vc, Uc) if direction == "V<=U" else (Uc, Vc)
    r = run_instance(direction, order, first, second, f"common domain (0,{hi})")
    return {"claim": label, "order": order,
            "status": "holds" if r["holds"] else "refuted",
            "instances": 1, "witness": r["witness"], "undecided_points": r["undecided"]}


def exc(label, order, U_list, V_list, kind, primary):
    """Printed counterexample: non-comparability checked in both directions."""
    hi = common_hi(None, [U_list, V_list])
    Uc = system(unshocked(U_list), kind, hi)
    Vc = system(unshocked(V_list), kind, hi)
    first, second = (Vc, Uc) if primary == "V" else (Uc, Vc)
    return both_dirs(label, order, first, second)


DISPATCH = {
    # printed examples (independent)
    "Example 3.11 (case q < 1)": lambda l, o:
        ex(l, o, comps_q_lam("0.5", "0.5", ["0.5", "1.5"]),
           comps_q_lam("0.5", "0.5", ["0.3", "1.6"]), "parallel", "U<=V"),
    "Example 3.11 (case q > 1, Fig. 7(b))": lambda l, o:
        ex(l, o, comps_q_lam("1.5", "0.5", ["0.5", "1.5"]),
           comps_q_lam("1.5", "0.5", ["0.3", "1.6"]), "parallel", "U<=V"),
    "Example 3.11 (case q < 1, Fig. 7(a))": lambda l, o:
        ex(l, o, comps_q_lam("0.5", "0.5", ["0.5", "1.5"]),
           comps_q_lam("0.5", "0.5", ["0.3", "1.6"]), "parallel", "U<=V"),
    "Example 3.2 (case 0 < q < 1)": lambda l, o:
        ex(l, o, comps_q_lam("0.5", "0.5", ["0.5", "1.5"]),
           comps_q_lam("0.5", "0.5", ["0.3", "1.8"]), "series", "V<=U"),
    "Example 3.2 (case 0 < q < 1, Fig. 1(a))": lambda l, o:
        ex(l, o, comps_q_lam("0.5", "0.5", ["0.5", "1.5"]),
           comps_q_lam("0.5", "0.5", ["0.3", "1.8"]), "series", "V<=U"),
    "Example 3.2 (case q > 1)": lambda l, o:
        ex(l, o, comps_q_lam("1.5", "0.5", ["0.6", "1.5"]),
           comps_q_lam("1.5", "0.5", ["0.3", "1.7"]), "series", "U<=V"),
    "Example 3.2 (case q > 1, Fig. 1(b))": lambda l, o:
        ex(l, o, comps_q_lam("1.5", "0.5", ["0.6", "1.5"]),
           comps_q_lam("1.5", "0.5", ["0.3", "1.7"]), "series", "U<=V"),
    "Example 3.5 (case q < 1)": lambda l, o:
        ex(l, o, comps_qvec("0.5", "2", ["0.3", "0.5"]),
           comps_qvec("0.5", "2", ["0.1", "0.6"]), "series", "V<=U"),
    "Example 3.5 (case q < 1, Fig. 3(a))": lambda l, o:
        ex(l, o, comps_qvec("0.5", "2", ["0.3", "0.5"]),
           comps_qvec("0.5", "2", ["0.1", "0.6"]), "series", "V<=U"),
    "Example 3.5 (case q > 1, Fig. 3(b))": lambda l, o:
        ex(l, o, comps_qvec("0.5", "2", ["1.3", "1.5"]),
           comps_qvec("0.5", "2", ["1.1", "1.6"]), "series", "V<=U"),
    "Example 3.8 (case q < 1)": lambda l, o:
        ex(l, o, comps_bvec("0.5", "1", ["0.5", "1.5"]),
           comps_bvec("0.5", "1", ["0.3", "1.7"]), "series", "V<=U"),
    "Example 3.8 (case q < 1, Fig. 5(a))": lambda l, o:
        ex(l, o, comps_bvec("0.5", "1", ["0.5", "1.5"]),
           comps_bvec("0.5", "1", ["0.3", "1.7"]), "series", "V<=U"),
    # printed counterexamples
    "Example 3.3 (case 0 < q < 1)": lambda l, o:
        exc(l, o, comps_q_lam("0.5", "0.5", ["0.5", "1.5"]),
            comps_q_lam("0.5", "0.5", ["0.3", "1.7"]), "series", "U"),
    "Example 3.3 (case 0 < q < 1, Fig. 2(a))": lambda l, o:
        exc(l, o, comps_q_lam("0.5", "0.5", ["0.5", "1.5"]),
            comps_q_lam("0.5", "0.5", ["0.3", "1.7"]), "series", "U"),
    "Example 3.3 (case q > 1)": lambda l, o:
        exc(l, o, comps_q_lam("1.5", "2", ["0.5", "1.5"]),
            comps_q_lam("1.5", "2", ["0.3", "1.7"]), "series", "U"),
    "Example 3.3 (case q > 1, Fig. 2(b))": lambda l, o:
        exc(l, o, comps_q_lam("1.5", "2", ["0.5", "1.5"]),
            comps_q_lam("1.5", "2", ["0.3", "1.7"]), "series", "U"),
    "Example 3.6 (case 0 < max_l{q_l, q★_l} < 1)": lambda l, o:
        exc(l, o, comps_qvec("0.5", "2", ["0.2", "0.7"]),
            comps_qvec("0.5", "2", ["0.1", "0.8"]), "series", "U"),
    "Example 3.6 (case q < 1, Fig. 4(a))": lambda l, o:
        exc(l, o, comps_qvec("0.5", "2", ["0.2", "0.7"]),
            comps_qvec("0.5", "2", ["0.1", "0.8"]), "series", "U"),
    "Example 3.6 (case 1 < min_l{q_l, q★_l} < 2)": lambda l, o:
        exc(l, o, comps_qvec("0.5", "2", ["1.2", "1.7"]),
            comps_qvec("0.5", "2", ["1.1", "1.8"]), "series", "U"),
    "Example 3.6 (case q > 1, Fig. 4(b))": lambda l, o:
        exc(l, o, comps_qvec("0.5", "2", ["1.2", "1.7"]),
            comps_qvec("0.5", "2", ["1.1", "1.8"]), "series", "U"),
    "Example 3.9 (case 0 < q < 1)": lambda l, o:
        exc(l, o, comps_bvec("0.3", "0.5", ["0.5", "0.5"]),
            comps_bvec("0.3", "0.5", ["0.3", "0.7"]), "series", "V"),
    "Example 3.9 (case 0 < q < 1, Fig. 6(a))": lambda l, o:
        exc(l, o, comps_bvec("0.3", "0.5", ["0.5", "0.5"]),
            comps_bvec("0.3", "0.5", ["0.3", "0.7"]), "series", "V"),
    "Example 3.9 (case 1 < q < 2)": lambda l, o:
        exc(l, o, comps_bvec("1.3", "0.5", ["0.5", "0.5"]),
            comps_bvec("1.3", "0.5", ["0.3", "0.7"]), "series", "V"),
    "Example 3.9 (case 1 < q < 2, Fig. 6(b))": lambda l, o:
        exc(l, o, comps_bvec("1.3", "0.5", ["0.5", "0.5"]),
            comps_bvec("1.3", "0.5", ["0.3", "0.7"]), "series", "V"),
    # theorems (independent, testable)
    "Theorem 3.1(1)": lambda l, o: aggregate(l, o, t31(1)),
    "Theorem 3.1(2)": lambda l, o: aggregate(l, o, t31(2)),
    "Theorem 3.4(1)": lambda l, o: aggregate(l, o, t34(1)),
    "Theorem 3.4(2)": lambda l, o: aggregate(l, o, t34(2)),
    "Theorem 3.7(1)": lambda l, o: aggregate(l, o, t37(1)),
    "Theorem 3.7(2)": lambda l, o: aggregate(l, o, t37(2)),
    "Theorem 3.10(1)": lambda l, o: aggregate(l, o, t310(1)),
    "Theorem 3.10(2)": lambda l, o: aggregate(l, o, t310(2)),
    "Theorem 5.1(1)": lambda l, o: aggregate(l, o, t51(1)),
    "Theorem 5.1(2)": lambda l, o: aggregate(l, o, t51(2)),
    "Theorem 5.2(1)": lambda l, o: aggregate(l, o, t52(1)),
    "Theorem 5.2(2)": lambda l, o: aggregate(l, o, t52(2)),
    "Theorem 5.3(1)": lambda l, o: aggregate(l, o, t53(1)),
    "Theorem 5.3(2)": lambda l, o: aggregate(l, o, t53(2)),
    "Theorem 5.4(1)": lambda l, o: aggregate(l, o, t54(1)),
    "Theorem 5.4(2)": lambda l, o: aggregate(l, o, t54(2)),
    "Theorem 5.5(1)": lambda l, o: aggregate(l, o, t55(1)),
    "Theorem 5.5(2)": lambda l, o: aggregate(l, o, t55(2)),
}

COPULA_NOTE = ("Archimedean-copula/dependent-components claim: outside the "
               "independent-system harness (out of harness scope)")


def main():
    data = json.load(open(CANON))
    out = []
    for rec in data:
        label, order = rec["claim"], rec["conclusion"]["order"]
        if order not in ("st", "hr", "rh", "lr"):
            out.append(fixed(label, order, "unsupported order",
                             "harness supports st/hr/rh/lr only"))
            continue
        if "4.2" in label or "4.4" in label or "4.1" in label or "4.3" in label:
            out.append(fixed(label, order, "out of harness scope", COPULA_NOTE))
            continue
        fn = DISPATCH.get(label)
        if fn is None:
            out.append(fixed(label, order, "out of harness scope",
                             "no evaluator encoded for this record"))
            continue
        print(f"[eval] {label}", flush=True)
        out.append(fn(label, order))
    json.dump(out, open(OUT, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
