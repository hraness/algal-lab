"""Evaluate canonical claims of doi_10.32604/csse.2021.017362 (ILBMD).

Inverse length-biased Maxwell distribution ILBMD(a), a > 0:
    f(x; a) = (1/(2 a^4 x^5)) exp(-1/(2 a^2 x^2)),  x > 0.
Integrated survival (verified symbolically):
    S(x; a) = 1 - (1 + 1/(2 a^2 x^2)) exp(-1/(2 a^2 x^2)).
X ~ ILBMD(a), Y ~ ILBMD(h) with h < a: claim X <=_{lr,hr,st,mrl} Y.
mrl is unsupported by the frozen harness.
"""
import json, os
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.32604_csse.2021.017362.json")
OUT = os.path.join(HERE, "eval_doi_10.32604_csse.2021.017362.result.json")
R = sp.Rational

def S(a):
    u = R(1, 2) / (a**2 * x**2)             # 1/(2 a^2 x^2)
    return 1 - (1 + u)*sp.exp(-u)

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
        for (a, h) in [(R(2), R(1)), (R(3), R(1)), (R(5), R(2)), (R(3,2), R(1,2))]:
            X = Closed(S(a)); Y = Closed(S(h))
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
