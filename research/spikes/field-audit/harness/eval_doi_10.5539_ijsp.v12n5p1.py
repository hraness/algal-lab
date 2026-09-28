"""Evaluate canonical claims of doi_10.5539/ijsp.v12n5p1 (MOEGE family).

Marshall-Olkin Extended Generalized Exponential MOEGE(alpha, eta, rho):
    F(x) = U / (1 - abar*(1 - U)),   U = (1 - e^{-eta x})^rho,
    S(x) = alpha*(1 - U) / (1 - abar*(1 - U)),   abar = 1 - alpha.
(eqs (6)-(7) of the paper; alpha>0 is the tilt parameter.)

Section 3.6 claims X1 <=_{lr,hr,st} X2 when alpha1 < alpha2 with common eta,rho.
"""
import json, os
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.5539_ijsp.v12n5p1.json")
OUT = os.path.join(HERE, "eval_doi_10.5539_ijsp.v12n5p1.result.json")
R = sp.Rational

def S(al, et, ro):
    U = (1 - sp.exp(-et*x))**ro
    return al*(1 - U) / (1 - (1 - al)*(1 - U))

ORDER_CLAIM = {"lr": "likelihood ratio order", "hr": "hazard rate order",
               "st": "usual stochastic order"}

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
        for (a1, a2, et, ro) in [(R(3,10), R(6,10), R(1), R(2)),
                                 (R(1,5), R(9,10), R(2), R(3)),
                                 (R(2,5), R(4,5), R(1), R(5)),
                                 (R(1,10), R(1,2), R(3), R(2))]:
            X1 = Closed(S(a1, et, ro)); X2 = Closed(S(a2, et, ro))
            h, w, u = cf.check(order, X1, X2)
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
