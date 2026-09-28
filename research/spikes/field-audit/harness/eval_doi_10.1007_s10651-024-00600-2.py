"""Evaluation of canonical claims for doi:10.1007/s10651-024-00600-2
(SMSN scale mixtures / tail-weight orderings).

Encodable pieces:
- Proposition 1(i): S1*Z <=st S2*Z for independent positive factors.
  Pareto products are closed form:  S ~ Par(a): S_S(t)=t^{-a} on [1,oo),
  Z ~ Par(b): S_{SZ}(t) = t^{-b} + b/(a-b) (t^{-b} - t^{-a}).
- Proposition 1(ii): s1 Z <=lr s2 Z, s1<s2, Z=Exp(1) (decreasing elasticity).
- Proposition 1(iii): lr-ordered Pareto factors times Pareto Z:
  f_{SZ}(t) = ab/(a-b) (t^{-b-1} - t^{-a-1}), closed form; Pareto density
  elasticity xg'/g = -(b+1) constant => nonincreasing, hypothesis holds.
- Degeneracy claims for skew-t: mixing S = V^{-1/2}, V ~ chi^2_nu/nu.
  For even nu closed form: nu=2 -> S_S(s)=1-e^{-s^{-2}};
  nu=4 -> S_S(s)=1-e^{-2 s^{-2}}(1+2 s^{-2}).  Printed claim: S1 <=st S2
  forces nu1=nu2 -> confirmed when the st check fails in BOTH directions.

Out of scope: SN density (erf/Phi not interval-evaluable), chi^2_p with
odd p, discrete-mixture quadratic forms, c-tw/star order claims.
"""
import json
import os

import sympy as sp

import closedform as cf
from closedform import x, Closed

R = sp.Rational
HERE = os.path.dirname(os.path.abspath(__file__))


def S_par(a, lo=1):
    """Pareto-I: S(t) = t^{-a} on [1, oo)."""
    return x ** (-R(a))


def S_parprod(a, b):
    """Survival of product of independent Par(a), Par(b) on [1,oo), a!=b."""
    a, b = R(a), R(b)
    return x ** (-b) + b / (a - b) * (x ** (-b) - x ** (-a))


def S_sco(nu):
    """S = V^{-1/2}, V ~ chi^2_nu/nu, even nu: survival on (0, oo)."""
    if nu == 2:
        return 1 - sp.exp(-x ** (-2))
    if nu == 4:
        return 1 - sp.exp(-2 * x ** (-2)) * (1 + 2 * x ** (-2))
    raise ValueError(nu)


def rec(record, status, instances=0, witness=None, undecided=0):
    return {"claim": record["claim"], "order": record["conclusion"]["order"],
            "status": status, "instances": instances,
            "witness": None if witness is None else str(witness),
            "undecided_points": undecided}


def prop_1_i():
    """S1 <=st S2, Z indep positive => S1 Z <=st S2 Z.
    Par(a) <=st Par(a') iff a >= a' (heavier tail = stochastically larger
    requires smaller a: t^{-a} >= t^{-a'} iff a <= a'). So S1=Par(a1),
    S2=Par(a2) with a1 <= a2 gives S1 >=st S2; to get S1 <=st S2 need
    a1 >= a2."""
    n, wit, und = 0, None, 0
    cases = [  # (a1, a2, b): S1=Par(a1) <=st S2=Par(a2) requires a1 >= a2
        (R(3), R(2), R(1)),
        (R(3), R(2), R(4)),
        (R(5, 2), R(3, 2), R(1)),
        (R(4), R(3), R(6)),
        (R(5), R(4), R(2)),
    ]
    for a1, a2, b in cases:
        assert a1 >= a2 and a1 != b and a2 != b
        P1 = Closed(S_parprod(a1, b), 1)
        P2 = Closed(S_parprod(a2, b), 1)
        h, w, u = cf.check("st", P1, P2)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def prop_1_ii():
    """s1 Z <=lr s2 Z for s1 < s2, Z = Exp(1): s Z ~ Exp(rate 1/s)."""
    n, wit, und = 0, None, 0
    for s1, s2 in [(R(1), R(2)), (R(1), R(3)), (R(1, 2), R(1)),
                   (R(2), R(5)), (R(3, 2), R(4))]:
        assert s1 < s2
        X = Closed(sp.exp(-x / s1))
        Y = Closed(sp.exp(-x / s2))
        h, w, u = cf.check("lr", X, Y)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def prop_1_iii():
    """S1 <=lr S2 => S1 Z <=lr S2 Z, Pareto factors, closed-form product
    density f(t) = ab/(a-b)(t^{-b-1}-t^{-a-1}); survival = S_parprod."""
    n, wit, und = 0, None, 0
    cases = [  # (a1, a2, b): Par(a1) <=lr Par(a2) requires a1 >= a2
        (R(3), R(2), R(1)),
        (R(5, 2), R(3, 2), R(1)),
        (R(4), R(3), R(6)),
        (R(5), R(4), R(2)),
    ]
    for a1, a2, b in cases:
        assert a1 >= a2 and len({a1, a2, b}) == 3
        P1 = Closed(S_parprod(a1, b), 1)
        P2 = Closed(S_parprod(a2, b), 1)
        h, w, u = cf.check("lr", P1, P2)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    return n, wit, und


def degeneracy():
    """Printed: S1 <=st S2 forces nu1 = nu2 for skew-t mixing variables.
    Confirm: for nu=2 vs nu=4 the st check fails in BOTH directions."""
    S2, S4 = Closed(S_sco(2)), Closed(S_sco(4))
    h1, w1, u1 = cf.check("st", S2, S4)
    h2, w2, u2 = cf.check("st", S4, S2)
    ok = (w1 is not None) and (w2 is not None)
    return ok, w1 if w1 is not None else w2, u1 + u2, 2


def main():
    canon = json.load(open(os.path.join(HERE, "..", "canonical", "doi_10.1007_s10651-024-00600-2.json")))
    results = []
    for recd in canon:
        order = recd["conclusion"]["order"]
        label = recd["claim"]
        if order not in ("st", "hr", "rh", "lr"):
            results.append(rec(recd, "unsupported order"))
            continue
        if label == "Proposition 1(i)":
            n_, w, u = prop_1_i()
        elif label == "Proposition 1(ii)":
            n_, w, u = prop_1_ii()
        elif label == "Proposition 1(iii)":
            n_, w, u = prop_1_iii()
        elif label.startswith("Degeneracy") or label.startswith("Remark after Proposition 4"):
            ok, w, u, n_ = degeneracy()
            results.append(rec(recd, "holds" if ok else "refuted",
                               instances=n_, witness=w, undecided=u))
            continue
        else:
            results.append(rec(recd, "out of harness scope"))
            continue
        results.append(rec(recd, "holds" if w is None else "refuted",
                           instances=n_, witness=w, undecided=u))
    out = os.path.join(HERE, "eval_doi_10.1007_s10651-024-00600-2.result.json")
    json.dump(results, open(out, "w"), indent=1)
    for r in results:
        print(r["claim"], "|", r["order"], "|", r["status"],
              "| n =", r["instances"], "| w =", r["witness"], "| u =", r["undecided_points"])


if __name__ == "__main__":
    main()
