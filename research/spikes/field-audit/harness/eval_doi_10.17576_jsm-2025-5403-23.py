"""Evaluate canonical claims of doi_10.17576/jsm-2025-5403-23 (GTHPL).

Gompertz three-parameter Lindley GTHPL(alpha, beta, eta, lam):
    f(x) = lam*al^2 e^{lam x} (beta*u + 2*eta) / [(al*beta + eta) u^3]
    S(x) = al^2 (beta*u + eta) / [(al*beta + eta) u^2],  u = e^{lam x} + al - 1
(integration verified symbolically: -S' reproduces the printed pdf eq (7)).
alpha, eta, lam > 0, beta >= 0.

Theorem 2.3 (OCR of p.933): X ~ GTHPL(a1,b,n,l), Y ~ GTHPL(a2,b,n,l),
0 < a1 < a2  ==>  X <=_{lr,fr,mrl,st} Y.  mrl unsupported.
The "definitions" record asserts no comparison -> out of harness scope.
"""
import json, os
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.17576_jsm-2025-5403-23.json")
OUT = os.path.join(HERE, "eval_doi_10.17576_jsm-2025-5403-23.result.json")
R = sp.Rational

def S(al, be, et, la):
    u = sp.exp(la*x) + al - 1
    return al**2 * (be*u + et) / ((al*be + et) * u**2)

def go():
    recs = json.load(open(CANON))
    out = []
    for r in recs:
        c = r.get("conclusion") or {}
        order = c.get("order")
        claim = r["claim"]
        if "definitions" in claim.lower() or "Stochastic-order definitions" in claim:
            out.append(dict(claim=claim, order=order, status="out of harness scope",
                            instances=0, witness=None, undecided_points=0))
            continue
        if order not in ("st", "hr", "rh", "lr"):
            out.append(dict(claim=claim, order=order, status="unsupported order",
                            instances=0, witness=None, undecided_points=0))
            continue
        inst = 0; wit = None; und = 0; allhold = True
        for (a1, a2, be, et, la) in [(R(1), R(2), R(1), R(1), R(1)),
                                    (R(1,2), R(3), R(0), R(2), R(2)),
                                    (R(2), R(4), R(3), R(1,2), R(1,2)),
                                    (R(1), R(3,2), R(2), R(5), R(3))]:
            X = Closed(S(a1, be, et, la)); Y = Closed(S(a2, be, et, la))
            ok, w, u = cf.check(order, X, Y)
            inst += 1; und += u
            if not ok:
                allhold = False; wit = str(w)
        out.append(dict(claim=claim, order=order,
                        status="holds" if allhold else "refuted",
                        instances=inst, witness=wit, undecided_points=und))
    json.dump(out, open(OUT, "w"), indent=1)
    for o in out:
        print(o["claim"], "|", o["order"], "|", o["status"], "| inst", o["instances"],
              "| wit", o["witness"])

if __name__ == "__main__":
    go()
