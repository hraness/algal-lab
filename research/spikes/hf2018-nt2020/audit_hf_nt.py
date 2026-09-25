"""Audit of HF2018 (Hazra-Finkelstein, TEST 27:988-1006) and NT2020
(Nadeb-Torabi, CSTM 51(10):3104-3119) ordering claims.

Full texts are closed-access; claims are reconstructed from:
 - SAF2022 Rem 6.6: Thm 6.5 "extends Theorem 3.2 in Nadeb and Torabi (2020)"
   -> NT-3.2: ordinary mixtures, common p, (p,lam),(p,gam) in U_n,
      Fbar(t|lam) dec+convex in lam, lam ~^w gam (lam weakly supermajorizes
      gam)  =>  sum p_i Fbar(t|lam_i) >= sum p_i Fbar(t|gam_i)  (st order).
   Ordinary mixture = SAF alpha-mixture at alpha_i = 1 (abar=1): (ii),(iv)
   vacuous beyond p dec, which U_n + lam inc already gives.
 - SAF2022 Cor 6.21: "extends Theorem 4.2 in Nadeb and Torabi (2020)"
   -> NT-4.2: PH family Fbar^lam, n=2, p1>=p2, (p,lam),(p,gam) in U2,
      lam ~^m gam  =>  h(p,lam) <= h(p,gam)  (hr order, Schur-concavity).
      n>2 left open by NT (SAF Rem 6.18) -- we test n=3 too.
 - SKF2026 Thms 3.9/3.12 proofs "follow from Theorem 3.4 of Hazra and
   Finkelstein (2018)" -> HF-3.4: T-transform chains with DIFFERENT
   structures, intermediates in V_n/W_n, imply hr (and rh) ordering of
   ordinary mixtures.  HF's own statement applies to ordinary mixtures
   (alpha=1); we test the PH-family version
        htilde_{p,lam}(u) = sum p_i lam_i u^{lam_i} / sum p_i u^{lam_i},
   u in (0,1), exactly, plus the rh analog for the PRH family
        rtilde_{p,lam}(x) = sum p_i lam_i x^{lam_i} / (x sum p_i x^{lam_i})
   (x = F(t); only the bracket matters for signs).
   Also the single-T (same-structure) analogs, n=2,3,4.

All arithmetic exact rational (sympy); sign changes certified by Sturm
count_roots on the numerator polynomial.
"""
import sys, random, itertools
sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/mixture-audit")
import sympy as sp
from audit_lib import (R, weak_super, weak_sub, majorizes, inc_order, dec_order,
                       in_Un, in_Vn, in_Wn)

s = sp.Symbol("s", positive=True)
GRID = [R(1, 32), R(1, 16), R(1, 8), R(1, 4), R(2, 5), R(1, 2),
        R(3, 4), R(7, 8), R(15, 16), R(31, 32)]


def report(vals, expected, tie_ok=True):
    signs = {sg for _, sg in vals} - {0}
    if not signs:
        return "ok" if tie_ok else "ok-zero"
    if len(signs) > 1:
        return "crossing"
    return "ok" if signs.pop() == expected else "violation"


def htilde(p, lam, u):
    """PH-mixture hazard shape factor: sum p_i lam_i u^lam_i / sum p_i u^lam_i."""
    num = sum(pi * li * u ** int(li) for pi, li in zip(p, lam))
    den = sum(pi * u ** int(li) for pi, li in zip(p, lam))
    return sp.cancel(num / den)


def rtilde(p, lam, x):
    """PRH-mixture reversed-hazard shape factor (times x): sum p_i lam_i x^lam_i / sum p_i x^lam_i.

    r_mix(t) = r_F(t) * sum p_i lam_i F^{lam_i}/(F sum p_i F^{lam_i}).
    Sign of (r_mix-r'_mix)/r_F equals sign of bracket diff times 1/x>0.
    """
    num = sum(pi * li * x ** int(li) for pi, li in zip(p, lam))
    den = sum(pi * x ** int(li) for pi, li in zip(p, lam))
    return sp.cancel(num / den)   # bracket = this / x ; x>0 so compare num/den


def ttransform(mat2, i, j, om):
    """Apply T-transform with parameter om to columns i,j of 2 x n matrix.
    mat2 = [row1, row2] as lists of rationals. Returns new matrix."""
    a = [list(r) for r in mat2]
    for r in range(2):
        ai, aj = a[r][i], a[r][j]
        a[r][i] = om * ai + (1 - om) * aj
        a[r][j] = (1 - om) * ai + om * aj
    return a


# ==========================================================================
# CLAIM NT-3.2 (transmitted): st order under weak supermajorization.
#   p dec, lam,gam inc, (p,lam),(p,gam) in U_n, lam ~^w gam
#   (inc partial sums of lam <= gam's), Fbar dec+convex in lam.
#   Claim: sum p_i s^{lam_i} >= sum p_i s^{gam_i} on (0,1), exp baseline.
# ==========================================================================
def audit_nt32(trials=6000, seed=7):
    rng = random.Random(seed)
    res = [0, 0]; ex = None
    for _ in range(trials):
        n = rng.choice([2, 3, 4])
        p = tuple(sorted((R(rng.randint(1, 40), 40) for _ in range(n)),
                         reverse=True))
        tot = sum(p); p = tuple(pi / tot for pi in p)
        lam = tuple(sorted(rng.randint(1, 9) for _ in range(n)))
        gam = tuple(sorted(rng.randint(1, 10) for _ in range(n)))
        if not (in_Un(list(p), list(lam)) and in_Un(list(p), list(gam))):
            continue
        if not weak_super(list(gam), list(lam)) or lam == gam:
            continue
        d = sp.expand(sum(p[i] * s ** lam[i] for i in range(n))
                      - sum(p[i] * s ** gam[i] for i in range(n)))
        vals = [(v, sp.sign(d.subs(s, v))) for v in GRID]
        res[0] += 1
        if report(vals, +1) != "ok":
            res[1] += 1
            ex = ex or (p, lam, gam, vals, d)
    return res, ex


# ==========================================================================
# CLAIM NT-4.2 (transmitted): hr order, PH family, MAJORIZATION.
#   n=2: p1>=p2, lam inc, gam inc, lam ~^m gam => htilde(p,lam) <= htilde(p,gam).
#   n>2: left open by NT2020/HF2018 (SAF Rem 6.18); we test it.
# ==========================================================================
def audit_nt42(n_fixed=2, trials=6000, seed=11):
    rng = random.Random(seed)
    res = [0, 0]; ex = None
    for _ in range(trials):
        n = n_fixed
        p = tuple(sorted((R(rng.randint(1, 40), 40) for _ in range(n)),
                         reverse=True))
        tot = sum(p); p = tuple(pi / tot for pi in p)
        lam = tuple(sorted(rng.randint(1, 9) for _ in range(n)))
        gam = tuple(sorted(rng.randint(1, 9) for _ in range(n)))
        if not (in_Un(list(p), list(lam)) and in_Un(list(p), list(gam))):
            continue
        if not majorizes(list(lam), list(gam)) or lam == gam:
            continue
        d = sp.cancel(sp.together(htilde(p, lam, s) - htilde(p, gam, s)))
        vals = [(v, sp.sign(d.subs(s, v))) for v in GRID]
        res[0] += 1
        if report(vals, -1) != "ok":   # claim h_lam <= h_gam
            res[1] += 1
            ex = ex or (p, lam, gam, vals, d)
    return res, ex


# ==========================================================================
# CLAIM HF-T (transmitted via SKF, HF Thm 3.4 pattern): T-transform chains.
#   PH family. [p;lam] in V_n (or W_n); single T or chains; claim
#   htilde_p,lam >= htilde_q,gam on u in (0,1)  for V_n  (<= for W_n).
#   V_n: rows antiordered (p_i-p_j)(l_i-l_j)<=0; W_n: comonotone.
# ==========================================================================
def audit_hf_single_T(cls="V", trials=8000, seed=13):
    rng = random.Random(seed)
    res = [0, 0]; ex = None
    for _ in range(trials):
        n = rng.choice([2, 3, 4])
        p = tuple(R(rng.randint(1, 40), 40) for _ in range(n))
        tot = sum(p); p = tuple(pi / tot for pi in p)
        lam = tuple(rng.randint(1, 9) for _ in range(n))
        ok = in_Vn(list(p), list(lam)) if cls == "V" else in_Wn(list(p), list(lam))
        if not ok:
            continue
        i, j = sorted(rng.sample(range(n), 2))
        om = R(rng.randint(1, 19), 20)
        qg = ttransform([list(p), list(lam)], i, j, om)
        q, gam = qg[0], qg[1]
        d = sp.cancel(sp.together(htilde(p, lam, s) - htilde(q, gam, s)))
        vals = [(v, sp.sign(d.subs(s, v))) for v in GRID]
        res[0] += 1
        # V: claim U >=hr V i.e. htilde_p >= htilde_q -> d >= 0. W: <= -> d<=0.
        exp_sign = +1 if cls == "V" else -1
        if report(vals, exp_sign) != "ok":
            res[1] += 1
            ex = ex or (cls, n, p, lam, q, gam, i, j, om, vals, d)
    return res, ex


def audit_hf_chain(cls="V", k=2, trials=8000, seed=17):
    """Different-structure T-chains with ALL intermediates in cls."""
    rng = random.Random(seed)
    res = [0, 0]; ex = None
    for _ in range(trials):
        n = rng.choice([3, 4])
        p = tuple(R(rng.randint(1, 40), 40) for _ in range(n))
        tot = sum(p); p = tuple(pi / tot for pi in p)
        lam = tuple(rng.randint(1, 9) for _ in range(n))
        chk = in_Vn if cls == "V" else in_Wn
        if not chk(list(p), list(lam)):
            continue
        cur = [list(p), list(lam)]
        pairs = rng.sample(list(itertools.combinations(range(n), 2)), k)
        chain = []
        good = True
        for (i, j) in pairs:
            om = R(rng.randint(1, 19), 20)
            cur = ttransform(cur, i, j, om)
            chain.append((i, j, om))
            if not chk(list(cur[0]), list(cur[1])):
                good = False
                break
        if not good:
            continue
        q, gam = cur[0], cur[1]
        d = sp.cancel(sp.together(htilde(p, lam, s) - htilde(q, gam, s)))
        vals = [(v, sp.sign(d.subs(s, v))) for v in GRID]
        res[0] += 1
        exp_sign = +1 if cls == "V" else -1
        if report(vals, exp_sign) != "ok":
            res[1] += 1
            ex = ex or (cls, n, p, lam, q, gam, chain, vals, d)
    return res, ex


# rh analog (PRH family): claim for V_n: rtilde_p <= rtilde_q (U <=rh V);
# for W_n: >=.
def audit_hf_rh(cls="V", trials=8000, seed=19):
    rng = random.Random(seed)
    res = [0, 0]; ex = None
    x = s
    for _ in range(trials):
        n = rng.choice([3, 4])
        p = tuple(R(rng.randint(1, 40), 40) for _ in range(n))
        tot = sum(p); p = tuple(pi / tot for pi in p)
        lam = tuple(rng.randint(1, 9) for _ in range(n))
        chk = in_Vn if cls == "V" else in_Wn
        if not chk(list(p), list(lam)):
            continue
        i, j = sorted(rng.sample(range(n), 2))
        om = R(rng.randint(1, 19), 20)
        qg = ttransform([list(p), list(lam)], i, j, om)
        q, gam = qg[0], qg[1]
        d = sp.cancel(sp.together(rtilde(p, lam, x) - rtilde(q, gam, x)))
        vals = [(v, sp.sign(d.subs(x, v))) for v in GRID]
        res[0] += 1
        exp_sign = -1 if cls == "V" else +1   # V: r_p <= r_q ; W: r_p >= r_q
        if report(vals, exp_sign) != "ok":
            res[1] += 1
            ex = ex or (cls, n, p, lam, q, gam, i, j, om, vals, d)
    return res, ex


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "nt32"):
        r, e = audit_nt32()
        print("NT-3.2 st weak-supermaj:", r, "ex:", e[:4] if e else None)
    if which in ("all", "nt42"):
        for n in (2, 3, 4):
            r, e = audit_nt42(n_fixed=n, trials=5000, seed=11 + n)
            print(f"NT-4.2 hr majorization n={n}:", r, "ex:", e[:4] if e else None)
    if which in ("all", "hfsingle"):
        for cls in ("V", "W"):
            r, e = audit_hf_single_T(cls)
            print(f"HF single-T hr cls={cls}:", r,
                  "ex:", e[:8] if e else None)
    if which in ("all", "hfchain"):
        for cls in ("V", "W"):
            r, e = audit_hf_chain(cls, k=2)
            print(f"HF chain k=2 hr cls={cls}:", r,
                  "ex:", e[:7] if e else None)
    if which in ("all", "hfrh"):
        for cls in ("V", "W"):
            r, e = audit_hf_rh(cls)
            print(f"HF single-T rh cls={cls}:", r,
                  "ex:", e[:8] if e else None)
