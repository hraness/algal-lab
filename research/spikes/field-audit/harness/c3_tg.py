"""C3 second evaluation for doi_10.1080/10920277.2019.1671203 (TG portfolio)
refutations -- pure mpmath (independent of closedform).

TG marginal survival: S_l(x) = Fbar(x)*(1 - l*F(x)), Fbar in {e^{-x}, e^{-x^2}}.
Max survival: 1 - prod_i (1 - p_i S_{l_i}(x));  min: prod_i p_i S_{l_i}(x).
Starred side: Robin-Hood transfer T applied to lambda and to u_i=h(p_i);
p*_i = h^{-1}(u*_i).  Claim (PDF-verified): Y*_{n:n} <=st Y_{n:n}, i.e.
S_star - S_starred... the tested expression is S_Y - S_Y* >= 0.
"""
from mpmath import mp, mpf, iv

mp.dps = 80; iv.dps = 80


def hval(p, h, L):
    return L.log(2 + p) if h == "log" else (5 * p + 2) / (p + 1)


def h_inv(u, h, L):
    return L.exp(u) - 2 if h == "log" else (u - 2) / (5 - u)


def t_apply(v, i, j, om):
    v = list(v)
    vi, vj = v[i], v[j]
    v[i] = (1 - om) * vi + om * vj
    v[j] = om * vi + (1 - om) * vj
    return v


def tgs(l, Fb, xx, L):
    F = 1 - Fb(xx, L)
    return Fb(xx, L) * (1 - l * F)


def maxsf(ps, ls, Fb, xx, L):
    g = 1
    for p, l in zip(ps, ls):
        g *= 1 - p * tgs(l, Fb, xx, L)
    return 1 - g


FBE = lambda z, L: L.exp(-z)
FBW = lambda z, L: L.exp(-z ** 2)


def scan(label, L):
    # instance 1: EXP, h=log, ls=(1/5,4/5), ps=(3/10,9/10), om=1/5
    ls = [L.mpf('0.2'), L.mpf('0.8')]; ps = [L.mpf('0.3'), L.mpf('0.9')]
    u = [hval(p, 'log', L) for p in ps]
    l2 = t_apply(ls, 0, 1, L.mpf('0.2')); u2 = t_apply(u, 0, 1, L.mpf('0.2'))
    pst = [h_inv(v, 'log', L) for v in u2]
    for x0 in ['1e-9', '0.05', '0.5', '0.8', '1', '2', '8']:
        d = maxsf(ps, ls, FBE, L.mpf(x0), L) - maxsf(pst, l2, FBE, L.mpf(x0), L)
        print(label, 'EXP d(%s)=%s' % (x0, mp.nstr(d, 8)))
    # instance 2: WBL, h=ratio, om=2/5
    u = [hval(p, 'ratio', L) for p in ps]
    l2 = t_apply(ls, 0, 1, L.mpf('0.4')); u2 = t_apply(u, 0, 1, L.mpf('0.4'))
    pst = [h_inv(v, 'ratio', L) for v in u2]
    for x0 in ['0.05', '0.5', '0.8', '1', '2', '8']:
        d = maxsf(ps, ls, FBW, L.mpf(x0), L) - maxsf(pst, l2, FBW, L.mpf(x0), L)
        print(label, 'WBL d(%s)=%s' % (x0, mp.nstr(d, 8)))
    # instance 3: n=3 EXP h=log two transfers
    ls3 = [L.mpf('0.1'), L.mpf('0.6'), L.mpf('0.9')]
    ps3 = [L.mpf('0.2'), L.mpf('0.5'), L.mpf('0.8')]
    u3 = [hval(p, 'log', L) for p in ps3]
    l3 = t_apply(ls3, 0, 1, L.mpf('0.2')); u3 = t_apply(u3, 0, 1, L.mpf('0.2'))
    l3 = t_apply(l3, 1, 2, L.mpf('0.4')); u3 = t_apply(u3, 1, 2, L.mpf('0.4'))
    ps3t = [h_inv(v, 'log', L) for v in u3]
    for x0 in ['0.05', '0.5', '0.8', '1', '2', '8']:
        d = maxsf(ps3, ls3, FBE, L.mpf(x0), L) - maxsf(ps3t, l3, FBE, L.mpf(x0), L)
        print(label, 'EXP3 d(%s)=%s' % (x0, mp.nstr(d, 8)))


print('== max claims: S_Y - S_Y* (claim Y* <=st Y requires >= 0) ==')
scan('mp', mp)
scan('iv', iv)
