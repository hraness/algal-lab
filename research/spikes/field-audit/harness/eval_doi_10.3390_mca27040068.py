"""Evaluator for doi:10.3390/mca27040068 (odd exponential-logarithmic-G, OEL-G).

Proposition 4: X1 (p1), X2 (p2) in the OEL-G family with common beta and
baseline G; p1 <= p2 => X1 <=lr X2 (=> <=hr, <=st).
F(x) = 1 - (1/log p) log(1 - (1-p) exp(-beta G/(1-G))).
Baseline instance: G(x) = 1 - e^{-x} (exponential).
"""
import json
import auditlib as A
import sympy as sp

x = A.x
E = A.e


def oelg_surv(p, beta, G):
    Gx = G
    inner = 1 - (1 - p) * E ** (-beta * Gx / (1 - Gx))
    return (1 / sp.log(p)) * sp.log(inner)


def run(order, p1, p2, beta):
    G = 1 - E ** (-x)
    X = A.C(oelg_surv(A.R(p1), A.R(beta), G))
    Y = A.C(oelg_surv(A.R(p2), A.R(beta), G))
    return A.check_dist(order, X, Y)


def main():
    claims = json.load(open("../canonical/doi_10.3390_mca27040068.json"))
    out = []
    insts = [(A.R(1, 4), A.R(1, 2), A.R(1)),
             (A.R(1, 2), A.R(3, 4), A.R(2)),
             (A.R(1, 3), A.R(4, 5), A.R(1, 2))]
    for recd in claims:
        order = recd["conclusion"]["order"]
        if order not in ("st", "hr", "rh", "lr"):
            out.append(A.rec(recd, "unsupported order"))
            continue
        n = und = 0
        wit = None
        for p1, p2, b in insts:
            h, w, u = run(order, p1, p2, b)
            n += 1
            und += u
            if not h and wit is None:
                wit = w
        out.append(A.rec(recd, "holds" if wit is None else "refuted",
                         instances=n, witness=str(wit) if wit else None,
                         undecided=und, note="baseline G = Exp(1)."))
    A.emit("eval_doi_10.3390_mca27040068.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
