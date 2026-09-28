"""Independent check: arxiv:2503.21275 Sect 4.3.2 FR error sign (FGMW parallel).

Printed: Fbar_D(t) = theta(t) + (-1)^{n-1} exp(A(t)) gamma (1 - theta(t)),
  theta = 1 - prod(1 - S_i) = Fbar_I,  exp(A(t)) = prod S_i,
  S_i(t) = exp(-lambda_i t^{alpha_i}).
Printed sign rule: E^r(t) <= 0 (i.e. r_D <= r_I) if gamma>0 & n odd,
  or gamma<0 & n even.
Hazard computed as -d/dt log S (avoids underflow).
"""
import mpmath as mp

mp.mp.dps = 110


def S_i(lam, al, t):
    return mp.exp(-mp.mpf(lam) * mp.mpf(t) ** mp.mpf(al))


def logSbar(n, gam, t, dependent=True):
    t = mp.mpf(t)
    S = [S_i(1, 1, t) for _ in range(n)]
    prodC = mp.fprod(1 - s for s in S)
    theta = 1 - prodC
    if not dependent:
        return mp.log(theta)
    prodS = mp.fprod(S)
    return mp.log(theta + mp.mpf(-1) ** (n - 1) * prodS * mp.mpf(gam) * prodC)


def hazard(n, gam, t, dependent):
    return -mp.diff(lambda u: logSbar(n, gam, u, dependent), mp.mpf(t))


for n, gam in [(2, '0.5'), (2, '-0.5'), (3, '0.5'), (3, '-0.5'), (4, '0.5'), (5, '0.5'), (2,'0.9'),(2,'-0.9')]:
    leq = (mp.mpf(gam) > 0 and n % 2 == 1) or (mp.mpf(gam) < 0 and n % 2 == 0)
    pos = neg = None
    npos = nneg = 0
    for i in range(1, 1600):
        t = mp.mpf(10) ** (mp.mpf(-3) + mp.mpf(i) * mp.mpf('0.0025'))  # t in (0.001,~40)
        d = hazard(n, gam, t, True) - hazard(n, gam, t, False)
        if d > mp.mpf('1e-60'):
            npos += 1
            if pos is None: pos = (t, d)
        elif d < -mp.mpf('1e-60'):
            nneg += 1
            neg = (t, d)
    print(f"n={n} gamma={gam} printed {'E^r<=0' if leq else 'E^r>=0(complement)'}:"
          f" pos {npos}, neg {nneg}")
    if pos: print("    + e.g. t=%s: %s" % (mp.nstr(pos[0],6), mp.nstr(pos[1],8)))
    if neg: print("    - e.g. t=%s: %s" % (mp.nstr(neg[0],6), mp.nstr(neg[1],8)))
    if pos and neg:
        print("    --> NOT one-signed")
# eval witness t=16/15 for n=2,g=1/2
for ts in ('0.001','1.0666666666666667','1.5','0.5'):
    d = hazard(2,'0.5',mp.mpf(ts),True)-hazard(2,'0.5',mp.mpf(ts),False)
    print(f"n=2 g=0.5 t={ts}: r_D-r_I = {mp.nstr(d,15)}")
