"""CERT F: lr-ordering claim shape under a single T-transform (frozen column).

Extends certify_batch.py (CERTs A-E): the likelihood-ratio order requires
f_X/f_Y monotone; for ordinary exponential mixtures the density ratio is a
ratio of sums, so the frozen column invalidates the lift there too.

Instance = CERT B: p=(1/8,29/72,17/36), lam=(9,5,4) in V_3;
T on columns 1,2 with omega=13/20 gives q=(2/9,11/36,17/36), gam=(38/5,32/5,4).
u = e^{-t} in (0,1); f(t) proportional to sum p_i lam_i u^{lam_i}.

Result: d/du [f_p/f_q] numerator has exactly 1 Sturm root on (0,1);
R' changes sign + -> - between u=1/4 and u=1/2 => ratio NOT monotone
=> lr ordering fails. Certified: sympy Rational + Poly.count_roots.
"""
import sys
sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/mixture-audit")
import sympy as sp
from audit_lib import R, in_Vn

p2 = (R(1, 8), R(29, 72), R(17, 36))
lam2 = (R(9), R(5), R(4))
q2 = (R(2, 9), R(11, 36), R(17, 36))
gam2 = (R(38, 5), R(32, 5), R(4))
om = R(13, 20)
print("V3:", in_Vn(list(p2), list(lam2)),
      "| T-check:", om * p2[0] + (1 - om) * p2[1] == q2[0],
      om * lam2[0] + (1 - om) * lam2[1] == gam2[0],
      "| frozen col:", p2[2] == q2[2] and lam2[2] == gam2[2])

u = sp.Symbol("u", positive=True)


def dens(pvec, lvec):
    return sum(pi * li * u ** int(li) for pi, li in zip(pvec, lvec))


Rratio = sp.cancel(dens(p2, lam2) / dens(q2, gam2))
dR = sp.cancel(sp.together(sp.diff(Rratio, u)))
num, den = sp.fraction(dR)
P = sp.Poly(sp.expand(num), u)
print("deg", P.degree(), "| Sturm roots on (0,1):", P.count_roots(0, 1),
      "| den roots on (0,1):", sp.Poly(sp.expand(den), u).count_roots(0, 1))
for v in (R(1, 4), R(1, 2)):
    print("  R'(%s) sign %s" % (v, sp.sign(dR.subs(u, v))))
print("=> density ratio non-monotone: lr ordering FAILS at claim shape")
