"""Evaluate canonical claims of arxiv:2601.07249 (CLFRD).

Compounded linear failure rate CLFRD(a, b, l), a,b,l > 0:
    S(x) = exp(-a x - b x^2/2 - l + l exp(-a x - b x^2/2))
    g(x) = (a + b x)(1 + l e^{-a x - b x^2/2}) * S(x)   (printed pdf eq (3))

Theorem 3.2: joint reading -- a1<=a2, b1<=b2, l1<=l2 ==> Y <=lr X (X>=lr Y).
Known pilot refutation at X=(1,1,1), Y=(1,2,1), witness near x=0.
Remark 3.3 lists st, hr, rh (plus convex, concave, mrl, hmrl -> unsupported).
"""
import json, os
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "arxiv_2601.07249.json")
OUT = os.path.join(HERE, "eval_arxiv_2601.07249.result.json")
R = sp.Rational

def S(a, b, l):
    E = sp.exp(-a*x - b*x**2/2)
    return sp.exp(-a*x - b*x**2/2 - l + l*E)

# admissible instances with a1<=a2, b1<=b2, l1<=l2 (joint componentwise order)
INST = [(R(1), R(1), R(1), R(1), R(2), R(1)),
        (R(1), R(1), R(1), R(2), R(1), R(1)),
        (R(1), R(1), R(1), R(1), R(1), R(2)),
        (R(1,2), R(1), R(1,2), R(1), R(3,2), R(2)),
        (R(1), R(1,2), R(1,3), R(2), R(3,4), R(1,2))]

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
        for (a1, b1, l1, a2, b2, l2) in INST:
            X = Closed(S(a1, b1, l1)); Y = Closed(S(a2, b2, l2))
            # claim: X >=order Y  i.e. Y <=order X
            ok, w, u = cf.check(order, Y, X)
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
