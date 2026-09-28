"""C3 second evaluation for doi_10.3934/math.2024434 refutations
(Corollary 2, Corollary 3) -- pure mpmath, independent of closedform.check.

MPHRS marginal:  S_i(x) = a*Fb(t*x)^la / (1 - (1-a)*Fb(t*x)^la)
MPRHRS marginal cdf: G_i(x) = a*F(t*x)^be / (1 - (1-a)*F(t*x)^be)
S_{2:n} = sum_i prod_{j!=i} s_j - (n-1) prod s_j   (independence copula,
which satisfies every copula hypothesis: product generator is log-concave).
F_{n-1:n} = same expression on cdfs; survival = 1 - F_{n-1:n}.
"""
from mpmath import mp, mpf, iv

mp.dps = 80; iv.dps = 80


def mphrs_s(a, t, la, base, xx):
    v = base(t * xx) ** la
    return a * v / (1 - (1 - a) * v)


def mprhrs_g(a, t, be, cdf, xx):
    v = cdf(t * xx) ** be
    return a * v / (1 - (1 - a) * v)


def os2(survs):
    n = len(survs); P = 1
    for s in survs: P *= s
    t = 0
    for i in range(n):
        p = 1
        for j in range(n):
            if j != i: p *= survs[j]
        t += p
    return t - (n - 1) * P


# Corollary 2: X ~ (a=1/3, theta_i, la=1; Fb=e^{-3x}), Y ~ (a=1/3, th0=1; Fb=e^{-2x})
# premise: theta0 = 1 >= mean(theta_i) = 0.75; claim X_{2:4} <=st Y_{2:4}.
a = mpf('1/3'); la = mpf(1)
def delta(xx):
    sX = [mphrs_s(a, t, la, lambda z: mp.exp(-3 * z), xx)
          for t in [mpf('0.6'), mpf('0.7'), mpf('0.8'), mpf('0.9')]]
    sY = [mphrs_s(a, mpf(1), la, lambda z: mp.exp(-2 * z), xx)] * 4
    return os2(sY) - os2(sX)      # SY - SX >= 0 iff X <=st Y
for xx in ['0.01', '0.1', '0.5', '1', '2', '5']:
    print('Cor2 delta(%s) =' % xx, mp.nstr(delta(mpf(xx)), 8))

def deltaiv(xx):
    ai = iv.mpf(1) / 3
    sx = [mphrs_s(ai, t, 1, lambda z: iv.exp(-3 * z), xx) for t in
          [iv.mpf(str(t)) for t in ['0.6','0.7','0.8','0.9']]]
    sy = [mphrs_s(ai, iv.mpf(1), 1, lambda z: iv.exp(-2 * z), xx)] * 4
    return os2(sy) - os2(sx)
for xx in ['1/10', '1/2', '1', '2']:
    v = deltaiv(iv.mpf(xx))
    print('Cor2 interval delta(%s) =' % xx, v)

# Corollary 3 (MPRHRS X_{n-1:n}): X: a=1/2, th=1, la=(2,3,4), F1=1-e^{-x/2};
# Y: a=1/2, th=1, la0=4; F2=1-e^{-x}.  Premise la0=4 >= mean(2,3,4)=3; F1<=F2.
a2 = mpf('1/2')
def delta3(xx):
    gX = [mprhrs_g(a2, mpf(1), l, lambda z: 1 - mp.exp(-z/2), xx)
          for l in [mpf(2), mpf(3), mpf(4)]]
    gY = [mprhrs_g(a2, mpf(1), mpf(4), lambda z: 1 - mp.exp(-z), xx)] * 3
    return (1 - os2(gY)) - (1 - os2(gX))   # SY - SX for X_{n-1:n}
for xx in ['0.01', '0.1', '0.5', '1', '2', '5']:
    print('Cor3 delta(%s) =' % xx, mp.nstr(delta3(mpf(xx)), 8))
def delta3iv(xx):
    gx = [mprhrs_g(iv.mpf('0.5'), iv.mpf(1), iv.mpf(l), lambda z: 1 - iv.exp(-z/2), xx)
          for l in ['2','3','4']]
    gy = [mprhrs_g(iv.mpf('0.5'), iv.mpf(1), iv.mpf(4), lambda z: 1 - iv.exp(-z), xx)] * 3
    return (1 - os2(gy)) - (1 - os2(gx))
for xx in ['1/10', '1/2', '1']:
    print('Cor3 interval delta(%s) =' % xx, delta3iv(iv.mpf(xx)))
