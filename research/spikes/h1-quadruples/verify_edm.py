import random, itertools

def Fc(c, X):
    c4 = -(c[0]+c[1]+c[2])
    s = sum(c[i]*sum(v*v for v in X[i]) for i in range(3))
    t = [sum(c[i]*X[i][j] for i in range(3)) for j in range(3)]
    return c4*s + sum(v*v for v in t)

def circum(P):
    d = [[P[i+1][j]-P[0][j] for j in range(3)] for i in range(3)]
    det = (d[0][0]*(d[1][1]*d[2][2]-d[1][2]*d[2][1])
          -d[0][1]*(d[1][0]*d[2][2]-d[1][2]*d[2][0])
          +d[0][2]*(d[1][0]*d[2][1]-d[1][1]*d[2][0]))
    if det != 0: return False
    R = [sum(v*v for v in P[i+1]) - sum(v*v for v in P[0]) for i in range(3)]
    w = [[d[0][j],d[1][j],d[2][j]] for j in range(3)]   # columns
    nus=[]
    for i,j in itertools.combinations(range(3),2):
        a,b=w[i],w[j]
        nus.append([a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]])
    nu=None
    for cand in nus:
        if any(cand): nu=cand;break
    if nu is None: return False
    return sum(nu[i]*R[i] for i in range(3))==0

random.seed(1)
n=4; box=range(n)
pts=[(x,y,z) for x in box for y in box for z in box]
tested=0; hits=0; noncirc=0; collx4=0; total_quads=0
quadset=set()
K=6
cvals=list(range(-K,K+1))
for X in itertools.combinations(pts,3):
    x1,x2,x3=X
    e1=[x2[j]-x1[j] for j in range(3)]; e2=[x3[j]-x1[j] for j in range(3)]
    cr=[e1[1]*e2[2]-e1[2]*e2[1],e1[2]*e2[0]-e1[0]*e2[2],e1[0]*e2[1]-e1[1]*e2[0]]
    if not any(cr): continue
    tested+=1
    d=[sum((x1[j]-x2[j])**2 for j in range(3)),
       sum((x1[j]-x3[j])**2 for j in range(3)),
       sum((x2[j]-x3[j])**2 for j in range(3))]
    for c1 in cvals:
      if c1==0: continue
      for c2 in cvals:
        if c2==0: continue
        den=d[2]*c2+d[1]*c1
        if den==0: continue
        num=-d[0]*c1*c2
        if num%den: continue
        c3=num//den
        if c3==0 or abs(c3)>K: continue
        c4=-(c1+c2+c3)
        if c4==0 or abs(c4)>K: continue
        if Fc([c1,c2,c3],[list(x1),list(x2),list(x3)])!=0: continue
        S=[c1*x1[j]+c2*x2[j]+c3*x3[j] for j in range(3)]
        if any(S[j]%c4 for j in range(3)): continue
        x4=tuple(-S[j]//c4 for j in range(3))
        if x4 in (x1,x2,x3): continue
        if not all(0<=v<n for v in x4): continue
        hits+=1
        quadset.add(tuple(sorted([x1,x2,x3,x4])))
        if not circum([x1,x2,x3,x4]):
            # check collinearity of x4 with the triple's plane -> actually must be concyclic or collinear
            noncirc+=1
print("triples:",tested,"(c,x4) hits:",hits,"distinct quads found:",len(quadset),"nonconcyclic:",noncirc)
# expected concyclic quads at n=4: 6360. K=6 cutoff misses quads with |c|>6.
