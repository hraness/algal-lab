"""C3 for arxiv_2601.07249 (CLFRD) Remark 3.3 reversed-hazard refutation --
independent mpmath/interval check (cf. c3_clfrd.py for the lr claim).

S(x) = exp(-a x - b x^2/2 - l + l e^{-a x - b x^2/2});  F = 1 - S.
Claim (canonicalized): X >=rh Y when a1<=a2,b1<=b2,l1<=l2, i.e.
F_X/F_Y must be nondecreasing.  Since lr fails (g_Y/g_X decreasing near 0,
c3_clfrd.py), rh likely fails too.  Check log F_X - log F_Y slopes; the
reversed-hazard claim needs log F_X(x) - log F_Y(x) NONDECREASING.
Instance: X=(1,1,1), Y=(1,2,1) (a1=a2=1, b1=1<=b2=2, l1=l2=1).
"""
from mpmath import mp, mpf, iv

mp.dps = 80; iv.dps = 80


def Sf(a, b, l, t, L):
    e = L.exp(-a * t - b * t * t / 2)
    return L.exp(-a * t - b * t * t / 2 - l + l * e)


def logratio(t, L):
    return L.log(1 - Sf(1, 1, 1, t, L)) - L.log(1 - Sf(1, 2, 1, t, L))


pts = [mpf(k) / 10 ** 4 for k in (1, 2, 4, 8, 16, 64)] + [mpf('0.2'), mpf('0.5'), mpf(1)]
vals = [logratio(t, mp) for t in pts]
print('log FX/FY at t:', [mp.nstr(t, 4) for t in pts])
print('vals:', [mp.nstr(v, 8) for v in vals])
print('nondecreasing (needs X>=rhY):',
      all(v1 <= v2 for v1, v2 in zip(vals, vals[1:])))
d1 = logratio(iv.mpf('0.001'), iv); d2 = logratio(iv.mpf('0.01'), iv)
print('iv log-ratio(0.001) - log-ratio(0.01):',
      mp.nstr((d1 - d2).a, 8), '(>0 => strictly decreasing => rh fails)')
