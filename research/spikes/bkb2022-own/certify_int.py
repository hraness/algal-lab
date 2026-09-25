"""Exact certification of integer-rate counterexamples (tiny polynomials).

All rates nu_i are positive integers -> z = s (L=1), polynomials are small,
Sturm counts fast.  Matrices [nu; p] (rate row) with B = A T^{ij}_{1/2}.
Both A and B verified in the claimed class exactly.
"""
import sys
import sympy as sp

sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/mixture-audit")
from audit_lib import in_Vn, in_Wn

s = sp.Symbol("s", positive=True)


def cls_tag(row, p):
    return "V" if in_Vn(row, p) else ("W" if in_Wn(row, p) else "-")


def certify(order, nu, p, nuB, pB, cols, label):
    print(f"--- {label}")
    print(f"  A : nu={[int(x) for x in nu]} p={[str(x) for x in p]} -> "
          f"{cls_tag(nu, p)}")
    print(f"  B : nu={[int(x) for x in nuB]} p={[str(x) for x in pB]} -> "
          f"{cls_tag(nuB, pB)}   (omega=1/2 on cols {cols})")
    Na = sum(pi * vi * s ** vi for pi, vi in zip(p, nu))
    Nb = sum(pi * vi * s ** vi for pi, vi in zip(pB, nuB))
    Da = sum(pi * s ** vi for pi, vi in zip(p, nu))
    Db = sum(pi * s ** vi for pi, vi in zip(pB, nuB))
    if order == "rh":
        Da = 1 - Da
        Db = 1 - Db
    num = sp.Poly(sp.expand(Na * Db - Nb * Da), s)
    print(f"  numerator (deg {num.degree()}): {num.as_expr()}")
    nroots = num.count_roots(0, 1)
    print(f"  Sturm roots in (0,1): {nroots}")
    # exact rational witnesses at every grid k/16 + fine tail
    grid = [sp.Rational(k, 16) for k in range(1, 16)] + \
           [sp.Rational(k, 256) for k in range(224, 256, 4)]
    vals = [(q, sp.sign(num.as_expr().subs(s, q))) for q in grid]
    line = [(str(q), int(sv)) for q, sv in vals]
    print("  signs:", line)
    neg = [q for q, sv in vals if sv < 0]
    pos = [q for q, sv in vals if sv > 0]
    if neg and pos:
        v1 = num.as_expr().subs(s, neg[0])
        v2 = num.as_expr().subs(s, pos[0])
        print(f"  CERTIFIED CROSSING: num({neg[0]}) = {v1} < 0 ; "
              f"num({pos[0]}) = {v2} > 0")
        print(f"  => rate_A - rate_B takes both signs in (0,1): "
              f"the ordering fails in BOTH directions.")


if __name__ == "__main__":
    H = sp.Rational
    certify("rh", [1, 15, 3], [H(33, 40), H(1, 20), H(1, 8)],
            [2, 15, 2], [H(19, 40), H(1, 20), H(19, 40)], (0, 2),
            "rh V_3 antiordered, exp baseline")
    certify("rh", [10, 16, 2], [H(9, 40), H(27, 40), H(1, 10)],
            [13, 13, 2], [H(9, 20), H(9, 20), H(1, 10)], (0, 1),
            "rh W_3 comonotone, exp baseline")
    certify("hr", [13, 15, 11], [H(3, 20), H(1, 20), H(4, 5)],
            [14, 14, 11], [H(1, 10), H(1, 10), H(4, 5)], (0, 1),
            "hr V_3 antiordered, exp baseline")
    certify("hr", [9, 1, 12], [H(17, 40), H(1, 20), H(21, 40)],
            [5, 5, 12], [H(19, 80), H(19, 80), H(21, 40)], (0, 1),
            "hr W_3 comonotone, exp baseline")
    # n=2 probes (integer rates, omega=1/2)
    certify("rh", [1, 6], [H(1, 4), H(3, 4)],
            [4, 3], [H(3, 8), H(5, 8)], (0, 1),
            "rh V_2? probe")
    certify("hr", [1, 15, 3], [H(33, 40), H(1, 20), H(1, 8)],
            [2, 15, 2], [H(19, 40), H(1, 20), H(19, 40)], (0, 2),
            "hr same-as-C1 instance for contrast")
