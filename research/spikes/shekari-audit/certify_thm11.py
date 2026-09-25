"""Sturm certificate for Thm 11(i) counterexample under PHR D(u;g)=u^g.

Instance (n=3, A_3):
    A = [g; p] = [[2, 4, 3], [7/12, 1/12, 1/3]]
    T on columns (2,3) [1-indexed], omega = 3/10:
    B = A T = [[2, 33/10, 37/10], [7/12, 31/120, 19/120]]
Claim (i): htilde_A(u) <= htilde_B(u) on (0,1)  [P_3 >=_hr Q_3].
In z = u^{1/10} the difference is a rational function of z on (0,1).
"""
import sympy as sp
from sympy import Rational as R

z = sp.Symbol("z", positive=True)   # u = z^10, z in (0,1)

gam = (R(2), R(4), R(3))
p = (R(7, 12), R(1, 12), R(1, 3))
gs = (R(2), R(33, 10), R(37, 10))
ps = (R(7, 12), R(31, 120), R(19, 120))

# ---- exact hypothesis verification -------------------------------------
print("A_3 membership of A: ",
      all((gam[i]-gam[j])*(p[i]-p[j]) <= 0 for i in range(3) for j in range(3)))
print("A_3 membership of B: ",
      all((gs[i]-gs[j])*(ps[i]-ps[j]) <= 0 for i in range(3) for j in range(3)))
print("T-transform check (cols 2,3, w=3/10):")
w = R(3, 10); i, j = 1, 2
ok = (gs[i] == w*gam[i]+(1-w)*gam[j] and gs[j] == (1-w)*gam[i]+w*gam[j]
      and ps[i] == w*p[i]+(1-w)*p[j] and ps[j] == (1-w)*p[i]+w*p[j]
      and gs[0] == gam[0] and ps[0] == p[0])
print("   B == A*T:", ok)
print("   sum p* =", sum(ps))

# ---- htilde difference in z ---------------------------------------------
def htilde(p_, g_):
    # u^{g_i} = z^{10 g_i}
    num = sum(pi * gi * z ** sp.nsimplify(10 * gi) for pi, gi in zip(p_, g_))
    den = sum(pi * z ** sp.nsimplify(10 * gi) for pi, gi in zip(p_, g_))
    return sp.cancel(num / den)

d = sp.cancel(sp.together(htilde(p, gam) - htilde(ps, gs)))
num, den = sp.fraction(d)
num, den = sp.expand(num), sp.expand(den)
print("\nhtilde_A - htilde_B (u=z^10):")
print("numerator deg", sp.degree(num, z), ": d  denom deg", sp.degree(den, z))
pn, pd = sp.Poly(num, z), sp.Poly(den, z)
print("Sturm roots numerator in (0,1):", pn.count_roots(0, 1))
print("Sturm roots denominator in (0,1):", pd.count_roots(0, 1))
print("denominator sign on (0,1): eval at 1/2:", sp.sign(den.subs(z, R(1, 2))))
print("\nwitnesses (z -> exact d sign):")
for v in [R(1, 16), R(1, 4), R(1, 2), R(3, 4), R(7, 8), R(15, 16), R(31, 32)]:
    dv = sp.cancel(d.subs(z, v))
    print(f"  z={v}: sign {sp.sign(dv)}   value {sp.nsimplify(dv) if abs(dv)>0 else 0}")
# report u-values too
print("\nsame in u = z^10:")
for v in [R(7, 8), R(15, 16)]:
    print(f"  u = {v}^10 = {v**10} ~ {sp.N(v**10,6)}")
