"""Claim-shape certificates for NT2022 (Nadeb-Torabi, CSTM 51(10):3104-3119;
online 9 Jul 2020; DOI 10.1080/03610926.2020.1788082). Text is closed access;
claims audited at the shapes transmitted by SAF2022, SPBB2026, GY2024,
BKKA2024, BKF2024, BTDK.

Exact arithmetic: /Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python
(sympy Rational; Sturm Poly.count_roots + exact rational witnesses).

Model: ordinary/PHR mixture, exponential baseline Fbar_i = exp(-lam_i t):
    h(t) = sum p_i lam_i s^{lam_i} / sum p_i s^{lam_i},  s = e^{-t} in (0,1).
PHR Fbar_i = Fbar^{lam_i} gives the same bracket in s = Fbar(t); alpha-mixture
and Weibull subfamily readings are the same polynomial (see suspect-batch).

SHAPE L  (lambda-side vector majorization, the SAF2022 transmission):
    (p,lam),(p,gam) in U_3, lam >=^m gam  =>  h_lam <= h_gam.
    = CERT A of suspect-batch / Certificate 1 of hf2018-nt2020. FAILS at n=3.
    NT2022 does NOT claim it (SAF2022 Rem 6.18: NT section 4 leaves n>2 open);
    the certificate resolves the stated open problem negatively.

SHAPE P  (pi-side vector majorization, the ambiguous SPBB2026 Rem 7
    transmission): lam fixed, (lam,pi),(lam,pi*) in A_n (antiordered,
    SPBB Def. 4 = audit_lib U_n), pi >=^m pi*  =>  h_pi vs h_pi* ordered.
    SPBB2026 Thms 5/6 assert this at general n for DSFM/DDFM models and map
    NT Thms 3.1/3.2/Rem 3.2 into them; NT's own n-scope is unretrieved.
    Tested at n=2 (control) and n=3.
"""
import sys
sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/mixture-audit")
import itertools
import sympy as sp
from audit_lib import R, majorizes, in_Un

u = sp.Symbol("u", positive=True)


def bracket(pvec, lvec):
    num = sum(pi * li * u ** int(li) for pi, li in zip(pvec, lvec))
    den = sum(pi * u ** int(li) for pi, li in zip(pvec, lvec))
    return sp.cancel(num / den)


def roots(d):
    num, den = sp.fraction(sp.cancel(sp.together(d)))
    P = sp.Poly(sp.expand(num), u)
    return P.degree(), P.count_roots(0, 1)


def interior_roots_and_crossing(d):
    """Sign change across rational probes (the certificate itself), plus a
    Sturm count on the endpoint-stripped numerator."""
    num, den = sp.fraction(sp.cancel(sp.together(d)))
    signs = {sp.sign(num.subs(u, v)) for v in (R(1, 4), R(1, 2), R(9, 10))}
    signs.discard(0)
    P = sp.Poly(sp.expand(num), u)
    e = sp.factor_list(sp.expand(num))[1]
    keep = 1
    for base, mult in e:
        if base.subs(u, 0) != 0 and base.subs(u, 1) != 0:
            keep *= base ** mult
    n_int = sp.Poly(sp.expand(keep), u).count_roots(0, 1)
    return P.degree(), n_int, len(signs) > 1, signs


print("=" * 72)
print("CERT A rerun (SHAPE L): n=3 lambda-majorization hr claim shape")
print("p dec, lam,gam inc; lam >=m gam; exp/PHR/alpha-mixture reading")
print("=" * 72)
p = (R(39, 86), R(18, 43), R(11, 86))
lam = (R(4), R(6), R(9))
gam = (R(4), R(7), R(8))
print("U3:", in_Un(list(p), list(lam)), in_Un(list(p), list(gam)),
      "| lam >=m gam:", majorizes(list(lam), list(gam)))
d = bracket(p, lam) - bracket(p, gam)
print("deg, roots(0,1]:", roots(d))
for v in (R(1, 2), R(3, 4)):
    print("  d(%s) = %s  sign %s" % (v, d.subs(u, v), sp.sign(d.subs(u, v))))

print()
print("=" * 72)
print("SHAPE P control (n=2): lam fixed, pi >=m pi* with A_2 arrangement")
print("n=2 prob vectors: pi=(a,1-a), pi*=(b,1-b); majorization is scalar")
print("=" * 72)
adm2 = 0
viol2 = 0
first2 = None
pos_dir = 0
neg_dir = 0
for lam2 in [(R(1), R(2)), (R(1), R(3)), (R(2), R(5)), (R(1), R(4))]:
    for anum in range(1, 10):
        for bnum in range(1, 10):
            a, b = R(anum, 10), R(bnum, 10)
            pi, pis = (a, 1 - a), (b, 1 - b)
            if not (majorizes(list(pi), list(pis)) or majorizes(list(pis), list(pi))):
                continue
            if not (in_Un(list(lam2), list(pi)) and in_Un(list(lam2), list(pis))):
                continue
            adm2 += 1
            dd = bracket(pi, lam2) - bracket(pis, lam2)
            deg, rts, cross, signs = interior_roots_and_crossing(dd)
            if cross:
                viol2 += 1
                if first2 is None:
                    first2 = (lam2, pi, pis, deg, rts, signs)
            elif signs == {1}:
                pos_dir += 1
            elif signs == {-1}:
                neg_dir += 1
print("n=2 admissible:", adm2, "| TRUE sign-change crossings:", viol2,
      "| first:", first2)
print("n=2 direction split: d>0 throughout:", pos_dir,
      "| d<0 throughout:", neg_dir,
      "(d := h_pi - h_pi* with pi >=m pi*)")

print()
print("=" * 72)
print("SHAPE P at n=3: lam fixed inc, pi,pi* prob, (lam,pi),(lam,pi*) in A_3")
print("(antiordered => pi decreasing), pi >=m pi*; look for a Sturm root")
print("=" * 72)
found = []
adm3 = 0
grid_pi = [R(i, 8) for i in range(1, 8)]
lams = [tuple(R(i) for i in L) for L in
        itertools.combinations_with_replacement(range(1, 8), 3)]
pis = [pt for pt in itertools.product(grid_pi, repeat=2)]
for L in lams:
    for (a, b) in pis:
        pi = (a, b, 1 - a - b)
        if pi[2] <= 0:
            continue
        for (c, e) in pis:
            pis_ = (c, e, 1 - c - e)
            if pis_[2] <= 0:
                continue
            if not majorizes(list(pi), list(pis_)):
                continue
            if not (in_Un(list(L), list(pi)) and in_Un(list(L), list(pis_))):
                continue
            adm3 += 1
            dd = bracket(pi, L) - bracket(pis_, L)
            numd, _ = sp.fraction(sp.cancel(sp.together(dd)))
            s1 = sp.sign(numd.subs(u, R(1, 4)))
            s2 = sp.sign(numd.subs(u, R(1, 2)))
            s3 = sp.sign(numd.subs(u, R(9, 10)))
            if len({s1, s2, s3} - {0}) <= 1:
                continue
            P = sp.Poly(sp.expand(numd), u)
            keep = 1
            for base, mult in sp.factor_list(sp.expand(numd))[1]:
                if base.subs(u, 0) != 0 and base.subs(u, 1) != 0:
                    keep *= base ** mult
            rts = sp.Poly(sp.expand(keep), u).count_roots(0, 1)
            if rts >= 1:
                found.append((L, pi, pis_, P.degree(), rts, s1, s2, s3))
print("n=3 admissible:", adm3, "| crossing pairs:", len(found))
for f in found[:8]:
    print("  lam=%s pi=%s pi*=%s deg=%s introots=%s signs=(%s,%s,%s)" % f)
if found:
    L, pi, pis_, deg, rts, s1, s2, s3 = found[0]
    print()
    print("CERT P certificate (first instance):")
    dd = sp.cancel(sp.together(bracket(pi, L) - bracket(pis_, L)))
    num, den = sp.fraction(dd)
    print("  lam =", L, "| pi =", pi, "| pi* =", pis_)
    print("  pi >=m pi*:", majorizes(list(pi), list(pis_)),
          "| A_3:", in_Un(list(L), list(pi)), in_Un(list(L), list(pis_)))
    print("  num deg:", sp.Poly(sp.expand(num), u).degree(),
          "| Sturm roots (0,1]:", sp.Poly(sp.expand(num), u).count_roots(0, 1),
          "| interior roots:", rts)
    for v in (R(1, 4), R(1, 2), R(9, 10)):
        print("  d(%s) = %s" % (v, dd.subs(u, v)))
