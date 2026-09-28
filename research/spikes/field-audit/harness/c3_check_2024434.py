"""Independent check: doi:10.3934/math.2024434 Corollaries 2 & 3.

MPHRS marginal survival: S_i(x) = a_i Fbar(x th_i)^{la_i}
                                  /(1-(1-a_i) Fbar(x th_i)^{la_i}).
MPRHRS marginal cdf:       H_i(x) = a_i F(x th_i)^{be_i}
                                  /(1-(1-a_i) F(x th_i)^{be_i}).
Independent (product copula) 2nd order stat:
  S_{2:n} = sum_i prod_{j!=i} S_j - (n-1) prod_j S_j.
(n-1)th of n (second largest) cdf:
  F_{n-1:n} = sum_i prod_{j!=i} H_j - (n-1) prod_j H_j.
Cor 2: X2:n <=st Y2:n under theta >= mean(theta_i), Fbar1<=Fbar2.
Cor 3: X_{n-1:n} >=st Y_{n-1:n} under lambda >= mean(lambda_i), F1<=F2.
"""
import mpmath as mp
mp.mp.dps = 110


def S_mphrs(t, a, th, la, Fb):
    v = Fb(mp.mpf(t) * mp.mpf(th)) ** mp.mpf(la)
    a = mp.mpf(a)
    return a * v / (1 - (1 - a) * v)


def H_mprhrs(t, a, th, be, F):
    v = F(mp.mpf(t) * mp.mpf(th)) ** mp.mpf(be)
    a = mp.mpf(a)
    return a * v / (1 - (1 - a) * v)


def S2(pars, t, Fb):
    S = [S_mphrs(t, *p, Fb) for p in pars]
    n = len(S)
    tot = mp.mpf(0)
    for i in range(n):
        tot += mp.fprod(S[j] for j in range(n) if j != i)
    return tot - (n - 1) * mp.fprod(S)


def Snm1(pars, t, F):
    H = [H_mprhrs(t, *p, F) for p in pars]
    n = len(H)
    tot = mp.mpf(0)
    for i in range(n):
        tot += mp.fprod(H[j] for j in range(n) if j != i)
    Fnm1 = tot - (n - 1) * mp.fprod(H)
    return 1 - Fnm1


EXP = lambda k: (lambda y: mp.e ** (-k * y))

print("===== Corollary 2: theta >= mean(theta) => X2:n <=st Y2:n =====")
for th, t0 in [([mp.mpf('0.6'), mp.mpf('0.7'), mp.mpf('0.8'), mp.mpf('0.9')], mp.mpf('1')),
               ([mp.mpf('0.2'), mp.mpf('0.4'), mp.mpf('0.6')], mp.mpf('1'))]:
    n = len(th); a = mp.mpf('1') / 3; la = mp.mpf('1')
    print("premise theta>=mean:", mp.nstr(t0, 5), ">=", mp.nstr(sum(th) / n, 5),
          "->", t0 >= sum(th) / n, "| Fbar1=e^-3x <= e^-2x=Fbar2: True")
    X = [(a, t, la) for t in th]
    Y = [(a, t0, la)] * n
    neg = []
    for i in range(1, 400):
        t = mp.mpf('30') * i / 400
        d = S2(X, t, EXP(3)) - S2(Y, t, EXP(2))
        if d > mp.mpf('1e-70'):
            neg.append((t, d))
    print("   X<=stY (SX<=SY):", "VIOLATED" if neg else "holds",
          [(mp.nstr(t, 5), mp.nstr(d, 8)) for t, d in neg[:2]], len(neg))
    t0v = mp.mpf('1e-12')
    print("   witness ~0: SX-SY =", mp.nstr(S2(X, t0v, EXP(3)) - S2(Y, t0v, EXP(2)), 12))
    # also opposite direction sanity
    neg2 = []
    for i in range(1, 400):
        t = mp.mpf('30') * i / 400
        d = S2(Y, t, EXP(2)) - S2(X, t, EXP(3))
        if d > mp.mpf('1e-70'):
            neg2.append((t, d))
    print("   opposite Y<=stX:", "VIOLATED" if neg2 else "holds", len(neg2))

print("===== Corollary 3: lambda >= mean(lambda) => X_{n-1:n} >=st Y =====")
for lv, l0 in [([mp.mpf('2'), mp.mpf('3'), mp.mpf('4')], mp.mpf('4')),
               ([mp.mpf('0.5'), mp.mpf('1'), mp.mpf('1.5')], mp.mpf('2')),
               ([mp.mpf('1'), mp.mpf('2'), mp.mpf('3'), mp.mpf('4')], mp.mpf('5'))]:
    n = len(lv); a = mp.mpf('0.5'); th = mp.mpf('1')
    print("premise lambda>=mean:", mp.nstr(l0, 5), ">=", mp.nstr(sum(lv) / n, 5),
          "->", l0 >= sum(lv) / n, "| F1=1-e^{-x/2} <= F2=1-e^{-x}: True")
    F1 = lambda y: 1 - mp.e ** (-y / 2)
    F2 = lambda y: 1 - mp.e ** (-y)
    X = [(a, th, l) for l in lv]
    Y = [(a, th, l0)] * n
    neg = []
    for i in range(1, 400):
        t = mp.mpf('40') * i / 400
        d = Snm1(X, t, F1) - Snm1(Y, t, F2)
        if d < -mp.mpf('1e-60'):
            neg.append((t, d))
    print("   X>=stY (SX>=SY):", "VIOLATED" if neg else "holds",
          [(mp.nstr(t, 5), mp.nstr(d, 8)) for t, d in neg[:2]], len(neg))
    t0v = mp.mpf('1e-12')
    print("   witness ~0: SX-SY =", mp.nstr(Snm1(X, t0v, F1) - Snm1(Y, t0v, F2), 12))
