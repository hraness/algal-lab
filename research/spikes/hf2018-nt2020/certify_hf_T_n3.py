"""Certificate: single T-transform hazard-rate claim for ORDINARY
PH/exponential mixtures fails at n=3.

Pattern audited (HF2018 machinery, transmitted via SKF2026 Thms 3.8/3.9
whose proof is deferred to "Theorem 3.4 of Hazra and Finkelstein (2018)"):
    [p;lam] in V_3 (rows antiordered), [q;gam] = [p;lam] M_T (single
    T-transform)  ==claimed==>  htilde_{p,lam}(u) <= htilde_{q,gam}(u)
    on u in (0,1)   (i.e. U >=hr V for the ordinary PH mixture).

Counterexample (exact rational instance found by search):
    p   = (1/8, 29/72, 17/36),  lam = (9, 5, 4)      in V_3
    T on columns (1,2) [0-indexed (0,1)], om = 13/20:
    q   = (2/9, 11/36, 17/36),  gam = (38/5, 32/5, 4)

htilde(u) = sum p_i lam_i u^{lam_i}/sum p_i u^{lam_i};  in w = u^{1/5} the
difference is rational with polynomial numerator; Sturm counts below.
"""
import sys
sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/mixture-audit")
import sympy as sp
from audit_lib import R, in_Vn

w = sp.Symbol("w", positive=True)   # u = w^5 clears the /5 exponents

p = (R(1, 8), R(29, 72), R(17, 36))
lam = (R(9), R(5), R(4))
q = (R(2, 9), R(11, 36), R(17, 36))
gam = (R(38, 5), R(32, 5), R(4))

print("== hypothesis checks ==")
print("p prob:", sum(p) == 1, " q prob:", sum(q) == 1)
print("(p,lam) in V3:", in_Vn(list(p), list(lam)))
print("T-check col0: q0 =", sp.nsimplify(R(13, 20) * p[0] + R(7, 20) * p[1]),
      "==", q[0], " gam0 =", sp.nsimplify(R(13, 20) * lam[0] + R(7, 20) * lam[1]),
      "==", gam[0])
print("T-check col1: q1 =", sp.nsimplify(R(7, 20) * p[0] + R(13, 20) * p[1]),
      "==", q[1], " gam1 =", sp.nsimplify(R(7, 20) * lam[0] + R(13, 20) * lam[1]),
      "==", gam[1])


def ht(pvec, lvec):
    # htilde in w: u^{lam_i} = w^{5 lam_i} (5*lam integer for our data)
    num = sum(pi * li * w ** int(5 * li) for pi, li in zip(pvec, lvec))
    den = sum(pi * w ** int(5 * li) for pi, li in zip(pvec, lvec))
    return num, den


np_, dp_ = ht(p, lam)
nq_, dq_ = ht(q, gam)
D = sp.expand(np_ * dq_ - nq_ * dp_)   # sign = this (dens > 0 on (0,1))
P = sp.Poly(D, w)
print("\n== D(w) numerator: sign of h_p - h_q on w in (0,1) ==")
print("deg:", P.degree(), " roots(0,1) [Sturm]:", P.count_roots(0, 1))
print("intervals:", P.intervals())
for v in (R(1, 4), R(1, 2), R(3, 4), R(7, 8), R(9, 10)):
    val = D.subs(w, v)
    print(f"  D({v}) = {val}  (sign {sp.sign(val)})")
print("\nClaimed: D <= 0 on (0,1).  Positive witnesses above refute it:")
print("D(1/4) =", D.subs(w, R(1, 4)), "> 0")
