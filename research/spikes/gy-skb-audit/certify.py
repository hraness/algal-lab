"""Sturm-certified counterexamples.

GY Thm 6 (n=3) and SKB Thm 8 (n=3, a=-4) / Thm 11 (n=3, a=1).
Also SKB Thm 9/12/21/24 different-structure chains if a 2-step instance exists.
"""
import sympy as sp
from audit_mphr import (R, y, in_Vn, gy_Cker, skb_Aker, skb_Bker,
                        certify)

def show(name, d, wit_lo, wit_hi):
    num, den = sp.fraction(sp.cancel(sp.together(d)))
    num, den = sp.expand(num), sp.expand(den)
    P = sp.Poly(num, y)
    D = sp.Poly(den, y) if den.has(y) else None
    nr = P.count_roots(0, 1)
    dnr = D.count_roots(0, 1) if D else 0
    print(f"=== {name} ===")
    print(f"  numerator degree {sp.degree(P)}, Sturm roots in (0,1): {nr}")
    print(f"  denominator roots in (0,1): {dnr}")
    for v, tag in [(wit_lo, "lo"), (wit_hi, "hi")]:
        val = sp.cancel(d.subs(y, v))
        print(f"  witness y={v}: value = {val}  sign={sp.sign(val)}")
    print(f"  numerator: {num}")
    print(f"  denominator: {den}")
    print(flush=True)


# ---- GY2024 Thm 6 counterexample (n=3, single T)
p = [R(16, 37), R(9, 37), R(12, 37)]
a = [R(1, 2), R(8, 9), R(2, 3)]
# verify equal products
prods = [pi * ai for pi, ai in zip(p, a)]
assert len(set(prods)) == 1, prods
q = [R(15, 37), R(9, 37), R(13, 37)]
b = [R(13, 24), R(8, 9), R(5, 8)]
# verify T-transform: on coords (0,2), w=3/4
w = R(3, 4)
assert q[0] == w * p[0] + (1 - w) * p[2] and q[2] == w * p[2] + (1 - w) * p[0]
assert b[0] == w * a[0] + (1 - w) * a[2] and b[2] == w * a[2] + (1 - w) * a[0]
assert in_Vn(p, a)  # K_n == V_n
d_gy = gy_Cker(p, a) - gy_Cker(q, b)
show("GY2024 Thm6", d_gy, R(1, 16), R(1, 5))

# ---- SKB2026 Thm 8 counterexample (n=3, a=-4, single T on (1,2) w=9/10)
p2 = [R(7, 16), R(1, 4), R(5, 16)]
th2 = [R(9, 4), R(9), R(3)]
assert in_Vn(p2, th2)
q2 = [R(7, 16), R(41, 160), R(49, 160)]
gm2 = [R(9, 4), R(42, 5), R(18, 5)]
w2 = R(9, 10)
assert q2[1] == w2 * p2[1] + (1 - w2) * p2[2] and q2[2] == w2 * p2[2] + (1 - w2) * p2[1]
assert gm2[1] == w2 * th2[1] + (1 - w2) * th2[2] and gm2[2] == w2 * th2[2] + (1 - w2) * th2[1]
d8 = skb_Aker(p2, th2, -4) - skb_Aker(q2, gm2, -4)
show("SKB2026 Thm8 (==Thm23)", d8, R(1, 100), R(1, 4))

# ---- SKB2026 Thm 11 counterexample (n=3, a=1, single T on (0,1) w=3/10)
p3 = [R(3, 11), R(13, 44), R(19, 44)]
th3 = [R(5), R(3, 2), R(1, 4)]
assert in_Vn(p3, th3)
q3 = [R(127, 440), R(123, 440), R(19, 44)]
gm3 = [R(51, 20), R(79, 20), R(1, 4)]
w3 = R(3, 10)
assert q3[0] == w3 * p3[0] + (1 - w3) * p3[1] and q3[1] == w3 * p3[1] + (1 - w3) * p3[0]
assert gm3[0] == w3 * th3[0] + (1 - w3) * th3[1] and gm3[1] == w3 * th3[1] + (1 - w3) * th3[0]
d11 = skb_Bker(p3, th3, 1) - skb_Bker(q3, gm3, 1)
show("SKB2026 Thm11 (==Thm20)", d11, R(1, 2), R(3, 5))
