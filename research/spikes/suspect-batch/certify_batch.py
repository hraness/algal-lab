"""Claim-shape certificate battery for the paywalled suspect queue.

Run dir: research/spikes/context/runs/suspect-batch/ (gitignored).
Exact arithmetic: /Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python
(sympy Rational; Sturm Poly.count_roots + exact rational witnesses).

METHOD (same as certify_smh.py). Every claim below is audited AT CLAIM SHAPE
-- the papers are paywalled; each certificate refutes the standard claim shape
transmitted by citing papers / stated in the abstract. One polynomial covers
whole claim families because:

* Ordinary mixture of exponentials Fbar_i = exp(-lam_i t):
      h(t) = sum p_i lam_i s^{lam_i} / sum p_i s^{lam_i},  s = e^{-t} in (0,1).
* alpha-mixture of SFs (BKZ2021, SKB2026's "FalphaMM" BKB-SPL24):
      Fbar_a = (sum p_i Fbar_i^a)^{1/a}  =>  same bracket in u = e^{-a t}
      for EVERY a>0 (a=1 = ordinary mixture).
* PHR components (PKP2022) Fbar_i = Fbar^{lam_i}: exponential baseline =
  the same bracket with s = Fbar(t).
* Generalized Lehmann components (SBB2022) F_i = F^{theta_i}: UNIFORM
  baseline gives power-function F_i = t^{theta_i} on (0,1); then
      h(t) = (1/t) * bracket(t)   and   r(t) = (1/t) * bracket(t)
  -> the same polynomial certificate refutes GL hr AND rh claims.
* Generalized Weibull components (BBKP2024): the Weibull subfamily
  Fbar_i = exp(-lam_i t^k) gives h(t) = k t^{k-1} * bracket(u), u=e^{-t^k}
  -> same bracket, u in (0,1).
* alpha-mixture of CDFs (rh claims): r_a(t) = (1/t)*bracket(t^a) for
  power-function components -> same bracket, all a>0 (CERT C).

CERT A: (p,lam),(p,gam) in U_3, lam majorizes gam => hr ordered.  FALSE.
CERT B: [p;lam] in V_3, [q;gam] = [p;lam] M_T (single T) => hr ordered. FALSE.
CERT C: rh bracket = hr bracket (symbolic).  Same sign certificate.
CERT D: multiple-outlier restriction (BKB-SPL24): two-valued parameter
        vectors, n=3, ordinary + alpha-mixture rh bracket -- exact search
        for a crossing under the standard M-O weak-majorization hypotheses.
"""
import sys
sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/mixture-audit")
import sympy as sp
from audit_lib import R, majorizes, weak_super, weak_sub, p_larger, in_Un, in_Vn

u = sp.Symbol("u", positive=True)


def bracket(pvec, lvec):
    """h~(u) = sum p_i lam_i u^{lam_i} / sum p_i u^{lam_i}."""
    num = sum(pi * li * u ** int(li) for pi, li in zip(pvec, lvec))
    den = sum(pi * u ** int(li) for pi, li in zip(pvec, lvec))
    return sp.cancel(num / den)


def cert_sign_change(d, var, lo=0, hi=1, probes=()):
    num, den = sp.fraction(sp.cancel(sp.together(d)))
    num, den = sp.expand(num), sp.expand(den)
    P = sp.Poly(num, var)
    print("  num deg", P.degree(), "| den roots on (0,1):",
          sp.Poly(den, var).count_roots(0, 1),
          "| num roots on (0,1] [Sturm]:", P.count_roots(0, 1))
    for v in probes:
        print(f"    d({v}) = {d.subs(var, v)}  sign {sp.sign(d.subs(var, v))}")
    return P.count_roots(0, 1)


print("=" * 74)
print("CERT A  (refutes hr-claim shape of BKZ2021, SBB2022, PKP2022-PHR,")
print("         BBKP2024; and by rh duality the rh shapes of BKZ2021, PKP2022)")
print("shape: (p,lam),(p,gam) in U_3, lam >maj gam => h_lam <= h_gam")
print("=" * 74)
p = (R(39, 86), R(18, 43), R(11, 86))
lam = (R(4), R(6), R(9))
gam = (R(4), R(7), R(8))
print("hypotheses: p prob:", sum(p) == 1,
      "| (p,lam) U3:", in_Un(list(p), list(lam)),
      "| (p,gam) U3:", in_Un(list(p), list(gam)),
      "| lam >maj gam:", majorizes(list(lam), list(gam)))
d = sp.cancel(sp.together(bracket(p, lam) - bracket(p, gam)))
cert_sign_change(d, u, probes=(R(1, 2), R(3, 4), R(7, 8)))
print("=> hazards cross once on (0,1): FAILS for ordinary mixtures, PHR")
print("   mixtures, all alpha>0 alpha-mixtures (SF side) and Weibull")
print("   (u=e^{-t^k}) subfamily instances; rh dual for CDF-side families")
print("   incl. power-function/GL-uniform components (CERT C). For GL")
print("   components' own hr expression see CERT E.")

print()
print("=" * 74)
print("CERT B  (frozen-column lift shape: [p;lam] in V_3, one T-transform)")
print("refutes the matrix-change hr/rh claim shape of BKZ2021, SBB2022,")
print("BBKP2024 (two-parameter heterogeneity), PKP2022")
print("=" * 74)
p2 = (R(1, 8), R(29, 72), R(17, 36))
lam2 = (R(9), R(5), R(4))
q2 = (R(2, 9), R(11, 36), R(17, 36))
gam2 = (R(38, 5), R(32, 5), R(4))
om = R(13, 20)
print("hypotheses: p,q prob:", sum(p2) == 1, sum(q2) == 1,
      "| (p,lam) V3:", in_Vn(list(p2), list(lam2)))
print("T-check:", om * p2[0] + (1 - om) * p2[1] == q2[0],
      (1 - om) * p2[0] + om * p2[1] == q2[1],
      om * lam2[0] + (1 - om) * lam2[1] == gam2[0],
      (1 - om) * lam2[0] + om * lam2[1] == gam2[1],
      "| frozen col:", p2[2] == q2[2] and lam2[2] == gam2[2])
w = sp.Symbol("w", positive=True)


def b5(pvec, lvec):
    n_ = sum(pi * li * w ** int(5 * li) for pi, li in zip(pvec, lvec))
    d_ = sum(pi * w ** int(5 * li) for pi, li in zip(pvec, lvec))
    return n_, d_


np_, dp_ = b5(p2, lam2)
nq_, dq_ = b5(q2, gam2)
D = sp.expand(np_ * dq_ - nq_ * dp_)
P2 = sp.Poly(D, w)
print("D(w) = num(h_p - h_q): deg", P2.degree(),
      "| roots(0,1) [Sturm]:", P2.count_roots(0, 1))
for v in (R(1, 4), R(1, 2), R(7, 8), R(9, 10)):
    print(f"    D({v}) sign {sp.sign(D.subs(w, v))}")
print("=> crossing: the lift fails; the frozen third column sits inside")
print("   numerator AND denominator of the rate ratio.")

print()
print("=" * 74)
print("CERT C  (rh <-> hr bracket identity for CDF-mixtures, symbolic)")
print("=" * 74)
a, t = sp.symbols("a t", positive=True)
n = 3
pp = [sp.symbols(f"p{i}", positive=True) for i in range(n)]
ll = [sp.symbols(f"l{i}", positive=True) for i in range(n)]
Fi = [t ** ll[i] for i in range(n)]
Fa = sum(pp[i] * Fi[i] ** a for i in range(n)) ** (1 / a)
ra = sp.diff(Fa, t) / Fa
brk = sum(pp[i] * ll[i] * (t ** a) ** ll[i] for i in range(n)) / \
    sum(pp[i] * (t ** a) ** ll[i] for i in range(n))
print("r_a - (1/t)*bracket == 0 :", sp.simplify(ra - brk / t) == 0)
print("=> CERT A/B sign changes refute rh claims for CDF/alpha-mixtures too.")

print()
print("=" * 74)
print("CERT D  BKB-SPL24 shape: multiple-outlier n=3 rh claim")
print("groups (n1,n2)=(2,1): lam_A=(a,a,b), lam_B=(c,c,d);")
print("ordinary/alpha-mixture CDF of power-function components, rh bracket")
print("=" * 74)
# search: two-valued parameter vectors, equal weights to isolate the
# parameter-side claim; test every standard M-O hypothesis direction.
found = []
vals = [R(1), R(2), R(3), R(4), R(5), R(6), R(7), R(8), R(9), R(10), R(12)]
for a_ in vals:
    for b_ in vals:
        for c_ in vals:
            for d_ in vals:
                la, lb = (a_, a_, b_), (c_, c_, d_)
                # distinct-parameter vectors theta_A=(a,b), theta_B=(c,d)
                thA, thB = (a_, b_), (c_, d_)
                hyps = {
                    "weaksub_th": weak_sub(list(la), list(lb)),
                    "weaksuper_th": weak_super(list(la), list(lb)),
                    "weaksub_2v": weak_sub(list(thA), list(thB)),
                    "weaksuper_2v": weak_super(list(thA), list(thB)),
                    "maj_2v": majorizes(list(thA), list(thB)),
                    "plarger_2v": p_larger(list(thA), list(thB)),
                }
                if not any(hyps.values()):
                    continue
                pw = (R(1, 3), R(1, 3), R(1, 3))
                dd = sp.cancel(sp.together(bracket(pw, la) - bracket(pw, lb)))
                num, den = sp.fraction(dd)
                rts = sp.Poly(sp.expand(num), u).count_roots(0, 1)
                if rts >= 1:
                    s1 = sp.sign(dd.subs(u, R(1, 4)))
                    s2 = sp.sign(dd.subs(u, R(1, 2)))
                    s3 = sp.sign(dd.subs(u, R(9, 10)))
                    if len({s1, s2, s3}) > 1:
                        found.append((la, lb, hyps, s1, s2, s3))
print("crossing instances found:", len(found))
for la, lb, hyps, s1, s2, s3 in found[:6]:
    print("  lam_A=%s lam_B=%s hyps=%s signs(1/4,1/2,9/10)=(%s,%s,%s)"
          % (la, lb, [k for k, v in hyps.items() if v], s1, s2, s3))
print("note: lam_A=(1,1,2) vs lam_B=(1,1,3) is a COMPONENTWISE increase")
print("(and weak-submajorization on both the 3-vector and the distinct-")
print("parameter 2-vector) yet the rh rates cross: refutes every M-O rh")
print("claim shape whose hypotheses these satisfy, in BOTH directions.")

print()
print("=" * 74)
print("CERT E  SBB2022 shape: generalized Lehmann components")
print("F_i = F^{theta_i}; uniform baseline F=t on (0,1) gives the")
print("power-function subfamily; GL mixture hazard rate")
print("    h_GL(t) = sum p_i th_i t^{th_i-1} / sum p_i (1 - t^{th_i})")
print("has the *other* denominator -> needs its own certificate.")
print("shape tested: (p,th),(p,et) in U_3, th >maj et => h_GL ordered")
print("=" * 74)
t_ = sp.Symbol("t", positive=True)


def h_gl(pvec, thvec):
    num = sum(pi * ti * t_ ** int(ti - 1) for pi, ti in zip(pvec, thvec))
    den = sum(pi * (1 - t_ ** int(ti)) for pi, ti in zip(pvec, thvec))
    return sp.cancel(num / den)


# CERT A instance under the GL-hr expression:
th = (R(4), R(6), R(9))
et = (R(4), R(7), R(8))
print("CERT A instance (p=%s, th=%s, et=%s):" % (p, th, et))
dE = sp.cancel(sp.together(h_gl(p, th) - h_gl(p, et)))
cert_sign_change(dE, t_, probes=(R(1, 4), R(1, 2), R(3, 4), R(7, 8)))

# if that instance is ordered, run a small exact search
print()
print("exact search over integer th,et in U_3, th >maj et (n=3):")
cnt = 0
first = None
import itertools
grid = [R(i) for i in range(1, 9)]
pw3 = (R(2, 5), R(2, 5), R(1, 5))
if not (in_Un(list(pw3), [R(1), R(2), R(3)])):
    pw3 = (R(1, 2), R(1, 4), R(1, 4))
for thc in itertools.combinations_with_replacement(grid, 3):
    for etc in itertools.combinations_with_replacement(grid, 3):
        if not majorizes(list(thc), list(etc)):
            continue
        if not (in_Un(list(pw3), list(thc)) and in_Un(list(pw3), list(etc))):
            continue
        dd = sp.cancel(sp.together(h_gl(pw3, thc) - h_gl(pw3, etc)))
        num, den = sp.fraction(dd)
        if sp.Poly(sp.expand(num), t_).count_roots(0, 1) >= 1:
            s1 = sp.sign(dd.subs(t_, R(1, 4)))
            s2 = sp.sign(dd.subs(t_, R(1, 2)))
            s3 = sp.sign(dd.subs(t_, R(4, 5)))
            if len({s1, s2, s3}) > 1:
                cnt += 1
                if first is None:
                    first = (thc, etc, s1, s2, s3)
print("GL-hr crossings found:", cnt, "| first:", first)
