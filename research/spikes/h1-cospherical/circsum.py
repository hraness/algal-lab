#!/usr/bin/env python3
"""circsum.py -- aggregate circles.c output.

circles output: id tot [~]nplanes cmax nx ny nz cop5 cp irr C4circ
Each sphere s (carrying t points, sampled w.p. N_s/B where
N_s = C(t,4)-C4circ = # non-coplanar 4-subsets on s, B = # valid bases):
  Z_circ = sum_s cp_s = B * mean_valid[ cp_s / N_s ]
  Z_irr  = sum_s irr_s;  Z_sphere = Z_circ + Z_irr;  cop5 similar.
k=0 lines (absent from extras file) contribute 0 -> divide by M_TOTAL.

Usage: circsum.py n circles.txt m_total
"""
import sys
from math import comb

n = int(sys.argv[1]); fn = sys.argv[2]; M = int(sys.argv[3])
r4 = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0

N3 = n ** 3
B = comb(N3, 4) * (1 - r4)
m = 0
s_cp = s_irr = s_cop5 = s_deg = 0.0
norms = {}
cmaxh = {}
byA = {}
sampled = 0
cpw_by_a = {}
with open(fn) as f:
    for line in f:
        p = line.split()
        if len(p) == 8:   # old format: id tot npl cmax cop5 cp irr C4c
            sid = int(p[0]); tot = int(p[1])
            npl = int(p[2]); cmax = int(p[3])
            nx = ny = nz = -1
            cop5, cp, irr, C4c = int(p[4]), int(p[5]), int(p[6]), int(p[7])
        elif len(p) >= 11:
            sid = int(p[0]); tot = int(p[1])
            if p[2].startswith('~'):
                sampled += 1
                npl = int(p[2][1:])
            else:
                npl = int(p[2])
            cmax = int(p[3]); nx, ny, nz = int(p[4]), int(p[5]), int(p[6])
            cop5, cp, irr, C4c = int(p[7]), int(p[8]), int(p[9]), int(p[10])
        else:
            continue
        t = tot
        Ns = comb(t, 4) - C4c
        if Ns <= 0:
            continue
        m += 1
        s_cop5 += cop5 / Ns; s_cp += cp / Ns; s_irr += irr / Ns; s_deg += (cop5+cp+irr) / Ns
        if nx < 0:
            continue
        key = tuple(sorted((abs(nx), abs(ny), abs(nz))))
        norms[key] = norms.get(key, 0) + 1
        cmaxh[cmax] = cmaxh.get(cmax, 0) + 1
        ab = max(key).bit_length()
        rec = byA.get(ab) or [0, 0.0]
        rec[0] += 1; rec[1] += cp / Ns; byA[ab] = rec

print(f"n={n} extras lines: {m} (sampled-mode {sampled}); M_total={M}")
print(f"  mean cp/N={s_cp/M:.3e} irr/N={s_irr/M:.3e} cop5/N={s_cop5/M:.3e}  (over ALL samples)")
print(f"  Z_circ~{B*s_cp/M:.4e}  Z_irr~{B*s_irr/M:.4e}  Z_sphere~{B*(s_cp+s_irr)/M:.4e}"
      f"  -> Z_sphere/n^11 ~ {B*(s_cp+s_irr)/M/n**11:.5f}")
print(f"  circle+point share of Z_sphere: {s_cp/(s_cp+s_irr):.4f}")
print("  cmax hist:", sorted(cmaxh.items())[:18])
top = sorted(norms.items(), key=lambda kv: -kv[1])[:15]
print("  dominant circle normals (sorted |v|,count):", top)
print("  cp/N sum by dominant circle |v|_inf bucket:", sorted((k, v[0], f"{v[1]/M:.3e}") for k,v in byA.items()))
