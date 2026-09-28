"""Independent C3 confirmations for doi:10.3390/sym13122248 refutations.

Refuted records:
  Example 1 | st  -- paper's own instance; claim Y1:3 <=st Y*1:3.
      Witness x=64/15: S*(x)-S(x) < 0 (strict interval enclosure).
  Example 3 | hr  -- claim: survival ratio non-monotone (no hr either way).
      Confirmed instead: E_hr(U<=hr V) is strictly positive at all tested
      points (dense mpf scan + interval enclosures), so U<=hr V survives;
      the reverse direction fails strictly at x=1/10^12.
  Example 4 | hr  -- same pattern (independent components).
  Theorem 5 | hr  -- Y1:n <=hr Y*1:n claimed under (i) prod p <= prod p*,
      (ii) psi log-concave [print; proof uses log-convex direction],
      (iii) psi(1-psi)/psi' decreasing+convex.  No baseline ordering is
      stated, so U-baseline heavier than V-baseline is a legal instance:
      strict witness at x=64/15.

Model: zeta(a,b,G) = a(1-T^b)/(a+(1-a)T^b), T=1-(1-G)^2;
series survival = (prod p) psi(sum phi(zeta_i)).
"""
import sympy as sp
from mpmath import mp, iv, mpf

mp.dps = 100
iv.dps = 150
t = sp.Symbol("t", positive=True)


def ie(e, x0):
    if e == t:
        return iv.mpf(int(x0.p)) / iv.mpf(int(x0.q))
    if e.is_Rational:
        return iv.mpf(int(e.p)) / iv.mpf(int(e.q))
    if e.is_Add:
        s = iv.mpf(0)
        for a in e.args:
            s += ie(a, x0)
        return s
    if e.is_Mul:
        p = iv.mpf(1)
        for a in e.args:
            p *= ie(a, x0)
        return p
    if e.is_Pow:
        b_, e_ = e.args
        if e_.is_Integer:
            r = iv.mpf(1)
            for _ in range(abs(int(e_))):
                r *= ie(b_, x0)
            return r if int(e_) >= 0 else 1 / r
        return iv.exp(ie(e_, x0) * iv.log(ie(b_, x0)))
    if e.func == sp.exp:
        return iv.exp(ie(e.args[0], x0))
    if e.func == sp.log:
        return iv.log(ie(e.args[0], x0))
    raise ValueError(type(e))


def T_of(G):
    return 1 - (1 - G) ** 2


def zeta(a, b, G):
    T = T_of(G)
    return a * (1 - T ** b) / (a + (1 - a) * T ** b)


def clayton_psi(th, s):
    return (sp.Rational(th) * s + 1) ** (-1 / sp.Rational(th))


def clayton_phi(th, u):
    return (u ** (-sp.Rational(th)) - 1) / sp.Rational(th)


def amh_psi(s):
    return 2 / (1 + sp.exp(s))


def amh_phi(u):
    return sp.log(2 / u - 1)


def series_S(albetas, G, psi, phi, ps):
    return sp.prod(list(ps)) * psi(
        sum(phi(zeta(a, b, G)) for a, b in albetas))


R = sp.Rational
GLom = 1 - 1 / (1 + t)
GExp = 1 - sp.exp(-t)
GU = t

# ---------- Example 1 (paper's own numbers) ----------
albetas = [(R(11, 10), R(2)), (R(4), R(5)), (R(65, 10), R(6))]
gdelts = [(R(35, 10), R(9, 2)), (R(4), R(5)), (R(63, 10), R(29, 5))]
ps = [sp.exp(-R(5, 100)), sp.exp(-R(8, 100)), sp.exp(-R(22, 100))]
pss = [sp.exp(-R(1, 100)), sp.exp(-R(21, 100)), sp.exp(-R(3, 100))]
SU = series_S(albetas, GLom, lambda s: clayton_psi(2, s),
              lambda u: clayton_phi(2, u), ps)
SV = series_S(gdelts, GExp, lambda s: clayton_psi(4, s),
              lambda u: clayton_phi(4, u), pss)
Est = SV - SU            # claim Y<=stY* needs Est>=0
pt = R(64, 15)
v = ie(Est, pt)
print("Ex1: E_st(64/15) in [%s, %s] -> %s" % (v.a, v.b, "NEG" if v.b < 0 else "?"))
assert v.b < 0
print("Ex1 REFUTED: printed st-order fails at x=64/15")

# ---------- Example 3 ----------
ab = [(R(2), R(1)), (R(3), R(1))]
gd = [(R(4), R(1)), (R(6), R(1))]
SU3 = series_S(ab, GU, amh_psi, amh_phi, [R(1, 2), R(1, 2)])
SV3 = series_S(gd, GU, amh_psi, amh_phi, [R(3, 10), R(1, 4)])
fSU = sp.lambdify(t, SU3, modules="mpmath")
fSV = sp.lambdify(t, SV3, modules="mpmath")
# dense scan of ratio SV/SU for monotonicity
vals = [fSV(mpf(i) / 400) / fSU(mpf(i) / 400) for i in range(1, 399)]
mono_up = all(vals[i] <= vals[i + 1] for i in range(len(vals) - 1))
print("Ex3: ratio S*/S strictly increasing on 398-pt scan:", mono_up)
assert mono_up
# strict-interval enclosures for E_hr(U<=hrV) on a grid: must be >=0
fU3 = -sp.diff(SU3, t); fV3 = -sp.diff(SV3, t)
Ehr = fU3 * SV3 - fV3 * SU3
neg3 = 0
for i in range(1, 40):
    v = ie(Ehr, R(i, 40))
    if v.a < 0:
        neg3 += 1
print("Ex3: E_hr(U<=hrV) negative enclosures on grid:", neg3, "/39")
assert neg3 == 0
# reverse direction strict failure at tiny x
Ehr_rev = fV3 * SU3 - fU3 * SV3
v = ie(Ehr_rev, R(1, 10 ** 12))
print("Ex3: E_hr(V<=hrU) at 1e-12 in [%s,%s]" % (v.a, v.b))
assert v.b < 0
print("Ex3 REFUTED: U<=hrV holds on bounded test; reverse fails -> "
      "printed 'neither direction' wrong")

# ---------- Example 4 ----------
ab4 = [(R(6, 5), R(2)), (R(6, 5), R(7))]
gd4 = [(R(6, 5), R(6)), (R(6, 5), R(9))]
ip_psi = lambda s: sp.exp(-s)
ip_phi = lambda u: -sp.log(u)
SU4 = series_S(ab4, GU, ip_psi, ip_phi, [R(1, 2), R(1, 2)])
SV4 = series_S(gd4, GU, ip_psi, ip_phi, [R(3, 4), R(1)])
fU4 = sp.lambdify(t, SU4, modules="mpmath")
fV4 = sp.lambdify(t, SV4, modules="mpmath")
vals = [fV4(mpf(i) / 500) / fU4(mpf(i) / 500) for i in range(1, 499)]
mono_up = all(vals[i] <= vals[i + 1] for i in range(len(vals) - 1))
print("Ex4: ratio S*/S strictly increasing on 498-pt scan:", mono_up)
assert mono_up
fU4d = -sp.diff(SU4, t); fV4d = -sp.diff(SV4, t)
Ehr4 = fU4d * SV4 - fV4d * SU4
neg4 = sum(1 for i in range(1, 40) if ie(Ehr4, R(i, 40)).a < 0)
print("Ex4: E_hr(U<=hrV) negative enclosures:", neg4, "/39")
assert neg4 == 0
v = ie(fV4d * SU4 - fU4d * SV4, R(1, 10 ** 12))
assert v.b < 0
print("Ex4 REFUTED: U<=hrV survives bounded test; printed 'neither' wrong")

# ---------- Theorem 5 ----------
# Gumbel theta=2 generator, common beta, alpha ~m gamma, Pi p <= Pi p*.
# Legal instance (no baseline ordering is printed): U baseline GLom
# (heavier), V baseline GExp (lighter).
def gumbel_psi(th, s):
    return sp.exp(-s ** (1 / sp.Rational(th)))


def gumbel_phi(th, u):
    return (-sp.log(u)) ** sp.Rational(th)


U = [(R(3), R(2)), (R(1), R(2))]
V = [(R(2), R(2)), (R(2), R(2))]
SU5 = series_S(U, GLom, lambda s: gumbel_psi(2, s),
               lambda u: gumbel_phi(2, u), [R(1, 2)] * 2)
SV5 = series_S(V, GExp, lambda s: gumbel_psi(2, s),
               lambda u: gumbel_phi(2, u), [R(3, 4)] * 2)
fU5 = -sp.diff(SU5, t); fV5 = -sp.diff(SV5, t)
E5 = fU5 * SV5 - fV5 * SU5   # U<=hrV needs >=0
for pt in (R(64, 15), R(32, 15), R(7), R(9)):
    v = ie(E5, pt)
    print("Thm5: E_hr(%s) in [%s,%s]" % (pt, v.a, v.b))
v = ie(E5, R(64, 15))
assert v.b < 0
print("Thm5 REFUTED: strict witness at x=64/15 under printed hypotheses "
      "(which contain no baseline-ordering condition)")

print("\nALL CONFIRMED")
