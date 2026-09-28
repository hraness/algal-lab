"""Independent verification: doi:10.1007/s11587-026-01094-9 (7 refuted).

Model (fresh): T_i = J_i U_i, J_i~Ber(p_i), p_i = psi^{-1}(v_i).
S_{T_i}(x) = p_i Fbar(x;a_i).  min T_{1:n}: S = prod p_i Fbar_i.
max T_{n:n}: F = prod (1 - p_i Fbar_i).
Random N: F_{T_{N:N}} = sum_m P(N=m) F_{T_{m:m}}(x); S analog for min.
psi = 1/p (decr convex log-convex): p = 1/v.  Fbar(x;a)=e^{-a x}
(Kw-G with G=1-e^{-x},gamma=1 / scale family Fbar_0=e^{-x} / prop-hazard
all reduce to e^{-a x}).
Def 2.2 printed: a >=^w b iff ascending partial sums of a >= b's.
Claims all have direction T >=st T* (S_U-side >= S_V-side).
"""
import mpmath as mp
mp.mp.dps = 110


def asc_sup(a, b):
    A, B = sorted(map(mp.mpf, a)), sorted(map(mp.mpf, b))
    return all(sum(A[:k]) >= sum(B[:k]) - mp.mpf('1e-60')
               for k in range(1, len(A) + 1))


def asc_sub(a, b):
    A, B = sorted(map(mp.mpf, a)), sorted(map(mp.mpf, b))
    return all(sum(A[:k]) <= sum(B[:k]) + mp.mpf('1e-60')
               for k in range(1, len(A) + 1))


def in_M(v, a):
    n = len(v)
    return all((mp.mpf(v[i]) - mp.mpf(v[j])) * (mp.mpf(a[i]) - mp.mpf(a[j]))
               >= -mp.mpf('1e-60') for i in range(n) for j in range(n))


def S_min(vs, aa, t):
    t = mp.mpf(t)
    return mp.fprod((1 / mp.mpf(v)) * mp.e ** (-mp.mpf(a) * t)
                    for v, a in zip(vs, aa))


def S_max(vs, aa, t):
    t = mp.mpf(t)
    return 1 - mp.fprod(1 - (1 / mp.mpf(v)) * mp.e ** (-mp.mpf(a) * t)
                        for v, a in zip(vs, aa))


def S_randmax(vs, aa, pmf, t):
    return sum(mp.mpf(w) * S_max(vs[:m], aa[:m], t)
               for m, w in enumerate(pmf) if mp.mpf(w) != 0)


def scan(U, V, fun, hi='50', npts=400):
    neg = []
    for i in range(1, npts + 1):
        t = mp.mpf(hi) * i / (npts + 1)
        d = fun(*U, t) - fun(*V, t)
        if d < -mp.mpf('1e-60'):
            neg.append((t, d))
    return neg


print("===== Theorem 3.1: alpha >=^w beta => T_1:n >=st T* =====")
for v, a, b in [([3, 3], [3, 3], [2, 4]),
                ([2, 2, 2], [3, 3, 3], [2, 3, 4]),
                ([4, 4], [4, 4], [2, 5])]:
    print("inst", v, a, b, "premise asc_sup:", asc_sup(a, b),
          "M:", in_M(v, a), in_M(v, b))
    neg = scan((v, a), (v, b), S_min)
    print("   T>=st T* (S_U>=S_V):", "VIOLATED" if neg else "holds",
          [(mp.nstr(t, 5), mp.nstr(d, 6)) for t, d in neg[:2]], len(neg))
    t0 = mp.mpf('1e-12')
    print("   witness 1e-12:", mp.nstr(S_min(v, a, t0) - S_min(v, b, t0), 10))
    neg2 = scan((v, b), (v, a), S_min)
    print("   opposite T<=st T*:", "VIOLATED" if neg2 else "holds", len(neg2))

print("===== Theorem 3.2: psi(p) >=^w psi(p*), psi=1/p =====")
for v, u_, a in [([3, 3], [2, 4], [1, 1]),
                 ([4, 4], [2, 5], [1, 2]),
                 ([2, 2, 2], [1, 2, 3], [1, 1, 1])]:
    print("inst", v, u_, a, "premise:", asc_sup(v, u_),
          "M:", in_M(v, a), in_M(u_, a))
    neg = scan((v, a), (u_, a), S_min)
    print("   VIOLATED" if neg else "   holds",
          [(mp.nstr(t, 5), mp.nstr(d, 6)) for t, d in neg[:2]], len(neg))
    t0 = mp.mpf('1e-12')
    print("   witness 1e-12:", mp.nstr(S_min(v, a, t0) - S_min(u_, a, t0), 10))

print("===== Theorem 3.4: parallel max, row-weak-maj =====")
for v, u_, a, b in [([3, 3], [2, 4], [1, 1], ['0.5', '1.5']),
                    ([4, 4], [3, 5], [1, 3], ['0.5', '2.5']),
                    ([5, 5], [4, 6], [2, 3], [1, 3])]:
    print("inst", v, u_, a, b, "premise:", asc_sup(v, u_), asc_sup(a, b),
          "M:", in_M(v, a), in_M(u_, b))
    neg = scan((v, a), (u_, b), S_max)
    print("   T>=st T*:", "VIOLATED" if neg else "holds",
          [(mp.nstr(t, 5), mp.nstr(d, 6)) for t, d in neg[:2]], len(neg))
    t0 = mp.mpf('1e-12')
    print("   witness 1e-12:", mp.nstr(S_max(v, a, t0) - S_max(u_, b, t0), 10))
    neg2 = scan((u_, b), (v, a), S_max)
    print("   opposite:", "VIOLATED" if neg2 else "holds", len(neg2))

print("===== Theorem 3.5: random max, N1=2 <=st N2=3 =====")
pmf1, pmf2 = [0, 1], [0, 0, 1]
for v, u_, a, b in [([3, 3], [2, 4], [1, 1], ['0.5', '1.5']),
                    ([4, 4], [3, 5], [1, 3], ['0.5', '2.5']),
                    ([5, 5], [4, 6], [2, 3], [1, 3])]:
    print("inst", v, u_, a, b, "premise:", asc_sup(v, u_), asc_sup(a, b))
    U = (v, a, pmf1); V = (u_, b, pmf2)
    neg = scan(U, V, S_randmax)
    print("   T_N1:N1 >=st T_N2:N2*:", "VIOLATED" if neg else "holds",
          [(mp.nstr(t, 5), mp.nstr(d, 6)) for t, d in neg[:2]], len(neg))
    t0 = mp.mpf('1e-12')
    print("   witness 1e-12:",
          mp.nstr(S_randmax(v, a, pmf1, t0) - S_randmax(u_, b, pmf2, t0), 10))

print("===== Theorems 3.6/3.7/3.8 (families -> e^{-ax}) =====")
insts = [([3, 3], [2, 4], [1, 1], ['0.5', '1.5']),
         ([5, 5], [3, 6], [1, 2], ['0.5', '1.5'])]
for nm in ('3.6', '3.7', '3.8'):
    for v, u_, a, b in insts:
        print(nm, v, u_, a, b, "premise:", asc_sup(v, u_), asc_sup(a, b),
              "M:", in_M(v, a), in_M(u_, b))
        neg = scan((v, a, pmf1), (u_, b, pmf2), S_randmax)
        print("   ", "VIOLATED" if neg else "holds", len(neg),
              [(mp.nstr(t, 4), mp.nstr(d, 5)) for t, d in neg[:1]])
        t0 = mp.mpf('1e-12')
        print("   witness:", mp.nstr(S_randmax(v, a, pmf1, t0)
                                    - S_randmax(u_, b, pmf2, t0), 10))
