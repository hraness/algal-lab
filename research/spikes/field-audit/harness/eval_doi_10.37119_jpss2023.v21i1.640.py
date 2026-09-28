"""Evaluate canonical claims of doi_10.37119/jpss2023.v21i1.640 (MWR).

Modified weighted Rayleigh MWR(sigma, lam):
    f(x) = (1+lam^2) x/sig^2 * exp(-(1+lam^2) x^2/(2 sig^2))
    S(x) = exp(-(1+lam^2) x^2/(2 sig^2)),   x > 0, sig > 0, lam >= 0.

Theorem (1)(i): X ~ (sig, lam1) <=_{lr,hr,st} Y ~ (sig, lam2), lam1 > lam2.
Theorem (1)(ii): X ~ (sig1, lam) <=_{lr,hr,st} Y ~ (sig2, lam), sig1 < sig2.
"""
import json, os
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.37119_jpss2023.v21i1.640.json")
OUT = os.path.join(HERE, "eval_doi_10.37119_jpss2023.v21i1.640.result.json")
R = sp.Rational

def S(sig, lam):
    return sp.exp(-(1+lam**2)*x**2/(2*sig**2))

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
        if "(i)" in claim and "(ii)" not in claim:
            insts = [  # common sigma, lam1 > lam2 (X has larger lambda)
                (R(1), R(2), R(1), R(1)),
                (R(2), R(3), R(2), R(1,2)),
                (R(1), R(5,2), R(1), R(3,2)),
                (R(3), R(4), R(3), R(2)),
            ]
            for (s, l1, s2, l2) in insts:
                X = Closed(S(s, l1)); Y = Closed(S(s2, l2))
                ok, w, u = cf.check(order, X, Y)
                inst += 1; und += u
                if not ok:
                    allhold = False; wit = str(w)
        else:
            insts = [  # common lambda, sig1 < sig2 (X has smaller sigma)
                (R(1), R(1), R(2), R(1)),
                (R(1,2), R(2), R(1), R(2)),
                (R(2), R(1), R(3), R(1)),
                (R(3,4), R(3), R(2), R(3)),
            ]
            for (s1, l, s2, l2) in insts:
                X = Closed(S(s1, l)); Y = Closed(S(s2, l2))
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
