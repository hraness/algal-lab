"""shape-sweep: attack dispersive-order (SB2022) and star/Lorenz-order (PKP2022)
claim shapes for ordinary exponential mixtures under majorization.

Model: Fbar(t) = sum p_i e^{-lam_i t}.  Common rate denominator D,
k_i = D*lam_i integers, s = e^{-t/D} in (0,1):

    SF        V(s) = sum p_i s^{k_i}              exact rational at rational s
    density   f(t) = (1/D) A(s),  A(s) = sum p_i k_i s^{k_i}  (incr. in s)
    quantile  s*(u) solves V(s*) = 1-u; bisection gives certified rational
              interval [lo,hi] (V increasing; exact endpoint signs in Q)
    t*(u)     = D*(-ln s*)  in  D*[-ln hi, -ln lo]  (mpmath iv, rigorous)

Order characterizations used
----------------------------
disp   X <=disp Y  iff  f_X(F_X^-1(u)) >= f_Y(F_Y^-1(u))  for all u in (0,1)
       (equivalent to quantile-gap ordering; also = hazard-at-quantile since
       f(F^-1(u)) = h(F^-1(u))*(1-u)).
star   X <=* Y     iff  F_X^-1(u)/F_X^-1(v) >= F_Y^-1(u)/F_Y^-1(v)  0<u<v<1
       (quantile-ratio form of "G^-1 F(x)/x increasing").
Lorenz X <=L Y     iff  L_X(p) >= L_Y(p),
       L(p) = [sum_i p_i(1-s^{k_i})/lam_i + D(-ln s)(1-p)] / [sum_i p_i/lam_i]
       (partial first moment of Exp(lam) to T=-D ln s: 1/lam - s^k/lam + k s^k (-ln s)/lam... 
        see code; derived exactly).

CERTIFICATION: dispersive verdicts are exact rational comparisons (no floats).
Star/Lorenz use rigorous mpmath.iv enclosures anchored on the certified
rational quantile intervals.  Bisection 48+ iters -> interval width 2^-48.
"""
import sys
import itertools
sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/mixture-audit")
import sympy as sp
from audit_lib import R, majorizes, in_Un, in_Vn
from mpmath import mp, iv

mp.dps = 60
iv.dps = 80


def ilcm(*args):
    out = 1
    for a in args:
        out = out * int(a) // int(sp.igcd(out, int(a)))
    return out


def ivq(r):
    """rigorous enclosure of rational r as iv.mpf."""
    r = sp.Rational(r)
    return iv.mpf(int(r.p)) / iv.mpf(int(r.q))


def ivlnq(r):
    """rigorous enclosure of ln(r), r positive rational."""
    r = sp.Rational(r)
    return iv.ln(iv.mpf(int(r.p))) - iv.ln(iv.mpf(int(r.q)))


class ExpMix:
    def __init__(self, p, lam):
        self.p = [R(x) for x in p]
        self.lam = [R(x) for x in lam]
        self.D = ilcm(*[q.q for q in self.lam])
        self.k = [int(x * self.D) for x in self.lam]
        assert sum(self.p) == 1 and all(pi > 0 for pi in self.p)

    def V(self, sq):
        return sum(pi * sq ** ki for pi, ki in zip(self.p, self.k))

    def A(self, sq):
        return sum(pi * ki * sq ** ki for pi, ki in zip(self.p, self.k))

    def mean(self):
        return sum(pi / li for pi, li in zip(self.p, self.lam))

    def quant_interval(self, u, iters=48):
        """certified [lo,hi] (rationals) containing s*(u): V(lo) <= 1-u <= V(hi)."""
        c = 1 - R(u)
        lo, hi = R(0), R(1)
        # invariant: V(lo) <= c <= V(hi), lo <= s* <= hi
        for _ in range(iters):
            mid = (lo + hi) / 2
            if self.V(mid) < c:
                lo = mid
            else:
                hi = mid
        return lo, hi

    def dens_at_quant(self, u, iters=48):
        """certified rational interval (f_lo,f_hi) for f(F^-1(u)); A increasing."""
        lo, hi = self.quant_interval(u, iters)
        return self.A(lo) / self.D, self.A(hi) / self.D

    def t_quant(self, u, iters=48):
        """rigorous iv enclosure of t* = F^-1(u) = D*(-ln s*)."""
        lo, hi = self.quant_interval(u, iters)
        ln_lo = ivlnq(lo)   # ln(lo) enclosure
        ln_hi = ivlnq(hi)
        # -ln s* in [-ln_hi.b, -ln_lo.a]
        return iv.mpf([-self.D * ln_hi.b, -self.D * ln_lo.a])

    def lorenz(self, pq, iters=48):
        """rigorous iv enclosure of the Lorenz ordinate L(pq).

        M(pq) = int_0^{pq} F^-1(u) du; u=F(t) gives M = int_0^T t f(t) dt with
        T = F^-1(pq) = D(-ln s*).  Componentwise:
            int_0^T t lam e^{-lam t} dt = (1/lam)(1-e^{-lam T}) - T e^{-lam T}
        so, with V(s*) = 1-pq:
            M = sum_i p_i (1-s*^{k_i})/lam_i  -  D(-ln s*)(1-pq).
        Over s* in [lo,hi]:  (1-s^k) decreasing, (-ln s) decreasing:
            M in [ Mrat(hi) - Dc(-ln lo),  Mrat(lo) - Dc(-ln hi) ].
        """
        c = 1 - R(pq)
        lo, hi = self.quant_interval(pq, iters)

        def Mrat(sq):
            return sum(pi * (1 - sq ** ki) / li
                       for pi, ki, li in zip(self.p, self.k, self.lam))

        ln_lo = ivlnq(lo)          # enclosure of ln(lo)
        ln_hi = ivlnq(hi)
        Mlo = ivq(Mrat(hi)) - self.D * ivq(c) * (-ln_lo)
        Mhi = ivq(Mrat(lo)) - self.D * ivq(c) * (-ln_hi)
        M = iv.mpf([Mlo.a, Mhi.b])
        return M / ivq(self.mean())


# ------------------------------------------------------------------ scans
def st_direction(mix1, mix2, sgrid):
    """sign of SF1 - SF2 on grid: '12' if Fbar1>=Fbar2 throughout (mix2 st>=mix1?)

    Fbar1 >= Fbar2 everywhere <=> X2 >=st X1.  Returns 'F1>=F2', 'F2>=F1', or 'cross'."""
    s1 = s2 = True
    for sq in sgrid:
        d = mix1.V(sq) - mix2.V(sq)
        if d < 0:
            s1 = False
        if d > 0:
            s2 = False
    if s1:
        return "F1>=F2"   # mix1 stochastically smaller? Fbar1>=Fbar2 => X1 >=st X2
    if s2:
        return "F2>=F1"
    return "cross"


def disp_scan(mixX, mixY, ugrid, iters=44):
    """X <=disp Y requires fX(u) >= fY(u) at equal quantiles.
    Returns list of certified violations (u, fX_hi < fY_lo)."""
    viol = []
    for u in ugrid:
        fx_lo, fx_hi = mixX.dens_at_quant(u, iters)
        fy_lo, fy_hi = mixY.dens_at_quant(u, iters)
        if fx_hi < fy_lo:
            viol.append((u, fx_hi, fy_lo, "fX_hi<fY_lo"))
    return viol


def star_scan(mixX, mixY, upairs, iters=44):
    """X <=* Y requires TX(u)/TX(v) >= TY(u)/TY(v). Returns violations."""
    viol = []
    cache = {}

    def T(mix, u):
        key = (id(mix), u)
        if key not in cache:
            cache[key] = mix.t_quant(u, iters)
        return cache[key]

    for u, v in upairs:
        RX = T(mixX, u) / T(mixX, v)
        RY = T(mixY, u) / T(mixY, v)
        if RX.b < RY.a:
            viol.append((u, v, RX, RY))
    return viol


def lorenz_scan(mixX, mixY, pgrid, iters=44):
    """X <=L Y requires L_X(p) >= L_Y(p). Returns violations (p, LX, LY)."""
    viol = []
    for pq in pgrid:
        LX = mixX.lorenz(pq, iters)
        LY = mixY.lorenz(pq, iters)
        if LX.b < LY.a:
            viol.append((pq, LX, LY))
    return viol


def st_cert(mix1, mix2, iters=40):
    """certified st comparison: does Fbar1 >= Fbar2 on all of (0,1)?
    Fbar diff is rational in s with INTEGER exponents -> Sturm on s in (0,1)."""
    s = sp.Symbol("s", positive=True)
    V1 = sum(pi * s ** ki for pi, ki in zip(mix1.p, mix1.k))
    V2 = sum(pi * s ** ki for pi, ki in zip(mix2.p, mix2.k))
    d = sp.cancel(sp.together(V1 - V2))
    num, den = sp.fraction(d)
    nroots = sp.Poly(sp.expand(num), s).count_roots(0, 1)
    # check endpoints sign: at s->0 both ->0; evaluate at 1/2 for direction
    vhalf = d.subs(s, R(1, 2))
    return nroots, vhalf
