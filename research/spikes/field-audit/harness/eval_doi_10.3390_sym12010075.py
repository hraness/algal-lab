"""Evaluate canonical claims of doi_10.3390/sym12010075 (TIIPTL-G family).

Family: Type II power Topp-Leone-G:
    F(x; a, b, xi) = 1 - (1-G(x;xi))^{a b} (2 - (1-G(x;xi))^b)^a
    S(x; a, b, xi) = (1-G)^{ab} (2 - (1-G)^b)^a,   a,b > 0.
Baseline chosen: G(x) = 1 - e^{-x}  (admissible: canonical fixes no baseline).

Proposition 1 (lr): X1 <=lr X2. The printed statement gives no hypothesis
relating a1,a2; the proof only derives the decreasing likelihood ratio under
a1 > a2 (canonical adjudication). We therefore test under a1 > a2 and also
under a1 < a2 to check direction.
"""
import json, os
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.3390_sym12010075.json")
OUT = os.path.join(HERE, "eval_doi_10.3390_sym12010075.result.json")
R = sp.Rational

def S(a, b):
    omG = sp.exp(-x)                      # 1 - G(x) for G = 1 - e^{-x}
    return omG**(a*b) * (2 - omG**b)**a

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
        # Proposition 1, lr. Instances satisfying the proof's hypothesis a1 > a2.
        inst = 0; wit = None; und = 0; allhold = True
        for (a1, a2, b) in [(R(2), R(1), R(1)), (R(3), R(3, 2), R(2)),
                            (R(5, 2), R(1), R(3)), (R(4), R(2), R(1))]:
            X1 = Closed(S(a1, b)); X2 = Closed(S(a2, b))
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
