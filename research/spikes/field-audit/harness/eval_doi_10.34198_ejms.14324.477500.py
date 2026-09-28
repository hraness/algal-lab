"""Evaluator for doi:10.34198/ejms.14324.477500 (Double XRama distribution).

Claim: Theorem 3.1 -- X ~ DXR(theta1), Y ~ DXR(theta2), theta1 >= theta2
       => X <=lr Y (paper also prints hr/mrl/st implications; canonical order lr).

S(x; theta) = e^{-theta x} (1 + 36 (theta^3 x^3 + 3 theta^2 x^2 + 6 theta x)/(theta^3+6)^3)
derived from integrating the printed pdf; normalizes to S(0)=1.
"""
import json
import auditlib as A
import sympy as sp

x = A.x
E = A.e


def dxr(theta):
    return A.C(A.doublexrama_surv(theta))


def test(theta1, theta2):
    return A.check_dist("lr", dxr(theta1), dxr(theta2))


def main():
    claims = json.load(open("../canonical/doi_10.34198_ejms.14324.477500.json"))
    out = []
    n = und = 0
    wit = None
    for t1, t2 in [(A.R(2), A.R(1)), (A.R(3), A.R(1, 2)), (A.R(5), A.R(2)),
                   (A.R(1), A.R(1, 3))]:
        h, w, u = test(t1, t2)
        n += 1
        und += u
        if not h and wit is None:
            wit = w
    recd = claims[0]
    status = "holds" if wit is None else "refuted"
    out.append(A.rec(recd, status, instances=n, witness=str(wit) if wit else None,
                     undecided=und,
                     note=("theta1 > theta2 instances; the proof's printed hypothesis "
                           "direction differs from the statement's, but the statement "
                           "is used here.")))
    A.emit("eval_doi_10.34198_ejms.14324.477500.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
