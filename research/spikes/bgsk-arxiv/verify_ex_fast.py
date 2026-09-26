"""Fast numeric/exact verification of BGSK Sec 5 examples (grid-based;
exact for rational baselines)."""
import sympy as sp
x = sp.Symbol('x')
R = sp.Rational

def pareto(k, lo):
    F = lambda u: 1 - (lo/u)**k
    f = lambda u: R(k)*lo**k/u**(k+1)
    return F, f

def expshift(rate, a):
    F = lambda u: 1 - sp.exp(sp.nsimplify(rate)*(a - u))
    f = lambda u: sp.nsimplify(rate)*sp.exp(sp.nsimplify(rate)*(a - u))
    return F, f

def cdf_at(F, c, xv, r, al, sg, lm):
    tot = 0
    for ri, ai, si, li in zip(r, al, sg, lm):
        if xv > si + c*li:
            tot += ri*F((xv-si)/li)**ai
    return tot

def pdf_at(F, f, c, xv, r, al, sg, lm):
    tot = 0
    for ri, ai, si, li in zip(r, al, sg, lm):
        if xv > si + c*li:
            u = (xv-si)/li
            tot += ri*(ai/li)*F(u)**(ai-1)*f(u)
    return tot

# --- Ex 5.1: Pareto k=5 c=1, st order (exact) ---
F, f = pareto(5, 1)
r = [R(2,5), R(11,20), R(1,20)]
bad = [p for p in [R(k,4) for k in range(13,200)]
       if cdf_at(F,1,p,r,[5,2,7],[1,2,3],[2,4,6]) < cdf_at(F,1,p,r,[9,10,8],[2,4,5],[6,7,9])]
print("Ex5.1 st grid violations:", len(bad), flush=True)

# --- Cex 5.1: Pareto k=2 lo=4 c=4, st fails (exact) ---
F, f = pareto(2, 4)
r = [R(1,10), R(3,10), R(6,10)]
cross = [p for p in [R(k,4) for k in range(60,400)]
         if cdf_at(F,4,p,r,[7,6,1],[2,6,7],[1,5,8]) < cdf_at(F,4,p,r,[6,9,9],[4,5,6],[2,3,4])]
print("Cex5.1 st-fail witness pts:", len(cross), "first:", cross[0] if cross else None, flush=True)

# --- Cex 5.2: Pareto k=6 lo=2 c=2, rh fails (CDF ratio dips) (exact) ---
F, f = pareto(6, 2)
r=[R(2,10),R(3,10),R(5,10)]
P = [R(k) for k in range(27,140)]
psi = [(p, cdf_at(F,2,p,r,[8,7,11],[6,11,16],[2,8,10])/cdf_at(F,2,p,r,[4,6,5],[3,10,14],[1,4,6])) for p in P]
dips = [(psi[i][0], psi[i][1], psi[i+1][1]) for i in range(len(psi)-1) if psi[i][1] > psi[i+1][1]]
print("Cex5.2 CDF-ratio dips:", len(dips), "first:", dips[0][0] if dips else None, flush=True)

# --- Cex 5.3: Pareto k=3 lo=5 c=5, lr fails (pdf ratio dips) (exact) ---
F, f = pareto(3, 5)
s=[R(85,100),R(5,100),R(10,100)]
P = [R(k) for k in range(33,140)]
xi = [(p, pdf_at(F,f,5,p,s,[6,7,9],[5,7,8],[2,4,6])/pdf_at(F,f,5,p,r,[2,6,5],[1,2,7],[1,2,5])) for p in P]
dips = [xi[i][0] for i in range(len(xi)-1) if xi[i][1] > xi[i+1][1]]
print("Cex5.3 pdf-ratio dips:", len(dips), "first:", dips[0] if dips else None, flush=True)

# --- Ex 5.2: trunc exp rate 1/2, c=2 (numeric) ---
F, f = expshift(R(1,2), 2)
r=[R(3,10),R(5,10),R(2,10)]; s=[R(85,100),R(5,100),R(10,100)]
alA=[R(1,10),5,R(13,10)]; alB=[R(51,10),6,R(55,10)]
sgA=[2,3,1]; sgB=[5,4,R(9,2)]; lmA=[3,5,2]; lmB=[7,5,6]
psis = []
for p in [R(k,4) for k in range(20,480)]:
    u_, v_ = cdf_at(F,2,p,r,alA,sgA,lmA), cdf_at(F,2,p,s,alB,sgB,lmB)
    if u_ > 0 and v_ > 0:
        psis.append((p, sp.N(v_/u_, 25)))
dips = [psis[i][0] for i in range(len(psis)-1) if psis[i][1] > psis[i+1][1]]
print("Ex5.2 CDF-ratio monotone x>=5:", len(dips), "dips:", dips[:5], flush=True)

# --- Cex 5.4: trunc exp rate 1/5, c=2 (numeric) ---
F, f = expshift(R(1,5), 2)
psis = []
for p in [R(k,4) for k in range(32,640)]:
    u_, v_ = cdf_at(F,2,p,r,alA,sgA,lmA), cdf_at(F,2,p,s,alB,sgB,[1,2,6])
    if u_ > 0 and v_ > 0:
        psis.append((p, sp.N(v_/u_, 25)))
dips = [psis[i][0] for i in range(len(psis)-1) if psis[i][1] > psis[i+1][1]]
print("Cex5.4 CDF-ratio dips x>=8:", len(dips), "first:", dips[0] if dips else None, flush=True)

# --- Ex 5.3: Pareto k=6 lo=4 c=4, pdf ratio increasing (exact) ---
F, f = pareto(6, 4)
alA=[6,3,5]; alB=[7,7,6]
P = [R(k,2) for k in range(28,320)]
xis = [(p, pdf_at(F,f,4,p,s,alB,[2]*3,[3]*3)/pdf_at(F,f,4,p,r,alA,[2]*3,[3]*3)) for p in P if p > 14]
dips = [xis[i][0] for i in range(len(xis)-1) if xis[i][1] > xis[i+1][1]]
print("Ex5.3 pdf-ratio dips x>14:", len(dips), "first:", dips[0] if dips else None, flush=True)

# --- Cex 5.5: Pareto k=2 lo=3 c=3 (exact) ---
F, f = pareto(2, 3)
alA=[R(1,5),9,R(1,10)]; alB=[7,R(7,10),6]
P = [R(k,2) for k in range(22,320)]
xis = [(p, pdf_at(F,f,3,p,s,alB,[2]*3,[3]*3)/pdf_at(F,f,3,p,r,alA,[2]*3,[3]*3)) for p in P if p > 11]
dips = [xis[i][0] for i in range(len(xis)-1) if xis[i][1] > xis[i+1][1]]
print("Cex5.5 pdf-ratio dips x>11:", len(dips), "first:", dips[0] if dips else None, flush=True)

# --- Ex 5.4: Benktander-II (numeric, mpf) ---
Fb = lambda u: 1 - u**(-R(1,5)) * sp.exp(R(25,4)*(1-u**R(4,5)))
r=[R(6,10),R(3,10),R(1,10)]; s=[R(4,10),R(4,10),R(2,10)]
bad = []
for p in [R(k,2) for k in range(10,400)]:
    a_ = sp.N(cdf_at(Fb,1,p,r,[5,6,14],[2]*3,[3]*3), 25)
    b_ = sp.N(cdf_at(Fb,1,p,s,[6,9,10],[4]*3,[5]*3), 25)
    if a_ < b_: bad.append(p)
print("Ex5.4 st grid violations:", len(bad), flush=True)

# --- Cex 5.6: Benktander-II variant (numeric) ---
Fc = lambda u: 1 - u**(-R(7,10)) * sp.exp(R(20,3)*(1-u**R(3,10)))
r=[R(8,10),R(1,10),R(1,10)]; s=[R(5,10),R(3,10),R(2,10)]
cross = []
for p in [R(k,2) for k in range(22,600)]:
    a_ = sp.N(cdf_at(Fc,1,p,r,[2,4,5],[3]*3,[7]*3), 25)
    b_ = sp.N(cdf_at(Fc,1,p,s,[1,R(3,2),3],[4]*3,[7]*3), 25)
    if a_ < b_: cross.append(p)
print("Cex5.6 st-fail witness pts:", len(cross), "first:", cross[0] if cross else None, flush=True)
print("DONE")
