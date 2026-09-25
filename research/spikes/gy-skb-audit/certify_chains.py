"""Sturm-certify the two-step different-structure chain counterexamples."""
import sympy as sp
from audit_mphr import R, y, in_Vn, gy_Cker, skb_Aker, skb_Bker


def show(name, d, wits):
    dd = sp.cancel(sp.together(d))
    num, den = sp.fraction(dd)
    num, den = sp.expand(num), sp.expand(den)
    P = sp.Poly(num, y)
    nr = P.count_roots(0, 1)
    dnr = sp.Poly(den, y).count_roots(0, 1) if den.has(y) else 0
    g = sp.gcd(num, den)
    print(f"=== {name} ===")
    print(f"  num degree {sp.degree(P)}; Sturm roots (0,1): {nr}; den roots: {dnr}; gcd={g}")
    for v in wits:
        val = sp.cancel(dd.subs(y, v))
        print(f"  witness y={v}: {val}  sign={sp.sign(val)}")
    print(f"  numerator: {num}")
    print(f"  denominator: {den}", flush=True)


# ---- SKB Thm 9 (== Thm 24): two-step chain, intermediates in V_3, a=-2
p = [R(5, 17), R(2, 17), R(10, 17)]
th = [R(1, 3), R(7), R(1, 4)]
assert in_Vn(p, th)
w1, w2 = R(19, 20), R(11, 20)
p1 = [R(21, 68), R(2, 17), R(39, 68)]
th1 = [R(79, 240), R(7), R(61, 240)]
p2 = [R(303, 1360), R(277, 1360), R(39, 68)]
th2 = [R(15989, 4800), R(6397, 1600), R(61, 240)]
# verify chain algebra
assert p1[0] == w1 * p[0] + (1 - w1) * p[2] and p1[2] == w1 * p[2] + (1 - w1) * p[0]
assert th1[0] == w1 * th[0] + (1 - w1) * th[2] and th1[2] == w1 * th[2] + (1 - w1) * th[0]
assert p2[0] == w2 * p1[0] + (1 - w2) * p1[1] and p2[1] == w2 * p1[1] + (1 - w2) * p1[0]
assert th2[0] == w2 * th1[0] + (1 - w2) * th1[1] and th2[1] == w2 * th1[1] + (1 - w2) * th1[0]
assert in_Vn(p1, th1)  # intermediate stays in V_3
d9 = skb_Aker(p, th, -2) - skb_Aker(p2, th2, -2)
show("SKB Thm9/24 (2-step)", d9, [R(1, 16), R(1, 8), R(1, 100)])

# ---- SKB Thm 12 (== Thm 21): two-step chain, a=2
p = [R(3, 34), R(7, 17), R(1, 2)]
th = [R(9), R(5, 4), R(1)]
assert in_Vn(p, th)
w1, w2 = R(19, 20), R(9, 20)
p1 = [R(3, 34), R(283, 680), R(337, 680)]
th1 = [R(9), R(99, 80), R(81, 80)]
p2 = [R(3653, 13600), R(3207, 13600), R(337, 680)]
th2 = [R(7569, 1600), R(8811, 1600), R(81, 80)]
assert p1[1] == w1 * p[1] + (1 - w1) * p[2] and p1[2] == w1 * p[2] + (1 - w1) * p[1]
assert th1[1] == w1 * th[1] + (1 - w1) * th[2] and th1[2] == w1 * th[2] + (1 - w1) * th[1]
assert p2[0] == w2 * p1[0] + (1 - w2) * p1[1] and p2[1] == w2 * p1[1] + (1 - w2) * p1[0]
assert th2[0] == w2 * th1[0] + (1 - w2) * th1[1] and th2[1] == w2 * th1[1] + (1 - w2) * th1[0]
assert in_Vn(p1, th1)
d12 = skb_Bker(p, th, 2) - skb_Bker(p2, th2, 2)
show("SKB Thm12/21 (2-step)", d12, [R(1, 2), R(3, 4)])

# ---- GY Cor 6: two-step chain intermediates in K_3 (=V_3), equal-products
p = [R(6, 13), R(4, 13), R(3, 13)]
a = [R(1, 2), R(3, 4), R(1)]
assert len({pi * ai for pi, ai in zip(p, a)}) == 1
assert in_Vn(p, a)
w1, w2 = R(3, 10), R(2, 5)
p1 = [R(6, 13), R(33, 130), R(37, 130)]
a1 = [R(1, 2), R(37, 40), R(33, 40)]
p2 = [R(219, 650), R(123, 325), R(37, 130)]
a2 = [R(151, 200), R(67, 100), R(33, 40)]
assert p1[1] == w1 * p[1] + (1 - w1) * p[2] and p1[2] == w1 * p[2] + (1 - w1) * p[1]
assert a1[1] == w1 * a[1] + (1 - w1) * a[2] and a1[2] == w1 * a[2] + (1 - w1) * a[1]
assert p2[0] == w2 * p1[0] + (1 - w2) * p1[1] and p2[1] == w2 * p1[1] + (1 - w2) * p1[0]
assert a2[0] == w2 * a1[0] + (1 - w2) * a1[1] and a2[1] == w2 * a1[1] + (1 - w2) * a1[0]
assert in_Vn(p1, a1)  # intermediate in K_3
d6 = gy_Cker(p, a) - gy_Cker(p2, a2)
show("GY Cor6 (2-step)", d6, [R(1, 100), R(1, 4)])
