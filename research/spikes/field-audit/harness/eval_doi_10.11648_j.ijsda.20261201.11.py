"""Evaluator for doi:10.11648/j.ijsda.20261201.11 (Kumaraswamy EE, KwEE).

Theorem 9.1:  X ~ KwEE(a1,b1,l1), Y ~ KwEE(a2,b2,l2):
  case i : a1=a2, b1=b2, l1>l2  => X <=lr Y <=hr <=st
  case ii: a1<a2, b1<b2, l1=l2 => same chain.
Survival: S(x) = (1 - (1 - e^{-lam x})^a)^b.  Integer params => rational in
z = e^{-x}; tested exactly.
"""
import json
import auditlib as A
from ratdist import Dist
import sympy as sp

z = A.z
x = A.x


def kwee_rat(a, b, lam2):
    """S = (1 - (1 - z^{lam2})^a)^b with z = e^{-x}; lam2 = printed lam^2 exp."""
    p = 1 - (1 - z ** lam2) ** a
    return Dist(sp.expand(p ** b), 0, 1, False)


def main():
    claims = json.load(open("../canonical/doi_10.11648_j.ijsda.20261201.11.json"))
    out = []
    # case i: a=b common; lam1 > lam2 (printed scale squared); use a=b=2, lam1^2=2, lam2^2=1
    inst_i = [(dict(a=2, b=2, l2=2), dict(a=2, b=2, l2=1)),
              (dict(a=1, b=3, l2=4), dict(a=1, b=3, l2=2)),
              (dict(a=3, b=1, l2=9), dict(a=3, b=1, l2=4))]
    # case ii: common lam; a1<a2, b1<b2
    inst_ii = [(dict(a=1, b=1, l2=1), dict(a=2, b=2, l2=1)),
               (dict(a=1, b=2, l2=4), dict(a=3, b=4, l2=4)),
               (dict(a=2, b=1, l2=2), dict(a=4, b=3, l2=2))]
    for recd in claims:
        order = recd["conclusion"]["order"]
        case = "case i" if "case i," in recd["claim"] else "case ii"
        if order not in ("st", "hr", "rh", "lr"):
            out.append(A.rec(recd, "unsupported order"))
            continue
        insts = inst_i if case == "case i" else inst_ii
        n = und = 0
        wit = None
        for px, py in insts:
            X = kwee_rat(px["a"], px["b"], px["l2"])
            Y = kwee_rat(py["a"], py["b"], py["l2"])
            h, w = A.test_rat(order, X, Y)
            n += 1
            if not h and wit is None:
                wit = w
        out.append(A.rec(recd, "holds" if wit is None else "refuted",
                         instances=n, witness=str(wit) if wit else None,
                         undecided=und,
                         note=f"exact rational check, z=e^-x; {case}."))
    A.emit("eval_doi_10.11648_j.ijsda.20261201.11.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
