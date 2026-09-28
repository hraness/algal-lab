"""Independent verification: doi:10.66224/jss.20.1.06 (Persian SAH paper).

SAH marginal: S_i(x) = Fbar(x/a_i)^{a_i} * e^{-theta_i x}.
Shock survival v_i = p_i S_i(x); w_i = 1 - v_i.
Archimedean copula (psi decreasing, phi=psi^{-1}):
  S_min(x) = phi( sum psi(v_i) );   S_max(x) = 1 - phi( sum psi(w_i) ).
Paper's convention (printed Example 1): a ~=^w l iff ascending partial
sums of a >= those of l.
Claims: all st, direction X <=st Y (S_X <= S_Y) unless noted.
"""
import mpmath as mp
mp.mp.dps = 110


def copula(name):
    if name == "indep":
        return (lambda u: -mp.log(u), lambda t: mp.e ** (-t))
    if name == "amh":
        d = mp.mpf('0.8')
        return (lambda u: mp.log((1 - d + d * u) / u),
                lambda t: (1 - d) / (mp.e ** t - d))
    if name == "ex5":
        return (lambda u: mp.log((2 - u) / u), lambda t: 2 / (1 + mp.e ** t))
    raise ValueError(name)


def marg(xv, a, th, Fbar):
    xv = mp.mpf(xv)
    return Fbar(xv / mp.mpf(a)) ** mp.mpf(a) * mp.e ** (-mp.mpf(th) * xv)


def S_min(ps, aa, ths, Fbar, cop, xv):
    psi, phi = copula(cop)
    V = mp.mpf(0)
    for p, a, t in zip(ps, aa, ths):
        V += psi(mp.mpf(p) * marg(xv, a, t, Fbar))
    return phi(V)


def S_max(ps, aa, ths, Fbar, cop, xv):
    psi, phi = copula(cop)
    V = mp.mpf(0)
    for p, a, t in zip(ps, aa, ths):
        V += psi(1 - mp.mpf(p) * marg(xv, a, t, Fbar))
    return 1 - phi(V)


def asc_sup(a, b):
    A, B = sorted(map(mp.mpf, a)), sorted(map(mp.mpf, b))
    return all(sum(A[:k]) >= sum(B[:k]) - mp.mpf('1e-60') for k in range(1, len(A) + 1))


def scan(X, Y, fun, lo, hi, npts=400, claim_dir='X<=stY'):
    neg = []
    for i in range(1, npts + 1):
        t = mp.mpf(lo) + (mp.mpf(hi) - mp.mpf(lo)) * mp.mpf(i) / (npts + 1)
        d = fun(*X, t) - fun(*Y, t)
        if d > mp.mpf('1e-60'):      # X<=stY needs SX<=SY
            neg.append((t, d))
    return neg


PARX = lambda y: 1 / y
WB5 = lambda y: mp.e ** (-y ** 5)
PAR2 = lambda y: (1 + y) ** (-2)
EXP = lambda y: mp.e ** (-y)

print("===== Example 1 / Theorem 2 (parallel max, a ~=^w l -> X<=stY) =====")
for av, lv, pv, cop in [([37, 24, 5], [7, 4, 2], ['0.72', '0.18', '0.02'], 'amh'),
                        ([37, 24, 5], [7, 4, 2], ['0.72', '0.18', '0.02'], 'indep'),
                        ([5, 7, 9], [3, 5, 11], ['0.5', '0.5', '0.5'], 'amh'),
                        ([5, 7, 9], [3, 5, 11], ['0.5', '0.5', '0.5'], 'indep')]:
    th = ['0.1'] * len(av)
    lo = max(max(av), max(lv), 1)
    print("inst", av, lv, cop, "premise a~=^w l:", asc_sup(av, lv),
          "| D+ check a,p,l all desc:",
          av == sorted(av, reverse=True), lv == sorted(lv, reverse=True))
    neg = scan((pv, av, th, PARX, cop), (pv, lv, th, PARX, cop),
               S_max, lo, '300')
    print("   X<=stY:", "VIOLATED" if neg else "holds",
          [(mp.nstr(t, 5), mp.nstr(d, 8)) for t, d in neg[:2]], len(neg))
    t0 = mp.mpf('37000000000001') / mp.mpf('1000000000000')
    print("   at eval witness 37.000000000001: SX-SY =",
          mp.nstr(S_max(pv, av, th, PARX, cop, t0)
                  - S_max(pv, lv, th, PARX, cop, t0), 10))
    neg2 = scan((pv, lv, th, PARX, cop), (pv, av, th, PARX, cop), S_max, lo, '300')
    print("   opposite Y<=stX:", "VIOLATED" if neg2 else "holds", len(neg2))

print("===== Theorem 1 (parallel, h(p)~=^w h(q), p>=q coord.) =====")
for pv, qv, cop in [(['0.4', '0.5', '0.6'], ['0.3', '0.4', '0.5'], 'amh'),
                    (['0.4', '0.5', '0.6'], ['0.3', '0.4', '0.5'], 'indep'),
                    (['0.6', '0.7', '0.8', '0.9'], ['0.5', '0.6', '0.7', '0.8'], 'amh'),
                    (['0.6', '0.7', '0.8', '0.9'], ['0.5', '0.6', '0.7', '0.8'], 'indep')]:
    th = ['0.1'] * len(pv); av = [3] * len(pv)
    print("inst", pv, qv, cop, "premise asc sums p>=q:", asc_sup(pv, qv))
    neg = scan((pv, av, th, PARX, cop), (qv, av, th, PARX, cop),
               S_max, '3', '200')
    print("   Xp<=stXq:", "VIOLATED" if neg else "holds",
          [(mp.nstr(t, 5), mp.nstr(d, 8)) for t, d in neg[:2]], len(neg))
    t0 = mp.mpf('3000000000001') / mp.mpf('1000000000000')
    print("   witness ~3+1e-12:", mp.nstr(
        S_max(pv, av, th, PARX, cop, t0) - S_max(qv, av, th, PARX, cop, t0), 10))

print("===== Theorem 3/9 same as 2 but both copulas; Thm9 series-min =====")
for claim, cps in [('Theorem 3', ['amh', 'indep']), ('Theorem 9', ['indep', 'ex5'])]:
    for cop in cps:
        for av, lv, pv in [([5, 7, 9], [3, 5, 11], ['0.5', '0.5', '0.5']),
                           ([37, 24, 5], [7, 4, 2], ['0.7', '0.2', '0.1'])]:
            th = ['0.1'] * len(av)
            lo = max(max(av), max(lv), 1)
            fun = S_min if claim == 'Theorem 9' else S_max
            print(claim, cop, av, lv, "premise:", asc_sup(av, lv))
            neg = scan((pv, av, th, PARX, cop), (pv, lv, th, PARX, cop),
                       fun, lo, '300')
            print("   X<=stY:", "VIOLATED" if neg else "holds",
                  [(mp.nstr(t, 5), mp.nstr(d, 8)) for t, d in neg[:1]], len(neg))

print("===== Example 5 / Theorem 8 (series min, WB5, log-concave gen.) =====")
for cop in ['indep', 'ex5']:
    for av, lv, pv, tv in [([5, 7, 9], [3, 5, 11], ['0.5'] * 3, ['0.1'] * 3),
                           ([6, 7, 8, 9], [4, 5, 7, 11], ['0.6'] * 4, ['0.2'] * 4),
                           ([5, 8], [3, 11], ['0.5'] * 2, ['0.1'] * 2)]:
        print(cop, av, lv, "premise a~=^w l:", asc_sup(av, lv))
        neg = scan((pv, av, tv, WB5, cop), (pv, lv, tv, WB5, cop),
                   S_min, '0', '30')
        print("   X<=stY:", "VIOLATED" if neg else "holds",
              [(mp.nstr(t, 5), mp.nstr(d, 8)) for t, d in neg[:1]], len(neg))
        t0 = mp.mpf('1e-12')
        print("   witness ~0: SX-SY =",
              mp.nstr(S_min(pv, av, tv, WB5, cop, t0)
                      - S_min(pv, lv, tv, WB5, cop, t0), 12))

print("===== Theorem 6(a) (series min, theta ~=^w eta, PAR2) =====")
for cop in ['indep', 'amh']:
    for tv, ev in [(['0.3', '0.4', '0.5'], ['0.1', '0.4', '0.6']),
                   (['0.4', '0.5', '0.6', '0.7'], ['0.2', '0.4', '0.6', '0.8']),
                   ([mp.mpf('0.0008'), mp.mpf('0.001'), mp.mpf('0.0012')],
                    [mp.mpf('0.0005'), mp.mpf('0.001'), mp.mpf('0.0015')])]:
        av = [2] * len(tv); pv = ['0.9'] * len(tv)
        print(cop, [mp.nstr(v, 5) for v in tv], [mp.nstr(v, 5) for v in ev],
              "premise th~=^w eta:", asc_sup(tv, ev))
        neg = scan((pv, av, tv, PAR2, cop), (pv, av, ev, PAR2, cop),
                   S_min, '0', '60')
        print("   X<=stY:", "VIOLATED" if neg else "holds",
              [(mp.nstr(t, 5), mp.nstr(d, 8)) for t, d in neg[:1]], len(neg))
        t0 = mp.mpf('1e-12')
        print("   witness ~0: SX-SY =",
              mp.nstr(S_min(pv, av, tv, PAR2, cop, t0)
                      - S_min(pv, av, ev, PAR2, cop, t0), 12))
