"""Independent verification: doi:10.1080/03610926.2021.1919898.

GM(a,b,l): S(x)=exp(-l x - (a/b)(e^{b x}-1)), r(x)=l+a e^{b x}.
Series min: S12=prod S_i, r=sum r_i, f=S*r.
Parallel max: F=prod(1-S_i).
lr order X<=lr Y iff f_X/f_Y decreasing (log-derivative <=0).
'no lr ordering' requires BOTH directions to fail (density ratio
non-monotone); 'no st ordering' requires F_X-F_Y to change sign.
Def 1: x >=^m y: desc partial sums x_[i] >= y_[i], equal totals.
"""
import mpmath as mp
mp.mp.dps = 110


def S_gm(t, a, b, l):
    a, b, l, t = mp.mpf(a), mp.mpf(b), mp.mpf(l), mp.mpf(t)
    return mp.e ** (-l * t - (a / b) * (mp.e ** (b * t) - 1))


def S_series(t, pars):
    return mp.fprod(S_gm(t, a, b, l) for a, b, l in pars)


def f_series(t, pars):
    return -mp.diff(lambda u: S_series(u, pars), mp.mpf(t))


def lr_dir(A, B, lo='0.0001', hi='5', npts=600):
    """Check X<=lr Y: d/dx (log f_X - log f_Y) <= 0 everywhere.
    Return list of positive-derivative points (violations)."""
    viol = []
    for i in range(1, npts + 1):
        t = mp.mpf(lo) + (mp.mpf(hi) - mp.mpf(lo)) * i / (npts + 1)
        d = mp.diff(lambda u: mp.log(f_series(u, A)), t) \
            - mp.diff(lambda u: mp.log(f_series(u, B)), t)
        if d > mp.mpf('1e-40'):
            viol.append((t, d))
    return viol


def F_par(t, pars):
    return mp.fprod(1 - S_gm(t, a, b, l) for a, b, l in pars)


def maj_desc(a, b):
    A = sorted(map(mp.mpf, a), reverse=True)
    B = sorted(map(mp.mpf, b), reverse=True)
    return abs(sum(A) - sum(B)) < mp.mpf('1e-60') and all(
        sum(A[:k]) >= sum(B[:k]) - mp.mpf('1e-60')
        for k in range(1, len(A)))


print("===== Counterexample 1(i): alpha>=^m alpha*, no lr order =====")
A1 = [('0.1', '0.2', '0.6'), ('20', '0.1', '0.5')]
B1 = [('2.1', '0.2', '0.6'), ('18', '0.1', '0.5')]
print("premise: alpha=(0.1,20) >=^m alpha*=(2.1,18):",
      maj_desc(['0.1', '20'], ['2.1', '18']),
      "| alpha,alpha* in E+, beta in D+: True")
v1 = lr_dir(A1, B1)
v2 = lr_dir(B1, A1)
print("X<=lr Y violations:", len(v1), [(mp.nstr(t, 5), mp.nstr(d, 8)) for t, d in v1[:2]])
print("Y<=lr X violations:", len(v2), [(mp.nstr(t, 5), mp.nstr(d, 8)) for t, d in v2[:2]])
print("eval witness 1/15: log-ratio deriv:",
      mp.nstr(mp.diff(lambda u: mp.log(f_series(u, A1)), mp.mpf('1') / 15)
              - mp.diff(lambda u: mp.log(f_series(u, B1)), mp.mpf('1') / 15), 10))

print("===== Counterexample 1(ii)/(b): beta>=^m beta*, no lr =====")
A2 = [('20', '0.8', '0.5'), ('0.1', '0.2', '0.6')]
B2 = [('20', '0.7', '0.5'), ('0.1', '0.3', '0.6')]
print("premise: beta=(0.8,0.2) >=^m beta*=(0.7,0.3):",
      maj_desc(['0.8', '0.2'], ['0.7', '0.3']))
v1 = lr_dir(A2, B2)
v2 = lr_dir(B2, A2)
print("X<=lr Y violations:", len(v1), [(mp.nstr(t, 5), mp.nstr(d, 8)) for t, d in v1[:2]])
print("Y<=lr X violations:", len(v2), [(mp.nstr(t, 5), mp.nstr(d, 8)) for t, d in v2[:2]])
print("eval witness 1e-12:", mp.nstr(
    mp.diff(lambda u: mp.log(f_series(u, A2)), mp.mpf('1e-12'))
    - mp.diff(lambda u: mp.log(f_series(u, B2)), mp.mpf('1e-12')), 10))

print("===== Counterexample 2: parallel max, alpha>=^m alpha*, 'no st' =====")
A = [('0.2', '2', '0.6'), ('0.1', '1', '0.6')]
B = [('0.18', '2', '0.6'), ('0.12', '1', '0.6')]
print("premise alpha=(0.2,0.1) >=^m alpha*=(0.18,0.12):",
      maj_desc(['0.2', '0.1'], ['0.18', '0.12']))
# st order: F_X - F_Y sign
mn = mp.mpf('1e30'); mx = mp.mpf('-1e30'); wmn = wmx = None
for i in range(1, 800):
    t = mp.mpf('0.0001') + mp.mpf('10') * i / 800
    d = F_par(t, A) - F_par(t, B)
    if d < mn: mn, wmn = d, t
    if d > mx: mx, wmx = d, t
print("F_X-F_Y min=%s at %s | max=%s at %s" % (mp.nstr(mn, 8), mp.nstr(wmn, 5), mp.nstr(mx, 8), mp.nstr(wmx, 5)))
t0 = mp.mpf('7') / 15
print("eval witness 7/15: F_X-F_Y =", mp.nstr(F_par(t0, A) - F_par(t0, B), 12))

print("===== Counterexample 3: 1/beta>=^m 1/beta*, 'no st' =====")
A = [('0.1', '0.5', '0.02'), ('0.2', '1', '0.02')]
B = [('0.1', mp.mpf(1) / mp.mpf('1.6'), '0.02'), ('0.2', mp.mpf(1) / mp.mpf('1.4'), '0.02')]
print("premise 1/beta=(2,1) >=^m 1/beta*=(1.6,1.4):",
      maj_desc(['2', '1'], ['1.6', '1.4']))
mn = mp.mpf('1e30'); mx = mp.mpf('-1e30'); wmn = wmx = None
for i in range(1, 800):
    t = mp.mpf('0.0001') + mp.mpf('15') * i / 800
    d = F_par(t, A) - F_par(t, B)
    if d < mn: mn, wmn = d, t
    if d > mx: mx, wmx = d, t
print("F_X-F_Y min=%s at %s | max=%s at %s" % (mp.nstr(mn, 8), mp.nstr(wmn, 5), mp.nstr(mx, 8), mp.nstr(wmx, 5)))
t0 = mp.mpf('1e-12')
print("eval witness ~0: F_X-F_Y =", mp.nstr(F_par(t0, A) - F_par(t0, B), 12),
      "| F_X(0)=", mp.nstr(F_par(t0, A), 8), "F_Y(0)=", mp.nstr(F_par(t0, B), 8))
