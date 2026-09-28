"""Part 2: Thm 4.2, 4.3(i), 4.5(i), 4.8(i), 4.11(i), Example 5.2."""
import mpmath as mp
mp.mp.dps = 110


def GLFR05(yy): return 1 - mp.e ** (-mp.sqrt(yy))
def MOQL(yy):
    a, b, d = mp.mpf('0.1'), mp.mpf('-0.9'), mp.mpf('0.8')
    q = (b + 1 + d * yy) / (b + 1) * mp.e ** (-d * yy)
    return (1 - q) / (1 - (1 - a) * q)
def LOM5(yy): return 1 - (1 + 5 * yy) ** mp.mpf('-0.2')
def DEC1(yy): return 1 - yy ** (-2) * mp.e ** (1 / yy - 1)
def DEC2(yy): return 1 - yy ** (-2) * mp.e ** ((1 / yy ** 2 - 1) / 2)


def FU(t, probs, alps, lams, ths, base):
    t = mp.mpf(t)
    out = mp.mpf(1)
    for p_, a_, l_, t_ in zip(probs, alps, lams, ths):
        y = (t - mp.mpf(l_)) / mp.mpf(t_)
        out *= 1 - mp.mpf(p_) * (1 - base(y) ** mp.mpf(a_))
    return out


def SU(t, *a): return 1 - FU(t, *a)


def scan_st(U, V, lo, hi, npts=400):
    """points where U>=st V fails (S_U<S_V)."""
    neg = []
    for i in range(1, npts + 1):
        t = mp.mpf(lo) + (mp.mpf(hi) - mp.mpf(lo)) * i / (npts + 1)
        d = SU(t, *U) - SU(t, *V)
        if d < -mp.mpf('1e-70'):
            neg.append((t, d))
    return neg


def rtil(t, params):
    return mp.diff(lambda u: mp.log(FU(u, *params)), mp.mpf(t))


def scan_rh(U, V, lo, hi, npts=400):
    neg = []
    for i in range(1, npts + 1):
        t = mp.mpf(lo) + (mp.mpf(hi) - mp.mpf(lo)) * i / (npts + 1)
        d = rtil(t, U) - rtil(t, V)
        if d < -mp.mpf('1e-60'):
            neg.append((t, d))
    return neg


def asc_sums(a, b):
    sa, sb = sorted(map(mp.mpf, a)), sorted(map(mp.mpf, b))
    return all(sum(sa[:k]) >= sum(sb[:k]) - mp.mpf('1e-60') for k in range(1, len(sa) + 1))


def asc_prods(a, b):
    sa, sb = sorted(map(mp.mpf, a)), sorted(map(mp.mpf, b))
    return all(mp.fprod(sa[:k]) <= mp.fprod(sb[:k]) + mp.mpf('1e-60') for k in range(1, len(sa) + 1))


def asc_prods_ge(a, b):
    sa, sb = sorted(map(mp.mpf, a)), sorted(map(mp.mpf, b))
    return all(mp.fprod(sa[:k]) >= mp.fprod(sb[:k]) - mp.mpf('1e-60') for k in range(1, len(sa) + 1))


def desc_prods(a, b):
    sa = sorted(map(mp.mpf, a), reverse=True)
    sb = sorted(map(mp.mpf, b), reverse=True)
    return all(mp.fprod(sa[:k]) >= mp.fprod(sb[:k]) - mp.mpf('1e-60') for k in range(1, len(sa) + 1))


print("===== Theorem 4.2: psi(p)>=^w psi(q), alpha=beta, th=delta, lam=mu =====")
wp = [mp.mpf('0.25'), mp.mpf('0.49'), mp.mpf('0.81')]
wq = [mp.mpf('0.16'), mp.mpf('0.36'), mp.mpf('0.64')]
p = [mp.sqrt(w) for w in wp]; q = [mp.sqrt(w) for w in wq]
print("premise asc sums psip>=psiq:", asc_sums(wp, wq))
lam = ["1", "2", "3"]; th = ["1", "2", "3"]; al = ["0.5", "0.7", "0.9"]
U = (p, al, lam, th, GLFR05); V = (q, al, lam, th, GLFR05)
neg = scan_st(U, V, '3', '400')
print("GLFR05:", "VIOLATED" if neg else "holds", neg[:2], len(neg))
t0 = mp.mpf('31') / 10
print("  eval witness t=31/10:", mp.nstr(SU(t0, *U) - SU(t0, *V), 12))
U = (p, al, lam, th, LOM5); V = (q, al, lam, th, LOM5)
neg = scan_st(U, V, '3', '400')
print("LOM5 (extra baseline):", "VIOLATED" if neg else "holds", neg[:2], len(neg))

print("===== Theorem 4.3(i): 1/th >=^p 1/del =====")
lam = ["1", "1.5", "2"]; p = ["0.2", "0.5", "0.8"]
for th, dl in (([mp.mpf('1'), mp.mpf('3'), mp.mpf('5')], [mp.mpf('2'), mp.mpf('3'), mp.mpf('6')]),
               ([mp.mpf('1'), mp.mpf('2'), mp.mpf('8')], [mp.mpf('2'), mp.mpf('4'), mp.mpf('4')])):
    r1 = asc_prods([1 / t for t in th], [1 / d for d in dl])
    r2 = asc_prods_ge([1 / t for t in th], [1 / d for d in dl])
    r3 = desc_prods(th, dl)
    print(f"th={th} dl={dl}: literal-def(asc prod 1/th <= 1/dl): {r1}; "
          f"conv-reading(asc prod 1/th >= 1/dl): {r2}; desc-prod th >= dl: {r3}")
    U = (p, ["0.5"] * 3, lam, th, DEC1)
    V = (p, ["0.5"] * 3, lam, dl, DEC1)
    lo = max([mp.mpf(l) + mp.mpf(t) for l, t in zip(lam, th)] + [mp.mpf(l) + mp.mpf(d) for l, d in zip(lam, dl)])
    neg = scan_st(U, V, lo, '300')
    print("   DEC1 U>=stV:", "VIOLATED" if neg else "holds", neg[:1], len(neg))
    t0 = mp.mpf('8000000000001') / mp.mpf('1000000000000')
    print("   witness ~8+1e-12: S_U-S_V =", mp.nstr(SU(t0, *U) - SU(t0, *V), 12))
# fresh instance admissible under LITERAL def (asc prod 1/th <= 1/dl):
th, dl = [mp.mpf('2'), mp.mpf('4'), mp.mpf('9')], [mp.mpf('1'), mp.mpf('3'), mp.mpf('8')]
print("literal-admissible inst: th=(2,4,9) dl=(1,3,8):",
      asc_prods([1 / t for t in th], [1 / d for d in dl]),
      "| all asc E+:", th == sorted(th), dl == sorted(dl))
U = (p, ["0.5"] * 3, lam, th, DEC1)
V = (p, ["0.5"] * 3, lam, dl, DEC1)
lo = max([mp.mpf(l) + mp.mpf(t) for l, t in zip(lam, th)] + [mp.mpf(l) + mp.mpf(d) for l, d in zip(lam, dl)])
neg = scan_st(U, V, lo, '300')
print("   DEC1:", "VIOLATED" if neg else "holds", neg[:1], len(neg))

print("===== Theorem 4.5(i): 1/th>=^p1/dl & psi_p>=^w psi_q & lam>=^w mu =====")
th, dl = [mp.mpf('1'), mp.mpf('3'), mp.mpf('5')], [mp.mpf('2'), mp.mpf('3'), mp.mpf('6')]
lam, mu = [mp.mpf('1'), mp.mpf('3'), mp.mpf('6')], [mp.mpf('0.5'), mp.mpf('2.5'), mp.mpf('4')]
p = [mp.sqrt(w) for w in wp]; q = [mp.sqrt(w) for w in wq]
print("premises: p-larger(conv):", asc_prods_ge([1 / t for t in th], [1 / d for d in dl]),
      "supmaj psip:", asc_sums(wp, wq), "supmaj lam:", asc_sums(lam, mu))
U = (p, ["0.5"] * 3, lam, th, DEC1)
V = (q, ["0.5"] * 3, mu, dl, DEC1)
lo = max([mp.mpf(l) + mp.mpf(t) for l, t in zip(lam, th)]
         + [mp.mpf(m) + mp.mpf(d) for m, d in zip(mu, dl)])
neg = scan_st(U, V, lo, '300')
print("DEC1:", "VIOLATED" if neg else "holds", neg[:1], len(neg))
t0 = mp.mpf('2479') / 120
print("  witness 2479/120=%s:" % mp.nstr(t0, 8), mp.nstr(SU(t0, *U) - SU(t0, *V), 12))

print("===== Theorem 4.8(i): 1/th >=^w 1/del (sums); U>=rhV =====")
lam = ["1", "1.5", "2"]; p = ["0.2", "0.5", "0.8"]
for th, dl in (([mp.mpf('1'), mp.mpf('3'), mp.mpf('5')], [mp.mpf('2'), mp.mpf('3'), mp.mpf('6')]),
               ([mp.mpf('1'), mp.mpf('2'), mp.mpf('8')], [mp.mpf('2'), mp.mpf('4'), mp.mpf('4')])):
    real = asc_sums([1 / t for t in th], [1 / d for d in dl])
    print(f"th={th} dl={dl}: printed premise asc-sums 1/th>=1/dl: {real}")
    U = (p, ["1"] * 3, lam, th, DEC1)
    V = (p, ["1"] * 3, lam, dl, DEC1)
    lo = max([mp.mpf(l) + mp.mpf(t) for l, t in zip(lam, th)] + [mp.mpf(l) + mp.mpf(d) for l, d in zip(lam, dl)])
    neg = scan_rh(U, V, lo, '300')
    print("   DEC1 U>=rhV:", "VIOLATED" if neg else "holds", neg[:1], len(neg))
    t0 = mp.mpf('8000000000001') / mp.mpf('1000000000000')
    print("   witness ~8+1e-12: rtU-rtV =", mp.nstr(rtil(t0, U) - rtil(t0, V), 12))

print("===== Theorem 4.11(i): 1/th>=^w1/dl & psip>=^w psiq & lam>=^w mu; rh =====")
th, dl = [mp.mpf('1'), mp.mpf('3'), mp.mpf('5')], [mp.mpf('2'), mp.mpf('3'), mp.mpf('6')]
lam, mu = [mp.mpf('1'), mp.mpf('3'), mp.mpf('6')], [mp.mpf('0.5'), mp.mpf('2.5'), mp.mpf('4')]
p = [mp.sqrt(w) for w in wp]; q = [mp.sqrt(w) for w in wq]
print("premises:", asc_sums([1 / t for t in th], [1 / d for d in dl]),
      asc_sums(wp, wq), asc_sums(lam, mu))
U = (p, ["1"] * 3, lam, th, DEC1)
V = (q, ["1"] * 3, mu, dl, DEC1)
lo = max([mp.mpf(l) + mp.mpf(t) for l, t in zip(lam, th)]
         + [mp.mpf(m) + mp.mpf(d) for m, d in zip(mu, dl)])
neg = scan_rh(U, V, lo, '300')
print("DEC1:", "VIOLATED" if neg else "holds", neg[:1], len(neg))
t0 = mp.mpf('3277') / 120
print("  witness 3277/120=%s:" % mp.nstr(t0, 8), mp.nstr(rtil(t0, U) - rtil(t0, V), 12))

print("===== Example 5.2: printed concrete claim U2:2>=stV2:2 =====")
U = ([mp.sqrt(mp.mpf('0.2')), mp.sqrt(mp.mpf('0.5'))], ["0.52"] * 2,
     ["5", "6.1"], ["0.01"] * 2, MOQL)
V = ([mp.sqrt(mp.mpf('0.32')), mp.sqrt(mp.mpf('0.38'))], ["0.52"] * 2,
     ["5.44", "5.66"], ["0.01"] * 2, MOQL)
# Figure range ~6-10; check sign of F_U - F_V
for ts in ('6.1', '6.101', '6.5', '7', '7.5', '8', '9', '10', '15', '30'):
    t = mp.mpf(ts)
    print(f"  t={ts}: F_U-F_V = {mp.nstr(FU(t,*U)-FU(t,*V),12)}")
