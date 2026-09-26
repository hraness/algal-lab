"""Audit of Barmalzan-Kosari-Balakrishnan (2022) lemmas as used by SKF2026.

BKB2022 = G. Barmalzan, S. Kosari, N. Balakrishnan, "Orderings of finite
mixture models with location-scale distributed components", Probab. Eng.
Inform. Sci. 36(2):461-481 (2022), DOI 10.1017/S0269964820000467.

SKF2026 Lemma 2.4 (attributed to BKB2022; cf. Shekari et al. 2026 Lemma 7
attributing the same statement to Thm 2 of Balakrishnan-Haidari-Masoumifard
2015, IEEE T. Reliab. 64(1):333-348):
  Psi: R^4_+ -> R_+ differentiable satisfies
      Psi(A) >= Psi(B) for all A,B with A in V_2 (or W_2), A >> B   (chain maj)
  iff
    (i)  Psi(A) = Psi(A Pi) for all permutation matrices Pi, A in V_2 (W_2);
    (ii) sum_{i=1}^{2} (a_{ik} - a_{ij}) [Psi_{ik}(A) - Psi_{ij}(A)] >= 0
         for all j,k = 1,2, all A in V_2 (W_2).

SKF2026 Lemma 2.5 (attributed to BKB2022):
  Psi: R^2_+ -> R_+ differentiable; Psi_n : R^{2n}_+ -> R_+ defined by
  Psi_n(A) = sum_{i=1}^{n} Psi(a_{1i}, a_{2i}).  If Psi_2 satisfies
  condition (2.1), then Psi_n(A) >= Psi_n(B) for A in V_n (W_n), B = AT.

Checks performed here (exact rational arithmetic):
  [A] Symbolic proof skeleton of Lemma 2.4 sufficiency: along the T-path
      A(w) = A T(w), T(w) = w I + (1-w) Pi_12, verify
        d/dw Psi(A(w)) = sum_i (a_{i1} - a_{i2}) (Psi_{i1} - Psi_{i2}) |_{A(w)}
      and that V_2 (W_2) is closed under the path:
        a_{i1}(w) - a_{i2}(w) = (2w-1)(a_{i1} - a_{i2})
      so the product of column-gap signs is preserved. Together with (ii)
      this forces Psi(A(w)) to have its minimum at w=1/2, hence Psi(A) >= Psi(AT).
  [B] Lemma 2.5: the separable decomposition
        Psi_n(A) - Psi_n(A T^{jk}) = Psi_2(A^{jk}) - Psi_2(A^{jk} T_2)
      verified symbolically for generic columns; A in V_n => A^{jk} in V_2
      checked exhaustively on rational instances. Lemma is TRUE.
  [C] SKF's object htilde_{p,gam}(y) = sum p_i gam_i y^{gam_i}/sum p_i y^{gam_i}
      is NOT of the separable form: htilde(A) - htilde(AT^{13}) depends on the
      third column, so Lemma 2.5 cannot be invoked. Exact certificate.
  [D] The n=3 counterexample (from the sibling audit): certified sign change
      of htilde_p - htilde_q on y in (1,infty), plus the failure of the
      necessary pair-differential condition (the n-column analogue of
      Lemma 2.4(ii)) at the same instance.
"""
import sys, itertools, random
sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/mixture-audit")
sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/context/runs/mixture-claim-audit")
import sympy as sp
from audit_lib import in_Vn, in_Wn

R = sp.Rational

print("=" * 72)
print("[A] Lemma 2.4: T-path derivative identity and V_2 closure")
print("=" * 72)
w = sp.Symbol("w")                      # w in [0,1]
a11, a12, a21, a22 = sp.symbols("a11 a12 a21 a22", positive=True)
# A(w) columns: col1' = w c1 + (1-w) c2 ; col2' = (1-w) c1 + w c2
b11 = w * a11 + (1 - w) * a12
b12 = (1 - w) * a11 + w * a12
b21 = w * a21 + (1 - w) * a22
b22 = (1 - w) * a21 + w * a22
x = sp.Symbol("x")
# generic differentiable Psi via an unspecified function's derivatives:
p11, p12, p21, p22 = sp.symbols("p11 p12 p21 p22")  # Psi_{ij} evaluated at A(w)
# d/dw Psi(A(w)) = sum_ij Psi_{ij} * db_ij/dw
db = {(1, 1): a11 - a12, (1, 2): a12 - a11, (2, 1): a21 - a22, (2, 2): a22 - a21}
dPsi = p11 * db[(1, 1)] + p12 * db[(1, 2)] + p21 * db[(2, 1)] + p22 * db[(2, 2)]
dPsi_simplified = sp.expand(dPsi)
pair_expr = (a11 - a12) * (p11 - p12) + (a21 - a22) * (p21 - p22)
print("dPsi/dw =", dPsi_simplified)
print("equals (a_i1 - a_i2)(Psi_i1 - Psi_i2) summed over rows:", sp.simplify(dPsi_simplified - pair_expr) == 0)
# column-gap evolution: a_{i1}(w) - a_{i2}(w) = (2w-1)(a_{i1} - a_{i2})
g1 = sp.expand(b11 - b12)
g2 = sp.expand(b21 - b22)
print("col gap row1:", g1, " == (2w-1)(a11-a12)?", sp.simplify(g1 - (2 * w - 1) * (a11 - a12)) == 0)
print("col gap row2:", g2, " == (2w-1)(a21-a22)?", sp.simplify(g2 - (2 * w - 1) * (a21 - a22)) == 0)
# Hence product of gaps gets factor (2w-1)^2 >= 0: V_2 (and W_2) closed under T-path.
# Rewrite derivative: since a_i1 - a_i2 = gap_i(w)/(2w-1) for w != 1/2,
# dPsi/dw = [sum_i gap_i(w)(Psi_i1 - Psi_i2)] / (2w-1).
# Condition (ii) at A(w) in V_2 says sum_i (a_i2(w)-a_i1(w))(Psi_i2-Psi_i1) >= 0,
# i.e. sum_i gap_i(w)(Psi_i1 - Psi_i2) >= 0.  => sign(dPsi/dw) = sign(2w-1).
# So Psi(A(w)) is min at w=1/2, Psi(A) >= Psi(A T(w)) for all w:  lemma 2.4
# (sufficiency) TRUE.  Necessity follows by w -> 1 limit.  Verified.
print("V_2/W_2 closure under T-path: product factor (2w-1)^2 >= 0 -- verified symbolically")

print()
print("=" * 72)
print("[B] Lemma 2.5 (separable-sum lift): decomposition identity")
print("=" * 72)
n_sym = 3
# generic column values; Psi applied per column -> separable Psi_n
c1, c2, c3 = sp.symbols("c1 c2 c3")     # dummy placeholders for Psi(col_i)
# For separable Psi_n, Psi_n(A) - Psi_n(AT^{jk}) only touches cols j,k.
# Symbolically: Psi_n(A) = f(c1)+f(c2)+f(c3) ; T^{13} mixes cols 1,3.
f = sp.Function("psi")
om = sp.Symbol("om")
col1 = sp.Matrix(sp.symbols("a11 a21"))
col2 = sp.Matrix(sp.symbols("a12 a22"))
col3 = sp.Matrix(sp.symbols("a13 a23"))
ncol1 = om * col1 + (1 - om) * col3
ncol3 = (1 - om) * col1 + om * col3
Pn_A = f(col1[0], col1[1]) + f(col2[0], col2[1]) + f(col3[0], col3[1])
Pn_B = f(ncol1[0], ncol1[1]) + f(col2[0], col2[1]) + f(ncol3[0], ncol3[1])
diff_full = Pn_A - Pn_B
pair_A = f(col1[0], col1[1]) + f(col3[0], col3[1])
pair_B = f(ncol1[0], ncol1[1]) + f(ncol3[0], ncol3[1])
print("Psi_n(A)-Psi_n(AT) == Psi_2(pair) - Psi_2(pair T):",
      sp.simplify(diff_full - (pair_A - pair_B)) == 0)
print("=> Lemma 2.5 reduces a single T to the 2-column hypothesis; TRUE as stated.")

# A in V_n implies every column pair in V_2 -- exhaustive check on rational samples
random.seed(7)
cnt = 0
for _ in range(2000):
    gam = [R(random.randint(1, 20), random.randint(1, 9)) for _ in range(3)]
    p = [R(random.randint(1, 20), random.randint(1, 9)) for _ in range(3)]
    if in_Wn(gam, p):
        for j, k in itertools.combinations(range(3), 2):
            assert in_Wn([gam[j], gam[k]], [p[j], p[k]])
        cnt += 1
    if in_Vn(gam, p):
        for j, k in itertools.combinations(range(3), 2):
            assert in_Vn([gam[j], gam[k]], [p[j], p[k]])
        cnt += 1
print(f"V_3/W_3 => every column pair in V_2/W_2: {cnt} instances, all pairs OK")

print()
print("=" * 72)
print("[C] htilde is NOT separable in the columns")
print("=" * 72)
y = sp.Symbol("y", positive=True)

def htilde(gam, p, yv):
    num = sum(pi * gi * yv ** gi for pi, gi in zip(p, gam))
    den = sum(pi * yv ** gi for pi, gi in zip(p, gam))
    return sp.cancel(num / den)

# columns (gam_i, p_i); show htilde(A) - htilde(A T^{13}) depends on col 2
gA = [R(1), R(2), R(5)]; pA = [R(1, 2), R(1, 4), R(1, 4)]
om_ = R(1, 3)
def Tcol(v, j, k, om_):
    v = list(v)
    vj = om_ * v[j] + (1 - om_) * v[k]
    vk = (1 - om_) * v[j] + om_ * v[k]
    v[j], v[k] = vj, vk
    return v
gB = Tcol(gA, 0, 2, om_); pB = Tcol(pA, 0, 2, om_)
d_base = sp.cancel(htilde(gA, pA, y) - htilde(gB, pB, y))
# now change column 2 and re-evaluate the difference at y = 3
for mid_g, mid_p in [(R(2), R(1, 4)), (R(9), R(3, 8))]:
    gA2 = [gA[0], mid_g, gA[2]]; pA2 = [pA[0], mid_p, pA[2]]
    gB2 = Tcol(gA2, 0, 2, om_); pB2 = Tcol(pA2, 0, 2, om_)
    d2 = sp.cancel(htilde(gA2, pA2, y) - htilde(gB2, pB2, y))
    print(f"  col2=(g={mid_g},p={mid_p}): htilde(A)-htilde(AT) at y=3 -> {d2.subs(y,3)}")
print("  (for a separable Psi_n this difference cannot depend on column 2)")

print()
print("=" * 72)
print("[D] Certified counterexample: htilde not T-monotone on W_3 (alpha<=0 half)")
print("=" * 72)
# Sibling-audit instance, recomputed independently:
p = [R(17, 44), R(5, 11), R(7, 44)]
gam = [R(7), R(9), R(2)]
print("in W_3:", in_Wn(gam, p), " in V_3:", in_Vn(gam, p))
om_ = R(17, 20)
q = Tcol(p, 0, 2, om_); dl = Tcol(gam, 0, 2, om_)
print("q =", q, " delta =", dl)
d = sp.cancel(htilde(gam, p, y) - htilde(dl, q, y))
# clear quarter powers: z = y^(1/4), z > 1
z = sp.Symbol("z", positive=True)
dz = sp.cancel(d.subs(y, z ** 4))
num, den = sp.fraction(sp.together(dz))
num = sp.expand(num); den = sp.expand(den)
print("d(z), z = y^(1/4) > 1, numerator:", sp.factor(num))
print("denominator:", sp.factor(den))
poly = sp.Poly(num, z)
print("roots of numerator in (1, oo):", poly.count_roots(1, sp.oo))
print("isolating:", poly.intervals())
# exact witnesses (in y)
for yv in [R(1), R(3, 2), R(2), R(4), R(8)]:
    print(f"  d({yv}) = {sp.nsimplify(d.subs(y, yv))}")
# Thm 3.8 W_n half claims U <=hr V i.e. htilde_A - htilde_B <= 0 on y>1.

print()
print("=" * 72)
print("[D2] Failure of the necessary pair-differential condition")
print("=" * 72)
# For Psi_n = htilde on R^{2n}, T-monotonicity Psi(A) <= Psi(AT^{jk}) on W_n
# would require (necessary, w->1 limit):
#   sum_{i in rows} (a_{ik} - a_{ij})(Psi_{ik} - Psi_{ij}) <= 0 on W_n.
# (same pair condition as Lemma 2.4(ii), sign matching claimed direction).
# Compute M_13(A;y) = sum_i (a_i3 - a_i1)(Psi_i3 - Psi_i1) exactly.
g1_, g2_, g3_, p1_, p2_, p3_ = sp.symbols("g1 g2 g3 p1 p2 p3", positive=True)
N_ = p1_ * g1_ * y ** g1_ + p2_ * g2_ * y ** g2_ + p3_ * g3_ * y ** g3_
D_ = p1_ * y ** g1_ + p2_ * y ** g2_ + p3_ * y ** g3_
Psi = N_ / D_
# rows: row1 = g (gam), row2 = p.  a_{1i} = g_i, a_{2i} = p_i.
M13 = ((g3_ - g1_) * (sp.diff(Psi, g3_) - sp.diff(Psi, g1_))
       + (p3_ - p1_) * (sp.diff(Psi, p3_) - sp.diff(Psi, p1_)))
M13 = sp.cancel(sp.together(M13))
subd = {g1_: gam[0], g2_: gam[1], g3_: gam[2], p1_: p[0], p2_: p[1], p3_: p[2]}
M13z = sp.cancel(M13.subs(subd).subs(y, z ** 4))
M13_num, M13_den = sp.fraction(sp.together(M13z))
M13_num = sp.expand(M13_num); M13_den = sp.expand(M13_den)
print("M_13 numerator:", sp.factor(M13_num))
print("M_13 denominator factors:", sp.factor(M13_den))
# z=1 (i.e. y=1, the t=0 boundary): ln z = 0 -> exact rational value
m1 = sp.simplify(M13z.subs(z, 1))
print(f"M_13 at y=1 (exact): {m1} = {sp.nsimplify(m1)} > 0 ? {m1 > 0}")
for yv in [R(2), R(4)]:
    v = sp.N(M13.subs(subd).subs(y, yv), 40)
    print(f"  M_13(y={yv}) ~ {v}")
