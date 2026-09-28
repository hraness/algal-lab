"""Evaluator for doi:10.1017/S026996482400007X (Chaudhary, Kayal & co.:
ordering results on extremes of dependent extended-Weibull samples).

Reads canonical/doi_10.1017_s026996482400007x.json and writes
eval_doi_10.1017_s026996482400007x.result.json.

EW marginals:  S_i(x) = alpha_i e^{-(lam_i x)^k} / (1 - (1-alpha_i) e^{-(lam_i x)^k}),
checked directly in closedform (interval arithmetic on the printed
expressions).  Theorems 3.7-3.9 explicitly set the Archimedean survival
copulas to independence (psi1 = psi2 = e^{-x}), so the system survivals are
the plain products / cdf products over the sample:
    series  X_{1:n}:  prod S_i,      parallel X_{n:n}:  1 - prod (1 - S_i).

All copula-quantified records (psi1, psi2 arbitrary Archimedean generators;
the paper's Gumbel/Clayton counterexamples; the random-size-N results) are
'out of harness scope' — the frozen harness has no copula dependence.  The
dispersive, star and Lorenz orders are 'unsupported order'.

Majorization convention (paper's own Definition 2.1):  c is 'weakly
supermajorized by' d (c <=w_sup d) iff sum_{i=1}^l c_{i:n} >= sum d_{i:n}
(ascending partial sums).  The preamble to Theorems 3.8/3.9 names 'weakly
super-majorization', so the adjudicated reading of alpha >=w beta is
'beta <=w_sup alpha', i.e. beta's ascending sums dominate alpha's.  The
converse reading is tested as a sensitivity check.
"""

import json
import os

import sympy as sp

import closedform as cf
from closedform import x

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.1017_s026996482400007x.json")
OUT = os.path.join(HERE, "eval_doi_10.1017_s026996482400007x.result.json")

t = x


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def wjson(w):
    if w is None:
        return None
    if isinstance(w, sp.Rational):
        return f"t = {w.p}/{w.q} (~{float(w):.6g})"
    return str(w)


def chk(order, SA, SB, hi=sp.oo):
    h, w, u = cf.check(order, cf.Closed(SA, hi=hi), cf.Closed(SB, hi=hi))
    return {"holds": h, "witness": w, "undecided": u}


def combine(results):
    """list of (tag, res) -> aggregate dict."""
    holds = all(r["holds"] for _, r in results)
    witness = None
    for tag, r in results:
        if not r["holds"]:
            witness = f"{tag}: {wjson(r['witness'])}"
            break
    undec = sum(r["undecided"] for _, r in results)
    return {"holds": holds, "witness": witness, "undecided": undec,
            "instances": len(results)}


# ----------------------------------------------------------------------------
# EW model
# ----------------------------------------------------------------------------

def ew_surv(a, lam, k):
    """S(x) = a e^{-(lam x)^k} / (1 - (1-a) e^{-(lam x)^k})."""
    e = sp.exp(-(R(lam) * t) ** R(k))
    return R(a) * e / (1 - (1 - R(a)) * e)


def ew_min(params, lam, k):
    """series survival prod S_i."""
    return sp.prod([ew_surv(a, lam, k) for a in params])


def ew_max(params, lam, k):
    """parallel survival 1 - prod (1 - S_i)."""
    return sp.expand(1 - sp.prod([1 - ew_surv(a, lam, k) for a in params]))


def majorizes(a, b, kind="sup"):
    """Does a '>=w' b under the named reading?

    sup : b's ascending partial sums >= a's  (beta bottom-dominant;
          the reading named 'weakly super-majorization' in the preamble).
    sub : a's descending partial sums >= b's (alpha top-dominant).
    """
    sa = sorted(sp.Rational(v) for v in a)
    sb = sorted(sp.Rational(v) for v in b)
    n = len(sa)
    if kind == "sup":
        return all(sum(sb[:l]) >= sum(sa[:l]) for l in range(1, n + 1))
    else:
        return all(sum(sa[n - l:]) >= sum(sb[n - l:]) for l in range(1, n + 1))


# ----------------------------------------------------------------------------
# Theorem 3.7 (hr): lambda ⪰^m mu (lambda more spread), alpha scalar, k >= 1
#   => Y_{1:n} ⪰hr X_{1:n}   i.e. X <=hr Y :  hr(X, Y).
# ----------------------------------------------------------------------------

def test_thm37():
    res = []
    cases = [
        # (alpha scalar, k, lam, mu) with lam ⪰^m mu (equal totals, more spread)
        (R(1, 2), 2, (3, 2, 1), (2, 2, 2)),
        (R(1),   1, (4, 1, 1), (2, 2, 2)),
        (R(1, 3), R(3, 2), (5, 2), (R(7, 2), R(7, 2))),
        (R(4, 5), 3, (5, 3, 1), (3, 3, 3)),
    ]
    for a, k, lam, mu in cases:
        # premise check: lam ⪰^m mu  <=>  mu ⪯^m lam  <=>  mu asc-sums >=
        # lam asc-sums with equal totals.
        sa, sb = sorted(lam), sorted(mu)
        assert sum(lam) == sum(mu)
        assert all(sum(sb[:l]) >= sum(sa[:l]) for l in range(1, len(sa) + 1))
        # per-component rates: S_i uses lam_i
        SX = sp.prod([ew_surv(a, li, k) for li in lam])
        SY = sp.prod([ew_surv(a, mi, k) for mi in mu])
        res.append((f"a={a},k={k}", chk("hr", SX, SY)))
    return res


# ----------------------------------------------------------------------------
# Theorem 3.8 (hr): alpha ⪰w beta, same lam, k => Y_{1:n} ⪰hr X_{1:n}
#   i.e. X <=hr Y : hr(X, Y).
# Adjudicated reading (preamble: weakly super-majorization): beta's
# ascending partial sums >= alpha's -> beta bigger -> Y bigger -> h_Y <= h_X.
# ----------------------------------------------------------------------------

def _weak_sup_pairs():
    """(alpha, beta) with beta's ascending sums >= alpha's (super reading),
    strictly, and alpha NOT top-dominant over beta."""
    return [
        ((R(1, 2), R(9, 10)), (R(7, 10), R(4, 5))),
        ((R(1, 2), R(3, 5), R(9, 10)), (R(7, 10), R(4, 5), R(4, 5))),
        ((R(1, 2), R(1, 2)), (R(3, 4), R(3, 4))),
    ]


def _weak_sub_pairs():
    """alpha top-dominant over beta only (converse reading)."""
    return [
        ((R(9, 10), R(3, 5)), (R(3, 5), R(7, 10))),
        ((R(9, 10), R(7, 10), R(3, 5)), (R(3, 5), R(7, 10), R(4, 5))),
    ]


def _sup_reverse_pairs():
    """'alpha supermajorizes beta' reading: alpha's ascending sums >= beta's
    (alpha bottom-dominant; the non-converse parse of the same glyph)."""
    return [
        ((R(3, 5), R(4, 5)), (R(1, 2), R(9, 10))),
        ((R(3, 4), R(3, 4)), (R(1, 2), R(1, 2))),
    ]


def test_thm38():
    res = []
    for a, b in _weak_sup_pairs():
        assert majorizes(a, b, "sup"), (a, b)
        SX = ew_min(a, 1, 1)
        SY = ew_min(b, 1, 1)
        res.append((f"sup {a}", chk("hr", SX, SY)))
    for a, b in _weak_sub_pairs():
        assert majorizes(a, b, "sub") and not majorizes(a, b, "sup")
        SX = ew_min(a, 1, 1)
        SY = ew_min(b, 1, 1)
        res.append((f"sub {a}", chk("hr", SX, SY)))
    # 'alpha supermajorizes beta' parse of the same glyph (alpha asc-dominant)
    for a, b in _sup_reverse_pairs():
        sa, sb = sorted(a), sorted(b)
        assert all(sum(sa[:l]) >= sum(sb[:l]) for l in range(1, len(sa) + 1))
        SX = ew_min(a, 1, 1)
        SY = ew_min(b, 1, 1)
        res.append((f"suprev {a}", chk("hr", SX, SY)))
    # k = 3/2 variants under super reading
    for a, b in _weak_sup_pairs()[:2]:
        SX = ew_min(a, 1, R(3, 2))
        SY = ew_min(b, 1, R(3, 2))
        res.append((f"sup-k32 {a}", chk("hr", SX, SY)))
    return res


# ----------------------------------------------------------------------------
# Theorem 3.9 (rh): alpha ⪰w beta, same lam => Y_{n:n} ⪰rh X_{n:n}
#   i.e. X <=rh Y : rh(X, Y).
# ----------------------------------------------------------------------------

def test_thm39():
    res = []
    for a, b in _weak_sup_pairs():
        SX = ew_max(a, 1, 1)
        SY = ew_max(b, 1, 1)
        res.append((f"sup {a}", chk("rh", SX, SY)))
    for a, b in _weak_sub_pairs():
        SX = ew_max(a, 1, 1)
        SY = ew_max(b, 1, 1)
        res.append((f"sub {a}", chk("rh", SX, SY)))
    for a, b in _sup_reverse_pairs():
        SX = ew_max(a, 1, 1)
        SY = ew_max(b, 1, 1)
        res.append((f"suprev {a}", chk("rh", SX, SY)))
    for a, b in _weak_sup_pairs()[:2]:
        SX = ew_max(a, 1, R(3, 2))
        SY = ew_max(b, 1, R(3, 2))
        res.append((f"sup-k32 {a}", chk("rh", SX, SY)))
    return res


# ----------------------------------------------------------------------------
# dispatch
# ----------------------------------------------------------------------------

OUT_OF_SCOPE_PREFIXES = (
    "Counterexample", "Example",
)

OUT_OF_SCOPE = {
    "Theorem 3.1": "quantifies over Archimedean survival copula generators psi1, psi2 — dependence",
    "Theorem 3.2": "copula-quantified (psi1, psi2, super-additivity) — dependence",
    "Theorem 3.3": "copula-quantified — dependence",
    "Theorem 3.4": "copula-quantified — dependence",
    "Theorem 3.5": "copula-quantified — dependence",
    "Theorem 3.6": "copula-quantified — dependence",
    "Theorem 3.10": "copula-quantified — dependence",
    "Theorem 3.13": "random-size extremes under copulas — dependence",
    "Theorem 3.14": "random-size extremes under copulas — dependence",
    "Theorem 3.15": "random-size extremes under copulas — dependence",
    "Theorem 3.16": "random-size extremes under copulas — dependence",
    "Theorem 3.17": "random-size extremes under copulas — dependence",
    "Theorem 3.18": "random-size extremes under copulas — dependence",
}

TESTS = {
    "Theorem 3.7": test_thm37,
    "Theorem 3.8": test_thm38,
    "Theorem 3.9": test_thm39,
}

NOTES = {
    "Theorem 3.8": "preamble fixes 'weakly super-majorization' (beta asc sums >= alpha's); converse sub-reading instances are included as sensitivity",
    "Theorem 3.9": "same weak-order glyph caveat as Theorem 3.8",
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
            res = TESTS[label]()
            sup = [(t_, r) for t_, r in res
                   if t_.startswith("sup ") or t_.startswith("sup-")]
            sub = [(t_, r) for t_, r in res if t_.startswith("sub")]
            suprev = [(t_, r) for t_, r in res if t_.startswith("suprev")]
            note = NOTES.get(label)
            if not sup and not sub and not suprev:
                # Thm 3.7: exact majorization — no ambiguity.
                c = combine(res)
                status = "holds" if c["holds"] else "refuted"
                witness = c["witness"]
            else:
                # adjudicated reading = weak super-majorization converse
                # (preamble-named): beta's ascending sums dominate alpha's.
                sup_ok = all(r["holds"] for _, r in sup)
                alt_groups = {"sub": sub, "suprev": suprev}
                alt_fail = {k: [r for _, r in v if not r["holds"]]
                            for k, v in alt_groups.items() if v}
                if sup_ok:
                    status = "holds"
                    witness = None
                    fails = {k: v for k, v in alt_fail.items() if v}
                    if fails:
                        subw = wjson(next(iter(fails.values()))[0]["witness"])
                        note = (note or "") + (
                            "; NOTE: the claim FAILS under the converse "
                            "readings " + ", ".join(fails)
                            + f" (witness {subw}) — verdict is under the "
                            "preamble-named weak super-majorization "
                            "converse reading")
                else:
                    status = "refuted"
                    witness = wjson(next(r["witness"]
                                         for _, r in sup if not r["holds"]))
            c = combine(res)
            entry.update({"status": status,
                          "instances": c["instances"],
                          "witness": witness,
                          "undecided_points": c["undecided"]})
            if note:
                entry["note"] = note
        elif label in OUT_OF_SCOPE or label.startswith(OUT_OF_SCOPE_PREFIXES):
            entry.update({"status": "out of harness scope", "instances": 0,
                          "witness": None, "undecided_points": 0,
                          "note": OUT_OF_SCOPE.get(
                              label, "copula-dependent example/counterexample")})
        else:
            entry.update({"status": "out of harness scope", "instances": 0,
                          "witness": None, "undecided_points": 0,
                          "note": "no evaluator mapping"})
        out.append(entry)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    for e in out:
        print(f'{e["status"]:22} {e["order"]:8} {e["claim"][:75]}')
        if e.get("note"):
            print(f'{"":22} note: {e["note"][:110]}')
    print("wrote", OUT)


if __name__ == "__main__":
    main()
