"""For genuine cospherical zero 5-subsets, how many points of S lie on that sphere, and what are the
sphere denominators?  Compares against random 5-subsets' circumsphere denominators."""
import sys, os, random, collections
from fractions import Fraction
sys.path.insert(0, os.path.dirname(__file__))
import nrc, translate4, analyze_zeros as az

p = int(sys.argv[1]); seed = int(sys.argv[2]); A = translate4.TETRA if sys.argv[3] == "tetra" else translate4.AXES
mode = sys.argv[4] if len(sys.argv) > 4 else "nrc"; M = int(sys.argv[5]) if len(sys.argv) > 5 else p
rng = random.Random(seed)
S1 = nrc.points(nrc.random_curve(p, rng), p) if mode == "nrc" else [tuple(rng.randrange(p) for _ in range(3)) for _ in range(p)]
pts, base = translate4.build(S1, M, A)
zeros, summary = translate4.run_zero5(pts)
seen = {}; load = collections.Counter(); dens = collections.Counter()
for z in zeros:
    P5 = [pts[i] for i in z]
    if az.mechanism(P5) != "sphere5": continue
    sph = az.sphere(P5[:4]) or az.sphere(P5[1:]); c, r2 = sph
    key = (tuple(c), r2)
    if key in seen: continue
    on = [q for q in pts if sum((q[i]-c[i])**2 for i in range(3)) == r2]
    seen[key] = len(on); load[len(on)] += 1
    d = max(x.denominator for x in c); dens[d] += 1
print("p=%d M=%d mode=%s distinct genuine spheres=%d  points-of-S-on-sphere histogram=%s" % (p, M, mode, len(seen), dict(sorted(load.items()))))
print(" center denominators:", dict(sorted(dens.items())))
# random 5-subsets for comparison
rd = collections.Counter(); rs = random.Random(7)
for _ in range(2000):
    P5 = rs.sample(pts, 5); sph = az.sphere(P5[:4])
    if sph: rd[max(x.denominator for x in sph[0]) < 100] += 1
print(" random 5-subsets with small (<100) center denominator:", dict(rd))
big = sorted(seen.items(), key=lambda kv: -kv[1])[:3]
for (c, r2), k in big: print(" sphere center", [str(x) for x in c], "r2", r2, "carries", k, "points of S")
