#!/usr/bin/env python
"""Exact verification for the model reduction and the reversed hazard rate statements.

Part 1 (model reduction).  For the finite alpha-mixture with resilience-scaled
components, S_U(t) = [sum_i p_i Gbar(t/theta)^(alpha g_i)]^(1/alpha) (alpha != 0),
the hazard rate is h_U(t) = theta^{-1} h(t/theta) htilde_{p,g}(Gbar(t/theta)^alpha),
where h is the baseline hazard rate and
    htilde_{p,g}(y) = sum_i p_i g_i y^{g_i} / sum_i p_i y^{g_i}
is the exponential-mixture hazard rate in the variable y = e^{-t}.  The reversed
hazard rate displayed in the proof of Theorem 3.11 of Sahoo, Kayal and Finkelstein
(accepted manuscript: statement on page 23, proof on page 24),
    theta^{-1} g(t/theta) sum_i p_i g_i G^{alpha g_i - 1}(t/theta) / sum_i p_i G^{alpha g_i}(t/theta),
equals theta^{-1} r(t/theta) htilde_{p,g}(G(t/theta)^alpha) with r = g/G, and it is the
reversed hazard rate of the distribution function [sum_i p_i G(t/theta)^(alpha g_i)]^(1/alpha).

Part 2 (reversed hazard rates of exponential mixtures, model (1.3) as printed).
    r_{p,v}(t) = f/F = sum_i p_i v_i q^{v_i} / (1 - sum_i p_i q^{v_i}),  q = e^{-t}.
  (1,3,5) vs (1,4,4), equal weights: r_lambda - r_gamma = q^3 C(q)/(D_1 D_2) with
  C = 9 - 8q - 4q^2 - 4q^3 - 2q^4 strictly decreasing, so exactly one crossing, and
  the difference is 9/475 at q = 1/2 and negative at q = 9/10.
  (3,5) vs (4,4), equal weights: r values 17/59 and 4/15 at q = 1/2, one crossing.
  Tail: r_{p,v}(t) e^{v_min t} -> W_1 v_min.

Part 3 (alpha < 0 half).  htilde_{(1,3,5)}(1/q) - htilde_{(1,4,4)}(1/q)
    = 2(q - 1)(q^4 - 2q^3 - q - 1) / ((q^3 + 2)(q^2 - q + 1)(q^2 + q + 1))
has no root in (0,1) and is positive there.
"""
import sys

import sympy as sp

R = sp.Rational
q = sp.Symbol("q", positive=True)
RESULTS = []


def check(name, condition):
    ok = bool(condition)
    RESULTS.append((name, ok))
    print(("PASS " if ok else "FAIL ") + name)


def is_zero(expr):
    e = sp.powsimp(sp.expand(expr.rewrite(sp.exp)), force=True)
    return sp.simplify(sp.cancel(sp.together(e))) == 0


# Part 1: model reduction (three components, all parameters symbolic).
# Write Gbar(u) = exp(-H(u)) with H the cumulative baseline hazard rate, so h = H' and,
# by the chain rule with u = t/theta, d/dt = (H'(u)/theta) d/dH.  The value H(u) and the
# derivative H'(u) are represented by the positive symbols Hs and Hp.
th, al = sp.symbols("theta alpha", positive=True)
p1, p2, p3, g1, g2, g3 = sp.symbols("p1 p2 p3 g1 g2 g3", positive=True)
Hs, Hp = sp.symbols("H Hp", positive=True)
Gbar = sp.exp(-Hs)


def htilde(y):
    return (p1 * g1 * y**g1 + p2 * g2 * y**g2 + p3 * g3 * y**g3) / (p1 * y**g1 + p2 * y**g2 + p3 * y**g3)


SU = (p1 * Gbar**(al * g1) + p2 * Gbar**(al * g2) + p3 * Gbar**(al * g3))**(1 / al)
hU = -(sp.diff(SU, Hs) * Hp / th) / SU
check("1 h_U(t) = theta^{-1} h(t/theta) htilde_{p,g}(Gbar(t/theta)^alpha) for the model (1.3)",
      is_zero(hU - Hp / th * htilde(Gbar**al)))
check("1' with Gbar(u) = e^{-u} (H = u, H' = 1) and theta = alpha = 1 this is the exponential-mixture hazard rate",
      is_zero(hU.subs({Hp: 1, th: 1, al: 1}) - htilde(sp.exp(-Hs))))

# Distribution-function side: G(u) = exp(K(u)), so r = g/G = K'; symbols Ks (value) and Kp (derivative).
Ks, Kp = sp.symbols("K Kp", real=True)
G = sp.exp(Ks)
g_at_u = G * Kp                     # G'(u) = G(u) K'(u)
displayed = (1 / th) * g_at_u * (p1 * g1 * G**(al * g1 - 1) + p2 * g2 * G**(al * g2 - 1) + p3 * g3 * G**(al * g3 - 1)) \
    / (p1 * G**(al * g1) + p2 * G**(al * g2) + p3 * G**(al * g3))
check("2 the displayed reversed hazard rate equals theta^{-1} r(t/theta) htilde_{p,g}(G(t/theta)^alpha)",
      is_zero(displayed - Kp / th * htilde(G**al)))
FU = (p1 * G**(al * g1) + p2 * G**(al * g2) + p3 * G**(al * g3))**(1 / al)
check("3 the displayed formula is the reversed hazard rate F'/F of F = [sum p_i G^{alpha g_i}(t/theta)]^{1/alpha}",
      is_zero(displayed - (sp.diff(FU, Ks) * Kp / th) / FU))
SU_from_G = (p1 * (1 - G)**(al * g1) + p2 * (1 - G)**(al * g2) + p3 * (1 - G)**(al * g3))**(1 / al)
rU_model = -(sp.diff(SU_from_G, Ks) * Kp / th) / (1 - SU_from_G)
_pt = {th: 1, al: 1, p1: R(1, 3), p2: R(1, 3), p3: R(1, 3), g1: 1, g2: 3, g3: 5, Ks: sp.log(R(1, 2)), Kp: 1}
check("4 it differs from the reversed hazard rate of the model (1.3): at G = 1/2 (exponential baseline, t = log 2) "
      "the displayed value is 11/7 while r_U(log 2) = 11/25",
      sp.nsimplify(displayed.subs(_pt)) == R(11, 7) and sp.nsimplify(rU_model.subs(_pt)) == R(11, 25))
# Instance (1) under the displayed formula: exponential baseline G(u) = 1 - e^{-u}, so r(u) = e^{-u}/(1 - e^{-u});
# at t = log(4/3) one has G = 1/4 and r = 3, and the displayed difference for (1,3,5) versus (1,4,4)
# is 3 (103/91 - 12/11) = 123/1001 > 0, contradicting r_U <= r_V.
_pa = {th: 1, al: 1, p1: R(1, 3), p2: R(1, 3), p3: R(1, 3), Ks: sp.log(R(1, 4)), Kp: 3}
_d135 = displayed.subs(_pa).subs({g1: 1, g2: 3, g3: 5})
_d144 = displayed.subs(_pa).subs({g1: 1, g2: 4, g3: 4})
check("4' displayed formula, exponential baseline, t = log(4/3): r_(1,3,5) - r_(1,4,4) = 3 (103/91 - 12/11) = 123/1001 > 0",
      sp.nsimplify(_d135) == R(309, 91) and sp.nsimplify(_d144) == R(36, 11)
      and sp.nsimplify(_d135 - _d144) == R(123, 1001))


# Part 2: reversed hazard rates of exponential mixtures.
def rh(rates, p):
    S = sum(pi * q**r for r, pi in zip(rates, p))
    return sum(pi * r * q**r for r, pi in zip(rates, p)) / (1 - S)


p3u = (R(1, 3),) * 3
d = sp.cancel(sp.together(rh((1, 3, 5), p3u) - rh((1, 4, 4), p3u)))
Cq = 9 - 8 * q - 4 * q**2 - 4 * q**3 - 2 * q**4
D1 = q**4 + q**3 + 2 * q**2 + 2 * q + 3
D2 = 2 * q**3 + 2 * q**2 + 2 * q + 3
check("5 3 - q - q^3 - q^5 = (1 - q) D_1 and 3 - q - 2q^4 = (1 - q) D_2",
      sp.expand((1 - q) * D1 - (3 - q - q**3 - q**5)) == 0 and sp.expand((1 - q) * D2 - (3 - q - 2 * q**4)) == 0)
check("6 r_(1,3,5) - r_(1,4,4) = q^3 C(q) / (D_1 D_2), C = 9 - 8q - 4q^2 - 4q^3 - 2q^4",
      sp.cancel(d - q**3 * Cq / (D1 * D2)) == 0)
check("7 C' = -8 - 8q - 12q^2 - 8q^3 < 0 on (0,1); C(1/2) = 27/8 > 0 > C(9/10); exactly one root of C in (0,1)",
      sp.expand(sp.diff(Cq, q) + 8 + 8 * q + 12 * q**2 + 8 * q**3) == 0
      and Cq.subs(q, R(1, 2)) == R(27, 8) and Cq.subs(q, R(9, 10)) < 0
      and sp.Poly(Cq, q).count_roots(0, 1) == 1)
print("   C(9/10) =", Cq.subs(q, R(9, 10)))
check("8 r_(1,3,5)(log 2) = 11/25, r_(1,4,4)(log 2) = 8/19, difference 9/475 > 0",
      rh((1, 3, 5), p3u).subs(q, R(1, 2)) == R(11, 25) and rh((1, 4, 4), p3u).subs(q, R(1, 2)) == R(8, 19)
      and d.subs(q, R(1, 2)) == R(9, 475))
check("9 difference negative at q = 9/10 (t = log(10/9)), positive as q -> 0 (C(0) = 9)",
      d.subs(q, R(9, 10)) < 0 and Cq.subs(q, 0) == 9)

p2u = (R(1, 2), R(1, 2))
d2 = sp.cancel(sp.together(rh((3, 5), p2u) - rh((4, 4), p2u)))
C2 = 3 - 2 * q - 2 * q**2 - 2 * q**3 - q**4
check("10 r_(3,5)(log 2) = 17/59 > 4/15 = r_(4,4)(log 2)",
      rh((3, 5), p2u).subs(q, R(1, 2)) == R(17, 59) and rh((4, 4), p2u).subs(q, R(1, 2)) == R(4, 15))
check("11 r_(3,5) - r_(4,4) = q^3 C_2(q)/((2 + 2q + 2q^2 + q^3 + q^4)(1 + q + q^2 + q^3)), C_2 = 3 - 2q - 2q^2 - 2q^3 - q^4",
      sp.cancel(d2 - q**3 * C2 / ((2 + 2 * q + 2 * q**2 + q**3 + q**4) * (1 + q + q**2 + q**3))) == 0)
check("12 C_2 strictly decreasing, C_2(0) = 3 > 0 > -4 = C_2(1): exactly one crossing; negative at q = 99/100",
      sp.Poly(C2, q).count_roots(0, 1) == 1 and C2.subs(q, 0) == 3 and C2.subs(q, 1) == -4
      and all(c <= 0 for c in sp.Poly(sp.diff(C2, q), q).all_coeffs()) and d2.subs(q, R(99, 100)) < 0)

# Tail of the reversed hazard rate: r_{p,v}(t) e^{v_min t} -> W_1 v_min.
t = sp.Symbol("t", positive=True)
a, dd, w = sp.symbols("a d w", positive=True)
r2 = (w * a * sp.exp(-a * t) + (1 - w) * (a + dd) * sp.exp(-(a + dd) * t)) / (1 - w * sp.exp(-a * t) - (1 - w) * sp.exp(-(a + dd) * t))
check("13 two rates a < a + d with weights w, 1 - w: lim r(t) e^{at} = w a",
      sp.simplify(sp.limit(r2 * sp.exp(a * t), t, sp.oo) - w * a) == 0)
r135_t = rh((1, 3, 5), p3u).subs(q, sp.exp(-t))
check("13' (1,3,5) with equal weights: lim r(t) e^{t} = 1/3", sp.limit(r135_t * sp.exp(t), t, sp.oo) == R(1, 3))


# Part 3: the alpha < 0 half (y = Gbar^alpha > 1, written y = 1/q).
def ht(rates, p, y):
    return sum(pi * r * y**r for r, pi in zip(rates, p)) / sum(pi * y**r for r, pi in zip(rates, p))


da = sp.cancel(sp.together(ht((1, 3, 5), p3u, 1 / q) - ht((1, 4, 4), p3u, 1 / q)))
check("14 htilde_(1,3,5)(1/q) - htilde_(1,4,4)(1/q) = 2(q-1)(q^4 - 2q^3 - q - 1)/((q^3+2)(q^2-q+1)(q^2+q+1))",
      sp.cancel(da - 2 * (q - 1) * (q**4 - 2 * q**3 - q - 1) / ((q**3 + 2) * (q**2 - q + 1) * (q**2 + q + 1))) == 0)
check("15 no root in (0,1) and positive there (value 72/119 at q = 1/2): the alpha < 0 direction is not contradicted",
      sp.Poly(sp.fraction(da)[0], q).count_roots(R(1, 10**9), 1 - R(1, 10**9)) == 0 and da.subs(q, R(1, 2)) == R(72, 119)
      and sp.Poly(q**4 - 2 * q**3 - q - 1, q).count_roots(0, 1) == 0)

failed = [name for name, ok in RESULTS if not ok]
print(f"\n{len(RESULTS) - len(failed)} passed, {len(failed)} failed")
sys.exit(1 if failed else 0)
