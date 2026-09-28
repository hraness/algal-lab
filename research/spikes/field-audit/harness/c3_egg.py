"""C3 second evaluation for doi_10.1214/18-BJPS410 (EGG) refutations --
independent mpmath implementation.

Exponentiated-scale margins: cdf_i(x) = F(l_i x)^{a_i}; GE baseline
F(t)=1-e^{-t} (EGG sub-family nu=tau=1; tr~ decreasing & convex, verified
numerically).  Lomax F(t)=1-(1+t)^{-2} also satisfies all conditions.
Max survival S_{n:n} = 1 - prod_i F(l_i x)^{a_i};  claim Y <=st X i.e.
S_Y <= S_X.  rh: r~_Y <= r~_X checked via log-cdf ratios: F_Y(x)/F_X(x)
must be increasing; equivalently log F_Y - log F_X nondecreasing.
"""
from mpmath import mp, mpf, iv

mp.dps = 80; iv.dps = 80
FIG1 = dict(ls=[mpf(v) for v in ['9','6','1','0.7']],
            ms=[mpf(v) for v in ['8','5','0.8','0.75']],
            aa=[mpf(v) for v in ['1','3','5','0.6']],
            bb=[mpf(v) for v in ['4.6','4.4','0.5','0.1']])
FIG2 = dict(ls=[mpf(v) for v in ['2','11','12','13']],
            ms=[mpf(v) for v in ['5','6','10','14']],
            aa=[mpf(v) for v in ['4','0.8','3.3','5']],
            bb=[mpf(v) for v in ['1','3','2.1','7']])


def fcdf(l, a, base, xx, L):
    return base(l * xx, L) ** a


GE    = lambda t, L: 1 - L.exp(-t)
LOMAX = lambda t, L: 1 - (1 + t) ** (-2)


def maxsf(ls, aa, base, xx, L):
    g = 1
    for l, a in zip(ls, aa):
        g *= fcdf(l, a, base, xx, L)
    return 1 - g


def maxcdf(ls, aa, base, xx, L):
    g = 1
    for l, a in zip(ls, aa):
        g *= fcdf(l, a, base, xx, L)
    return g


# Theorem 3/6 (st, Y<=st X): FIG1 params; GE and Lomax baselines
for base, bn in [(GE, 'GE'), (LOMAX, 'LOMAX')]:
    ds = []
    for t in ['0.5', '1', '2', '5', '10', '50']:
        d = maxsf(FIG1['ms'], FIG1['bb'], base, mpf(t), mp) - \
            maxsf(FIG1['ls'], FIG1['aa'], base, mpf(t), mp)
        ds.append(mp.nstr(d, 8))
    print('Thm6 st %s SY-SX:' % bn, ds)

# strict interval at x=2 under GE (SY-SX must be >=0 for claim)
d = maxsf([iv.mpf(v) for v in ['8','5','0.8','0.75']],
          [iv.mpf(v) for v in ['4.6','4.4','0.5','0.1']], GE, iv.mpf(2), iv) - \
    maxsf([iv.mpf(v) for v in ['9','6','1','0.7']],
          [iv.mpf(v) for v in ['1','3','5','0.6']], GE, iv.mpf(2), iv)
print('Thm6 st GE iv x=2:', mp.nstr(d.a, 10), '..', mp.nstr(d.b, 10))

# Theorem 4/7 (rh, Y<=rh X): need F_Y(x)/F_X(x) increasing <=>
# log(F_Y)-log(F_X) nondecreasing.  Sample at increasing x.
for base, bn in [(GE, 'GE'), (LOMAX, 'LOMAX')]:
    xs = ['0.3', '0.5', '0.8', '1', '1.5', '2', '4']
    vals = []
    for t in xs:
        v = mp.log(maxcdf(FIG2['ms'], FIG2['bb'], base, mpf(t), mp)) - \
            mp.log(maxcdf(FIG2['ls'], FIG2['aa'], base, mpf(t), mp))
        vals.append(mp.nstr(v, 8))
    print('Thm7 rh %s log(FY/FX):' % bn, xs)
    print('   vals:', vals, 'nondecreasing?',
          all(mp.mpf(v1) <= mp.mpf(v2) + mpf('1e-20')
              for v1, v2 in zip(vals, vals[1:])))
