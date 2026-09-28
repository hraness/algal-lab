"""Evaluate canonical claim of doi_10.1007/s44199-026-00167-w (GTL-HT-G).

Gamma Topp-Leone-Heavy-Tailed-G family, cdf eq (3):
    F(x; d, b, th, psi) = 1 - gamma(-log((1-U_G)^b), d)/Gamma(d),
    1 - U_G(x; th, psi) = [Gbar(x) / (1 - (1-th) G(x))]^{2 th}.
The printed cdf is increasing in the regularized-lower-gamma argument and
equals 1 at L=0, so it is actually the SURVIVAL (upper-regularized gamma);
the pdf eq (4) confirms
    f_i ∝ Gamma(d2)^{-1} [b(-log(1-U_G))]^{d_i - 1} * (d-independent factors),
so f1/f2 ∝ L(x)^{d1-d2} with L(x) = -b log(1-U_G(x)) INCREASING in x.
Hence for d1 > d2 the ratio f1/f2 is increasing, i.e. X1 >=lr X2 -- opposite
of the printed claim "X1 <=lr X2 for d1 > d2".

The claim is tested on the only elementary subfamily: integer d (gamma cdf
in closed form), baseline G(x) = 1 - e^{-x}, various b, theta.
S_d(x) = Gamma(d, L(x))/Gamma(d) = e^{-L} sum_{k<d} L^k/k! .
"""
import json, os
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.1007_s44199-026-00167-w.json")
OUT = os.path.join(HERE, "eval_doi_10.1007_s44199-026-00167-w.result.json")
R = sp.Rational

def Lfun(b, th):
    # L(x) = -b*log(1-U_G),  1-U_G = (e^{-x}/(th+(1-th)e^{-x}))^{2 th}
    # expand the log explicitly so no Pow-inside-log / Abs nodes appear
    D = th + (1-th)*sp.exp(-x)
    return 2*b*th*(x + sp.log(D))

def S(d, b, th):
    # integer d: S = e^{-L} * sum_{k=0}^{d-1} L^k/k!
    L = Lfun(b, th)
    return sp.exp(-L) * sum(L**k/sp.factorial(k) for k in range(int(d)))

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
        # hypothesis: d1 > d2, common th, b, baseline.  Claim: X1 <=lr X2.
        for (d1, d2, b, th) in [(2, 1, R(1), R(1)), (3, 1, R(1), R(1)),
                                (3, 2, R(1), R(1)), (2, 1, R(2), R(2)),
                                (3, 1, R(1,2), R(3))]:
            X1 = Closed(S(d1, b, th)); X2 = Closed(S(d2, b, th))
            ok, w, u = cf.check(order, X1, X2)
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
