"""Sturm-certified counterexample to the reconstructed VKF2025 Thm 3.1(i):
   alpha >= gamma, t^2 g increasing, p in D+ (or E+), theta,xi in E+ (or D+),
   theta <^w xi  =>  U >=st V.   Lomax baseline Gbar=1/(1+t), t^2 g =
   t^2/(1+t)^2 strictly increasing on t>0.

Witness (found by audit_vkf_fast.py, Fraction-exact grid):
   n=2, p=(4/5,1/5) [decreasing, D+], gamma=2, alpha=2 (so alpha >= gamma,
   alpha*gamma=4 > 1), theta=(4,7), xi=(1,9) [increasing, E+],
   theta <^w xi: partial sums of increasing rearrangements 4>=1, 11>=10.
"""
import sympy as sp
from audit_lib import R, inc_order

t_ = sp.Symbol("t", positive=True)


def inner_lomax(p, theta, ag):
    return sum(p[i] * (R(theta[i]) / (R(theta[i]) + t_)) ** int(ag)
               for i in range(len(p)))


p = (R(4, 5), R(1, 5))
gam, alpha = R(2), R(2)
theta, xi = (R(4), R(7)), (R(1), R(9))
ag = int(alpha * gam)

# hypothesis checks (exact)
ps, qs = inc_order(theta), inc_order(xi)
assert all(sum(ps[:k]) >= sum(qs[:k]) for k in range(1, 3)), "theta <^w xi fails"
print("hypotheses: p dec:", list(p) == sorted(p, reverse=True),
      "| theta,xi inc:",
      list(theta) == sorted(theta), list(xi) == sorted(xi),
      "| theta <^w xi:", [sum(ps[:k]) >= sum(qs[:k]) for k in (1, 2)],
      "| alpha>=gamma:", alpha >= gam, "| ag =", ag)

d = sp.cancel(sp.together(inner_lomax(list(p), list(theta), ag)
                          - inner_lomax(list(p), list(xi), ag)))
num, den = sp.fraction(d)
num, den = sp.expand(num), sp.expand(den)
print("d(t) = inner_U - inner_V; claim requires d >= 0 on t>0")
print("num =", sp.factor(num) if sp.factor(num) != num else num)
print("den =", den, "=", sp.factor(den))
npoly = sp.Poly(num, t_)
print("positive roots (Sturm, (0,oo) via count_roots(0, oo)):")
print("  (0,1):", npoly.count_roots(0, 1), " (1,oo):", npoly.count_roots(1, sp.oo))
print("  isolating intervals:", npoly.intervals())
for v in (R(1, 4), R(1, 2), R(1), R(3), R(8), R(12), R(15)):
    print(f"  d({v}) = {d.subs(t_, v)}  ~ {sp.N(d.subs(t_, v), 10)}")

# --- control: SKF 3.4 certified cex also lies in VKF 3.1(ii) range --------
print("\n[control] SKF-audit cex: p=(1/3,2/3) inc, gam=3, alpha=2/3 -> "
      "0 < alpha < gamma (VKF 3.1(ii) range); theta=(3,1), xi=(7/2,1/2) dec")
d2 = sp.cancel(sp.together(inner_lomax((R(1, 3), R(2, 3)), (R(3), R(1)), 2)
                           - inner_lomax((R(1, 3), R(2, 3)), (R(7, 2), R(1, 2)), 2)))
n2, dd2 = sp.fraction(d2)
print("  roots in (0,1):", sp.Poly(sp.expand(n2), t_).count_roots(0, 1),
      "| d(1) =", d2.subs(t_, 1), "| d(20) =", d2.subs(t_, 20))
