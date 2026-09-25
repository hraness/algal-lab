"""Explicit arc family with fiber profile (1,3,3) on the paraboloid mod p (p = 1 mod 4):
   x = t,  y = (t*q(t) + r(t)) / (2t),  z = (t*q(t) - r(t)) / (2 i t),   t in F_p^*,
   q(t) = q2 t^2 + q1 t + q0,  r(t) = r2 t^2 + r1 t + r0,  i^2 = -1,  q2*r2*r0 != 0.
Homogeneous quartics: U = t s^3, X = t^2 s^2, Y = s^2 (t q + r)/2 (homogenized), Z likewise, W = t^3 s + q r.
Verified here: the residue set is a mod-p arc (exact 5x5 dets over Z are all nonzero via zero5),
x-fibers are 1, y- and z-fibers <= 3.  Usage: family133.py pmax [q2 q1 q0 r2 r1 r0]"""
import sys, os, subprocess, collections
HERE = os.path.dirname(os.path.abspath(__file__))

def sqrt_m1(p):
    for i in range(2, p):
        if (i * i + 1) % p == 0: return i
    return None

def points(p, q2=1, q1=0, q0=0, r2=1, r1=0, r0=1):
    i = sqrt_m1(p); inv2 = pow(2, -1, p); pts = []
    for t in range(1, p):
        q = (q2 * t * t + q1 * t + q0) % p; r = (r2 * t * t + r1 * t + r0) % p
        it = pow(t, -1, p)
        y = ((t * q + r) * inv2 * it) % p
        z = ((t * q - r) * inv2 * it * pow(i, -1, p)) % p
        pts.append((t, y, z))
    return pts

def zero5(pts):
    inp = "\n".join("%d %d %d" % q for q in pts) + "\n"
    out = subprocess.run([os.path.join(HERE, "zero5"), "5"], input=inp, capture_output=True, text=True).stdout
    return out.strip().splitlines()[-1]

if __name__ == "__main__":
    pmax = int(sys.argv[1]); coef = [int(a) for a in sys.argv[2:8]] or [1, 0, 0, 1, 0, 1]
    for p in range(5, pmax + 1):
        if any(p % d == 0 for d in range(2, int(p ** 0.5) + 1)) or p % 4 != 1: continue
        if (coef[0] * coef[3] * coef[5]) % p == 0: print(p, "degenerate coefficients, skipped"); continue
        S = points(p, *coef)
        fib = [max(collections.Counter(q[k] for q in S).values()) for k in range(3)]
        print("p=%d |S|=%d box=[0,%d)^3 fibers=%s %s" % (p, len(S), p, fib, zero5(S)), flush=True)
