"""BKF2024 audit: certified counterexamples + verification of paper's own
examples/counterexamples.  All arithmetic exact (sympy Rational)."""
import sys, sympy as sp
sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/context/runs/bkf2024")
from bkf_lib import (BASELINES, make_power, comp_vals, mix_sf, mix_hr, mix_rh,
                     in_D, in_E, maj, weak_super, weak_sub, recip_maj,
                     t_transform, in_Mn)
R = sp.Rational
OUT = []

def P(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s); print(s)

def chk(name, cond):
    P(f"    [{ 'OK' if cond else 'FAIL'}] {name}")

# ============================================================ THEOREM 5 ====
# Claim: h increasing (IFR baseline), lam in Dn+ (En+) => U <=hr (>=hr) V.
# NO condition on r,s.  Proof eq(12): xi' = sum_ij s_i r_j Fbar_i Fbar_j
# (b_j - b_i), b_k=(1/lam_k)h(u_k).  Pair (i,j): factor (b_j-b_i)(s_i r_j -
# s_j r_i) -- unsigned unless s_i/r_i ordered.  Counterexample:
P("="*72)
P("THM 5 counterexample (missing r-s condition)")
P("="*72)
base = BASELINES["linhaz"]  # Fbar=(1-u)^2, h=2/(1-u) increasing on (0,1)
sig = R(1,10)
# (i) lam in D2+: claim U <=hr V
lam = (R(2), R(1)); r = (R(1,2), R(1,2)); sv = (R(1,10), R(9,10))
x = R(3,5)
sl = [(sig, l) for l in lam]
hU, hV = mix_hr(x, r, sl, base), mix_hr(x, sv, sl, base)
P(f"(i) lam={lam} in D2+, r={r}, s={sv}, x={x}")
chk("lam in D2+", in_D(lam))
P(f"    h_U={hU}  h_V={hV}  h_U-h_V={sp.cancel(hU-hV)}")
chk("U<=hrV claimed but h_U<h_V here", hU < hV)
# (ii) lam in E2+: claim U >=hr V i.e. h_U <= h_V; s on low-hazard comp2
lam2 = (R(1), R(2)); sv2 = (R(1,10), R(9,10))
sl2 = [(sig, l) for l in lam2]
hU2, hV2 = mix_hr(x, r, sl2, base), mix_hr(x, sv2, sl2, base)
P(f"(ii) lam={lam2} in E2+, r={r}, s={sv2}, x={x}")
chk("lam in E2+", in_E(lam2))
P(f"    h_U={hU2}  h_V={hV2}  h_U-h_V={sp.cancel(hU2-hV2)}")
chk("U>=hrV claimed but h_U>h_V here", hU2 > hV2)

# also certify the derivative-of-ratio sign directly (xi' < 0 at x=3/5)
x_ = sp.Symbol("x", positive=True)
u1, u2 = (x_-sig)/lam[0], (x_-sig)/lam[1]
Fb1, Fb2 = (1-u1)**2, (1-u2)**2
h1, h2 = 2/(1-u1), 2/(1-u2)
xi = (sv[0]*Fb1 + sv[1]*Fb2)/(r[0]*Fb1 + r[0]*Fb2) if False else \
     (sv[0]*Fb1 + sv[1]*Fb2)/(r[0]*Fb1 + r[1]*Fb2)
dxi = sp.cancel(sp.diff(xi, x_).subs(x_, x))
P(f"    xi=Fbar_V/Fbar_U: xi'(3/5) = {dxi} (sign {sp.sign(dxi)})")
chk("xi'(3/5)<0 so Fbar_V/Fbar_U not increasing -> U<=hrV fails", dxi < 0)

# ============================================================ THEOREM 4 ====
# Claim: f increasing, r in Dn+ (En+), lam in En+ (Dn+), r m s => U >=hr V.
# Defect: bounded support => dead components; proof's tau2>=0 fails for
# dead-alive pairs (f_dead = 0).  Middle-region subvector weights rhat_A vs
# shat_A are not majorization-controlled.
P("\n" + "="*72)
P("THM 4 counterexample (n=3, middle region)")
P("="*72)
base = BASELINES["power2"]  # f=2u increasing on (0,1]
sig = R(1,10)
# branch (D,E): r in D3+, lam in E3+
r   = (R(2,5), R(2,5), R(1,5))     # D3+
sv  = (R(1,2), R(3,10), R(1,5))    # D3+
lam = (R(1,4), R(1,2), R(1))       # E3+ ; support ends sig+lam_i = .35,.6,1.1
chk("r in D3+", in_D(r)); chk("s in D3+", in_D(sv)); chk("lam in E3+", in_E(lam))
chk("r majorized by s (r m s)", maj(r, sv))
x = R(1,2)  # comps {2,3} alive: u1=(0.4)/0.25=1.6>1 dead
sl = [(sig, l) for l in lam]
alive = [comp_vals(x, sig, l, base)["alive"] for l in lam]
chk("alive set {2,3} at x=1/2", alive == [False, True, True])
hU, hV = mix_hr(x, r, sl, base), mix_hr(x, sv, sl, base)
P(f"    x={x}: h_U={hU}={sp.nsimplify(hU)}  h_V={hV}  h_U-h_V={sp.cancel(hU-hV)}")
chk("claimed h_U<=h_V but h_U>h_V", hU > hV)
# branch (E,D): r in E3+, lam in D3+
r2  = (R(1,10), R(9,20), R(9,20))  # E3+
sv2 = (R(1,20), R(1,5), R(3,4))    # E3+
lam2= (R(1), R(1,2), R(1,4))       # D3+; ends 1.1,.6,.35 -> region .35,.6 = {1,2}
chk("r in E3+", in_E(r2)); chk("s in E3+", in_E(sv2)); chk("lam in D3+", in_D(lam2))
chk("r m s", maj(r2, sv2))
sl2 = [(sig, l) for l in lam2]
alive2 = [comp_vals(x, sig, l, base)["alive"] for l in lam2]
chk("alive set {1,2} at x=1/2", alive2 == [True, True, False])
hU2, hV2 = mix_hr(x, r2, sl2, base), mix_hr(x, sv2, sl2, base)
P(f"    x={x}: h_U={hU2}  h_V={hV2}  diff={sp.cancel(hU2-hV2)}")
chk("claimed h_U<=h_V but h_U>h_V", hU2 > hV2)
# n=2 sanity: r m s at n=2 (r=(3/10,7/10) is majorized by s=(1/4,3/4)):
P("    n=2 control: lam=(1/4,1/2) E2+, r=(7/10,3/10) m s=(3/4,1/4)")
lam3=(R(1,4),R(1,2)); r3=(R(7,10),R(3,10)); s3=(R(3,4),R(1,4))
chk("r in D2+, s in D2+, r m s", in_D(r3) and in_D(s3) and maj(r3,s3))
sl3=[(sig,l) for l in lam3]
xs=[R(1,8),R(1,5),R(3,10)]
diffs=[sp.cancel(mix_hr(xx,r3,sl3,base)-mix_hr(xx,s3,sl3,base)) for xx in xs]
P("    h_U-h_V at xs:", xs, "=", diffs)
chk("all <=0 (claim holds at n=2 on these points)", all(d<=0 for d in diffs))

# ============================================================ THEOREM 6 ====
# rh order, location mixture, common lam.  pareto2: f=2/u^3 decreasing.
P("\n" + "="*72)
P("THM 6 counterexamples (n=3, middle region)")
P("="*72)
base = BASELINES["pareto2"]   # support u>=1; comp i alive iff x>=sig_i+lam
lam = R(2); sig = (R(3), R(2), R(1))  # D3+; alive thresholds 5,4,3
chk("sigma in D3+", in_D(sig))
# (i) r in D3+, r m s, claim U <=rh V (r~_U <= r~_V)
r  = (R(2,5), R(2,5), R(1,5))
sv = (R(3,5), R(1,5), R(1,5))
chk("r,s in D3+", in_D(r) and in_D(sv)); chk("r m s", maj(r, sv))
x = R(9,2)  # in (sig_2+2, sig_1+2] = (4,5]: comps {2,3}
sl = [(si, lam) for si in sig]
alive = [comp_vals(x, si, lam, base)["alive"] for si in sig]
chk("alive set {2,3} at x=9/2", alive == [False, True, True])
rU, rV = mix_rh(x, r, sl, base), mix_rh(x, sv, sl, base)
P(f"    (i) x={x}: r~_U={rU}  r~_V={rV}  diff={sp.cancel(rU-rV)}")
chk("claimed r~_U<=r~_V but r~_U>r~_V", rU > rV)
# (ii) r in E3+, sigma in D3+, claim U >=rh V
r2  = (R(1,5), R(3,10), R(1,2))
sv2 = (R(1,10), R(2,5), R(1,2))
chk("r,s in E3+", in_E(r2) and in_E(sv2)); chk("r m s", maj(r2, sv2))
rU2, rV2 = mix_rh(x, r2, sl, base), mix_rh(x, sv2, sl, base)
P(f"    (ii) x={x}: r~_U={rU2}  r~_V={rV2}  diff={sp.cancel(rU2-rV2)}")
chk("claimed r~_U>=r~_V but r~_U<r~_V", rU2 < rV2)

# ============================================================ THEOREM 2 ====
P("\n" + "="*72)
P("THM 2 counterexample (printed lam _w th direction)")
P("="*72)
sig=R(1,10); base=BASELINES["burr3"]
r=(R(1,5),R(2,5),R(2,5)); lam=(R(2),R(1,2),R(1,5)); th=(R(2),R(1),R(2,3))
chk("r in E3+", in_E(r)); chk("lam,th in D3+", in_D(lam) and in_D(th))
chk("lam _w th (weak submaj)", weak_sub(lam,th))
x=R(1,4); d=mix_sf(x,r,[(sig,l) for l in lam],base)-mix_sf(x,r,[(sig,l) for l in th],base)
P(f"    x=1/4: SF_U-SF_V = {d}  (claim >=st i.e. >=0)")
chk("U>=stV claimed but SF_U<SF_V", d<0)

# ============================================================ THEOREM 3 ====
P("\n" + "="*72)
P("THM 3 counterexample (lam rm th, INTERIOR, all alive)")
P("="*72)
sig=R(1,10); base=BASELINES["power2"]
r=(R(1,2),R(3,10),R(1,5)); lam=(R(1,10),R(2,5),R(7,10)); th=(R(1,10),R(3,10),R(3,5))
chk("r in D3+",in_D(r)); chk("lam,th in E3+",in_E(lam) and in_E(th))
chk("lam rm th", recip_maj(lam,th))
x=R(3,20)
chk("all alive at x=3/20", all(0<(x-sig)/l<=1 for l in lam+th))
d=mix_sf(x,r,[(sig,l) for l in lam],base)-mix_sf(x,r,[(sig,l) for l in th],base)
P(f"    x=3/20: SF_U-SF_V = {d}  (claim <=st i.e. <=0)")
chk("U<=stV claimed but SF_U>SF_V", d>0)

# ============================================================ THEOREM 8 ====
P("\n" + "="*72)
P("THM 8 counterexample (printed _w direction, lam-side)")
P("="*72)
sig=R(1,10); base=BASELINES["burr3"]
r=(R(1,3),R(1,3),R(1,3)); s=(R(1,4),R(1,4),R(1,2))
lam=(R(2),R(3,4),R(1,4)); th=(R(2),R(3,4),R(1,2))
chk("r,s in E3+", in_E(r) and in_E(s)); chk("lam,th in D3+", in_D(lam) and in_D(th))
chk("r _w s", weak_sub(r,s)); chk("lam _w th", weak_sub(lam,th))
x=R(1,4); d=mix_sf(x,r,[(sig,l) for l in lam],base)-mix_sf(x,s,[(sig,l) for l in th],base)
P(f"    x=1/4: SF_U-SF_V = {d}  (claim >=st i.e. >=0)")
chk("U>=stV claimed but SF_U<SF_V", d<0)
d2=mix_sf(x,s,[(sig,l) for l in lam],base)-mix_sf(x,s,[(sig,l) for l in th],base)
P(f"    lam->th step alone (s fixed): SF_W-SF_V = {d2} (needs >=0)")
d1=mix_sf(x,r,[(sig,l) for l in lam],base)-mix_sf(x,s,[(sig,l) for l in lam],base)
P(f"    r->s step alone (lam fixed): SF_U-SF_W = {d1} (needs >=0)")
chk("failing step is the lam-side", d2<0 and d1>=0)

# ============================================================ THEOREM 1 ====
P("\n" + "="*72)
P("THM 1 boundary counterexample (below-support truncation)")
P("="*72)
sig=R(1,10); base=BASELINES["pareto1"]
r=(R(1,6),R(1,6),R(2,3)); lam=(R(1,5),R(3,5),R(1)); th=(R(1,5),R(1,2),R(3,2))
chk("r,lam,th in E3+", in_E(r) and in_E(lam) and in_E(th))
il=[1/l for l in lam]; it=[1/l for l in th]
chk("1/lam ^w 1/th (weak supermaj)", weak_super(il,it))
x=R(11,10); d=mix_sf(x,r,[(sig,l) for l in lam],base)-mix_sf(x,r,[(sig,l) for l in th],base)
P(f"    x=11/10: SF_U-SF_V = {d}  (claim <=st i.e. <=0); V comp3 u=2/3<1 -> Fbar=1")
chk("U<=stV claimed but SF_U>SF_V", d>0)

# ============================================================ THEOREM 10 ====
# hr, location+weights.  power c=3,l=2: f inc, h~=f/F=c/t dec. lam=4.
# eq(49) needs Schur-concave h + r majorizing s (r m s).  Their Example 5
# uses r=(.5,.3,.2), s=(.6,.3,.1): s is MORE spread -> r m s actually.
P("\n" + "="*72)
P("THM 10 probes (power c=3 l=2, lam=4)")
P("="*72)
base = make_power(3, 2); lam = R(4)
sig = (R(3), R(2), R(1)); mu = (R(1,2), R(1,3), R(1,4))
chk("max mu <= min sig", max(mu) <= min(sig))
# paper's own Example-5 weights: r m s (NOT r majorizing s)
r_ex, s_ex = (R(1,2),R(3,10),R(1,5)), (R(3,5),R(3,10),R(1,10))
P(f"    Ex5 params: r={r_ex}, s={s_ex}")
chk("r m s holds (paper needs r majorizes s for Schur-concavity)",
    maj(r_ex, s_ex) and not maj(s_ex, r_ex))
# search violations of h_U<=h_V (the U >=hr V claim) under BOTH readings:
#   maj(r_,s_) True  <=> r m s  (paper Ex-5 direction; Schur-concave would
#                      give h_U >= h_W -- opposite of eq(49))
#   maj(s_,r_) True  <=> r majorizes s  (what eq(49) needs)
import itertools
from fractions import Fraction as Fr
from bkf_lib import hr_frac
# (a) eq(49) step: h_U(r;sig) vs h_W(s;sig).  (b) theorem conclusion:
# U(r;sig) vs V(s;mu) with constant mu=(1,1,1) (<= min sig, admissible).
viol_lit, n_lit, viol_proof, n_proof = 0,0,0,0
violV_lit, violV_proof = 0,0
ex_lit = ex_proof = exV_lit = exV_proof = None
muv = (Fr(1),Fr(1),Fr(1)); lamF = Fr(4)
gridx=[Fr(21,10),Fr(5,2),Fr(4),Fr(5),Fr(7),Fr(19,2),Fr(21,2)]
sl_sig=[(si,lamF) for si in [Fr(3),Fr(2),Fr(1)]]; sl_mu=[(mi,lamF) for mi in muv]
for ra in itertools.product(range(1,9), repeat=3):
    r_=tuple(Fr(a,sum(ra)) for a in ra)
    if not in_D(r_): continue
    for sa in itertools.product(range(1,9), repeat=3):
        s_=tuple(Fr(a,sum(sa)) for a in sa)
        if not in_D(s_): continue
        r_le_s, r_ge_s = maj(r_,s_), maj(s_,r_)
        if not (r_le_s or r_ge_s): continue
        for xx in gridx:
            hU=hr_frac(xx,r_,sl_sig,"power",c=3,l=2)
            hW=hr_frac(xx,s_,sl_sig,"power",c=3,l=2)
            hV=hr_frac(xx,s_,sl_mu,"power",c=3,l=2)
            if hU is None or hW is None or hV is None: continue
            if r_le_s:
                n_lit+=1
                if hU>hW: viol_lit+=1; ex_lit=ex_lit or (r_,s_,xx,hU,hW)
                if hU>hV: violV_lit+=1; exV_lit=exV_lit or (r_,s_,xx,hU,hV)
            if r_ge_s:
                n_proof+=1
                if hU>hW: viol_proof+=1; ex_proof=ex_proof or (r_,s_,xx,hU,hW)
                if hU>hV: violV_proof+=1; exV_proof=exV_proof or (r_,s_,xx,hU,hV)
P(f"    eq49 h_U<=h_W, r m s (Ex5 dir): {n_lit} evals, viol={viol_lit}, e.g. {ex_lit}")
P(f"    eq49 h_U<=h_W, r majorizes s: {n_proof} evals, viol={viol_proof}, e.g. {ex_proof}")
P(f"    thm   h_U<=h_V, r m s (Ex5 dir): viol={violV_lit}, e.g. {exV_lit}")
P(f"    thm   h_U<=h_V, r majorizes s: viol={violV_proof}, e.g. {exV_proof}")
