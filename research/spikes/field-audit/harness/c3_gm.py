"""C3 for doi:10.1080/03610926.2021.1919898 refutations.

GM(a,b,l) hazard: r(x)=l + a e^{b x}; S(x)=exp(-l x - (a/b)(e^{bx}-1)).
Thinned: S_i = p_i S_i.  Series min hazard = sum of component hazards;
series density = -d(S_min).  Parallel max: F = prod(1 - S_i).

Refuted records:
  Counterexample 1 (a/i):  lr fails  (alpha vs alpha*)
  Counterexample 1 (b/ii): lr fails  (beta vs beta*)
  Counterexample 2:        st fails  (parallel maxima)
  Counterexample 3:        st fails  (parallel maxima, 1/beta maj)
  Theorem 21:              hr fails for thinned series (X1:n <=hr Y1:n)
"""
from mpmath import mp, mpf, exp, diff

mp.dps = 200


def S_gm(a, b, l, xv):
    return exp(-mpf(l) * xv - (mpf(a) / mpf(b)) * (exp(mpf(b) * xv) - 1))


def S_min(params, xv):
    s = mpf(1)
    for (p, a, b, l) in params:
        s *= mpf(p) * S_gm(a, b, l, xv)
    return s


def f_min(params, xv):
    return -diff(lambda t: S_min(params, t), xv)


def S_max(params, xv):
    f = mpf(1)
    for (p, a, b, l) in params:
        f *= 1 - mpf(p) * S_gm(a, b, l, xv)
    return 1 - f


def hr_diff(paramsX, paramsY, xv):
    """E_hr for X <=hr Y:  f_X S_Y - f_Y S_X."""
    return f_min(paramsX, xv) * S_min(paramsY, xv) \
        - f_min(paramsY, xv) * S_min(paramsX, xv)


def lr_expr(paramsX, paramsY, xv):
    """E_lr for X <=lr Y:  f_X' S-ish... use density-ratio derivative:
    d/dx [f_Y/f_X] >= 0 iff X <=lr Y; equivalently
    f_Y' f_X - f_Y f_X' >= 0."""
    fX = f_min(paramsX, xv)
    fY = f_min(paramsY, xv)
    fXp = diff(lambda t: f_min(paramsX, t), xv)
    fYp = diff(lambda t: f_min(paramsY, t), xv)
    return fYp * fX - fY * fXp


one = mpf(1)

# --- Counterexample 1 (i)/(a): alpha vs alpha* ---
a1 = [mpf("0.1"), mpf(20)]
a2 = [mpf("2.1"), mpf(18)]
bb = [mpf("0.2"), mpf("0.1")]
ll = [mpf("0.6"), mpf("0.5")]
PX = [(one, a1[0], bb[0], ll[0]), (one, a1[1], bb[1], ll[1])]
PY = [(one, a2[0], bb[0], ll[0]), (one, a2[1], bb[1], ll[1])]
print("Cex1(i): E_lr (should dip below 0):")
for xv in (mpf("0.02"), mpf("0.05"), mpf("0.1"), mpf("0.3"), mpf(1),
           mpf(3)):
    print("  x=%s  E=%s" % (xv, mp.nstr(lr_expr(PX, PY, xv), 12)))

# --- Counterexample 1 (ii)/(b): beta vs beta* ---
aa = [mpf(20), mpf("0.1")]
b1 = [mpf("0.8"), mpf("0.2")]
b2 = [mpf("0.7"), mpf("0.3")]
ll2 = [mpf("0.5"), mpf("0.6")]
PXb = [(one, aa[0], b1[0], ll2[0]), (one, aa[1], b1[1], ll2[1])]
PYb = [(one, aa[0], b2[0], ll2[0]), (one, aa[1], b2[1], ll2[1])]
print("Cex1(ii): E_lr:")
for xv in (mpf("0.05"), mpf("0.1"), mpf("0.3"), mpf(1), mpf(3), mpf(10)):
    print("  x=%s  E=%s" % (xv, mp.nstr(lr_expr(PXb, PYb, xv), 12)))

# --- Counterexample 2: parallel st fails ---
aa2 = [mpf("0.2"), mpf("0.1")]
aa2s = [mpf("0.18"), mpf("0.12")]
bb2 = [mpf(2), mpf(1)]
lc = mpf("0.6")
QX = [(one, a, b, lc) for a, b in zip(aa2, bb2)]
QY = [(one, a, b, lc) for a, b in zip(aa2s, bb2)]
print("Cex2: S_maxX - S_maxY (sign change expected):")
for xv in (mpf("0.1"), mpf("0.3"), mpf("0.5"), mpf(1), mpf(2), mpf(5)):
    print("  x=%s  D=%s" % (xv, mp.nstr(S_max(QX, xv) - S_max(QY, xv), 12)))

# --- Counterexample 3: 1/beta majorization ---
aa3 = [mpf("0.1"), mpf("0.2")]
b3 = [mpf("0.5"), mpf(1)]
b3s = [mpf("0.625"), mpf("0.7142857142857143")]
lc3 = mpf("0.02")
RX = [(one, a, b, lc3) for a, b in zip(aa3, b3)]
RY = [(one, a, b, lc3) for a, b in zip(aa3, b3s)]
print("Cex3: S_maxX - S_maxY:")
for xv in (mpf("0.5"), mpf(1), mpf(2), mpf(5), mpf(10), mpf(30)):
    print("  x=%s  D=%s" % (xv, mp.nstr(S_max(RX, xv) - S_max(RY, xv), 12)))

# --- Theorem 21: beta-majorized thinned series, X1:n <=hr Y1:n fails ---
TX = [(mpf("0.5"), mpf(2), mpf(3), mpf("0.5")),
      (mpf("0.5"), mpf(1), mpf(1), mpf("0.25"))]
TY = [(mpf(1) / 3, mpf(2), mpf(2), mpf("0.5")),
      (mpf(1) / 3, mpf(1), mpf(2), mpf("0.25"))]
print("Thm21: E_hr (X <=hr Y; failure iff <0):")
for xv in (mpf("1e-12"), mpf("0.01"), mpf("0.1"), mpf("0.5"), mpf(1),
           mpf(3)):
    print("  x=%s  E=%s" % (xv, mp.nstr(hr_diff(TX, TY, xv), 12)))
