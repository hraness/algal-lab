"""C3 for arXiv:1704.03656 -- refuted system-ordering claims.

The scale/shape-ordering claims print the majorization relation in the
opposite direction from the true one (the journal version
doi:10.2991/jsta.2018.17.3.8 prints the opposite direction for the
corresponding claims, which holds).  For each printed claim we exhibit an
instance satisfying the printed hypotheses and an interval-certified point
where the order expression has the wrong sign.

  Corollary 3.10 / Theorem 3.9 (GE/ES series, st): lam=(2,3) ~^w lam*=(1,4)
     [alpha=1/2 branch] and lam=(1,2) ~_w lam*=(2,3) [alpha=2 branch].
     Printed directions fail; the opposite ordering holds pointwise.
  Corollary 3.8 / Theorem 3.7 (ES series, hr): alpha=(2,3) ~^w alpha*=(1,4):
     X1:n <=hr X*1:n fails exactly at z=1/2 (z=e^{-x}).
  Corollary 3.3 (Frechet parallel, rh): (i) lam=(1,2) ~_w lam*=(2,3), alpha=2:
     r~X < r~X* so Xn:n >=rh X*n:n fails; (ii) lam=(2,3) ~^w lam*=(1,4),
     alpha=1/2: r~X > r~X* so Xn:n <=rh X*n:n fails.
  Theorem 3.4 (Frechet location): mu ~_w mu* forces max mu* >= max mu; just
     right of x=max mu*, r~X* -> +infty while r~X stays bounded, so
     Xn:n >=rh X*n:n fails on the joint support.
  Theorem 3.1(ii) increasing-f: f=u^2, alpha=3, lam*=(1,2) ~_wf lam=(2,3):
     printed Xn:n >=rh X*n:n fails; r~X* > r~X.
  Theorem 3.5(i) hr branches: gamma=1/2 baseline lam=(2,3)~^w(1,4) and
     gamma=2 baseline lam=(1,2)~_w(2,3): printed directions fail.
  Theorem 3.6: scale st claim fails for G=Exp, f=u^2, lam=(2,4)~^wf(1,3).
"""
import sympy as sp
from mpmath import iv
import auditlib as A
import closedform as cf
from ratdist import Dist

z = A.z
x = A.x
e = A.e


def iv_at(E, pt, dps=90):
    iv.dps = dps
    return cf.iv_eval(E, sp.Rational(pt))


def ge_surv(alpha, lam):
    return 1 - (1 - e ** (-A.R(lam) * x)) ** A.R(alpha)


def series(lams, alpha):
    return sp.prod([ge_surv(alpha, l) for l in lams])


def fr_rh(mu, lams, a):
    F = sp.prod([e ** (-((x - A.R(mu)) / A.R(l)) ** (-A.R(a))) for l in lams])
    return sp.diff(F, x) / F


def gez(alpha, lam2):
    """GE survival in z=e^{-x/2}."""
    return sp.expand(1 - (1 - z ** lam2) ** alpha)


def main():
    print("== GE series st: Cor 3.10 / Thm 3.9 ==")
    for tag, alpha, lX, lY, rel in [
            ("dec branch alpha=1/2", A.R(1, 2), [2, 3], [1, 4], "X*<=stX i.e. S_X-S_X*>=0"),
            ]:
        E = series(lX, alpha) - series(lY, alpha)
        print(f"  {tag} lamX={lX} lam*={lY}, need E>=0 for X*<=st X:")
        for pt in ["1/1000", "1/2", "2"]:
            print(f"   x={pt}: {iv_at(E, pt)}")
    # alpha=2 branch, exact in z=e^{-x}
    S1 = sp.prod([1 - (1 - z ** (2 * l)) ** 2 for l in (1, 2)])
    S2 = sp.prod([1 - (1 - z ** (2 * l)) ** 2 for l in (2, 3)])
    E = sp.expand(S2 - S1)
    print("  inc branch alpha=2: S_X*-S_X =", sp.factor(E))
    print("   (>=0 iff X1:2 <=st X*1:2; evaluated signs at z=1/2, 3/4)")
    for v in [sp.Rational(1, 2), sp.Rational(3, 4)]:
        print(f"   z={v}: {sp.N(E.subs(z, v), 12)}")

    print("== ES series hr: Cor 3.8 / Thm 3.7, alpha=(2,3) vs (1,4), z=e^{-x} ==")
    X_ = Dist(sp.expand(sp.prod([1 - (1 - z) ** a for a in (2, 3)])), 0, 1, False)
    Y_ = Dist(sp.expand(sp.prod([1 - (1 - z) ** a for a in (1, 4)])), 0, 1, False)
    E = sp.together(X_.density() * Y_.survival - Y_.density() * X_.survival)
    print("  E_hr numerator:", sp.factor(E.as_numer_denom()[0]))
    h, w = A.test_rat("hr", X_, Y_)
    print(f"  holds: {h}, witness z={w}")

    print("== Frechet parallel rh: Cor 3.3 ==")
    for tag, lX, lY, a in [("(i) a=2", [1, 2], [2, 3], 2),
                           ("(ii) a=1/2", [2, 3], [1, 4], A.R(1, 2))]:
        rX, rY = fr_rh(0, lX, a), fr_rh(0, lY, a)
        print(f"  {tag} lam={lX} vs {lY}; r~X - r~Y:")
        for pt in ["1/2", "1", "3"]:
            print(f"   x={pt}: {iv_at(rX - rY, pt)}")

    print("== Frechet location rh: Thm 3.4 (boundary blowup) ==")
    mu, mus = [0, A.R(1, 3)], [A.R(1, 5), A.R(4, 5)]  # X locs, X* locs
    FX = sp.prod([e ** (-(x - A.R(m)) ** (-2)) for m in mu])   # X side cdf
    FY = sp.prod([e ** (-(x - A.R(m)) ** (-2)) for m in mus])  # X* side cdf
    # check rh(X*,X): E = f_X F_X* - f_X* F_X = F_X F_X* (r~X - r~*)
    E = sp.diff(FX, x) * FY - sp.diff(FY, x) * FX
    for eps in ["1/100", "1/1000", "1/10000"]:
        p = A.R(4, 5) + A.R(eps)
        v = iv_at(E, p, 200)
        print(f"   x={p}: {v}")

    print("== Thm 3.1(ii) increasing f=u^2, alpha=3 ==")
    rX, rY = fr_rh(0, [2, 3], 3), fr_rh(0, [1, 2], 3)
    print("  claim X* <=rh X needs r~X* <= r~X; r~X - r~X*:")
    for pt in ["1/4", "1", "3"]:
        print(f"   x={pt}: {iv_at(rX - rY, pt)}")

    print("== Thm 3.5(i) hr branches ==")
    for tag, g, lX, lY in [("dec gamma=1/2", A.R(1, 2), [2, 3], [1, 4]),
                           ("inc gamma=2", A.R(2), [1, 2], [2, 3])]:
        SX = sp.prod([e ** (-(A.R(l) * x) ** g) for l in lX])
        SY = sp.prod([e ** (-(A.R(l) * x) ** g) for l in lY])
        hX = -sp.diff(SX, x) / SX
        hY = -sp.diff(SY, x) / SY
        # dec branch claim X*<=hr X needs h_X*>=h_X; inc branch X<=hr X* needs
        # h_X>=h_X*
        need = "h_X*-h_X>=0" if "dec" in tag else "h_X-h_X*>=0"
        E = hY - hX if "dec" in tag else hX - hY
        print(f"  {tag}: need {need}")
        for pt in ["1/2", "1", "3"]:
            print(f"   x={pt}: {iv_at(E, pt)}")

    print("== Thm 3.6 scale st, f=u^2 ==")
    SX = sp.prod([e ** (-A.R(l) * x) for l in (2, 4)])
    SY = sp.prod([e ** (-A.R(l) * x) for l in (1, 3)])
    # claim Xn:n >=st X*n:n <=> F_X <= F_* ... for MAX: parallel cdf
    # here we use SERIES?  Thm 3.6 is on Xn:n: F_n:n = prod G(l x) =
    # prod(1-e^{-l x}); claim X>=st X* <=> F_X <= F_X*
    FX = sp.prod([1 - e ** (-A.R(l) * x) for l in (2, 4)])
    FY = sp.prod([1 - e ** (-A.R(l) * x) for l in (1, 3)])
    E = FY - FX  # >=0 iff X <=st X*; claim opposite
    print("  claim Xn:n >=st X* needs F_Y - F_X >=0 ... F_Y-F_X =")
    for pt in ["1/4", "1", "3"]:
        print(f"   x={pt}: {iv_at(FX - FY, pt)}")


if __name__ == "__main__":
    main()
