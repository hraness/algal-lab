"""Exact rational confirmation of witnesses for doi:10.1080/02331888.2025.2552185.

All survivals are polynomials in z = e^{-x} with integer exponents.  Hazard
rate r(x) = z S'(z)/S(z); reversed hazard = z S'(z)/(1-S(z)); density prop z S'(z).
Signs computed exactly with sympy Rational arithmetic at the witness points.
"""

import sympy as sp

z = sp.Symbol("z")
R = sp.Rational


def kw(c, a, g):
    """(1-(1-z^c)^a)^g as expanded poly."""
    return sp.expand((1 - (1 - z**c)**a)**g)


def S_min(components, pmf):
    out = sp.Integer(0)
    for m, p in pmf.items():
        t = sp.Integer(1)
        for s in components[:m]:
            t *= s
        out += p * t
    return sp.expand(out)


def S_max(components, pmf):
    out = sp.Integer(0)
    for m, p in pmf.items():
        t = sp.Integer(1)
        for s in components[:m]:
            t *= (1 - s)
        out += p * t
    return sp.expand(1 - out)


def hr_diff(SX, SY, z0):
    """sign of r_X - r_Y at z0, exact. r = z S'/S."""
    expr = sp.together(sp.diff(SX, z) / SX - sp.diff(SY, z) / SY)  # times z>0
    return sp.sign(expr.subs(z, z0)), expr.subs(z, z0)


def rh_diff(SX, SY, z0):
    expr = sp.together(sp.diff(SX, z) / (1 - SX) - sp.diff(SY, z) / (1 - SY))
    return sp.sign(expr.subs(z, z0)), expr.subs(z, z0)


def ratio_diff(SX, SY, z0):
    """d/dz (fY/fX) sign via derivative of S'Y/S'X."""
    expr = sp.together(sp.diff(sp.diff(SY, z) / sp.diff(SX, z), z))
    return sp.sign(expr.subs(z, z0)), sp.nsimplify(expr.subs(z, z0))


pmf3 = {1: R(1, 3), 2: R(1, 3), 3: R(1, 3)}
pmf2 = {1: R(1, 2), 2: R(1, 2)}

print("== Thm 3.9/3.10 adj-a: a=(1,1,2) b=(2,2,2) g=(1,1,1) G=H=Exp1 ==")
SX = S_min([kw(1,1,1),kw(1,1,1),kw(1,2,1)], pmf3)
SY = S_min([kw(1,2,1)]*3, pmf3)
for z0 in (R(1,12), R(1,2), R(3,5), R(9,10)):
    s, v = hr_diff(SX, SY, z0)
    print(f"  z={z0}: rX-rY = {v}  sign {s}  (rX<rY kills X<=hrY; rX>rY kills X>=hrY)")

print("== adj-b g=(1,1,2) ==")
SX = S_min([kw(1,1,1),kw(1,1,1),kw(1,2,2)], pmf3)
SY = S_min([kw(1,2,1),kw(1,2,1),kw(1,2,2)], pmf3)
for z0 in (R(1,12), R(1,2), R(9,10)):
    print(f"  z={z0}: sign rX-rY = {hr_diff(SX,SY,z0)[0]}")

print("== alt-c a=(2,3,3) b=(2,2,2) g=(1,1,1) ==")
SX = S_min([kw(1,2,1),kw(1,3,1),kw(1,3,1)], pmf3)
SY = S_min([kw(1,2,1)]*3, pmf3)
for z0 in (R(1,3), R(1,2), R(3,5), R(9,10), R(99,100)):
    s, v = hr_diff(SX, SY, z0)
    print(f"  z={z0}: rX-rY sign {s}")

print("== Thm 3.10 adj-G2H1 (premise satisfied; expect rX>=rY i.e. X<=hrY) ==")
SX = S_min([kw(2,1,1),kw(2,2,2)], pmf2)     # G=Exp(2)
SY = S_min([kw(1,2,1),kw(1,3,2)], pmf2)     # H=Exp(1)
for z0 in (R(1,12), R(1,2), R(9,10)):
    print(f"  z={z0}: sign rX-rY = {hr_diff(SX,SY,z0)[0]}")

print("== Thm 3.10 adj-D+ a=(2,1,1) desc ==")
SX = S_min([kw(1,2,1),kw(1,1,1),kw(1,1,1)], pmf3)
SY = S_min([kw(1,2,1)]*3, pmf3)
for z0 in (R(1,12), R(1,2), R(9,10)):
    print(f"  z={z0}: sign rX-rY = {hr_diff(SX,SY,z0)[0]}")

print("== Thm 3.7 ==")
# litsuf-f: g=(4,5) d=(1,8) sums 9<=9, pmf {1:9/10, 2:1/10}; claim X>=hrY (rX<=rY)
pmf910 = {1: R(9,10), 2: R(1,10)}
SX = S_min([kw(1,1,4),kw(1,1,5)], pmf910)
SY = S_min([kw(1,1,1),kw(1,1,8)], pmf910)
for z0 in (R(1,2), R(9,10), R(1,10)):
    s, v = hr_diff(SX, SY, z0)
    print(f"  litsuf-f z={z0}: rX-rY={v} sign {s} (positive kills X>=hrY)")
# necc-d: N=1; premise sums 7<=6 fails; conclusion X>=hrY: rX=2? use polys z^2,z^3
SXn = z**2; SYn = z**3
s, v = hr_diff(SXn, SYn, R(1,2))
print(f"  necc-d rX-rY sign {s} ({v}) -> X>=hrY holds while premise 7<=6 fails: iff broken")

print("== Thm 3.8 desc-c: g=(4,1,1) d=(2,2,2) a=2 G=H; claim X>=hrY ==")
K = kw(1,2,1)   # (1-(1-z)^2) = 2z-z^2
SX = S_min([K**4,K**1,K**1], pmf3)
SY = S_min([K**2]*3, pmf3)
for z0 in (R(1,2), R(1,4), R(3,4)):
    s, v = hr_diff(SX, SY, z0)
    print(f"  z={z0}: rX-rY = {v} sign {s} (positive kills X>=hrY)")

print("== Thm 3.12 adj: a=(1,1,2) b=(2,2,2) g=2; claim X>=rhY (rtX>=rtY) ==")
SX = S_max([kw(1,1,2),kw(1,1,2),kw(1,2,2)], pmf3)
SY = S_max([kw(1,2,2)]*3, pmf3)
for z0 in (R(1,2), R(1,4), R(9,10)):
    s, v = rh_diff(SX, SY, z0)
    print(f"  z={z0}: rtX-rtY = {v} sign {s} (negative kills X>=rhY)")
print("== Thm 3.12 alt: a=(2,3,3) ==")
SX2 = S_max([kw(1,2,2),kw(1,3,2),kw(1,3,2)], pmf3)
for z0 in (R(1,2), R(1,20), R(9,10)):
    s, v = rh_diff(SX2, SY, z0)
    print(f"  z={z0}: rtX-rtY sign {s}")

print("== Thm 3.18: a1=3,a=2,b1=1 g=1; claim X<=lrY (d/dz(fY/fX)<=0) ==")
SX = S_min([kw(1,3,1),kw(1,2,1)], pmf2)
SY = S_min([kw(1,1,1),kw(1,2,1)], pmf2)
for z0 in (R(1,2), R(1,4), R(9,10)):
    s, v = ratio_diff(SX, SY, z0)
    print(f"  z={z0}: d/dz(fY/fX) = {v} sign {s} (positive kills X<=lrY since it must be decreasing in z)")
