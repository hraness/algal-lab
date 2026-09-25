"""EXACT CERTIFICATION: counterexamples to the W_n / alpha<=0 halves of
SKF2026 Theorems 3.8 and 3.11 (halves untouched by the existing manuscript).

Thm 3.8 (Wn, a<=0): [p;gam] in W3, [q;del]=[p;gam]M_T  =>  U <=hr V,
i.e. h_U >= h_V for all t.  With exp baseline and theta=1:
h_U(t) = htilde_{p,gam}(e^{-alpha t}) with alpha=-2 -> y=e^{2t} in (1,oo);
equivalently in s=e^{-t}: htilde = sum p_i g_i s^{-2 g_i}/sum p_i s^{-2 g_i}.

Instance (n=3):
  p = (17/44, 5/11, 7/44),  gam = (7, 9, 2)   -> comonotone: in W3
  T-transform on coordinates (1,3) with omega = 17/20:
  q = (31/88, 5/11, 17/88),  del = (25/4, 9, 11/4)
  alpha = -2.
Check: h_U(t) - h_V(t) changes sign: negative for s<=3/4, positive at 7/8.
"""
import sympy as sp
from audit_lib import R, in_Wn, weak_super

s = sp.Symbol("s", positive=True)

p = (R(17, 44), R(5, 11), R(7, 44))
gam = (R(7), R(9), R(2))
q = (R(31, 88), R(5, 11), R(17, 88))
dele = (R(25, 4), R(9), R(11, 4))
alpha = R(-2)

# ---- hypothesis checks ----
print("sum p =", sum(p), " sum q =", sum(q))
print("[p;gam] in W3:", in_Wn(list(p), list(gam)))
om = R(17, 20)
# verify [q;del] = [p;gam] T on coordinates 1,3 (0-indexed 0,2):
print("q1 = om*p1+(1-om)*p3:", om * p[0] + (1 - om) * p[2], "vs", q[0])
print("q3 = (1-om)p1+om p3:", (1 - om) * p[0] + om * p[2], "vs", q[2])
print("d1 = om*g1+(1-om)g3:", om * gam[0] + (1 - om) * gam[2], "vs", dele[0])
print("d3 = (1-om)g1+om g3:", (1 - om) * gam[0] + om * gam[2], "vs", dele[2])

# ---- hazard difference ----
def htilde(pp, gg):
    num = sum(pp[i] * gg[i] * s ** sp.nsimplify(alpha * gg[i]) for i in range(3))
    den = sum(pp[i] * s ** sp.nsimplify(alpha * gg[i]) for i in range(3))
    return sp.cancel(num / den)

d = sp.cancel(sp.together(htilde(p, gam) - htilde(q, dele)))
num, den = sp.fraction(d)
print("\nh_U - h_V numerator:", sp.expand(num))
print("denominator:", sp.expand(den))
# substitute s = w^2 to clear half-powers
w = sp.Symbol("w", positive=True)
numw = sp.Poly(sp.expand(num.subs(s, w ** 2)), w)
denw = sp.Poly(sp.expand(den.subs(s, w ** 2)), w)
print("roots of num in (0,1):", numw.count_roots(0, 1))
print("root intervals:", numw.intervals())
print("roots of den in (0,1):", denw.count_roots(0, 1))
for v in (R(1, 4), R(1, 2), R(3, 4), R(13, 16), R(7, 8), R(15, 16), R(31, 32)):
    print(f"  d({v}) = {d.subs(s, v)} = {float(d.subs(s, v)):.4f}")
