"""Independent verification of the 15 refuted claims, doi:10.2298/FIL2104315d.

Model (fresh): largest claim U_{n:n} cdf
  F_U(t) = prod_i [1 - p_i (1 - F((t-lam_i)/th_i)^{a_i})],  t > max lam_i.
Baselines (y>0): GLFR05 F=1-e^{-sqrt(y)}; MOQL per eq (5.2) a=0.1,b=-0.9,d=0.8;
LOM5 F=1-(1+5y)^{-1/5}; DEC1 Fbar=y^{-2}e^{1/y-1} (y>=1);
DEC2 Fbar=y^{-2}e^{(1/y^2-1)/2} (y>=1).
Checks: st (S_U >= S_V), rh (rt_U >= rt_V where rt=f/F).
"""
import mpmath as mp

mp.mp.dps = 110
I = mp.inf


def GLFR05(yy):
    return 1 - mp.e ** (-mp.sqrt(yy))


def MOQL(yy):
    a, b, d = mp.mpf('0.1'), mp.mpf('-0.9'), mp.mpf('0.8')
    q = (b + 1 + d * yy) / (b + 1) * mp.e ** (-d * yy)
    return (1 - q) / (1 - (1 - a) * q)


def LOM5(yy):
    return 1 - (1 + 5 * yy) ** mp.mpf('-0.2')


def DEC1(yy):
    return 1 - yy ** (-2) * mp.e ** (1 / yy - 1)


def DEC2(yy):
    return 1 - yy ** (-2) * mp.e ** ((1 / yy ** 2 - 1) / 2)


def FU(t, probs, alps, lams, ths, base):
    t = mp.mpf(t)
    out = mp.mpf(1)
    for p_, a_, l_, t_ in zip(probs, alps, lams, ths):
        y = (t - mp.mpf(l_)) / mp.mpf(t_)
        out *= 1 - mp.mpf(p_) * (1 - base(y) ** mp.mpf(a_))
    return out


def SU(t, *a):
    return 1 - FU(t, *a)


def diff_st(p1, lo, hi, npts=250):
    """S_U - S_V over (lo,hi): U>=st V iff >=0. Return min sign + witness."""
    lo, hi = mp.mpf(lo), mp.mpf(hi)
    neg = []
    for i in range(1, npts + 1):
        t = lo + (hi - lo) * i / (npts + 1)
        d = SU(t, *p1[0]) - SU(t, *p1[1])
        if d < -mp.mpf('1e-70'):
            neg.append((t, d))
    return neg


def rtil(t, params):
    """reversed hazard f/F = -d/dt log F."""
    return mp.diff(lambda u: mp.log(FU(u, *params)), mp.mpf(t))


def diff_rh(p1, lo, hi, npts=250):
    """U >=rh V iff rt_U >= rt_V."""
    lo, hi = mp.mpf(lo), mp.mpf(hi)
    neg = []
    for i in range(1, npts + 1):
        t = lo + (hi - lo) * i / (npts + 1)
        d = rtil(t, p1[0]) - rtil(t, p1[1])
        if d < -mp.mpf('1e-60'):
            neg.append((t, d))
    return neg


def maj_asc(a, b):
    """ascending partial sums of a >= b's (paper's >=^w)."""
    sa, sb = sorted(map(mp.mpf, a)), sorted(map(mp.mpf, b))
    return all(sum(sa[:k]) >= sum(sb[:k]) - mp.mpf('1e-60')
               for k in range(1, len(sa) + 1))


def plarge(th, dl):
    """1/th >=^p 1/del: asc products of th <= dl."""
    sa, sb = sorted(map(mp.mpf, th)), sorted(map(mp.mpf, dl))
    return all(mp.fprod(sa[:k]) <= mp.fprod(sb[:k]) + mp.mpf('1e-60')
               for k in range(1, len(sa) + 1))


def tchain(rows, w, i, j):
    """Apply T_w swapping cols i,j: new_i = w a_i + (1-w) a_j."""
    out = []
    for r in rows:
        r = list(r)
        ai, aj = r[i], r[j]
        r[i] = w * ai + (1 - w) * aj
        r[j] = (1 - w) * ai + w * aj
        out.append(r)
    return out


def M2(xrow, yrow):
    return all((xrow[i] - xrow[j]) * (yrow[i] - yrow[j]) >= 0
               for i in range(len(xrow)) for j in range(len(xrow)))


sqrt = mp.sqrt
EXP = mp.e

print("===== Theorem 3.1(i): psi=p^2 (C9), theta=delta=1; M2 + T_{1/2} =====")
# instance 1: G baseline
pU = (["0.5", "0.9"], ["0.5"] * 2, ["0.4", "1.2"], ["1"] * 2, GLFR05)
pV = ([sqrt(mp.mpf('0.53')), sqrt(mp.mpf('0.53'))], ["0.5"] * 2,
      ["0.8", "0.8"], ["1"] * 2, GLFR05)
print("premise: M2:", M2([mp.mpf('0.25'), mp.mpf('0.81')], [mp.mpf('0.4'), mp.mpf('1.2')]))
neg = diff_st((pU, pV), mp.mpf('1.2'), mp.mpf('400'))
print("GLFR05 inst1:", "VIOLATED" if neg else "holds", neg[:2], "n=", len(neg))
t0 = mp.mpf('41317') / 300
print("  at eval witness t=41317/300=%s: S_U-S_V = %s" % (mp.nstr(t0, 8), mp.nstr(SU(t0, *pU) - SU(t0, *pV), 10)))
# instance 2: L5
pU = (["0.5", "0.9"], ["0.8"] * 2, ["0.4", "1.2"], ["1"] * 2, LOM5)
pV = ([sqrt(mp.mpf('0.53')), sqrt(mp.mpf('0.53'))], ["0.8"] * 2,
      ["0.8", "0.8"], ["1"] * 2, LOM5)
neg = diff_st((pU, pV), mp.mpf('1.2'), mp.mpf('400'))
print("LOM5 inst2:", "VIOLATED" if neg else "holds", neg[:2], "n=", len(neg))

print("===== Theorem 3.2(i): n=3 =====")
wp = [mp.mpf('0.09'), mp.mpf('0.25'), mp.mpf('0.64')]
p = [sqrt(w) for w in wp]
lam = [mp.mpf('0.2'), mp.mpf('0.7'), mp.mpf('1.5')]
wq, mu = tchain([wp, lam], mp.mpf('0.5'), 0, 1)
q = [sqrt(w) for w in wq]
print("psi(q),mu =", [mp.nstr(v, 8) for v in wq], [mp.nstr(v, 8) for v in mu])
print("premise M3 co-monotone:", M2(wp, lam))
pU = (p, ["0.5"] * 3, lam, ["1"] * 3, GLFR05)
pV = (q, ["0.5"] * 3, mu, ["1"] * 3, GLFR05)
neg = diff_st((pU, pV), mp.mpf('1.5'), mp.mpf('300'))
print("GLFR05:", "VIOLATED" if neg else "holds", neg[:1], len(neg))
pU = (p, ["0.9"] * 3, lam, ["1"] * 3, LOM5)
pV = (q, ["0.9"] * 3, mu, ["1"] * 3, LOM5)
neg = diff_st((pU, pV), mp.mpf('1.5'), mp.mpf('300'))
print("LOM5 a=.9:", "VIOLATED" if neg else "holds", neg[:1], len(neg))
t0 = mp.mpf('6625') / 48
print("  eval witness 6625/48=%s" % mp.nstr(t0, 8),
      "S_U-S_V=", mp.nstr(SU(t0, *(["0.5"] * 3,) if False else (0)), 5) if False else "")

print("===== Theorem 3.3(i): two different-structure T =====")
wq, mu = tchain([wp, lam], mp.mpf('0.6'), 0, 1)
wq, mu = tchain([wq, mu], mp.mpf('0.6'), 1, 2)
q = [sqrt(w) for w in wq]
pU = (p, ["0.5"] * 3, lam, ["1"] * 3, GLFR05)
pV = (q, ["0.5"] * 3, mu, ["1"] * 3, GLFR05)
neg = diff_st((pU, pV), mp.mpf('1.5'), mp.mpf('300'))
print("GLFR05:", "VIOLATED" if neg else "holds", neg[:1], len(neg))

print("===== Theorem 3.4(ii): (lam,psi_p) in M2 chain; rh =====")
p = [sqrt(mp.mpf('0.25')), sqrt(mp.mpf('0.81'))]
lam = [mp.mpf('0.4'), mp.mpf('1.2')]
wq, mu = tchain([wp if False else [mp.mpf('0.25'), mp.mpf('0.81')], lam], mp.mpf('0.5'), 0, 1)
q = [sqrt(w) for w in wq]
print("premise M2(lam,psip):", M2(lam, [mp.mpf('0.25'), mp.mpf('0.81')]),
      "| q:", [mp.nstr(v, 8) for v in q], "mu:", mu)
for base, nm in ((LOM5, 'LOM5'), (MOQL, 'MOQL')):
    pU = (p, ["1"] * 2, lam, ["1"] * 2, base)
    pV = (q, ["1"] * 2, mu, ["1"] * 2, base)
    neg = diff_rh((pU, pV), mp.mpf('1.2'), mp.mpf('400'))
    print(nm, ":", "VIOLATED" if neg else "holds", neg[:1], len(neg))
t0 = mp.mpf('2621797') / 300
pU = (p, ["1"] * 2, lam, ["1"] * 2, LOM5)
pV = (q, ["1"] * 2, mu, ["1"] * 2, LOM5)
print("  at witness 2621797/300:", mp.nstr(rtil(t0, pU) - rtil(t0, pV), 10))

print("===== Theorem 3.5(ii): n=3 rh =====")
wp = [mp.mpf('0.09'), mp.mpf('0.25'), mp.mpf('0.64')]
p = [sqrt(w) for w in wp]
lam = [mp.mpf('0.2'), mp.mpf('0.7'), mp.mpf('1.5')]
wq, mu = tchain([wp, lam], mp.mpf('0.5'), 0, 2)
q = [sqrt(w) for w in wq]
print("premise M3(lam,psip):", M2(lam, wp))
for base, nm in ((LOM5, 'LOM5'), (DEC1, 'DEC1')):
    lo = mp.mpf('1.5') if base is LOM5 else mp.mpf('2.5')  # lam+th=2.5 for DEC1
    pU = (p, ["1"] * 3, lam, ["1"] * 3, base)
    pV = (q, ["1"] * 3, mu, ["1"] * 3, base)
    neg = diff_rh((pU, pV), lo, mp.mpf('300'))
    print(nm, ":", "VIOLATED" if neg else "holds", neg[:1], len(neg))
t0 = mp.mpf('107') / 8
pU = (p, ["1"] * 3, lam, ["1"] * 3, LOM5)
pV = (q, ["1"] * 3, mu, ["1"] * 3, LOM5)
print("  at witness 107/8:", mp.nstr(rtil(t0, pU) - rtil(t0, pV), 10))

print("===== Theorem 3.6(ii): two T's, rh =====")
wq, mu = tchain([wp, lam], mp.mpf('0.6'), 0, 1)
wq, mu = tchain([wq, mu], mp.mpf('0.6'), 1, 2)
q = [sqrt(w) for w in wq]
pU = (p, ["1"] * 3, lam, ["1"] * 3, LOM5)
pV = (q, ["1"] * 3, mu, ["1"] * 3, LOM5)
neg = diff_rh((pU, pV), mp.mpf('1.5'), mp.mpf('300'))
print("LOM5:", "VIOLATED" if neg else "holds", neg[:1], len(neg))
t0 = mp.mpf('2097509') / 240
print("  at witness 2097509/240=%s:" % mp.nstr(t0, 8), mp.nstr(rtil(t0, pU) - rtil(t0, pV), 10))

print("===== Corollary 3.1(i) = Thm 3.2(i) tested above =====")
print("===== Corollary 3.2(ii) = Thm 3.5(ii) tested above =====")

print("===== Theorem 4.1: alpha >=^w beta, p desc vs alpha asc; claim U<=stV =====")
alp = [mp.mpf('1'), mp.mpf('3'), mp.mpf('5')]
bet = [mp.mpf('0.5'), mp.mpf('3.5'), mp.mpf('4')]
p = [mp.mpf('0.9'), mp.mpf('0.6'), mp.mpf('0.3')]
print("premise asc-partials alpha>=beta:", maj_asc(alp, bet),
      "| alpha asc & p desc (E+/D+ mix): alpha asc:", alp == sorted(alp),
      "p desc:", p == sorted(p, reverse=True))
for thv in (["1"] * 3, ["2"] * 3):
    pU = (p, alp, ["1"] * 3, thv, GLFR05)
    pV = (p, bet, ["1"] * 3, thv, GLFR05)
    # claim U <=st V: S_U <= S_V
    neg2 = diff_st((pV, pU), mp.mpf('1'), mp.mpf('400'))
    print("th=", thv[0], ":", "VIOLATED" if neg2 else "holds", neg2[:1], len(neg2))
    t0 = mp.mpf('1000000000001') / mp.mpf('1000000000000')
    print("  at witness ~1+1e-12:", mp.nstr(SU(t0, *pU) - SU(t0, *pV), 12))

print("===== Theorem 4.2: psi_p >=^w psi_q; claim U>=stV =====")
wp = [mp.mpf('0.25'), mp.mpf('0.49'), mp.mpf('0.81')]
wq = [mp.mpf('0.16'), mp.mpf('0.36'), mp.mpf('0.64')]
p = [sqrt(w) for w in wp]; q = [sqrt(w) for w in wq]
print("premise psi_p >=^w psi_q:", maj_asc(wp, wq))
lam = ["1", "2", "3"]; th = ["1", "2", "3"]; al = ["0.5", "0.7", "0.9"]
for base, nm in ((GLFR05, 'GLFR05'), (MOQL, 'MOQL')):
    pU = (p, al, lam, th, base)
    pV = (q, al, lam, th, base)
    neg = diff_st((pU, pV), mp.mpf('1'), mp.mpf('400'))
    print(nm, ":", "VIOLATED" if neg else "holds", neg[:1], len(neg))
t0 = mp.mpf('31') / 10
pU = (p, al, lam, th, GLFR05); pV = (q, al, lam, th, GLFR05)
print("  witness 31/10: S_U-S_V =", mp.nstr(SU(t0, *pU) - SU(t0, *pV), 10))

print("===== Theorem 4.3(i): 1/th >=^p 1/del; claim U>=stV =====")
lam = ["1", "1.5", "2"]; p = ["0.2", "0.5", "0.8"]
for th, dl in (([mp.mpf('1'), mp.mpf('3'), mp.mpf('5')], [mp.mpf('2'), mp.mpf('3'), mp.mpf('6')]),
               ([mp.mpf('1'), mp.mpf('2'), mp.mpf('8')], [mp.mpf('2'), mp.mpf('4'), mp.mpf('4')])):
    print("premise p-larger:", plarge(th, dl))
    pU = (p, ["0.5"] * 3, lam, th, DEC1)
    pV = (p, ["0.5"] * 3, lam, dl, DEC1)
    lo = max(mp.mpf(l) + mp.mpf(t) for l, t in zip(lam, th + dl))
    neg = diff_st((pU, pV), lo, mp.mpf('300'))
    print("  DEC1:", "VIOLATED" if neg else "holds", neg[:1], len(neg))
    t0 = mp.mpf('8000000000001') / mp.mpf('1000000000000')
    print("  witness ~8+1e-12: S_U-S_V =", mp.nstr(SU(t0, *pU) - SU(t0, *pV), 12))

print("===== Theorem 4.5(i): all three hetero =====")
th, dl = [mp.mpf('1'), mp.mpf('3'), mp.mpf('5')], [mp.mpf('2'), mp.mpf('3'), mp.mpf('6')]
lam, mu = [mp.mpf('1'), mp.mpf('3'), mp.mpf('6')], [mp.mpf('0.5'), mp.mpf('2.5'), mp.mpf('4')]
wp = [mp.mpf('0.25'), mp.mpf('0.49'), mp.mpf('0.81')]
wq = [mp.mpf('0.16'), mp.mpf('0.36'), mp.mpf('0.64')]
print("premises:", plarge(th, dl), maj_asc(wp, wq), maj_asc(lam, mu))
p = [sqrt(w) for w in wp]; q = [sqrt(w) for w in wq]
pU = (p, ["0.5"] * 3, lam, th, DEC1)
pV = (q, ["0.5"] * 3, mu, dl, DEC1)
lo = max([l + t for l, t in zip(lam, th)] + [m + d for m, d in zip(mu, dl)])
neg = diff_st((pU, pV), lo, mp.mpf('300'))
print("DEC1:", "VIOLATED" if neg else "holds", neg[:1], len(neg))
t0 = mp.mpf('2479') / 120
print("  witness 2479/120:", mp.nstr(SU(t0, *pU) - SU(t0, *pV), 10))

print("===== Theorem 4.8(i): 1/th >=^w 1/del; claim U>=rhV =====")
lam = ["1", "1.5", "2"]; p = ["0.2", "0.5", "0.8"]
for th, dl in (([mp.mpf('1'), mp.mpf('3'), mp.mpf('5')], [mp.mpf('2'), mp.mpf('3'), mp.mpf('6')]),
               ([mp.mpf('1'), mp.mpf('2'), mp.mpf('8')], [mp.mpf('2'), mp.mpf('4'), mp.mpf('4')])):
    # 1/th >=^w 1/del <=> asc sums of 1/th >= of 1/del <=> asc sums th <= dl
    inv_ok = maj_asc([1 / t for t in th], [1 / d for d in dl])
    print("premise 1/th >=^w 1/del:", inv_ok)
    pU = (p, ["1"] * 3, lam, th, DEC1)
    pV = (p, ["1"] * 3, lam, dl, DEC1)
    lo = max(mp.mpf(l) + mp.mpf(t) for l, t in zip(lam, th + dl))
    neg = diff_rh((pU, pV), lo, mp.mpf('300'))
    print("  DEC1:", "VIOLATED" if neg else "holds", neg[:1], len(neg))
    t0 = mp.mpf('8000000000001') / mp.mpf('1000000000000')
    print("  witness ~8+1e-12: rtU-rtV =", mp.nstr(rtil(t0, pU) - rtil(t0, pV), 12))

print("===== Theorem 4.11(i): combined weak-maj, rh =====")
th, dl = [mp.mpf('1'), mp.mpf('3'), mp.mpf('5')], [mp.mpf('2'), mp.mpf('3'), mp.mpf('6')]
lam, mu = [mp.mpf('1'), mp.mpf('3'), mp.mpf('6')], [mp.mpf('0.5'), mp.mpf('2.5'), mp.mpf('4')]
p = [sqrt(w) for w in wp]; q = [sqrt(w) for w in wq]
print("premises:", maj_asc([1 / t for t in th], [1 / d for d in dl]),
      maj_asc(wp, wq), maj_asc(lam, mu))
pU = (p, ["1"] * 3, lam, th, DEC1)
pV = (q, ["1"] * 3, mu, dl, DEC1)
lo = max([l + t for l, t in zip(lam, th)] + [m + d for m, d in zip(mu, dl)])
neg = diff_rh((pU, pV), lo, mp.mpf('300'))
print("DEC1:", "VIOLATED" if neg else "holds", neg[:1], len(neg))
t0 = mp.mpf('3277') / 120
print("  witness 3277/120:", mp.nstr(rtil(t0, pU) - rtil(t0, pV), 10))

print("===== Example 5.2 (printed concrete claim U>=stV) =====")
pU = ([sqrt(mp.mpf('0.2')), sqrt(mp.mpf('0.5'))], ["0.52"] * 2,
      ["5", "6.1"], ["0.01"] * 2, MOQL)
pV = ([sqrt(mp.mpf('0.32')), sqrt(mp.mpf('0.38'))], ["0.52"] * 2,
      ["5.44", "5.66"], ["0.01"] * 2, MOQL)
# printed premise check: T_{0.6}: (0.2,0.5)*T -> (0.32,0.38)?  0.2*0.6+0.5*0.4=0.32 ok; lam: 5*0.6+6.1*0.4=5.44, 5*0.4+6.1*0.6=5.66 ok
print("printed T_0.6 check:", 0.2 * 0.6 + 0.5 * 0.4, 5 * 0.6 + 6.1 * 0.4)
neg = diff_st((pU, pV), mp.mpf('6.1'), mp.mpf('30'), npts=400)
print("MOQL:", "VIOLATED" if neg else "holds", neg[:2], len(neg))
t0 = mp.mpf('6101') / 1000
print("  witness 6101/1000:", mp.nstr(SU(t0, *pU) - SU(t0, *pV), 12))
