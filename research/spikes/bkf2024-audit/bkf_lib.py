"""Exact-arithmetic audit library for BKF2024 (Bhakta-Kayal-Finkelstein,
MCAP 26:52, 2024): finite mixtures of location-scale components.

Model: component i ~ F((x - sig_i)/lam_i).  Mixture SF = sum r_i Fbar(u_i),
u_i = (x-sig_i)/lam_i.  Baselines are piecewise: Fbar=1 below support,
Fbar=0 above; f=0 outside support.  All evaluation exact (sympy Rational).
"""
from fractions import Fraction
import sympy as sp

R = sp.Rational


# ---------------------------------------------------------------- baselines
# each: dict with u_min,u_max (support bounds, u_max=None for unbounded),
# Fbar(u), f(u) exact sympy expressions in u (on support).
u = sp.Symbol("u", positive=True)

BASELINES = {
    # Pareto shape 1: Fbar=1/u, f=1/u^2 on [1,inf).  tf(t)=1/t decreasing.
    "pareto1": dict(u_min=sp.Integer(1), u_max=None,
                    Fbar=1/u, f=1/u**2),
    # Pareto shape 2 (their Cex4/5): F=1-1/t^2, f=2/t^3 on [1,inf).
    "pareto2": dict(u_min=sp.Integer(1), u_max=None,
                    Fbar=1/u**2, f=2/u**3),
    # power F=t^2, f=2t, Fbar=1-t^2 on (0,1]  (f increasing).
    "power2": dict(u_min=sp.Integer(0), u_max=sp.Integer(1),
                   Fbar=1-u**2, f=2*u),
    # power F=(t/l)^c general c,l: f = c/l^c t^{c-1} on (0,l].
    # instantiated via make_power(c,l)
    # Burr-III: F=t/(1+t), f=1/(1+t)^2, Fbar=1/(1+t) on (0,inf).
    "burr3": dict(u_min=sp.Integer(0), u_max=None,
                  Fbar=1/(1+u), f=1/(1+u)**2),
    # Fbar=(1-t)^2 on (0,1]: f=2(1-t) decreasing, h=2/(1-t) increasing.
    "linhaz": dict(u_min=sp.Integer(0), u_max=sp.Integer(1),
                   Fbar=(1-u)**2, f=2*(1-u)),
}


def make_power(c, l):
    c, l = sp.nsimplify(c), sp.nsimplify(l)
    return dict(u_min=sp.Integer(0), u_max=l,
                Fbar=1-(u/l)**c, f=c/l**c*u**(c-1))


def comp_vals(x, sig, lam, base):
    """Return (Fbar_i, f_i, F_i, alive) for component i at point x,
    exact.  u_i = (x-sig)/lam; alive iff u_min <= u_i <= u_max."""
    ui = sp.nsimplify((x-sig)/lam)
    lo, hi = base["u_min"], base["u_max"]
    alive = (lo is None or ui >= lo) and (hi is None or ui <= hi)
    if not alive:
        if lo is not None and ui < lo:
            return dict(u=ui, Fbar=sp.Integer(1), f=sp.Integer(0),
                        F=sp.Integer(0), alive=False)
        return dict(u=ui, Fbar=sp.Integer(0), f=sp.Integer(0),
                    F=sp.Integer(1), alive=False)
    return dict(u=ui, Fbar=sp.nsimplify(base["Fbar"].subs(u, ui)),
                f=sp.nsimplify(base["f"].subs(u, ui)),
                F=sp.nsimplify(1-base["Fbar"].subs(u, ui)), alive=True)


# ------------------------------------------------- fast Fraction versions --
# Plain-fraction evaluation (no sympy) for search loops.
FBASE_F = {
    "pareto1": (lambda u: 1/u, 1, None),
    "pareto2": (lambda u: 1/u**2, 1, None),
    "power2":  (lambda u: 1-u**2, 0, 1),
    "burr3":   (lambda u: 1/(1+u), 0, None),
    "linhaz":  (lambda u: (1-u)**2, 0, 1),
}

def fFbar(base_name, uu, c=None, l=None):
    """Fbar(uu) as Fraction; base_name in FBASE_F or 'power' with (c,l)."""
    if base_name == "power":
        lo, hi = Fraction(0), Fraction(l)
        Fb = 1 - (uu/l)**c
    else:
        fn, lo, hi = FBASE_F[base_name]; Fb = fn(uu)
    return Fb, lo, hi

def hr_frac(x, r, sig_lam, base_name, c=None, l=None):
    """Mixture hazard at Fraction x, piecewise-aware, all-Fraction."""
    num = den = Fraction(0)
    for ri, (si, li) in zip(r, sig_lam):
        uu = (x - si)/li
        if base_name == "power":
            lo, hi = Fraction(0), Fraction(l)
            Fb = 1 - (uu/l)**c
            fv = Fraction(c, l**c)*uu**(c-1)
        else:
            fn, lo, hi = FBASE_F[base_name]
            Fb, fv = fn(uu), None
        if uu < lo or (hi is not None and uu > hi):
            continue
        if base_name == "pareto1": fv = 1/uu**2
        elif base_name == "pareto2": fv = 2/uu**3
        elif base_name == "power2": fv = 2*uu
        elif base_name == "burr3": fv = 1/(1+uu)**2
        elif base_name == "linhaz": fv = 2*(1-uu)
        num += ri*fv/li
        den += ri*Fb
    if den == 0:
        return None
    return num/den

def rh_frac(x, r, sig_lam, base_name, c=None, l=None):
    num = den = Fraction(0)
    for ri, (si, li) in zip(r, sig_lam):
        uu = (x - si)/li
        if base_name == "power":
            lo, hi = Fraction(0), Fraction(l)
            Fb = 1 - (uu/l)**c
            fv = Fraction(c, l**c)*uu**(c-1)
        else:
            fn, lo, hi = FBASE_F[base_name]
            Fb, fv = fn(uu), None
        if uu < lo or (hi is not None and uu > hi):
            continue
        if base_name == "pareto1": fv = 1/uu**2
        elif base_name == "pareto2": fv = 2/uu**3
        elif base_name == "power2": fv = 2*uu
        elif base_name == "burr3": fv = 1/(1+uu)**2
        elif base_name == "linhaz": fv = 2*(1-uu)
        num += ri*fv/li
        den += ri*(1-Fb)
    if den == 0:
        return None
    return num/den


def sf_frac(x, r, sig_lam, base_name, c=None, l=None):
    tot = Fraction(0)
    for ri, (si, li) in zip(r, sig_lam):
        uu = (x - si)/li
        if base_name == "power":
            lo, hi = Fraction(0), Fraction(l)
            Fb = 1-(uu/l)**c if 0 < uu <= hi else (Fraction(1) if uu <= 0 else Fraction(0))
        else:
            fn, lo, hi = FBASE_F[base_name]
            if uu < lo:
                Fb = Fraction(1)
            elif hi is not None and uu > hi:
                Fb = Fraction(0)
            else:
                Fb = fn(uu)
        tot += ri*Fb
    return tot


def mix_sf(x, r, sig_lam, base):
    """Mixture SF at rational x. sig_lam = list of (sig_i, lam_i)."""
    tot = sp.Integer(0)
    for ri, (si, li) in zip(r, sig_lam):
        cv = comp_vals(x, si, li, base)
        tot += ri*cv["Fbar"]
    return sp.cancel(tot)


def mix_hr(x, r, sig_lam, base):
    """Mixture hazard rate at x: sum_{active} r_i (1/lam_i) f_i / sum r_i Fbar_i.
    Components past support have Fbar=f=0 -> drop out."""
    num = sp.Integer(0); den = sp.Integer(0)
    for ri, (si, li) in zip(r, sig_lam):
        cv = comp_vals(x, si, li, base)
        if cv["alive"]:
            num += ri*(1/li)*cv["f"]
            den += ri*cv["Fbar"]
    if den == 0:
        return None  # beyond support of all components
    return sp.cancel(num/den)


def mix_rh(x, r, sig_lam, base):
    """Mixture reversed hazard at x: sum_{active} r_i (1/lam_i) f_i / sum r_i F_i."""
    num = sp.Integer(0); den = sp.Integer(0)
    for ri, (si, li) in zip(r, sig_lam):
        cv = comp_vals(x, si, li, base)
        if cv["alive"]:
            num += ri*(1/li)*cv["f"]
            den += ri*cv["F"]
    if den == 0:
        return None
    return sp.cancel(num/den)


# ------------------------------------------------------------ hypothesis ----
def inc(v): return tuple(sorted(v))
def dec(v): return tuple(sorted(v, reverse=True))


def in_D(v):   return all(v[i] >= v[i+1] for i in range(len(v)-1))
def in_E(v):   return all(v[i] <= v[i+1] for i in range(len(v)-1))


def maj(a, b):
    """a is majorized by b (a  b): lower partial sums of a_(i) >= b's, equal total."""
    aa, bb = inc(a), inc(b)
    if sum(aa) != sum(bb): return False
    return all(sum(aa[:k]) >= sum(bb[:k]) for k in range(1, len(aa)))


def weak_super(a, b):
    """a weakly supermajorized by b: sums of k smallest of a >= b's."""
    aa, bb = inc(a), inc(b)
    return all(sum(aa[:k]) >= sum(bb[:k]) for k in range(1, len(aa)+1))


def weak_sub(a, b):
    """a weakly submajorized by b: sums of k largest of a <= b's."""
    aa, bb = dec(a), dec(b)
    return all(sum(aa[:k]) <= sum(bb[:k]) for k in range(1, len(aa)+1))


def recip_maj(a, b):
    """a reciprocally majorized by b: sums of k smallest of 1/a <= 1/b's?"""
    aa, bb = inc(a), inc(b)
    return all(sum(1/x for x in aa[:k]) <= sum(1/x for x in bb[:k])
               for k in range(1, len(aa)+1))


def t_transform(row_pair, i, j, om):
    """Apply T = om I + (1-om) Swap_ij to a 2xn matrix (rows listed)."""
    M = [list(row_pair[0]), list(row_pair[1])]
    for row in M:
        a, b = row[i], row[j]
        row[i] = om*a + (1-om)*b
        row[j] = om*b + (1-om)*a
    return M


def in_Mn(row1, row2):
    """(u,v) in M_n: (u_i-u_j)(v_i-v_j) <= 0 all i,j (antiordered)."""
    return all((row1[i]-row1[j])*(row2[i]-row2[j]) <= 0
               for i in range(len(row1)) for j in range(len(row1)))
