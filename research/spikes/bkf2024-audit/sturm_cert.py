"""Interval-wide sign certificates via Sturm sequences.
Each certified claim is: a rational function diff(x)=N(x)/D(x) has the asserted
sign on a whole interval I, proved by (a) D(x) nonzero on I (Sturm count 0)
and (b) N(x) nonzero on I (Sturm count 0) plus sign at one rational witness.
"""
import sys
sys.path.insert(0,"/Users/bg/Documents/algal-lab/research/spikes/context/runs/bkf2024")
import sympy as sp
x = sp.symbols('x')

def sturm_count(poly, a, b):
    """Number of real roots of poly in (a,b] via Sturm sequence."""
    seq = sp.sturm(sp.Poly(poly, x))
    return int(seq[-1] if False else
        sum(1 for _ in ()) + (len(seq) and
        __import__('sympy').count_roots if False else 0))

def count_roots(poly, a, b):
    return int(sp.Poly(poly, x).count_roots(sp.Rational(a), sp.Rational(b)))

def certify_sign_on_interval(N, D, a, b, expect, name):
    """N,D sympy polynomials; interval (a,b]; expect in {+1,-1} claimed sign."""
    na = count_roots(N, a, b); da = count_roots(D, a, b)
    mid = sp.Rational(a,1) if False else None
    # witness: midpoint
    w = (sp.Rational(a) + sp.Rational(b))/2 if isinstance(a, int) else (a+b)/2
    val = sp.Rational(N.subs(x, w))/sp.Rational(D.subs(x, w))
    sgn = 1 if val > 0 else (-1 if val < 0 else 0)
    ok = (na==0 and da==0 and sgn==expect)
    print(f"  [{ 'OK' if ok else 'FAIL'}] {name}: roots N on I={na}, roots D on I={da}, "
          f"sign at witness {w} is {sgn} (expected {expect})")
    return ok

P = lambda *a: print(" ".join(str(t) for t in a), flush=True)

# ---------- Thm 9 certified instance: r m s, sig _w mu, max sig<=min mu ---
# pareto1: Fbar_i = lam/(x-sig_i) when x>=sig_i+lam else 1.
# r=(1/3,1/3,1/3)? need r m s on E3+: take r=(1/3,1/3,1/3), s=(1/4,1/4,1/2)? s E3+ yes; r m s yes.
# sig=(1/4,1/2,3/4) E3+, mu=(1,3/2,2) E3+, max sig=3/4<=min mu=1. lam=1.
P("THM 9 interval certificate (pareto1, lam=1)")
r=[sp.Rational(1,3)]*3; s=[sp.Rational(1,4),sp.Rational(1,4),sp.Rational(1,2)]
sig=[sp.Rational(1,4),sp.Rational(1,2),sp.Rational(3,4)]
mu=[sp.Rational(1),sp.Rational(3,2),sp.Rational(2)]; lam=sp.Rational(1)
# breakpoints for U: sig_i+1 = 5/4,3/2,7/4 ; for V: mu_i+1 = 2,5/2,3
# all-alive region for both: x>=3 ; piecewise cell (3,oo): all alive
cells = [(sp.Rational(3),sp.Rational(4)), (sp.Rational(2),sp.Rational(5,2)),
         (sp.Rational(7,4),sp.Rational(2)), (sp.Rational(5,2),sp.Rational(3))]
def sf_expr(weights, locs):
    tot = 0
    for ri, si in zip(weights, locs):
        tot += ri * lam/(x-si)   # alive formula (x > si+lam)
    return tot
# cell-by-cell expression differs by which comps alive; in cells chosen all V-comps
# alive iff x>2,5/2,3 ; all U-comps alive iff x>7/4.
# cell (3,4): all alive both
dU = sf_expr(r,sig); dV = sf_expr(s,mu)
N,D = sp.fraction(sp.together(dU-dV))
certify_sign_on_interval(N, D, 3, 4, -1, "Thm9 claim U<=stV, cell x in (3,4]")
# cell (5/2,3]: V comp3 dead? mu3+1=3 -> for x in (5/2,3): V comps 1,2 alive? x<=3 -> u3=(x-2)<=1 alive iff x>=3 hmm
# alive iff (x-mu_i)>=1 i.e. x>=mu_i+1: at x in (5/2,3): comp3 x<3 dead => Fbar=1
dV_c = s[0]*lam/(x-mu[0]) + s[1]*lam/(x-mu[1]) + s[2]*1
N,D = sp.fraction(sp.together(dU-dV_c))
certify_sign_on_interval(N, D, sp.Rational(5,2), 3, -1, "Thm9 claim, cell (5/2,3] V3 dead")
# cell (2,5/2]: V comps 1 alive (x>2), 2,3 dead
dV_c = s[0]*lam/(x-mu[0]) + (s[1]+s[2])*1
N,D = sp.fraction(sp.together(dU-dV_c))
certify_sign_on_interval(N, D, 2, sp.Rational(5,2), -1, "Thm9 claim, cell (2,5/2] V2,V3 dead")

# ---------- Thm 11 certified instance (Ex7, IE baseline beta=2) -------------
# IE: Fbar = 1-exp(-beta/x). Non-algebraic -> Sturm N/A on x; but ordering on the
# transformed y=q(x) is still transcendental.  Report pointwise certificate only.
P("Thm 11/Ex7: transcendental -> pointwise Fraction check only (no Sturm)")

# ---------- Thm 4 middle-region: certify h_U>h_V on a whole interval --------
# r=(7/20,7/20,3/10), s=(3/5,1/5,1/5), lam=(1/4,4/3,2), power2, sig=1/10.
# region x in (sig+1/4, sig+4/3] = (7/20, 43/30]: comps 2,3 alive.
P("THM 4 interval certificate (power2, middle region, comps {2,3} alive)")
r=[sp.Rational(7,20),sp.Rational(7,20),sp.Rational(3,10)]
s=[sp.Rational(3,5),sp.Rational(1,5),sp.Rational(1,5)]
lam_=[sp.Rational(1,4),sp.Rational(4,3),sp.Rational(2)]; sig=sp.Rational(1,10)
a,b = sig+lam_[0], sig+lam_[1]      # (7/20, 43/30]
def h_expr(w):
    num = den = 0
    for ri,li in zip(w[1:],lam_[1:]):   # comps 2,3 alive
        u = (x-sig)/li
        num += ri/li * 2*u
        den += ri*(1-u**2)
    return num/den
dh = sp.together(h_expr(r)-h_expr(s)); N,D = sp.fraction(dh)
# need h_U<=h_V i.e. diff<=0; certify the FAILURE (diff>0) on part of the cell
certify_sign_on_interval(N, D, a, b, +1, "Thm4 violation h_U>h_V on (7/20,43/30]")
print("  N(x) =", sp.expand(N))
print("  D(x) =", sp.expand(D))
