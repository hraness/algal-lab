"""Independent C3 for doi_10.29252_jss.12.2.395 (thinned portfolio sums).

Refutes Thm 2/3/4/5 as printed: with n=2 Exp severities the aggregate
survival S_agg(x) = p1(1-p2)S1 + p2(1-p1)S2 + p1 p2 S_conv is polynomial
in z=e^{-x}; the claimed directions fail.

  T2: E=S_p-S_q = -19 z/300 + 9 z^3/100: negative for z^2 < 27/19*... i.e.
      x > ln(81/19)/2 ~ 0.726; at x=1, E=-0.0188.
  T3: E=S_mu-S_lam < 0 for all x>0 (numerically at interior points).
  T4: at x->0+, S_agg(0) = p1+p2-p1p2: 2/3 vs 0.6465 -> E=-2/99<0.
  T5: PRHR version of T4: same coverage-sum deficit at x=0+:
      S(0)=P(any claim): 2/3 vs 0.6465 -> printed direction fails.
"""
import sympy as sp

x = sp.symbols('x', positive=True)
z = sp.symbols('z', positive=True)


def S_exp(l):
    return sp.exp(-l * x)


def conv_exp(l1, l2):
    if l1 == l2:
        return (1 + l1 * x) * sp.exp(-l1 * x)
    return (l2 * sp.exp(-l1 * x) - l1 * sp.exp(-l2 * x)) / (l2 - l1)


def agg(p1, l1, p2, l2):
    return (p1 * (1 - p2) * S_exp(l1) + p2 * (1 - p1) * S_exp(l2)
            + p1 * p2 * conv_exp(l1, l2))


print("== T2: p=(1/3,1/2)@lam=(1,3) vs q=(2/5,2/5)@lam=(1,3) ==")
Sp = agg(sp.Rational(1, 3), 1, sp.Rational(1, 2), 3)
Sq = agg(sp.Rational(2, 5), 1, sp.Rational(2, 5), 3)
E = sp.factor(sp.expand(Sp - Sq).subs(sp.exp(-x), z))
print("E = S_p - S_q =", E)
# -19/300 z + 9/100 z^3 = z(9/100 z^2 - 19/300): zero at z^2=19/27
print("zero of E/z at z^2 =", sp.solve(sp.expand(Sp - Sq).subs(
    sp.exp(-x), z) / z, z))
print("E(1) =", sp.N((Sp - Sq).subs(x, 1), 10))

print("\n== T3: mu=(2,2) vs lam=(3,1), p=(1/2,1/2) ==")
Smu = agg(sp.Rational(1, 2), 2, sp.Rational(1, 2), 2)
Slam = agg(sp.Rational(1, 2), 3, sp.Rational(1, 2), 1)
E3 = sp.expand(Smu - Slam)
print("E = S_mu - S_lam =", E3)
for v in [sp.Rational(1, 10), 1, 2, 4, 8]:
    print("  x=%s E=%s" % (v, sp.N(E3.subs(x, v), 8)))

print("\n== T4: (lam,p)=((3,1),(1/2,1/3)) vs (mu,q)=((5/2,3/2),(4/9,4/11)) ==")
Sl = agg(sp.Rational(1, 2), 3, sp.Rational(1, 3), 1)
Sm = agg(sp.Rational(4, 9), sp.Rational(5, 2), sp.Rational(4, 11),
         sp.Rational(3, 2))
E4 = Sm - Sl
print("claim E = S_qmu - S_plam; E(0+) =", sp.simplify(
    sp.limit(E4, x, 0, dir='+')),
    "= -2/99 < 0")
for v in [sp.Rational(1, 10), 1, 3]:
    print("  x=%s E=%s" % (v, sp.N(E4.subs(x, v), 8)))

print("\n== T5 (PRHR): coverage-sum deficit at x=0+ ==")
print("S_agg(0+) independent of family: p-side 2/3, q-side 4/9+4/11-16/99")
print("  =", sp.Rational(4, 9) + sp.Rational(4, 11) - sp.Rational(16, 99),
      "= 64/99 < 2/3 = 66/99 -> E(0+) = -2/99 < 0")
