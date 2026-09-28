"""Evaluator for doi:10.21307/stattrans-2018-004 (generalized Zeghdoudi GZD).

Theorem 4: X_i ~ GZD(theta_i), theta1 >= theta2 => X1 <lr X2, <hr, <s(st), <=cx.
The family density is f(x;theta) = (sum a_k x^k) e^{-theta x} /
                                  (sum a_k k! theta^{-(k+1)}).
Instance: the Lindley member a = (1, 1): f = theta^2 (1+x) e^{-theta x}/(theta+1).
Survival of Lindley(theta): e^{-theta x} (1 + theta x/(theta+1)).
"""
import json
import auditlib as A
import sympy as sp

x = A.x
E = A.e


def gzd_surv(theta, a):
    """S(x;theta) for GZD with coefficient vector a (a_k multiplies x^k)."""
    num = 0
    den = 0
    for k, ak in enumerate(a):
        ak = A.R(ak)
        den += ak * sp.factorial(k) / theta ** (k + 1)
        inner = sum((theta * x) ** j / sp.factorial(j) for j in range(k + 1))
        num += ak * sp.factorial(k) / theta ** (k + 1) * inner
    return E ** (-theta * x) * num / den


def test(order, theta1, theta2, a):
    X = A.C(gzd_surv(A.R(theta1), a))
    Y = A.C(gzd_surv(A.R(theta2), a))
    return A.check_dist(order, X, Y)


def main():
    claims = json.load(open("../canonical/doi_10.21307_stattrans-2018-004.json"))
    out = []
    a = [1, 1]                      # Lindley sub-model (a_0 = a_1 = 1)
    pairs = [(2, 1), (3, A.R(1, 2)), (A.R(3, 2), 1)]
    for recd in claims:
        order = recd["conclusion"]["order"]
        if order == "lr":
            n = und = 0
            wit = None
            for t1, t2 in pairs:
                h, w, u = test("lr", t1, t2, a)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            out.append(A.rec(recd, "holds" if wit is None else "refuted", order="lr",
                             instances=n, witness=str(wit) if wit else None,
                             undecided=und, note="Lindley member a=(1,1)."))
        elif order == "hr":
            n = und = 0
            wit = None
            for t1, t2 in pairs:
                h, w, u = test("hr", t1, t2, a)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            out.append(A.rec(recd, "holds" if wit is None else "refuted", order="hr",
                             instances=n, witness=str(wit) if wit else None,
                             undecided=und, note="Lindley member a=(1,1)."))
        elif order == "st":
            n = und = 0
            wit = None
            for t1, t2 in pairs:
                h, w, u = test("st", t1, t2, a)
                n += 1
                und += u
                if not h and wit is None:
                    wit = w
            out.append(A.rec(recd, "holds" if wit is None else "refuted", order="st",
                             instances=n, witness=str(wit) if wit else None,
                             undecided=und, note="Lindley member a=(1,1)."))
        else:
            out.append(A.rec(recd, "unsupported order"))
    A.emit("eval_doi_10.21307_stattrans-2018-004.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
