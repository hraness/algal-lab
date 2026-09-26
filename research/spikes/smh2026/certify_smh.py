"""Certificate script for SMH2026 (Sahoo-Misra-Hazra, "On stochastic
comparisons of mixtures of distributions", Statistics, DOI
10.1080/02331888.2026.2661806, online 2026-04-28).

STATUS: paper closed access (T&F; Unpaywall: closed; no arXiv/repo/figshare
copy; 0 citing papers). Everything below is audited AT CLAIM SHAPE: the
claims tested are the canonical n-component ordering statements of the
cited machinery (HF2018 / NT2020 / BKZ2021 / Misra-Naqvi 2018), which the
abstract says the paper "generalizes". Each certificate is marked.

WHY ONE POLYNOMIAL CERTIFIES ALL alpha>0
-----------------------------------------
alpha-mixture of survival functions (AES2019, cited by SMH2026):
    Fbar_a(t) = ( sum_i p_i Fbar_i(t)^a )^{1/a}.
With exponential components Fbar_i = exp(-lam_i t):
    h_a(t) = f_a/Fbar_a = sum_i p_i lam_i Fbar_i(t)^a / sum_i p_i Fbar_i(t)^a
                          = sum_i p_i lam_i u^{lam_i} / sum_i p_i u^{lam_i},
    u = exp(-a t) in (0,1)  for a>0, t>0.
So h_a(t) = htilde(u) with the SAME polynomial difference for every a>0:
a sign change of htilde on u in (0,1) refutes the hr-ordering claim for
all a>0 simultaneously (a=1 included = ordinary mixture).

alpha-mixture of CDFs (Shojaee-Momeni 2023, cited by SMH2026):
    F_a(t) = ( sum_i p_i F_i(t)^a )^{1/a}, rh rate
    r_a(t) = f_a/F_a = sum_i p_i r_i(t) F_i(t)^a / sum_i p_i F_i(t)^a.
Power-function components F_i(t) = t^{lam_i} on (0,1):  r_i = lam_i/t,
    r_a(t) = (1/t) * sum_i p_i lam_i x^{lam_i} / sum_i p_i x^{lam_i},
    x = t^a in (0,1) for a>0. Same bracket; factor 1/t > 0 -> same sign
certificate refutes the rh-ordering claim for all a>0.

CLAIM SHAPE A (U_n + majorization; NT2020 Thm 4.2 / HF2018 pattern):
    (p,lam),(p,gam) in U_n, lam majorizes gam  ==>  h_a^lam <= h_a^gam.
CLAIM SHAPE B (V_n + single T-transform; the frozen-column lift):
    [p;lam] in V_n, [q;gam] = [p;lam] M_T  ==>  hr ordering holds.
Both are FALSE at n=3, certified below; the SAME instances refute the rh
claims for the CDF-mixture (power-function components).
"""
import sys
sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/mixture-audit")
import sympy as sp
from audit_lib import R, majorizes, in_Un, in_Vn

u = sp.Symbol("u", positive=True)


def ht(pvec, lvec):
    """htilde(u) = sum p_i lam_i u^{lam_i} / sum p_i u^{lam_i} (= h_a for
    exp components with u=e^{-a t}; = t*r_a for power-function CDF
    components with x=t^a)."""
    num = sum(pi * li * u ** int(li) for pi, li in zip(pvec, lvec))
    den = sum(pi * u ** int(li) for pi, li in zip(pvec, lvec))
    return sp.cancel(num / den)


print("=" * 72)
print("CERT A: claim shape (p,lam),(p,gam) in U_3, lam >maj gam => hr ordered")
print("        holds for alpha-mixture SF (all a>0) -- REFUTED at n=3")
print("=" * 72)
p = (R(39, 86), R(18, 43), R(11, 86))
lam = (R(4), R(6), R(9))
gam = (R(4), R(7), R(8))
print("hypotheses: p prob:", sum(p) == 1,
      "| (p,lam) U3:", in_Un(list(p), list(lam)),
      "| (p,gam) U3:", in_Un(list(p), list(gam)),
      "| lam >maj gam:", majorizes(list(lam), list(gam)),
      "| lam inc:", lam[0] < lam[1] < lam[2], "gam inc:", gam[0] < gam[1] < gam[2])
d = sp.cancel(sp.together(ht(p, lam) - ht(p, gam)))
num, den = sp.fraction(d)
num, den = sp.expand(num), sp.expand(den)
P = sp.Poly(num, u)
print("d(u)=h_lam-h_gam: num deg", P.degree(),
      "| den roots(0,1):", sp.Poly(den, u).count_roots(0, 1),
      "| num roots(0,1) [Sturm]:", P.count_roots(0, 1))
for v in (R(1, 2), R(3, 4), R(7, 8)):
    print(f"  d({v}) = {d.subs(u, v)}  sign {sp.sign(d.subs(u, v))}")
print("=> ONE interior root: hazards cross; claim fails for EVERY a>0,")
print("   incl. a=1 (ordinary mixture). Same bracket => rh claim for the")
print("   CDF-mixture fails too (power-function components, x=t^a).")
print("-- a<0 domain (u in (1,inf)):")
for v in (R(3, 2), R(2), R(4)):
    print(f"  d({v}) = {d.subs(u, v)}  sign {sp.sign(d.subs(u, v))}",
          " <- sign change on (1,inf) would cover a<0 too")

print()
print("=" * 72)
print("CERT B: claim shape [p;lam] in V_3, [q;gam]=[p;lam] M_T => hr ordered")
print("        (the frozen-column lift) -- REFUTED at n=3, all a>0")
print("=" * 72)
p2 = (R(1, 8), R(29, 72), R(17, 36))
lam2 = (R(9), R(5), R(4))
q2 = (R(2, 9), R(11, 36), R(17, 36))
gam2 = (R(38, 5), R(32, 5), R(4))
om = R(13, 20)
print("hypotheses: p,q prob:", sum(p2) == 1, sum(q2) == 1,
      "| (p,lam) V3:", in_Vn(list(p2), list(lam2)))
print("T-check:", sp.nsimplify(om * p2[0] + (1 - om) * p2[1]) == q2[0],
      sp.nsimplify((1 - om) * p2[0] + om * p2[1]) == q2[1],
      sp.nsimplify(om * lam2[0] + (1 - om) * lam2[1]) == gam2[0],
      sp.nsimplify((1 - om) * lam2[0] + om * lam2[1]) == gam2[1],
      "| col2 frozen: p2[2]==q2[2]:", p2[2] == q2[2], " lam2[2]==gam2[2]:",
      lam2[2] == gam2[2])
# exponents 5*lam integer via w = u^{1/5}
w = sp.Symbol("w", positive=True)


def ht5(pvec, lvec):
    num = sum(pi * li * w ** int(5 * li) for pi, li in zip(pvec, lvec))
    den = sum(pi * w ** int(5 * li) for pi, li in zip(pvec, lvec))
    return num, den


np_, dp_ = ht5(p2, lam2)
nq_, dq_ = ht5(q2, gam2)
D = sp.expand(np_ * dq_ - nq_ * dp_)
P2 = sp.Poly(D, w)
print("D(w) sign of h_p - h_q on w in (0,1): deg", P2.degree(),
      "| roots(0,1) [Sturm]:", P2.count_roots(0, 1))
for v in (R(1, 4), R(1, 2), R(7, 8), R(9, 10)):
    print(f"  D({v}) sign {sp.sign(D.subs(w, v))}")
print("=> crossing on (0,1): frozen-column lift fails for every a>0.")
print("   The untouched third column sits inside both numerator and")
print("   denominator of the ratio -- the additive-lift lemma cannot apply.")

print()
print("=" * 72)
print("CERT C (symbolic check): CDF-mixture rh bracket = SF-mixture hr bracket")
print("=" * 72)
a, t = sp.symbols("a t", positive=True)
pi_, li_ = sp.symbols("p l", positive=True)
# power-function F(t)=t^lam on (0,1): verify r_a = (1/t)*htilde(t^a)
n = 3
pp = [sp.symbols(f"p{i}", positive=True) for i in range(n)]
ll = [sp.symbols(f"l{i}", positive=True) for i in range(n)]
Fi = [t ** ll[i] for i in range(n)]
Fa = sum(pp[i] * Fi[i] ** a for i in range(n)) ** (1 / a)
ra = sp.diff(Fa, t) / Fa
bracket = sum(pp[i] * ll[i] * (t ** a) ** ll[i] for i in range(n)) / \
    sum(pp[i] * (t ** a) ** ll[i] for i in range(n))
print("r_a - (1/t)*bracket simplifies to:",
      sp.simplify(ra - bracket / t) == 0, "(expected True)")
print("=> sign of r_a difference = sign of htilde difference at x=t^a.")
