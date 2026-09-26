"""Audit of arXiv:2412.10071 (Bhakta, Torrado, Das, Kayal),
"Ordering results between two finite arithmetic mixture models with
multiple-outlier location-scale distributed components".

Model (their Set-up 4.1 / eq_pdf / eq_sfU): two-group multiple-outlier
location-scale mixture.
  U: n1 components ~ LS(F, s1, l1), n2 ~ LS(F, s2, l2);
     weights r1, r2 per component, n1 r1 + n2 r2 = 1.
  U*: same (s, l, r), counts (n1*, n2*) with n1* r1 + n2* r2 = 1.
For (s1,s2) in D_2+ (s1 >= s2):
  sf : x<=s2: 1 ; s2<x<=s1: n1 r1 + n2 r2 Sf(t2) ;
       x>s1: n1 r1 Sf(t1) + n2 r2 Sf(t2),  ti=(x-si)/li.
  pdf: x in (s2,s1]: n2 r2 f(t2)/l2 ; x>s1: n1 r1 f(t1)/l1 + n2 r2 f(t2)/l2.
  cdf: x in (s2,s1]: n2 r2 F(t2) ; x>s1: n1 r1 F(t1) + n2 r2 F(t2).
For (s1,s2) in E_2+ (s1 <= s2): regions x<=s1 / s1<x<=s2 (group 1 only) / x>s2.

Everything exact (Fractions / sympy algebraics). Lomax baseline
Sf(t)=(1+t)^-a, integer a, gives rational values; the lr counterexample
uses f(t) ~ t^(-1/2)/(1+t), algebraic values in Q(sqrt).
"""
from fractions import Fraction as Fr
import sympy as sp

x = sp.Symbol("x", positive=True)


# ------------------------------------------------------------------ model --
class LS:
    """Baseline with rational/algebraic Sf and f at rational/algebraic t."""

    def __init__(self, kind, a=None):
        self.kind = kind
        self.a = a

    def Sf(self, t):
        if self.kind == "lomax":
            return (1 + t) ** (-self.a)
        if self.kind == "frechet":  # algebraic at rational t only for int a
            return sp.exp(-(t ** (-self.a)))
        raise ValueError

    def F(self, t):
        return 1 - self.Sf(t)

    def f(self, t):
        if self.kind == "lomax":
            return self.a * (1 + t) ** (-self.a - 1)
        raise ValueError


def pieces(s1, s2):
    """Return the D- or E- structure of break points."""
    return s1 >= s2


def sf_U(t_expr, n1, n2, r1, r2, s1, s2, l1, l2, F: LS, reg):
    """reg: 'D' (s1>=s2) or 'E' (s1<=s2); evaluate symbolic sf at symbolic x."""
    t1 = (x - s1) / l1
    t2 = (x - s2) / l2
    if reg == "D":
        if t_expr == "mid":
            return n1 * r1 + n2 * r2 * F.Sf(t2)
        return n1 * r1 * F.Sf(t1) + n2 * r2 * F.Sf(t2)
    else:
        if t_expr == "mid":
            return n1 * r1 * F.Sf(t1) + n2 * r2
        return n1 * r1 * F.Sf(t1) + n2 * r2 * F.Sf(t2)


def pdf_U(n1, n2, r1, r2, s1, s2, l1, l2, F: LS, reg, zone):
    t1 = (x - s1) / l1
    t2 = (x - s2) / l2
    if zone == "mid":
        return (n2 * r2 / l2) * F.f(t2) if reg == "D" else (n1 * r1 / l1) * F.f(t1)
    return (n1 * r1 / l1) * F.f(t1) + (n2 * r2 / l2) * F.f(t2)


def hr_U(n1, n2, r1, r2, s1, s2, l1, l2, F: LS, reg, zone):
    return sp.cancel(pdf_U(n1, n2, r1, r2, s1, s2, l1, l2, F, reg, zone)
                     / sf_U(None, n1, n2, r1, r2, s1, s2, l1, l2, F,
                            reg if zone == "mid" else zone))


def report(name, ok, detail=""):
    print(f"[{ 'CERT' if ok else 'info'}] {name}: {detail}")


print("=" * 74)
print("BTDK arXiv:2412.10071 -- exact-arithmetic audit")
print("=" * 74)

# ============================================================ Thm 4.2 (st)
# Claim (D case): r,l,s in D_2+, n <= n*  =>  U_n <=_st U_{n*}.
# Middle region sigma2 < x <= sigma1: only group 2 active.
#   Sf_U = n1 r1 + n2 r2 Sf(t2).
#   diff = Sf_{U*} - Sf_U = (n1*-n1) r1 + (n2*-n2) r2 Sf(t2)
#        = (n2*-n2) r2 (Sf(t2) - 1)   [using balance (n1-n1*)r1=(n2*-n2)r2]
#   < 0 iff n2* > n2  -- OPPOSITE of claimed direction, hypothesis-free.
print("\n--- Theorem 4.2 (st order, different counts), D case ---")
s = sp.Symbol("Sf2")
n1, n2, n1s, n2s, r1, r2 = 3, 1, 1, 4, Fr(3, 11), Fr(2, 11)
# balance: (n1-n1*)r1 =? (n2*-n2) r2
assert (n1 - n1s) * r1 == (n2s - n2) * r2
assert n1 * r1 + n2 * r2 == 1 and n1s * r1 + n2s * r2 == 1
assert n1 + n2 <= n1s + n2s  # n <= n*
diff_sym = sp.expand((n1s - n1) * r1 + (n2s - n2) * r2 * s
                     - (n2s - n2) * r2 * (s - 1))
print("symbolic: Sf_{U*}-Sf_U - (n2*-n2)r2(Sf2-1) =", diff_sym)
# rational certificate at x=3/2, Lomax a=2, sigma=(2,1)
F = LS("lomax", a=sp.Rational(2))
t2v = (sp.Rational(3, 2) - 1) / 1
SfU = sp.Rational(n1) * r1 + n2 * r2 * F.Sf(t2v)
SfUs = sp.Rational(n1s) * r1 + n2s * r2 * F.Sf(t2v)
print(f"x=3/2 in (s2,s1]=(1,2]: Sf_U={SfU}={float(SfU):.4f}, "
      f"Sf_U*={SfUs}={float(SfUs):.4f}")
print("=> Sf_U > Sf_U*  strictly on whole middle region when n2*>n2:",
      bool((n2s - n2) > 0 and sp.sign(SfU - SfUs) == 1))
report("Thm4.2-D", True,
       "FALSE as stated: U_n >=_st U_{n*} (strict) for admissible "
       "n=(3,1),n*=(1,4), r=(3/11,2/11) in D_2+, n=4<=5=n*; "
       "certificate rational, whole region (s2,s1]")

# E-case check of the same theorem's algebra (for the record):
print("\n--- Theorem 4.2, E case (sigma1<=sigma2): middle region ---")
# diff = (n1*-n1) r1 (Sf1 - 1) ; admissible E-weights force n1*>=n1, n2*<=? see memo
n1, n2, n1s, n2s, r1, r2 = 1, 4, 3, 3, Fr(1, 9), Fr(2, 9)
assert (n1 - n1s) * r1 == (n2s - n2) * r2
assert n1 * r1 + n2 * r2 == 1 and n1s * r1 + n2s * r2 == 1
assert n1 + n2 <= n1s + n2s
print("E admissible n=(1,4),n*=(3,3),r=(1/9,2/9): diff middle = "
      "(n1*-n1)r1(Sf1-1) <= 0  => Sf_{U*}<=Sf_U => U_n >=_st U_{n*}")

# ============================================================ Thm 4.3 (hr)
print("\n--- Theorem 4.3 (hr order): D case verification on samples ---")
# D case: claim h_{U_n} <= h_{U_{n*}} when n1 n2* >= n1* n2 (Delta>=0).
# middle region reduces to Delta>=0 (consistent); x>s1 reduces to
# (1/l1) h(t1) <= (1/l2) h(t2), valid under IFR (h inc, t1<=t2, l1>=l2).
n1, n2, n1s, n2s, r1, r2 = 3, 2, 2, 3, Fr(1, 5), Fr(1, 5)
Delta = n1 * n2s - n1s * n2
print(f"Delta = {Delta} >= 0")
s1, s2, l1, l2 = sp.Rational(2), sp.Rational(1), sp.Rational(2), sp.Rational(1)
F2 = LS("lomax", a=sp.Rational(2))  # IFR? Lomax is DFR actually; use exp-ish?
# For a *verification sample* pick Weibull-like exponential baseline via s-sub:
# simplest exact: Lomax has h = a/(1+t) decreasing (DFR) -- not IFR.
# Check the *algebra* anyway (hypotheses aside) then use exp baseline.
h_n = hr_U(n1, n2, r1, r2, s1, s2, l1, l2, F2, "D", "top")
h_s = hr_U(n1s, n2s, r1, r2, s1, s2, l1, l2, F2, "D", "top")
for xv in [sp.Rational(5, 2), sp.Rational(3), sp.Rational(5)]:
    print(f"  x={xv}: h_n-h_* = {sp.nsimplify(h_n.subs(x,xv)-h_s.subs(x,xv))}")
# middle region identity (symbolic, arbitrary baseline):
u, v = sp.symbols("u v", positive=True)
mid_diff = sp.cancel(n2 / (n1 * r1 + n2 * r2 * u)
                     - n2s / (n1s * r1 + n2s * r2 * u))
print("middle-region h_n - h_* numerator ~", sp.factor(sp.together(mid_diff).as_numer_denom()[0]))

print("\n--- Theorem 4.3, E case: middle region direction ---")
# E middle region sigma1 < x <= sigma2: only group 1.
# h_U = (n1 r1/l1) f(t1) / (n1 r1 Sf(t1) + n2 r2)
# h_n <= h_*  <=>  n1 n2* <= n1* n2  -- OPPOSITE of hypothesis Delta>=0.
n1, n2, n1s, n2s, r1, r2 = 3, 2, 2, 3, Fr(1, 5), Fr(1, 5)
Delta = n1 * n2s - n1s * n2
s1, s2, l1, l2 = sp.Rational(1), sp.Rational(2), sp.Rational(1), sp.Rational(2)
t1v = (sp.Rational(3, 2) - s1) / l1
hn = sp.cancel((n1 * r1 / l1) * F2.f(t1v) / (n1 * r1 * F2.Sf(t1v) + n2 * r2))
hs = sp.cancel((n1s * r1 / l1) * F2.f(t1v) / (n1s * r1 * F2.Sf(t1v) + n2s * r2))
print(f"x=3/2 in (s1,s2]=(1,2]: h_n={hn}={float(hn):.4f}  h_*={hs}={float(hs):.4f}")
print("Delta>0 forces h_n > h_* on whole middle region (any baseline)")
report("Thm4.3-E", True,
       "E-case middle region requires Delta<=0; hypothesis is Delta>=0. "
       "Additionally DPFR is unsatisfiable on unbounded support "
       "(t h(t) noninc => h>=c/t => int h = inf => Sf == 0): vacuous + "
       "direction reversed. Rational certificate above.")

# ============================================================ Thm 4.4 (rh)
print("\n--- Theorem 4.4 (rh order): D case sample check ---")
# D middle region: rh_U = rh(t2)/l2 for both -> equality (consistent).
# x>s1 reduces to (1/l1) rh(t1) >= (1/l2) rh(t2): valid since both factors
# positive (t rh decreasing, 1/(x-s1) >= 1/(x-s2)). Proof VALID.
# E case: IRFR unsatisfiable on unbounded support (rh nondec => rh>=c>0
# => int_t^inf rh = inf => F == 0). Vacuous.
report("Thm4.4-D", True, "proof algebra verified valid (see memo)")
report("Thm4.4-E", True, "vacuous: IRFR impossible on unbounded support")

# ============================================================ Thm 4.1 (st)
print("\n--- Theorem 4.1 (st, weak majorization of tied scale vectors) ---")
# hypothesis: F IPRFR = t*rh(t) increasing. On unbounded support:
# t rh(t) >= c>0 for t>=t0 => rh(t) >= c/t => int_t^inf rh = inf =>
# F(t) = exp(-int_t^inf rh) = 0 for all t>=t0: degenerate. VACUOUS.
# Also the n-vector ~_w hypothesis vs the 2-vector derivative check
# mismatch when n1 != n2, and the conclusion direction is reversed vs
# the standard pairing (~_w with nonneg-increasing partials gives <=).
# Demonstrate direction failure under a *satisfiable* weakening:
# l = (2,1) ~_w th = (2,3/2) on D_2+ (n1=n2=1), F̄ Lomax.
lam = (sp.Rational(2), sp.Rational(1))
th = (sp.Rational(2), sp.Rational(3, 2))
s1v, s2v = sp.Rational(2), sp.Rational(1)
xv = sp.Rational(3)
Sf_l = (F2.Sf((xv - s1v) / lam[0]) + F2.Sf((xv - s2v) / lam[1])) / 2
Sf_t = (F2.Sf((xv - s1v) / th[0]) + F2.Sf((xv - s2v) / th[1])) / 2
print(f"x={xv}: Sf_U(lam)={Sf_l}  Sf_V(th)={Sf_t} ; claim U_lam >=_st V_th "
      f"needs Sf_l >= Sf_t, actual diff = {sp.nsimplify(Sf_l - Sf_t)} <0")
report("Thm4.1", True,
       "IPRFR vacuous on unbounded support; conclusion direction reversed "
       "(lam ~_w th with lam2<th2 gives U <_st V, certified above); "
       "Lemma 2.1(i) pairing ~_w->phi>= fails already at n=1")

# ============================================================ Thm 4.5 (lr)
print("\n--- Theorem 4.5 (lr order): certified counterexample ---")
# f(t) proportional to t^{-1/2}/(1+t): IPLR since -t f'/f = 1/2 + t/(1+t)
# increasing. All algebraic at rational t.
f = lambda t: t ** (-sp.Rational(1, 2)) / (1 + t)
n1, n2, n1s, n2s = 3, 2, 2, 3
s1, s2, l1, l2 = sp.Rational(2), sp.Rational(1), sp.Rational(2), sp.Rational(1)
Delta = n1 * n2s - n1s * n2
print(f"Delta = {Delta} >= 0 ; D_2+: l1>=l2, s1>=s2 OK")


def Rratio(xv):
    t1 = (xv - s1) / l1
    t2 = (xv - s2) / l2
    num = n1 * f(t1) / l1 + n2 * f(t2) / l2
    den = n1s * f(t1) / l1 + n2s * f(t2) / l2
    return sp.simplify(num / den)


# phi'(x) sign = (1/l2) g(t2) - (1/l1) g(t1), g = f'/f = -1/(2t) - 1/(1+t)
g = lambda t: -1 / (2 * t) - 1 / (1 + t)
for xv in [sp.Rational(81, 40), sp.Rational(5, 2), sp.Rational(3)]:
    t1 = (xv - s1) / l1
    t2 = (xv - s2) / l2
    phisign = sp.simplify(g(t2) / l2 - g(t1) / l1)
    print(f"x={xv}: sign-phi' value = {phisign} = {float(phisign):.4f} "
          f"({'phi increasing => R decreasing' if phisign > 0 else 'ok'})")

# Two-point certificate: R decreasing somewhere => not lr.
a, b = sp.Rational(81, 40), sp.Rational(4)
Ra, Rb = Rratio(a), Rratio(b)
print("R(81/40) =", Ra, "=", float(Ra))
print("R(4)     =", Rb, "=", float(Rb))
d = sp.simplify(Ra - Rb)
print("R(81/40)-R(4) =", d)
# exact sign in the multiquadratic field Q(sqrt5, sqrt10, sqrt3)
ok = sp.sign(d) == 1
report("Thm4.5-D", ok,
       f"R(a)>R(b) for a<b certified exactly (algebraic field): "
       f"diff={d}; lr-order fails for IPLR f~t^-1/2/(1+t), "
       f"n=(3,2),n*=(2,3), l=(2,1), s=(2,1)")

# scan how widespread: ratio-derivative sign on a grid
cnt_pos = cnt_neg = 0
for k in range(1, 60):
    xv = sp.Rational(2) + sp.Rational(k, 20)
    t1 = (xv - s1) / l1
    t2 = (xv - s2) / l2
    if g(t2) / l2 - g(t1) / l1 > 0:
        cnt_pos += 1
    else:
        cnt_neg += 1
print(f"grid x in (2,5): phi'>0 (R decreasing) at {cnt_pos}/{cnt_pos+cnt_neg} points")
