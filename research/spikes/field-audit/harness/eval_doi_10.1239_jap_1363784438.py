"""Evaluate canonical claims of doi_10.1239/jap.1363784438
(dynamic signatures / sequential order statistics under PHR).

PHR model: F_i = 1 - Fbar^{alpha_i}; sequential OS coincide with generalized
order statistics with gamma_j = alpha_j (n-j+1).  With exponential baseline
Fbar = e^{-x} and distinct gamma_j, the r-th generalized-OS survival is

    S_r(t) = sum_{j=1..r} ( prod_{l<=r, l!=j} gamma_l/(gamma_l-gamma_j) )
             * e^{-gamma_j t}     -- exact polynomial in z = e^{-t}.

Coefficient vectors: p_i(t) = s_i S_i(t) / sum_k s_k S_k(t)  (residual),
p~_i(t) = s_i F_i(t) / sum_k s_k F_k(t)                        (inactivity).

- Lemma 2.1 (residual): p(t1) <=lr p(t2) for t1 <= t2, i.e.
  p_i(t2)/p_i(t1) nondecreasing in i  <=>  S_i(t1) S_j(t2) - S_i(t2) S_j(t1)
  >= 0 for all i<j.  Take t2 = 2 t1  (s2 = s1^2): polynomial in z, exact.
- Lemma 2.1 (inactivity): same with F_i = 1 - S_i.
- Remark 2.1 premise check: X*_{r:n} <=hr X*_{r+1:n} under PHR (PHR gives the
  even stronger lr ordering, so a PHR instance is admissible).
- Theorem 2.2(a): residual lifetimes (T1-t|T1>t) vs (T2-t|T2>t) when the
  coefficient vectors are <=st / <=hr / <=lr at time t.  We pick signature
  vectors s1, s2, verify the discrete order at the chosen t exactly, and
  test the residual-lifetime order.  Residual survival (u >= 0):
      R(u) ∝ sum_i s_i S_i(t+u)  =  sum_i s_i sum_j c_ij q^{gamma_j} z^{gamma_j}
  with q = e^{-t} rational and z = e^{-u}: polynomial in z.
- Theorem 2.2(b): inactivity lifetimes (t-T|T<=t), reversed direction,
  survival in u:  sum_i s_i F_i(t-u) = sum_i s_i (1 - sum_j c_ij q^{gamma_j}
  z^{-gamma_j})  on z in [q,1]  (Laurent polynomial; ratdist handles it).
"""
import json, os
import sympy as sp
import ratdist as rd
from ratdist import z, Dist

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.1239_jap_1363784438.json")
OUT = os.path.join(HERE, "eval_doi_10.1239_jap_1363784438.result.json")
R = sp.Rational


def gen_os_sf(alphas, r):
    """Survival of r-th generalized OS under PHR, Fbar = e^{-x}, z=e^{-x}.

    gamma_j = alpha_j (n-j+1); requires distinct gamma_1..gamma_r.
    """
    n = len(alphas)
    gam = [R(a) * (n - j) for j, a in enumerate(alphas)]
    sub = gam[:r]
    assert len(set(sub)) == len(sub), "need distinct gammas"
    expr = sp.Integer(0)
    for j in range(r):
        c = R(1)
        for l in range(r):
            if l != j:
                c *= sub[l] / (sub[l] - sub[j])
        expr += c * z ** int(sub[j])
    return sp.expand(expr)


def coeff_vec(sig, alphas, sval):
    """p_i(t) evaluated at z = sval = e^{-t}: returns list of exact rationals."""
    n = len(alphas)
    Ps = [gen_os_sf(alphas, i + 1).subs(z, sval) for i in range(n)]
    tot = sum(si * pi for si, pi in zip(sig, Ps))
    return [si * pi / tot for si, pi in zip(sig, Ps)], Ps


def disc_order(p, q, kind):
    """is discrete pmf p <=_{st,hr,lr} q on {1..n}?"""
    n = len(p)
    if kind == "st":
        return all(sum(p[i:]) <= sum(q[i:]) for i in range(1, n + 1))
    if kind == "hr":
        # discrete hr: tail-ratio monotone:  P_p([i,..])/P_q([i,..]) dec. in i
        tp = [sum(p[i:]) for i in range(n)]
        tq = [sum(q[i:]) for i in range(n)]
        return all(tp[i] * tq[i + 1] >= tp[i + 1] * tq[i] for i in range(n - 1))
    if kind == "rh":
        # discrete rh: cdf ratio F_p(i)/F_q(i) nonincreasing in i
        cp = [sum(p[:i + 1]) for i in range(n)]
        cq = [sum(q[:i + 1]) for i in range(n)]
        return all(cp[i] * cq[i + 1] >= cp[i + 1] * cq[i] for i in range(n - 1))
    if kind == "lr":
        return all(p[i] * q[i + 1] >= p[i + 1] * q[i] for i in range(n - 1))
    raise ValueError(kind)


def resid_sf(sig, alphas, tval):
    """R(u) proportional to sum_i s_i S_i(t+u) as polynomial in z=e^{-u};
    t enters via q = e^{-t} rational.  Normalized to 1 at u=0 (z=1)."""
    q = tval                            # q = e^{-t} supplied as rational
    expr = sp.Integer(0)
    n = len(alphas)
    gam = [R(a) * (n - j) for j, a in enumerate(alphas)]
    for i in range(n):
        r = i + 1
        gam_r = gam[:r]
        for j in range(r):
            c = R(1)
            for l in range(r):
                if l != j:
                    c *= gam_r[l] / (gam_r[l] - gam_r[j])
            expr += sig[i] * c * q ** int(gam_r[j]) * z ** int(gam_r[j])
    expr = sp.expand(expr)
    expr = expr / expr.subs(z, sp.Integer(1))   # normalize: R(0) = 1
    return Dist(sp.expand(expr), sp.Integer(0), sp.Integer(1), False)


def inact_sf(sig, alphas, tval):
    """survival of (t - T | T <= t) at lag u in [0,t]:
    P(t-T > u | T<=t) ∝ sum_i s_i F_i(t-u), z = e^{-u} on [q,1]."""
    q = tval
    expr = sp.Integer(0)
    n = len(alphas)
    gam = [R(a) * (n - j) for j, a in enumerate(alphas)]
    for i in range(n):
        r = i + 1
        gam_r = gam[:r]
        Fi = sp.Integer(1)
        for j in range(r):
            c = R(1)
            for l in range(r):
                if l != j:
                    c *= gam_r[l] / (gam_r[l] - gam_r[j])
            Fi -= c * q ** int(gam_r[j]) * z ** (-int(gam_r[j]))
        expr += sig[i] * Fi
    expr = sp.expand(expr)
    expr = expr / expr.subs(z, sp.Integer(1))   # normalize: value 1 at u=0
    return Dist(sp.expand(expr), q, sp.Integer(1), False)


def go():
    recs = json.load(open(CANON))
    out = []
    for r in recs:
        c = r.get("conclusion") or {}
        order = c.get("order")
        claim = r["claim"]
        if order not in ("st", "hr", "rh", "lr"):
            out.append(dict(claim=claim, order=order, status="unsupported order",
                            instances=0, witness=None, undecided_points=0))
            continue
        inst = 0; wit = None; und = 0; allhold = True
        if "Lemma 2.1" in claim and "inactivity" in claim:
            # F_i(t1) F_j(t2) - F_i(t2) F_j(t1) >= 0 for i<j, t2 = 2 t1:
            # polynomial in z = e^{-t1}, decided exactly on (0,1).
            for sig, alphas in [((R(1,2),R(1,4),R(1,4)), (R(1),R(1),R(1))),
                                ((R(1,3),R(1,3),R(1,3)), (R(1),R(2),R(5))),
                                ((R(1,2),R(1,4),R(1,4)), (R(1),R(3),R(2))),
                                ((R(1,5),R(2,5),R(2,5)), (R(2),R(1),R(1)))]:
                n = len(alphas)
                for i in range(n):
                    for j in range(i + 1, n):
                        Fi = 1 - gen_os_sf(alphas, i + 1)
                        Fj = 1 - gen_os_sf(alphas, j + 1)
                        E = Fi * Fj.subs(z, z**2) - Fi.subs(z, z**2) * Fj
                        ok, w = rd._nonnegative(sp.expand(E), sp.Integer(0), sp.Integer(1))
                        inst += 1
                        if not ok:
                            allhold = False; wit = str(w)
        elif "Lemma 2.1" in claim:
            # residual coefficients: for i<j need S_i(t1) S_j(t2) >=
            # S_i(t2) S_j(t1); choose t2 = 2 t1 -> s2 = s1^2, poly in z.
            for sig, alphas in [((R(1,2),R(1,4),R(1,4)), (R(1),R(1),R(1))),
                                ((R(1,3),R(1,3),R(1,3)), (R(1),R(2),R(5))),
                                ((R(1,2),R(1,4),R(1,4)), (R(1),R(3),R(2))),
                                ((R(1,5),R(2,5),R(2,5)), (R(2),R(1),R(1)))]:
                n = len(alphas)
                for i in range(n):
                    for j in range(i + 1, n):
                        Si = gen_os_sf(alphas, i + 1)
                        Sj = gen_os_sf(alphas, j + 1)
                        E = Si * Sj.subs(z, z**2) - Si.subs(z, z**2) * Sj
                        ok, w = rd._nonnegative(E, sp.Integer(0), sp.Integer(1))
                        inst += 1
                        if not ok:
                            allhold = False; wit = str(w)
        elif "Remark 2.1" in claim:
            # X*_{r:n} <=hr X*_{r+1:n} under PHR (PHR premise gives lr, so the
            # weaker hr must hold on every admissible PHR instance).
            for alphas in [(R(1),R(1),R(1)), (R(1),R(2),R(5)),
                           (R(2),R(1),R(1)), (R(1),R(1),R(1),R(1))]:
                n = len(alphas)
                for rr in range(1, n):
                    A = Dist(gen_os_sf(alphas, rr), sp.Integer(0), sp.Integer(1), False)
                    B = Dist(gen_os_sf(alphas, rr + 1), sp.Integer(0), sp.Integer(1), False)
                    ok, w = rd.hr(A, B)
                    inst += 1
                    if not ok:
                        allhold = False; wit = str(w)
        elif "Theorem 2.2(a)" in claim:
            # residual lifetimes: choose s1,s2 with p1 <=order p2 at t,
            # verify exact discrete order, then compare residuals.
            sigsets = [
                ((R(1,2),R(1,4),R(1,4)), (R(1,3),R(1,3),R(1,3))),
                ((R(1,2),R(1,4),R(1,4)), (R(1,4),R(1,4),R(1,2))),
                ((R(3,5),R(1,5),R(1,5)), (R(1,5),R(2,5),R(2,5))),
            ]
            for (s1, s2) in sigsets:
                for alphas in [(R(1),R(1),R(1)), (R(1),R(2),R(5))]:
                    for q in [R(1,2), R(1,4)]:
                        p1, _ = coeff_vec(s1, alphas, q)
                        p2, _ = coeff_vec(s2, alphas, q)
                        if not disc_order(p1, p2, order):
                            continue  # hypothesis not met at this t; skip
                        A = resid_sf(s1, alphas, q)
                        B = resid_sf(s2, alphas, q)
                        ok, w = rd.ORDERS[order](A, B)
                        inst += 1
                        if not ok:
                            allhold = False; wit = str(w)
        elif "Theorem 2.2(b)" in claim:
            # inactivity: claim (t-T1|T1<=t) >=order (t-T2|T2<=t) given
            # p~1 <=order p~2 -- equivalently T2-side <=order T1-side.
            sigsets = [
                ((R(1,2),R(1,4),R(1,4)), (R(1,3),R(1,3),R(1,3))),
                ((R(1,4),R(1,4),R(1,2)), (R(1,2),R(1,4),R(1,4))),
                ((R(1,5),R(2,5),R(2,5)), (R(3,5),R(1,5),R(1,5))),
            ]
            for (s1, s2) in sigsets:
                for alphas in [(R(1),R(1),R(1)), (R(1),R(2),R(5))]:
                    for q in [R(1,2), R(1,4)]:
                        # discrete order on F_i-based coefficients
                        n = len(alphas)
                        Fs1 = [1 - gen_os_sf(alphas, i + 1).subs(z, q) for i in range(n)]
                        tot1 = sum(si * fi for si, fi in zip(s1, Fs1))
                        p1 = [si * fi / tot1 for si, fi in zip(s1, Fs1)]
                        tot2 = sum(si * fi for si, fi in zip(s2, Fs1))
                        p2 = [si * fi / tot2 for si, fi in zip(s2, Fs1)]
                        if not disc_order(p1, p2, order):
                            continue
                        A = inact_sf(s1, alphas, q)
                        B = inact_sf(s2, alphas, q)
                        ok, w = rd.ORDERS[order](B, A)   # reversed direction
                        inst += 1
                        if not ok:
                            allhold = False; wit = str(w)
        else:
            out.append(dict(claim=claim, order=order, status="out of harness scope",
                            instances=0, witness=None, undecided_points=0))
            continue
        out.append(dict(claim=claim, order=order,
                        status="holds" if allhold else "refuted",
                        instances=inst, witness=wit, undecided_points=und))
    json.dump(out, open(OUT, "w"), indent=1)
    for o in out:
        print(o["claim"], "|", o["order"], "|", o["status"], "| inst", o["instances"],
              "| wit", o["witness"])


if __name__ == "__main__":
    go()
