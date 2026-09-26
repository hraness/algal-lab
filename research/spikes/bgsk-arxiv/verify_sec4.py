"""Verify BGSK Section-4 examples/counterexamples + Thm 4.1 both-direction scan
+ counterexample bookkeeping (unnormalized weights check)."""
import sympy as sp, random
x = sp.Symbol('x')
R = sp.Rational


def lomax(k, a):
    F = lambda u: 1 - ((1+u)/(1+a))**(-k)
    f = lambda u: k*(1+a)**k/(1+u)**(k+1)
    return F, f

def burr_trunc(p, q, a):
    F = lambda u: 1 - ((1+u**p)/(1+a**p))**(-q)
    f = lambda u: sp.nsimplify(p*q)*(1+a**p)**q*u**(p-1)/(1+u**p)**(q+1)
    return F, f

def loglog(k):
    F = lambda u: u**k/(1+u**k)
    f = lambda u: sp.nsimplify(k)*u**(k-1)/(1+u**k)**2
    return F, f


def rh2(xv, n, r, al, sg, lm, c, F, f):
    """h~ of 2-type MRV at xv."""
    n1, n2 = n; r1, r2 = r
    num = den = 0
    for ni, ri, ai, si, li in ((n1, r1, al[0], sg[0], lm[0]),
                               (n2, r2, al[1], sg[1], lm[1])):
        if xv > si + c*li:
            u = (xv - si)/li
            num += ni*ri*(ai/li)*F(u)**(ai-1)*f(u)
            den += ni*ri*F(u)**ai
    return num/den if den != 0 else sp.nan

def pdf2(xv, n, r, al, sg, lm, c, F, f):
    n1, n2 = n; r1, r2 = r
    tot = 0
    for ni, ri, ai, si, li in ((n1, r1, al[0], sg[0], lm[0]),
                               (n2, r2, al[1], sg[1], lm[1])):
        if xv > si + c*li:
            u = (xv - si)/li
            tot += ni*ri*(ai/li)*F(u)**(ai-1)*f(u)
    return tot


out = []
def rep(k, v): out.append((k, v)); print(k, ":", v, flush=True)


# ---- weight normalization checks (Assumption 4.1: n1 r1 + n2 r2 = 1) -------
rep("Ex5.5 weights", 25*R('0.032')+8*R('0.025'))            # 1
rep("Ex5.5 weights*", 15*R('0.020')+20*R('0.035'))          # 1
rep("Cex5.7 weights", 10*R('0.03')+10*R('0.04'))            # 0.7 !
rep("Cex5.7 weights*", 7*R('0.01')+3*R('0.01'))             # 0.1 !
rep("Ex5.6 weights", 15*R('0.04')+5*R('0.08'))              # 1
rep("Ex5.6 weights*", 10*R('0.08')+20*R('0.01'))            # 1
rep("Cex5.8 weights", 10*R('0.05')+25*R('0.02'))            # 1
rep("Cex5.8 weights*", 7*R('0.01')+3*R('0.01'))             # 0.1 !
rep("Ex5.7 weights", 10*R('0.02')+8*R('0.10'))              # 1
rep("Ex5.7 weights*", 20*R('0.02')+15*R('0.04'))            # 1
rep("Cex5.9 weights", 4*R('0.1')+6*R('0.1'))                # 1
rep("Cex5.9 weights*", 10*R('0.05')+25*R('0.02'))           # 1

# ---- Ex 5.5 (Thm 4.1): Burr XII p=3/2,q=5,a=2,c=2 --------------------------
F, f = burr_trunc(R(3,2), 5, 2)
n, ns = (25, 8), (15, 20)
r, s_ = (R('0.032'), R('0.025')), (R('0.020'), R('0.035'))
sg, lm, al = (5, 10), (4, 6), (R('2.3'), 4)
bad = []
for k in range(60, 400):
    xv = R(k, 4)
    hU = rh2(xv, n, r, al, sg, lm, 2, F, f)
    hV = rh2(xv, ns, s_, al, sg, lm, 2, F, f)
    if hU is not sp.nan and hU > hV:
        bad.append((xv, sp.N(hU, 15), sp.N(hV, 15)))
rep("Ex5.5 rh holds on grid", f"{len(bad)} violations")

# ---- Cex 5.7: Burr XII p=2,q=1,a=3,c=3; weights unnormalized ---------------
F, f = burr_trunc(2, 1, 3)
n, ns = (10, 10), (7, 3)
r, s_ = (R('0.03'), R('0.04')), (R('0.01'), R('0.01'))
sg, lm, al = (4, 9), (R('0.6'), 8), (6, 2)
bad = []
for k in range(60, 800):
    xv = R(k, 8)
    hU = rh2(xv, n, r, al, sg, lm, 3, F, f)
    hV = rh2(xv, ns, s_, al, sg, lm, 3, F, f)
    if hU is not sp.nan and hV is not sp.nan and hU > hV:
        bad.append(xv)
rep("Cex5.7 rh-fail witness", f"{len(bad)} pts hU>hV; first={bad[0] if bad else None}")

# ---- Ex 5.6 (Thm 4.2!): Lomax k=5 a=6 -- EXACT ------------------------------
F, f = lomax(5, 6)
n, ns = (15, 5), (10, 20)
r, s_ = (R('0.04'), R('0.08')), (R('0.08'), R('0.01'))
sg, lm, al = (3, 4), (1, 2), (2, 4)
# xi(x) = f_U/f_{U*} should be increasing for x>9. On (9,16] const; check x>16.
u1 = (x - sg[0])/lm[0]; u2 = (x - sg[1])/lm[1]
fU = n[0]*r[0]*(al[0]/lm[0])*F(u1)**(al[0]-1)*f(u1) + n[1]*r[1]*(al[1]/lm[1])*F(u2)**(al[1]-1)*f(u2)
fV = ns[0]*s_[0]*(al[0]/lm[0])*F(u1)**(al[0]-1)*f(u1) + ns[1]*s_[1]*(al[1]/lm[1])*F(u2)**(al[1]-1)*f(u2)
xi = sp.cancel(sp.together(fU/fV))
xip = sp.cancel(sp.together(sp.diff(xi, x)))
num, den = sp.fraction(xip); num, den = sp.expand(num), sp.expand(den)
num = num.xreplace({c: sp.nsimplify(c) for c in num.atoms(sp.Float)})
den = den.xreplace({c: sp.nsimplify(c) for c in den.atoms(sp.Float)})
pn, pd = sp.Poly(num, x), sp.Poly(den, x)
rep("Ex5.6 xi' certificate", f"num deg {pn.degree()}, roots(16,oo)={pn.count_roots(16, sp.oo)}, den roots(16,oo)={pd.count_roots(16, sp.oo)}, sign(20)={sp.sign(num.subs(x,20))}, sign(100)={sp.sign(num.subs(x,100))}")

# ---- Cex 5.8: Lomax k=3 a=2; alpha=(0.2,0.7) fractional -> numeric ---------
F, f = lomax(3, 2)
n, ns = (10, 25), (7, 3)
r, s_ = (R('0.05'), R('0.02')), (R('0.01'), R('0.01'))
sg, lm, al = (3, 4), (2, 4), (R('0.2'), R('0.7'))
xis = []
for k in range(40, 400):
    xv = R(k, 4)
    fU = pdf2(xv, n, r, al, sg, lm, 2, F, f)
    fV = pdf2(xv, ns, s_, al, sg, lm, 2, F, f)
    if fU > 0 and fV > 0:
        xis.append((xv, sp.N(fU/fV, 25)))
dip = [xis[i][0] for i in range(len(xis)-1) if xis[i][1] > xis[i+1][1]]
rep("Cex5.8 pdf-ratio nonmonotone", f"{len(dip)} decreasing steps; first={dip[0] if dip else None}")

# ---- Ex 5.7 (Thm 4.3): log-logistic k=0.9, c=0 -----------------------------
F, f = loglog(R('0.9'))
n, ns = (10, 8), (20, 15)
r, s_ = (R('0.02'), R('0.10')), (R('0.02'), R('0.04'))
sg, mu, lm, th, al = R(6), R(4), (4, 6), (3, 2), R('0.3')
Lams = []
for k in range(26, 400):
    xv = R(k, 4)
    hU = rh2(xv, n, r, (al, al), (sg, sg), lm, 0, F, f)
    hV = rh2(xv, ns, s_, (al, al), (mu, mu), th, 0, F, f)
    Lams.append((xv, sp.N(hU/hV, 25)))
inc = [Lams[i][0] for i in range(len(Lams)-1) if Lams[i][1] < Lams[i+1][1]]
rep("Ex5.7 Lambda decreasing x>=6", f"{len(inc)} increasing steps; first={inc[0] if inc else None}")
# hypothesis check: f'/f increasing for k=0.9?
t = sp.Symbol('t', positive=True)
Fp = lambda u: sp.nsimplify(R(9,10))*u**R('-0.1')/(1+u**R('0.9'))**2
r_ = sp.log(Fp(t)); r_ = sp.cancel(sp.diff(r_, t))
vals = [sp.N(r_.subs(t, v), 15) for v in [R(1,10), R(1,2), 1, 2, 5, 20, 100]]
rep("Ex5.7 f'/f monotone?", [str(v) for v in vals])

# ---- Cex 5.9: log-logistic k=4 ---------------------------------------------
F, f = loglog(4)
n, ns = (4, 6), (10, 25)
r, s_ = (R('0.1'), R('0.1')), (R('0.05'), R('0.02'))
sg, mu, lm, th, al = R(5), R(2), (3, 7), (2, 1), R('0.8')
Lams = []
for k in range(24, 400):
    xv = R(k, 4)
    hU = rh2(xv, n, r, (al, al), (sg, sg), lm, 0, F, f)
    hV = rh2(xv, ns, s_, (al, al), (mu, mu), th, 0, F, f)
    if hV != 0:
        Lams.append((xv, sp.N(hU/hV, 25)))
inc = [Lams[i][0] for i in range(len(Lams)-1) if Lams[i][1] < Lams[i+1][1]]
rep("Cex5.9 Lambda nonmonotone x>=5", f"{len(inc)} increasing steps; first={inc[0] if inc else None}")

# ---- Thm 4.1 (<=) D-variant scan -------------------------------------------
Fr = lambda u: 1 - 1/u; fr = lambda u: 1/u**2
rng = random.Random(2)
adm = 0; viol = 0
for _ in range(400):
    a1 = R(rng.randint(1,4)); a2 = a1 - R(rng.randint(0,2))  # D order: a1>=a2
    if a2 <= 0: continue
    s1_ = R(rng.randint(0,3)); s2_ = s1_ - R(0)  # keep s sorted D: s1>=s2>=0
    s2_ = R(rng.randint(0,3)); 
    if s1_ < s2_: s1_, s2_ = s2_, s1_
    l1 = R(rng.randint(1,4)); l2 = l1 - R(rng.randint(0,2))
    if l2 <= 0: l1, l2 = l2, l1
    n1_, n2_, m1, m2 = [rng.randint(1,6) for _ in range(4)]
    r1_ = R(1, rng.randint(1,8)); r2_ = (1-n1_*r1_)/n2_
    q1 = R(1, rng.randint(1,8)); q2 = (1-m1*q1)/m2
    if r2_ <= 0 or q2 <= 0: continue
    if not (n1_*r1_*m2*q2 <= n2_*r2_*m1*q1):  # (<=) direction
        continue
    # sigma in D: s1 >= s2, support order s2 + l2? supports must order:
    # piecewise formula in paper assumes E; for D the roles swap. We only test x > max support.
    adm += 1
    lo = max(s1_ + l1, s2_ + l2)
    for k in range(1, 30):
        xv = lo + R(k, 6)
        hU = rh2(xv, (n1_, n2_), (r1_, r2_), (a1, a2), (s1_, s2_), (l1, l2), 0, Fr, fr)
        hV = rh2(xv, (m1, m2), (q1, q2), (a1, a2), (s1_, s2_), (l1, l2), 0, Fr, fr)
        if hU is sp.nan or hV is sp.nan:
            continue
        if hU > hV:
            viol += 1; break
rep("Thm4.1(<=) D-variant", f"admissible={adm}, violations={viol}")

for k, v in out: pass
print("DONE")
