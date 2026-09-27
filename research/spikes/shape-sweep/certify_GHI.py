"""CERT G/H/I: flagship certificates for disp/star/Lorenz claim shapes.

CERT G (disp, SB2022):  lam=(2,3,8) >maj gam=(2,4,7), p=(4/11,4/11,3/11) in U_3.
   Fbar_lam - Fbar_gam = s^3(1-s)(4-3s^4)/11 > 0 on (0,1): X_lam strictly
   st-greater, so the only st-compatible disp direction is X_gam <=disp X_lam;
   it fails at u=19/20 by EXACT rational interval bounds.

CERT H (star, PKP2022): lam=(3,4,11) >maj gam=(3,6,9), equal weights.
   gam <=* lam fails at (u,v)=(13/16,15/16), rigorous iv enclosure.
   Plus CERT-A instance: star fails BOTH directions.

CERT I (Lorenz, PKP2022): same instance, gam <=L lam fails at p=15/16.
   Note: lam <=L gam (the opposite direction) survives every probed grid.

Also: n=4 probe  lam=(2,5,9,14) >maj gam=(3,6,8,13), equal weights.
"""
import sys
sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/mixture-audit")
sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/context/runs/shape-sweep")
import sympy as sp
from audit_lib import R, majorizes, in_Un, in_Vn
from mixlib import ExpMix, st_cert, disp_scan, star_scan, lorenz_scan
from mpmath import mp, iv

mp.dps = 50
iv.dps = 60
s = sp.Symbol("s", positive=True)


def sf_diff_poly(m1, m2):
    V1 = sum(pi * s ** ki for pi, ki in zip(m1.p, m1.k))
    V2 = sum(pi * s ** ki for pi, ki in zip(m2.p, m2.k))
    return sp.factor(V1 - V2), sp.Poly(sp.expand(sp.together(V1 - V2).as_numer_denom()[0]), s)


print("=" * 72)
print("CERT G  dispersive-order claim shape (SB2022)")
print("=" * 72)
lamG = (R(2), R(3), R(8)); gamG = (R(2), R(4), R(7)); pG = (R(4, 11), R(4, 11), R(3, 11))
print("p=%s lam=%s gam=%s" % (pG, lamG, gamG))
print("U_3:", in_Un(list(pG), list(lamG)), in_Un(list(pG), list(gamG)),
      "| lam >maj gam:", majorizes(list(lamG), list(gamG)))
mX = ExpMix(pG, gamG); mY = ExpMix(pG, lamG)
fac, poly = sf_diff_poly(mY, mX)
print("Fbar_lam - Fbar_gam =", fac)
print("  numerator roots on (0,1) [Sturm]:", poly.count_roots(0, 1),
      "-> X_lam strictly st-larger; only gam<=disp lam possible")
u = R(19, 20)
fx_lo, fx_hi = mX.dens_at_quant(u, 56)
fy_lo, fy_hi = mY.dens_at_quant(u, 56)
print("u=19/20: f_gam(F_gam^-1(u)) in [%s, %s]" % (float(fx_lo), float(fx_hi)))
print("         f_lam(F_lam^-1(u)) in [%s, %s]" % (float(fy_lo), float(fy_hi)))
print("  certified gap: f_gam_hi < f_lam_lo ?", fx_hi < fy_lo,
      "| margin =", float(fy_lo - fx_hi))
print("  => X_gam <=disp X_lam FAILS at u=19/20 (exact rational certificate)")
vd = disp_scan(mX, mY, [R(k, 40) for k in range(1, 40)], iters=44)
print("  all violating grid u (gam<=disp lam):",
      [str(v[0]) for v in vd])

print()
print("CERT-A instance, disp both directions (SFs cross; hypotheses U_3+maj):")
pA = (R(39, 86), R(18, 43), R(11, 86)); lamA = (R(4), R(6), R(9)); gamA = (R(4), R(7), R(8))
mLA = ExpMix(pA, lamA); mGA = ExpMix(pA, gamA)
facA, polyA = sf_diff_poly(mLA, mGA)
print("  SF_lam-SF_gam =", facA, "| roots(0,1):", polyA.count_roots(0, 1))
for uu in (R(39, 40), R(199, 200)):
    glo, ghi = mGA.dens_at_quant(uu, 56)
    llo, lhi = mLA.dens_at_quant(uu, 56)
    print("  u=%s: f_gam in [%s,%s] ; f_lam in [%s,%s] ; f_gam_hi<f_lam_lo: %s"
          % (uu, float(glo), float(ghi), float(llo), float(lhi), ghi < llo))

print()
print("=" * 72)
print("CERT H  star-order claim shape (PKP2022)")
print("=" * 72)
lamH = (R(3), R(4), R(11)); gamH = (R(3), R(6), R(9)); pH = (R(1, 3),) * 3
print("p=(1/3,1/3,1/3) lam=%s gam=%s" % (lamH, gamH))
print("U_3 (trivial at equal weights):", in_Un(list(pH), list(lamH)),
      in_Un(list(pH), list(gamH)), "| lam >maj gam:", majorizes(list(lamH), list(gamH)))
mXh = ExpMix(pH, gamH); mYh = ExpMix(pH, lamH)
fach, polyh = sf_diff_poly(mYh, mXh)
print("Fbar_lam - Fbar_gam =", fach, "| roots(0,1):", polyh.count_roots(0, 1))
u, v = R(13, 16), R(15, 16)
TXu = mXh.t_quant(u, 56); TXv = mXh.t_quant(v, 56)
TYu = mYh.t_quant(u, 56); TYv = mYh.t_quant(v, 56)
RX = TXu / TXv; RY = TYu / TYv
print("u=13/16 v=15/16:")
print("  T_gam(u)/T_gam(v) in %s" % RX)
print("  T_lam(u)/T_lam(v) in %s" % RY)
print("  certified: RX.b < RY.a ?", RX.b < RY.a)
print("  => X_gam <=* X_lam FAILS at (13/16,15/16) (rigorous interval cert)")
vs = star_scan(mXh, mYh, [(R(a, 16), R(b, 16)) for a in range(1, 15)
                         for b in range(a + 1, 16)], iters=44)
print("  all violating (u,v) pairs:", [(str(a), str(b)) for a, b, _, _ in vs])

print()
print("CERT-A instance, star both directions:")
for u, v in [(R(1, 24), R(1, 12))]:
    RXl = mLA.t_quant(u, 48) / mLA.t_quant(v, 48)
    RYl = mGA.t_quant(u, 48) / mGA.t_quant(v, 48)
    print("  u=%s v=%s  T_lam ratio %s | T_gam ratio %s | lam<=*gam fails: %s"
          % (u, v, RXl, RYl, RXl.b < RYl.a))
for u, v in [(R(1, 24), R(2, 3))]:
    RXl = mGA.t_quant(u, 48) / mGA.t_quant(v, 48)
    RYl = mLA.t_quant(u, 48) / mLA.t_quant(v, 48)
    print("  u=%s v=%s  T_gam ratio %s | T_lam ratio %s | gam<=*lam fails: %s"
          % (u, v, RXl, RYl, RXl.b < RYl.a))

print()
print("=" * 72)
print("CERT I  Lorenz-order claim shape (PKP2022)")
print("=" * 72)
pq = R(15, 16)
LX = mXh.lorenz(pq, 56); LY = mYh.lorenz(pq, 56)
print("same instance; p=15/16:")
print("  L_gam(p) in %s" % LX)
print("  L_lam(p) in %s" % LY)
print("  certified: L_gam.b < L_lam.a ?", LX.b < LY.a)
print("  => X_gam <=L X_lam FAILS at p=15/16")
vl = lorenz_scan(mXh, mYh, [R(k, 16) for k in range(1, 16)], iters=44)
print("  all violating p:", [str(vv[0]) for vv in vl])
print("  opposite direction lam<=L gam on same instance:")
vl2 = lorenz_scan(mYh, mXh, [R(k, 16) for k in range(1, 16)], iters=44)
print("    violations:", len(vl2), "(0 = consistent with X_lam <=L X_gam)")

print()
print("=" * 72)
print("n=4 probe: lam=(2,5,9,14) >maj gam=(3,6,8,13), equal weights")
print("=" * 72)
lam4 = (R(2), R(5), R(9), R(14)); gam4 = (R(3), R(6), R(8), R(13))
p4 = (R(1, 4),) * 4
print("lam>maj gam:", majorizes(list(lam4), list(gam4)),
      "| in_Un:", in_Un(list(p4), list(lam4)), in_Un(list(p4), list(gam4)))
m4X = ExpMix(p4, gam4); m4Y = ExpMix(p4, lam4)
fac4, poly4 = sf_diff_poly(m4Y, m4X)
print("SF_lam-SF_gam:", fac4, "| roots(0,1):", poly4.count_roots(0, 1))
vd4 = disp_scan(m4X, m4Y, [R(k, 24) for k in range(1, 24)], iters=40)
print("disp gam<=disp lam violations:", [(str(v[0]),) for v in vd])
vs4 = star_scan(m4X, m4Y, [(R(a, 16), R(b, 16)) for a in range(1, 15)
                          for b in range(a + 1, 16)], iters=40)
print("star gam<=* lam violations:", [(str(a), str(b)) for a, b, _, _ in vs4])
vl4 = lorenz_scan(m4X, m4Y, [R(k, 16) for k in range(1, 16)], iters=40)
print("lorenz gam<=L lam violations:", [(str(vv[0]),) for vv in vl4])
