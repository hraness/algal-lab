"""Audit of VKF2025 claims as reconstructed from SKF2026's citations.

[VKF2025] Varghese, A.A., K., A.M., Sarkar, S., Ghosh, S., Majumder, P. (2025),
"On stochastic comparisons of alpha-mixture models with location-scale family
of distributions", Statistics 59(5):1278-1300, DOI 10.1080/02331888.2025.2502946.
Paywalled; no OA/AM copy found (unpaywall closed; no Strathprints/arXiv/RG).
Statements below are reconstructed from SKF2026 (Strathprints 96227), which
cites VKF theorems by number:

  SKF Rem 3.4 (after Thm 3.4): "When alpha >= gamma_1, the result is similar
      to Theorem 3.1(i) of Varghese et al. (2025)."
  SKF before Thm 3.4: Thm 3.4 "can be treated as an improved version of the
      result in Theorem 3.1(ii) of Varghese et al. (2025) since it holds for
      a wider range of the parameter alpha. The range of alpha includes
      non-positive values."
  SKF before Thm 3.6: "The similar setup has been considered by Varghese et
      al. (2025) in their result, for example Theorem 3.10. However, their
      sufficient conditions do not match with the conditions proposed in the
      following result. Mainly, we have proved it when alpha is non-positive."

=> Reconstructed claims (in the common scale-family frame; a location-scale
family contains the pure scale family as the mu=0 subfamily, so failures here
refute any claim covering scale-only components):

  R1 [VKF Thm 3.1(i)]:  t^2 g(t) increasing; p in E+ (or D+); theta, xi in
      D+ (or E+); theta <^w xi; alpha >= gamma (scalar gamma>0)
      => U_n >=st V_n  (i.e. inner_U - inner_V >= 0 since alpha > 0).
  R2 [VKF Thm 3.1(ii)]: same claim for 0 < alpha < gamma.
      (SKF's own audit refutes SKF Thm 3.4's alpha>0 branch; the certified
      instance p=(1/3,2/3), gamma=3, alpha=2/3, theta=(3,1), xi=(7/2,1/2),
      Lomax baseline has 0 < alpha < gamma -> refutes R2 directly.)
  R3 [VKF Thm 3.10]:   two-parameter heterogeneity (p vs q, theta vs xi,
      scalar gamma) for alpha > 0.  SKF 3.6 proves the alpha <= 0 version
      with p <_w q, theta <^w xi.  VKF's alpha>0 analog is tested with both
      p <_w q and p <^w q orientations (weak-order direction not recoverable
      from the citation).

Model: inner(t) = sum_i p_i Gbar(t/theta_i)^{alpha*gamma}, S = inner^{1/alpha},
alpha>0 => sign(S_U - S_V) = sign(inner_U - inner_V).
Baselines with t^2 g increasing: Lomax Gbar=1/(1+t) (t>0);
power-law Gbar = 1 - t^2 on 0<t<1 (t^2 g = 2t^3/(1-t^2)*?? check: g=2t,
t^2 g = 2 t^3 increasing on (0,1) -- yes).
"""
import sys
import random
import sympy as sp
from audit_lib import R, weak_super, weak_sub, p_larger

t_ = sp.Symbol("t", positive=True)
GRID_POS = [R(1, 4), R(1, 2), R(1), R(2), R(3), R(5), R(8), R(15)]
GRID_01 = [R(1, 8), R(1, 4), R(1, 2), R(3, 4), R(7, 8), R(15, 16)]


def inner_lomax(p, theta, ag):
    return sum(p[i] * (R(theta[i]) / (R(theta[i]) + t_)) ** int(ag)
               for i in range(len(p)))


def inner_power2(p, theta, ag):
    """Gbar(t/theta) = 1-(t/theta)^2, valid t < min theta."""
    return sum(p[i] * (1 - (t_ / R(theta[i])) ** 2) ** int(ag)
               for i in range(len(p)))


def rand_sorted_prob(rng, n, dec=False):
    p = [R(rng.randint(1, 40), 40) for _ in range(n)]
    tot = sum(p)
    p = [pi / tot for pi in p]
    return tuple(sorted(p, reverse=dec))


def rand_sorted_ints(rng, n, lo, hi, dec=True):
    return tuple(sorted((rng.randint(lo, hi) for _ in range(n)), reverse=dec))


def scan(d, grid):
    vals = [(v, sp.sign(d.subs(t_, v))) for v in grid]
    return vals, {sg for _, sg in vals} - {0}


def certify(d):
    """Sturm count on (0,1) and isolating intervals for the numerator."""
    num, den = sp.fraction(sp.cancel(sp.together(d)))
    num, den = sp.expand(num), sp.expand(den)
    nr = sp.Poly(num, t_).count_roots(0, 1) if num != 0 else 0
    dr = sp.Poly(den, t_).count_roots(0, 1) if den.has(t_) else 0
    return nr, dr, num, den


# ==========================================================================
# R1: alpha >= gamma branch of the scale-vector st-order claim (VKF 3.1(i))
# ==========================================================================
def audit_R1(trials=4000, seed=5):
    rng = random.Random(seed)
    res = {}
    ex = {}
    for _ in range(trials):
        n = rng.choice([2, 3, 3, 4])
        for pdir, tdir in (("inc", "dec"), ("dec", "inc")):
            p = rand_sorted_prob(rng, n, dec=(pdir == "dec"))
            # gamma scalar > 0; alpha >= gamma.  gamma < 1 allowed:
            # gamma in {1/2,1,2,3,4,6}, alpha in {gamma, gamma+..., bigger}
            gam = rng.choice([R(1, 2), R(1), R(2), R(3), R(5)])
            cands = [gam, gam + R(1, 2), 2 * gam, gam + 3, R(2), R(4)]
            cands = [a for a in cands if a >= gam and (a * gam).denominator == 1]
            if not cands:
                continue
            alpha = rng.choice(cands)
            ag = alpha * gam  # integer by construction; alpha >= gamma
            theta = rand_sorted_ints(rng, n, 1, 9, dec=(tdir == "dec"))
            xi = rand_sorted_ints(rng, n, 1, 9, dec=(tdir == "dec"))
            if not weak_super(list(theta), list(xi)) or theta == xi:
                continue
            for base in ("lomax", "power2"):
                fn = inner_lomax if base == "lomax" else inner_power2
                grid = GRID_POS if base == "lomax" else [g for g in GRID_01]
                if base == "power2" and min(min(theta), min(xi)) <= 1:
                    continue
                d = sp.cancel(sp.together(fn(list(p), list(theta), ag)
                                          - fn(list(p), list(xi), ag)))
                vals, signs = scan(d, grid)
                key = (n, pdir, tdir, base, "ag>1" if ag > 1 else "ag<=1")
                res.setdefault(key, [0, 0])
                res[key][0] += 1
                if len(signs) > 1 or (signs and signs.pop() != 1):
                    res[key][1] += 1
                    ex.setdefault(key, (p, gam, alpha, theta, xi, vals))
    return res, ex


# ==========================================================================
# R3: two-parameter heterogeneity, alpha > 0 (VKF 3.10 reconstruction).
#   Both p-weak-order orientations tested.
# ==========================================================================
def audit_R3(trials=4000, seed=9):
    rng = random.Random(seed)
    res = {"p_sub": [0, 0], "p_super": [0, 0]}
    ex = {"p_sub": None, "p_super": None}
    for _ in range(trials):
        n = 3
        p = rand_sorted_prob(rng, n)          # increasing
        q = rand_sorted_prob(rng, n)
        theta = rand_sorted_ints(rng, n, 1, 9)   # decreasing
        xi = rand_sorted_ints(rng, n, 1, 9)
        gam = rng.choice([R(1, 2), R(1), R(2), R(3)])
        cands = [gam, gam + 1, 2 * gam, R(1, 2), R(1), R(2)]
        cands = [a for a in cands if (a * gam).denominator == 1]
        alpha = rng.choice(cands)
        ag = alpha * gam
        if ag <= 0:
            continue
        if not weak_super(list(theta), list(xi)) or theta == xi:
            continue
        du = inner_lomax(list(p), list(theta), ag)
        dv = inner_lomax(list(q), list(xi), ag)
        d = sp.cancel(sp.together(du - dv))
        vals, signs = scan(d, GRID_POS)
        if weak_sub(list(p), list(q)):
            res["p_sub"][0] += 1
            if len(signs) > 1 or (signs and signs.pop() != 1):
                res["p_sub"][1] += 1
                ex["p_sub"] = ex["p_sub"] or (p, q, gam, alpha, theta, xi, vals)
        if weak_super(list(p), list(q)):
            res["p_super"][0] += 1
            if len(signs) > 1 or (signs and signs.pop() != 1):
                res["p_super"][1] += 1
                ex["p_super"] = ex["p_super"] or (p, q, gam, alpha, theta, xi, vals)
    return res, ex


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    tr = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
    if which in ("all", "r1"):
        res, ex = audit_R1(tr)
        print("== R1 (VKF 3.1(i) recon: alpha >= gamma, theta <^w xi) ==")
        for k in sorted(res, key=str):
            print(f"  {k}: admissible={res[k][0]} violations={res[k][1]}")
            if res[k][1] and k in ex:
                print(f"     ex: {ex[k]}")
        sys.stdout.flush()
    if which in ("all", "r3"):
        res, ex = audit_R3(tr)
        print("== R3 (VKF 3.10 recon: p,q + theta,xi, alpha>0) ==", res)
        for k, v in ex.items():
            if v: print("   ex", k, v)
