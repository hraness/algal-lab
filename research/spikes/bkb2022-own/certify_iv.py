"""Interval-certified crossings for the scale-row (convention S) instances.

mpmath.iv outward-rounded arithmetic: a negative/positive interval is a
rigorous sign certificate.  Continuity of the rate difference on (0,1) gives
IVT crossings; denominators positive analytically.
"""
import sys
import sympy as sp
from mpmath import iv

sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/mixture-audit")
from audit_lib import in_Vn, in_Wn


def ivq(x):
    return iv.mpf(int(x.p)) / iv.mpf(int(x.q))


def rate_iv(order, nu, p, s):
    siv = ivq(s)
    N = sum(ivq(pi) * ivq(vi) * siv ** ivq(vi) for pi, vi in zip(p, nu))
    D = sum(ivq(pi) * siv ** ivq(vi) for pi, vi in zip(p, nu))
    if order == "rh":
        D = 1 - D
    return N / D


def cls_tag(row, p):
    return "V" if in_Vn(row, p) else ("W" if in_Wn(row, p) else "-")


def run(order, nu, p, nuB, pB, om, cols, label):
    lam = [1 / x for x in nu]
    lamB = [1 / x for x in nuB]
    print(f"--- {label}")
    print(f"  A : lam={[str(x) for x in lam]} p={[str(x) for x in p]} "
          f"-> {cls_tag(lam, p)}")
    print(f"  B : lam={[str(x) for x in lamB]} p={[str(x) for x in pB]} "
          f"-> {cls_tag(lamB, pB)}")
    ks = list(range(2, 128))
    ds = [rate_iv(order, nu, p, sp.Rational(k, 128)) -
          rate_iv(order, nuB, pB, sp.Rational(k, 128)) for k in ks]
    pat = "".join("-" if d < 0 else ("+" if d > 0 else "?") for d in ds)
    negs = [(k, d) for k, d in zip(ks, ds) if d < 0]
    poss = [(k, d) for k, d in zip(ks, ds) if d > 0]
    print(f"  sign pattern (s=k/128): {pat}")
    if negs and poss:
        print(f"  CERTIFIED CROSSING: d({negs[0][0]}/128) in "
              f"[{negs[0][1].a},{negs[0][1].b}] <0 ; "
              f"d({poss[0][0]}/128) in [{poss[0][1].a},{poss[0][1].b}] >0")
    elif negs or poss:
        which = negs or poss
        print(f"  one-sided violation: d({which[0][0]}/128) in "
              f"[{which[0][1].a},{which[0][1].b}]")


H = sp.Rational
run("rh", [H(13, 4), H(7, 6), H(23, 5)],
    [H(13, 40), H(9, 40), H(9, 20)],
    [H(182, 141), H(182, 71), H(23, 5)],
    [H(6, 25), H(31, 100), H(9, 20)], H(3, 20), (0, 1),
    "C3 rh n=3, scale row [lam;p], V_3")
run("rh", [H(10), H(4), H(15, 4)],
    [H(9, 40), H(1, 4), H(21, 40)],
    [H(400, 61), H(400, 79), H(15, 4)],
    [H(187, 800), H(193, 800), H(21, 40)], H(13, 20), (0, 1),
    "C4 rh n=3, scale row [lam;p], W_3")
run("hr", [H(1, 4), H(10), H(4, 3)],
    [H(3, 40), H(1, 2), H(17, 40)],
    [H(80, 73), H(10), H(80, 307)],
    [H(163, 400), H(1, 2), H(37, 400)], H(1, 20), (0, 2),
    "C5 hr n=3, scale row [lam;p], V_3")
run("hr", [H(6, 5), H(2), H(1, 2)],
    [H(9, 40), H(7, 40), H(3, 5)],
    [H(5, 3), H(15, 11), H(1, 2)],
    [H(19, 100), H(21, 100), H(3, 5)], H(3, 10), (0, 1),
    "C6 hr n=3, scale row [lam;p], W_3")
