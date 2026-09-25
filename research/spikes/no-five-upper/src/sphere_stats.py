#!/usr/bin/env python3
"""Statistics of the circumspheres of dumped cospherical 5-subsets: center denominator,
radius, number of set points and of grid points on the sphere.  Exact rationals."""
import sys
from fractions import Fraction as F
from collections import Counter
pts=[tuple(map(int,l.split())) for l in open(sys.argv[1])]
n=int(sys.argv[2]); tuples=[tuple(map(int,l.split())) for l in open(sys.argv[3])]
import itertools
def circumsphere(P5):
    for P in itertools.combinations(P5,4):
        try: return _circ(P)
        except ZeroDivisionError: continue
    raise ValueError("all 4-subsets coplanar")
def _circ(P):
    A=P[0]; rows=[]
    for B in P[1:4]:
        rows.append([2*(B[i]-A[i]) for i in range(3)]+[sum(B[i]**2 for i in range(3))-sum(A[i]**2 for i in range(3))])
    # solve 3x3 by Cramer
    M=[[F(v) for v in r[:3]] for r in rows]; b=[F(r[3]) for r in rows]
    def det(m): return m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])-m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])+m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0])
    D=det(M); c=[]
    for j in range(3):
        Mj=[r[:] for r in M]
        for i in range(3): Mj[i][j]=b[i]
        c.append(det(Mj)/D)
    R=sum((F(A[i])-c[i])**2 for i in range(3)); return tuple(c),R
seen={}
for t in tuples:
    P=[pts[i] for i in t]; c,R=circumsphere(P)
    key=(c,R)
    if key not in seen:
        onset=sum(1 for p in pts if sum((F(p[i])-c[i])**2 for i in range(3))==R)
        seen[key]=onset
dens=Counter(); big=[]
for (c,R),onset in seen.items():
    q=1
    for v in c: q=q*v.denominator//__import__('math').gcd(q,v.denominator)
    dens[q]+=1; big.append((onset,q,c,R))
print("distinct spheres:",len(seen))
print("center-denominator histogram (q: #spheres):",sorted(dens.items())[:25])
print("set-points-on-sphere histogram:",sorted(Counter(v for v in seen.values()).items()))
big.sort(reverse=True)
for onset,q,c,R in big[:8]: print("  points_on_sphere=%d denom=%d center=%s R=%s"%(onset,q,tuple(str(v) for v in c),R))
