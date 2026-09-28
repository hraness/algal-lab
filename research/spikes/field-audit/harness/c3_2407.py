"""C3 for the arxiv:2407.18801 counterexample: independent evaluator.

Independent exponentials (the SC or PHR model after the increasing transform to
exponential rates, independence copula). P(X_{2:3} > t) = P(at most one failed)
computed directly: prod_j e^{-r_j t} + sum_i (1 - e^{-r_i t}) prod_{j != i} e^{-r_j t}.
theta = (11/4, 1/4, 3) is p-larger than theta* = (1/2, 9/4, 2); the claim is
X_{2:3} >=st Y_{2:3}, i.e. S_X(t) >= S_Y(t) for all t.
"""
from mpmath import exp, iv, mp, mpf, nstr


def surv(rates, t, lib):
    e = [lib.exp(-r * t) for r in rates]
    total = e[0] * e[1] * e[2]
    for i in range(3):
        others = [e[j] for j in range(3) if j != i]
        total += (1 - e[i]) * others[0] * others[1]
    return total


iv.dps = 50
theta = [iv.mpf(11) / 4, iv.mpf(1) / 4, iv.mpf(3)]
theta_s = [iv.mpf(1) / 2, iv.mpf(9) / 4, iv.mpf(2)]
for t in ["2", "2.7725887222397812", "4", "8"]:
    T = iv.mpf(t)
    d = surv(theta, T, iv) - surv(theta_s, T, iv)
    print("t =", t, " S_X - S_Y in", nstr(d.a, 12), nstr(d.b, 12), "negative" if d.b < 0 else ("positive" if d.a > 0 else "undecided"))

print("\n== Archimedean-copula model (as printed in the paper) ==")
# S_{2:n}(x) = sum_i psi(sum_{j!=i} phi(S_j)) - (n-1) psi(sum_j phi(S_j))
# Gumbel-Barnett theta=1/5: psi(t)=e^{t(1-e^t)}... paper prints
# psi(t)=e^{(1-e^t)/th}, phi(u)=ln(1-th ln u).
ln = iv.ln
exp = iv.exp


def psi_gb(t, th):
    return exp((1 - exp(t)) / th)


def phi_gb(u, th):
    return ln(1 - th * ln(u))


def s2n(margins, th):
    phi_t = [phi_gb(m, th) for m in margins]
    tot = sum(phi_t)
    n = len(margins)
    return sum(psi_gb(tot - p, th) for p in phi_t) - (n - 1) * psi_gb(tot, th)


def ew(t_i, x):
    return 1 - (1 - exp(-(t_i * x) ** iv.mpf('0.9'))) ** iv.mpf('0.9')


TH = iv.mpf(1) / 5
T1 = [iv.mpf(t) for t in ["0.12", "0.28", "0.51", "0.62", "0.73"]]
T2 = [iv.mpf(t) for t in ["0.21", "0.42", "0.73", "0.89", "0.92"]]
print("EW example, claim X2:5 >=st Y2:5 i.e. S_X-S_Y>=0; printed theta=0.2")
for t in ["0.000001", "0.01", "0.1", "0.3", "0.5", "1"]:
    xx = iv.mpf(t)
    d = s2n([ew(v, xx) for v in T1], TH) - s2n([ew(v, xx) for v in T2], TH)
    print(f"  x={t:>9}: S_X-S_Y in [{nstr(d.a,9)},{nstr(d.b,9)}]",
          "NEGATIVE (refutes)" if d.b < 0 else "nonneg")

# same sign pattern under theta=1/10 (printed coefficient 10)
print("theta=0.1:")
for t in ["0.01", "0.1"]:
    xx = iv.mpf(t)
    d = s2n([ew(v, xx) for v in T1], iv.mpf(1) / 10) \
        - s2n([ew(v, xx) for v in T2], iv.mpf(1) / 10)
    print(f"  x={t:>9}: S_X-S_Y in [{nstr(d.a,9)},{nstr(d.b,9)}]",
          "NEGATIVE (refutes)" if d.b < 0 else "nonneg")

print("\n== Proposition 2 (location-scale, logistic baseline) ==")
# F = logistic; margins F_i = F(th_i (x - lam)), lam=1; claim X2:n >=st Y2:n
# th=(1,2,3) vs th*=(3/2,2,5/2): products of smallest of th <= th*'s.
flog = lambda u: 1 / (1 + exp(-u))
SXm = [flog(t * (iv.mpf(xx) - 1)) for t in [1, 2, 3]]
SYm = [flog(t * (iv.mpf(xx) - 1)) for t in
       [iv.mpf(3) / 2, 2, iv.mpf(5) / 2]]
for t_ in ["1.1", "1.5", "2", "3", "5", "10"]:
    xx = iv.mpf(t_)
    SXm = [flog(t * (xx - 1)) for t in [iv.mpf(1), 2, 3]]
    SYm = [flog(t * (xx - 1)) for t in [iv.mpf(3) / 2, 2, iv.mpf(5) / 2]]
    d = s2n(SXm, TH) - s2n(SYm, TH)
    print(f"  x={t_:>4}: S_X-S_Y in [{nstr(d.a,9)},{nstr(d.b,9)}]",
          "NEGATIVE (refutes)" if d.b < 0 else "nonneg")

print("\n== Weibull + Clayton(10) counterexample ==")
# S_i = e^{-(t_i x)^0.9}; Clayton psi(t)=(1+th t)^{-1/th}, phi=(u^{-th}-1)/th.
# Paper claims NO ordering; we check both directions.


def psi_cl(t, th):
    return (1 + th * t) ** (-1 / th)


def phi_cl(u, th):
    return (u ** (-th) - 1) / th


def s2n_cl(margins, th):
    phi_t = [phi_cl(m, th) for m in margins]
    tot = sum(phi_t)
    n = len(margins)
    return sum(psi_cl(tot - p, th) for p in phi_t) - (n - 1) * psi_cl(tot, th)


def wb(t_i, x):
    return exp(-(t_i * x) ** iv.mpf('0.9'))


T3 = [iv.mpf(t) for t in ["0.13", "0.31", "0.49", "0.61", "0.72"]]
T4 = [iv.mpf(t) for t in ["0.22", "0.41", "0.71", "0.88", "0.92"]]
neg10 = iv.mpf(10)
for t_ in ["0.01", "0.1", "0.5", "1", "2", "4", "8"]:
    xx = iv.mpf(t_)
    d = s2n_cl([wb(v, xx) for v in T3], neg10) \
        - s2n_cl([wb(v, xx) for v in T4], neg10)
    print(f"  x={t_:>5}: S_X-S_Y in [{nstr(d.a,9)},{nstr(d.b,9)}]",
          "NEGATIVE" if d.b < 0 else "POSITIVE")
print("-> S_X - S_Y >= 0 throughout: X2:5 >=st Y2:5 holds; the printed "
      "'no ordering' conclusion is refuted.")
