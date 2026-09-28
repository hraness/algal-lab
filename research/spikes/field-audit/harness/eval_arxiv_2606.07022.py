"""Evaluator for arxiv:2606.07022 -- integral orders of m-generalized order
statistics (m-GOS) from transform-ordered families.

Uniform-baseline m-GOS density (paper eq. (6)-(7)):
    f_{r,g,m}(x) = M(r,g,m)/(r-1)! * (1-x)^{g-1} * g_m(x)^{r-1}, 0<x<1
    g_m(x) = (1-(1-x)^m)/m   (m != 0),   g_0(x) = -ln(1-x)
    M(r,g,m) = prod_{i=1}^r (g + (i-1)m)

Expanding g_m^{r-1} gives the survival function in closed form for
rational m > 0:
    S_{r,g,m}(x) = M/((r-1)! m^{r-1}) *
        sum_{k=0}^{r-1} (-1)^k C(r-1,k) (1-x)^{g+m k}/(g+m k)

Baseline-composed survival: Sbar(G) = S_{r,g,m} evaluated at u = F(x),
i.e. 1-u = survival S_F(x).  Testable orders: st only (icv/icx/star/IH
records are unsupported / out of scope).
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def M(r, g, m):
    return sp.prod([g + (i) * m for i in range(r)])


def S_unif(r, g, m, uvar):
    """Survival of uniform m-GOS as a function of v = 1-u (= survival of
    baseline at x). m > 0 rational."""
    s = R(0)
    for k in range(r):
        s += (-1) ** k * sp.binomial(r - 1, k) * \
            uvar ** (g + m * k) / (g + m * k)
    return M(r, g, m) / (sp.factorial(r - 1) * m ** (r - 1)) * s


def S_at(r, g, m, base):
    """Survival on x >= 0 for baseline survival `base` = 1-F(x)."""
    return S_unif(r, g, m, base)


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


v = 1 - x          # uniform-case variable on (0,1)


def corollary_1():
    """gamma1 > beta1 and Lemma-2(i): m,nu>0 and Mratio >= 1; or
    gamma1=beta1 with m >= nu.  Claim X_{r,g} <=st X_{r,b} i.e. uniform
    GOS survivals ordered on (0,1) and composed with a common baseline."""
    cases = [  # (r, g, m, b, nu) with g>b, m,nu>0, Mratio>=1
        (3, R(2), R(1), R(3, 2), R(1)),
        (3, R(2), R(1, 2), R(1), R(2)),
        (3, R(3, 2), R(1), R(1), R(1, 2)),
        (4, R(2), R(1), R(3, 2), R(1, 2)),
        # g=b, m>=nu branch
        (3, R(2), R(3), R(2), R(1)),
        (4, R(3, 2), R(2), R(3, 2), R(1)),
    ]
    res = []
    for r, g, m, b, nu in cases:
        assert g > b or (g == b and m >= nu)
        if g > b:
            assert m > 0 and nu > 0 and M(r, g, m) >= M(r, b, nu)
        SU = Closed(S_unif(r, g, m, v), 0, 1)
        SV = Closed(S_unif(r, b, nu, v), 0, 1)
        h, w_, u_ = cf.check("st", SU, SV)
        res.append((w_ is None, w_, u_))
        # composed with a common baseline F = Exp(1): u = 1-e^{-x}
        SU2 = Closed(S_at(r, g, m, sp.exp(-x)))
        SV2 = Closed(S_at(r, b, nu, sp.exp(-x)))
        h, w_, u_ = cf.check("st", SU2, SV2)
        res.append((w_ is None, w_, u_))
    return all(r_[0] for r_ in res), \
        next((r_[1] for r_ in res if r_[1] is not None), None), \
        sum(r_[2] for r_ in res), len(res)


def corollary_2():
    """Same difference m both sides; g1 >= b1 and r <= q:
    X_{r,g} <=st X_{q,b} on common baseline (uniform case)."""
    cases = [  # (r, g1, q, b1, m)
        (2, R(2), 3, R(3, 2), R(1)),
        (2, R(3), 4, R(1), R(1, 2)),
        (3, R(3), 3, R(2), R(1)),
        (2, R(5, 2), 3, R(5, 2), R(2)),
    ]
    res = []
    for r, g, q, b, m in cases:
        assert g >= b and r <= q
        SU = Closed(S_unif(r, g, m, v), 0, 1)
        SV = Closed(S_unif(q, b, m, v), 0, 1)
        h, w_, u_ = cf.check("st", SU, SV)
        res.append((w_ is None, w_, u_))
        SU2 = Closed(S_at(r, g, m, 1 / (1 + x)))
        SV2 = Closed(S_at(q, b, m, 1 / (1 + x)))
        h, w_, u_ = cf.check("st", SU2, SV2)
        res.append((w_ is None, w_, u_))
    return all(r_[0] for r_ in res), \
        next((r_[1] for r_ in res if r_[1] is not None), None), \
        sum(r_[2] for r_ in res), len(res)


def remark_2_item1():
    """Swapped roles: g1 <= b1 (r <= q, same m) => X_{q,b} <=st X_{r,g}."""
    cases = [
        (2, R(1), 3, R(2), R(1)),      # g1=1 <= b1=2
        (2, R(3, 2), 4, R(5, 2), R(1, 2)),
        (3, R(1), 3, R(2), R(1)),
    ]
    res = []
    for r, g, q, b, m in cases:
        assert g <= b and r <= q
        SU = Closed(S_unif(q, b, m, v), 0, 1)   # X_{q,b} is the 'smaller'
        SV = Closed(S_unif(r, g, m, v), 0, 1)
        h, w_, u_ = cf.check("st", SU, SV)
        res.append((w_ is None, w_, u_))
        SU2 = Closed(S_at(q, b, m, sp.exp(-x)))
        SV2 = Closed(S_at(r, g, m, sp.exp(-x)))
        h, w_, u_ = cf.check("st", SU2, SV2)
        res.append((w_ is None, w_, u_))
    return all(r_[0] for r_ in res), \
        next((r_[1] for r_ in res if r_[1] is not None), None), \
        sum(r_[2] for r_ in res), len(res)


def remark_2_item2():
    """p<r elements of gamma (take a contiguous arithmetic prefix),
    s>q extension of beta; baselines F<=stG (Exp(1) <=st Lomax):
    X_{p,gp} <=st X_{s,bs}."""
    res = []
    cases = [
        # (gamma_p, beta_s): each arithmetic; Cor-2 premise g1_p >= b1_q
        # with beta_s an extension of beta_q (same common difference).
        ([R(2), R(3)], [R(1), R(2), R(3)]),
        ([R(5, 2), R(3)], [R(1), R(3, 2), R(2), R(5, 2)]),
        ([R(2), R(3), R(4)], [R(3, 2), R(2), R(5, 2), R(3)]),
    ]
    for gseq, bseq in cases:
        assert gseq[0] >= bseq[0]
        baseU = sp.exp(-x)          # F = Exp(1): survival e^{-x}
        baseV = 1 / (1 + x)         # G = Lomax: heavier => G >=st F
        SU = Closed(S_unif_list(gseq, baseU))
        SV = Closed(S_unif_list(bseq, baseV))
        h, w_, u_ = cf.check("st", SU, SV)
        res.append((w_ is None, w_, u_))
    return all(r_[0] for r_ in res), \
        next((r_[1] for r_ in res if r_[1] is not None), None), \
        sum(r_[2] for r_ in res), len(res)


def S_unif_list(gamma, uvar):
    """m-GOS survival for an arithmetic parameter list: infers the common
    difference from consecutive entries."""
    r = len(gamma)
    g1 = gamma[0]
    m = gamma[1] - gamma[0] if r > 1 else R(1)
    for i in range(1, r):
        assert gamma[i] - gamma[i - 1] == m
    return S_unif(r, g1, m, uvar)


def main():
    canon = json.load(open(os.path.join(
        HERE, "..", "canonical", "arxiv_2606.07022.json")))
    results = []
    for recd in canon:
        order = recd["conclusion"]["order"]
        label = recd["claim"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        if label == "Corollary 1":
            ok, w, u, n_ = corollary_1()
        elif label == "Corollary 2":
            ok, w, u, n_ = corollary_2()
        elif label == "Remark 2 (item 1)":
            ok, w, u, n_ = remark_2_item1()
        elif label == "Remark 2 (item 2)":
            ok, w, u, n_ = remark_2_item2()
        else:
            results.append(rec(recd, "out of harness scope"))
            continue
        results.append(rec(recd, "holds" if ok else "refuted",
                           instances=n_, witness=w, undecided=u))
    out = os.path.join(HERE, "eval_arxiv_2606.07022.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"],
              "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
