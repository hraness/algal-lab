"""Evaluator for doi:10.6339/jds.202001(18)1.0001 (generalized inverse Weibull GIW).

Section 4.7: Case I theta1<theta2 => X <=lr Y (+hr/st/rhr by implication);
             Case II alpha2<alpha1 => X <=lr Y (same chain).
GIW cdf (18): G(y) = a^t (1 - v^t) / ((1 - a^t) v^t), v = 1-(1-a)e^{-(lam/y)^b}.
"""
import json
import auditlib as A
import sympy as sp

x = A.x


def giw(params):
    return A.C(1 - A.giw_cdf(params["a"], params["th"], params["lam"], params["b"]))


def run(order, paramsX, paramsY):
    return A.check_dist(order, giw(paramsX), giw(paramsY))


def main():
    claims = json.load(open("../canonical/doi_10.6339_jds.202001_18_1_.0001.json"))
    out = []
    # Case I: common a, lam, b; theta1 < theta2.
    I = [(dict(a=A.R(1, 2), th=A.R(1), lam=A.R(1), b=A.R(1)),
          dict(a=A.R(1, 2), th=A.R(2), lam=A.R(1), b=A.R(1))),
         (dict(a=A.R(1, 3), th=A.R(1), lam=A.R(2), b=A.R(1)),
          dict(a=A.R(1, 3), th=A.R(3), lam=A.R(2), b=A.R(1))),
         (dict(a=A.R(2), th=A.R(1), lam=A.R(1), b=A.R(1)),
          dict(a=A.R(2), th=A.R(2), lam=A.R(1), b=A.R(1)))]
    # Case II: common th, lam, b; alpha2 < alpha1 (X has bigger alpha).
    II = [(dict(a=A.R(2), th=A.R(1), lam=A.R(1), b=A.R(1)),
           dict(a=A.R(1, 2), th=A.R(1), lam=A.R(1), b=A.R(1))),
          (dict(a=A.R(3), th=A.R(2), lam=A.R(1), b=A.R(2)),
           dict(a=A.R(1, 2), th=A.R(2), lam=A.R(1), b=A.R(2))),
          (dict(a=A.R(4), th=A.R(1), lam=A.R(2), b=A.R(1)),
           dict(a=A.R(2), th=A.R(1), lam=A.R(2), b=A.R(1)))]
    for recd in claims:
        order = recd["conclusion"]["order"]
        insts = II if "Case II" in recd["claim"] else I
        n = und = 0
        wit = None
        for px, py in insts:
            h, w, u = run(order, px, py)
            n += 1
            und += u
            if not h and wit is None:
                wit = w
        note = None
        if wit is not None and "Case I" not in recd["claim"]:
            pass
        elif wit is not None:
            note = ("refuted within the printed hypotheses: the paper does not "
                    "restrict alpha and itself plots alpha=1.5; for alpha>1 the "
                    "theta-ordering reverses (c3_giw_case1.py)")
        out.append(A.rec(recd, "holds" if wit is None else "refuted",
                         instances=n, witness=str(wit) if wit else None,
                         undecided=und, note=note))
    A.emit("eval_doi_10.6339_jds.202001_18_1_.0001.result.json", out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
