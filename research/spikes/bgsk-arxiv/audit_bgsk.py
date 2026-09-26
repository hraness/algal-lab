"""Audit of arXiv:2511.00791 (Bhakta-Gupta-Saadat Kia-Kayal), ELS mixtures.

Model: component CDF F_i(x) = F((x-s_i)/l_i)^{a_i} on x > s_i + c l_i.
Mixture RV U_n(r,a,s,l): CDF = sum_i r_i F_i(x).

Sec 4 (multiple-outlier): U_n has n1 comps of type 1 (a1,s1,l1) at weight r1
each, n2 comps type 2 at r2, n1 r1 + n2 r2 = 1; U_n* analogous with s1,s2.

Thm 4.2 claim (lr): under a,l,s in E_2^+, alpha_i>=1, t*h~(t) and t*f'/f
decreasing, and n1 r1 n2* s2 <= n2 r2 n1* s1:  U_n >=_lr U_n*, i.e.
zeta(x) = f_U(x)/f_U*(x) increasing for x > s1 + c l1.

CERTIFIED COUNTEREXAMPLE below: Pareto k=1 baseline (c=1),
F(t)=1-1/t, f=1/t^2, h~=1/(t(t-1)), t h~=1/(t-1) decreasing on t>1,
t f'/f = -2 constant (weakly decreasing) -- all hypotheses satisfied,
but zeta decreases on (4, infty).
"""
import sympy as sp
from fractions import Fraction
import random

x = sp.Symbol('x', positive=True)
R = sp.Rational


def pareto_cdf(k):
    """F(t) = 1 - t^{-k}, t >= 1 (c = 1)."""
    t = sp.Symbol('t', positive=True)
    return 1 - t**(-k)


# ---------------------------------------------------------------- Thm 4.2
def thm42_counterexample():
    """Exact certification. Returns dict."""
    Fk, fk = pareto_cdf(1), None
    t = sp.Symbol('t', positive=True)
    f = sp.diff(1 - 1/t, t)  # 1/t^2
    # instance
    sig = (R(0), R(1)); lam = (R(1), R(1)); al = (R(1), R(2))
    n1, n2, ns1, ns2 = 1, 2, 2, 1
    r1, r2 = R(1, 2), R(1, 4)
    s1, s2 = R(2, 5), R(1, 5)
    assert n1*r1 + n2*r2 == 1 and ns1*s1 + ns2*s2 == 1
    hyp = dict(
        E_alpha=(al[0] <= al[1]), E_lam=(lam[0] <= lam[1]),
        E_sig=(sig[0] <= sig[1]), alpha_ge_1=(al[0] >= 1 and al[1] >= 1),
        weight_ineq=(n1*r1*ns2*s2 <= n2*r2*ns1*s1),
    )
    u1 = (x - sig[0])/lam[0]
    u2 = (x - sig[1])/lam[1]
    F = lambda u: 1 - 1/u
    f_ = lambda u: 1/u**2
    phi = sp.cancel((al[0]/lam[0]) * F(u1)**(al[0]-1) * f_(u1) /
                    ((al[1]/lam[1]) * F(u2)**(al[1]-1) * f_(u2)))
    # zeta on x > sig2 + c lam2 = 2
    zeta = sp.cancel((n1*r1*phi + n2*r2)/(ns1*s1*phi + ns2*s2))
    zp = sp.cancel(sp.diff(zeta, x))
    num, den = sp.fraction(zp)
    num, den = sp.expand(num), sp.expand(den)
    pnum = sp.Poly(num, x)
    # roots on (2, oo): only x=4 ; sign: + on (2,4), - on (4,oo)
    cert = {
        "zeta'": zp,
        "num": num, "den": den,
        "roots_num_(2,oo)": pnum.count_roots(2, sp.oo),   # the x=4 root
        "roots_num_(2,4)": pnum.count_roots(2, 4),
        "roots_num_(4,oo)_open": pnum.count_roots(4, sp.oo),
        "den_roots_(2,oo)": sp.Poly(den, x).count_roots(2, sp.oo),
        "zeta(4)": zeta.subs(x, 4), "zeta(5)": zeta.subs(x, 5),
        "zeta(10)": zeta.subs(x, 10),
        "sign_num_at_3": sp.sign(num.subs(x, 3)),
        "sign_num_at_5": sp.sign(num.subs(x, 5)),
        "witness_dec": (zeta.subs(x, 4) > zeta.subs(x, 5)),
    }
    return hyp, cert


# ---------------------------------------------------------------- Thm 4.1
def rh_two_type(xv, n, r, p):
    """h~ of 2-type mixture at x: sum n_i r_i (a_i/l_i) F^{a_i-1} f / sum n_i r_i F^{a_i}.
    p = (a1,a2,s1,s2,l1,l2,c,baseline F,f). xv rational. Piecewise by support."""
    a1, a2, s1, s2, l1, l2, c, F, f = p
    u1 = (xv - s1)/l1; u2 = (xv - s2)/l2
    n1, n2 = n; r1, r2 = r
    num = den = 0
    if xv > s1 + c*l1:
        num += n1*r1*(a1/l1)*F(u1)**(a1-1)*f(u1)
        den += n1*r1*F(u1)**a1
    if xv > s2 + c*l2:
        num += n2*r2*(a2/l2)*F(u2)**(a2-1)*f(u2)
        den += n2*r2*F(u2)**a2
    return num/den if den != 0 else sp.nan


def thm41_search(trials=400, seed=1):
    """Thm 4.1: n1r1n2*s2 >= n2r2n1*s1 (+ E ordering) => h~_U <= h~_U*.
    Pareto k=1 (t h~ decreasing). Random admissible instances, rational grid."""
    rng = random.Random(seed)
    F = lambda u: 1 - 1/u
    f = lambda u: 1/u**2
    admissible = 0; violations = []
    for _ in range(trials):
        a1 = R(rng.randint(1, 4)); a2 = a1 + R(rng.randint(0, 3))  # a in E
        s1 = R(rng.randint(0, 3)); s2 = s1 + R(rng.randint(0, 3))
        l1 = R(rng.randint(1, 4)); l2 = l1 + R(rng.randint(0, 3))
        n1, n2, ns1, ns2 = [rng.randint(1, 6) for _ in range(4)]
        # weights r1,r2>0, n1 r1 + n2 r2 = 1
        r1 = R(1, rng.randint(1, 8)); r2 = (1 - n1*r1)/n2
        s1_ = R(1, rng.randint(1, 8)); s2_ = (1 - ns1*s1_)/ns2
        if r2 <= 0 or s2_ <= 0:
            continue
        if not (n1*r1*ns2*s2_ >= n2*r2*ns1*s1_):
            continue
        admissible += 1
        p = (a1, a2, s1, s2, l1, l2, R(1), F, f)
        lo = s1 + l1  # x > s1 + c l1
        ok = True
        for k in range(1, 40):
            xv = lo + R(k, 7)
            hU = rh_two_type(xv, (n1, n2), (r1, r2), p)
            hV = rh_two_type(xv, (ns1, ns2), (s1_, s2_), p)
            if hU > hV:
                ok = False
                violations.append((xv, hU, hV, (n1, n2, ns1, ns2),
                                  (r1, r2, s1_, s2_), (a1, a2, s1, s2, l1, l2)))
                break
        if not ok:
            pass
    return admissible, violations


# ---------------------------------------------------------------- Thm 4.3
def lomax_params(k):
    """F(t)=1-(1+t)^{-k}, t>=0 (c=0); f'/f = -(k+1)/(1+t) increasing;
    t h~ decreasing (verified numerically in memo)."""
    F = lambda u: 1 - (1+u)**(-k)
    f = lambda u: k*(1+u)**(-k-1)
    return F, f


def thm43_lambda(xv, n, r, lam, s_loc, al, F, f):
    """h~_U at xv for common alpha, sigma; U uses (lam_i, sigma)."""
    n1, n2 = n; r1, r2 = r
    l1, l2 = lam
    u1 = (xv - s_loc)/l1; u2 = (xv - s_loc)/l2
    num = (n1*r1*(al/l1)*F(u1)**(al-1)*f(u1)
           + n2*r2*(al/l2)*F(u2)**(al-1)*f(u2))
    den = n1*r1*F(u1)**al + n2*r2*F(u2)**al
    return sp.cancel(num/den)


def thm43_search(k=1):
    """Claim: Lam(x) = h~_U/h~_V decreasing for x > max(sigma,mu).
    Sigma >= mu, min lam >= max theta, alpha in (0,1], c=0.
    Lomax k integer, alpha=1 -> rational in x."""
    F, f = lomax_params(k)
    hits = []
    # deterministic sweep of admissible instances
    for sig in [R(2), R(5), R(8), R(12)]:
        for mu in [R(0), R(1)]:
            if mu > sig:
                continue
            for l1 in [R(1), R(2), R(3)]:
                for l2 in [R(1), R(2), R(3), R(5)]:
                    for t1 in [R(1), R(2)]:
                        for t2 in [R(1), R(2)]:
                            if min(l1, l2) < max(t1, t2):
                                continue
                            n = (2, 3); ns = (3, 2)
                            r = (R(1, 4), R(1, 6))
                            assert n[0]*r[0] + n[1]*r[1] == 1
                            s_ = (R(1, 6), R(1, 4))
                            assert ns[0]*s_[0] + ns[1]*s_[1] == 1
                            hU = thm43_lambda(x, n, r, (l1, l2), sig, R(1), F, f)
                            hV = thm43_lambda(x, ns, s_, (t1, t2), mu, R(1), F, f)
                            Lam = sp.cancel(hU/hV)
                            Lp = sp.cancel(sp.diff(Lam, x))
                            num, den = sp.fraction(Lp)
                            s5 = sp.sign(num.subs(x, sig + 10))
                            s20 = sp.sign(num.subs(x, sig + 40))
                            if s5 > 0 or s20 > 0:
                                hits.append((sig, mu, l1, l2, t1, t2,
                                             s5, s20, sp.factor(num)))
    return hits


if __name__ == "__main__":
    print("=== Thm 4.2 certificate ===")
    hyp, cert = thm42_counterexample()
    print("hypotheses:", hyp)
    for kk, vv in cert.items():
        print(f"  {kk}: {vv}")
    print("\n=== Thm 4.1 admissible scan (Pareto k=1) ===")
    adm, viol = thm41_search()
    print(f"admissible={adm}, violations={len(viol)}")
    for v in viol[:5]:
        print("  ", v)
    print("\n=== Thm 4.3 sweep (Lomax k=1, alpha=1) ===")
    hits = thm43_search(1)
    print(f"sign-positive Lam' hits: {len(hits)}")
    for h in hits[:8]:
        print("  ", h)
