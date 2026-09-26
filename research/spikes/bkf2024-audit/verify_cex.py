"""Verify BKF2024's own Examples and Counterexamples exactly (Fractions)."""
import sys
sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/context/runs/bkf2024")
from fractions import Fraction as Fr
from bkf_lib import hr_frac, rh_frac, sf_frac, in_D, in_E, maj, weak_super, \
    weak_sub, t_transform

def P(*a): print(" ".join(str(x) for x in a))
def chk(name, cond): print(f"    [{'OK' if cond else 'FAIL'}] {name}")

# ====================================================== Counterexample 1 ===
# power2 baseline f=2t inc; r=(.2,.5,.3), lam=(.4,.5,.1), s=(.1,.6,.3), sig=.1
P("="*72); P("CEX 1 (Thm 4): K1(t)=h_U-h_V at t=0.52, 0.55; power2, sig=0.1")
sig = Fr(1,10)
r=(Fr(1,5),Fr(1,2),Fr(3,10)); lam=(Fr(2,5),Fr(1,2),Fr(1,10))
sv=(Fr(1,10),Fr(3,5),Fr(3,10))
chk("r m s", maj(r,sv)); chk("r unordered (as they state)", not in_D(r) and not in_E(r))
sl=[(sig,l) for l in lam]
for t in (Fr(13,25), Fr(11,20)):
    al=[(t-sig)/l<=1 for l in lam]
    hU,hV=hr_frac(t,r,sl,"power2"),hr_frac(t,sv,sl,"power2")
    P(f"    t={t}: alive={al} hU={hU} hV={hV} diff={hU-hV}")
    chk("K1 identically 0 (single alive comp)", hU==hV)
P("    scanning region where >=2 comps alive: (0.2,0.5]")
sgn=[]
for k in range(21,51):
    t=Fr(k,100); d=hr_frac(t,r,sl,"power2")-hr_frac(t,sv,sl,"power2")
    sgn.append((t,int((d>0)-(d<0))))
P("    signs t=0.21..0.50:", [s for _,s in sgn])
P("    distinct:", set(s for _,s in sgn))
# also (0.1,0.2] all three alive
sgn3=[int(((hr_frac(Fr(k,100),r,sl,"power2")-hr_frac(Fr(k,100),sv,sl,"power2"))>0)
          -((hr_frac(Fr(k,100),r,sl,"power2")-hr_frac(Fr(k,100),sv,sl,"power2"))<0))
      for k in range(11,21)]
P("    signs t=0.11..0.20 (all alive):", sgn3)

# ====================================================== Counterexample 2 ===
P("\n"+"="*72); P("CEX 2 (Thm 4): K2 at t=0.903, 0.990; power2")
r=(Fr(1,10),Fr(1,5),Fr(7,10)); lam=(Fr(9,10),Fr(4,5),Fr(3,5)); sv=(Fr(1,5),Fr(1,5),Fr(3,5))
chk("r NOT majorized by s (as they state)", not maj(r,sv))
sl=[(sig,l) for l in lam]
for t in (Fr(903,1000), Fr(99,100)):
    al=[(t-sig)/l<=1 for l in lam]
    hU,hV=hr_frac(t,r,sl,"power2"),hr_frac(t,sv,sl,"power2")
    P(f"    t={t}: alive={al} hU={hU} hV={hV} diff={hU-hV}")
    chk("K2 identically 0 (single alive comp)", hU==hV)
sgn=[]
for k in range(11,101):
    t=Fr(k,100)
    hU,hV=hr_frac(t,r,sl,"power2"),hr_frac(t,sv,sl,"power2")
    if hU is None: continue
    d=hU-hV
    if d!=0: sgn.append((t,int((d>0)-(d<0))))
P("    nonzero evals t=0.11..1.00:", sgn)

# ====================================================== Counterexample 3 ===
P("\n"+"="*72); P("CEX 3 (Thm 4): K3 at t=0.80, 0.77; pareto1")
# For pareto1: (1/lam)f(u)=lam/(x-sig)^2, Fbar=lam/(x-sig) when u>=1.
# h(x)= [S r_i lam_i]/(x-sig)^2 / [S r_i lam_i/(x-sig)] = 1/(x-sig) always.
r=(Fr(1,5),Fr(1,2),Fr(3,10)); lam=(Fr(3,5),Fr(1,5),Fr(3,10)); sv=(Fr(1,10),Fr(3,5),Fr(3,10))
chk("r m s", maj(r,sv))
sl=[(sig,l) for l in lam]
for t in (Fr(4,5), Fr(77,100), Fr(3,2), Fr(5)):
    hU,hV=hr_frac(t,r,sl,"pareto1"),hr_frac(t,sv,sl,"pareto1")
    P(f"    t={t}: hU={hU} hV={hV} diff={hU-hV}   1/(t-sig)={1/(t-sig)}")
    chk("K3 identically 0", hU==hV)
P("    => h(x)=1/(x-sig) for ANY weights/scales; +-2.2e-16 = FP noise.")

# ====================================================== Counterexample 4 ===
P("\n"+"="*72); P("CEX 4 (Thm 6): K4 at t=5 (>0), t=50 (<0); pareto2 lam=2")
lam=Fr(2)
r=(Fr(1,5),Fr(3,5),Fr(1,5)); sigv=(Fr(2,5),Fr(3,5),Fr(3,10)); sv=(Fr(1,10),Fr(1,5),Fr(7,10))
chk("r m s", maj(r,sv))
sl=[(si,lam) for si in sigv]
for t in (Fr(5), Fr(50)):
    rU,rV=rh_frac(t,r,sl,"pareto2"),rh_frac(t,sv,sl,"pareto2")
    P(f"    t={t}: rU={rU}  rV={rV}  diff={rU-rV} ~ {float(rU-rV):.6g}")
chk("K4(5)>0 and K4(50)<0 (genuine sign change)",
    rh_frac(Fr(5),r,sl,"pareto2")>rh_frac(Fr(5),sv,sl,"pareto2") and
    rh_frac(Fr(50),r,sl,"pareto2")<rh_frac(Fr(50),sv,sl,"pareto2"))

# ====================================================== Counterexample 5 ===
P("\n"+"="*72); P("CEX 5 (Thm 6): K5 at t=2.2003, 2.2083; pareto2 lam=2")
r=(Fr(1,10),Fr(3,10),Fr(3,5)); sigv=(Fr(3,5),Fr(2,5),Fr(1,5)); sv=(Fr(1,5),Fr(3,10),Fr(1,2))
chk("r NOT m s", not maj(r,sv))
sl=[(si,lam) for si in sigv]
for t in (Fr(22003,10000), Fr(22083,10000)):
    al=[t>=si+2 for si in sigv]
    rU,rV=rh_frac(t,r,sl,"pareto2"),rh_frac(t,sv,sl,"pareto2")
    P(f"    t={t}: alive={al} rU={rU} rV={rV} diff={rU-rV}")
    chk("K5 identically 0 (only comp3 alive)", rU==rV)
P("    genuine scan in (2.4,2.6] (comps 2,3) and (2.6,3.1] (all):")
sgn=[]
for k in range(241,311):
    t=Fr(k,100); d=rh_frac(t,r,sl,"pareto2")-rh_frac(t,sv,sl,"pareto2")
    sgn.append(int((d>0)-(d<0)))
P("    signs 2.41..3.10:", sgn, "distinct:", set(sgn))

# ====================================================== Counterexample 7 ===
P("\n"+"="*72); P("CEX 7 (Thm 11): burr3, T_0.3, sf sign change")
r=(Fr(1,5),Fr(4,5)); lam=(Fr(2,5),Fr(3,5)); sv=(Fr(31,50),Fr(19,50)); th=(Fr(27,50),Fr(23,50))
B=t_transform([list(r),list(lam)],0,1,Fr(3,10))
P("    [r;lam]T_0.3 =",B," ; claimed (s,th)=",[list(sv),list(th)])
chk("exact factorization", B[0]==list(sv) and B[1]==list(th))
chk("r in E2+ not D2+ (hypothesis fails)", in_E(r) and not in_D(r))
slU=[(Fr(0),l) for l in lam]; slV=[(Fr(0),l) for l in th]
sgn=[]
for k in range(1,60):
    t=Fr(k,20); d=sf_frac(t,r,slU,"burr3")-sf_frac(t,sv,slV,"burr3")
    sgn.append((t,int((d>0)-(d<0))))
P("    SF_U-SF_V signs t=0.05..2.95:", [(str(t),s) for t,s in sgn if s!=0][:20])
P("    distinct signs:", set(s for _,s in sgn))

# ====================================================== Example 1 =========
P("\n"+"="*72); P("EXAMPLE 1 (Thm 1): pareto1, 1/lam weak-supermaj 1/th")
sig=Fr(1,10)
r=(Fr(1,5),Fr(3,10),Fr(1,2)); lam=(Fr(1,10),Fr(2,5),Fr(4,5)); th=(Fr(1,5),Fr(1,2),Fr(4,5))
chk("1/lam w 1/th", weak_super([1/l for l in lam],[1/l for l in th]))
chk("r,lam in E3+", in_E(r) and in_E(lam))
slU=[(sig,l) for l in lam]; slV=[(sig,l) for l in th]
sgn=[(t,int(((sf_frac(t,r,slU,"pareto1")-sf_frac(t,r,slV,"pareto1"))>0)
            -((sf_frac(t,r,slU,"pareto1")-sf_frac(t,r,slV,"pareto1"))<0)))
     for t in [Fr(11,10),Fr(2),Fr(3),Fr(5),Fr(9),Fr(20)]]
P("    SF_U-SF_V:", sgn); chk("all <=0 (U<=stV)", all(s<=0 for _,s in sgn))

# ====================================================== Example 2 =========
P("\n"+"="*72); P("EXAMPLE 2 (Thm 6ii): pareto1 lam=2, sig=(.4,.2,.1)")
lam=Fr(2)
r=(Fr(1,5),Fr(3,10),Fr(1,2)); sv=(Fr(1,10),Fr(3,10),Fr(3,5)); sigv=(Fr(2,5),Fr(1,5),Fr(1,10))
chk("r,s in E3+, sig in D3+, r m s", in_E(r) and in_E(sv) and in_D(sigv) and maj(r,sv))
sl=[(si,lam) for si in sigv]
sgn=[]
for k in range(211,600,7):
    t=Fr(k,100); d=rh_frac(t,r,sl,"pareto1")-rh_frac(t,sv,sl,"pareto1")
    sgn.append(int((d>0)-(d<0)))
P("    r~_U-r~_V signs over 2.11..5.96 (claim >=0): distinct", set(sgn))
chk("claim U>=rhV on grid", all(s>=0 for s in sgn))

# ====================================================== Example 4 =========
P("\n"+"="*72); P("EXAMPLE 4 (Thm 8): IE F=e^{-2/t} -- mpmath check")
import mpmath as mp; mp.mp.dps=40
r=[mp.mpf("0.2"),mp.mpf("0.3"),mp.mpf("0.5")]; s=[mp.mpf("0.1"),mp.mpf("0.3"),mp.mpf("0.6")]
lam=[mp.mpf("10.2"),mp.mpf("8.3"),mp.mpf("5.2")]; th=[mp.mpf("12.5"),mp.mpf("9.8"),mp.mpf("4.3")]
sg=mp.mpf("0.1")
chk("r w s", weak_sub([Fr(1,5),Fr(3,10),Fr(1,2)],[Fr(1,10),Fr(3,10),Fr(3,5)]))
chk("lam w th", weak_sub([Fr(51,5),Fr(83,10),Fr(26,5)],[Fr(25,2),Fr(49,5),Fr(43,10)]))
def sfu(x,r_,lv): return sum(ri*(1-mp.e**(-2*li/(x-sg))) for ri,li in zip(r_,lv))
ds=[sfu(x,r,lam)-sfu(x,s,th) for x in (mp.mpf("0.2"),mp.mpf("0.5"),1,2,5,20,mp.mpf("100"))]
P("    SF_U-SF_V:", [mp.nstr(d,6) for d in ds]); chk("U>=stV (>=0)", all(d>=0 for d in ds))

# ====================================================== Example 5 =========
P("\n"+"="*72); P("EXAMPLE 5 (Thm 10): power c=3 l=2, lam=4")
lam=Fr(4)
r=(Fr(1,2),Fr(3,10),Fr(1,5)); sv=(Fr(3,5),Fr(3,10),Fr(1,10))
sigv=(Fr(4,5),Fr(7,10),Fr(2,5)); muv=(Fr(2,5),Fr(3,10),Fr(1,5))
chk("r m s (paper's hypothesis dir; eq49 needs r majorizes s)",
    maj(r,sv) and not maj(sv,r))
chk("max mu<=min sig", max(muv)<=min(sigv))
slU=[(si,lam) for si in sigv]; slV=[(mi,lam) for mi in muv]
bad=[]
for k in range(9,220,3):
    t=Fr(k,100); hU=hr_frac(t,r,slU,"power",3,2); hV=hr_frac(t,sv,slV,"power",3,2)
    if hU is None or hV is None: continue
    if hU>hV: bad.append(t)
P("    points h_U>h_V (violating U>=hrV):", bad[:10], f"total={len(bad)}")
sgn=[]
for t in [Fr(2,1),Fr(4),Fr(7),Fr(9),Fr(95,10),Fr(105,10)]:
    hU=hr_frac(t,r,slU,"power",3,2); hV=hr_frac(t,sv,slV,"power",3,2)
    if hU is None or hV is None: continue
    sgn.append((t,hU-hV))
P("    sample diffs h_U-h_V:", sgn)
