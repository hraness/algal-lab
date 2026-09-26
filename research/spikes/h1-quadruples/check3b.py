from itertools import combinations
import numpy as np
from collections import Counter
n=4
pts=[(x,y,z) for x in range(n) for y in range(n) for z in range(n)]
def conc(P):
    a=np.array(P[1],dtype=np.int64)-np.array(P[0],dtype=np.int64)
    b=np.array(P[2],dtype=np.int64)-np.array(P[0],dtype=np.int64)
    c=np.array(P[3],dtype=np.int64)-np.array(P[0],dtype=np.int64)
    detv=a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
    if detv!=0: return None
    nrm=np.cross(a,b)
    if not nrm.any(): nrm=np.cross(a,c)
    if not nrm.any(): return "collinear"
    wr=np.stack([a,b,c])           # rows a,b,c ; coordinate vectors wr[:,j]
    nu=np.cross(wr[:,0],wr[:,1])   # left kernel
    if not nu.any(): nu=np.cross(wr[:,0],wr[:,2])
    if not nu.any(): nu=np.cross(wr[:,1],wr[:,2])
    if not nu.any(): return "collinear"
    R=[int((np.array(P[i+1],dtype=np.int64)**2).sum()-(np.array(P[0],dtype=np.int64)**2).sum()) for i in range(3)]
    if sum(int(nu[i])*R[i] for i in range(3))!=0: return "copl"
    g=np.gcd.reduce(np.abs(nrm)); v=tuple((nrm//g).tolist())
    if v[0]<0 or (v[0]==0 and v[1]<0) or (v[0]==0 and v[1]==0 and v[2]<0): v=tuple(-x for x in v)
    return v
C=Counter()
for P in combinations(pts,4):
    r=conc(P)
    if isinstance(r,tuple): C[r]+=1
print("total concyclic:",sum(C.values()))
for v,c in C.most_common(14): print(v,c)
