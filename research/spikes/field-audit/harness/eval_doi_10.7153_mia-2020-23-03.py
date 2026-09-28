"""Evaluate canonical claims of doi_10.7153/mia-2020-23-03 (claim amounts, copula).

Y_i = I_{p_i} X_{lambda_i}; severities coupled by copula C, shocks possibly
dependent.  Printed formula (11):
    G_{Yn:n}(x) = sum_{mu in {0,1}^n} p(mu) * C( F(x;l_1)^{mu_1}, ... ),
with p(mu)=prod p_i^{mu_i}(1-p_i)^{1-mu_i} under independent shocks, and
F^{0}=1.  Survival of the max is 1-G.

Copulas used:
    indep Pi (PQD, Schur-concave, dC/dv1 >= dC/dv2 for v1<=v2 all hold);
    gumbel2 (PQD, dominates Pi:  Pi ~< Gumbel in concordance), generator
    psi=(-ln u)^2, phi=e^{-sqrt(t)}.

Shock vector LWSAI: for independent Bernoulli, LWSAI iff p(1,0)<=p(0,1)
i.e. p1<=p2 (Lemma 3.1).  h(p)=log(2+p): strictly increasing concave,
h^{-1}(u)=e^u-2, and log h^{-1} concave (Thm 3.1/3.3 hypotheses).

'S' membership = (lambda_i, h(p_i)) similarly ordered (comonotone).
~<^m = majorization (equal totals, less spread); ~<^w = weak
supermajorization (ascending partial sums >=).
"""
import json, os, itertools
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.7153_mia-2020-23-03.json")
OUT = os.path.join(HERE, "eval_doi_10.7153_mia-2020-23-03.result.json")
R = sp.Rational


def c_eval(cop, vs):
    """Copula C(v_1..v_n); C(...,1,...)=marginal (drop the 1's)."""
    vv = [v for v in vs if v != 1]
    if not vv:
        return sp.Integer(1)
    if cop == "indep":
        g = sp.Integer(1)
        for v in vv:
            g *= v
        return g
    if cop == "gumbel2":
        t = sp.Integer(0)
        for v in vv:
            t += (sp.log(v)) ** 2
        return sp.exp(-sp.sqrt(t))
    if cop == "amh":
        th = R(1, 2)  # PQD
        t = sp.Integer(0)
        for v in vv:
            t += sp.log((1 - th + th * v) / v)
        return (1 - th) / (sp.exp(t) - th)
    raise ValueError(cop)


def port_max_cdf(ps, sfs, cop):
    """G(x)=sum_mu p(mu) C(F_i^{mu_i}); sfs = list of Fbar_i expressions."""
    n = len(ps)
    Fi = [1 - s for s in sfs]
    g = sp.Integer(0)
    for mu in itertools.product([0, 1], repeat=n):
        w = sp.Integer(1); vs = []
        for i, m in enumerate(mu):
            if m:
                w *= ps[i]; vs.append(Fi[i])
            else:
                w *= 1 - ps[i]; vs.append(sp.Integer(1))
        g += w * c_eval(cop, vs)
    return g


def port_max_sf(ps, sfs, cop):
    return 1 - port_max_cdf(ps, sfs, cop)


# marginal families
def scale_sf(lam):      # Fbar(lam x): baseline Pareto (f decreasing) / exp
    return (1 + lam * x) ** (-2)


def power_sf(lam):      # Fbar(x)^lam with Fbar=e^{-x}
    return sp.exp(-lam * x)


def tg_sf(lam):         # Fbar(1 - lam F), Fbar=e^{-x}
    Fb = sp.exp(-x)
    return Fb * (1 - lam * (1 - Fb))


def gen_sf(lam):        # Fbar(x;lam)=e^{-lam x}: decreasing & convex in lam
    return sp.exp(-lam * x)


def hval(p):
    return sp.log(2 + p)


def h_inv(u):
    return sp.exp(u) - 2


def instances(claim):
    """-> list of (S_starred, S_unstarred); claim always Y* <=st Y."""
    out = []
    if claim == "Theorem 3.1":
        # lambda common; h(p*) ~<^m h(p); (l,h(p)),(l,h(p*)) in S; C PQD.
        for (ls, ps, pss, cop) in [
                ([R(1,2), R(1)], [R(1,5), R(4,5)],
                 [h_inv((hval(R(1,5)) * 2 + hval(R(4,5))) / 3),
                  h_inv((hval(R(1,5)) + 2 * hval(R(4,5))) / 3)], "indep")]:
            out.append((port_max_sf(pss, [gen_sf(l) for l in ls], cop),
                        port_max_sf(ps, [gen_sf(l) for l in ls], cop)))
        return out
    if claim == "Example 3.2":
        # (lambda,h(p)) NOT in S: anti-comonotone; crossing expected.
        for (ls, ps, pss, cop) in [
                ([R(1,2), R(1)], [R(4,5), R(1,5)],
                 [R(3,5), R(2,5)], "indep")]:
            out.append((port_max_sf(pss, [gen_sf(l) for l in ls], cop),
                        port_max_sf(ps, [gen_sf(l) for l in ls], cop)))
        return out
    if claim in ("Theorem 3.2", "Example 3.2b-never"):
        # lambda* ~<^w lambda (supermaj), common p; C with dC1>=dC2
        for (ls, lss, ps, cop) in [
                ([R(1,2), R(1)], [R(7,10), R(1)], [R(1,5), R(4,5)], "indep"),
                ([R(1,5), R(1,2)], [R(2,5), R(1,2)], [R(1,5), R(4,5)], "indep")]:
            out.append((port_max_sf(ps, [gen_sf(l) for l in lss], cop),
                        port_max_sf(ps, [gen_sf(l) for l in ls], cop)))
        return out
    if claim in ("Theorem 3.3", "Theorem 3.4", "Example 3.1"):
        fam = scale_sf if claim in ("Theorem 3.4", "Example 3.1") else gen_sf
        for (ls, lss, ps, pss, cop) in [
                ([R(1,2), R(1)], [R(3,5), R(9,10)], [R(1,5), R(4,5)],
                 [h_inv((hval(R(1,5)) * 2 + hval(R(4,5))) / 3),
                  h_inv((hval(R(1,5)) + 2 * hval(R(4,5))) / 3)], "indep")]:
            out.append((port_max_sf(pss, [fam(l) for l in lss], cop),
                        port_max_sf(ps, [fam(l) for l in ls], cop)))
        return out
    if claim in ("Theorem 3.5", "Example 3.3"):
        fam = power_sf
        for (ls, lss, ps, pss) in [
                ([R(1,2), R(1)], [R(3,5), R(9,10)], [R(1,5), R(4,5)],
                 [h_inv((hval(R(1,5)) * 2 + hval(R(4,5))) / 3),
                  h_inv((hval(R(1,5)) + 2 * hval(R(4,5))) / 3)])]:
            out.append((port_max_sf(pss, [fam(l) for l in lss], "indep"),
                        port_max_sf(ps, [fam(l) for l in ls], "indep")))
        return out
    if claim in ("Theorem 3.6", "Example 3.4"):
        fam = tg_sf
        for (ls, lss, ps, pss) in [
                ([R(1,2), R(1)], [R(3,5), R(9,10)], [R(1,5), R(4,5)],
                 [h_inv((hval(R(1,5)) * 2 + hval(R(4,5))) / 3),
                  h_inv((hval(R(1,5)) + 2 * hval(R(4,5))) / 3)])]:
            out.append((port_max_sf(pss, [fam(l) for l in lss], "indep"),
                        port_max_sf(ps, [fam(l) for l in ls], "indep")))
        return out
    if claim in ("Theorem 3.7", "Theorem 3.8", "Theorem 3.9",
                 "Theorem 3.10", "Example 3.5", "Example 3.6"):
        # LWSAI shocks (p1<=p2), Fbar dec+convex in lam, lam* ~<^m lam
        # with l1>=l2, l*1>=l*2; C Schur-concave (indep).
        fam = gen_sf
        if claim in ("Theorem 3.8", "Example 3.6"):
            fam = scale_sf
        if claim in ("Theorem 3.9", "Example 3.5"):
            fam = power_sf
        if claim == "Theorem 3.10":
            fam = tg_sf
        both = []
        if claim == "Example 3.6":
            # lambda relation violated: l1 < l2 (violates l1 >= l2)
            both = [([R(1,5), R(4,5)], [R(2,5), R(3,5)])]
        else:
            both = [([R(4,5), R(1,5)], [R(3,5), R(2,5)]),
                    ([R(9,10), R(3,10)], [R(3,5), R(1,2)])]
        for (ls, lss) in both:
            ps = [R(1,5), R(2,5)]          # p1 <= p2 -> LWSAI
            out.append((port_max_sf(ps, [fam(l) for l in lss], "indep"),
                        port_max_sf(ps, [fam(l) for l in ls], "indep")))
        return out
    if claim == "Theorem 3.11":
        # common p, lambda_i <= lambda*_i; C indep
        for (ls, lss) in [([R(1,2), R(1), R(3,2)], [R(1), R(3,2), R(2)]),
                          ([R(1,5), R(2,5), R(3,5)], [R(2,5), R(3,5), R(1)])]:
            ps = [R(1,5), R(2,5), R(3,5)][:len(ls)]
            out.append((port_max_sf(ps, [gen_sf(l) for l in lss], "indep"),
                        port_max_sf(ps, [gen_sf(l) for l in ls], "indep")))
        return out
    if claim in ("Theorem 3.12",):
        # C ~< C* : same margins+shocks; starred uses gumbel2
        for (ls, ps) in [([R(1,2), R(1), R(3,2)], [R(1,5), R(2,5), R(3,5)])]:
            sfs = [gen_sf(l) for l in ls]
            out.append((port_max_sf(ps, sfs, "gumbel2"),
                        port_max_sf(ps, sfs, "indep")))
        return out
    if claim in ("Theorem 3.13", "Theorem 3.14", "Theorem 3.15",
                 "Theorem 3.16", "Example 3.7"):
        fam = gen_sf
        if claim in ("Theorem 3.14", "Example 3.7"):
            fam = scale_sf
        if claim == "Theorem 3.15":
            fam = power_sf
        if claim == "Theorem 3.16":
            fam = tg_sf
        if claim == "Theorem 3.16":
            # TG margins need lambda in [-1,1]
            cases = [([R(1,4), R(1,2), R(3,4)], [R(1,2), R(3,4), R(4,5)]),
                     ([R(1,5), R(3,5), R(1,2)], [R(2,5), R(3,4), R(3,5)])]
        else:
            cases = [([R(1,2), R(1), R(3,2)], [R(1), R(3,2), R(2)]),
                     ([R(1,5), R(2,5), R(3,5)], [R(2,5), R(3,5), R(1)])]
        for (ls, lss) in cases:
            ps = [R(1,5), R(2,5), R(3,5)][:len(ls)]
            out.append((port_max_sf(ps, [fam(l) for l in lss], "gumbel2"),
                        port_max_sf(ps, [fam(l) for l in ls], "indep")))
        return out
    return []


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
        pairs = instances(claim)
        if not pairs:
            out.append(dict(claim=claim, order=order,
                            status="out of harness scope", instances=0,
                            witness=None, undecided_points=0))
            continue
        # "no ordering / crossing" assertions (Examples 3.2, 3.6)
        crossing = "cross" in str(c.get("direction")).lower() or \
            "no st order" in str(c.get("direction")).lower()
        inst = 0; wit = None; und = 0; allhold = True
        for (SA, SB) in pairs:
            if crossing:
                ok1, w1, u1 = cf.check(order, Closed(SA), Closed(SB))
                ok2, w2, u2 = cf.check(order, Closed(SB), Closed(SA))
                und += u1 + u2; inst += 1
                if ok1 or ok2:
                    allhold = None
                else:
                    wit = wit or str(w1)
            else:
                ok, w, u = cf.check(order, Closed(SA), Closed(SB))
                inst += 1; und += u
                if not ok:
                    allhold = False; wit = str(w)
        status = "holds" if allhold else "refuted"
        if allhold is None:
            status = "out of harness scope"
        out.append(dict(claim=claim, order=order, status=status,
                        instances=inst, witness=wit, undecided_points=und))
    json.dump(out, open(OUT, "w"), indent=1)
    for o in out:
        print(o["claim"], "|", o["order"], "|", o["status"], "| inst", o["instances"],
              "| wit", o["witness"])


if __name__ == "__main__":
    go()
