"""Bounded sweeps around the BKB2022 T-transform lemmas (dict-poly version).

All quantities are integer-coefficient polynomials in a uniform variable u
(u = y^{1/L} or u = s^{1/L}, L = lcm of exponent denominators), represented
as dicts {int_exp: Fraction}. Evaluation/signs are exact rational arithmetic.
"""
import sys, random, itertools
from fractions import Fraction as F
from math import lcm
sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/mixture-audit")
from audit_lib import in_Vn, in_Wn

random.seed(11)
GRIDu = [F(1, 16), F(1, 8), F(1, 4), F(2, 5), F(1, 2), F(3, 4), F(7, 8), F(15, 16)]
GRIDu_gt1 = [F(5, 4), F(3, 2), F(2), F(3), F(4)]


def Tpair(v, j, k, om):
    v = list(v)
    vj = om * v[j] + (1 - om) * v[k]
    vk = (1 - om) * v[j] + om * v[k]
    v[j], v[k] = vj, vk
    return v


def rand_prob(n):
    xs = sorted(random.sample(range(1, 30), n - 1))
    cuts = [0] + xs + [30]
    return [F(cuts[i + 1] - cuts[i], 30) for i in range(n)]


def add(a, b):
    r = dict(a)
    for k, v in b.items():
        r[k] = r.get(k, F(0)) + v
    return {k: v for k, v in r.items() if v}


def mul(a, b):
    r = {}
    for ka, va in a.items():
        for kb, vb in b.items():
            k = ka + kb
            r[k] = r.get(k, F(0)) + va * vb
    return {k: v for k, v in r.items() if v}


def sub(a, b):
    return add(a, {k: -v for k, v in b.items()})


def peval(poly, u):
    return sum(c * u ** e for e, c in poly.items())


def poly_signs(poly, grid):
    return [(v - F(0)) for v in (peval(poly, q) for q in grid)]
    # sign via compare; Fraction supports <0


def sgn_list(poly, grid):
    return [1 if peval(poly, q) > 0 else (-1 if peval(poly, q) < 0 else 0)
            for q in grid]


def L_of(vecs):
    L = 1
    for v in vecs:
        for x in v:
            L = lcm(L, x.denominator)
    return L


print("=" * 72)
print("[1] Separable Psi sanity (Lemma 2.5 domain)")
print("=" * 72)
viol_ab = viol_sq = tot = 0
for _ in range(3000):
    n = 3
    gam = [F(random.randint(1, 30), random.randint(1, 9)) for _ in range(n)]
    p = [F(random.randint(1, 30), random.randint(1, 9)) for _ in range(n)]
    cls = "V" if in_Vn(gam, p) else ("W" if in_Wn(gam, p) else None)
    if not cls:
        continue
    j, k = sorted(random.sample(range(n), 2))
    om = F(random.randint(1, 19), 20)
    gB, pB = Tpair(gam, j, k, om), Tpair(p, j, k, om)
    d_ab = sum(g * pp for g, pp in zip(gam, p)) - sum(g * pp for g, pp in zip(gB, pB))
    if d_ab > 0:
        viol_ab += 1
    d_sq = sum(g * g + pp * pp for g, pp in zip(gam, p)) - \
        sum(g * g + pp * pp for g, pp in zip(gB, pB))
    if d_sq < 0:
        viol_sq += 1
    tot += 1
print(f"Psi=ab (<= version): {viol_ab}/{tot} violations of Psi_n(A)<=Psi_n(AT)")
print(f"Psi=a^2+b^2 (>= version): {viol_sq}/{tot} violations of Psi_n(A)>=Psi_n(AT)")

print()
print("=" * 72)
print("[2] htilde T-monotonicity violation counts (exact)")
print("=" * 72)
# htilde_{gam,p}(y): y = z^L clears exponents; N = sum p_i g_i z^{g_i L},
# D = sum p_i z^{g_i L};  sign(ht_A - ht_B) = sign(NA*DB - NB*DA), D > 0.
def ht_poly(gam, p, L):
    N, D = {}, {}
    for pi, gi in zip(p, gam):
        e = int(gi * L)
        N[e] = N.get(e, F(0)) + pi * gi
        D[e] = D.get(e, F(0)) + pi
    return N, D

violV = violW = nV = nW = 0
exV = exW = None
for _ in range(4000):
    n = 3
    gam = [F(random.randint(1, 20), random.randint(1, 5)) for _ in range(n)]
    p = rand_prob(n)
    j, k = sorted(random.sample(range(n), 2))
    om = F(random.randint(1, 19), 20)
    gB, pB = Tpair(gam, j, k, om), Tpair(p, j, k, om)
    L = L_of([gam, gB])
    Na, Da = ht_poly(gam, p, L)
    Nb, Db = ht_poly(gB, pB, L)
    diff = sub(mul(Na, Db), mul(Nb, Da))   # sign of ht_A - ht_B (z>0)
    if in_Vn(gam, p):
        nV += 1
        sg = sgn_list(diff, GRIDu)         # z in (0,1) ~ alpha>0 side
        if any(x < 0 for x in sg):
            violV += 1
            if exV is None:
                exV = (gam, p, gB, pB, om, sg, L)
    if in_Wn(gam, p):
        nW += 1
        sg = sgn_list(diff, GRIDu_gt1)     # z in (1,oo) ~ alpha<0 side
        if any(x > 0 for x in sg):
            violW += 1
            if exW is None:
                exW = (gam, p, gB, pB, om, sg, L)
print(f"V_3 claim ht_A>=ht_B on (0,1): {violV}/{nV} violating")
if exV: print("   e.g.", exV)
print(f"W_3 claim ht_A<=ht_B on (1,oo): {violW}/{nW} violating")
if exW: print("   e.g.", exW)

print()
print("=" * 72)
print("[3] Ordinary-mixture REVERSED hazard under single T-transform")
print("=" * 72)
# r = N/D, N = sum p_i lam_i s^{lam_i}, D = 1 - sum p_i s^{lam_i}, s=u^L
def rh_poly(lam, p, L):
    N, D = {}, {0: F(1)}
    for pi, li in zip(p, lam):
        e = int(li * L)
        N[e] = N.get(e, F(0)) + pi * li
        D[e] = D.get(e, F(0)) - pi
    return N, D

viol = {"V_geq": 0, "V_leq": 0, "W_geq": 0, "W_leq": 0}
cnt = {"V": 0, "W": 0}
ex = {"V_geq": None, "V_leq": None, "W_geq": None, "W_leq": None}
for _ in range(6000):
    n = 3
    lam = [F(random.randint(1, 24), random.randint(1, 6)) for _ in range(n)]
    p = rand_prob(n)
    j, k = sorted(random.sample(range(n), 2))
    om = F(random.randint(1, 19), 20)
    lB, pB = Tpair(lam, j, k, om), Tpair(p, j, k, om)
    cls = "V" if in_Vn(lam, p) else ("W" if in_Wn(lam, p) else None)
    if not cls:
        continue
    cnt[cls] += 1
    L = L_of([lam, lB])
    Na, Da = rh_poly(lam, p, L)
    Nb, Db = rh_poly(lB, pB, L)
    diff = sub(mul(Na, Db), mul(Nb, Da))
    sg = sgn_list(diff, GRIDu)
    if any(x < 0 for x in sg):
        viol[cls + "_geq"] += 1
        if ex[cls + "_geq"] is None:
            ex[cls + "_geq"] = (lam, p, lB, pB, om, sg)
    if any(x > 0 for x in sg):
        viol[cls + "_leq"] += 1
        if ex[cls + "_leq"] is None:
            ex[cls + "_leq"] = (lam, p, lB, pB, om, sg)
print(f"V_3: r_A-r_B<0 seen {viol['V_geq']}/{cnt['V']}; r_A-r_B>0 seen {viol['V_leq']}/{cnt['V']}")
print(f"W_3: r_A-r_B<0 seen {viol['W_geq']}/{cnt['W']}; r_A-r_B>0 seen {viol['W_leq']}/{cnt['W']}")
for kk, vv in ex.items():
    if vv:
        print("  e.g.", kk, vv)

print()
print("=" * 72)
print("[4] Ordinary-mixture HAZARD rate under single T-transform")
print("=" * 72)
def h_poly(lam, p, L):
    N, D = {}, {}
    for pi, li in zip(p, lam):
        e = int(li * L)
        N[e] = N.get(e, F(0)) + pi * li
        D[e] = D.get(e, F(0)) + pi
    return N, D

viol = {"V_geq": 0, "V_leq": 0, "W_geq": 0, "W_leq": 0}
cnt = {"V": 0, "W": 0}
ex2 = {"V_geq": None, "V_leq": None, "W_geq": None, "W_leq": None}
for _ in range(6000):
    n = 3
    lam = [F(random.randint(1, 24), random.randint(1, 6)) for _ in range(n)]
    p = rand_prob(n)
    j, k = sorted(random.sample(range(n), 2))
    om = F(random.randint(1, 19), 20)
    lB, pB = Tpair(lam, j, k, om), Tpair(p, j, k, om)
    cls = "V" if in_Vn(lam, p) else ("W" if in_Wn(lam, p) else None)
    if not cls:
        continue
    cnt[cls] += 1
    L = L_of([lam, lB])
    Na, Da = h_poly(lam, p, L)
    Nb, Db = h_poly(lB, pB, L)
    diff = sub(mul(Na, Db), mul(Nb, Da))
    sg = sgn_list(diff, GRIDu)
    if any(x < 0 for x in sg):
        viol[cls + "_geq"] += 1
        if ex2[cls + "_geq"] is None:
            ex2[cls + "_geq"] = (lam, p, lB, pB, om, sg)
    if any(x > 0 for x in sg):
        viol[cls + "_leq"] += 1
        if ex2[cls + "_leq"] is None:
            ex2[cls + "_leq"] = (lam, p, lB, pB, om, sg)
print(f"V_3: h_A-h_B<0 seen {viol['V_geq']}/{cnt['V']}; h_A-h_B>0 seen {viol['V_leq']}/{cnt['V']}")
print(f"W_3: h_A-h_B<0 seen {viol['W_geq']}/{cnt['W']}; h_A-h_B>0 seen {viol['W_leq']}/{cnt['W']}")
for kk, vv in ex2.items():
    if vv:
        print("  e.g.", kk, vv)
