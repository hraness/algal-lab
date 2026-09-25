"""Independent re-verification of the derivative identities and algebraic
identities used in the manuscript.  Symbolic checks use sympy; numerical
checks use mpmath at 50 digits.  No repository code is imported.

Run:  python identities.py
"""
import random
import sympy as sp
import mpmath as mp

mp.mp.dps = 50
random.seed(20260925)
FAIL = []


def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        FAIL.append(name)


# ---------------------------------------------------------------------------
# 1. One Boltzmann mean: first and second derivatives (Lemma: identities)
# ---------------------------------------------------------------------------
n = 3
c = sp.symbols("c", real=True)
x = sp.symbols("x1:%d" % (n + 1), real=True)
u = sp.symbols("u1:%d" % (n + 1), real=True)
w = [sp.exp(c * xi) for xi in x]
Z = sum(w)
B = sum(xi * wi for xi, wi in zip(x, w)) / Z
p = [wi / Z for wi in w]
h = [1 + c * (xi - B) for xi in x]

# first derivative
ok = all(sp.simplify(sp.diff(B, x[k]) - p[k] * h[k]) == 0 for k in range(n))
check("dB/dx_k = p_k h_k", ok)
# gradient components sum to one
check("sum_k dB/dx_k = 1", sp.simplify(sum(sp.diff(B, x[k]) for k in range(n)) - 1) == 0)
# sum p_i(1+h_i) = 2
check("sum_i p_i (1+h_i) = 2", sp.simplify(sum(p[i] * (1 + h[i]) for i in range(n)) - 2) == 0)
# second derivatives
ok = True
for k in range(n):
    for l in range(n):
        d = sp.diff(B, x[k], x[l])
        delta = 1 if k == l else 0
        rhs = c * p[k] * (delta * h[k] - p[l] * h[k] + delta - p[l] * h[l])
        ok = ok and sp.simplify(d - rhs) == 0
check("d2B/dx_k dx_l = c p_k[delta h_k - p_l h_k + delta - p_l h_l]", ok)
ok = all(sp.simplify(sp.diff(B, x[k], 2) - c * p[k] * (1 + h[k] - 2 * p[k] * h[k])) == 0 for k in range(n))
check("d2B/dx_k^2 = c p_k (1 + h_k - 2 p_k h_k)", ok)
# quadratic form identities (5) and centered form
quad = sum(sp.diff(B, x[k], x[l]) * u[k] * u[l] for k in range(n) for l in range(n))
ubar = sum(p[i] * u[i] for i in range(n))
DB = sum(p[i] * h[i] * u[i] for i in range(n))
form1 = c * sum(p[i] * (1 + h[i]) * u[i] ** 2 for i in range(n)) - 2 * c * ubar * DB
form2 = c * sum(p[i] * (2 + c * (x[i] - B)) * (u[i] - ubar) ** 2 for i in range(n))
check("D2B[u,u] = c sum p_i(1+h_i)u_i^2 - 2c ubar DB[u]", sp.simplify(quad - form1) == 0)
check("D2B[u,u] = c sum p_i[2+c(x_i-b)](u_i-ubar)^2", sp.simplify(quad - form2) == 0)
# temperature derivative equals variance; scaling derivative
Var = sum(p[i] * x[i] ** 2 for i in range(n)) - B ** 2
check("dB_c/dc = Var_c(x)", sp.simplify(sp.diff(B, c) - Var) == 0)
s, t = sp.symbols("s t", positive=True)
Bs = B.subs(c, s * t)
scaled = s * Bs  # score of the column s*x equals s*B_{st}(x)
Bst_direct = sum(s * xi * sp.exp(t * s * xi) for xi in x) / sum(sp.exp(t * s * xi) for xi in x)
check("B_t(s x) = s B_{st}(x)", sp.simplify(scaled - Bst_direct) == 0)
Var_st = Var.subs(c, s * t)
check("d/ds[s B_{st}(x)] = B_{st}(x) + s t Var_{st}(x)", sp.simplify(sp.diff(scaled, s) - (Bs + s * t * Var_st)) == 0)

# own-weight curvature formula: with h = 1 + (1-p) d,  1 + h - 2ph = (1-p)[2 - (2p-1) d]
pp, dd = sp.symbols("p d", real=True)
hh = 1 + (1 - pp) * dd
check("1+h-2ph = (1-p)[2-(2p-1)d] when h = 1+(1-p)d", sp.simplify((1 + hh - 2 * pp * hh) - (1 - pp) * (2 - (2 * pp - 1) * dd)) == 0)

# ---------------------------------------------------------------------------
# 2. Nested chain rule, second directional derivative (numerical, 50 digits)
# ---------------------------------------------------------------------------
def boltz(vec, cc):
    ws = [mp.e ** (cc * v) for v in vec]
    return sum(v * wi for v, wi in zip(vec, ws)) / sum(ws)


def reward(A, tt, tau):
    N, M = len(A), len(A[0])
    S = [boltz([A[i][j] for i in range(N)], tt) for j in range(M)]
    return boltz(S, tau)


def second_dir_pieces(A, U, tt, tau):
    N, M = len(A), len(A[0])
    S = [boltz([A[i][j] for i in range(N)], tt) for j in range(M)]
    R = boltz(S, tau)
    ZS = sum(mp.e ** (tau * Sj) for Sj in S)
    P = [mp.e ** (tau * Sj) / ZS for Sj in S]
    g = [1 + tau * (Sj - R) for Sj in S]
    W = [P[j] * g[j] for j in range(M)]
    total = mp.mpf(0)
    v = []
    for j in range(M):
        col = [A[i][j] for i in range(N)]
        Zc = sum(mp.e ** (tt * a) for a in col)
        pj = [mp.e ** (tt * a) / Zc for a in col]
        hj = [1 + tt * (a - S[j]) for a in col]
        Uj = [U[i][j] for i in range(N)]
        vj = sum(pj[i] * hj[i] * Uj[i] for i in range(N))
        ubar = sum(pj[i] * Uj[i] for i in range(N))
        D2S = tt * sum(pj[i] * (1 + hj[i]) * Uj[i] ** 2 for i in range(N)) - 2 * tt * ubar * vj
        total += W[j] * D2S
        v.append(vj)
    vbar = sum(P[j] * v[j] for j in range(M))
    DBv = sum(W[j] * v[j] for j in range(M))
    D2outer = tau * sum(P[j] * (1 + g[j]) * v[j] ** 2 for j in range(M)) - 2 * tau * vbar * DBv
    return total + D2outer, DBv


ok = True
for trial in range(12):
    N, M = random.choice([(2, 2), (3, 3), (4, 3), (3, 5)])
    tt, tau = mp.mpf(random.uniform(0.2, 6)), mp.mpf(random.uniform(0.2, 6))
    A = [[mp.mpf(random.uniform(0.05, 0.3)) for _ in range(M)] for _ in range(N)]
    U = [[mp.mpf(random.uniform(-1, 1)) for _ in range(M)] for _ in range(N)]
    f = lambda z: reward([[A[i][j] + z * U[i][j] for j in range(M)] for i in range(N)], tt, tau)
    eps = mp.mpf("1e-10")
    fd2 = (-f(2 * eps) + 16 * f(eps) - 30 * f(0) + 16 * f(-eps) - f(-2 * eps)) / (12 * eps ** 2)
    fd1 = (f(eps) - f(-eps)) / (2 * eps)
    pred2, pred1 = second_dir_pieces(A, U, tt, tau)
    ok = ok and abs(fd2 - pred2) < mp.mpf("1e-15") and abs(fd1 - pred1) < mp.mpf("1e-18")
check("nested chain rule: D2R[U,U] = sum_j W_j D2S_j + D2B_tau[v,v] (12 random cases)", ok)

# ---------------------------------------------------------------------------
# 3. Path-direction algebra (universal purity): (13), (14), (15)
# ---------------------------------------------------------------------------
W, pv, hv, lam, tt_ = sp.symbols("W p h lambda t", positive=True)
Usq = (1 / lam) ** 2
lhs13 = tt_ * W * pv * (1 + hv) * Usq
rhs13 = tt_ * lam * (1 + 1 / hv) * Usq
check("(13): t W p (1+h) U^2 = t lambda (1+1/h) U^2 when lambda = W p h", sp.simplify((lhs13 - rhs13).subs(lam, W * pv * hv)) == 0)
lhs14 = tt_ * W * pv * (1 + hv - 2 * pv * hv) * Usq
rhs14 = tt_ * lam * (1 + 1 / hv - 2 * pv) * Usq
check("(14): t W p (1+h-2ph) U^2 = t lambda (1+1/h-2p) U^2 when lambda = W p h", sp.simplify((lhs14 - rhs14).subs(lam, W * pv * hv)) == 0)
# (15): 2 + 1/h_priv + 1/h_int - 2 p_priv > 0 for p_priv < 1, h > 0
hp, hi, ppr = sp.symbols("h_p h_i p_p", positive=True)
expr15 = 2 + 1 / hp + 1 / hi - 2 * ppr
ok = all(expr15.subs({hp: random.uniform(0.01, 5), hi: random.uniform(0.01, 5), ppr: random.uniform(0, 0.999)}) > 0 for _ in range(2000))
check("(15): 2 + 1/h_priv + 1/h_int - 2 p_priv > 0 sampled (p<1)", ok)

# ---------------------------------------------------------------------------
# 4. Two agents, two tasks: R = 1/2 + g_t(d) + g_tau(u)
# ---------------------------------------------------------------------------
def gfun(z, cc):
    return z * mp.tanh(cc * z)


ok = True
for trial in range(300):
    a, b = mp.mpf(random.random()), mp.mpf(random.random())
    tt, tau = mp.mpf(random.uniform(-5, 5)), mp.mpf(random.uniform(-5, 5))
    A = [[a, 1 - a], [b, 1 - b]]
    R = reward(A, tt, tau)
    uu, dd_ = (a + b - 1) / 2, (a - b) / 2
    ok = ok and abs(R - (mp.mpf(1) / 2 + gfun(dd_, tt) + gfun(uu, tau))) < mp.mpf("1e-40")
check("two agents two tasks: R = 1/2 + g_t(d) + g_tau(u) (300 random, any signs)", ok)
# slice derivative f'(a) = e^v (1+e^v+v)/(1+e^v)^2, v = t(a-c)
a_, c_ = sp.symbols("a c", real=True)
fslice = (a_ * sp.exp(t * a_) + c_ * sp.exp(t * c_)) / (sp.exp(t * a_) + sp.exp(t * c_))
v_ = t * (a_ - c_)
fprime = sp.exp(v_) * (1 + sp.exp(v_) + v_) / (1 + sp.exp(v_)) ** 2
check("slice derivative d/da B_t(a,c) = e^v(1+e^v+v)/(1+e^v)^2", sp.simplify(sp.diff(fslice, a_) - fprime) == 0)
# sigma(alpha,2) = 1/2 + g_alpha(1/2)
al = sp.symbols("alpha", positive=True)
check("1/2 + (1/2)tanh(alpha/2) = e^alpha/(e^alpha+1)", sp.simplify((sp.Rational(1, 2) + sp.Rational(1, 2) * sp.tanh(al / 2) - sp.exp(al) / (sp.exp(al) + 1)).rewrite(sp.exp)) == 0)

# ---------------------------------------------------------------------------
# 5. Consolidation lemma algebra
# ---------------------------------------------------------------------------
xx, yy, tau_ = sp.symbols("x y tau", positive=True)
X, Y = sp.exp(tau_ * xx), sp.exp(tau_ * yy)
DN = xx * X * (Y - 1) + yy * Y * (X - 1)
DD = (X - 1) * (Y - 1)
check("consolidation: DN/DD = x/(1-e^{-tau x}) + y/(1-e^{-tau y})", sp.simplify(DN / DD - (xx / (1 - sp.exp(-tau_ * xx)) + yy / (1 - sp.exp(-tau_ * yy)))) == 0)
# numerator/denominator change of replacing scores (x,y) by (x+y,0)
Num0, Den0 = sp.symbols("Num0 Den0", positive=True)
newN = Num0 - xx * X - yy * Y + (xx + yy) * X * Y + 0
newD = Den0 - X - Y + X * Y + 1
check("consolidation: Delta N and Delta D formulas", sp.simplify((newN - Num0) - DN) == 0 and sp.simplify((newD - Den0) - DD) == 0)
# q_N(u)/u strictly increasing for N>=2 : derivative of e^{tu}/(e^{tu}+N-1)
uu_, NN = sp.symbols("u N", positive=True)
rho = sp.exp(t * uu_) / (sp.exp(t * uu_) + NN - 1)
check("d/du [q_N(u)/u] = t (N-1) e^{tu}/(e^{tu}+N-1)^2", sp.simplify(sp.diff(rho, uu_) - t * (NN - 1) * sp.exp(t * uu_) / (sp.exp(t * uu_) + NN - 1) ** 2) == 0)
# 1 - e^{-z} < z for z > 0 (sampled) and (v-R)e^{tau v} derivative
zz = sp.symbols("z", positive=True)
ok = all((1 - mp.e ** (-z)) < z for z in [mp.mpf(random.uniform(1e-6, 20)) for _ in range(1000)])
check("1 - e^{-z} < z sampled", ok)
vv, RR = sp.symbols("v R", real=True)
check("d/dv[(v-R)e^{tau v}] = e^{tau v}[1+tau(v-R)]", sp.simplify(sp.diff((vv - RR) * sp.exp(tau_ * vv), vv) - sp.exp(tau_ * vv) * (1 + tau_ * (vv - RR))) == 0)

# ---------------------------------------------------------------------------
# 6. Dominance lemma: tangent inequality and Z h_a identity
# ---------------------------------------------------------------------------
ok = all((1 + uval) <= mp.e ** uval for uval in [mp.mpf(random.uniform(-10, 10)) for _ in range(1000)])
check("tangent inequality 1+u <= e^u sampled", ok)
xs = sp.symbols("y1:5", real=True)
aa = sp.symbols("a", real=True)
Zc = sum(sp.exp(t * yi) for yi in xs)
Sc = sum(yi * sp.exp(t * yi) for yi in xs) / Zc
ha = 1 + t * (aa - Sc)
check("Z h_a = sum_l e^{t x_l}[1 + t(a - x_l)]", sp.simplify(Zc * ha - sum(sp.exp(t * yi) * (1 + t * (aa - yi)) for yi in xs)) == 0)

# ---------------------------------------------------------------------------
# 7. Zero-row endpoint comparison, outer second derivative at W_j = 0
# ---------------------------------------------------------------------------
E_, T_, C_ = sp.symbols("E T C", positive=True)
check("(E+T)/(E+C) - T/(1+C) = [E(1+C-T)+T]/[(E+C)(1+C)]", sp.simplify((E_ + T_) / (E_ + C_) - T_ / (1 + C_) - (E_ * (1 + C_ - T_) + T_) / ((E_ + C_) * (1 + C_))) == 0)

# ---------------------------------------------------------------------------
# 8. Matched-temperature gap identity and its ingredients
# ---------------------------------------------------------------------------
m_, n_ = sp.symbols("m n", positive=True)
E = sp.symbols("E", positive=True)
s_m = m_ * E / (m_ * E + n_ - m_)
hval = E / (E + n_ - 1)
D_m = (m_ * E + n_ - m_) / n_
check("s_m - h = h (m-1)/D_m", sp.simplify(s_m - hval - hval * (m_ - 1) / D_m) == 0)
# full identity (3) for k = 3 parts m1,m2,m3 with m1+m2+m3 = n
m1, m2, m3 = sp.symbols("m1 m2 m3", positive=True)
nsum = m1 + m2 + m3
k = 3
def s_of(m):
    return m * E / (m * E + nsum - m)
def D_of(m):
    return (m * E + nsum - m) / nsum
hv_ = E / (E + nsum - 1)
Zv = sum(E ** s_of(m) for m in (m1, m2, m3)) + nsum - k
Rv = sum(s_of(m) * E ** s_of(m) for m in (m1, m2, m3)) / Zv
rhs = (hv_ / Zv) * sum((m - 1) * (E ** s_of(m) / D_of(m) - 1) for m in (m1, m2, m3))
diffexpr = sp.simplify(sp.together(Rv - hv_ - rhs))
ok = diffexpr == 0
if not ok:  # fall back to numeric spot checks
    ok = all(abs(sp.N((Rv - hv_ - rhs).subs({m1: v1, m2: v2, m3: v3, E: ev}), 40)) < 1e-30
             for (v1, v2, v3, ev) in [(2, 3, 4, 3), (1, 1, 5, 2), (3, 3, 3, sp.Rational(7, 2)), (2, 2, 1, 5)])
check("gap identity (3): R - h = (h/Z) sum (m_j-1)(E^{s}/D - 1)", ok)
# f(E) = pE log E - D log D, f' = p log(E/D)
p_ = sp.symbols("p", positive=True)
Dp = 1 - p_ + p_ * E
fE = p_ * E * sp.log(E) - Dp * sp.log(Dp)
check("f'(E) = p log(E/D)", sp.simplify(sp.expand_log(sp.diff(fE, E) - p_ * sp.log(E / Dp), force=True)) == 0)
check("f(1) = 0", sp.simplify(fE.subs(E, 1)) == 0)
# E^{s} > D certificate as integer comparison n^P E^{mE} > P^P with P = mE + n - m
ok = True
for nn in range(3, 13):
    for mm in range(1, nn + 1):
        for EE in range(2, 9):
            P = mm * EE + nn - mm
            lhs_ = nn ** P * EE ** (mm * EE)
            rhs_ = P ** P
            if 1 < mm < nn:
                ok = ok and lhs_ > rhs_
            elif mm == nn:
                ok = ok and lhs_ == rhs_
check("integer certificate n^P E^{mE} > P^P for 1<m<n (n<=12, E<=8), equality at m=n", ok)

# ---------------------------------------------------------------------------
# 9. Small and large temperature expansions
# ---------------------------------------------------------------------------
tt2 = sp.symbols("t", positive=True)
Et = sp.exp(tt2)
Dpt = 1 - p_ + p_ * Et
spt = p_ * Et / Dpt
ser = sp.series(spt * tt2 - sp.log(Dpt), tt2, 0, 3).removeO()
check("s log E - log D = p(1-p) t^2/2 + O(t^3)", sp.simplify(ser - p_ * (1 - p_) * tt2 ** 2 / 2) == 0)


def R_partition(parts, nn, tt2v):
    Ev = sp.exp(tt2v)
    kk = len(parts)
    Zp = sum(Ev ** (mm * Ev / (mm * Ev + nn - mm)) for mm in parts) + nn - kk
    return sum((mm * Ev / (mm * Ev + nn - mm)) * Ev ** (mm * Ev / (mm * Ev + nn - mm)) for mm in parts) / Zp


for parts, coef in [((5, 4), sp.Rational(70, 6561)), ((3, 3, 3), sp.Rational(54, 6561))]:
    expr = R_partition(parts, 9, tt2) - sp.exp(tt2) / (sp.exp(tt2) + 8)
    ser2 = sp.series(expr, tt2, 0, 3).removeO()
    check("small-t coefficient for n=9 %s equals %s" % (parts, coef), sp.simplify(ser2 - coef * tt2 ** 2) == 0)
    # generic formula t^2/(2 n^4) sum m(m-1)(n-m)
    formula = sp.Rational(1, 2 * 9 ** 4) * sum(mm * (mm - 1) * (9 - mm) for mm in parts)
    check("  matches t^2/(2n^4) sum m(m-1)(n-m) for %s" % (parts,), sp.simplify(formula - coef) == 0)

# large temperature: (1 - R) e^t -> A(m) numerically at t = 60 (error O(t e^{-t}))
for parts, Acoef in [((5, 4), mp.mpf(181) / 40), ((3, 3, 3), mp.mpf(4))]:
    tv = mp.mpf(60)
    Ev = mp.e ** tv
    nn = 9
    kk = len(parts)
    svals = [mm * Ev / (mm * Ev + nn - mm) for mm in parts]
    Zp = sum(Ev ** sv for sv in svals) + nn - kk
    Rv_ = sum(sv * Ev ** sv for sv in svals) / Zp
    approx = (1 - Rv_) * Ev
    Aform = (mp.mpf(nn) / kk) * (1 + sum(mp.mpf(1) / mm for mm in parts)) - 2
    check("large-t: (1-R)e^t at t=60 for n=9 %s within 1e-20 of A(m)=%s" % (parts, Acoef), abs(approx - Acoef) < mp.mpf("1e-20") and abs(Aform - Acoef) < mp.mpf("1e-45"))

# merge identity for the small-t coefficient
a_s, b_s, n_s = sp.symbols("a b n", positive=True)
fm = lambda m: m * (m - 1) * (n_s - m)
check("merge identity f(a+b)-f(a)-f(b) = ab[2(n+1)-3(a+b)]", sp.simplify(fm(a_s + b_s) - fm(a_s) - fm(b_s) - a_s * b_s * (2 * (n_s + 1) - 3 * (a_s + b_s))) == 0)
# A(m) lower bound: sum 1/m_j >= k^2/n and A >= k + n/k - 2, checked on all partitions of n<=20
def partitions(nn, maxpart=None):
    if maxpart is None:
        maxpart = nn
    if nn == 0:
        yield ()
        return
    for first in range(min(nn, maxpart), 0, -1):
        for rest in partitions(nn - first, first):
            yield (first,) + rest
ok = True
for nn in range(2, 21):
    for parts in partitions(nn):
        kk = len(parts)
        Am = sp.Rational(nn, kk) * (1 + sum(sp.Rational(1, mm) for mm in parts)) - 2
        ok = ok and Am >= sp.Rational(kk, 1) + sp.Rational(nn, kk) - 2
        if nn in (4, 9, 16):
            r = int(round(nn ** 0.5))
            if parts != tuple([r] * r):
                ok = ok and Am > 2 * r - 2
            else:
                ok = ok and Am == 2 * r - 2
check("A(m) >= k + n/k - 2, strict unless square-root groups (n<=20)", ok)

# ---------------------------------------------------------------------------
# 10. Two agents, M tasks: crossover algebra
# ---------------------------------------------------------------------------
F, bb, MM = sp.symbols("F b M", positive=True)
fF = 2 * F ** bb + MM - 2
Dv = 2 * bb * F ** bb / fF
Hv = F / (F + MM - 1)
GF = (F + MM - 1) * sp.diff(fF, F) - fF
check("D - H = F G(F)/(f(F)(F+M-1))", sp.simplify(Dv - Hv - F * GF / (fF * (F + MM - 1))) == 0)
check("G'(F) = 2b(b-1)(F+M-1)F^{b-2}", sp.simplify(sp.diff(GF, F) - 2 * bb * (bb - 1) * (F + MM - 1) * F ** (bb - 2)) == 0)
check("G(1) = M(2b-1)", sp.simplify(GF.subs(F, 1) - MM * (2 * bb - 1)) == 0)
check("G(F) = 2F^{b-1}[b(M-1)-(1-b)F]-(M-2)", sp.simplify(GF - (2 * F ** (bb - 1) * (bb * (MM - 1) - (1 - bb) * F) - (MM - 2))) == 0)
bE = E / (E + 1)
GE = GF.subs({bb: bE, F: E})
check("G(E) = (M-2)[2E^b/(E+1) - 1] with b = E/(E+1)", sp.simplify(GE - (MM - 2) * (2 * E ** bE / (E + 1) - 1)) == 0)
check("G(E(M-1)) = -(M-2)", sp.simplify(GF.subs({bb: bE, F: E * (MM - 1)}) + (MM - 2)) == 0)
JE = E * sp.log(E) / (E + 1) - sp.log((E + 1) / 2)
check("J'(E) = log E/(E+1)^2", sp.simplify(sp.diff(JE, E) - sp.log(E) / (E + 1) ** 2) == 0)
check("J(1) = 0", sp.simplify(JE.subs(E, 1)) == 0)
# 1/150 certificate
r = sp.symbols("r", positive=True)
Dlog2 = 4 * r / (3 * (2 * r + 1))
check("M=3, t=tau=log 2: D - 1/2 = (2r-3)/(6(2r+1)) with r = 2^{2/3}", sp.simplify(Dlog2 - sp.Rational(1, 2) - (2 * r - 3) / (6 * (2 * r + 1))) == 0)
check("19^3 = 6859 < 6912 = 4 * 12^3", 19 ** 3 == 6859 and 4 * 12 ** 3 == 6912 and 6859 < 6912)
check("gain at r = 19/12 equals 1/150", sp.Rational(2 * 19, 12) - 3 == sp.Rational(19, 6) - 3 and sp.simplify(((2 * sp.Rational(19, 12) - 3) / (6 * (2 * sp.Rational(19, 12) + 1))) - sp.Rational(1, 150)) == 0)
check("d/dr (2r-3)/(6(2r+1)) = 4/(3(2r+1)^2) > 0", sp.simplify(sp.diff((2 * r - 3) / (6 * (2 * r + 1)), r) - 4 / (3 * (2 * r + 1) ** 2)) == 0)

# ---------------------------------------------------------------------------
# 11. Three agents, three tasks: thresholds algebra
# ---------------------------------------------------------------------------
tau3 = sp.symbols("tau", positive=True)
a3 = 2 * E / (2 * E + 1)
b3 = E / (E + 2)
Q = (a3 * sp.exp(tau3 * a3) + b3 * sp.exp(tau3 * b3)) / (sp.exp(tau3 * a3) + sp.exp(tau3 * b3) + 1)
check("Q - b = [(a-b)e^{tau a} - b]/(e^{tau a}+e^{tau b}+1)", sp.simplify(Q - b3 - ((a3 - b3) * sp.exp(tau3 * a3) - b3) / (sp.exp(tau3 * a3) + sp.exp(tau3 * b3) + 1)) == 0)
check("b/(a-b) = (2E+1)/3", sp.simplify(b3 / (a3 - b3) - (2 * E + 1) / 3) == 0)
f3 = F ** a3 + F ** b3 + 1
G3 = (F + 2) * sp.diff(f3, F) - f3
Q_F = F * sp.diff(f3, F) / f3
H3 = F / (F + 2)
check("Q - H = F G(F)/(f(F)(F+2))", sp.simplify(Q_F - H3 - F * G3 / (f3 * (F + 2))) == 0)
check("G'(F) = (F+2) f''(F)", sp.simplify(sp.diff(G3, F) - (F + 2) * sp.diff(f3, F, 2)) == 0)
check("G(1) = 3(a+b-1)", sp.simplify(G3.subs(F, 1) - 3 * (a3 + b3 - 1)) == 0)
check("a + b - 1 = 2(E-1)(E+1)/((2E+1)(E+2)) > 0 for E>1", sp.simplify(a3 + b3 - 1 - 2 * (E - 1) * (E + 1) / ((2 * E + 1) * (E + 2))) == 0)
check("2a/(1-a) = 4E", sp.simplify(2 * a3 / (1 - a3) - 4 * E) == 0)
G4E = sp.simplify(G3.subs(F, 4 * E))
check("G(4E) = (4E)^{b-1}[2b - 4E(1-b)] - 1 with 2b-4E(1-b) = -6E/(E+2)", sp.simplify(G4E - ((4 * E) ** (b3 - 1) * (2 * b3 - 4 * E * (1 - b3)) - 1)) == 0 and sp.simplify(2 * b3 - 4 * E * (1 - b3) + 6 * E / (E + 2)) == 0)
# 1/295 certificate
rr, qq = sp.symbols("r q", positive=True)
Qlog2 = (sp.Rational(4, 5) * rr + sp.Rational(1, 2) * qq) / (rr + qq + 1)
check("t=tau=log 2: Q - 1/2 = (3r-5)/(10(r+q+1)), r=2^{4/5}, q=sqrt2", sp.simplify(Qlog2 - sp.Rational(1, 2) - (3 * rr - 5) / (10 * (rr + qq + 1))) == 0)
check("12^5 < 16 * 7^5", 12 ** 5 < 16 * 7 ** 5)
check("value at r=12/7, q=3/2 is 1/295", sp.simplify((3 * sp.Rational(12, 7) - 5) / (10 * (sp.Rational(12, 7) + sp.Rational(3, 2) + 1)) - sp.Rational(1, 295)) == 0)
# four-agent certificates
check("(19/12)^3 < 4 and 2(19/12)/(3(19/12+1)) = 38/93", sp.Rational(19, 12) ** 3 < 4 and sp.simplify(2 * sp.Rational(19, 12) / (3 * (sp.Rational(19, 12) + 1)) - sp.Rational(38, 93)) == 0)
check("38/93 - 2/5 = 4/465", sp.Rational(38, 93) - sp.Rational(2, 5) == sp.Rational(4, 465))
check("3^5 = 243 < 256 = 4^4 and 3/5 - 4/7 = 1/35", 3 ** 5 < 4 ** 4 and sp.Rational(3, 5) - sp.Rational(4, 7) == sp.Rational(1, 35))

# ---------------------------------------------------------------------------
# 12. Envelope slopes, crumb function, Lemma 1 constant
# ---------------------------------------------------------------------------
kk_, NN_ = sp.symbols("k N", positive=True)
s_k = kk_ * E / (NN_ + kk_ * (E - 1))
d_k = s_k.subs(kk_, kk_ + 1) - s_k
check("d_k = E N /((N+k(E-1))(N+(k+1)(E-1)))", sp.simplify(d_k - E * NN_ / ((NN_ + kk_ * (E - 1)) * (NN_ + (kk_ + 1) * (E - 1)))) == 0)
check("s_N = 1", sp.simplify(s_k.subs(kk_, NN_) - 1) == 0)
y_, q_ = sp.symbols("y q", positive=True)
col_score = (q_ * E + y_ * sp.exp(t * y_)) / (q_ * E + sp.exp(t * y_) + NN_ - q_ - 1)
s_q = q_ * E / (q_ * E + NN_ - q_)
hcrumb = y_ * (q_ * E + NN_ - q_) - q_ * E * (1 - sp.exp(-t * y_))
# (score - s_q) has the sign of h(y): compare cross-multiplied difference
crossdiff = sp.simplify((q_ * E + y_ * sp.exp(t * y_)) * (q_ * E + NN_ - q_) - q_ * E * (q_ * E + sp.exp(t * y_) + NN_ - q_ - 1))
check("crumb: cross-multiplied difference = e^{ty} h(y)", sp.simplify(crossdiff - sp.exp(t * y_) * hcrumb) == 0)
check("h'(0) = (qE+N-q)(1 - t s_q)", sp.simplify(sp.diff(hcrumb, y_).subs(y_, 0) - (q_ * E + NN_ - q_) * (1 - t * s_q)) == 0)
check("h(1) = N with E = e^t", sp.simplify(hcrumb.subs({y_: 1, E: sp.exp(t)}) - NN_) == 0)
check("h''(y) = q E t^2 e^{-ty}", sp.simplify(sp.diff(hcrumb, y_, 2) - q_ * E * t ** 2 * sp.exp(-t * y_)) == 0)
ok = all(uv * mp.e ** (-cv * uv) <= 1 / (mp.e * cv) + mp.mpf("1e-45") for uv, cv in [(mp.mpf(random.uniform(0, 5)), mp.mpf(random.uniform(0.1, 20))) for _ in range(2000)])
check("u e^{-cu} <= 1/(e c) sampled", ok)
# Chebyshev identity used for the mean comparison
xs2 = sp.symbols("z1:4", real=True)
ws2 = sp.symbols("w1:4", real=True)
lhs_ch = 3 * sum(xi * wi for xi, wi in zip(xs2, ws2)) - sum(xs2) * sum(ws2)
rhs_ch = sum((xs2[i] - xs2[j]) * (ws2[i] - ws2[j]) for i in range(3) for j in range(i + 1, 3))
check("d sum x_i w_i - (sum x)(sum w) = sum_{i<j}(x_i-x_j)(w_i-w_j)", sp.simplify(lhs_ch - rhs_ch) == 0)

# ---------------------------------------------------------------------------
# 13. Envelope gap constant equals half of the Cohen-Fausti Lemma 5.2 bound
#     with uniform base measure (S_I = k/N) and Hilbert distance R = t
# ---------------------------------------------------------------------------
kk3, NN3 = sp.symbols("k N", positive=True)
cf = (kk3 / NN3) * (1 - kk3 / NN3) * (E - 1) / (1 + (kk3 / NN3) * (E - 1))
gap = kk3 * E / (NN3 + kk3 * (E - 1)) - kk3 / NN3
check("s_k - k/N = S(1-S)(E-1)/(1+S(E-1)) with S = k/N (Cohen-Fausti (41) specialization)", sp.simplify(cf - gap) == 0)

print()
print("FAILURES:", FAIL if FAIL else "none")
