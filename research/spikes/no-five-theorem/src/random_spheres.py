"""Structure of the zero hypergraph of a uniformly random m = gamma*N point set in [0,N)^3:
distinct spheres/planes carrying zero 5-subsets, how many points of S each carries, and the point-degree
distribution (how concentrated the zeros are).   Usage: random_spheres.py N gamma seed"""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import translate4, analyze_zeros as az
N = int(sys.argv[1]); gamma = float(sys.argv[2]); seed = int(sys.argv[3]); m = int(round(gamma * N))
rng = random.Random(seed); pts = set()
while len(pts) < m: pts.add(tuple(rng.randrange(N) for _ in range(3)))
pts = sorted(pts)
zeros, summary = translate4.run_zero5(pts, maxprint=10 ** 7)
deg = collections.Counter(i for z in zeros for i in z)
spheres = {}; planes = 0
for z in zeros:
    P5 = [pts[i] for i in z]
    if az.coplanar(P5): planes += 1; continue
    for k in range(5):
        sph = az.sphere([P5[j] for j in range(5) if j != k])
        if sph: break
    c, r2 = sph; key = (tuple(c), r2)
    if key not in spheres: spheres[key] = sum(1 for q in pts if sum((q[i] - c[i]) ** 2 for i in range(3)) == r2)
load = collections.Counter(spheres.values())
dh = collections.Counter(deg.values())
print("N=%d m=%d seed=%d %s coplanar-zeros=%d distinct-zero-spheres=%d points-on-sphere-hist=%s" % (N, m, seed, summary, planes, len(spheres), dict(sorted(load.items()))))
print("  point degrees (zeros per point): top10=%s  #points-with-degree>0=%d  hist=%s" % (sorted(deg.values(), reverse=True)[:10], len(deg), dict(sorted(dh.items()))))
