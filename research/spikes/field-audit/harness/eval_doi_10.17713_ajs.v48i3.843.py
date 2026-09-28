"""Evaluate canonical claims of doi_10.17713/ajs.v48i3.843 (gamma-Lindley GaL).

GaL(alpha, beta), alpha,beta > 0, x > 0:
    f(x) = a*b^2 (1+a+b+x) x^{a-1} / [(1+b)(b+x)^{2+a}]
    R(x) = [(b+x)^{a+1}(1+b) - x^a (1+b)(b+x) - b a x^a] / [(b+x)^{a+1}(1+b)]

Theorem 4:
  case a1 = a2:  X1 <=_{lr,hr,st} X2  iff  b1 <= b2  (we test the b1 < b2 direction);
  case b1 = b2 >= 1:  X1 <=_{lr,hr,st} X2  iff  a1 <= a2.
"""
import json, os
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.17713_ajs.v48i3.843.json")
OUT = os.path.join(HERE, "eval_doi_10.17713_ajs.v48i3.843.result.json")
R = sp.Rational

def S(a, b):
    num = (b+x)**(a+1)*(1+b) - x**a*(1+b)*(b+x) - b*a*x**a
    return num / ((b+x)**(a+1)*(1+b))

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
        if "α1 = α2" in claim:
            insts = [  # shared a, b1 < b2
                (R(1), R(1), R(1,2), R(2)),
                (R(2), R(2), R(1), R(3)),
                (R(1,2), R(1,2), R(2), R(4)),
                (R(3), R(3), R(1), R(2)),
            ]
            for (a1, a2, b1, b2) in insts:
                X1 = Closed(S(a1, b1)); X2 = Closed(S(a2, b2))
                ok, w, u = cf.check(order, X1, X2)
                inst += 1; und += u
                if not ok:
                    allhold = False; wit = str(w)
        else:  # case beta1 = beta2 >= 1: shared b >= 1, a1 < a2
            insts = [
                (R(1), R(2), R(1), R(1)),
                (R(1,2), R(3), R(2), R(2)),
                (R(2), R(4), R(3), R(3)),
                (R(1,3), R(1), R(5,2), R(5,2)),
            ]
            for (a1, a2, b1, b2) in insts:
                X1 = Closed(S(a1, b1)); X2 = Closed(S(a2, b2))
                ok, w, u = cf.check(order, X1, X2)
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
