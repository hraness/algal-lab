"""C3 for doi_10.1007/s44199-026-00167-w: GTL-HT-G shape-parameter ordering.
Independent check (pure mpmath, no symbolic differentiation).

From the paper's pdf, f_i(x) ∝ Gamma(d_i)^{-1} * L(x)^{d_i-1} * g(x), with
L(x) = -b*log(1-U_G(x)) and shared theta,b,psi: the ratio
    f_{X2}/f_{X1}(x) = const * L(x)^{d2-d1}
and L(x) is increasing.  For the claim X1 <=lr X2 with d1>d2 the ratio must
be NONDECREASING, but d2-d1<0 makes it strictly decreasing -> refuted.
We verify L increasing and the ratio decreasing at rational points with
interval arithmetic; baseline G=1-e^{-x} -> 1-U_G = (e^{-x}/(th+(1-th)e^{-x}))^{2 th}.
"""
from mpmath import mp, mpf, iv

mp.dps = 80; iv.dps = 80


def Lfun(b, th, xx, L):
    D = th + (1 - th) * L.exp(-xx)
    return 2 * b * th * (xx + L.log(D))


def ratio(d1, d2, b, th, xx, L):
    return Lfun(b, th, xx, L) ** (d2 - d1)


for (b, th) in [(mpf(1), mpf(1)), (mpf(2), mpf(2)), (mpf('0.5'), mpf(3))]:
    pts = [mpf('1e-6'), mpf('1e-4'), mpf('0.01'), mpf('0.1'), mpf('0.5'), mpf(1), mpf(2)]
    Ls = [Lfun(b, th, t, mp) for t in pts]
    print('b,th=', b, th, 'L increasing:', all(a < c for a, c in zip(Ls, Ls[1:])))
    rr = [ratio(2, 1, b, th, t, mp) for t in pts]
    print('   f2/f1 (d1=2,d2=1):', [mp.nstr(v, 6) for v in rr],
          'strictly decreasing:', all(a > c for a, c in zip(rr, rr[1:])))
# interval confirm: ratio strictly decreasing across [0.01, 0.1]
r1 = ratio(2, 1, iv.mpf(1), iv.mpf(1), iv.mpf('0.01'), iv)
r2 = ratio(2, 1, iv.mpf(1), iv.mpf(1), iv.mpf('0.1'), iv)
print('iv: r(0.01) - r(0.1) =', mp.nstr((r1 - r2).a, 8), '(lower bound>0 iff strictly decreasing)')
