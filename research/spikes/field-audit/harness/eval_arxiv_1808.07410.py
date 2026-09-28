"""Evaluate canonical claims of arxiv:1808.07410 (EIPLD).

Exponentiated Inverse Power Lindley EIPLD(alpha, beta, theta):
    G(z) = [ (1 + beta/((1+beta) z^a)) * e^{-beta / z^a} ]^theta,  z > 0
    S(z) = 1 - G(z).
(the e^{-beta/z^a} multiplies the whole bracket, as the printed pdf's
e^{-theta*beta/z^a} factor confirms).

Theorem 4: Y ~ (a, b1, t1) <=_{lr,hr,mrl,st} Z ~ (a, b2, t2) under
  case 1: equal beta (b1 = b2), theta2 >= theta1;
  case 2: equal theta, beta2 >= beta1;
  alpha set equal in the proof (canonical adjudication), so we use a1 = a2.
mrl is unsupported.  The "Section 8 definitions" record asserts an
implication chain between orders rather than a comparison of two named
distributions -> out of harness scope.
"""
import json, os
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "arxiv_1808.07410.json")
OUT = os.path.join(HERE, "eval_arxiv_1808.07410.result.json")
R = sp.Rational

def S(a, b, t):
    return 1 - ((1 + b/((1+b)*x**a)) * sp.exp(-b/x**a))**t

CASE1 = [  # equal beta, theta2 >= theta1
    (R(1), R(1), R(2), R(1), R(2)),   # a, b(=b1=b2), -, t1, t2
    (R(2), R(3), None, R(1), R(3)),
    (R(1,2), R(1,2), None, R(2), R(4)),
]
CASE2 = [  # equal theta, beta2 >= beta1
    (R(1), R(1), R(2), R(1), R(1)),   # a, b1, b2, t(=t1=t2), -
    (R(2), R(1,2), R(3,2), R(2), R(2)),
    (R(1), R(1,4), R(1), R(3), R(3)),
]

def go():
    recs = json.load(open(CANON))
    out = []
    for r in recs:
        c = r.get("conclusion") or {}
        order = c.get("order")
        claim = r["claim"]
        if "Section 8" in claim:
            out.append(dict(claim=claim, order=order, status="out of harness scope",
                            instances=0, witness=None, undecided_points=0))
            continue
        if order not in ("st", "hr", "rh", "lr"):
            out.append(dict(claim=claim, order=order, status="unsupported order",
                            instances=0, witness=None, undecided_points=0))
            continue
        inst = 0; wit = None; und = 0; allhold = True
        for (a, b1, b2, t1, t2) in CASE1 + CASE2:
            bb2 = b2 if b2 is not None else b1
            tt2 = t2 if t2 is not None else t1
            Y = Closed(S(a, b1, t1)); Z = Closed(S(a, bb2, tt2))
            ok, w, u = cf.check(order, Y, Z)
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
