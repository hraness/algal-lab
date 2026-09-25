"""Sympy re-derivations of the identities used in the memo.
L1  Demonstrandum Lemma 1: det5(c+a,c-a,c+b,c-b,c+w) for the (2,2,1) symmetry class.
L3  Demonstrandum Lemma 3: det5(c+a,c-a,c+p,c+q,c+r) reduces to 2(|a|^2 (a.u) - a.w) form.
T   Twin-pair factorization: det5(P, P+m u, R, S, T) = m * det5'(sigma, P, R, S, T)
    with sigma = (u, 2u.P + m|u|^2, 0) the secant direction (a point at infinity).
TC  Twisted cubic: det5((t_i,t_i^2,t_i^3)) = V(t) (1 + h_2(t)).
"""
import sympy as sp

def lift(v):
    return list(v) + [sum(c**2 for c in v), 1]

def det5(pts):
    return sp.Matrix([lift(p) for p in pts]).det()

def sym(names):
    return sp.Matrix(sp.symbols(names))

c = sym('c1 c2 c3'); a = sym('a1 a2 a3'); b = sym('b1 b2 b3'); w = sym('w1 w2 w3')
p_ = sym('p1 p2 p3'); q = sym('q1 q2 q3'); r = sym('r1 r2 r3'); u = sym('u1 u2 u3')
m = sp.Symbol('m')

# L1: (2,2,1) class, points c+-a, c+-b, c+w
D = det5([c + a, c - a, c + b, c - b, c + w])
det3 = sp.Matrix.hstack(a, b, w).det()
L1 = sp.expand(D + 4 * (a.dot(a) - b.dot(b)) * det3)
print("L1 (2,2,1): det5(c+a,c-a,c+b,c-b,c+w) + 4(|a|^2-|b|^2) det3[a,b,w] ==", L1)

# L3: (2,1,1,1) class: det5(c+a, c-a, c+p, c+q, c+r).  Reported form: 2(|a|^2 (a.u) - a.w)
# where u, w are the cross-product/bracket data of p,q,r.  We derive the exact form.
D3 = sp.expand(det5([c + a, c - a, c + p_, c + q, c + r]))
# Try: D3 = -2 * ( |a|^2 * det3[a; q-p; r-p]-like )  -- solve by matching against candidates
cand_u = (q - p_).cross(r - p_)                       # normal of the plane p,q,r
cand_w = (p_.dot(p_) * (q.cross(r)) + q.dot(q) * (r.cross(p_)) + r.dot(r) * (p_.cross(q)))
expr = 2 * (a.dot(a) * a.dot(cand_u) - a.dot(cand_w))
diff = sp.expand(D3 - expr)
print("L3 (2,1,1,1): det5 - 2(|a|^2 a.u - a.w) with u=(q-p)x(r-p), w=sum |p|^2 (q x r) cyclic ==", diff)
if diff != 0:
    diff2 = sp.expand(D3 + expr)
    print("   with opposite sign ==", diff2)

# T: twin pair P, P+m u with any R,S,T (no symmetry assumed)
P = sym('P1 P2 P3'); R = sym('R1 R2 R3'); S = sym('S1 S2 S3'); T = sym('T1 T2 T3')
DT = det5([P, P + m * u, R, S, T])
sigma = list(u) + [2 * u.dot(P) + m * u.dot(u), 0]
M = sp.Matrix([lift(P), sigma, lift(R), lift(S), lift(T)])
print("T twin-pair: det5(P,P+mu,R,S,T) - m*det[P;sigma;R;S;T] ==", sp.expand(DT - m * M.det()))

# TC: twisted cubic
t = sp.symbols('t1:6')
DTC = det5([(ti, ti**2, ti**3) for ti in t])
V = sp.prod([t[j] - t[i] for i in range(5) for j in range(i + 1, 5)])
h2 = sum(t[i] * t[j] for i in range(5) for j in range(i, 5))
print("TC: det5(twisted cubic) - V*(1+h2) ==", sp.expand(DTC - V * (1 + h2)))
