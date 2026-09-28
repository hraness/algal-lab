"""Independent C3 check for refuted claims in doi:10.1007/s41060-022-00369-2.

Instance (v1,q1,a1) = (2,1,1) vs (v2,q2,a2) = (3,2,2) satisfies the printed
hypotheses v1<=v2, q1<=q2, a1<=a2.  mpmath (non-interval, 60 digits)
evaluation of each order expression at the witness x = 16/15 and neighbours.
"""
import mpmath as mp

mp.mp.dps = 60


def S(v, q, a, xx):
    G = 1 - mp.e ** (-q * xx) * (1 + q + q * xx) / (1 + q)
    return (v - v ** (G ** a)) / (v - 1)


def f(v, q, a, xx):
    h = mp.mpf("1e-30")
    return -(S(v, q, a, xx + h) - S(v, q, a, xx - h)) / (2 * h)


def dfdx(v, q, a, xx):
    h = mp.mpf("1e-20")
    return (f(v, q, a, xx + h) - f(v, q, a, xx - h)) / (2 * h)


P1 = (mp.mpf(2), mp.mpf(1), mp.mpf(1))
P2 = (mp.mpf(3), mp.mpf(2), mp.mpf(2))
for xx in [mp.mpf(16) / 15, mp.mpf(1), mp.mpf(2)]:
    SX, SY = S(*P1, xx), S(*P2, xx)
    fX, fY = f(*P1, xx), f(*P2, xx)
    dfX, dfY = dfdx(*P1, xx), dfdx(*P2, xx)
    E_st = SY - SX
    E_hr = fX * SY - fY * SX
    E_lr = dfY * fX - fY * dfX
    print(f"x={mp.nstr(xx,6)}: E_st={mp.nstr(E_st,10)} E_hr={mp.nstr(E_hr,10)} "
          f"E_lr={mp.nstr(E_lr,10)}")
