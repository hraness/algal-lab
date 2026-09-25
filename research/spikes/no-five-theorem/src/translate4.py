"""Test S = S_1 + p*A for an NRC residue set S_1 in [0,p)^3 and A subset {0,1}^3.
Reports zero-determinant 5-subsets classified by their residue-class pattern.
Usage: translate4.py p seed A [cubic] with A in {axes, tetra}."""
import random, subprocess, sys, os, collections
sys.path.insert(0, os.path.dirname(__file__))
import nrc

HERE = os.path.dirname(os.path.abspath(__file__))
AXES = [(0,0,0),(1,0,0),(0,1,0),(0,0,1)]
TETRA = [(0,0,0),(1,1,0),(1,0,1),(0,1,1)]

def build(S1, p, A, allowed=None):
    pts, base = [], []
    for i, P in enumerate(S1):
        for a in A:
            if allowed is None or allowed(P, a):
                pts.append((P[0] + p*a[0], P[1] + p*a[1], P[2] + p*a[2])); base.append(i)
    return pts, base

def run_zero5(pts, maxprint=100000):
    inp = "\n".join("%d %d %d" % q for q in pts) + "\n"
    out = subprocess.run([os.path.join(HERE, "zero5"), str(maxprint)], input=inp, capture_output=True, text=True).stdout
    zeros = [tuple(map(int, l.split()[1:])) for l in out.splitlines() if l.startswith("zero ")]
    summary = out.strip().splitlines()[-1]
    return zeros, summary

def max_fiber(S1):
    return [max(collections.Counter(P[c] for P in S1).values()) for c in range(3)]

if __name__ == "__main__":
    p = int(sys.argv[1]); seed = int(sys.argv[2]); A = AXES if sys.argv[3] == "axes" else TETRA
    rng = random.Random(seed)
    V = nrc.random_curve(p, rng, quartic=not (len(sys.argv) > 4 and sys.argv[4] == "cubic"))
    S1 = nrc.points(V, p)
    pts, base = build(S1, p, A)
    zeros, summary = run_zero5(pts)
    pat = collections.Counter()
    for z in zeros:
        pat[tuple(sorted(collections.Counter(base[i] for i in z).values(), reverse=True))] += 1
    print("p=%d seed=%d A=%s |S1|=%d fibers=%s |S|=%d %s patterns=%s" % (p, seed, sys.argv[3], len(S1), max_fiber(S1), len(pts), summary, dict(pat)))
