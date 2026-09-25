#!/usr/bin/env python3
import math
rows = [  # n, m, E, se, maxk, share_circ (extras coplanar w/ base triple)
 (8,  1000000, 3.727270, 0.007315,   68, 0.3289),
 (12, 1000000, 2.668888, 0.007394,  116, 0.2790),
 (16, 1000000, 2.030376, 0.007326,  164, 0.2395),
 (20, 1000000, 1.586429, 0.007124,  212, 0.2205),
 (24, 1000000, 1.272137, 0.006738,  220, 0.2158),
 (32,  800000, 0.885481, 0.006978,  344, 0.1958),
 (40,  800000, 0.674646, 0.007014,  436, 0.1797),
 (48,  600000, 0.508868, 0.007199,  548, 0.1740),
 (64,  500000, 0.334722, 0.007136,  620, 0.1635),
 (96,  250000, 0.175020, 0.007418,  566, 0.1577),
 (128, 150000, 0.109487, 0.009051,  640, 0.1438),
]
print(" n      E(n)      se      nE     n2E    n2E/ln2n  loc_slope")
prev=None
for (n,m,E,se,mk,sc) in rows:
    l = math.log(n)
    sl = "" if prev is None else f"{math.log(prev[2]/E)/math.log(n/prev[0]):6.3f}"
    print(f"{n:3d} {E:9.5f} {se:.5f}  {n*E:7.3f} {n*n*E:8.1f}  {n*n*E/l**2:7.2f}   {sl}")
    prev=(n,m,E)

def fit(rows, i0):
    xs = [math.log(r[0]) for r in rows[i0:]]
    ys = [math.log(r[2]) for r in rows[i0:]]
    w  = [r[2]/r[3] for r in rows[i0:]]       # 1/se weights
    sw=sum(w); sx=sum(wi*x for wi,x in zip(w,xs))/sw; sy=sum(wi*y for wi,y in zip(w,ys))/sw
    sxy=sum(wi*(x-sx)*(y-sy) for wi,x,y in zip(w,xs,ys)); sxx=sum(wi*(x-sx)**2 for wi,x in zip(w,xs))
    a=-sxy/sxx; c=math.exp(sy-sxy/sxx*sx)
    resid=[y-(math.log(c)-a*x) for x,y in zip(xs,ys)]
    return a,c,resid

for i0 in (0,3,5):
    a,c,resid=fit(rows,i0)
    print(f"log-log fit n>={rows[i0][0]}: E~{c:.3f} n^-{a:.3f}; resid={['%.2f'%x for x in resid]}")
# fit nE = c' (ln n)^gamma / n  i.e. E = c' (ln n)^gamma / n^2 on log E*n^2 vs log ln n
xs=[math.log(math.log(r[0])) for r in rows[5:]]
ys=[math.log(r[2]*r[0]**2) for r in rows[5:]]
sx=sum(xs)/len(xs); sy=sum(ys)/len(ys)
g=sum((x-sx)*(y-sy) for x,y in zip(xs,ys))/sum((x-sx)**2 for x in xs)
c=math.exp(sy-g*sx)
print(f"gamma fit n>=32: n^2 E ~ {c:.2f} (ln n)^{g:.3f}   resid={['%.2f'%(math.log(r[2]*r[0]**2)-(math.log(c)+g*math.log(math.log(r[0])))) for r in rows[5:]]}")
