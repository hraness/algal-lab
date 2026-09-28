"""Independent check: doi:10.21136/am.2018.0105-17 Theorem 3.5(a).

NP(a,b): F(x)=(x^a-b^a)/(x^a+b^a), S(x)=2b^a/(x^a+b^a), x>b.
Component hazard r(x)=a x^{a-1}/(x^a+b^a); series hazard = sum_i r_i.
Claim (a): 0<a<=1, beta >=m beta* => X1:n >=fr Y1:n  (r_X <= r_Y).
Own Thm 3.1(b): same premise, X1:n <=st Y1:n (S_X <= S_Y) for all a>0.
"""
import mpmath as mp

mp.mp.dps = 110


def r_i(b, x, a):
    b, x, a = mp.mpf(b), mp.mpf(x), mp.mpf(a)
    return a * x ** (a - 1) / (x ** a + b ** a)


def rS(betas, x, a):
    return sum(r_i(b, x, a) for b in betas)


def S_i(b, x, a):
    b, x, a = mp.mpf(b), mp.mpf(x), mp.mpf(a)
    return 2 * b ** a / (x ** a + b ** a)


def SS(betas, x, a):
    return mp.fprod(S_i(b, x, a) for b in betas)


pairs = [([mp.mpf('0.1'), 1, 9], [mp.mpf('0.1'), 4, 6]),
         ([1, 2, 7], [3, 3, 4])]
for b, bs in pairs:
    sb, sbs = sorted(map(mp.mpf, b)), sorted(map(mp.mpf, bs))
    ok = abs(sum(sb) - sum(sbs)) < mp.mpf('1e-40') and all(
        sum(sbs[:l]) >= sum(sb[:l]) for l in range(1, len(sb)))
    print(f"beta={b} beta*={bs}: beta >=m beta* = {ok}")

for a in ('0.5', '0.8', '1.0'):
    for b, bs in pairs:
        lo = max(max(b), max(bs))
        # scan x just above lo and beyond
        rows = []
        for t in ('0.000000000001', '0.000001', '0.001', '0.01', '0.5', '1', '5', '50'):
            x = mp.mpf(lo) + mp.mpf(t)
            d = rS(b, x, a) - rS(bs, x, a)
            rows.append((t, d))
        claimed_ok = all(d <= mp.mpf('1e-60') for _, d in rows)   # r_X <= r_Y
        opposite_ok = all(d >= -mp.mpf('1e-60') for _, d in rows)
        print(f"a={a} beta={b} vs {bs}: r_X - r_Y by offset:")
        for t, d in rows:
            print(f"    x=max+{t}: {mp.nstr(d, 12)}")
        print(f"    claim X>=hrY (rX<=rY): {claimed_ok}; opposite X<=hrY: {opposite_ok}")
        # st check: claim of Thm 3.1(b): S_X <= S_Y
        st_ok = all(SS(b, mp.mpf(lo) + mp.mpf(t), a) <= SS(bs, mp.mpf(lo) + mp.mpf(t), a) + mp.mpf('1e-60')
                    for t in ('0.001', '0.5', '1', '5', '50'))
        print(f"    Thm3.1(b) X<=stY (S_X<=S_Y): {st_ok}")
