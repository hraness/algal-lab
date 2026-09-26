"""Verify BGSK2025 (arXiv:2511.00791) Section 5 examples/counterexamples and
sample-check Sec 3 theorems. Exact rational arithmetic where the baseline is
rational (Pareto/Lomax/Burr with integer params); mpf numeric otherwise.

Mixture CDF: F_U(x) = sum_i r_i F((x-s_i)/l_i)^{a_i} on x > s_i + c l_i.
rh order check: psi(x) = F_V/F_U increasing; lr: xi(x) = f_V/f_U increasing;
st: F_U >= F_V for U <=_st V.
"""
import sympy as sp
x = sp.Symbol('x')
R = sp.Rational


def make_mixture(baseline, c):
    """Return function: F_U(x, weights, alpha, sigma, lam) exact/numeric."""
    F, f = baseline
    def cdf(xv, r, al, sg, lm):
        tot = 0
        for ri, ai, si, li in zip(r, al, sg, lm):
            if xv > si + c*li:
                tot += ri * F((xv - si)/li)**ai
        return tot
    def pdf(xv, r, al, sg, lm):
        tot = 0
        for ri, ai, si, li in zip(r, al, sg, lm):
            if xv > si + c*li:
                u = (xv - si)/li
                tot += ri * (ai/li) * F(u)**(ai-1) * f(u)
        return tot
    return cdf, pdf


def pareto(k, lo):
    """F(t)=1-(lo/t)^k, t>=lo (c=lo)."""
    F = lambda u: 1 - (lo/u)**k
    f = lambda u: sp.nsimplify(k)*lo**k/u**(k+1)
    return F, f


def lomax(k, a):
    """F(t) = 1 - ((1+t)/(1+a))^{-k}, t>=a (c=a)."""
    F = lambda u: 1 - ((1+u)/(1+a))**(-k)
    f = lambda u: k*(1+a)**k/(1+u)**(k+1)
    return F, f


def burr_trunc(p, q, a):
    """Left-truncated Burr XII: F = 1 - ((1+t^p)/(1+a^p))^{-q}, t>=a."""
    F = lambda u: 1 - ((1+u**p)/(1+a**p))**(-q)
    f = lambda u: sp.nsimplify(p*q)*(1+a**p)**q*u**(p-1)/(1+u**p)**(q+1)
    return F, f


def expshift(rate, a):
    """F(t) = 1 - exp(rate*(a-t)), t >= a (c=a): left-truncated exponential."""
    F = lambda u: 1 - sp.exp(sp.nsimplify(rate)*(a - u))
    f = lambda u: sp.nsimplify(rate)*sp.exp(sp.nsimplify(rate)*(a - u))
    return F, f


def benktander(a_, b_, lo):
    """F(t) = 1 - t^{-a} exp((lo^b/b... standard form: 1-t^{-(1-b)}e^{(a/b)(1-t^b)}"""
    F = lambda u: 1 - u**(b_-1) * sp.exp(sp.nsimplify(a_)/b_ * (1 - u**b_))
    f = None
    return F, f


out = []
def rep(name, text):
    out.append((name, text)); print(name, ":", text)


# ---------------- Example 5.1 (validates Thm 3.1): Pareto k=5, c=1 ----------
cdf, pdf = make_mixture(pareto(5, 1), 1)
r = [R(2,5), R(11,20), R(1,20)]
sgA = [1,2,3]; lmA = [2,4,6]; alA = [5,2,7]
sgB = [2,4,5]; lmB = [6,7,9]; alB = [9,10,8]
# claim U <=_st U* <=> F_U >= F_V.  grid over (1+2=3 ... 5+9*... )
pts = [R(k,2) for k in range(7, 80)]   # x from 3.5 up
bad = [p for p in pts if cdf(p,r,alA,sgA,lmA) < cdf(p,r,alB,sgB,lmB)]
rep("Ex5.1 st holds on grid", f"grid={len(pts)}, violations={len(bad)}")
# certify on tail x > mu3 + c*th3 = 14: rational difference, Sturm count
u = lambda s_,l_: (x - s_)/l_
FU = sum(ri*(1-(1/u(si,li))**5)**ai for ri,ai,si,li in zip(r,alA,sgA,lmA))
FV = sum(ri*(1-(1/u(si,li))**5)**bi for ri,bi,si,li in zip(r,alB,sgB,lmB))
d = sp.cancel(sp.together(FU - FV))
num, den = sp.fraction(d)
pn = sp.Poly(sp.expand(num), x)
roots = pn.count_roots(14, sp.oo)
rep("Ex5.1 tail certificate", f"F_U-F_V numerator roots on (14,oo): {roots}, sign at 20: {sp.sign(num.subs(x,20))}")

# ---------------- Counterexample 5.1: Pareto F=1-(4/t)^2, c=4 ----------------
cdf, pdf = make_mixture(pareto(2, 4), 4)
r = [R(1,10), R(3,10), R(6,10)]
sgA=[2,6,7]; lmA=[1,5,8]; alA=[7,6,1]
sgB=[4,5,6]; lmB=[2,3,4]; alB=[6,9,9]
pts = [R(k,4) for k in range(60, 400)]
cross = [(p, cdf(p,r,alA,sgA,lmA), cdf(p,r,alB,sgB,lmB)) for p in pts
         if cdf(p,r,alA,sgA,lmA) < cdf(p,r,alB,sgB,lmB)]
rep("Cex5.1 st-fail witness", f"{len(cross)} pts where F_U < F_V; first={cross[0][0] if cross else None}")

# ---------------- Counterexample 5.2: Pareto F=1-(2/t)^6, c=2 ---------------
cdf, pdf = make_mixture(pareto(6, 2), 2)
r = [R(2,10), R(3,10), R(5,10)]
lmA=[1,4,6]; lmB=[2,8,10]; sgA=[3,10,14]; sgB=[6,11,16]; alA=[4,6,5]; alB=[8,7,11]
pts = [R(k) for k in range(23, 120)]  # > max support start mu3+c*th3=26? sgB3+2*6? actually support B_i: mu_i+2*th_i
psi = [(p, cdf(p,r,alA,sgA,lmA), cdf(p,r,alB,sgB,lmB)) for p in pts]
psi = [(p, v/u) for p,u,v in psi if u > 0 and v > 0]
dip = [(psi[i][0], psi[i][1], psi[i+1][1]) for i in range(len(psi)-1) if psi[i][1] > psi[i+1][1]]
rep("Cex5.2 CDF-ratio nonmonotone", f"{len(dip)} decreasing steps; first at x={dip[0][0] if dip else None}")

# ---------------- Counterexample 5.3: Pareto k=3 lo=5, c=5 ------------------
cdf, pdf = make_mixture(pareto(3, 5), 5)
r=[R(3,10),R(2,10),R(5,10)]; s=[R(85,100),R(5,100),R(10,100)]
lmA=[1,2,5]; lmB=[2,4,6]; sgA=[1,2,7]; sgB=[5,7,8]; alA=[2,6,5]; alB=[6,7,9]
pts = [R(k) for k in range(33, 130)]
xi = [(p, pdf(p,r,alA,sgA,lmA), pdf(p,r,alB,sgB,lmB)) for p in pts]
xi = [(p, v/u) for p,u,v in xi if u > 0]
dip = [(xi[i][0]) for i in range(len(xi)-1) if xi[i][1] > xi[i+1][1]]
rep("Cex5.3 pdf-ratio nonmonotone", f"{len(dip)} decreasing steps; first at x={dip[0] if dip else None}")

# ---------------- Example 5.2 (validates Thm 3.2): trunc exp, c=2 -----------
# F(t) = (e^{-1}-e^{-t/2})/e^{-1} = 1 - e^{1-t/2}, t>=2
cdf, pdf = make_mixture(expshift(R(1,2), 2), 2)
r=[R(3,10),R(5,10),R(2,10)]; s=[R(85,100),R(5,100),R(10,100)]
sgA=[2,3,1]; sgB=[5,4,R(9,2)]; lmA=[3,5,2]; lmB=[7,5,6]
alA=[R(1,10),5,R(13,10)]; alB=[R(51,10),6,R(55,10)]
# hypothesis check: max sg<=min sgB etc
rep("Ex5.2 hyp", f"maxA_sig={max(sgA)}<=minB={min(sgB)}, maxA_lam={max(lmA)}<=minB={min(lmB)}, maxA_al={max(alA)}<=minB={min(alB)}")
pts = [R(k,2) for k in range(10, 120)]
psis = []
for p in pts:
    u_, v_ = cdf(p,r,alA,sgA,lmA), cdf(p,s,alB,sgB,lmB)
    if u_ > 0 and v_ > 0:
        psis.append((p, sp.N(v_/u_, 30)))
dip = [psis[i][0] for i in range(len(psis)-1) if psis[i][1] > psis[i+1][1]]
rep("Ex5.2 CDF-ratio monotone (x>=5)", f"{len(dip)} decreasing steps in x>=5 grid {len(psis)} pts; dips={dip[:5]}")

# ---------------- Counterexample 5.4: trunc exp rate 1/5, c=2 ---------------
cdf, pdf = make_mixture(expshift(R(1,5), 2), 2)
sgA=[2,3,4]; sgB=[6,4,R(9,2)]; lmA=[3,5,2]; lmB=[1,2,6]
pts = [R(k,2) for k in range(16, 200)]
psis = []
for p in pts:
    u_, v_ = cdf(p,r,alA,sgA,lmA), cdf(p,s,alB,sgB,lmB)
    if u_ > 0 and v_ > 0:
        psis.append((p, sp.N(v_/u_, 30)))
dip = [psis[i][0] for i in range(len(psis)-1) if psis[i][1] > psis[i+1][1]]
rep("Cex5.4 CDF-ratio nonmonotone (x>=8)", f"{len(dip)} decreasing steps; dips={dip[:8]}")

# ---------------- Example 5.3 (validates Thm 3.3): Pareto k=6 lo=4 ----------
cdf, pdf = make_mixture(pareto(6, 4), 4)
r=[R(3,10),R(2,10),R(5,10)]; s=[R(85,100),R(5,100),R(10,100)]
alA=[6,3,5]; alB=[7,7,6]; sg=2; lm=3
pts = [R(k,2) for k in range(28, 160)]
xis = [(p, pdf(p,s,alB,[sg]*3,[lm]*3)/pdf(p,r,alA,[sg]*3,[lm]*3)) for p in pts if p > sg+4*lm]
dip = [xis[i][0] for i in range(len(xis)-1) if xis[i][1] > xis[i+1][1]]
rep("Ex5.3 pdf-ratio increasing x>=14", f"{len(dip)} decreasing steps")
# exact: xi' numerator positivity on (14,oo)? build symbolic
u_ = (x - 2)/3
Fu = 1 - (4/u_)**6; fu = sp.diff(Fu, x)
fA = sum(ri*(ai/3)*Fu**(ai-1)*fu for ri,ai in zip(r,alA))
fB = sum(si_*(bi/3)*Fu**(bi-1)*fu for si_,bi in zip(s,alB))
xi = sp.cancel(sp.together(fB/fA))
xip = sp.cancel(sp.together(sp.diff(xi, x)))
num, den = sp.fraction(xip); num = sp.expand(num); den = sp.expand(den)
pn, pd = sp.Poly(num, x), sp.Poly(den, x)
rep("Ex5.3 certificate", f"xi' num deg {pn.degree()}, roots(14,oo)={pn.count_roots(14, sp.oo)}, den roots={pd.count_roots(14, sp.oo)}, sign(20)={sp.sign(num.subs(x,20))}")

# ---------------- Counterexample 5.5: Pareto k=2 lo=3 -----------------------
cdf, pdf = make_mixture(pareto(2, 3), 3)
alA=[R(1,5),9,R(1,10)]; alB=[7,R(7,10),6]
pts = [R(k,2) for k in range(22, 160)]
xis = [(p, pdf(p,s,alB,[2]*3,[3]*3)/pdf(p,r,alA,[2]*3,[3]*3)) for p in pts if p > 2+3*3]
dip = [xis[i][0] for i in range(len(xis)-1) if xis[i][1] > xis[i+1][1]]
rep("Cex5.5 pdf-ratio nonmonotone x>=11", f"{len(dip)} decreasing steps; first={dip[0] if dip else None}")

# ---------------- Example 5.4 (Thm 3.4): Benktander-II ----------------------
# F(x) = 1 - x^{-0.2} e^{(5/0.8)(1-x^{0.8})}, x>=1
F = lambda u: 1 - u**(-R(1,5)) * sp.exp(R(25,4)*(1-u**R(4,5)))
cdf2 = lambda xv, r_, a_, s_, l_: sum(ri*F((xv-si)/li)**ai for ri,ai,si,li in zip(r_,a_,s_,l_) if xv > si + li)
r=[R(6,10),R(3,10),R(1,10)]; s=[R(4,10),R(4,10),R(2,10)]
alA=[5,6,14]; alB=[6,9,10]
pts = [R(k,2) for k in range(10, 200)]
bad = [(p, sp.N(cdf2(p,r,alA,[2]*3,[3]*3),20), sp.N(cdf2(p,s,alB,[4]*3,[5]*3),20))
       for p in pts if sp.N(cdf2(p,r,alA,[2]*3,[3]*3),20) < sp.N(cdf2(p,s,alB,[4]*3,[5]*3),20)]
rep("Ex5.4 st holds on grid (x>=5)", f"violations={len(bad)} of {len(pts)}")

# ---------------- Counterexample 5.6: Benktander-II variant -----------------
F2 = lambda u: 1 - u**(-R(7,10)) * sp.exp(R(20,3)*(1-u**R(3,10)))
cdf3 = lambda xv, r_, a_, s_, l_: sum(ri*F2((xv-si)/li)**ai for ri,ai,si,li in zip(r_,a_,s_,l_) if xv > si + li)
r=[R(8,10),R(1,10),R(1,10)]; s=[R(5,10),R(3,10),R(2,10)]
alA=[2,4,5]; alB=[1,R(3,2),3]
pts = [R(k,2) for k in range(22, 300)]
cross = [(p, sp.N(cdf3(p,r,alA,[3]*3,[7]*3),20), sp.N(cdf3(p,s,alB,[4]*3,[7]*3),20))
         for p in pts if sp.N(cdf3(p,r,alA,[3]*3,[7]*3),20) < sp.N(cdf3(p,s,alB,[4]*3,[7]*3),20)]
rep("Cex5.6 st-fail witness", f"{len(cross)} pts F_U<F_V; first={cross[0][0] if cross else None}")

print("\nDONE sec3/5")
for k,v in out: print(k, "->", v)
