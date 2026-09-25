"""Certified counterexamples to BKB2022-style n>=3 rate orderings.

Model: ordinary scale mixtures F_i(t) = F((t-sigma)/lam_i), common location.
Exponential baseline F=1-e^{-t}, rates nu_i=1/lam_i, s=e^{-t} in (0,1):
    rh: r(s) = sum p_i nu_i s^{nu_i} / (1 - sum p_i s^{nu_i})
    hr: h(s) = sum p_i nu_i s^{nu_i} /      sum p_i s^{nu_i}
(Inverted-exponential baseline F=e^{-1/t} gives t^2 r(t) = the hr ratio with
s=e^{-1/t}; its t^2 f is increasing -- a second admissible baseline flavour.)

Two certification devices, both exact:
  (a) Sturm root count on the numerator in z = s^{1/L} (integer-exponent
      polynomial), plus exact rational witnesses -- used when L is small
      (convention R: parameter row = rates).
  (b) Certified interval evaluation (mpmath.iv, outward-rounded) of the rate
      difference at rational s -- rigorous sign bounds for convention S
      (parameter row = scales, rates 1/lam have large denominators).
Denominator positivity on (0,1) is analytic: hr denom is a positive sum;
rh denom 1 - sum p_i s^{nu_i} > 0 because sum p_i = 1 and s^{nu_i} < 1.
"""
import sys
from math import lcm
import sympy as sp
from mpmath import iv

sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/mixture-audit")
from audit_lib import in_Vn, in_Wn

z = sp.Symbol("z", positive=True)
STURM_MAX_DEG = 8000


def cls_tag(row, p):
    if in_Vn(row, p):
        return "V"
    if in_Wn(row, p):
        return "W"
    return "-"


def ivq(x):
    """exact rational -> interval mpf (sympy Rational or Fraction)."""
    try:
        num, den = int(x.p), int(x.q)
    except AttributeError:
        num, den = int(x.numerator), int(x.denominator)
    return iv.mpf(num) / iv.mpf(den)


def rate_iv(order, nu, p, s):
    siv = ivq(s) if not hasattr(s, "a") else s
    N = sum(ivq(pi) * ivq(vi) * siv ** ivq(vi) for pi, vi in zip(p, nu))
    D = sum(ivq(pi) * siv ** ivq(vi) for pi, vi in zip(p, nu))
    if order == "rh":
        D = 1 - D
    return N / D


def certify(order, conv, nu, p, nuB, pB, om, cols, label, do_sturm=True):
    lam = [1 / x for x in nu]
    lamB = [1 / x for x in nuB]
    rowA = lam if conv == "S" else nu
    rowB = lamB if conv == "S" else nuB
    cA, cB = cls_tag(rowA, p), cls_tag(rowB, pB)
    print(f"--- {label}")
    print(f"  conv={conv} order={order} omega={om} cols={cols}")
    print(f"  A : row={[str(x) for x in rowA]} p={[str(x) for x in p]} -> {cA}")
    print(f"  B : row={[str(x) for x in rowB]} p={[str(x) for x in pB]} -> {cB}")
    assert cA == cB != "-", "matrices not in the same admissible class"

    # ---- device (b): certified interval witnesses on s grid ---------------
    ks = list(range(2, 63, 2))
    ds = [rate_iv(order, nu, p, sp.Rational(k, 64)) -
          rate_iv(order, nuB, pB, sp.Rational(k, 64)) for k in ks]
    negs = [(k, d) for k, d in zip(ks, ds) if d < 0]
    poss = [(k, d) for k, d in zip(ks, ds) if d > 0]
    print("  interval signs:", "".join("-" if d < 0 else ("+" if d > 0 else "?")
                                        for d in ds))
    if negs and poss:
        print(f"  CERTIFIED CROSSING (interval arithmetic): "
              f"d({negs[0][0]}/64) in {negs[0][1]} <0 ; d({poss[0][0]}/64) in "
              f"{poss[0][1]} >0")
    elif negs or poss:
        print("  one-direction violation only:",
              "neg" if negs else "pos",
              f"d({(negs or poss)[0][0]}/64) in {(negs or poss)[0][1]}")
    else:
        print("  no violation detected on this grid")
        return

    # ---- device (a): exact symbolic numerator + optional Sturm ------------
    L = 1
    for v in (nu, nuB):
        for x in v:
            L = lcm(L, sp.Rational(x).q)
    exA = [int(sp.Rational(vi) * L) for vi in nu]
    exB = [int(sp.Rational(vi) * L) for vi in nuB]
    deg = max(exA + exB)
    print(f"  L={L} max exponent={deg}")
    if deg > STURM_MAX_DEG:
        print("  (degree too large for fast Sturm -- interval certificate stands)")
        return
    Na = sum(pi * vi * z ** e for pi, vi, e in zip(p, nu, exA))
    Nb = sum(pi * vi * z ** e for pi, vi, e in zip(pB, nuB, exB))
    Da = sum(pi * z ** e for pi, e in zip(p, exA))
    Db = sum(pi * z ** e for pi, e in zip(pB, exB))
    if order == "rh":
        Da = 1 - Da
        Db = 1 - Db
    num = sp.Poly(sp.expand(Na * Db - Nb * Da), z)
    # exact rational witnesses on a z-grid (z = s^{1/L} monotone in s);
    # include a fine tail window since s-level crossings map near z -> 1
    zg = [sp.Rational(k, 64) for k in range(2, 63, 2)] + \
         [sp.Rational(m, 8192) for m in range(7900, 8192, 8)]
    zvals = [(q, sp.sign(num.as_expr().subs(z, q))) for q in zg]
    print("  exact num signs (z=k/64, then fine tail):",
          "".join("-" if sv < 0 else ("+" if sv > 0 else "0")
                  for _, sv in zvals))
    e_neg = [q for q, sv in zvals if sv < 0]
    e_pos = [q for q, sv in zvals if sv > 0]
    if e_neg and e_pos:
        print(f"  exact witnesses: num({e_neg[0]})<0, num({e_pos[0]})>0")
    if do_sturm:
        nroots = num.count_roots(0, 1)
        print(f"  Sturm: roots of numerator in (0,1) = {nroots}")


if __name__ == "__main__":
    H = sp.Rational
    cases = [
        ("rh", "R",
         [H(7, 4), H(6), H(7, 6)], [H(13, 40), H(1, 2), H(7, 40)],
         [H(329, 240), H(6), H(371, 240)],
         [H(91, 400), H(1, 2), H(109, 400)], H(7, 20), (0, 2),
         "C1 rh n=3, row=[nu;p], W_3 comonotone"),
        ("rh", "R",
         [H(7), H(14, 5), H(8)], [H(1, 4), H(21, 40), H(9, 40)],
         [H(637, 100), H(343, 100), H(8)],
         [H(233, 800), H(387, 800), H(9, 40)], H(17, 20), (0, 1),
         "C2 rh n=3, row=[nu;p], V_3 antiordered"),
        ("rh", "S",
         [H(13, 4), H(7, 6), H(23, 5)],
         [H(13, 40), H(9, 40), H(9, 20)],
         [H(182, 141), H(182, 71), H(23, 5)],
         [H(6, 25), H(31, 100), H(9, 20)], H(3, 20), (0, 1),
         "C3 rh n=3, row=[lam;p] scales, V_3"),
        ("rh", "S",
         [H(10), H(4), H(15, 4)],
         [H(9, 40), H(1, 4), H(21, 40)],
         [H(400, 61), H(400, 79), H(15, 4)],
         [H(187, 800), H(193, 800), H(21, 40)], H(13, 20), (0, 1),
         "C4 rh n=3, row=[lam;p] scales, W_3"),
        ("hr", "S",
         [H(1, 4), H(10), H(4, 3)],
         [H(3, 40), H(1, 2), H(17, 40)],
         [H(80, 73), H(10), H(80, 307)],
         [H(163, 400), H(1, 2), H(37, 400)], H(1, 20), (0, 2),
         "C5 hr n=3, row=[lam;p] scales, V_3"),
        ("hr", "S",
         [H(6, 5), H(2), H(1, 2)],
         [H(9, 40), H(7, 40), H(3, 5)],
         [H(5, 3), H(15, 11), H(1, 2)],
         [H(19, 100), H(21, 100), H(3, 5)], H(3, 10), (0, 1),
         "C6 hr n=3, row=[lam;p] scales, W_3"),
        ("rh", "R",
         [H(12, 5), H(1, 2)], [H(1, 4), H(3, 4)],
         [H(29, 20), H(29, 20)], [H(1, 2), H(1, 2)], H(1, 2), (0, 1),
         "C7 rh n=2, row=[nu;p], V_2 (base-case probe)"),
        ("rh", "R",
         [H(17, 3), H(4)], [H(19, 20), H(1, 20)],
         [H(21, 4), H(53, 12)], [H(29, 40), H(11, 40)], H(3, 4), (0, 1),
         "C8 rh n=2, row=[nu;p], W_2 (base-case probe)"),
    ]
    for order, conv, nu, p, nuB, pB, om, cols, label in cases:
        certify(order, conv, nu, p, nuB, pB, om, cols, label)
