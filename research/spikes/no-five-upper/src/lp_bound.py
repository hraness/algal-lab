#!/usr/bin/env python3
"""lp_bound.py n SPHEREFILE -- certified LP upper bound for C(n).

Primal LP:  max sum_p x_p,  0 <= x_p <= 1,
   sum_{p in P} x_p <= 4  for every plane P with >= 5 grid points,
   sum_{p in S} x_p <= 4  for every sphere S with >= 5 grid points (from SPHEREFILE, see spheres.c),
   sum_{p in L} x_p <= 3  for every line L with >= 4 grid points,
   sum_{p in G} x_p <= 3  for every circle G with >= 4 grid points.
Every constraint holds for a no-five set with >= 5 points (kill lemma), so C(n) <= LP(n) <= any
dual value.  We solve with GLOP, then round the dual multipliers to rationals and evaluate the
dual objective exactly:  bound = sum_c rhs_c*y_c + sum_p max(0, 1 - sum_{c ∋ p} y_c),
which is a valid upper bound for every y >= 0 (weak duality with the box constraints).
"""
import sys, itertools
from fractions import Fraction
from math import gcd
from ortools.linear_solver import pywraplp

def int_rank(rows):
    """rank of an integer matrix (list of tuples), fraction-free Gaussian elimination"""
    m = [list(r) for r in rows]; rank = 0; ncol = len(m[0]) if m else 0
    for c in range(ncol):
        piv = next((i for i in range(rank, len(m)) if m[i][c] != 0), None)
        if piv is None: continue
        m[rank], m[piv] = m[piv], m[rank]
        for i in range(len(m)):
            if i != rank and m[i][c] != 0:
                f, g = m[i][c], m[rank][c]
                m[i] = [g * a - f * b for a, b in zip(m[i], m[rank])]
        rank += 1
    return rank

def lifted_affine_rank(pts, mem):
    p0 = pts[mem[0]]
    lift = lambda p: (p[0]-p0[0], p[1]-p0[1], p[2]-p0[2], p[0]**2+p[1]**2+p[2]**2-(p0[0]**2+p0[1]**2+p0[2]**2))
    return int_rank([lift(pts[i]) for i in mem[1:]])

def verify(pts, cons):
    """Every constraint (rhs 4) must be a set of points on a common sphere or plane
    (lifted affine rank <= 3); every constraint (rhs 3) a set on a common circle or line
    (lifted affine rank <= 2).  Both are then valid for no-five sets with >= 5 points."""
    for rhs, mem in cons:
        r = lifted_affine_rank(pts, mem)
        if (rhs == 4 and r > 3) or (rhs == 3 and r > 2):
            raise SystemExit(f"INVALID constraint rhs={rhs} rank={r} mem={mem}")
    return True

def build_constraints(n, spherefile):
    pts = [(x, y, z) for x in range(n) for y in range(n) for z in range(n)]
    idx = {p: i for i, p in enumerate(pts)}
    N = len(pts)
    cons = []  # (rhs, sorted tuple of point indices)
    seen = set()
    def sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
    def cross(u, v): return (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
    def dot(u, v): return u[0]*v[0]+u[1]*v[1]+u[2]*v[2]
    def prim(v):
        g = gcd(gcd(abs(v[0]), abs(v[1])), abs(v[2]))
        v = tuple(c // g for c in v)
        for c in v:
            if c != 0:
                return v if c > 0 else tuple(-x for x in v)
    # lines (>= 4 points)
    for a, b in itertools.combinations(range(N), 2):
        d = prim(sub(pts[b], pts[a]))
        # base: the member with smallest index; key = (d, member set)
        mem = tuple(sorted(idx[p] for p in pts if cross(sub(p, pts[a]), d) == (0, 0, 0)))
        if len(mem) >= 4 and ('L', mem) not in seen:
            seen.add(('L', mem)); cons.append((3, mem))
    # planes: member lists of every plane with >= 4 grid points; constraint if >= 5
    planes = {}
    for a, b, c in itertools.combinations(range(N), 3):
        nv = cross(sub(pts[b], pts[a]), sub(pts[c], pts[a]))
        if nv == (0, 0, 0): continue
        nv = prim(nv); dd = dot(nv, pts[a])
        if (nv, dd) in planes: continue
        mem = tuple(i for i, p in enumerate(pts) if dot(nv, p) == dd)
        planes[(nv, dd)] = mem
        if len(mem) >= 5: cons.append((4, mem))
    # circles (>= 4 points): circumcircle of every non-collinear triple inside a plane,
    # keyed by (plane, D, D*centre, D^2*radius^2) in lowest terms; membership tested with integers only.
    # (An earlier version omitted the radius from the key and silently dropped concentric circles;
    #  xcheck_circles.py / the brute-force comparison in xcheck_circles.py caught it.)
    for (nv, dd), pm in planes.items():
        if len(pm) < 4: continue
        for a, b, c in itertools.combinations(pm, 3):
            A, B, C = pts[a], pts[b], pts[c]
            u, v = sub(B, A), sub(C, A); w = cross(u, v)
            if w == (0, 0, 0): continue
            uu, vv = dot(u, u), dot(v, v)
            num = cross(tuple(uu*v[i] - vv*u[i] for i in range(3)), w); D = 2*dot(w, w)
            oi = tuple(D*A[i] + num[i] for i in range(3))
            g = gcd(gcd(gcd(D, abs(oi[0])), abs(oi[1])), abs(oi[2]))
            D2 = D // g; o2 = tuple(t // g for t in oi)
            R2 = sum((D2*A[i] - o2[i])**2 for i in range(3))
            key = ('C', nv, dd, D2, o2, R2)   # centre AND radius: concentric circles share a centre
            if key in seen: continue
            seen.add(key)
            mem = tuple(i for i in pm if sum((D2*pts[i][k] - o2[k])**2 for k in range(3)) == R2)
            if len(mem) >= 4: cons.append((3, mem))
    # spheres (>= 5 points) from spheres.c output
    nsph = 0
    for line in open(spherefile):
        f = list(map(int, line.split()))
        if f[0] >= 5: cons.append((4, tuple(f[1:]))); nsph += 1
    return pts, cons, nsph

def main():
    n = int(sys.argv[1]); spherefile = sys.argv[2]
    pts, cons, nsph = build_constraints(n, spherefile); N = len(pts)
    verify(pts, cons)
    kinds = {}
    for rhs, mem in cons: kinds[rhs] = kinds.get(rhs, 0) + 1
    mx3 = max((len(mem) for rhs, mem in cons if rhs == 3), default=0)
    mx4 = max((len(mem) for rhs, mem in cons if rhs == 4), default=0)
    print(f"n={n} points={N} constraints={len(cons)} (spheres {nsph}; rhs-4 constraints {kinds.get(4,0)}, rhs-3 constraints {kinds.get(3,0)}); "
          f"max points on one rhs-3 set (circle/line) {mx3}, on one rhs-4 set (sphere/plane) {mx4}; all constraints verified valid by exact lifted-rank check")
    solver = pywraplp.Solver.CreateSolver('GLOP')
    x = [solver.NumVar(0, 1, f'x{i}') for i in range(N)]
    rows = []
    for rhs, mem in cons:
        ct = solver.Constraint(-solver.infinity(), rhs)
        for i in mem: ct.SetCoefficient(x[i], 1)
        rows.append(ct)
    solver.Maximize(sum(x))
    st = solver.Solve()
    assert st == pywraplp.Solver.OPTIMAL
    val = solver.Objective().Value()
    # exact dual certificate
    y = [Fraction(max(0.0, r.dual_value())).limit_denominator(10**6) for r in rows]
    cover = [Fraction(0)] * N
    for (rhs, mem), yc in zip(cons, y):
        if yc:
            for i in mem: cover[i] += yc
    bound = sum(rhs * yc for (rhs, mem), yc in zip(cons, y)) + sum(max(Fraction(0), 1 - cv) for cv in cover)
    print(f"GLOP primal value = {val:.6f}; certified dual bound = {bound} ~ {float(bound):.6f}; "
          f"so C({n}) <= {int(bound)}  (4n = {4*n})")

if __name__ == '__main__':
    main()
