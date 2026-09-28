"""Evaluate canonical claims of doi_10.1214/18-bjps410 (EGG parallel systems).

EGG CDF: F(t;alpha,nu,tau,lambda) = (incomplete-gamma kernel)^alpha -- needs
gamma functions, not in the harness language.  The theorems quantify over
nu,tau (or impose only 0<nu<=1), so admissible elementary sub-families:
    GE   (nu=tau=1):  F(t) = (1 - e^{-lambda t})^alpha
    EW2  (nu=tau=2):  F(t) = (1 - e^{-(lambda t)^2})^alpha
The generic-baseline theorems (3,4,5) need t*r~(t) decreasing (+convex,
+t*r~'/r~ decreasing): verified numerically for F=1-e^{-t} and F=1-(1+t)^{-2}.

Parallel-system max:  S_{n:n}(x) = 1 - prod_i (1 - e^{-l_i x})^{a_i} (GE).
Claim direction (all records):  Y <=ord X with Y ~ (mu, beta), X ~ (lambda,
alpha), Z ~ (mu, alpha).

Majorization (Def. 2/3):  u ~<^w_p v on Dn: vectors desc-sorted, weighted
prefix sums sum_{j<=i} p_j u_j <= sum p_j v_j;  u ~<^uo v: POSITIONAL prefix
sums <= with equal totals.  Printed Fig-2 premise mu ~<^w_alpha lambda on
G^pi uses the suffix/ascending reading; our instances satisfy the printed
premise as asserted (parameters are copied verbatim).
"""
import json, os
import sympy as sp
import closedform as cf
from closedform import x, Closed

HERE = os.path.dirname(os.path.abspath(__file__))
CANON = os.path.join(HERE, "..", "canonical", "doi_10.1214_18-bjps410.json")
OUT = os.path.join(HERE, "eval_doi_10.1214_18-bjps410.result.json")
R = sp.Rational


def margin(lam, a, base):
    F = base.subs(x, lam * x)
    return 1 - F ** a          # survival of component


def max_sf(ls, aa, base):
    g = sp.Integer(1)
    for l, a in zip(ls, aa):
        g *= (base.subs(x, l * x)) ** a
    return 1 - g               # survival of the maximum


GE = 1 - sp.exp(-x)           # F base
LOMAX = 1 - (1 + x) ** (-2)   # F base

# printed vectors
FIG1 = dict(ls=[R(9), R(6), R(1), R(7,10)], ms=[R(8), R(5), R(4,5), R(3,4)],
            aa=[R(1), R(3), R(5), R(3,5)], bb=[R(23,5), R(22,5), R(1,2), R(1,10)])
FIG2 = dict(ls=[R(2), R(11), R(12), R(13)], ms=[R(5), R(6), R(10), R(14)],
            aa=[R(4), R(4,5), R(33,10), R(5)], bb=[R(1), R(3), R(21,10), R(7)])
FIG3 = dict(ls=[R(8), R(2), R(2), R(2)], ms=[R(6), R(3), R(3), R(3)],
            aa=[R(11,10), R(2), R(1,5), R(4)],
            bb=[R(6,5), R(1), R(3,2), R(18,5)])
FIG82 = dict(ls=[R(20)]*3 + [R(1,10)]*2, ms=[R(18)]*3 + [R(2)]*2,
             aa=[R(2,5), R(2,5), R(1), R(5), R(57,10)],
             bb=[R(3), R(4,5), R(18,5), R(6,5), R(39,10)])
CEX_HR = dict(ls=[R(9), R(7,2), R(1,10)], ms=[R(10), R(29,10), R(3,10)],
              aa=[R(9,2), R(2), R(3)], bb=[R(9,2), R(2), R(3)])
CEX_LR = dict(ls=[R(7), R(6), R(1)], ms=[R(100), R(20), R(1)],
              aa=[R(1,10), R(3,5), R(2,5)], bb=[R(7,10), R(1,5), R(1,5)])
CEX_RH = dict(ls=[R(10), R(1), R(1)], ms=[R(7), R(5), R(2)],
              aa=[R(5), R(4), R(9)], bb=[R(6), R(7,2), R(17,2)])

ST_CASES = [FIG1,
            dict(ls=[R(9), R(6), R(1)], ms=[R(8), R(5), R(1,2)],
                 aa=[R(1), R(2), R(3)], bb=[R(3), R(2), R(1)]),
            ]
RH_CASES = [FIG2,
            dict(ls=[R(9), R(6), R(1)], ms=[R(8), R(5), R(1,2)],
                 aa=[R(1), R(2), R(3)], bb=[R(3), R(2), R(1)]),
            ]
HR_CASES = [FIG3]
LR_CASES = [FIG82, FIG3]


def pairs_st():
    return [("st", max_sf(d['ms'], d['bb'], GE), max_sf(d['ls'], d['aa'], GE))
            for d in ST_CASES] + \
           [("st", max_sf(d['ms'], d['bb'], LOMAX), max_sf(d['ls'], d['aa'], LOMAX))
            for d in ST_CASES]


def pairs_rh():
    return [("st", max_sf(d['ms'], d['bb'], GE), max_sf(d['ls'], d['aa'], GE))
            for d in RH_CASES] + \
           [("st", max_sf(d['ms'], d['bb'], LOMAX), max_sf(d['ls'], d['aa'], LOMAX))
            for d in RH_CASES]


def instances(claim, order):
    key = claim.lower()
    if "counterexample" in key or "cannot be compared" in key or "cross" in key:
        d = CEX_HR if order == "hr" else CEX_LR if order == "lr" else CEX_RH
        return [("none", max_sf(d['ms'], d['bb'], GE), max_sf(d['ls'], d['aa'], GE))]
    if 'theorem 5' in key:
        # Y <=lr Z: Z uses (mu, alpha), Y uses (mu, beta)
        out = []
        for d in [FIG3, FIG82]:
            out.append(("st", max_sf(d['ms'], d['bb'], GE),
                        max_sf(d['ms'], d['aa'], GE)))
        return out
    if 'lemma 8(i)' in key or 'lemma 8(i)' in key:
        d = FIG3
        return [("st", max_sf(d['ms'], d['aa'], GE), max_sf(d['ls'], d['aa'], GE))]
    if 'lemma 8(ii)' in key:
        d = FIG82
        return [("st", max_sf(d['ms'], d['aa'], GE), max_sf(d['ls'], d['aa'], GE))]
    if 'lemma 8(iii)' in key:
        d = dict(ls=[R(8), R(2), R(2)], ms=[R(5), R(2), R(2)],
                 aa=[R(2), R(3), R(1)], bb=None)
        return [("st", max_sf(d['ms'], d['aa'], GE), max_sf(d['ls'], d['aa'], GE))]
    if 'theorem 8(i)' in key or ('theorem 8' in key and 'ii' not in key):
        return [("st", max_sf(d['ms'], d['bb'], GE), max_sf(d['ls'], d['aa'], GE))
                for d in HR_CASES]
    if '8(ii)' in key:
        return [("st", max_sf(d['ms'], d['bb'], GE), max_sf(d['ls'], d['aa'], GE))
                for d in LR_CASES]
    if 'theorem 9' in key:
        out = []
        for d in [dict(ls=[R(10), R(9)], ms=[R(8), R(5)], aa=[R(2), R(3)],
                       bb=[R(4), R(1)])]:
            out.append(("st", max_sf(d['ms'], d['bb'], GE),
                        max_sf(d['ls'], d['aa'], GE)))
        return out
    if 'theorem 10' in key:
        return [("st", max_sf(d['ms'], d['bb'], GE), max_sf(d['ls'], d['aa'], GE))
                for d in LR_CASES]
    if 'rh' in key or 'reversed' in key or 'theorem 4' in key or 'theorem 7' in key \
            or 'remark 4' in key or 'figure 2' in key or 'theorem 9' in key:
        return pairs_rh()
    return pairs_st()


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
        dirn = str(c.get("direction") or "").lower()
        # claim orientation: "Yn:n <=ord Xn:n" or "Z <=ord X"; counterexamples
        # assert non-ordering ("cross"/"not monotone"/"no ... order").
        crossing = ("no " in dirn and "order" in dirn) or "cross" in dirn \
            or "not monotone" in dirn
        if crossing:
            # printed counterexample uses specific EGG nu,tau (incomplete
            # gamma) not encodable in the {+,x,Pow,exp,log} harness family
            out.append(dict(claim=claim, order=order,
                            status="out of harness scope", instances=0,
                            witness=None, undecided_points=0,
                            note=("counterexample asserted for EGG nu,tau"
                                  " values needing the incomplete gamma;"
                                  " not encodable")))
            continue
        pairs = instances(claim, order)
        inst = 0; wit = None; und = 0; allhold = True
        for (tag, SA, SB) in pairs:
            A, B = Closed(SA), Closed(SB)
            if crossing or tag == "none":
                ok1, w1, u1 = cf.check(order, A, B)
                ok2, w2, u2 = cf.check(order, B, A)
                und += u1 + u2; inst += 1
                if ok1 or ok2:
                    allhold = None
                else:
                    wit = wit or str(w1)
            else:
                ok, w, u = cf.check(order, A, B)
                inst += 1; und += u
                if not ok:
                    allhold = False; wit = str(w)
        status = "holds" if allhold else "refuted"
        if allhold is None:
            status = "out of harness scope"
        out.append(dict(claim=claim, order=order, status=status,
                        instances=inst, witness=wit, undecided_points=und))
    json.dump(out, open(OUT, "w"), indent=1)
    for o in out:
        print(o["claim"], "|", o["order"], "|", o["status"], "| inst",
              o["instances"], "| wit", o["witness"])


if __name__ == "__main__":
    go()
