"""Zero census of S1 + M*A for several shifts M (is the zero mechanism p-adic or geometric?)."""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(__file__))
import nrc, translate4, analyze_zeros as az

p = int(sys.argv[1]); seed = int(sys.argv[2]); A = translate4.TETRA if sys.argv[3] == "tetra" else translate4.AXES
mode = sys.argv[4] if len(sys.argv) > 4 else "nrc"
rng = random.Random(seed)
if mode == "nrc":
    V = nrc.random_curve(p, rng); S1 = nrc.points(V, p)
else:  # random base set with distinct coordinates in each axis (a 3-way graph) or fully random
    S1 = [tuple(rng.randrange(p) for _ in range(3)) for _ in range(p)]
for M in [p, p + 1, p + 3, 2 * p, 97]:
    pts, base = translate4.build(S1, M, A)
    zeros, summary = translate4.run_zero5(pts)
    out, ex = az.classify(pts, base, zeros)
    agg = collections.Counter()
    for (pat, mech), c in out.items(): agg[(len(pat), mech)] += c
    distinct = sum(c for (pat, mech), c in out.items() if len(pat) == 5)
    print("M=%d mode=%s |S|=%d %s distinct-base zeros=%d by (support,mech)=%s" % (M, mode, len(pts), summary, distinct, dict(sorted(agg.items()))))
