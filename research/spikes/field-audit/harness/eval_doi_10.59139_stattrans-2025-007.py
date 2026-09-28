"""Evaluate canonical claims of doi_10.59139/stattrans-2025-007 (GMOP-G family).

GMOP-G(theta, alpha, lambda): reconstructed survival function (verified against
the printed pdf in eq. (5) by symbolic differentiation)
    S(t; th, al, lam) = al^th * A^th / B^th,
    A = e^{-lam*G(t)} - e^{-lam},
    B = 1 - al*e^{-lam} - (1-al)*e^{-lam*G(t)}.
Baseline chosen: G(t) = 1 - e^{-t} (canonical fixes no baseline).

Theorem 1 (lr): X ~ (th, al1, lam) <=lr Y ~ (th, al2, lam) if al1 < al2.
For a well-defined survival we need B(t) > 0 on t >= 0; B(t->inf) = 1 - al e^{-lam},
which for lam > 0 requires al < e^{lam} (automatic for al in (0,1)). We use
al in (0,1), lam > 0 (and also try lam < 0 where the structure stays positive).
"""
import json, os
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.59139_stattrans-2025-007.json")
OUT = os.path.join(HERE, "eval_doi_10.59139_stattrans-2025-007.result.json")
R = sp.Rational

def S(th, al, lam):
    G = 1 - sp.exp(-x)                       # baseline cdf (exponential)
    A = sp.exp(-lam*G) - sp.exp(-lam)
    B = 1 - al*sp.exp(-lam) - (1 - al)*sp.exp(-lam*G)
    return al**th * A**th / B**th

def go():
    recs = json.load(open(CANON))
    out = []
    for r in recs:
        c = r.get("conclusion") or {}
        order = c.get("order")
        if order not in ("st", "hr", "rh", "lr"):
            out.append(dict(claim=r["claim"], order=order, status="unsupported order",
                            instances=0, witness=None, undecided_points=0))
            continue
        inst = 0; wit = None; und = 0; allhold = True
        # admissible instances: al1 < al2, both < e^{lam}
        for (th, a1, a2, lam) in [(R(1), R(3,10), R(6,10), R(1)),
                                  (R(2), R(1,5), R(9,10), R(1)),
                                  (R(1), R(1,2), R(3,2), R(1,2)),
                                  (R(3), R(2,5), R(4,5), R(2))]:
            X = Closed(S(th, a1, lam)); Y = Closed(S(th, a2, lam))
            h, w, u = cf.check(order, X, Y)
            inst += 1; und += u
            if not h:
                allhold = False; wit = str(w)
        out.append(dict(claim=r["claim"], order=order,
                        status="holds" if allhold else "refuted",
                        instances=inst, witness=wit, undecided_points=und))
    json.dump(out, open(OUT, "w"), indent=1)
    for o in out:
        print(o["claim"], "|", o["order"], "|", o["status"], "| inst", o["instances"],
              "| wit", o["witness"])

if __name__ == "__main__":
    go()
