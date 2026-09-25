"""Classify zero 5-subsets of a translate construction by geometric mechanism."""
import itertools, collections
from fractions import Fraction

def det3(m):
    return (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])-m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])+m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))

def lifted_rank_le3(P4):
    a = P4[0]; D = [[q[i]-a[i] for i in range(3)] + [sum(q[i]**2 for i in range(3)) - sum(a[i]**2 for i in range(3))] for q in P4[1:]]
    for cols in itertools.combinations(range(4), 3):
        if det3([[row[c] for c in cols] for row in D]) != 0: return False
    return True

def collinear(P3):
    a, b, c = P3; u = [b[i]-a[i] for i in range(3)]; v = [c[i]-a[i] for i in range(3)]
    cr = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
    return cr == [0, 0, 0]

def coplanar(P):
    a = P[0]; M = [[q[i]-a[i] for i in range(3)] for q in P[1:]]
    return all(det3([M[i] for i in c]) == 0 for c in itertools.combinations(range(len(M)), 3))

def sphere(P4):
    """center (Fractions) and r^2 of the sphere through 4 non-coplanar points, else None."""
    a = P4[0]; A = [[2*(q[i]-a[i]) for i in range(3)] for q in P4[1:]]
    rhs = [sum(q[i]**2 for i in range(3)) - sum(a[i]**2 for i in range(3)) for q in P4[1:]]
    D = det3(A)
    if D == 0: return None
    c = []
    for i in range(3):
        M = [row[:] for row in A]
        for r in range(3): M[r][i] = rhs[r]
        c.append(Fraction(det3(M), D))
    r2 = sum((c[i]-a[i])**2 for i in range(3))
    return c, r2

def mechanism(P5):
    if any(collinear(t) for t in itertools.combinations(P5, 3)): return "collinear3"
    if any(lifted_rank_le3(q) for q in itertools.combinations(P5, 4)): return "concyclic4"
    if coplanar(P5): return "coplanar5"
    return "sphere5"

def classify(pts, base, zeros):
    out = collections.Counter(); examples = {}
    for z in zeros:
        P5 = [pts[i] for i in z]
        pat = tuple(sorted(collections.Counter(base[i] for i in z).values(), reverse=True))
        mech = mechanism(P5); key = (pat, mech); out[key] += 1
        if key not in examples: examples[key] = (P5, [base[i] for i in z])
    return out, examples

if __name__ == "__main__":
    import sys, os, random
    sys.path.insert(0, os.path.dirname(__file__))
    import nrc, translate4
    p = int(sys.argv[1]); seed = int(sys.argv[2]); A = translate4.AXES if sys.argv[3] == "axes" else translate4.TETRA
    rng = random.Random(seed); V = nrc.random_curve(p, rng); S1 = nrc.points(V, p)
    pts, base = translate4.build(S1, p, A)
    zeros, summary = translate4.run_zero5(pts)
    out, ex = classify(pts, base, zeros)
    for k in sorted(out): print(k, out[k])
    for k in sorted(ex):
        if k[1] == "sphere5":
            P5, b = ex[k]; sph = sphere(P5[:4]) or sphere(P5[1:])
            print("example", k, b, P5, "center", [str(c) for c in sph[0]], "r2", sph[1])
