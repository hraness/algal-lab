#!/usr/bin/env python3
"""brute.py -- exact small-n verification of the decomposition identities.

For n given: enumerate all 4-subsets of [0,n)^3 (points numbered lexicographically).
- count coplanar4, concyclic4, collinear4, noncoplanar4 (== accepted bases)
- for each non-coplanar 4-subset: sphere = unique; count extras; split extras into
  circ (x coplanar with a base triple -> {base,x} has a concyclic 4-subset) / irr.
- enumerate all 5-subsets: classify degenerate via det5; coplanar (rank<=2);
  cospherical non-coplanar; among those: # containing a concyclic 4-subset (Z_circ),
  irreducible (Z_irr); and count valid bases per subset.
Check: E*B = sum extras; 4*Z_circ = sum kc; 5*Z_irr = sum ki; Z_sphere = Z_circ+Z_irr.
"""
import sys
from itertools import combinations
from fractions import Fraction

n = int(sys.argv[1])
SKIP_EXTRAS = len(sys.argv) > 2 and sys.argv[2] == "skip"
G = [(x, y, z) for x in range(n) for y in range(n) for z in range(n)]
N = len(G)


def det3(a, b, c):
    return (a[0] * (b[1] * c[2] - b[2] * c[1])
            - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0]))


def coplanar(P):
    d = [[P[i + 1][j] - P[0][j] for j in range(3)] for i in range(3)]
    return det3(d[0], d[1], d[2]) == 0


def det5(P):
    M = [[Fraction(P[i][j]) for j in range(3)] +
         [Fraction(sum(x * x for x in P[i])), Fraction(1)] for i in range(5)]
    # bareiss
    M = [row[:] for row in M]
    sgn = 1
    for col in range(5):
        piv = None
        for r in range(col, 5):
            if M[r][col] != 0:
                piv = r
                break
        if piv is None:
            return Fraction(0)
        if piv != col:
            M[col], M[piv] = M[piv], M[col]
            sgn = -sgn
        pv = M[col][col]
        for r in range(col + 1, 5):
            f = M[r][col]
            if f == 0:
                continue
            for c in range(col, 5):
                M[r][c] = M[r][c] * pv - M[col][c] * f
                if col > 0:
                    M[r][c] /= prev
        prev = pv
    return M[4][4] * sgn


def det5fast(P):
    # det of lifted rows (x,y,z,|p|^2,1) == -det of 4x4 (P_i-P_0, |P_i|^2-|P_0|^2)
    d = [[P[i][j] - P[0][j] for j in range(3)] +
         [sum(P[i][x] * P[i][x] - P[0][x] * P[0][x] for x in range(3))] for i in range(1, 5)]
    return (d[0][0] * (d[1][1] * (d[2][2] * d[3][3] - d[2][3] * d[3][2])
                       - d[1][2] * (d[2][1] * d[3][3] - d[2][3] * d[3][1])
                       + d[1][3] * (d[2][1] * d[3][2] - d[2][2] * d[3][1]))
            - d[0][1] * (d[1][0] * (d[2][2] * d[3][3] - d[2][3] * d[3][2])
                         - d[1][2] * (d[2][0] * d[3][3] - d[2][3] * d[3][0])
                         + d[1][3] * (d[2][0] * d[3][2] - d[2][2] * d[3][0]))
            + d[0][2] * (d[1][0] * (d[2][1] * d[3][3] - d[2][3] * d[3][1])
                         - d[1][1] * (d[2][0] * d[3][3] - d[2][3] * d[3][0])
                         + d[1][3] * (d[2][0] * d[3][1] - d[2][1] * d[3][0]))
            - d[0][3] * (d[1][0] * (d[2][1] * d[3][2] - d[2][2] * d[3][1])
                         - d[1][1] * (d[2][0] * d[3][2] - d[2][2] * d[3][0])
                         + d[1][2] * (d[2][0] * d[3][1] - d[2][1] * d[3][0])))


def concyclic4(P):
    if not coplanar(P):
        return False
    d = [[P[i + 1][j] - P[0][j] for j in range(3)] for i in range(3)]
    R = [sum(x * x for x in P[i + 1]) - sum(x * x for x in P[0]) for i in range(3)]
    # left kernel nu of A (rows d_i): nu = cross of two independent COLUMNS
    w = [[d[i][j] for i in range(3)] for j in range(3)]
    pairs = [(0, 1), (0, 2), (1, 2)]
    for i, j in pairs:
        nu = [w[i][1] * w[j][2] - w[i][2] * w[j][1],
              w[i][2] * w[j][0] - w[i][0] * w[j][2],
              w[i][0] * w[j][1] - w[i][1] * w[j][0]]
        if any(nu):
            return nu[0] * R[0] + nu[1] * R[1] + nu[2] * R[2] == 0
    return False  # all parallel: 4 collinear


copl4 = circ4 = coll4 = valid4 = 0
sumk = sumkc = sumki = 0
for q in combinations(range(N), 4):
    P = [G[i] for i in q]
    d = [[P[i + 1][j] - P[0][j] for j in range(3)] for i in range(3)]
    det = det3(d[0], d[1], d[2])
    if det == 0:
        copl4 += 1
        if concyclic4(P):
            circ4 += 1
        continue
    valid4 += 1
    if SKIP_EXTRAS:
        continue
    # circumsphere via Fractions (reuse xcheck logic inline)
    M = [[2 * (P[i + 1][j] - P[0][j]) for j in range(3)] for i in range(3)]
    r = [sum(x * x for x in P[i + 1]) - sum(x * x for x in P[0]) for i in range(3)]
    DD = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])
          - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
          + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
    Cof = [[0] * 3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            mn = [[M[x][y] for y in range(3) if y != j] for x in range(3) if x != i]
            Cof[i][j] = ((-1) ** (i + j)) * (mn[0][0] * mn[1][1] - mn[0][1] * mn[1][0])
    cc = [Fraction(sum(Cof[j][i] * r[j] for j in range(3)), DD) for i in range(3)]
    R2 = sum((Fraction(P[0][j]) - cc[j]) ** 2 for j in range(3))
    kc = ki = 0
    tri = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    bset = set(P)
    for p in G:
        if p in bset:
            continue
        if sum((Fraction(p[j]) - cc[j]) ** 2 for j in range(3)) != R2:
            continue
        kc_this = False
        for t_ in tri:
            A, Bx, Cx = P[t_[0]], P[t_[1]], P[t_[2]]
            if det3([Bx[0] - A[0], Bx[1] - A[1], Bx[2] - A[2]],
                    [Cx[0] - A[0], Cx[1] - A[1], Cx[2] - A[2]],
                    [p[0] - A[0], p[1] - A[1], p[2] - A[2]]) == 0:
                kc_this = True
                break
        if kc_this:
            kc += 1
        else:
            ki += 1
    sumk += kc + ki
    sumkc += kc
    sumki += ki

# 5-subset census
Zsphere = Zcirc = Zirr = Zplane = 0
wbases = {}
for q in combinations(range(N), 5):
    P = [G[i] for i in q]
    # rank of 4 diffs
    d = [[P[i][j] - P[0][j] for j in range(3)] for i in range(1, 5)]
    rankle2 = all(det3(*[d[i] for i in tr]) == 0 for tr in combinations(range(4), 3))
    if rankle2:
        Zplane += 1
        continue
    if det5fast(P) != 0:
        continue  # non-degenerate
    Zsphere += 1
    hascirc = any(concyclic4([P[i] for i in qq]) for qq in combinations(range(5), 4))
    vb = sum(1 for qq in combinations(range(5), 4)
             if det3(*[[P[i][j] - P[qq[0]][j] for j in range(3)] for i in qq[1:]]) != 0)
    wbases[vb] = wbases.get(vb, 0) + 1
    if hascirc:
        Zcirc += 1
    else:
        Zirr += 1

E = sumk / valid4
print(f"n={n} N={N}")
print(f"4-subsets: coplanar={copl4} concyclic={circ4} noncopl(valid)={valid4}")
print(f"E={E:.6f} sum_extras={sumk} sum_kc={sumkc} sum_ki={sumki}")
print(f"5-subsets: Zplane={Zplane} Zsphere={Zsphere} Zcirc={Zcirc} Zirr={Zirr}")
print(f"check: 4*Zcirc={4*Zcirc} vs sum_kc={sumkc}; 5*Zirr={5*Zirr} vs sum_ki={sumki}")
print(f"       Zcirc_est=n^3*Ncirc4-ish={circ4 * N}  vs true Zcirc={Zcirc}")
print(f"valid-bases-per-subset hist: {wbases}")
