# Verify: for a primitive conic point c on EDM (A,B,C), writing g=gcd(c1,c2),
# a=c1/g, b=c2/g, u=|a|,v=|b|, g_A=gcd(A,u), g_B=gcd(B,v), M=(bA+aB)/(gAgB),
# gam=gcd(|M|,C), h=|M|/gam, t=C/gam, kappa=uv/(gAgB):
#   |c1|=uh, |c2|=vh, |c3|=kappa*t, |c4|=|kappa*t - eta*h|, eta in {u+v,|u-v|}
#   and primitive <=> gcd(h,kappa)=1 ; s=1 forced (c(s)=s*c(1)).
import itertools
from math import gcd
n=4; K=int(3*3**0.5*n*n/2)
pts=[(x,y,z) for x in range(n) for y in range(n) for z in range(n)]
bad=0; checked=0
for X in itertools.combinations(pts,3):
    x1,x2,x3=X
    e1=[x2[j]-x1[j] for j in range(3)]; e2=[x3[j]-x1[j] for j in range(3)]
    cr=[e1[1]*e2[2]-e1[2]*e2[1],e1[2]*e2[0]-e1[0]*e2[2],e1[0]*e2[1]-e1[1]*e2[0]]
    if not any(cr): continue
    A=sum((x3[j]-x2[j])**2 for j in range(3)); B=sum(v*v for v in e2); C=sum(v*v for v in e1)
    seen=set()
    for c1 in range(-K,K+1):
        if not c1: continue
        for c2 in range(-K,K+1):
            if not c2: continue
            den=A*c2+B*c1
            if not den: continue
            num=-C*c1*c2
            if num%den: continue
            c3=num//den
            if not c3 or abs(c3)>K: continue
            c4=-(c1+c2+c3)
            if not c4 or abs(c4)>K: continue
            g=gcd(gcd(abs(c1),abs(c2)),gcd(abs(c3),abs(c4)))
            cc=(c1//g,c2//g,c3//g,c4//g)
            if cc[0]<0: cc=tuple(-v for v in cc)
            if cc in seen: continue
            seen.add(cc)
            # now test factorization for THIS primitive cc
            c1p,c2p,c3p,c4p=cc
            gg=gcd(abs(c1p),abs(c2p)); a=c1p//gg; b=c2p//gg
            u,v=abs(a),abs(b)
            gA=gcd(A,u) if u else A; gB=gcd(B,v) if v else B
            Mv=(b*A+a*B)//(gA*gB) if (b*A+a*B)%(gA*gB)==0 else None
            if Mv is None or Mv==0:
                bad+=1; print("M-fail",X,cc); continue
            gam=gcd(abs(Mv),C); h=abs(Mv)//gam; t=C//gam
            kap=u*v//(gA*gB)
            eta=u+v if a*b>0 else abs(u-v)
            sig=1 if Mv>0 else -1
            pred=(abs(h*a),abs(h*b),kap*t,abs(kap*t - (1 if sig*(a*b>0) else -1)*0 ))  # placeholder
            # actual check: |c3| == kap*t and |c4| == |kap*t - eta*h| up to sign structure
            ok3 = abs(c3p)==kap*t
            ok4 = abs(c4p)==abs(kap*t-eta*h) or abs(c4p)==kap*t+eta*h
            prim = gcd(h,kap)==1 and gcd(h,t)==1
            if not(ok3 and ok4 and prim):
                bad+=1
                if bad<6: print("FAIL",cc,"g,ab=",gg,(a,b),"M,gam,h,t,kap,eta=",Mv,gam,h,t,kap,eta,"pred|3|",kap*t,"pred|4|",abs(kap*t-eta*h),kap*t+eta*h)
            checked+=1
print("checked",checked,"primitive conic pts; mismatches:",bad)
