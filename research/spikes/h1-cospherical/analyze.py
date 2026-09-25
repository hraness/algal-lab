#!/usr/bin/env python3
"""analyze.py -- decompose E(n) samples from esamp.

Streams <prefix>.spheres.tsv (a b1 b2 b3 c det k per accepted sample) and
<prefix>.extras.tsv (point lists for k>=1), and reports:
  * E(n), SE (batch means), P(k>=1), histogram, tail share
  - dyadic denominator decomposition by a (primitive |p|^2 coefficient) and by
    center denominator Dc = 2a/gcd(2a,b1,b2,b3)  [= lcm denom of center coords]
  - radius decomposition R/n
  - distinct-sphere view: multiplicity, concentration
  - structure of sphere point sets (axis-plane load, max coplanar subset)

Usage: analyze.py n prefix [max_coplanar_t]
"""
import sys, math
from math import gcd, isqrt
from collections import defaultdict, Counter

n = int(sys.argv[1])
prefix = sys.argv[2]
COPMAX = int(sys.argv[3]) if len(sys.argv) > 3 else 30  # enumerate triples for tot<=COPMAX


def bucket(x):
    return x.bit_length()  # dyadic: 2^(b-1) <= x < 2^b


m = 0
sumk = 0.0
sumsq = 0.0
hist = Counter()                    # k -> count
bk_a = defaultdict(lambda: [0, 0.0])   # log2 bucket of a -> [count, sumk]
bk_dc = defaultdict(lambda: [0, 0.0])
bk_det = defaultdict(lambda: [0, 0.0])
bk_R = defaultdict(lambda: [0, 0.0])   # radius/n bucket
spheres = {}                        # (a,b1,b2,b3,c) -> [mult, k]
batches = []                        # for batch SE
cur_b, cur_bn, B = 0.0, 0, None
BATCH = 64

with open(prefix + ".spheres.tsv") as f:
    lines = []
    for line in f:
        if line.startswith('#'):
            continue
        lines.append(line)
m_all = len(lines)
NB = max(1, m_all // BATCH)
for line in lines:
    p = line.split()
    a, b1, b2, b3, c = int(p[0]), int(p[1]), int(p[2]), int(p[3]), int(p[4])
    det, k = int(p[5]), int(p[6])
    m += 1
    sumk += k
    sumsq += k * k
    hist[k] += 1
    g = gcd(2 * a, gcd(b1, gcd(b2, b3)))
    dc = 2 * a // g                    # center denominator (lcm of coord denoms)
    # R^2 = (b^2 - 4ac)/(4a^2) ; R/n ratio bucket
    R2 = (b1 * b1 + b2 * b2 + b3 * b3 - 4 * a * c) / (4.0 * a * a)
    rn = math.sqrt(R2) / n if R2 > 0 else 0.0
    ba, bd, bt = bucket(a), bucket(dc), bucket(det)
    bk_a[ba][0] += 1; bk_a[ba][1] += k
    bk_dc[bd][0] += 1; bk_dc[bd][1] += k
    bk_det[bt][0] += 1; bk_det[bt][1] += k
    rb = max(0, int(round(math.log2(rn)))) if rn > 0 else 0
    rb = max(-6, min(6, rb))
    bk_R[rb][0] += 1; bk_R[rb][1] += k
    key = (a, b1, b2, b3, c)
    e = spheres.get(key)
    if e is None:
        spheres[key] = [1, k]
    else:
        e[0] += 1
    # batch sums
    if m % BATCH == 0:
        pass
    bi = m // BATCH
    if len(batches) <= bi:
        batches.append(0.0)
    batches[bi] += k

E = sumk / m
se = math.sqrt(max(sumsq / m - E * E, 0) / m)
# batch SE (more robust to heavy tail)
bn = len(batches)
bmean = sum(batches) / bn
bvar = sum((x - bmean) ** 2 for x in batches) / (bn - 1)
se_batch = math.sqrt(bvar / bn) / BATCH

print(f"=== n={n} m={m} ===")
print(f"E={E:.6f}  se={se:.6f}  se_batch={se_batch:.6f}  nE={n*E:.4f}  n2E={n*n*E:.1f}")
pk1 = 1 - hist[0] / m
print(f"P(k>=1)={pk1:.5f}  E[k|k>=1]={E/pk1:.4f}  maxk={max(hist)}")
top = sorted(hist.items())
print("hist k:count:", " ".join(f"{k}:{c}" for k, c in top if c > 0 and k <= 30),
      "| >30:", sum(c for k, c in top if k > 30))
# contribution of each k to E
contrib = sorted(((k * c / m, k) for k, c in hist.items()), reverse=True)
cum = 0
ksum = []
for cv, k in contrib:
    cum += cv
    ksum.append((k, cv, cum / E))
print("k-share (k, contrib, cumshare):", " ".join(f"{k}:{cv:.4f}:{cs:.3f}" for k, cv, cs in ksum[:12]))

print("-- dyadic buckets of a=primitive |p|^2 coeff (count, share of samples, E-contrib, share of E) --")
for b in sorted(bk_a):
    c_, s_ = bk_a[b]
    print(f"  a in [2^{b-1},2^{b}): cnt={c_} ({c_/m:.4f})  Econtrib={s_/m:.6f} ({s_/sumk:.4f})")
print("-- dyadic buckets of center denominator Dc --")
for b in sorted(bk_dc):
    c_, s_ = bk_dc[b]
    print(f"  Dc in [2^{b-1},2^{b}): cnt={c_} ({c_/m:.4f})  Econtrib={s_/m:.6f} ({s_/sumk:.4f})")
print("-- dyadic buckets of det (4-tuple property) --")
for b in sorted(bk_det):
    c_, s_ = bk_det[b]
    print(f"  det in [2^{b-1},2^{b}): cnt={c_} ({c_/m:.4f})  Econtrib={s_/m:.6f} ({s_/sumk:.4f})")
print("-- radius buckets (log2 R/n) --")
for b in sorted(bk_R):
    c_, s_ = bk_R[b]
    print(f"  R/n ~ 2^{b}: cnt={c_} ({c_/m:.4f})  Econtrib={s_/m:.6f} ({s_/sumk:.4f})")

# distinct-sphere concentration
mult = Counter()
nsph = len(spheres)
Erepeat = 0.0
topcontrib = []
kdist = Counter()   # distinct spheres with k>=1 by k
for key, (ms, k) in spheres.items():
    mult[ms] += 1
    Ec = ms * k / m
    if k >= 1:
        kdist[k] += 1
    if ms >= 2:
        Erepeat += Ec
    topcontrib.append((Ec, ms, k, key))
topcontrib.sort(reverse=True)
print(f"distinct spheres: {nsph}; E share from spheres sampled >=2x: {Erepeat/E:.4f}")
print("top sphere contributors (Econtrib, mult, k, a, b, c):")
for Ec, ms, k, key in topcontrib[:8]:
    print(f"  {Ec:.6f} mult={ms} k={k} a={key[0]} b={key[1:4]} c={key[4]}")
print("distinct spheres with k>=1 by k:", " ".join(f"{k}:{c}" for k, c in sorted(kdist.items()) if c > 0 and k <= 20), "| >20:", sum(c for k, c in kdist.items() if k > 20))

# ---- structure analysis on extras ----
def plane_key(p, q, r):
    ux, uy, uz = (q[0]-p[0], q[1]-p[1], q[2]-p[2])
    vx, vy, vz = (r[0]-p[0], r[1]-p[1], r[2]-p[2])
    nx, ny, nz = (uy*vz-uz*vy, uz*vx-ux*vz, ux*vy-uy*vx)
    d = nx*p[0]+ny*p[1]+nz*p[2]
    g = gcd(gcd(abs(nx), abs(ny)), gcd(abs(nz), abs(d)))
    if g: nx, ny, nz, d = nx//g, ny//g, nz//g, d//g
    if nx < 0 or (nx == 0 and (ny < 0 or (ny == 0 and (nz < 0 or (nz == 0 and d < 0))))):
        nx, ny, nz, d = -nx, -ny, -nz, -d
    return (nx, ny, nz, d)

import random
rng = random.Random(12345)
EXTRAS_CAP = int(sys.argv[4]) if len(sys.argv) > 4 else 30000
nextra = 0
stats = Counter()          # structural classes (E-weighted below)
w_axis = w_cop4 = w_allcop = w_coll = 0.0
w_struct_sumk = 0.0
sumkc = sumki = 0          # extras coplanar with a base triple (circle+point) vs not
struct_rows = []
with open(prefix + ".extras.tsv") as f:
    for line in f:
        if line.startswith('#'):
            continue
        if nextra >= EXTRAS_CAP:
            break
        parts = line.split('|')
        sid, tot = (int(x) for x in parts[0].split()[:2])
        pts = [int(x) for x in parts[2].split() if x.isdigit() or (x and x[0]=='-' and x[1:].isdigit())]
        if len(pts) % 3:
            pts = pts[:len(pts)//3*3]
        pts = [tuple(pts[3*i:3*i+3]) for i in range(len(pts)//3)]
        base = [int(x) for x in parts[1].split()]
        base = [tuple(base[3*i:3*i+3]) for i in range(4)]
        t = len(pts)
        if t < tot:  # truncated list; skip structure stats
            continue
        nextra += 1
        k = tot - 4
        # mechanism split of extras: x coplanar with a base triple -> {base,x} is
        # a "circle+point" degeneracy; else irreducible cospherical.
        bset = set(base)
        extras = [p for p in pts if p not in bset]
        tripl = [(base[0],base[1],base[2]),(base[0],base[1],base[3]),
                 (base[0],base[2],base[3]),(base[1],base[2],base[3])]
        kc = ki = 0
        for x in extras:
            copl = False
            for (A,B,Cp) in tripl:
                ux,uy,uz = B[0]-A[0],B[1]-A[1],B[2]-A[2]
                vx,vy,vz = Cp[0]-A[0],Cp[1]-A[1],Cp[2]-A[2]
                wx,wy,wz = x[0]-A[0],x[1]-A[1],x[2]-A[2]
                if (uy*vz-uz*vy)*wx + (uz*vx-ux*vz)*wy + (ux*vy-uy*vx)*wz == 0:
                    copl = True; break
            if copl: kc += 1
            else: ki += 1
        sumkc += kc; sumki += ki
        # axis-plane loads
        cx = Counter(p[0] for p in pts); cy = Counter(p[1] for p in pts); cz = Counter(p[2] for p in pts)
        axload = max(cx.most_common(1)[0][1], cy.most_common(1)[0][1], cz.most_common(1)[0][1])
        # max coplanar subset
        maxcop = 3
        if t <= COPMAX:
            planes = Counter()
            for i in range(t):
                for j in range(i+1, t):
                    for l in range(j+1, t):
                        planes[plane_key(pts[i], pts[j], pts[l])] += 1
            # a plane with r points gets C(r,3) triples
            if planes:
                import math as _m
                maxcop = 3
                for pl, tr in planes.items():
                    r = 3
                    while tr > _m.comb(r, 3):
                        r += 1
                    maxcop = max(maxcop, r)
        else:
            # random-triple subsample
            planes = Counter()
            for _ in range(6000):
                i, j, l = rng.sample(range(t), 3)
                planes[plane_key(pts[i], pts[j], pts[l])] += 1
            if planes:
                tr = max(planes.values())
                # rough inversion of C(r,3)/C(t,3)*6000 ~ tr
                est = (tr / 6000.0) ** (1/3) * t
                maxcop = max(3, int(round(est)))
        # collinear triple among pts?
        # (a sphere has no 3 collinear, so skip)
        stats['n_sphere'] += 1
        if axload >= 4: stats['axload>=4'] += 1; w_axis += k
        if axload >= max(4, tot-1): stats['axload~all'] += 1
        if maxcop >= 4: stats['coplanar>=4'] += 1; w_cop4 += k
        if maxcop == t: stats['all_coplanar'] += 1; w_allcop += k
        w_struct_sumk += k
print(f"-- structure over {nextra} spheres with extras (fraction of such spheres; k-weighted share of their total k={w_struct_sumk:.0f}) --")
for key in ('axload>=4', 'axload~all', 'coplanar>=4', 'all_coplanar'):
    print(f"  {key}: {stats[key]} ({stats[key]/nextra:.4f})")
print(f"  k-weighted: axis4={w_axis/w_struct_sumk:.4f} cop4={w_cop4/w_struct_sumk:.4f} allcop={w_allcop/w_struct_sumk:.4f}")
# mechanism split: E = E_circ + E_irr.  sumkc counts extras coplanar with a base
# triple (circle+point degeneracy: 4 valid bases per such 5-subset); sumki the rest
# (irreducible cospherical 5-subsets: 5 valid bases).  Share over a prefix of the
# extras lines estimates share over all (iid order).
share_circ = sumkc / (sumkc + sumki) if (sumkc + sumki) else 0.0
print(f"  extras coplanar with a base triple (circle+point): share={share_circ:.4f}"
      f"  -> E_circ~{E*share_circ:.6f} E_irr~{E*(1-share_circ):.6f}  [first {nextra} extras lines]")
Zfac = (n ** 3) * (n ** 3 - 1) * (n ** 3 - 2) * (n ** 3 - 3) / 24.0
print(f"  implied Z_circ~{(E*share_circ)*Zfac/4:.3e} Z_irr~{(E*(1-share_circ))*Zfac/5:.3e}"
      f"  vs Z_sphere~{E*Zfac:.3e}  (Z/n^11: {E*Zfac/n**11:.4f})")
