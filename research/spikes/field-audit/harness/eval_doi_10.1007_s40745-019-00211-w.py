"""Evaluator for doi:10.1007/s40745-019-00211-w (inverse xgamma IXGD).

Unnumbered Section 3.4 theorem: theta1 > theta2 => X <=lr Y (and other orders
via the implication chain).  IXGD survival:
S(x) = 1 - (1 + theta/((1+theta)x) + theta/(2(1+theta)x^2)) e^{-theta/x}.
"""
import json
import auditlib as A

x = A.x


def test(order, t1, t2):
    X = A.C(A.ixgd_surv(A.R(t1)))
    Y = A.C(A.ixgd_surv(A.R(t2)))
    return A.check_dist(order, X, Y)


def main():
    claims = json.load(open("../canonical/doi_10.1007_s40745-019-00211-w.json"))
    out = []
    pairs = [(A.R(2), A.R(1)), (A.R(3), A.R(1, 2)), (A.R(5), A.R(2))]
    for recd in claims:
        order = recd["conclusion"]["order"]
        if order not in ("st", "hr", "rh", "lr"):
            out.append(A.rec(recd, "unsupported order"))
            continue
        n = und = 0
        wits = []
        for t1, t2 in pairs:
            h, w, u = test(order, t1, t2)
            n += 1
            und += u
            if not h:
                wits.append(w)
        wit = max(wits) if wits else None
        out.append(A.rec(recd, "holds" if wit is None else "refuted",
                         instances=n, witness=str(wit) if wit is not None else None,
                         undecided=und,
                         note=("theta1 > theta2 instances. The printed direction is "
                               "wrong: the IXGD family is lr-INCREASING in theta "
                               "(X >=lr Y strictly; see c3_ixgd_lr.py).")))
    A.emit("eval_doi_10.1007_s40745-019-00211-w.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
