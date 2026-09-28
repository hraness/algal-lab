"""Evaluator for doi:10.1016/j.spl.2019.108691 (BG order statistics, SSD).

All printed dominance claims use the SSD/icv relation '>=2' except one
unnumbered FSD (st-order) statement: Z1 >=st Z2 when every input of the
decomposable composition FZ = FT(QY(FX)) FSD-dominates the corresponding
input of Z2.

The FSD claim is tested on a concrete instance: FT_i(u)=u^i powers and
QY likewise (any increasing generators), FX_i on (0,1).  With
componentwise FSD domination the composition inherits the order
pointwise -- tested with x^2 vs x^3 and x vs sqrt(x).
"""
import json
import auditlib as A
import sympy as sp

x = A.x
e = A.e


def main():
    claims = json.load(open("../canonical/doi_10.1016_j.spl.2019.108691.json"))
    out = []

    def add(recd, status, instances=0, witness=None, undecided=0, note=None):
        out.append(A.rec(recd, status, instances=instances, witness=witness,
                         undecided=undecided, note=note))

    for recd in claims:
        c = recd["claim"]
        order = recd["conclusion"]["order"]

        if c.startswith("Section 3 unnumbered FSD"):
            # FZ = FT(QY(FX(x))); FSD componentwise domination of all
            # three maps forces FZ1 <= FZ2 pointwise (maps increasing).
            FX1, FX2 = x ** 2, x          # FX1 <= FX2 on (0,1)
            QY1, QY2 = x ** 3, x          # QY1 <= QY2
            FT1, FT2 = x ** 2, x          # FT1 <= FT2
            FZ1 = FT1.subs(x, QY1.subs(x, FX1))
            FZ2 = FT2.subs(x, QY2.subs(x, FX2))
            # claim Z1 >=st Z2 <=> Z2 <=st Z1: E = S_Z1 - S_Z2 >= 0
            h, w, u = A.check_dist("st", A.C(1 - FZ2, 0, 1),
                                   A.C(1 - FZ1, 0, 1))
            # h=True <=> (1-FZ1)-(1-FZ2) = FZ2-FZ1 >= 0 <=> Z1 >=st Z2
            add(recd, "holds" if h else "refuted", 1,
                str(w) if w else None, u,
                note="instance FT1=u^2<=FT2=u, QY1=v^3<=v=QY2, FX1=x^2<=x"
                     "=FX2: composition gives FZ1=x^6 <= FZ2=x on (0,1).")
            continue

        # all remaining records are icv (SSD) -- not implemented
        add(recd, "unsupported order",
            note="icv (integrated-CDF/SSD) order is outside the harness "
                 "order set.")

    A.emit("eval_doi_10.1016_j.spl.2019.108691.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
