"""Independent C3 for doi:10.1016/j.orl.2020.12.009 Counterexample 4.1
(= arXiv:1612.00571 Counterexample 5.4).

The paper claims no stochastic ordering between the two parallel
systems.  Case (a): F(x) = 1 - e^{-x^{1/2}}, alphas a=(9/10, 29/20,
43/20) under LA generator th=9/10 vs b=(6/5, 39/20, 53/20) under GB
generator th=8.  We find the forward ordering S_B >= S_A pointwise:
the "neither" claim fails.

Generators (Archimedean, phi = psi^{-1}):
  LA:  psi(u) = e^{th/u} - e^{th};  phi(t) = th / log(t + e^{th})
  GB:  psi(u) = log(1 - th log u); phi(t) = e^{(1-e^t)/th}
PO margins: F_i(x) = F(x) / (a_i + (1-a_i) F(x)).
Parallel maximum cdf: phi( sum_i psi(F_i(x)) ).
"""
from mpmath import iv, nstr

iv.dps = 80
E = iv.e


def la_psi(u, th):
    return iv.exp(th / u) - iv.exp(th)


def la_phi(t, th):
    return th / iv.ln(t + iv.exp(th))


def gb_psi(u, th):
    return iv.ln(1 - th * iv.ln(u))


def gb_phi(t, th):
    return iv.exp((1 - iv.exp(t)) / th)


def po_F(F, a):
    return F / (a + (1 - a) * F)


def Fmax(x, alphas, psi, phi, th):
    F = 1 - iv.exp(-x ** iv.mpf('0.5'))
    s = sum(psi(po_F(F, a), th) for a in alphas)
    return phi(s, th)


A_ = [iv.mpf(9) / 10, iv.mpf(29) / 20, iv.mpf(43) / 20]
B_ = [iv.mpf(6) / 5, iv.mpf(39) / 20, iv.mpf(53) / 20]

print("case (a): E = S_B - S_A = (1-F_B) - (1-F_A) = F_A - F_B >= 0")
for t in ["0.001", "0.01", "0.1", "0.5", "1", "2", "4"]:
    xx = iv.mpf(t)
    d = Fmax(xx, A_, la_psi, la_phi, iv.mpf(9) / 10) \
        - Fmax(xx, B_, gb_psi, gb_phi, iv.mpf(8))
    print(f"x={t:>6}: F_A-F_B in [{nstr(d.a,8)},{nstr(d.b,8)}]",
          ">=0 (fwd order holds)" if d.a >= 0 else "NEGATIVE")
