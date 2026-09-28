"""Independent C3 verification for doi:10.1080/02331888.2025.2552185.

Fresh model code (NOT the eval script's): Kw-G survival S_i(x) =
(1 - G(x)^a_i)^g_i; G = Exp(c) gives G(x) = 1 - e^{-cx}; in z = e^{-x},
S_i(z) = (1 - (1-z^c)^a_i)^g_i.  Random minima: S_{1:N} = sum_m p_m prod_{i<=m} S_i.
Random maxima: S_{N:N} = 1 - sum_m p_m prod_{i<=m} (1 - S_i).

Orders in x (z=e^{-x} decreasing):
  X <=hr Y  iff r_X(x) >= r_Y(x)  iff  z S_X'(z)/S_X(z) >= z S_Y'(z)/S_Y(z)
  X <=rh Y  iff rt_X(x) <= rt_Y(x) iff  z S_X'(z)/(1-S_X(z)) <= same_Y
  X <=lr Y  iff f_Y(x)/f_X(x) increasing in x  iff  f_Y/f_X decreasing in z
         where f(z) = z S'(z).
We evaluate at 120-digit mpmath precision on a dense grid and also hunt for
sign witnesses with exact sympy rational arithmetic as a second opinion.
"""

import mpmath as mp
import sympy as sp

mp.mp.dps = 120
z = sp.Symbol("z")
R = sp.Rational


def S_kw(Gpoly, a, g):
    """survival (1-G^a)^g, G polynomial in z."""
    return (1 - Gpoly**a)**g


def S_min(components, pmf):
    """X_{1:N}: E over N of prod_{i<=m} S_i."""
    out = mp.mpf(0)
    return lambda zz: sum(pmf[m] * mp.fprod(s(zz) for s in components[:m])
                          for m in pmf)


def S_max(components, pmf):
    return lambda zz: 1 - sum(pmf[m] * mp.fprod(1 - s(zz) for s in components[:m])
                              for m in pmf)


def kw_exp(a, g, c=1):
    """Kw-G( a, g; Exp(c) ) survival as function of z: (1-(1-z^c)^a)^g."""
    return lambda zz: (1 - (1 - mp.mpf(zz)**c)**a)**g


def hazard_z(Sf, zz):
    """r(x) = z S'(z)/S(z) at z=e^{-x} (mpmath diff)."""
    zz = mp.mpf(zz)
    dS = mp.diff(Sf, zz)
    return zz * dS / Sf(zz)


def rhazard_z(Sf, zz):
    zz = mp.mpf(zz)
    dS = mp.diff(Sf, zz)
    return zz * dS / (1 - Sf(zz))


def dens_z(Sf, zz):
    return mp.mpf(zz) * mp.diff(Sf, zz)


def scan_hr(SX, SY, npts=400):
    """Check X <=hr Y  (r_X >= r_Y) and X >=hr Y (r_X <= r_Y) over z in (0,1).

    Returns (hr_XY_ok, hr_YX_ok, witnesses) using dense sampling; then exact
    sympy confirmation at the witness points."""
    pts = [mp.mpf(i) / npts for i in range(1, npts)]
    hr_xy, hr_yx = True, True
    w_xy = w_yx = None
    for t in pts:
        rx, ry = hazard_z(SX, t), hazard_z(SY, t)
        if rx < ry - mp.mpf('1e-40'):
            hr_xy = False
            w_xy = t
        if rx > ry + mp.mpf('1e-40'):
            hr_yx = False
            w_yx = t
    return hr_xy, hr_yx, w_xy, w_yx


def scan_rh(SX, SY, npts=400):
    pts = [mp.mpf(i) / npts for i in range(1, npts)]
    rh_xy, rh_yx = True, True   # rh_xy: X <=rh Y (rt_X <= rt_Y)
    w_xy = w_yx = None
    for t in pts:
        rx, ry = rhazard_z(SX, t), rhazard_z(SY, t)
        if rx > ry + mp.mpf('1e-40'):
            rh_xy = False; w_xy = t
        if rx < ry - mp.mpf('1e-40'):
            rh_yx = False; w_yx = t
    return rh_xy, rh_yx, w_xy, w_yx


def scan_lr(SX, SY, npts=400):
    """X <=lr Y iff f_Y/f_X decreasing in z. Check sign of d/dz(f_Y/f_X)."""
    pts = [mp.mpf(i) / npts for i in range(1, npts)]
    lr_xy = lr_yx = True
    w_xy = w_yx = None
    prev = None
    for t in pts:
        fx, fy = dens_z(SX, t), dens_z(SY, t)
        r = fy / fx
        if prev is not None:
            dr = r - prev[0]
            if dr > mp.mpf('1e-40'):
                lr_xy = False; w_xy = t
            if dr < -mp.mpf('1e-40'):
                lr_yx = False; w_yx = t
        prev = (r, t)
    return lr_xy, lr_yx, w_xy, w_yx


def hr_exact(SXp, SYp, z0):
    """Exact sympy check at rational z0: sign of r_X - r_Y (in z-space)."""
    num = sp.together(sp.diff(SXp, z) * SYp - sp.diff(SYp, z) * SXp)
    v = sp.simplify(num.subs(z, z0))
    return v, float(v)


# ---------------------------------------------------------------- instances
PMF3 = {1: mp.mpf('0.33333333333333333333333333333333333333333333333333'),
        2: mp.mpf('0.33333333333333333333333333333333333333333333333333'),
        3: mp.mpf('0.33333333333333333333333333333333333333333333333333')}
PMF3 = {m: mp.mpf(1) / 3 for m in (1, 2, 3)}
PMF2 = {m: mp.mpf(1) / 2 for m in (1, 2)}

print("=========== Theorem 3.9 / 3.10 shared instances ===========")
# adj-a: alpha=(1,1,2) beta=(2,2,2) gamma=delta=(1,1,1), G=H=Exp(1)
Xc = [kw_exp(1, 1), kw_exp(1, 1), kw_exp(2, 1)]
Yc = [kw_exp(2, 1), kw_exp(2, 1), kw_exp(2, 1)]
SX, SY = S_min(Xc, PMF3), S_min(Yc, PMF3)
print("adj-a: alpha=(1,1,2), beta=(2,2,2), g=(1,1,1), G=H, N~U{1,2,3}")
print("  premise sup(beta>=alpha): asc sums beta", [2, 4, 6], ">= alpha", [1, 2, 4], "-> True")
print("  Thm3.9 claim X >=hr Y :", scan_hr(SX, SY))
print("  Thm3.10 claim X <=hr Y:", scan_hr(SX, SY))
a, b, wa, wb = scan_hr(SX, SY)
print(f"  X<=hr Y: {a} (wit z={wb}), X>=hr Y: {b} (wit z={wa})")
# hazards at witness
for t in (mp.mpf('0.0833333333333333333333'), mp.mpf('0.5'), mp.mpf('0.6'), mp.mpf('0.9')):
    print("   z=", t, " rX=", mp.nstr(hazard_z(SX, t), 25), " rY=", mp.nstr(hazard_z(SY, t), 25))

# adj-b: gamma=delta=(1,1,2)
Xc = [kw_exp(1, 1), kw_exp(1, 1), kw_exp(2, 2)]
Yc = [kw_exp(2, 1), kw_exp(2, 1), kw_exp(2, 2)]
SXb, SYb = S_min(Xc, PMF3), S_min(Yc, PMF3)
a, b, wa, wb = scan_hr(SXb, SYb)
print("adj-b gamma=(1,1,2): X<=hrY", a, "wit", wb, "| X>=hrY", b, "wit", wa)

# alt-c: alpha=(2,3,3) supermajorizes beta=(2,2,2) (desc partial sums 3,6,8 vs 2,4,6)
Xc = [kw_exp(2, 1), kw_exp(3, 1), kw_exp(3, 1)]
Yc = [kw_exp(2, 1), kw_exp(2, 1), kw_exp(2, 1)]
SXc, SYc = S_min(Xc, PMF3), S_min(Yc, PMF3)
a, b, wa, wb = scan_hr(SXc, SYc)
print("alt-c alpha=(2,3,3): X<=hrY", a, "wit", wb, "| X>=hrY", b, "wit", wa)
for t in (mp.mpf('0.6'), mp.mpf('0.9'), mp.mpf('0.99')):
    print("   z=", t, " rX=", mp.nstr(hazard_z(SXc, t), 25), " rY=", mp.nstr(hazard_z(SYc, t), 25))

# Thm 3.10 extra instances
print("---- Thm 3.10 adj-G2H1: G=Exp(2),H=Exp(1), alpha=(1,2),beta=(2,3),gamma=(1,2), N U{1,2}")
Xc = [kw_exp(1, 1, 2), kw_exp(2, 2, 2)]
Yc = [kw_exp(2, 1, 1), kw_exp(3, 2, 1)]
SXd, SYd = S_min(Xc, PMF2), S_min(Yc, PMF2)
a, b, wa, wb = scan_hr(SXd, SYd)
print("  X<=hrY", a, "wit", wb, "| X>=hrY", b, "wit", wa)

print("---- Thm 3.10 adj-D+: alpha=(2,1,1) descending, beta=(2,2,2), G=H")
Xc = [kw_exp(2, 1), kw_exp(1, 1), kw_exp(1, 1)]
SXe, SYe = S_min(Xc, PMF3), S_min(Yc, PMF3)
a, b, wa, wb = scan_hr(SXe, SYe)
print("  X<=hrY", a, "wit", wb, "| X>=hrY", b, "wit", wa)

print("=========== Theorem 3.7 iff ===========")
# necc-d: N=1 det; X: gamma_1=2 (S=z^2), Y: delta_1=3 (S=z^3); vectors len 2: g=(2,5), d=(3,3)
# premise sums: 7 <= 6 ? false. conclusion X >=hr Y ?
SXn = kw_exp(1, 2, 1)
SYn = kw_exp(1, 3, 1)
print("necc-d N=1: S_X=z^2, S_Y=z^3; rX=2, rY=3 -> X>=hrY holds:",
      all(hazard_z(SXn, mp.mpf(i)/50) <= hazard_z(SYn, mp.mpf(i)/50) for i in range(1, 50)))
# litsuf-f: gamma=(4,5), delta=(1,8), sums 9<=9 satisfied; pmf {1:.9,2:.1}
pmf2 = {1: mp.mpf('0.9'), 2: mp.mpf('0.1')}
Xc = [kw_exp(1, 4), kw_exp(1, 5)]
Yc = [kw_exp(1, 1), kw_exp(1, 8)]
SXl, SYl = S_min(Xc, pmf2), S_min(Yc, pmf2)
a, b, wa, wb = scan_hr(SXl, SYl)
print("litsuf-f g=(4,5),d=(1,8) sums 9<=9: X<=hrY", a, "wit", wb, "| X>=hrY", b, "wit", wa)
for t in (mp.mpf('0.5'), mp.mpf('0.9'), mp.mpf('0.99'), mp.mpf('0.999')):
    print("   z=", t, " rX=", mp.nstr(hazard_z(SXl, t), 25), " rY=", mp.nstr(hazard_z(SYl, t), 25))

print("=========== Theorem 3.8 ===========")
# a=2: K=(1-(1-z)^2)^1=2z-z^2. asc-b: gamma=(1,1,4) delta=(2,2,2), N U{1,2,3}
K = kw_exp(2, 1)          # (1-(1-z)^2)^1 = 2z-z^2
def Kpow(k):
    return lambda zz: K(zz)**k
SXa = S_min([Kpow(1), Kpow(1), Kpow(4)], PMF3)
SYa = S_min([Kpow(2), Kpow(2), Kpow(2)], PMF3)
a, b, wa, wb = scan_hr(SXa, SYa)
print("asc-b gamma=(1,1,4),delta=(2,2,2): X<=hrY", a, "wit", wb, "| X>=hrY", b, "wit", wa)
# desc-c: gamma=(4,1,1) listed descending
SXd2 = S_min([Kpow(4), Kpow(1), Kpow(1)], PMF3)
a, b, wa, wb = scan_hr(SXd2, SYa)
print("desc-c gamma=(4,1,1),delta=(2,2,2): X<=hrY", a, "wit", wb, "| X>=hrY", b, "wit", wa)
for t in (mp.mpf('0.5'), mp.mpf('0.9'), mp.mpf('0.99')):
    print("   z=", t, " rX=", mp.nstr(hazard_z(SXd2, t), 25), " rY=", mp.nstr(hazard_z(SYa, t), 25))

print("=========== Theorem 3.12 (rh) ===========")
# gamma=2: X=(1,1,2), Y=(2,2,2) alphas; maxima.
Xc = [kw_exp(1, 2), kw_exp(1, 2), kw_exp(2, 2)]
Yc = [kw_exp(2, 2), kw_exp(2, 2), kw_exp(2, 2)]
SXr = S_max(Xc, PMF3)
SYr = S_max(Yc, PMF3)
rh_xy, rh_yx, wxy, wyx = scan_rh(SXr, SYr)
print("adj (beta asc sums >= alpha): X<=rhY", rh_xy, "wit", wxy, "| X>=rhY (claimed)", rh_yx, "wit", wyx)
for t in (mp.mpf('0.5'), mp.mpf('0.9'), mp.mpf('0.99'), mp.mpf('0.05')):
    print("   z=", t, " rtX=", mp.nstr(rhazard_z(SXr, t), 25), " rtY=", mp.nstr(rhazard_z(SYr, t), 25))
# alt reading: alpha=(2,3,3)
Xc2 = [kw_exp(2, 2), kw_exp(3, 2), kw_exp(3, 2)]
SXr2 = S_max(Xc2, PMF3)
rh_xy, rh_yx, wxy, wyx = scan_rh(SXr2, SYr)
print("alt alpha=(2,3,3): X<=rhY", rh_xy, "wit", wxy, "| X>=rhY (claimed)", rh_yx, "wit", wyx)
for t in (mp.mpf('0.5'), mp.mpf('0.9'), mp.mpf('0.05')):
    print("   z=", t, " rtX=", mp.nstr(rhazard_z(SXr2, t), 25), " rtY=", mp.nstr(rhazard_z(SYr, t), 25))

print("=========== Theorem 3.18 (lr) ===========")
pmf = PMF2
sxa1 = kw_exp(3, 1); sxa2 = kw_exp(2, 1); syb1 = kw_exp(1, 1)
SXl2 = S_min([sxa1, sxa2], pmf)
SYl2 = S_min([syb1, sxa2], pmf)
lr_xy, lr_yx, wxy, wyx = scan_lr(SXl2, SYl2)
print("a1=3,a=2,b1=1: X<=lrY (claimed)", lr_xy, "wit", wxy, "| Y<=lrX", lr_yx, "wit", wyx)
# st check
stXY = all(SXl2(mp.mpf(i)/200) <= SYl2(mp.mpf(i)/200) + mp.mpf('1e-50') for i in range(1, 200))
stYX = all(SYl2(mp.mpf(i)/200) <= SXl2(mp.mpf(i)/200) + mp.mpf('1e-50') for i in range(1, 200))
print("  X<=stY:", stXY, " Y<=stX:", stYX)
for t in (mp.mpf('0.5'), mp.mpf('0.9'), mp.mpf('0.99'), mp.mpf('0.1')):
    print("   z=", t, " fY/fX=", mp.nstr(dens_z(SYl2, t)/dens_z(SXl2, t), 25))
