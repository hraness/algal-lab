"""Evaluate canonical claims of doi_10.28924/2291-8639-23-2025-286 (Monsef).

Monsef distribution MoD(d), d > 0:
    f(v; d) = d^3 (v+1)^2 e^{-d v} / (d^2 + 2d + 2)
    S(v; d) = e^{-d v} (d^2 (v+1)^2 + 2d(v+1) + 2) / (d^2 + 2d + 2)
(antiderivative verified symbolically; S(0) = 1, S(inf) = 0).

Section 2.4: V1 ~ MoD(d1) <=_{lr,hr,rh,st} V2 ~ MoD(d2) when d2 < d1
(larger delta gives the smaller variable).
"""
import json, os
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.28924_2291-8639-23-2025-286.json")
OUT = os.path.join(HERE, "eval_doi_10.28924_2291-8639-23-2025-286.result.json")
R = sp.Rational

def S(d):
    D = d**2 + 2*d + 2
    return sp.exp(-d*x) * (d**2*(x+1)**2 + 2*d*(x+1) + 2) / D

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
        for (d1, d2) in [(R(2), R(1)), (R(3), R(1)), (R(5), R(3)), (R(7,2), R(3,2))]:
            V1 = Closed(S(d1)); V2 = Closed(S(d2))
            ok, w, u = cf.check(order, V1, V2)
            inst += 1; und += u
            if not ok:
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
