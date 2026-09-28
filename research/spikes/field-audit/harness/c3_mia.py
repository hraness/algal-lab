"""C3 second evaluation for doi_10.7153/mia-2020-23-03 refutations --
independent mpmath implementation (no sympy/closedform).

Portfolio max survival under independent Bernoulli indicators I(p_i):
   S(x) = 1 - E_mu[ C_cop( F_i(x)^{mu_i} ) ],  mu ~ prod Bernoulli
with independence copula C(u)=prod u_i ->  1 - prod_i (1 - p_i Fbar_i(x)).
h(u) = log(2+u), h^{-1}(t) = e^t - 2.
Margins: gen e^{-l x};  scale (1+l x)^{-2};  power e^{-l x};  tg e^{-x}(1-l(1-e^{-x})).
"""
from mpmath import mp, mpf, iv
from itertools import product

mp.dps = 80; iv.dps = 80


def hval(p, L): return L.log(2 + p)
def hinv(u, L): return L.exp(u) - 2


def port_max_sf(ps, sf_list, xx, L):
    g = 1
    for p, sf in zip(ps, sf_list):
        g *= 1 - p * sf(xx, L)
    return 1 - g


GEN = lambda l: (lambda xx, L: L.exp(-l * xx))
SCL = lambda l: (lambda xx, L: (1 + l * xx) ** (-2))
POW = lambda l: (lambda xx, L: L.exp(-l * xx))
TG  = lambda l: (lambda xx, L: L.exp(-xx) * (1 - l * (1 - L.exp(-xx))))


def show(label, diffs_at):
    for xx, d in diffs_at:
        print(label, 'x=%s:' % xx, mp.nstr(d, 10))


# Theorem 3.1: ls=(1/2,1), ps=(0.2,0.8); pss = hinv of 2/3-1/3 averages of
# h(p1),h(p2):  u*1=(2 h(p1)+h(p2))/3, u*2=(h(p1)+2 h(p2))/3.
for L, tag in [(mp, 'mp'), (iv, 'iv')]:
    hp1, hp2 = hval(L.mpf('0.2'), L), hval(L.mpf('0.8'), L)
    pss = [hinv((2 * hp1 + hp2) / 3, L), hinv((hp1 + 2 * hp2) / 3, L)]
    ps = [L.mpf('0.2'), L.mpf('0.8')]
    sfs = [GEN(L.mpf('0.5')), GEN(L.mpf(1))]
    for x0 in ['0.5', '1', '2.13', '5', '20']:
        d = port_max_sf(pss, sfs, L.mpf(x0), L) - port_max_sf(ps, sfs, L.mpf(x0), L)
        print('Thm3.1', tag, 'S*-S at x=%s:' % x0, mp.nstr(d, 10))

# Theorem 3.3/3.5 (gen margins) & 3.4/Ex3.1 (scale margins):
# ls=(1/2,1), lss=(3/5,9/10), same pss transform.
for fam, lab in [(GEN, 'Thm3.3/3.5'), (SCL, 'Thm3.4/Ex3.1')]:
    for L, tag in [(mp, 'mp'), (iv, 'iv')]:
        hp1, hp2 = hval(L.mpf('0.2'), L), hval(L.mpf('0.8'), L)
        pss = [hinv((2 * hp1 + hp2) / 3, L), hinv((hp1 + 2 * hp2) / 3, L)]
        ps = [L.mpf('0.2'), L.mpf('0.8')]
        sfX = [fam(L.mpf('0.5')), fam(L.mpf(1))]
        sfY = [fam(L.mpf('0.6')), fam(L.mpf('0.9'))]
        for x0 in ['0.5', '1', '2.13', '5', '20']:
            d = (port_max_sf(pss, sfY, L.mpf(x0), L)
                 - port_max_sf(ps, sfX, L.mpf(x0), L))
            print(lab, tag, 'x=%s:' % x0, mp.nstr(d, 10))
