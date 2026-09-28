"""C3 for doi:10.6339/jds.202001(18)1.0001 Section 4.7 Case I.

Claim: theta1 < theta2 (common alpha, lambda, beta) => X <=lr Y (=>hr,st,rhr).
Refutation instance satisfying the printed hypotheses: alpha=2, theta1=1/2,
theta2=1, lambda=beta=1.  For alpha>1 the theta-ordering reverses: the
stochastic comparison already fails, so the lr/hr/rh claims fail as well.

Independent check with plain mpmath (not the closedform iv evaluator).
"""
from mpmath import mp, exp, log

mp.dps = 80


def G(y, a, th, lam, b):
    t = exp(-(lam / y) ** b)
    v = 1 - (1 - a) * t
    return a ** th * (1 - v ** th) / ((1 - a ** th) * v ** th)


def main():
    a, l, b = mp.mpf(2), mp.mpf(1), mp.mpf(1)
    t1, t2 = mp.mpf(1), mp.mpf(2)
    print("S_Y(x) - S_X(x) = G_X(x) - G_Y(x):")
    for y in [mp.mpf("0.1"), mp.mpf("0.5"), mp.mpf(1), mp.mpf(2)]:
        d = G(y, a, t1, l, b) - G(y, a, t2, l, b)
        print(f"  x={y}: {mp.nstr(d, 12)}")
    # S_Y - S_X < 0 at x=1/2 etc. => X not <=st Y => X not <=lr/hr/rh Y.
    d = G(mp.mpf("0.5"), a, t1, l, b) - G(mp.mpf("0.5"), a, t2, l, b)
    assert d < 0
    print("=> X not <=st Y at x=1/2, so the claimed lr/hr/rh orders fail too.")


if __name__ == "__main__":
    main()
