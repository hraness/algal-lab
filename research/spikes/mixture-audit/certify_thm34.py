"""EXACT CERTIFICATION: counterexample to SKF2026 Theorem 3.4.

Theorem 3.4 (accepted ms, p.14): t^2 g(t) increasing on t>0, alpha < gamma
(scalar), p in eps+_n (increasing), theta,xi in D+_n (decreasing),
theta weakly supermajorized by xi (theta <^w xi: partial sums of increasing
rearrangement >=)  ==>  U_n(p,gam,theta) >=st V_n(p,gam,xi).

Counterexample (n=2, Lomax baseline Gbar(t)=1/(1+t), g(t)=1/(1+t)^2,
t^2 g(t)=t^2/(1+t)^2 increasing on t>0):
    p = (1/3, 2/3)  (increasing)
    gam = 3, alpha = 2/3  (alpha < gam)
    theta = (3, 1), xi = (7/2, 1/2)  (both decreasing)
    theta <^w xi: inc partial sums: 1 >= 1/2, 4 >= 4.
Claim: inner_U(t) >= inner_V(t) for all t>0 (a>0: S=inner^{1/a} increasing
in inner).  Compute
    d(t) = sum_i p_i [ (theta_i/(theta_i+t))^2 - (xi_i/(xi_i+t))^2 ]
    where exponent ag = alpha*gam = 2.
Certificate: numerator of d has exactly one root in (0,oo); d(1)=? >0,
d(20)<0 -> sign change -> claim false.
"""
import sympy as sp
from audit_lib import R, weak_super, weak_sub, inc_order

t = sp.Symbol("t", positive=True)

p = (R(1, 3), R(2, 3))
gam = R(3)
alpha = R(2, 3)
ag = alpha * gam              # = 2, exponent
theta = (R(3), R(1))
xi = (R(7, 2), R(1, 2))


def hypothesis_check():
    ok = True
    ok &= (p[0] < p[1])                              # p in eps+
    ok &= theta[0] > theta[1] and xi[0] > xi[1]      # theta, xi in D+
    ok &= weak_super(list(theta), list(xi))          # theta <^w xi
    ok &= (alpha < gam)                              # alpha < gamma
    ok &= not majorization_equal(theta, xi)
    # baseline admissibility: t^2 g increasing (identity check)
    g = 1 / (1 + t) ** 2
    t2g = sp.simplify(t ** 2 * g)
    ok &= sp.simplify(sp.diff(t2g, t) - 2 * t / (1 + t) ** 3) == 0
    ok &= (2 * t / (1 + t) ** 3).subs(t, 1) > 0
    print("hypotheses satisfied:", bool(ok))
    return ok


def majorization_equal(a, b):
    return tuple(sorted(a)) == tuple(sorted(b))


def build_d():
    du = sum(p[i] * (theta[i] / (theta[i] + t)) ** int(ag) for i in range(2))
    dv = sum(p[i] * (xi[i] / (xi[i] + t)) ** int(ag) for i in range(2))
    return sp.cancel(sp.together(du - dv))


def main():
    hypothesis_check()
    d = build_d()
    num, den = sp.fraction(d)
    num, den = sp.expand(num), sp.expand(den)
    print("inner_U - inner_V =", d)
    print("numerator =", num)
    print("denominator =", den)
    poly = sp.Poly(num, t)
    print("roots of numerator in (0,oo) (count):",
          poly.count_roots(0, sp.oo))
    print("root intervals:", poly.intervals())
    denpoly = sp.Poly(den, t)
    print("denominator roots in (0,oo):", denpoly.count_roots(0, sp.oo),
          "(denominator =", sp.factor(den), ")")
    for v in (R(1, 4), R(1), R(2), R(5), R(10), R(20), R(50)):
        print(f"  d({v}) = {d.subs(t, v)} = {float(d.subs(t, v)):.6f}")
    # witnesses
    w1 = d.subs(t, R(1))
    w2 = d.subs(t, R(20))
    print("CERT: d(1) =", w1, "> 0;", "d(20) =", w2, "< 0")
    # SF difference sign: S = inner^{1/alpha}, alpha=2/3>0 -> sign(S_U-S_V)
    # = sign(inner diff).  The claimed order U >=st V requires d >= 0
    # for ALL t>0; violated in a neighborhood of t=20.
    #
    # Also the 3-component instance found by random search:
    p3 = (R(25, 86), R(27, 86), R(17, 43))
    gam3, ag3 = R(6), R(5)
    theta3 = (R(8), R(8), R(5))
    xi3 = (R(9), R(8), R(4))
    print("\n--- 3-component instance ---")
    print("theta3 <^w xi3:", weak_super(list(theta3), list(xi3)),
          " inc:", inc_order(theta3), inc_order(xi3))
    du = sum(p3[i] * (theta3[i] / (theta3[i] + t)) ** int(ag3) for i in range(3))
    dv = sum(p3[i] * (xi3[i] / (xi3[i] + t)) ** int(ag3) for i in range(3))
    d3 = sp.cancel(sp.together(du - dv))
    num3, den3 = sp.fraction(d3)
    poly3 = sp.Poly(sp.expand(num3), t)
    print("roots in (0,oo):", poly3.count_roots(0, sp.oo))
    print("intervals:", poly3.intervals())
    for v in (R(1), R(5), R(20), R(50)):
        print(f"  d3({v}) = {float(d3.subs(t, v)):.6f}")


if __name__ == "__main__":
    main()
