"""p-adic valuation profile of det5 over (2,1,1,1) configurations {P,P+pu,R,S,T}
of the translate construction, and a dump of genuine cospherical examples."""
import sys, os, random, collections, itertools
sys.path.insert(0, os.path.dirname(__file__))
import nrc, translate4, analyze_zeros as az

def det5(P5):
    a = P5[0]; L = [list(q) + [sum(c*c for c in q)] for q in P5]
    M = [[L[i][j] - L[0][j] for j in range(4)] for i in range(1, 5)]
    # 4x4 determinant by cofactor expansion
    def d3(m): return az.det3(m)
    s = 0
    for c in range(4):
        sub = [[M[r][j] for j in range(4) if j != c] for r in range(1, 4)]
        s += (-1)**c * M[0][c] * d3(sub)
    return s

p = int(sys.argv[1]); seed = int(sys.argv[2]); A = translate4.TETRA if sys.argv[3] == "tetra" else translate4.AXES
nsamp = int(sys.argv[4]) if len(sys.argv) > 4 else 200000
rng = random.Random(seed); V = nrc.random_curve(p, rng); S1 = nrc.points(V, p)
pts, base = translate4.build(S1, p, A)
bybase = collections.defaultdict(list)
for i, b in enumerate(base): bybase[b].append(i)
val = collections.Counter(); genuine = []
rs = random.Random(seed + 1)
for _ in range(nsamp):
    b0 = rs.randrange(len(S1)); i, j = rs.sample(bybase[b0], 2)
    others = rs.sample([b for b in bybase if b != b0], 3)
    k = [rs.choice(bybase[b]) for b in others]
    P5 = [pts[i], pts[j]] + [pts[x] for x in k]
    D = det5(P5)
    if D == 0:
        v = "zero"; genuine.append(P5)
    else:
        v = 0
        while D % p == 0: D //= p; v += 1
    val[v] += 1
print("p=%d valuation profile over %d sampled (2,1,1,1) configs:" % (p, nsamp), dict(sorted(val.items(), key=lambda kv: str(kv[0]))))
for P5 in genuine[:6]:
    mech = az.mechanism(P5)
    if mech == "sphere5":
        sph = az.sphere(P5[:4]) or az.sphere(P5[1:])
        print(" genuine", P5, "center", [str(c) for c in sph[0]], "r2", sph[1])
