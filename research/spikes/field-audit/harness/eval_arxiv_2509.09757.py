"""Evaluate canonical claims of arxiv:2509.09757 (RBTLL).

Record-based transmuted log-logistic RBTLL(gamma, v, p), p in (0,1):
    G(x) = e^g x^v / (1 + e^g x^v)   (log-logistic baseline)
    F(x) = G + p (1-G) log(1-G)
    S(x) = (1 + p log(1 + e^g x^v)) / (1 + e^g x^v).

Theorem 1: X ~ (g, v, p1) <=_{lr,hr,mrl,st} Y ~ (g, v, p2) when p1 < p2.
mrl is unsupported by the frozen harness.
"""
import json, os
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "arxiv_2509.09757.json")
OUT = os.path.join(HERE, "eval_arxiv_2509.09757.result.json")
R = sp.Rational

def S(g, v, p):
    L = sp.log(1 + sp.exp(g) * x**v)
    return (1 + p*L) / (1 + sp.exp(g)*x**v)

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
        for (g, v, p1, p2) in [(R(1), R(2), R(1,5), R(1,2)),
                               (R(0), R(1), R(1,10), R(9,10)),
                               (R(2), R(3), R(3,10), R(7,10)),
                               (R(-1), R(1,2), R(1,4), R(3,4))]:
            X = Closed(S(g, v, p1)); Y = Closed(S(g, v, p2))
            ok, w, u = cf.check(order, X, Y)
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
