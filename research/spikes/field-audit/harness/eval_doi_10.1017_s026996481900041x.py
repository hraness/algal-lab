"""Evaluate canonical claims of doi_10.1017/S026996481900041X
(spacings/order statistics of independent exponentials).

All survivals are polynomials (sums of exponentials) in z = e^{-t};
exact decisions via ratdist.

Models
------
- X_{k:n}: k-th smallest of independent Exp(lambda_i); survival is a
  polynomial in z (ratdist.order_statistic_exponentials).
- Spacing D = X_{k:n} - X_{m:n}: conditioned on the ordered sequence
  sigma = (i_1,...,i_k) of the first k failures, the gaps between failures
  j-1 and j are independent Exp(Lambda_j) with Lambda_j = Lambda - sum_{l<j}
  lambda_{i_l};  P(sigma) = prod_j lambda_{i_j}/Lambda_j.  Hence
      P(D > t) = sum_sigma w(sigma) * H(t; Lambda_{m+1},...,Lambda_k)
  with H the hypoexponential survival (distinct Lambda_j required).
- Homogeneous sample: lambda_i = gamma for all i; D_Y is a single
  hypoexponential with rates (n-j+1) gamma, j = m+1..k.
- Lemma 3 weighted gamma sums at alpha = 1:  sum_i theta_i Z_i,
  Z_i ~ Exp(1) iid -> hypoexponential with rates 1/theta_i.

Theorem 1 (hr): Y_{k:n} <=hr X_{k:n} iff gamma >= (C(n,k)^{-1} s_k(lambda))^{1/k}.
Proposition 1 (st, hr): spacing comparison iff
    gamma^{k-m} >= C(n-m,k-m)^{-1} sum_r w(r) s_{k-m}(lambda \setminus r).
"""
import itertools
import json, os
import sympy as sp
import ratdist as rd
from ratdist import z, Dist

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.1017_s026996481900041x.json")
OUT = os.path.join(HERE, "eval_doi_10.1017_s026996481900041x.result.json")
R = sp.Rational


def hypox(rates):
    """P(E_1+...+E_r > t), E_j ~ Exp(mu_j), distinct mu_j, as poly in z=e^{-t}."""
    rates = [R(v) for v in rates]
    assert len(set(rates)) == len(rates), "need distinct gap rates"
    assert all(r.is_integer and r > 0 for r in rates), "rates must be positive integers in z=e^{-t}"
    expr = sp.Integer(0)
    for j, mj in enumerate(rates):
        a = R(1)
        for l, ml in enumerate(rates):
            if l != j:
                a *= ml / (ml - mj)
        expr += a * z ** int(mj)
    return Dist(sp.expand(expr), sp.Integer(0), sp.Integer(1), False)


def os_sf(rates, k):
    """P(X_{k:n} > t) for independent Exp(lambda_i), integer rates."""
    return rd.order_statistic_exponentials(rates, k, 1)


def spacing_sf(rates, m, k):
    """P(X_{k:n} - X_{m:n} > t) for heterogeneous Exp(lambda_i)."""
    n = len(rates)
    rates = [R(v) for v in rates]
    lam = sum(rates)
    expr = sp.Integer(0)
    for sigma in itertools.permutations(range(n), k):
        w = R(1)
        pref = R(0)          # sum of lambda_{i_l}, l < j
        mus = []
        for j in range(1, k + 1):
            lam_j = lam - pref
            w *= rates[sigma[j - 1]] / lam_j
            if j > m:
                mus.append(lam_j)
            pref += rates[sigma[j - 1]]
        expr += w * hypox(mus).survival
    return Dist(sp.expand(expr), sp.Integer(0), sp.Integer(1), False)


def spacing_sf_hom(gamma, n, m, k):
    """Spacing survival for iid Exp(gamma)."""
    mus = [(n - j + 1) * R(gamma) for j in range(m + 1, k + 1)]
    return hypox(mus)


def esf(vals, d):
    """elementary symmetric function of degree d."""
    tot = R(0)
    for c in itertools.combinations(vals, d):
        tot += sp.prod(c)
    return sp.expand(tot)


def cond2_rhs(lam, n, m, k):
    """RHS of condition (2): C(n-m,k-m)^{-1} sum_r w(r) s_{k-m}(lam\r)."""
    rates = [R(v) for v in lam]
    Lam = sum(rates)
    tot = R(0)
    for r in itertools.permutations(range(n), m):
        w = R(1); pref = R(0)
        for j in range(1, m + 1):
            lam_j = Lam - pref
            w *= rates[r[j - 1]] / lam_j
            pref += rates[r[j - 1]]
        rest = [rates[i] for i in range(n) if i not in r]
        tot += w * esf(rest, k - m)
    return sp.expand(tot / sp.binomial(n - m, k - m))


def check(order, A, B):
    return rd.ORDERS[order](A, B)


def run(order, pairs):
    inst = 0; wit = None; allhold = True
    for A, B in pairs:
        ok, w = check(order, A, B)
        inst += 1
        if not ok:
            allhold = False; wit = str(w)
    return inst, wit, allhold


def go():
    recs = json.load(open(CANON))
    out = []
    for r in recs:
        c = r.get("conclusion") or {}
        order = c.get("order")
        claim = r["claim"]
        status = None; inst = 0; wit = None
        if order not in ("st", "hr", "rh", "lr"):
            status = "unsupported order"
        elif "Lemma 3" in claim:
            # F_eta <=st F_theta, alpha=1: sum theta_i Z_i, Z_i ~ Exp(1).
            # log eta weakly submajorized by log theta; coordinatewise
            # log eta_i <= log theta_i is admissible.
            pairs = []
            # weights theta_i = 1/rho_i with integer rates rho_i (integer rates
            # required by z = e^{-t}); coordinatewise log eta < log theta
            for rates_t, rates_e in [((2,3,5), (4,6,8)),
                                     ((1,2), (3,4)),
                                     ((2,3,7), (3,4,9)),
                                     ((1,3), (2,5))]:
                DY = hypox(list(rates_e)); DX = hypox(list(rates_t))
                pairs.append((DY, DX))
            inst, wit, ok = run(order, pairs)
            status = "holds" if ok else "refuted"
        elif "Proposition 1" in claim:
            # spacing st / hr iff condition (2): test at gamma >= RHS and
            # gamma < RHS instances.
            pairs = []
            for lam, n, m, k in [((R(1), R(2), R(4)), 3, 1, 2),
                                 ((R(1), R(2), R(4)), 3, 1, 3),
                                 ((R(1), R(3), R(7)), 3, 1, 2),
                                 ((R(1), R(2), R(3), R(5)), 4, 1, 2)]:
                rhs = cond2_rhs(lam, n, m, k)          # bound on gamma^{k-m}
                base = sp.expand(rhs)**(R(1) / (k - m))  # real k-m-th root
                gam_ok = sp.nsimplify(base)            # may be irrational
                # choose rational gammas straddling the threshold
                lo = int(sp.floor(base)); gammas = [R(lo) if R(lo) > 0 else R(1, 2)]
                gammas += [R(lo + 1), R(lo + 2)]
                for g in gammas:
                    DX = spacing_sf(lam, m, k)
                    DY = spacing_sf_hom(g, n, m, k)
                    pairs.append((DY, DX, bool(R(g)**(k - m) >= rhs)))
            allhold = True
            for DY, DX, adm in pairs:
                ok, w = check(order, DY, DX)
                inst += 1
                if adm and not ok:
                    allhold = False
                    wit = wit or str(w)
            status = "holds" if allhold else "refuted"
        elif "Theorem 1" in claim:
            # Y_{k:n} <=hr X_{k:n} iff gamma >= (C(n,k)^{-1} s_k(lam))^{1/k}
            insts = [((R(1), R(2), R(4)), 3, 1), ((R(1), R(2), R(4)), 3, 2),
                     ((R(1), R(2), R(4)), 3, 3), ((R(1), R(3), R(7)), 3, 2),
                     ((R(1), R(2), R(3), R(5)), 4, 2), ((R(1), R(2), R(3), R(5)), 4, 3)]
            allhold = True
            for lam, n, k in insts:
                th = (esf(lam, k) / sp.binomial(n, k)) ** (R(1) / k)
                base = sp.floor(th)
                for g in {R(base) if base >= 1 else R(1, 2), R(base + 1), R(base + 2)}:
                    if not R(g)**k * sp.binomial(n, k) >= esf(lam, k):
                        continue  # keep only instances satisfying hypothesis
                    YD = os_sf([R(g)] * n, k)
                    XD = os_sf(list(lam), k)
                    ok, w = check("hr", YD, XD)
                    inst += 1
                    if not ok:
                        allhold = False; wit = str(w)
            status = "holds" if allhold else "refuted"
        else:
            status = "out of harness scope"
        out.append(dict(claim=claim, order=order, status=status,
                        instances=inst, witness=wit, undecided_points=0))
    json.dump(out, open(OUT, "w"), indent=1)
    for o in out:
        print(o["claim"], "|", o["order"], "|", o["status"], "| inst", o["instances"],
              "| wit", o["witness"])


if __name__ == "__main__":
    go()
