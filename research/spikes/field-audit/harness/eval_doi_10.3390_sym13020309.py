"""Evaluator for doi:10.3390/sym13020309 (half-logistic inverse Lomax, HLIL).

Claim 1 (Eq. 7): alpha2<=a1, lam1<=l2, beta1<=b2 => F(phi1) <= F(phi2)
       i.e. HLIL(phi1) >=st HLIL(phi2).
Claim 2: for beta in (0,1], HLIL(a,lam,beta) >=st IL(a,lam).

Half-logistic-G cdf: F = (1-(1-G)^beta)/(1+(1-G)^beta) with IL cdf
G = w^alpha, w = x/(x+lam).
"""
import json
import auditlib as A
import sympy as sp

x = A.x


def run_st(px, py):
    """claim: HLIL(px) >=st HLIL(py) i.e. py <=st px."""
    X = A.C(1 - A.hlil_cdf(*[A.R(v) for v in px]))
    Y = A.C(1 - A.hlil_cdf(*[A.R(v) for v in py]))
    return A.check_dist("st", Y, X)


def main():
    claims = json.load(open("../canonical/doi_10.3390_sym13020309.json"))
    out = []
    for recd in claims:
        order = recd["conclusion"]["order"]
        if order != "st":
            out.append(A.rec(recd, "unsupported order"))
            continue
        n = und = 0
        wit = None
        if "Equation (7)" in recd["claim"]:
            # phi1 = (a1,l1,b1), phi2 = (a2,l2,b2) with a2<=a1, l1<=l2, b1<=b2
            insts = [((2, 1, 1), (1, 2, 2)),
                     ((2, 1, A.R(1, 2)), (1, 1, 1)),
                     ((3, 1, 1), (2, 3, 2))]
        else:
            # HLIL(a,lam,beta) >=st IL(a,lam) for beta<=1:
            # st check A<=B means S_A<=S_B i.e. F_A>=F_B.
            n = und = 0
            for a, lam, b in [(1, 1, 1), (2, 1, A.R(1, 2)), (1, 2, A.R(1, 3)),
                              (A.R(1, 2), 1, A.R(1, 4))]:
                Xh = A.C(1 - A.hlil_cdf(A.R(a), A.R(lam), A.R(b)))
                Xil = A.C(1 - A.il_cdf(A.R(a), A.R(lam)))
                # claim: HLIL >=st IL i.e. IL <=st HLIL
                h, w, u = A.check_dist("st", Xil, Xh)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            out.append(A.rec(recd, "holds" if wit is None else "refuted",
                             instances=n, witness=str(wit) if wit else None,
                             undecided=und, note="beta in (0,1] as printed."))
            continue
        for px, py in insts:
            h, w, u = run_st(px, py)
            n += 1
            und += u
            if not h and wit is None:
                wit = w
        out.append(A.rec(recd, "holds" if wit is None else "refuted",
                         instances=n, witness=str(wit) if wit else None,
                         undecided=und))
    A.emit("eval_doi_10.3390_sym13020309.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
