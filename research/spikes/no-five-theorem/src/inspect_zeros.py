"""Print sample zero 5-subsets of the 4-translate construction with geometry (coplanar? sphere?)."""
import random, sys, os, collections
sys.path.insert(0, os.path.dirname(__file__))
import nrc, translate4
from fractions import Fraction

def coplanar(pts):
    a = pts[0]; M = [[q[i]-a[i] for i in range(3)] for q in pts[1:]]
    # rank of the 4x3 matrix < 3
    import itertools
    def det3(m): return (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])-m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])+m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))
    return all(det3([M[i] for i in c]) == 0 for c in itertools.combinations(range(4), 3))

p = int(sys.argv[1]); seed = int(sys.argv[2]); A = translate4.AXES if sys.argv[3] == "axes" else translate4.TETRA
want = sys.argv[4] if len(sys.argv) > 4 else None
rng = random.Random(seed); V = nrc.random_curve(p, rng); S1 = nrc.points(V, p)
pts, base = translate4.build(S1, p, A)
zeros, summary = translate4.run_zero5(pts)
shown = collections.Counter()
for z in zeros:
    pat = tuple(sorted(collections.Counter(base[i] for i in z).values(), reverse=True))
    key = str(pat)
    if want and key != want: continue
    if shown[key] >= 4: continue
    shown[key] += 1
    P = [pts[i] for i in z]
    print(pat, "bases", [base[i] for i in z], "pts", P, "coplanar" if coplanar(P) else "cospherical")
