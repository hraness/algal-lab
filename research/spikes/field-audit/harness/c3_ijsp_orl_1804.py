"""C3 second evaluations (independent mpmath) for three leftover refuted
papers:
  doi:10.11648/j.ijsda.20261201.11 (KwEE, Theorem 9.1 case ii)
  doi:10.1016/j.orl.2020.12.009   (PO systems, Counterexample 4.1)
  arxiv:1804.04103                (log-Lindley shocked parallel, Theorem 3.1i)
"""
from mpmath import mp, mpf, iv

mp.dps = 80; iv.dps = 80

# ---------- ijsda: KwEE  S(x) = (1 - (1 - e^{-l x})^a)^b ------------------
def kwee(a, b, l2, t, L):
    return (1 - (1 - L.exp(-l2 * t)) ** a) ** b

# case ii: a1<a2, b1<b2, l common -> printed chain X <=lr <=hr <=st Y.
# st: S_X <= S_Y pointwise.  Instances from eval: (1,1,1) vs (2,2,1) etc.
for px, py in [((1, 1, 1), (2, 2, 1)), ((1, 2, 4), (3, 4, 4)), ((2, 1, 2), (4, 3, 2))]:
    diffs = [kwee(*py, mpf(t), mp) - kwee(*px, mpf(t), mp)
             for t in ['0.01', '0.05', '0.19', '0.3', '0.5', '1', '2']]
    print('KwEE st S_Y-S_X', px, py, [mp.nstr(d, 6) for d in diffs])
# interval at witness 3/16 for first instance
d = kwee(2, 2, 1, iv.mpf('0.1875'), iv) - kwee(1, 1, 1, iv.mpf('0.1875'), iv)
print('KwEE iv st at 3/16:', mp.nstr(d.a, 10))

# ---------- orl.2020.12.009: PO parallel systems, Counterexample 4.1 ------
# PO margin survival S_a = a*Fbar/(1-(1-a)Fbar); cdf F_a = F/(a+(1-a)F).
# Counterexample 4.1: F=1-e^{-x^{1/2}}; a=(0.9,1.45,2.15), b=(1.2,1.95,2.65);
# copula pair (LA(0.9), GB(8)) and (GB(0.9), TI(1/5)).
def poF(Fv, a, L):
    return Fv / (a + (1 - a) * Fv)

def la(t, th, L):  return th / L.log(t + L.exp(th))
def la_psi(u, th, L): return L.exp(th / u) - L.exp(th)
def gb(t, th, L):  return L.exp((1 - L.exp(t)) / th)
def gb_psi(u, th, L): return L.log(1 - th * L.log(u))
def ti(t, a, L):   return (2 / (1 + L.exp(t))) ** (1 / a)
def ti_psi(u, a, L): return L.log(2 * u ** (-a) - 1)

def pmax(par, Fv, phipsi, xx, L):
    phi, psi = phipsi
    t = 0
    for p in par:
        t += psi(poF(Fv(xx), p, L))
    return 1 - phi(t)

FW = lambda z: mp.e ** (-mp.sqrt(z))
for label, g1, g2 in [
        ('LA0.9/GB8', (lambda t: la(t, mpf('0.9'), mp), lambda u: la_psi(u, mpf('0.9'), mp)),
                      (lambda t: gb(t, mpf(8), mp),   lambda u: gb_psi(u, mpf(8), mp))),
        ('GB0.9/TI0.2', (lambda t: gb(t, mpf('0.9'), mp), lambda u: gb_psi(u, mpf('0.9'), mp)),
                        (lambda t: ti(t, mpf('0.2'), mp), lambda u: ti_psi(u, mpf('0.2'), mp)))]:
    a = [mpf('0.9'), mpf('1.45'), mpf('2.15')]
    b = [mpf('1.2'), mpf('1.95'), mpf('2.65')]
    fwd = [pmax(b, FW, g2, mpf(t), mp) - pmax(a, FW, g1, mpf(t), mp)
           for t in ['0.01', '0.1', '0.5', '1', '2', '5']]
    rev = [pmax(a, FW, g1, mpf(t), mp) - pmax(b, FW, g2, mpf(t), mp)
           for t in ['0.01', '0.1', '0.5', '1', '2', '5']]
    print('orl', label, 'S_B-S_A fwd:', [mp.nstr(d, 5) for d in fwd])
    print('orl', label, 'rev:', [mp.nstr(d, 5) for d in rev])

# ---------- arxiv_1804.04103: log-Lindley shocked parallel ----------------
# S_T(x) = 1 - x^s + s x^s ln x/(1 + l s);  F_Xi = 1 - p_i S_Ti;  F_n:n = prod.
def ll_shock(p, s, lam, t, L):
    ST = 1 - t ** s + s * t ** s * L.log(t) / (1 + lam * s)
    return 1 - p * ST

def maxsurv(par, t, L):
    g = 1
    for p, s, lam in par:
        g *= ll_shock(p, s, lam, t, L)
    return 1 - g

# Thm 3.1 case (i): h(u)=u, uX=(4/5,1/5), uY=(3/4,1/2) (smallest-sums ~w),
# lam=(2,1), sigma=1, p_i = u_i.
PX = [(mpf('0.8'), 1, 2), (mpf('0.2'), 1, 1)]
PY = [(mpf('0.75'), 1, 2), (mpf('0.5'), 1, 1)]
# claim X >=st Y  => S_X - S_Y >= 0
for t in ['1e-12', '1e-9', '1e-4', '0.05', '0.2', '0.5', '0.9']:
    d = maxsurv(PX, mpf(t), mp) - maxsurv(PY, mpf(t), mp)
    print('ll Thm3.1(i) S_X-S_Y at t=%s:' % t, mp.nstr(d, 10))
d = maxsurv([(iv.mpf('0.8'), 1, 2), (iv.mpf('0.2'), 1, 1)], iv.mpf('1e-12'), iv) - \
    maxsurv([(iv.mpf('0.75'), 1, 2), (iv.mpf('0.5'), 1, 1)], iv.mpf('1e-12'), iv)
print('ll iv at 1e-12:', mp.nstr(d.a, 8))
