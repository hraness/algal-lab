"""C3 for arxiv:1904.08730 refutations.

(1) Theorem 3.10 (lr): min survival of EG2(theta,phi,alpha_i) components is
    (1 - e^{-t x^{-p}})^{sum a_i} = EG2(t, p, Sa).  Then
        f_{b}/f_{a} = (b/a) u(x)^{b-a},   u(x) = 1 - e^{-t x^{-p}},
    u'(x) = -t p x^{-p-1} e^{-t x^{-p}} < 0.  Hence for b > a the ratio is
    strictly decreasing -> X_{1:n} <=lr X*_{1:n} fails whenever
    sum a_i < sum a*_i (the printed hypothesis).  Verified symbolically and
    numerically at the evaluator witness x = 1/100.

(2) Example 3.3 (st): printed matrices satisfy the recorded hypothesis
    A = B*T_0.8; the claimed X_{1:2} <=st X*_{1:2} is checked at 300-digit
    precision at the interval witness x = 1/100 (phi = 1, as the paper does
    not print phi for this example).

(3) Example 3.4 (st): same check for X_{2:2} >=st X*_{2:2} (max survival).
"""
import sympy as sp
from mpmath import mp, mpf, exp, power

mp.dps = 300

x = sp.symbols('x', positive=True)
t_, p_, a_, b_ = sp.symbols('t p a b', positive=True)
u = 1 - sp.exp(-t_ * x ** (-p_))
Sa, Sb = u ** a_, u ** b_
fa, fb = -sp.diff(Sa, x), -sp.diff(Sb, x)
ratio = sp.simplify(fb / fa)
dr = sp.simplify(sp.diff(sp.log(ratio), x))
print("d/dx log(f_b/f_a) =", dr)
# substituting numbers shows sign for any positive params at interior x:
print("sign check at a=2,b=3,t=1,p=1,x=1/100:",
      sp.N(dr.subs({t_: 1, p_: 1, a_: 2, b_: 3, x: sp.Rational(1, 100)}), 15))


def S_eg2(th, ph, al, xv):
    th, ph, al, xv = mpf(th), mpf(ph), mpf(al), mpf(xv)
    return (1 - exp(-th * power(xv, -ph))) ** al


def S_min(mat, ph, xv):
    a, t = mat
    s = mpf(1)
    for ai, ti in zip(a, t):
        s *= S_eg2(ti, ph, ai, xv)
    return s


def S_max(mat, ph, xv):
    a, t = mat
    f = mpf(1)
    for ai, ti in zip(a, t):
        f *= 1 - S_eg2(ti, ph, ai, xv)
    return 1 - f


w = mpf(1) / 100

# Example 3.3 (phi=1): X_{1:2} <=st X*_{1:2} requires S_minX <= S_minY
mA = ([mpf("0.54"), mpf("0.66")], [mpf("1.7"), mpf("1.4")])
mB = ([mpf("0.5"), mpf("0.7")], [mpf("1.8"), mpf("1.3")])
d = S_min(mB, 1, w) - S_min(mA, 1, w)
print("Ex3.3: S_minB - S_minA at x=1/100:", mp.nstr(d, 20))

# Example 3.4 (phi=1): X_{2:2} >=st X*_{2:2} requires S_maxA >= S_maxB
mA2 = ([mpf("2.34"), mpf("2.26")], [mpf("1.32"), mpf("1.38")])
mB2 = ([mpf("2.1"), mpf("2.5")], [mpf("1.5"), mpf("1.2")])
d2 = S_max(mA2, 1, w) - S_max(mB2, 1, w)
print("Ex3.4: S_maxA - S_maxB at x=1/100:", mp.nstr(d2, 20))

# scan a few more points to see whether the differences are structural
for wv in [mpf(10) ** -k for k in (4, 3, 2, 1)]:
    print("x=%g  ex3.3 diff=%s  ex3.4 diff=%s" % (
        float(wv), mp.nstr(S_min(mB, 1, wv) - S_min(mA, 1, wv), 10),
        mp.nstr(S_max(mA2, 1, wv) - S_max(mB2, 1, wv), 10)))
