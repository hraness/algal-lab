"""Zero census for uniformly random m = gamma*N point sets in [0,N)^3, by mechanism (collinear3 / concyclic4 /
coplanar5 / sphere5).  Tests the scaling of the number of bad 5-subsets with N (n^10 => constant, n^11 => linear).
Usage: random_census.py N gamma seed"""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import translate4, analyze_zeros as az
N = int(sys.argv[1]); gamma = float(sys.argv[2]); seed = int(sys.argv[3]); m = int(round(gamma * N))
rng = random.Random(seed); pts = set()
while len(pts) < m: pts.add(tuple(rng.randrange(N) for _ in range(3)))
pts = sorted(pts)
zeros, summary = translate4.run_zero5(pts, maxprint=10 ** 7)
cen = collections.Counter(az.mechanism([pts[i] for i in z]) for z in zeros)
print("N=%d m=%d gamma=%.2f seed=%d %s census=%s" % (N, m, gamma, seed, summary, dict(sorted(cen.items()))), flush=True)
