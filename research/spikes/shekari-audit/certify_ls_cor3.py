"""Two further exact certificates.

C1. LS specialization (Remark 11(I)(i): BKB2022 Thm 2 as special case).
Ordinary exponential mixture with scale gam_i=1/m_i (rates lam_i=m_i);
A in A_3, single T on columns (1,3), omega=3/20:
    gam = (1/7, 1/2, 1/2),  p = (1/3,1/3,1/3)   in A_3 (boundary)
    gam* = (25/56, 1/2, 11/56), p* = p
    lam = (7,2,2), lam* = (56/25, 2, 56/11)
    h_A - h_B in z = s^{1/275}  (L = lcm(25,11) = 275):  -- big; use s=w
    Actually lam* denominators {25,11}: lcm 275. z = s^{1/275}.
    h(s) = sum p_i lam_i s^{lam_i} / sum p_i s^{lam_i}.
In z: exponents 275*lam_i all integers.

C2. Corollary 3 quick sweep: st-order under row majorization:
(γ,π),(γ*,π*) in A_n, γ >=^m γ*, π >=^m π*  =>  P_n <=_st Q_n
i.e. sum p_i u^{g_i} >= sum p*_i u^{g*_i} on u in (0,1) for PHR.
"""
import sys, random
import sympy as sp
from sympy import Rational as R
from fractions import Fraction as Fr
from math import gcd

z = sp.Symbol("z", positive=True)

# ---------------- C1 ----------------------------------------------------
print("=== C1: LS-exponential specialization of Thm 11 ===")
gam = (R(1, 7), R(1, 2), R(1, 2))
p = (R(1, 3), R(1, 3), R(1, 3))
gs = (R(25, 56), R(1, 2), R(11, 56))
ps = p
lam = tuple(1 / g for g in gam)
lams = tuple(1 / g for g in gs)
print("A in A_3:", all((gam[i]-gam[j])*(p[i]-p[j]) <= 0 for i in range(3) for j in range(3)))
print("B in A_3:", all((gs[i]-gs[j])*(ps[i]-ps[j]) <= 0 for i in range(3) for j in range(3)))
w = R(3, 20); i, j = 0, 2
print("B==AT:", gs[i] == w*gam[i]+(1-w)*gam[j], gs[j] == (1-w)*gam[i]+w*gam[j])
print("lam =", lam, " lam* =", lams)
L = 275  # lcm(25,11,1)

def h(p_, la_):
    num = sum(pi * li * z ** sp.nsimplify(L * li) for pi, li in zip(p_, la_))
    den = sum(pi * z ** sp.nsimplify(L * li) for pi, li in zip(p_, la_))
    return sp.cancel(num / den)

d = sp.cancel(sp.together(h(p, lam) - h(ps, lams)))
num, den = sp.fraction(d)
num, den = sp.expand(num), sp.expand(den)
print("numerator deg:", sp.degree(num, z), "denominator deg:", sp.degree(den, z))
print("Sturm roots num in (0,1):", sp.Poly(num, z).count_roots(0, 1))
print("Sturm roots den in (0,1):", sp.Poly(den, z).count_roots(0, 1))
for v in [R(1, 2), R(7, 8), R(9, 10), R(15, 16), R(19, 20), R(99, 100)]:
    dv = sp.cancel(d.subs(z, v))
    print(f"  z={v}: sign {sp.sign(dv)}")
# in s = z^275 terms:
for v in [R(1, 2), R(9, 10), R(19, 20)]:
    print(f"   s = {v}^275 ~ {sp.N(v**275,4)}")


# ---------------- C2 ----------------------------------------------------
print("\n=== C2: Corollary 3 (st order, row majorization, PHR) ===")
u = sp.Symbol("u", positive=True)
GRID = [Fr(1, 16), Fr(1, 8), Fr(1, 4), Fr(2, 5), Fr(1, 2), Fr(3, 4),
        Fr(7, 8), Fr(15, 16)]


def inc(v):
    return tuple(sorted(v))


def maj(x, y):
    xs, ys = inc(x), inc(y)
    return sum(xs) == sum(ys) and all(sum(xs[:k]) <= sum(ys[:k])
                                      for k in range(1, len(xs)))


def in_An(r1, r2):
    n = len(r1)
    if not (all(x > 0 for x in r1) and all(Fr(0) < y < Fr(1) for y in r2)):
        return False
    return all((r1[i] - r1[j]) * (r2[i] - r2[j]) <= 0
               for i in range(n) for j in range(n))


def sf_at(p_, g_, uv):
    return sum(pi * uv ** gi for pi, gi in zip(p_, g_))


rng = random.Random(13)
adm = 0
viol = 0
ex = None
for _ in range(40000):
    n = 3
    gam_sorted = sorted(Fr(rng.randint(1, 24), rng.choice([1, 2, 4]))
                        for _ in range(n))
    gss = sorted(Fr(rng.randint(1, 24), rng.choice([1, 2, 4]))
                 for _ in range(n))
    # gamma >=^m gamma*: need equal sums
    if sum(gam_sorted) != sum(gss):
        continue
    if not maj(gam_sorted, gss):
        continue
    # p >=^m p*: two prob vectors
    pa = sorted((Fr(rng.randint(1, 40)) for _ in range(n)))
    pb = sorted((Fr(rng.randint(1, 40)) for _ in range(n)))
    if not (maj(pa, pb)):
        continue
    p = tuple(x / sum(pa) for x in pa)
    pp = tuple(x / sum(pb) for x in pb)
    # A_n membership: rows (gam, p): antiordered columns.
    # permute gam vs p: gam increasing => p must be decreasing: take gam
    # paired anti-monotone with p.
    gam = tuple(sorted(gam_sorted))
    gam = tuple(gam[i] for i in sorted(range(n), key=lambda k: -p[k])) \
        if False else gam
    # simplest: require gam inc & p dec (one valid arrangement):
    gam = tuple(sorted(gam_sorted))
    p = tuple(sorted(p, reverse=True))
    pp_arr = tuple(sorted(pp, reverse=True))  # keep same pairing style
    if not (in_An(gam, p) and in_An(gss, pp_arr)):
        continue
    adm += 1
    dens = [x.denominator for x in gam] + [x.denominator for x in gss]
    L = 1
    for dd in dens:
        L = L * dd // gcd(L, dd)
    bad = False
    for v in GRID:
        dv = sum(pi * v ** (L * gi) for pi, gi in zip(p, gam)) - \
             sum(pi * v ** (L * gi) for pi, gi in zip(pp_arr, gss))
        if dv < 0:   # claim P<=_st Q: SF_A >= SF_B
            bad = True
            break
    if bad:
        viol += 1
        if ex is None:
            ex = (gam, p, gss, pp_arr)
print("Cor 3 (PHR st-order): admissible:", adm, " violating:", viol)
print("EX:", ex)
