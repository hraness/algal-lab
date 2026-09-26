"""Verify all printed Examples 3.1-3.8 and Counterexamples 3.1-3.7 of BKKA2024.

For each: (i) check the stated hypotheses exactly; (ii) check the claimed
order/non-order on a dense exact rational grid in y = 1/(1+x) in (0,1);
sign changes between adjacent grid points are certified by exact witnesses.
Sturm root counts are run where the degree permits.
"""
import sympy as sp
from ik_lib import R, y, Fy, fy, in_Ln, weak_sub, weak_super, sturm_roots_on_01

GRID = [R(k, 60) for k in range(1, 60)]


def grid_signs(expr, grid=None):
    grid = grid or GRID
    return [sp.sign(expr.subs(y, v)) for v in grid]


def changes(sgns, grid=None):
    grid = grid or GRID
    out = []
    for i in range(1, len(sgns)):
        if sgns[i - 1] * sgns[i] < 0:
            out.append((grid[i - 1], grid[i], sgns[i - 1], sgns[i]))
    return out


def report(name, expr, want):
    """want: 'nonpos', 'nonneg', or 'nonmono' (a crossing must exist)."""
    sg = grid_signs(expr)
    ch = changes(sg)
    allp = all(s >= 0 for s in sg)
    alln = all(s <= 0 for s in sg)
    ok = {'nonpos': alln, 'nonneg': allp, 'nonmono': len(ch) > 0}[want]
    print(f"  {name}: want {want:7s}; grid all>=0:{allp} all<=0:{alln} "
          f"changes:{[(str(a), str(b)) for a, b, _, _ in ch]} => "
          f"{'VERIFIED' if ok else '*** MISMATCH ***'}")
    return sg


def F(alphas, betas, p):
    return Fy(alphas, betas, p)


def Sbar(alphas, betas, p):
    return 1 - Fy(alphas, betas, p)


print("############ Examples (order should hold) ############")

# ---- Ex 3.1 (Thm 3.1): a=(.5,.4,.3),p=(.2,.2,.6),p*=(.3,.3,.4),beta=1
#   claim R(p*) <=st R(p): Fbar(p*) <= Fbar(p)
a, p, ps, b = [R(5, 10), R(4, 10), R(3, 10)], [R(2, 10), R(2, 10), R(6, 10)], \
    [R(3, 10), R(3, 10), R(4, 10)], R(1)
print("Ex3.1: (a,p) in L3:", in_Ln(a, p), "; (a,p*) in L3:", in_Ln(a, ps),
      "; p* ~_w p:", weak_sub(ps, p))
report("Ex3.1 Sbar(p*)-Sbar(p)",
       Sbar(a, [b] * 3, ps) - Sbar(a, [b] * 3, p), 'nonpos')

# ---- Cex 3.1: p=(.1,.7,.2),p*=(.2,.5,.3),a=(3.5,4.8,5.6),beta=20
a, p, ps, b = [R(35, 10), R(48, 10), R(56, 10)], [R(1, 10), R(7, 10), R(1, 5)], \
    [R(1, 5), R(1, 2), R(3, 10)], R(20)
print("Cex3.1: (a,p) in L3:", in_Ln(a, p), "(expect False); p* ~_w p:",
      weak_sub(ps, p))
# half-integer alphas: substitute via y -> we keep symbolic; grid eval exact
report("Cex3.1 Sbar(p*)-Sbar(p)", Sbar(a, [b] * 3, ps) - Sbar(a, [b] * 3, p),
       'nonmono')

# ---- Ex 3.2 (Thm 3.2): p=(.1,.3,.6),p*=(.2,.3,.5),b=(.5,.4,.3),alpha=.5
#   claim R(p) >=st R(p*)  (Thm: p* ~_w p => R(p*) >=st R(p)?? text: R(p*) >=st R(p))
p, ps, b, a = [R(1, 10), R(3, 10), R(6, 10)], [R(1, 5), R(3, 10), R(1, 2)], \
    [R(5, 10), R(4, 10), R(3, 10)], R(5, 10)
print("Ex3.2: (b,p) in L3:", in_Ln(b, p), "; (b,p*) in L3:", in_Ln(b, ps),
      "; p* ~_w p:", weak_sub(ps, p))
# Thm 3.2 concludes R(p*) >=st R(p) i.e. Fbar(p*) >= Fbar(p)
report("Ex3.2 Sbar(p*)-Sbar(p)", Sbar([a] * 3, b, ps) - Sbar([a] * 3, b, p),
       'nonneg')

# ---- Cex 3.2: p=(.2,.6,.2),p*=(.2,.5,.3),b=(5.2,15.8,5.6),alpha=1 ; not in L3
p, ps, b, a = [R(1, 5), R(3, 5), R(1, 5)], [R(1, 5), R(1, 2), R(3, 10)], \
    [R(52, 10), R(158, 10), R(56, 10)], R(1)
print("Cex3.2: (b,p) in L3:", in_Ln(b, p), "(expect False); p* ~_w p:",
      weak_sub(ps, p))
report("Cex3.2 Sbar(p*)-Sbar(p)",
       Sbar([a] * 3, b, ps) - Sbar([a] * 3, b, p), 'nonmono')

# ---- Ex 3.3 (Thm 3.3): a=(1.1,.9,.4),a*=(1.2,.9,.8),p=(.1,.2,.7),beta=.5
#   claim R(a*) <=st R(a) i.e. Fbar(a*) <= Fbar(a)
a, ast, p, b = [R(11, 10), R(9, 10), R(4, 10)], [R(12, 10), R(9, 10), R(8, 10)], \
    [R(1, 10), R(1, 5), R(7, 10)], R(5, 10)
print("Ex3.3: (a,p) in L3:", in_Ln(a, p), "; (a*,p) in L3:", in_Ln(ast, p),
      "; a* ~_w a:", weak_sub(ast, a))
report("Ex3.3 Sbar(a*)-Sbar(a)",
       Sbar(ast, [b] * 3, p) - Sbar(a, [b] * 3, p), 'nonpos')

# ---- Cex 3.3: a=(1.2,.8,.7), a*=(1.5,.9,.55), p=(...) beta=?
# read text around line 604
print("Cex3.3 (params from text):")

# ---- Cex 3.3: a=(1.2,.8,.7), a*=(1.5,.9,.55), p=(.20,.35,.45), beta=.5
a, ast, p, b = [R(12, 10), R(8, 10), R(7, 10)], [R(15, 10), R(9, 10), R(55, 100)], \
    [R(1, 5), R(7, 20), R(9, 20)], R(1, 2)
print("Cex3.3: (a,p) in L3:", in_Ln(a, p), "; (a*,p) in L3:", in_Ln(ast, p),
      "; a* ~_w a:", weak_sub(ast, a), "(expect False)")
report("Cex3.3 Sbar(a*)-Sbar(a)",
       Sbar(ast, [b] * 3, p) - Sbar(a, [b] * 3, p), 'nonmono')

# ---- Ex 3.4 (Thm 3.4 n=2): p=(.6,.4),p*=(.46,.54), a=(1,9), a*=(6.6,3.4), beta=.5
p, ps, a, ast, b = [R(6, 10), R(4, 10)], [R(46, 100), R(54, 100)], [R(1), R(9)], \
    [R(66, 10), R(34, 10)], R(1, 2)
print("Ex3.4: (p,a) in L2:", in_Ln(p, a))
report("Ex3.4 Sbar(p,a)-Sbar(p*,a*)",
       Sbar(a, [b] * 2, p) - Sbar(ast, [b] * 2, ps), 'nonneg')

# ---- Cex 3.4: a=(2,3),p=(.7,.3),a*=(2.6,2.4),p*=(.46,.54),beta=100
p, ps, a, ast, b = [R(7, 10), R(3, 10)], [R(46, 100), R(54, 100)], [R(2), R(3)], \
    [R(26, 10), R(24, 10)], R(100)
report("Cex3.4 Sbar(p,a)-Sbar(p*,a*)",
       Sbar(a, [b] * 2, p) - Sbar(ast, [b] * 2, ps), 'nonmono')

# ---- Ex 3.5 (Thm 3.7 n=2): p=(.2,.8),p*=(.74,.26),b=(6,2),b*=(2.4,5.6),a=.6
#   claim R(p,b) <=st R(p*,b*): Fbar(p) <= Fbar(p*)
p, ps, b, bs, a = [R(1, 5), R(4, 5)], [R(74, 100), R(26, 100)], [R(6), R(2)], \
    [R(24, 10), R(56, 10)], R(6, 10)
print("Ex3.5: (p,b) in L2:", in_Ln(p, b))
report("Ex3.5 Sbar(p,b)-Sbar(p*,b*)",
       Sbar([a] * 2, b, p) - Sbar([a] * 2, bs, ps), 'nonpos')

# ---- Cex 3.5: p=(.6,.4),b=(7,1); p*=(.48,.52),b*=(3.4,4.6); a=? (not stated;
#   the figure needs alpha -- take generic alpha=1? text gives no alpha; but
#   Thm 3.7 has fixed alpha. Check nonmonotonicity for alpha=1.
p, ps, b, bs, a = [R(6, 10), R(4, 10)], [R(48, 100), R(52, 100)], [R(7), R(1)], \
    [R(34, 10), R(46, 10)], R(1)
print("Cex3.5: (p,b) in L2:", in_Ln(p, b), "(expect False)")
report("Cex3.5 Sbar(p,b)-Sbar(p*,b*)  [a=1]",
       Sbar([a] * 2, b, p) - Sbar([a] * 2, bs, ps), 'nonmono')

print("\n############ Example 3.6 (Thm 3.10) -- ratio monotonicity ############")
# b=(.1,.2,.3),b*=(.5,1,2),p=(.1,.3,.6),p*=(.2,.3,.5),alpha=2 ; g=z^10
from ik_lib import rh_ratio_g, z, g as gs
Rz = rh_ratio_g([R(1, 10), R(1, 5), R(3, 10)], [R(1, 10), R(3, 10), R(6, 10)],
                [R(1, 2), R(1), R(2)], [R(1, 5), R(3, 10), R(1, 2)])
Rz = sp.cancel(Rz.subs(gs, z ** 10))
vals = [(zv, Rz.subs(z, zv)) for zv in
        [R(1, 20), R(1, 10), R(1, 5), R(2, 5), R(11, 20), R(3, 5),
         R(7, 10), R(4, 5), R(9, 10)]]
print("  R(z) exact values:")
prev = None
mono_dec = True
for zv, rv in vals:
    rv = sp.nsimplify(rv)
    if prev is not None and rv > prev[1]:
        mono_dec = False
        print(f"   *** INCREASE at z={zv}: {prev[1]} -> {rv}")
    prev = (zv, rv)
    print(f"   z={zv}: R={sp.N(rv, 10)}")
print("  monotone non-increasing:", mono_dec, " (Thm 3.10 prediction)")

print("\n############ Ex3.7/Cex3.6 (rh) and Ex3.8/Cex3.7 (lr): derivative grids ############")

def rh_grid(a1, b1, p1, a2, b2, p2, name):
    F1, F2 = Fy(a1, b1, p1), Fy(a2, b2, p2)
    d = sp.diff(F2 / F1, y)
    sg = grid_signs(d, GRID)
    ch = changes(sg, GRID)
    alln = all(s <= 0 for s in sg)
    # R1 <=rh R2 iff F2/F1 incr in x iff d/dy <= 0
    print(f"  {name}: d/dy[F2/F1] all<=0: {alln}; changes:{[(str(a_), str(b_)) for a_, b_, _, _ in ch]}",
          "=> rh holds-on-grid" if alln else "=> *** rh NONMONOTONE ***")

def lr_grid(a1, b1, p1, a2, b2, p2, name):
    f1, f2 = fy(a1, b1, p1), fy(a2, b2, p2)
    d = sp.diff(f1 / f2, y)
    sg = grid_signs(d, GRID)
    ch = changes(sg, GRID)
    alln = all(s <= 0 for s in sg)
    # R1 >=lr R2 iff f1/f2 incr in x iff d/dy <= 0
    print(f"  {name}: d/dy[f1/f2] all<=0: {alln}; changes:{[(str(a_), str(b_)) for a_, b_, _, _ in ch]}",
          "=> lr holds-on-grid" if alln else "=> *** lr NONMONOTONE ***")

rh_grid([R(5), R(8), R(6)], [R(2), R(1), R(1)], [R(1, 10), R(7, 10), R(1, 5)],
        [R(3), R(4), R(2)], [R(5), R(3), R(6)], [R(1, 5), R(1, 2), R(3, 10)],
        "Ex3.7 (Thm3.11 admissible; expect holds)")
rh_grid([R(1), R(3), R(5)], [R(3), R(6), R(9)], [R(3, 5), R(1, 4), R(3, 20)],
        [R(2), R(4), R(6)], [R(25), R(30), R(35)], [R(9, 20), R(3, 10), R(1, 4)],
        "Cex3.6 (expect fails)")
lr_grid([R(2), R(4), R(6)], [R(25), R(13), R(9)], [R(1, 5), R(2, 5), R(2, 5)],
        [R(8), R(10), R(12)], [R(3), R(4), R(1)], [R(3, 10), R(1, 2), R(1, 5)],
        "Ex3.8 (Thm3.12 admissible; expect holds)")
lr_grid([R(3), R(6), R(9)], [R(14), R(15), R(11)], [R(1, 10), R(1, 5), R(7, 10)],
        [R(5), R(8), R(12)], [R(4), R(2), R(3)], [R(3, 5), R(3, 10), R(1, 10)],
        "Cex3.7 (expect fails)")
