"""Bounded admissible-instance scan for BKF2024 theorems. All-Fraction, exact.
Reports admissible counts and violation counts (with first examples)."""
import sys, itertools, random
sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/context/runs/bkf2024")
from fractions import Fraction as Fr
from bkf_lib import hr_frac, rh_frac, sf_frac, in_D, in_E, maj, weak_super, \
    weak_sub, recip_maj, t_transform, in_Mn

def P(*a): print(" ".join(str(x) for x in a), flush=True)
random.seed(20240926)

def randp(n, pool):  # sorted prob vector (Fractions summing 1) in D or E
    while True:
        v = [random.choice(pool) for _ in range(n)]
        s = sum(v)
        return tuple(Fr(a, s) for a in v)

def scan_st(name, gen, n_pts=6, base="burr3", xgrid=None):
    """gen() -> (r,lam,s,th,sig) or None; test Fbar_U <= Fbar_V claimed."""
    ok=viol=0; ex=None
    for _ in range(4000):
        inst = gen()
        if inst is None: continue
        ok += 1
        r, lam, s, th, sig = inst
        slU=[(sig,l) for l in lam]; slV=[(sig,l) for l in th]
        for x in (xgrid or [Fr(1,4),Fr(1,2),Fr(1),Fr(2),Fr(4),Fr(8)]):
            d = sf_frac(x,r,slU,base)-sf_frac(x,s,slV,base)
            if d>0: viol+=1; ex=ex or (r,lam,s,th,x,d)
    P(f"{name}: admissible={ok}, x-evals w/ violation={viol}, e.g. {ex}")

# ---------------- Thm 1: tf dec (pareto1), 1/lam w 1/th, r,lam in E+ or D+ --
def gen_th1():
    n=3
    r = randp(n,[1,2,3,4,5,6,7,8])
    lam = tuple(sorted([random.choice([Fr(1,10),Fr(1,5),Fr(2,5),Fr(3,5),Fr(1,2),Fr(4,5),Fr(1),Fr(3,2),Fr(2)]) for _ in range(n)]))
    th  = tuple(sorted([random.choice([Fr(1,10),Fr(1,5),Fr(2,5),Fr(3,5),Fr(1,2),Fr(4,5),Fr(1),Fr(3,2),Fr(2)]) for _ in range(n)]))
    if not (in_E(r) and in_E(lam)): return None
    il=[1/l for l in lam]; it=[1/l for l in th]
    if not weak_super(il,it): return None
    return r,lam,r,th,Fr(1,10)   # same weights r (Thm 1)
P("--- Thm 1 (st, pareto1, 1/lam w 1/th): claim U<=stV")
scan_st("Thm1", gen_th1, base="pareto1", xgrid=[Fr(11,10),Fr(3,2),Fr(2),Fr(3),Fr(5),Fr(9),Fr(20)])

# ---------------- Thm 2: t^2f inc (burr3), lam w th ------------------------
LAMPOOL=[Fr(1,5),Fr(1,4),Fr(1,3),Fr(1,2),Fr(2,3),Fr(3,4),Fr(1),Fr(4,3),Fr(3,2),Fr(2),Fr(3)]
def gen_th2():
    n=3
    r = tuple(sorted(randp(n,[1,2,3,4,5,6])))            # r in E_n^+
    lam = tuple(sorted(random.sample(LAMPOOL,n),reverse=True))  # D_n^+
    th  = tuple(sorted(random.sample(LAMPOOL,n),reverse=True))  # D_n^+
    if not weak_sub(lam,th): return None
    return r,lam,r,th,Fr(1,10)
P("--- Thm 2 (st, burr3, lam w th): claim U>=stV i.e. SF_U-SF_V>=0")
# printed symbol is _w (weak submajorization).  Claim: SF_U>=SF_V.
a=v=0; ex=None; exw=None
for _ in range(4000):
    inst=gen_th2()
    if inst is None: continue
    r,lam,s,th,sig=inst; a+=1
    slU=[(sig,l) for l in lam]; slV=[(sig,l) for l in th]
    for x in [Fr(1,4),Fr(1,2),Fr(1),Fr(2),Fr(4),Fr(8),Fr(16)]:
        d=sf_frac(x,r,slU,"burr3")-sf_frac(x,r,slV,"burr3")
        if d<0: v+=1; ex=ex or (r,lam,th,x,d); break
P(f"    printed _w reading: admissible={a} violations={v} e.g. {ex}")
# alternative ^w (weak supermaj) reading -- same (E,D) pairing
a=v=0; ex=None
for _ in range(20000):
    r = tuple(sorted(randp(3,[1,2,3,4,5,6])))
    lam = tuple(sorted(random.sample(LAMPOOL,3),reverse=True))
    th  = tuple(sorted(random.sample(LAMPOOL,3),reverse=True))
    if not weak_super(lam,th): continue
    a+=1; sig=Fr(1,10)
    slU=[(sig,l) for l in lam]; slV=[(sig,l) for l in th]
    for x in [Fr(1,4),Fr(1,2),Fr(1),Fr(2),Fr(4),Fr(8),Fr(16)]:
        d=sf_frac(x,r,slU,"burr3")-sf_frac(x,r,slV,"burr3")
        if d<0: v+=1; ex=ex or (r,lam,th,x,d); break
P(f"    ^w-reading check: admissible={a} violations={v} e.g. {ex}")

# ---------------- Thm 3: f inc (power2), lam rm th, anti-paired -----------
def gen_th3():
    n=3
    r = tuple(sorted(randp(n,[1,2,3,4,5]), reverse=True))   # r in D3+
    lam = tuple(sorted(random.sample([Fr(1,10),Fr(1,5),Fr(3,10),Fr(2,5),Fr(1,2),Fr(3,5),Fr(7,10),Fr(4,5)],n)))  # E
    th  = tuple(sorted(random.sample([Fr(1,10),Fr(1,5),Fr(3,10),Fr(2,5),Fr(1,2),Fr(3,5),Fr(7,10),Fr(4,5)],n)))  # E
    if not recip_maj(lam,th): return None
    return r,lam,r,th,Fr(1,10)
P("--- Thm 3 (st, power2, lam rm th): claim U<=stV")
scan_st("Thm3", gen_th3, base="power2", xgrid=[Fr(1,4),Fr(1,2),Fr(3,5),Fr(4,5),Fr(9,10),Fr(1)])

# ---------------- Thm 4: f inc (power2), r m s, (r,lam) aligned -----------
P("--- Thm 4 (hr, power2): claim r m s => U>=hrV (h_U<=h_V)")
cnt={2:dict(a=0,v=0,ex=None),3:dict(a=0,v=0,ex=None),4:dict(a=0,v=0,ex=None)}
for n in (2,3,4):
  for _ in range(3000):
    r_=randp(n,[1,2,3,4,5,6,7]); s_=randp(n,[1,2,3,4,5,6,7])
    lam=tuple(sorted(random.sample([Fr(1,5),Fr(1,4),Fr(1,3),Fr(1,2),Fr(2,3),Fr(3,4),Fr(1),Fr(4,3),Fr(3,2),Fr(2),Fr(5,2)],n)))
    if not (maj(r_,s_) and in_D(r_) and in_D(s_) and in_E(lam)): continue
    cnt[n]["a"]+=1
    sig=Fr(1,10); sl=[(sig,l) for l in lam]
    # x grid covering all regions: support ends at sig+lam_i
    xs=[sig+l*Fr(1,2) for l in lam]+[sig+l*Fr(9,10) for l in lam]+[sig+l*Fr(1,20) for l in lam]
    bad=False
    for x in xs:
        d=hr_frac(x,r_,sl,"power2")-hr_frac(x,s_,sl,"power2")
        if d is not None and d>0: bad=True
    if bad: cnt[n]["v"]+=1; cnt[n]["ex"]=cnt[n]["ex"] or (r_,s_,lam)
for n,d in cnt.items():
    P(f"    n={n}: admissible={d['a']} violations={d['v']} e.g. {d['ex']}")

# ---------------- Thm 5: h inc (linhaz), lam in D+ or E+ --------------------
P("--- Thm 5 (hr, linhaz): claim lam in D+ => U<=hrV; lam in E+ => U>=hrV")
for mode,lsort,claim in (("D",True,"h_U>=h_V"),("E",False,"h_U<=h_V")):
    a=v=0; ex=None
    for _ in range(3000):
        n=2
        r_=randp(n,[1,2,3,4,5,6,7]); s_=randp(n,[1,2,3,4,5,6,7])
        lam=tuple(sorted(random.sample([Fr(1,4),Fr(1,2),Fr(3,4),Fr(1),Fr(5,4),Fr(3,2),Fr(2),Fr(3)],n),reverse=lsort))
        sig=Fr(1,10); sl=[(sig,l) for l in lam]
        for x in [Fr(1,5),Fr(2,5),Fr(3,5),Fr(4,5),Fr(1),Fr(6,5),Fr(8,5),Fr(2)]:
            hU=hr_frac(x,r_,sl,"linhaz"); hV=hr_frac(x,s_,sl,"linhaz")
            if hU is None or hV is None: continue
            a+=1
            if (claim=="h_U>=h_V" and hU<hV) or (claim=="h_U<=h_V" and hU>hV):
                v+=1; ex=ex or (r_,s_,lam,x,hU,hV)
    P(f"    lam in {'D' if lsort else 'E'}2+, claim {claim}: evals={a} viol={v} e.g. {ex}")

# ---------------- Thm 6: f dec (pareto2), location, common lam --------------
P("--- Thm 6 (rh, pareto2): (i) r,s in D+, sig in D+, r m s => U<=rhV")
lamF=Fr(2)
for part in ("i","ii"):
    a=v=0; ex=None
    for _ in range(4000):
        n=3
        r_=randp(n,[1,2,3,4,5,6,7]); s_=randp(n,[1,2,3,4,5,6,7])
        sigv=tuple(sorted(random.sample([Fr(1),Fr(3,2),Fr(2),Fr(5,2),Fr(3),Fr(7,2),Fr(4),Fr(1,2)],n),reverse=True))
        need = in_D(r_) and in_D(s_) if part=="i" else in_E(r_) and in_E(s_)
        if not (need and maj(r_,s_) and in_D(sigv)): continue
        a+=1
        sl=[(si,lamF) for si in sigv]
        # regions: comp i alive iff x>=sig_i+2
        xs=[sigv[i]+Fr(2)+Fr(1,10) for i in range(n)]+[sigv[0]+Fr(2)+Fr(1,10)]+[sigv[-1]+Fr(2)+Fr(3,10)]
        for x in xs:
            rU=rh_frac(x,r_,sl,"pareto2"); rV=rh_frac(x,s_,sl,"pareto2")
            if rU is None or rV is None: continue
            d=rU-rV
            if (part=="i" and d>0) or (part=="ii" and d<0):
                v+=1; ex=ex or (r_,s_,sigv,x,d); break
    P(f"    part ({part}): admissible={a} violations={v} e.g. {ex}")

# ---------------- Thm 8: st, r w s, lam w th (burr3/IE) -------------------
P("--- Thm 8 (st, burr3): r w s, lam w th, r,s in E+, lam,th in D+ => U>=stV")
a=v=0; ex=None
for _ in range(4000):
    r_=randp(3,[1,2,3,4,5]); s_=randp(3,[1,2,3,4,5])
    lam=tuple(sorted(random.sample([Fr(1,4),Fr(1,2),Fr(3,4),Fr(1),Fr(3,2),Fr(2),Fr(5,2),Fr(3)],3),reverse=True))
    th =tuple(sorted(random.sample([Fr(1,4),Fr(1,2),Fr(3,4),Fr(1),Fr(3,2),Fr(2),Fr(5,2),Fr(3)],3),reverse=True))
    if not (in_E(r_) and in_E(s_) and weak_sub(r_,s_) and weak_sub(lam,th)): continue
    a+=1; sig=Fr(1,10)
    slU=[(sig,l) for l in lam]; slV=[(sig,l) for l in th]
    for x in [Fr(1,4),Fr(1,2),Fr(1),Fr(2),Fr(4),Fr(8),Fr(16)]:
        d=sf_frac(x,r_,slU,"burr3")-sf_frac(x,s_,slV,"burr3")
        if d<0: v+=1; ex=ex or (r_,s_,lam,th,x,d); break
P(f"    admissible={a} violations={v} e.g. {ex}")

# ---------------- Thm 9: st, location, r m s, sig w mu, max sig<=min mu ---
P("--- Thm 9 (st, pareto1): r m s, sig w mu, r,sig in E+, max sig<=min mu")
lamF=Fr(1)
a=v=0; ex=None
for _ in range(4000):
    r_=randp(3,[1,2,3,4,5]); s_=randp(3,[1,2,3,4,5])
    sigv=tuple(sorted(random.sample([Fr(1,2),Fr(1),Fr(3,2),Fr(2),Fr(5,2)],3)))
    muv =tuple(sorted(random.sample([Fr(7,2),Fr(4),Fr(9,2),Fr(5),Fr(6)],3)))
    if not (in_E(r_) and in_E(s_) and maj(r_,s_) and weak_sub(sigv,muv)
            and max(sigv)<=min(muv)): continue
    a+=1
    slU=[(si,lamF) for si in sigv]; slV=[(mi,lamF) for mi in muv]
    for x in [Fr(2),Fr(5,2),Fr(3),Fr(4),Fr(6),Fr(8),Fr(12),Fr(20)]:
        d=sf_frac(x,r_,slU,"pareto1")-sf_frac(x,s_,slV,"pareto1")
        if d>0: v+=1; ex=ex or (r_,s_,sigv,muv,x,d); break
P(f"    admissible={a} violations={v} e.g. {ex}")

# ---------------- Thms 11-13/Cor2: st under T-transforms -------------------
P("--- Thm 11/12 (st, T-transform): burr3 + pareto1")
for base in ("burr3","pareto1"):
    for n in (2,3):
        a=v=0; ex=None
        for _ in range(4000):
            r_=randp(n,[1,2,3,4,5])
            lam=tuple(sorted(random.sample([Fr(1,5),Fr(1,4),Fr(1,3),Fr(1,2),Fr(3,4),Fr(1),Fr(4,3),Fr(3,2),Fr(2),Fr(3)],n)))
            if not (in_D(r_) and in_E(lam)): continue  # M_n antiordered
            i,j=sorted(random.sample(range(n),2)); om=Fr(random.randint(1,19),20)
            B=t_transform([list(r_),list(lam)],i,j,om)
            s_,th=tuple(B[0]),tuple(B[1])
            if not (all(x>0 for x in s_) and all(x>0 for x in th)): continue
            if not in_Mn(list(r_),list(lam)): continue
            a+=1; sig=Fr(1,10)
            slU=[(sig,l) for l in lam]; slV=[(sig,l) for l in th]
            xs=[Fr(1,4),Fr(1,2),Fr(1),Fr(2),Fr(4),Fr(8)]
            for x in xs:
                d=sf_frac(x,r_,slU,base)-sf_frac(x,s_,slV,base)
                if d>0: v+=1; ex=ex or (r_,s_,lam,th,i,j,om,x,d); break
        P(f"    base={base} n={n}: admissible={a} viol={v} e.g.{ex}")

# ---------------- Thm 10 conclusion: wider mu scan ---------------------------
P("--- Thm 10 conclusion (hr, power c=3 l=2): U>=hrV means h_U<=h_V")
lamF=Fr(4)
a=v_lit=v_prf=0; exl=exp=None
mus=[ (Fr(1),)*3, (Fr(1,2),Fr(1,3),Fr(1,4)), (Fr(3,4),Fr(1,2),Fr(1,4)),
      (Fr(1),Fr(1,2),Fr(1,2)), (Fr(4,5),Fr(3,5),Fr(1,5)) ]
sigs=[ (Fr(3),Fr(2),Fr(1)), (Fr(5),Fr(3),Fr(2)), (Fr(4),Fr(5,2),Fr(3,2)) ]
for sigv in sigs:
  for muv in mus:
    if max(muv)>min(sigv): continue
    slU=[(si,lamF) for si in sigv]; slV=[(mi,lamF) for mi in muv]
    xs=set()
    for si in sigv:
        for q in (Fr(1,10),Fr(1,2),Fr(9,10)):
            xs.add(si+q); xs.add(si+8+q)
    for mi in muv:
        for q in (Fr(1,10),Fr(1,2)): xs.add(mi+q)
    xs=sorted(xs)
    for ra in itertools.product(range(1,8),repeat=3):
        r_=tuple(Fr(x,sum(ra)) for x in ra)
        if not in_D(r_): continue
        for sa in itertools.product(range(1,8),repeat=3):
            s_=tuple(Fr(x,sum(sa)) for x in sa)
            if not in_D(s_): continue
            lit,prf=maj(r_,s_),maj(s_,r_)
            if not(lit or prf): continue
            a+=1
            for x in xs:
                hU=hr_frac(x,r_,slU,"power",3,2); hV=hr_frac(x,s_,slV,"power",3,2)
                if hU is None or hV is None: continue
                if hU>hV:
                    if lit: v_lit+=1; exl=exl or (r_,s_,sigv,muv,x,hU,hV)
                    if prf: v_prf+=1; exp=exp or (r_,s_,sigv,muv,x,hU,hV)
P(f"    evals={a}; r m s viol={v_lit} e.g.{exl}; r majorizes s viol={v_prf} e.g.{exp}")

# ---------------- Cex 4 / Cex 7 wide scans -----------------------------------
P("--- Cex4: does K4 sign change anywhere? pareto2 lam=2 sig=(.4,.6,.3)")
lam=Fr(2); r=(Fr(1,5),Fr(3,5),Fr(1,5)); sv=(Fr(1,10),Fr(1,5),Fr(7,10))
sl=[(si,lam) for si in (Fr(2,5),Fr(3,5),Fr(3,10))]
negpos=[]
for k in list(range(230,2000,17))+[5000,10000]:
    t=Fr(k,100)
    rU=rh_frac(t,r,sl,"pareto2"); rV=rh_frac(t,sv,sl,"pareto2")
    if rU is None or rV is None: continue
    d=rU-rV
    if d<0: negpos.append((t,d))
P("    t in 2.3..100 step .17 + 50,100: negative K4 points:",negpos[:10],
  f"count={len(negpos)}")
P("--- Cex7: burr3 sf diff on fine grid")
r=(Fr(1,5),Fr(4,5)); lam=(Fr(2,5),Fr(3,5)); sv=(Fr(31,50),Fr(19,50)); th=(Fr(27,50),Fr(23,50))
slU=[(Fr(0),l) for l in lam]; slV=[(Fr(0),l) for l in th]
mn=None; sgnset=set()
for k in range(1,4000):
    t=Fr(k,500)
    d=sf_frac(t,r,slU,"burr3")-sf_frac(t,sv,slV,"burr3")
    s=(d>0)-(d<0); sgnset.add(s)
    if d<0 and (mn is None or d<mn): mn=d
P(f"    sign set over t=0.002..8: {sgnset}, min diff={mn}")
