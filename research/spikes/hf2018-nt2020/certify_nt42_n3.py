"""Certificate: n=3 ordinary PH/exponential mixture hazard-rate ordering
under majorization FAILS -- resolves the n>2 question left open by
Hazra-Finkelstein 2018 (Sec. 4), Nadeb-Torabi 2020 (Sec. 4) and echoed in
SAF2022 Rem 6.18, in the negative, for ordinary mixtures (alpha_i = 1).

Instance (found by exact search):
    p   = (39/86, 18/43, 11/86)   (decreasing)
    lam = (4, 6, 9), gam = (4, 7, 8)   (increasing)
Hypotheses (all verified exactly below):
    (p,lam), (p,gam) in U_3  (p dec vs lam,gam inc = antiordered)
    lam ~^m gam  (majorization: 4<=4, 4+6=10<=4+7=11, totals 19=19)
Conclusion claimed (NT Thm 4.2 analog for n=3 / SAF Cor 6.21 pattern):
    h_{p,lam}(t) <= h_{p,gam}(t) for all t>=0
where h_{p,lam}(t) = sum p_i lam_i e^{-lam_i t} / sum p_i e^{-lam_i t}.

With s = e^{-t} in (0,1): d(s) = h_lam - h_gam is a rational function of s;
its numerator P(s) is a degree-19 polynomial. Sturm count + rational
witnesses certify a sign change on (0,1): the hazard rates cross, so the
mixtures are incomparable in the hr order.
"""
import sys
sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/mixture-audit")
import sympy as sp
from audit_lib import R, majorizes, in_Un

s = sp.Symbol("s", positive=True)

p = (R(39, 86), R(18, 43), R(11, 86))
lam = (R(4), R(6), R(9))
gam = (R(4), R(7), R(8))

print("== hypothesis checks (exact) ==")
print("p prob:", sum(p) == 1, "p dec:", p[0] > p[1] > p[2])
print("lam inc:", lam[0] < lam[1] < lam[2], "gam inc:", gam[0] < gam[1] < gam[2])
print("(p,lam) in U3:", in_Un(list(p), list(lam)))
print("(p,gam) in U3:", in_Un(list(p), list(gam)))
print("lam majorizes gam:", majorizes(list(lam), list(gam)))


def h(pvec, lvec):
    num = sum(pi * li * s ** int(li) for pi, li in zip(pvec, lvec))
    den = sum(pi * s ** int(li) for pi, li in zip(pvec, lvec))
    return sp.cancel(num / den)


d = sp.cancel(sp.together(h(p, lam) - h(p, gam)))
num, den = sp.fraction(d)
num = sp.expand(num); den = sp.expand(den)
P = sp.Poly(num, s)
print("\n== d(s) = h_lam - h_gam ==")
print("num deg:", P.degree(), " den sign on (0,1): den(0)=", den.subs(s, 0),
      " denroots(0,1):", sp.Poly(den, s).count_roots(0, 1))
print("num roots in (0,1) [Sturm]:", P.count_roots(0, 1))
print("num intervals:", P.intervals())

for v in (R(1, 8), R(1, 4), R(1, 2), R(3, 4), R(7, 8), R(15, 16)):
    print(f"  d({v}) = {d.subs(s, v)}  sign {sp.sign(d.subs(s, v))}")

print("\nBoundary behaviour:")
print("d(1) =", sp.simplify(d.subs(s, 1)), " (t=0: weighted means equal",
      sum(pi * li for pi, li in zip(p, lam)) ==
      sum(pi * gi for pi, gi in zip(p, gam)), ")")
