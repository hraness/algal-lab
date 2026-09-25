"""4-translate construction S = S1 + p*A (A = tetrahedron, box [0,2p)^3, |S| = 4|S1|) followed by greedy
hypergraph vertex-cover deletion (repeatedly delete the point lying in the most zero 5-subsets).  Also a
random baseline: 4p uniformly random points of [0,2p)^3.  Prints zero counts before deletion, the size of
the surviving valid set, and re-verifies the survivor with zero5.   Usage: greedy_delete.py p seed [nrc|random]"""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nrc, translate4

def greedy_cover(npts, zeros):
    alive = set(range(npts)); edges = [tuple(z) for z in zeros]; deleted = []
    while True:
        deg = collections.Counter()
        for e in edges:
            if all(v in alive for v in e):
                for v in e: deg[v] += 1
        if not deg: break
        v = max(deg, key=lambda k: (deg[k], -k)); alive.discard(v); deleted.append(v)
    return sorted(alive), deleted

if __name__ == "__main__":
    p = int(sys.argv[1]); seed = int(sys.argv[2]); mode = sys.argv[3] if len(sys.argv) > 3 else "nrc"
    M = int(round(float(sys.argv[4]) * 2 * p)) if len(sys.argv) > 4 else 4 * p
    rng = random.Random(seed)
    if mode == "nrc":
        S1 = nrc.points(nrc.random_curve(p, rng), p)
        pts, base = translate4.build(S1, p, translate4.TETRA)
    else:
        pts = list({tuple(rng.randrange(2 * p) for _ in range(3)) for _ in range(M)})
        while len(pts) < M: pts.append(tuple(rng.randrange(2 * p) for _ in range(3)))
        pts = sorted(set(pts))
    zeros, summary = translate4.run_zero5(pts, maxprint=10 ** 7)
    alive, deleted = greedy_cover(len(pts), zeros)
    surv = [pts[i] for i in alive]
    z2, s2 = translate4.run_zero5(surv, maxprint=10)
    print("p=%d n=%d mode=%s |S|=%d %s | greedy-deleted %d -> survivor %d (%.3f n), recheck %s" %
          (p, 2 * p, mode, len(pts), summary, len(deleted), len(surv), len(surv) / (2 * p), s2), flush=True)
