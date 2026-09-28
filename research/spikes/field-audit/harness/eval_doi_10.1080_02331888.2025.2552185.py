"""Evaluator for doi:10.1080/02331888.2025.2552185 (Kayal & co.: stochastic
comparisons of random extremes of dependent Kumaraswamy-G samples).

Reads canonical/doi_10.1080_02331888.2025.2552185.json and writes
eval_doi_10.1080_02331888.2025.2552185.result.json.

Model: X_i ~ Kw-G(α_i, γ_i; G), S_i(x) = (1 - G(x)^{α_i})^{γ_i}; same for Y_i
with (β_i, δ_i; H).  Random extremes mix over the sample-size law N:
    S_{X_{1:N}} = sum_m p_m prod_{i<=m} S_{X_i},
    S_{X_{N:N}} = 1 - sum_m p_m prod_{i<=m} F_{X_i}.

Independence claims (the paper's Section-3 second half fixes the Archimedean
survival copula at psi = e^{-x}) are exact-checked in z = e^{-x} via ratdist
whenever all parameters are integers (S_i are then polynomials in z);
otherwise closedform interval checks are used.

Claims that quantify over copulas, use the paper's printed copula-based
counterexamples, or involve Poisson-compounded applications are
'out of harness scope'.  'disp' records are 'unsupported order'.
"""

import json
import os

import sympy as sp
from mpmath import iv

import closedform as cf
import ratdist
from closedform import x
from ratdist import z

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.1080_02331888.2025.2552185.json")
OUT = os.path.join(HERE, "eval_doi_10.1080_02331888.2025.2552185.result.json")


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def wjson(w, varname="z"):
    if w is None:
        return None
    if isinstance(w, sp.Rational):
        return f"{varname} = {w.p}/{w.q} (~{float(w):.6g})"
    return str(w)


def dist(poly):
    """Dist on z = e^{-x} in (0,1), decreasing in x."""
    return ratdist.Dist(sp.expand(poly), sp.Integer(0), sp.Integer(1),
                        increasing=False)


def rcheck(order, Xp, Yp):
    """ratdist check X <=order Y; returns dict."""
    h, w = ratdist.ORDERS[order](dist(Xp), dist(Yp))
    return {"holds": h, "witness": w, "undecided": 0}


def combine(results):
    holds = all(r["holds"] for r in results)
    witness = None
    for r in results:
        if not r["holds"]:
            witness = wjson(r["witness"])
            break
    undec = sum(r["undecided"] for r in results)
    return {"holds": holds, "witness": witness, "undecided": undec,
            "instances": len(results)}


# baselines as polynomials in z = exp(-x):  G(x) = 1 - e^{-cx}
G1 = 1 - z            # Exp(1): r_g = 1
G2 = 1 - z ** 2       # Exp(2): r_g = 2


def kwg_surv(G, a, g):
    """Kw-G survival (1 - G^a)^g as a polynomial in z (integer a, g)."""
    return sp.expand((1 - G ** int(a)) ** int(g))


def min_surv(survs):
    p = sp.Integer(1)
    for s in survs:
        p *= s
    return sp.expand(p)


def max_surv(survs):
    """parallel survival 1 - prod(1 - S_i) = 1 - prod F_i."""
    p = sp.Integer(1)
    for s in survs:
        p *= (1 - s)
    return sp.expand(1 - p)


def rnd_surv(by_size, pmf):
    """sum_m p_m * surv_m;  by_size[m] is the size-m extreme survival."""
    tot = sp.Integer(0)
    for m, p in pmf.items():
        tot += sp.Rational(p) * by_size[m]
    return sp.expand(tot)


def min_sample(params, G, gam, n, pmf):
    """X_{1:N} survival: sum_m p_m prod_{i<=m} (1-G^{a_i})^{g_i}."""
    by = {}
    for m in pmf:
        S = [kwg_surv(G, params[i], gam[i]) for i in range(m)]
        by[m] = min_surv(S)
    return rnd_surv(by, pmf)


def max_sample(params, G, gam, n, pmf):
    """X_{N:N} survival: 1 - sum_m p_m prod_{i<=m} (1-(1-G^{a_i})^{g_i})."""
    by = {}
    for m in pmf:
        S = [kwg_surv(G, params[i], gam[i]) for i in range(m)]
        by[m] = max_surv(S)
    return rnd_surv(by, pmf)


# ----------------------------------------------------------------------------
# Theorem 3.7 (hr):  alpha=beta=1_n, r_g <= r_h:
#   "sum gamma_i <= sum delta_i  iff  X_{1:N} >=hr Y_{1:N}"   (printed iff)
# ----------------------------------------------------------------------------

def test_thm37():
    detail = []
    # ---- sufficiency instances (premise holds) ----
    # (a) random N on {1,2}, r_g = 1 <= 2 = r_h
    pmf = {1: R(1, 2), 2: R(1, 2)}
    SX = rnd_surv({1: kwg_surv(G1, 1, 1), 2: kwg_surv(G1, 1, 1) * kwg_surv(G1, 1, 2)}, pmf)
    SY = rnd_surv({1: kwg_surv(G2, 1, 3), 2: kwg_surv(G2, 1, 3) * kwg_surv(G2, 1, 1)}, pmf)
    detail.append(("suff-a", rcheck("hr", SY, SX)))   # Y <=hr X ?
    # (b) deterministic N=2, G=H
    SX = kwg_surv(G1, 1, 1) * kwg_surv(G1, 1, 2)
    SY = kwg_surv(G1, 1, 2) * kwg_surv(G1, 1, 2)
    detail.append(("suff-b", rcheck("hr", SY, SX)))
    # (c) random N, G=H
    SX = rnd_surv({1: kwg_surv(G1, 1, 1), 2: kwg_surv(G1, 1, 1) * kwg_surv(G1, 1, 1)}, pmf)
    SY = rnd_surv({1: kwg_surv(G1, 1, 2), 2: kwg_surv(G1, 1, 2) * kwg_surv(G1, 1, 2)}, pmf)
    detail.append(("suff-c", rcheck("hr", SY, SX)))
    # ---- necessity probes: premise violated (sum gamma > sum delta);
    # the iff requires the hr conclusion to FAIL there ----
    # (d) deterministic N=1: gamma1=2 <= delta1=3 but sums 7 > 6
    SX = kwg_surv(G1, 1, 2)          # z^2
    SY = kwg_surv(G1, 1, 3)          # z^3
    detail.append(("necc-d", rcheck("hr", SY, SX)))   # holds -> iff refuted
    # (e) random N: gamma=(1,3), delta=(2,1): sums 4 > 3
    SX = rnd_surv({1: kwg_surv(G1, 1, 1), 2: kwg_surv(G1, 1, 1) * kwg_surv(G1, 1, 3)}, pmf)
    SY = rnd_surv({1: kwg_surv(G1, 1, 2), 2: kwg_surv(G1, 1, 2) * kwg_surv(G1, 1, 1)}, pmf)
    detail.append(("necc-e", rcheck("hr", SY, SX)))
    # ---- literal-reading sufficiency probe: premise on total sums holds but
    # prefix sums violate it (gamma=(4,5) vs delta=(1,8), sums 9 <= 9) ----
    pmf2 = {1: R(9, 10), 2: R(1, 10)}
    SX = rnd_surv({1: kwg_surv(G1, 1, 4), 2: kwg_surv(G1, 1, 4) * kwg_surv(G1, 1, 5)}, pmf2)
    SY = rnd_surv({1: kwg_surv(G1, 1, 1), 2: kwg_surv(G1, 1, 1) * kwg_surv(G1, 1, 8)}, pmf2)
    detail.append(("litsuf-f", rcheck("hr", SY, SX)))
    return detail


def verdict_thm37(detail):
    """Iff claim.  Sufficiency instances must give holds=True; necessity
    probes must give holds=False (premise false -> conclusion must fail)."""
    notes = []
    suff_ok = all(r["holds"] for tag, r in detail if tag.startswith("suff"))
    refute_witness = None
    for tag, r in detail:
        if tag.startswith("necc") and r["holds"]:
            refute_witness = (f"{tag}: hr order held although sum gamma > "
                              f"sum delta (iff necessity fails)")
            notes.append(f"{tag}: conclusion holds without premise -> "
                         f"iff refuted")
        if tag.startswith("litsuf") and not r["holds"]:
            notes.append(f"{tag}: under the literal total-sums premise, "
                         f"sufficiency also fails (witness {wjson(r['witness'])})")
            if refute_witness is None:
                refute_witness = (f"{tag}: printed iff fails under literal "
                                  f"reading, witness {wjson(r['witness'])}")
    return {"suff_ok": suff_ok, "refute": refute_witness, "notes": notes}


# ----------------------------------------------------------------------------
# Theorem 3.8 (hr): alpha=beta=a 1_n, G=H, gamma (maj) delta read as
#   delta <=^m gamma: equal sums, delta lower-sums >= gamma lower-sums
#   => X_{1:N} >=hr Y_{1:N}   (i.e. check hr(Y, X): h_Y >= h_X)
# ----------------------------------------------------------------------------

def test_thm38():
    """returns list of (tag, result)."""
    res = []
    a = 2                       # common scalar tilt
    K = kwg_surv(G1, a, 1)      # (1-G^a)^1 = 2z - z^2
    pmf = {1: R(1, 2), 2: R(1, 2)}
    # gamma=(1,3), delta=(2,2): equal sums 4, delta asc sums >= gamma's.
    SX = rnd_surv({1: K ** 1, 2: K ** 4}, pmf)
    SY = rnd_surv({1: K ** 2, 2: K ** 4}, pmf)
    res.append(("asc-a", rcheck("hr", SY, SX)))
    # gamma=(1,1,4), delta=(2,2,2), N uniform {1,2,3}; prefix sums of gamma
    # (listed ascending) 1,2,6 ; delta 2,4,6.
    pmf3 = {1: R(1, 3), 2: R(1, 3), 3: R(1, 3)}
    SX = rnd_surv({1: K, 2: K ** 2, 3: K ** 6}, pmf3)
    SY = rnd_surv({1: K ** 2, 2: K ** 4, 3: K ** 6}, pmf3)
    res.append(("asc-b", rcheck("hr", SY, SX)))
    # same vectors listed descending gamma=(4,1,1): prefix sums 4,5,6 —
    # premise (order-free) still satisfied; conclusion may flip.
    SX = rnd_surv({1: K ** 4, 2: K ** 5, 3: K ** 6}, pmf3)
    res.append(("desc-c", rcheck("hr", SY, SX)))
    # a = 3 variant, ascending listing
    K3 = kwg_surv(G1, 3, 1)
    SX = rnd_surv({1: K3, 2: K3 ** 4}, pmf)
    SY = rnd_surv({1: K3 ** 2, 2: K3 ** 4}, pmf)
    res.append(("asc-d", rcheck("hr", SY, SX)))
    return res


# ----------------------------------------------------------------------------
# Theorem 3.9 (hr): gamma=delta, G=H, alpha >=w beta read as beta <=^w alpha
#   (beta's ascending partial sums >= alpha's)  => X_{1:N} >=hr Y_{1:N}.
# Conflicts with Thm 3.10 under the same reading (G=H satisfies r_g>=r_h).
# ----------------------------------------------------------------------------

def thm39_instances():
    pmf = {1: R(1, 3), 2: R(1, 3), 3: R(1, 3)}
    out = []
    # adjudicated reading, integer params: alpha=(1,1,2), beta=(2,2,2),
    # gamma=delta=(1,1,1): prefix alpha-sums 1,2,4 ; beta 2,4,6.
    alphas, betas, gam = (1, 1, 2), (2, 2, 2), (1, 1, 1)
    SX = min_sample(alphas, G1, gam, 3, pmf)
    SY = min_sample(betas, G1, gam, 3, pmf)
    out.append(("adj-a", SX, SY))
    # gamma=delta=(1,1,2) in E+
    gam = (1, 1, 2)
    SX = min_sample(alphas, G1, gam, 3, pmf)
    SY = min_sample(betas, G1, gam, 3, pmf)
    out.append(("adj-b", SX, SY))
    # alternative reading (alpha weakly SUPERmajorizes beta: alpha's
    # descending partial sums >= beta's): alpha=(2,3,3), beta=(2,2,2).
    SX = min_sample((2, 3, 3), G1, (1, 1, 1), 3, pmf)
    SY = min_sample((2, 2, 2), G1, (1, 1, 1), 3, pmf)
    out.append(("alt-c", SX, SY))
    return out


def test_thm39():
    res = []
    for tag, SX, SY in thm39_instances():
        r = rcheck("hr", SY, SX)              # claim: Y <=hr X
        r["tag"] = tag
        res.append(r)
    return res


# ----------------------------------------------------------------------------
# Theorem 3.10 (hr): same premise, r_g >= r_h (G=H satisfies) =>
#   X_{1:N} <=hr Y_{1:N}  (check hr(X, Y)).
# ----------------------------------------------------------------------------

def test_thm310():
    res = []
    pmf = {1: R(1, 3), 2: R(1, 3), 3: R(1, 3)}
    # G=H (r_g = r_h satisfies >=)
    SX = min_sample((1, 1, 2), G1, (1, 1, 1), 3, pmf)
    SY = min_sample((2, 2, 2), G1, (1, 1, 1), 3, pmf)
    res.append(rcheck("hr", SX, SY))
    # strict r_g > r_h: G=Exp(2), H=Exp(1); alpha=(1,2),beta=(2,3) in E+,
    # gamma=delta=(1,2) in E+, N on {1,2}.
    pmf2 = {1: R(1, 2), 2: R(1, 2)}
    SX = min_sample((1, 2), G2, (1, 2), 2, pmf2)
    SY = min_sample((2, 3), G1, (1, 2), 2, pmf2)
    res.append(rcheck("hr", SX, SY))
    # D+ (decreasing) listing variant: alpha=(2,1,1), beta=(2,2,2), G=H
    SX = min_sample((2, 1, 1), G1, (1, 1, 1), 3, pmf)
    SY = min_sample((2, 2, 2), G1, (1, 1, 1), 3, pmf)
    res.append(rcheck("hr", SX, SY))
    return res


# ----------------------------------------------------------------------------
# Theorem 3.12 (rh): gamma_i=delta_i=gamma scalar, alpha,beta >= 1_n, ordered,
#   beta <=^w alpha (adjudicated), G <= H and g >= h (satisfiable only with
#   equality for distinct cdfs -> G=H) => X_{N:N} >=rh Y_{N:N} (check rh(Y,X)).
# ----------------------------------------------------------------------------

def test_thm312():
    res = []
    pmf = {1: R(1, 3), 2: R(1, 3), 3: R(1, 3)}
    g = 2
    # adjudicated reading: beta bigger -> Y bigger -> Y >=rh X expected;
    # printed claims X >=rh Y.
    SX = max_sample((1, 1, 2), G1, (g,) * 3, 3, pmf)
    SY = max_sample((2, 2, 2), G1, (g,) * 3, 3, pmf)
    res.append(("adj", rcheck("rh", SY, SX)))          # Y <=rh X ?
    # alternative reading (alpha supermajorizes beta): alpha bigger.
    SX = max_sample((2, 3, 3), G1, (g,) * 3, 3, pmf)
    SY = max_sample((2, 2, 2), G1, (g,) * 3, 3, pmf)
    res.append(("alt", rcheck("rh", SY, SX)))
    # deterministic N=3 spot check, adjudicated
    SX = max_sample((1, 1, 2), G1, (g,) * 3, 3, {3: R(1)})
    SY = max_sample((2, 2, 2), G1, (g,) * 3, 3, {3: R(1)})
    res.append(("adj-det", rcheck("rh", SY, SX)))
    return res


# ----------------------------------------------------------------------------
# Theorem 3.15 (lr): two-group (a1 1_p, a2 1_q) vs (b1 1_p, b2 1_q),
#   a1 <= a2 <= b2 <= b1, read as (b) <=^m (a).  Exact majorization forces
#   a1=a2=b1=b2 (trivial); under the live weak reading the conclusion is
#   testable: claim X_{1:N} >=lr Y_{1:N}  (check lr(Y, X)).
# ----------------------------------------------------------------------------

def test_thm315():
    res = []
    pmf = {1: R(1, 2), 2: R(1, 2)}
    g = 1
    # weak-majorization instance: a1=1,a2=2,b1=3,b2=2  (1<=2<=2<=3);
    # beta asc sums (2,5) >= alpha asc sums (1,3).
    SX = min_sample((1, 2), G1, (g, g), 2, pmf)
    SY = min_sample((3, 2), G1, (g, g), 2, pmf)
    res.append(("weak-n2", rcheck("lr", SY, SX)))      # Y <=lr X ?
    # n=4, p=q=2: a=(1,1,2,2), b=(3,3,2,2)  [listed in the theorem's order]
    pmf4 = {1: R(1, 4), 2: R(1, 4), 3: R(1, 4), 4: R(1, 4)}
    SX = min_sample((1, 1, 2, 2), G1, (g,) * 4, 4, pmf4)
    SY = min_sample((3, 3, 2, 2), G1, (g,) * 4, 4, pmf4)
    res.append(("weak-n4", rcheck("lr", SY, SX)))
    # trivial (exact-majorization) instance: all equal -> equality holds
    SX = min_sample((2, 2), G1, (g, g), 2, pmf)
    SY = min_sample((2, 2), G1, (g, g), 2, pmf)
    res.append(("trivial", rcheck("lr", SY, SX)))
    return res


# ----------------------------------------------------------------------------
# Theorem 3.17 (lr): alpha=beta=1, G=H, two-group gamma1 >= gamma >= delta1
#   => X_{1:N} <=lr Y_{1:N}  (check lr(X, Y)).
# ----------------------------------------------------------------------------

def test_thm317():
    res = []
    pmf = {1: R(1, 2), 2: R(1, 2)}
    # gamma1=3 >= gamma=2 >= delta1=1 ; X=(3,2), Y=(1,2), S_i = (1-G)^g = z^g
    SX = rnd_surv({1: z ** 3, 2: z ** 5}, pmf)
    SY = rnd_surv({1: z ** 1, 2: z ** 3}, pmf)
    res.append(rcheck("lr", SX, SY))
    # n=3, p=1,q=2: gamma=(3,2,2), delta=(1,2,2): prefix sums 3,5,7 vs 1,3,5
    pmf3 = {1: R(1, 3), 2: R(1, 3), 3: R(1, 3)}
    SX = rnd_surv({1: z ** 3, 2: z ** 5, 3: z ** 7}, pmf3)
    SY = rnd_surv({1: z ** 1, 2: z ** 3, 3: z ** 5}, pmf3)
    res.append(rcheck("lr", SX, SY))
    # deterministic N=n=3
    SX = z ** 7
    SY = z ** 5
    res.append(rcheck("lr", SX, SY))
    return res


# ----------------------------------------------------------------------------
# Theorem 3.18 (lr): gamma=delta=1, alpha1 >= alpha >= beta1 =>
#   X_{1:N} <=lr Y_{1:N}.  (X has bigger first-group shape -> X_min >=st
#   Y_min, so the printed <=lr direction looks reversed.)
# ----------------------------------------------------------------------------

def test_thm318():
    res = []
    pmf = {1: R(1, 2), 2: R(1, 2)}
    # a1=3 >= a=2 >= b1=1 ; X=(3,2), Y=(1,2); F_i = G^{a_i} = (1-z)^{a_i}
    sxa1 = kwg_surv(G1, 3, 1)
    sxa2 = kwg_surv(G1, 2, 1)
    syb1 = kwg_surv(G1, 1, 1)
    SX = rnd_surv({1: sxa1, 2: sxa1 * sxa2}, pmf)
    SY = rnd_surv({1: syb1, 2: syb1 * sxa2}, pmf)
    res.append(rcheck("lr", SX, SY))                  # X <=lr Y ?
    res.append(rcheck("lr", SY, SX))                  # opposite direction
    res.append(rcheck("st", SX, SY))                  # X <=st Y ?
    res.append(rcheck("st", SY, SX))                  # Y <=st X ?
    # deterministic N=2
    res.append(rcheck("lr", sxa1 * sxa2, syb1 * sxa2))
    return res


# ----------------------------------------------------------------------------
# dispatch
# ----------------------------------------------------------------------------

TESTED = {
    "Theorem 3.7": "thm37",
    "Theorem 3.8": "thm38",
    "Theorem 3.9": "thm39",
    "Theorem 3.10": "thm310",
    "Theorem 3.12": "thm312",
    "Theorem 3.15": "thm315",
    "Theorem 3.17": "thm317",
    "Theorem 3.18": "thm318",
}

OUT_OF_SCOPE = {
    "Counterexample 3.1": "Archimedean (Gumbel) copulas psi1 != psi2, random maxima — dependence",
    "Counterexample 3.2": "Archimedean (Gumbel) copulas, random minima — dependence",
    "Counterexample 3.3": "Archimedean (Gumbel) copulas, random minima — dependence",
    "Remark 3.2": "hedged 'can also be true' statement over copulas — non-checkable quantification",
    "Theorem 3.1": "quantifies over Archimedean copula generators psi1, psi2 — dependence",
    "Section 4.1 application (first activation scheme, via Theorem 3.1 as premise)": "application via copula theorem — dependence",
    "Theorem 3.2": "quantifies over copula generators — dependence",
    "Theorem 3.3": "quantifies over copula generators — dependence",
    "Theorem 3.4": "quantifies over copula generators — dependence",
    "Section 4.1 application (last activation scheme, via Theorem 3.4 as premise)": "application via copula theorem — dependence",
    "Section 4.2 application (transportation, via Theorem 3.4)": "application via copula theorem + Poisson N — dependence",
    "Theorem 3.16": "quantifies over a general Archimedean generator psi satisfying regularity conditions — copula quantification",
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
        elif label in OUT_OF_SCOPE:
            entry.update({"status": "out of harness scope", "instances": 0,
                          "witness": None, "undecided_points": 0,
                          "note": OUT_OF_SCOPE[label]})
        elif label == "Theorem 3.7":
            detail = test_thm37()
            v = verdict_thm37(detail)
            if v["refute"]:
                status = "refuted"
            elif v["suff_ok"]:
                status = "holds"
            else:
                status = "refuted"
            entry.update({"status": status,
                          "instances": len(detail),
                          "witness": v["refute"],
                          "undecided_points": 0,
                          "note": " ; ".join(v["notes"])})
        elif label == "Theorem 3.8":
            res = test_thm38()
            c = combine([r for t_, r in res])
            asc = [r for t_, r in res if t_.startswith("asc")]
            desc = [r for t_, r in res if t_.startswith("desc")]
            note = None
            if all(r["holds"] for r in asc) and not all(r["holds"] for r in desc):
                note = ("holds for ascending-listed gamma but FAILS when the "
                        "same vector is listed in descending order "
                        f"(witness {wjson(desc[0]['witness'])}) — the printed "
                        "premise (majorization) is order-free but the "
                        "conclusion is not; status reflects this ambiguity")
            status = "holds" if c["holds"] else "refuted"
            if desc and not all(r["holds"] for r in desc) and c["holds"]:
                status = "ambiguous hypotheses"
            entry.update({"status": status,
                          "instances": len(res),
                          "witness": c["witness"],
                          "undecided_points": c["undecided"]})
            if note:
                entry["note"] = note
        elif label == "Theorem 3.9":
            res = test_thm39()
            adj = [r for r in res if r["tag"].startswith("adj")]
            alt = [r for r in res if r["tag"].startswith("alt")]
            adj_ok = all(r["holds"] for r in adj)
            alt_ok = all(r["holds"] for r in alt)
            if not adj_ok and alt_ok:
                status = "ambiguous hypotheses"
                w = wjson(next(r["witness"] for r in adj if not r["holds"]))
                note = ("fails under the adjudicated beta <=w alpha reading "
                        f"(witness {w}) but holds under the converse "
                        "alpha-supermajorization reading; the printed glyph "
                        "is undefined in the paper")
            elif not adj_ok and not alt_ok:
                status = "refuted"
                w = wjson(next(r["witness"] for r in res if not r["holds"]))
                note = "fails under both majorization readings"
            else:
                status = "holds" if adj_ok else "ambiguous hypotheses"
                w = None
                note = None
            entry.update({"status": status, "instances": len(res),
                          "witness": w, "undecided_points": 0})
            if note:
                entry["note"] = note
        elif label == "Theorem 3.12":
            res = test_thm312()
            adj = [r for t, r in res if t.startswith("adj")]
            alt = [r for t, r in res if t.startswith("alt")]
            adj_ok = all(r["holds"] for r in adj)
            alt_ok = all(r["holds"] for r in alt)
            if not adj_ok and alt_ok:
                status = "ambiguous hypotheses"
                w = wjson(next(r["witness"] for t, r in res
                               if t.startswith("adj") and not r["holds"]))
                note = ("fails under adjudicated beta <=w alpha reading; "
                        "holds under converse reading; 'G <= H and g >= h' "
                        "only satisfiable with G=H")
            elif not adj_ok and not alt_ok:
                status = "refuted"
                w = wjson(next(r["witness"] for t, r in res if not r["holds"]))
                note = "fails under both readings"
            else:
                status = "holds" if adj_ok else "ambiguous hypotheses"
                w = None
                note = None
            entry.update({"status": status, "instances": len(res),
                          "witness": w, "undecided_points": 0})
            if note:
                entry["note"] = note
        elif label == "Theorem 3.15":
            res = test_thm315()
            weak = [r for t, r in res if t.startswith("weak")]
            weak_fail = [r for r in weak if not r["holds"]]
            if weak_fail:
                entry.update({"status": "ambiguous hypotheses",
                              "instances": len(res),
                              "witness": wjson(weak_fail[0]["witness"]),
                              "undecided_points": 0,
                              "note": ("under the canonical exact-majorization "
                                       "reading the premise alpha1<=a2<=b2<=b1 "
                                       "with equal sums collapses to "
                                       "alpha=beta (claim vacuous); under the "
                                       "live weak-majorization reading the "
                                       "conclusion fails as printed")})
            else:
                entry.update({"status": "holds", "instances": len(res),
                              "witness": None, "undecided_points": 0})
        elif label == "Theorem 3.18":
            res = test_thm318()
            fwd, rev, stx, sty, det = res
            if not fwd["holds"]:
                entry.update({"status": "refuted",
                              "instances": len(res),
                              "witness": wjson(fwd["witness"]),
                              "undecided_points": 0,
                              "note": ("X_1's alpha=3 > beta_1=1 makes X "
                                       "components stochastically larger, so "
                                       "X_{1:N} >=st Y_{1:N}; the printed "
                                       "<=lr direction fails. Opposite lr "
                                       f"holds: {rev['holds']}; st check: "
                                       f"Y<=st X holds={sty['holds']}")})
            else:
                entry.update({"status": "holds", "instances": len(res),
                              "witness": None, "undecided_points": 0})
        else:
            res = {"Theorem 3.10": test_thm310, "Theorem 3.17": test_thm317}[label]()
            c = combine(res)
            entry.update({"status": "holds" if c["holds"] else "refuted",
                          "instances": c["instances"],
                          "witness": c["witness"],
                          "undecided_points": c["undecided"]})
        out.append(entry)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    for e in out:
        print(f'{e["status"]:22} {e["order"]:6} {e["claim"][:75]}')
        if e.get("note"):
            print(f'{"":22} note: {e["note"][:110]}')
    print("wrote", OUT)


if __name__ == "__main__":
    main()
