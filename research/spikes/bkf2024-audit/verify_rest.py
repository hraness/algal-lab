"""Remaining checks: Thm3 interior regions, Remark5, Ex3/Thm7 numeric,
Cex6 lognormal, Cex4/Cex7 wide scans."""
import sys
sys.path.insert(0,"/Users/bg/Documents/algal-lab/research/spikes/context/runs/bkf2024")
from fractions import Fraction as Fr
import itertools
from bkf_lib import hr_frac, rh_frac, sf_frac, in_D, in_E, maj, weak_super, \
    weak_sub, recip_maj
def P(*a): print(" ".join(str(x) for x in a),flush=True)
def chk(name,cond): print(f"    [{'OK' if cond else 'FAIL'}] {name}")

# ---- Thm 3 interior vs boundary ----------------------------------------
P("THM 3: interior (all alive) vs boundary-region behavior, power2")
sig=Fr(1,10)
r=(Fr(1,2),Fr(3,10),Fr(1,5)); lam=(Fr(1,10),Fr(2,5),Fr(7,10)); th=(Fr(1,10),Fr(3,10),Fr(3,5))
chk("r in D3+",in_D(r)); chk("lam,th in E3+",in_E(lam) and in_E(th))
chk("lam rm th",recip_maj(lam,th))
slU=[(sig,l) for l in lam]; slV=[(sig,l) for l in th]
for x in [Fr(3,20),Fr(1,5),Fr(1,4),Fr(3,10),Fr(2,5)]:
    dU=sf_frac(x,r,slU,"power2"); dV=sf_frac(x,r,slV,"power2")
    alU=[0< (x-sig)/l <=1 for l in lam]; alV=[0<(x-sig)/l<=1 for l in th]
    P(f"    x={x}: aliveU={alU} aliveV={alV} SF_U-SF_V={dU-dV}")
# bigger interior scan across admissible instances, all-alive region only
vint=vbnd=adm=0
import random; random.seed(7)
for _ in range(20000):
    r_=tuple(sorted((Fr(a,b) for a in [random.choice([1,2,3,4,5]) for _ in range(3)] for b in [0]), reverse=True)) if False else None
    rr=[random.choice([1,2,3,4,5]) for _ in range(3)]; S=sum(rr)
    r_=tuple(sorted((Fr(a,S) for a in rr),reverse=True))
    lam=tuple(sorted(random.sample([Fr(1,10),Fr(1,5),Fr(3,10),Fr(2,5),Fr(1,2)],3)))
    th =tuple(sorted(random.sample([Fr(1,10),Fr(1,5),Fr(3,10),Fr(2,5),Fr(1,2)],3)))
    if not recip_maj(lam,th): continue
    adm+=1; sig=Fr(1,10)
    xall=sig+min(lam[0],th[0])*Fr(4,5)   # strictly inside all-alive region
    xbnd=sig+min(lam[0],th[0])*Fr(11,10) # just past smallest support end
    slU=[(sig,l) for l in lam]; slV=[(sig,l) for l in th]
    dI=sf_frac(xall,r_,slU,"power2")-sf_frac(xall,r_,slV,"power2")
    dB=sf_frac(xbnd,r_,slU,"power2")-sf_frac(xbnd,r_,slV,"power2")
    if dI>0: vint+=1
    if dB>0: vbnd+=1
P(f"    admissible={adm} interior viol={vint} boundary viol={vbnd}")

# ---- Remark 5: Thm6 variants r in D,sig in E / r in E,sig in E ----------
P("\nREMARK 5 (Thm6 with sig in E3+): pareto2 lam=2")
lam=Fr(2); adm=v1=v2=0; ex1=ex2=None
import random; random.seed(11)
for _ in range(4000):
    rr=[random.choice([1,2,3,4,5,6,7]) for _ in range(3)]; S=sum(rr)
    r_=tuple(Fr(a,S) for a in rr)
    ss=[random.choice([1,2,3,4,5,6,7]) for _ in range(3)]; T=sum(ss)
    s_=tuple(Fr(a,T) for a in ss)
    sigv=tuple(sorted(random.sample([Fr(1),Fr(3,2),Fr(2),Fr(5,2),Fr(3),Fr(7,2),Fr(4),Fr(1,2)],3)))
    if not (maj(r_,s_)): continue
    case1 = in_D(r_) and in_E(sigv)   # r D, sig E -> claim (i-style) <=rh?
    case2 = in_E(r_) and in_E(sigv)
    if not (case1 or case2): continue
    adm+=1
    sl=[(si,lam) for si in sigv]
    xs=[sigv[i]+Fr(2)+Fr(1,10) for i in range(3)]+[sigv[0]+Fr(2)+Fr(3,10)]
    for x in xs:
        rU=rh_frac(x,r_,sl,"pareto2"); rV=rh_frac(x,s_,sl,"pareto2")
        if rU is None or rV is None: continue
        if case1 and rU>rV: v1+=1; ex1=ex1 or (r_,s_,sigv,x); break
        if case2 and rU<rV: v2+=1; ex2=ex2 or (r_,s_,sigv,x); break
P(f"    admissible={adm}; (rD,sigE) claim <=rh viol={v1} e.g.{ex1}")
P(f"                    (rE,sigE) claim >=rh viol={v2} e.g.{ex2}")

# ---- Example 3 (Thm 7, Weibull c=2 log-concave) --------------------------
P("\nEXAMPLE 3 (Thm7): weibull c=2, sig=(22,18,16),mu=(12,8,2),r=(.1,.7,.2),lam=2")
import mpmath as mp; mp.mp.dps=50
r=[mp.mpf("0.1"),mp.mpf("0.7"),mp.mpf("0.2")]; sig=[mp.mpf(22),mp.mpf(18),mp.mpf(16)]
mu=[mp.mpf(12),mp.mpf(8),mp.mpf(2)]; lam=mp.mpf(2)
def pdf_mix(x,r_,sv_):
    return sum(ri/lam*( (x-si)/lam )*mp.e**(-((x-si)/lam)**2) if x>si else mp.mpf(0)
               for ri,si in zip(r_,sv_))
# ratio f_U/f_V should be increasing on (16,inf) for U>=lrV (log-concave f)
rats=[]
for x in [mp.mpf(v)/10 for v in range(161,400,10)]+[mp.mpf(60),mp.mpf(100)]:
    fU,fV=pdf_mix(x,r,sig),pdf_mix(x,r,mu)
    rats.append((x,fU/fV if fV>0 else mp.nan))
mono=all(rats[i][1]<=rats[i+1][1]+mp.mpf("1e-30") for i in range(len(rats)-1))
P("    ratio monotone increasing on [16.1,100]:",mono)
P("    sample:", [(str(x),mp.nstr(rt,6)) for x,rt in rats[:5]],"...",mp.nstr(rats[-1][1],6))

# ---- Cex 6 (lognormal, Thm7 with f log-convex?) ---------------------------
P("\nCEX 6: lognormal F, sig=(.6,.4,.2),mu=(.3,.2,.1),lam=1/2?,r=(.2,.5,.3)")
# From text: sigma=(.6,.4,.2) D3+, mu=(.3,.2,.1), lambda=1/2
sig=[mp.mpf("0.6"),mp.mpf("0.4"),mp.mpf("0.2")]; mu=[mp.mpf("0.3"),mp.mpf("0.2"),mp.mpf("0.1")]
lam=mp.mpf("0.5"); r=[mp.mpf("0.2"),mp.mpf("0.5"),mp.mpf("0.3")]
def logn_pdf(u):  # LN(0,1): f=exp(-(ln u)^2/2)/(u sqrt(2pi))
    return mp.e**(-(mp.log(u))**2/2)/(u*mp.sqrt(2*mp.pi)) if u>0 else mp.mpf(0)
def pm(x,r_,sv_):
    return sum(ri/lam*logn_pdf((x-si)/lam) if x>si else mp.mpf(0)
               for ri,si in zip(r_,sv_))
vals=[]
for x in [mp.mpf(v)/100 for v in range(61,2000,20)]:
    fU,fV=pm(x,r,sig),pm(x,r,mu)
    if fV>0: vals.append((x,fU/fV))
mins=min(range(len(vals)),key=lambda i:vals[i][1]); maxs=max(range(len(vals)),key=lambda i:vals[i][1])
P(f"    ratio range: min {mp.nstr(vals[mins][1],5)} at x={vals[mins][0]}, max {mp.nstr(vals[maxs][1],5)} at x={vals[maxs][0]}")
chk("ratio non-monotone (their claim)", vals[mins][0]>vals[0][0] and vals[maxs][0]<vals[-1][0])

# ---- Cex 4 wide scan -----------------------------------------------------
P("\nCEX 4 wide: any negative K4 on (2.3,120]?")
lam=Fr(2); r=(Fr(1,5),Fr(3,5),Fr(1,5)); sv=(Fr(1,10),Fr(1,5),Fr(7,10))
sl=[(si,lam) for si in (Fr(2,5),Fr(3,5),Fr(3,10))]
neg=[]
for k in range(231,12000,13):
    t=Fr(k,100)
    rU=rh_frac(t,r,sl,"pareto2"); rV=rh_frac(t,sv,sl,"pareto2")
    if rU is None or rV is None: continue
    if rU<rV: neg.append(t)
P(f"    negative-K4 points: count={len(neg)} {neg[:8]}")

# ---- Cex 7 wide scan -----------------------------------------------------
P("\nCEX 7 wide: burr3 SF diff sign set on (0.002,40]")
r=(Fr(1,5),Fr(4,5)); lam=(Fr(2,5),Fr(3,5)); sv=(Fr(31,50),Fr(19,50)); th=(Fr(27,50),Fr(23,50))
slU=[(Fr(0),l) for l in lam]; slV=[(Fr(0),l) for l in th]
ss=set(); mn=(None,None)
for k in range(1,20000):
    t=Fr(k,500)
    d=sf_frac(t,r,slU,"burr3")-sf_frac(t,sv,slV,"burr3")
    s=int((d>0)-(d<0)); ss.add(s)
    if mn[1] is None or d<mn[1]: mn=(t,d)
P(f"    signs {ss}; min diff {mn[1]} at t={mn[0]}")
# try alternative sigma values? paper left sigma unspecified.
