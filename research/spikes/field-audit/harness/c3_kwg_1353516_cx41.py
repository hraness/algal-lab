"""Independent C3 check: Counterexample 4.1 of doi:10.1080/02331888.2017.1353516.

Paper asserts U_{1:n} <=hr V_{1:n} holds (Figure 4.2) with
U_i ~ Kw-G(alpha_i,beta_i,F1), V_i ~ Kw-G(gamma_i,beta_i,F2),
F1 = 1-e^{-3 x^4.4}, F2 = 1-e^{-0.2 x^0.4},
alpha=(1.99,0.01), gamma=(1.98,0.02), beta=(1,2).

For a series system the hazard rate adds: r = sum_i a_i b_i F^{a_i-1} f /
(1 - F^{a_i}).  sign(E_hr) = sign(r_U - r_V).  Near x->0 the small-alpha
term dominates: r_U ~ C_U x^{-0.956}, r_V ~ C_V x^{-0.992} -> r_V >> r_U,
so the hr ordering fails near 0 (the figure's y=e^{-x} plot region
y>0.985 i.e. x<0.015 barely misses this).
"""
import sympy as sp
from mpmath import iv

iv.dps = 150
t = sp.Symbol("t", positive=True)


def ie(e, x0):
    if e == t:
        return iv.mpf(int(x0.p)) / iv.mpf(int(x0.q))
    if e.is_Rational:
        return iv.mpf(int(e.p)) / iv.mpf(int(e.q))
    if e.is_Add:
        s = iv.mpf(0)
        for a in e.args:
            s += ie(a, x0)
        return s
    if e.is_Mul:
        p = iv.mpf(1)
        for a in e.args:
            p *= ie(a, x0)
        return p
    if e.is_Pow:
        b_, e_ = e.args
        if e_.is_Integer:
            r = iv.mpf(1)
            for _ in range(abs(int(e_))):
                r *= ie(b_, x0)
            return r if int(e_) >= 0 else 1 / r
        return iv.exp(ie(e_, x0) * iv.log(ie(b_, x0)))
    if e.func == sp.exp:
        return iv.exp(ie(e.args[0], x0))
    raise ValueError(type(e))


F1 = 1 - sp.exp(-3 * t ** sp.Rational(44, 10))
F2 = 1 - sp.exp(-sp.Rational(1, 5) * t ** sp.Rational(2, 5))
al = [sp.Rational(199, 100), sp.Rational(1, 100)]
ga = [sp.Rational(198, 100), sp.Rational(2, 100)]
be = [sp.Rational(1), sp.Rational(2)]
f1 = sp.diff(F1, t)
f2 = sp.diff(F2, t)

rU = sum(a * b * F1 ** (a - 1) * f1 / (1 - F1 ** a) for a, b in zip(al, be))
rV = sum(g * b * F2 ** (g - 1) * f2 / (1 - F2 ** g) for g, b in zip(ga, be))
D = rU - rV   # U <=hr V needs rU >= rV, i.e. D >= 0

neg = 0
for e10 in (6, 8, 10, 12, 15):
    for m_ in (1, 5, 9):
        pt = sp.Rational(m_) * sp.Rational(10) ** (-e10)
        v = ie(D, pt)
        flag = "NEGATIVE" if v.b < 0 else ("positive" if v.a > 0 else "undecided")
        print(f"x={pt}: rU-rV in [{v.a}, {v.b}]  {flag}")
        neg += v.b < 0
assert neg > 0
print("REFUTATION CONFIRMED: printed 'hr holds' figure claim fails near x=0")
