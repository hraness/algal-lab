"""Normal rational curves on the paraboloid w = x^2+y^2+z^2 over F_p.

A curve t -> (x(t), y(t), z(t)) with deg <= 4 and x^2+y^2+z^2 of degree <= 4
(mod p) whose lifted vectors (x,y,z,w,1) span the degree-<=4 polynomials is a
normal rational curve in PG(4,p) lying on the paraboloid; every 5 of its points
are linearly independent mod p (Vandermonde).  This module finds such curves by
random search and returns the residue point sets in [0,p)^3.
"""
import random

def modinv(a, p):
    return pow(a % p, p - 2, p)

def isotropic(p, rng):
    """Random nonzero v in F_p^3 with v.v = 0."""
    while True:
        a = rng.randrange(p); b = rng.randrange(p)
        s = (-(a * a + b * b)) % p
        # need c^2 = s
        c = pow(s, (p + 1) // 4, p) if p % 4 == 3 else None
        if p % 4 == 1:
            # Tonelli via brute force for small p
            c = next((x for x in range(p) if x * x % p == s), None)
        if c is not None and c * c % p == s and (a, b, c) != (0, 0, 0):
            return (a, b, c)

def dot(u, v, p):
    return sum(a * b for a, b in zip(u, v)) % p

def solve_linear(v, rhs, p, rng):
    """Random u with v.u = rhs (mod p), v != 0."""
    k = next(i for i in range(3) if v[i] % p)
    u = [rng.randrange(p) for _ in range(3)]
    s = sum(v[i] * u[i] for i in range(3) if i != k) % p
    u[k] = (rhs - s) * modinv(v[k], p) % p
    return tuple(u)

def det_mod(M, p):
    M = [row[:] for row in M]; n = len(M); d = 1
    for c in range(n):
        piv = next((r for r in range(c, n) if M[r][c] % p), None)
        if piv is None: return 0
        if piv != c: M[c], M[piv] = M[piv], M[c]; d = -d
        d = d * M[c][c] % p; inv = modinv(M[c][c], p)
        for r in range(c + 1, n):
            f = M[r][c] * inv % p
            if f:
                for j in range(c, n): M[r][j] = (M[r][j] - f * M[c][j]) % p
    return d % p

def random_curve(p, rng, quartic=True):
    """Coefficient vectors v0..v4 (each in F_p^3) of an NRC on the paraboloid."""
    for _ in range(1000):
        if quartic:
            v4 = isotropic(p, rng)
            v3 = solve_linear(v4, 0, p, rng)
            v2 = solve_linear(v4, (-dot(v3, v3, p)) * modinv(2, p), p, rng)
            v1 = solve_linear(v4, -dot(v3, v2, p), p, rng)
        else:
            v4 = (0, 0, 0)
            v3 = isotropic(p, rng)
            v2 = solve_linear(v3, 0, p, rng)
            v1 = tuple(rng.randrange(p) for _ in range(3))
        v0 = tuple(rng.randrange(p) for _ in range(3))
        V = [v0, v1, v2, v3, v4]
        w = [0] * 9
        for i in range(5):
            for j in range(5):
                w[i + j] = (w[i + j] + dot(V[i], V[j], p)) % p
        assert all(c == 0 for c in w[5:]), "degree of |.|^2 exceeds 4"
        rows = [[1, 0, 0, 0, 0]] + [[V[k][c] for k in range(5)] for c in range(3)] + [w[:5]]
        if det_mod(rows, p):
            return V

def points(V, p):
    """Residue points (x,y,z) in [0,p)^3 for t in F_p (t = infinity dropped)."""
    out = []
    for t in range(p):
        pt = tuple(sum(V[k][c] * pow(t, k, p) for k in range(5)) % p for c in range(3))
        out.append(pt)
    return out

if __name__ == "__main__":
    import sys
    p = int(sys.argv[1]); seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    rng = random.Random(seed)
    V = random_curve(p, rng, quartic=(len(sys.argv) <= 3 or sys.argv[3] != "cubic"))
    print("V =", V)
    for x, y, z in points(V, p): print(x, y, z)
