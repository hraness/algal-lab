#!/usr/bin/env python3
"""Symbolic verification (SymPy) of every algebraic identity used in the proofs.

Each identity is checked by exact symbolic simplification.  A numerical
high-precision spot check is also run for each, so that a failure of the
simplifier is distinguishable from a false identity.
"""
import random
import sympy as sp

random.seed(20260925)
FAILED = []


def check(name, expr, symbols):
    """expr must be identically zero."""
    ok_sym = sp.simplify(sp.expand(sp.simplify(expr.rewrite(sp.exp)))) == 0
    if not ok_sym:
        ok_sym = sp.simplify(expr.rewrite(sp.exp).together()) == 0
    ok_num = True
    for _ in range(5):
        subs = {s: sp.Rational(random.randint(1, 40), random.randint(1, 13)) for s in symbols}
        val = sp.N(expr.subs(subs), 40)
        if val.has(sp.nan) or val.has(sp.zoo) or not val.is_finite or abs(val) > sp.Float("1e-30"):
            ok_num = False
    status = "ok" if (ok_sym and ok_num) else f"FAIL (symbolic={ok_sym}, numeric={ok_num})"
    print(f"{name}: {status}")
    if not (ok_sym and ok_num):
        FAILED.append(name)


x, y, c, z, r, s, t, eps, a, b, K, tau, H0 = sp.symbols(
    "x y c z r s t epsilon a b K tau H0", real=True)
m, E, PE, q = sp.symbols("m E P_E q", positive=True)
u1, u2, u3, u4 = sp.symbols("u1:5", real=True)
U = (u1, u2, u3, u4)

# --- softmax means on four symbolic coordinates -----------------------------
S_neg = sum(sp.exp(-ui) for ui in U)
F = sum(ui * sp.exp(-ui) for ui in U) / S_neg               # B_{-1}
Z_pos = sum(sp.exp(ui) for ui in U)
H = sum(ui * sp.exp(ui) for ui in U) / Z_pos                # B_{+1}

check("(2) dF/du_1 = e^{-u_1}(1 - u_1 + F)/S",
      sp.diff(F, u1) - sp.exp(-u1) * (1 - u1 + F) / S_neg, U)
check("dH/du_1 = e^{u_1}(1 + u_1 - H)/Z",
      sp.diff(H, u1) - sp.exp(u1) * (1 + u1 - H) / Z_pos, U)

# --- reflection, shift and scaling identities (n = 3) -----------------------
def B(tt, vec):
    return sum(v * sp.exp(tt * v) for v in vec) / sum(sp.exp(tt * v) for v in vec)

V3 = (u1, u2, u3)
check("reflection B_t(x) = a + b - B_{-t}(a + b - x)",
      B(t, V3) - (a + b - B(-t, tuple(a + b - v for v in V3))), (u1, u2, u3, t, a, b))
check("shift B_t(x + s 1) = B_t(x) + s",
      B(t, tuple(v + s for v in V3)) - (B(t, V3) + s), (u1, u2, u3, t, s))
check("scaling B_{-t}(x) = a + F(t(x - a))/t",
      B(-t, V3) - (a + B(-1, tuple(t * (v - a) for v in V3)) / t), (u1, u2, u3, t, a))

# --- the pair numerator N and identity (3) ----------------------------------
A_, B_ = sp.exp(-x), sp.exp(-y)
N_def = (m + A_ + B_) * (A_ * (1 - x) - B_ * (1 - y)) + (A_ - B_) * (x * A_ + y * B_)
N_claim = m * ((1 - x) * A_ - (1 - y) * B_) + A_ ** 2 - B_ ** 2 + 2 * (y - x) * A_ * B_
check("N expansion", N_def - N_claim, (x, y, m))
N_cz = N_claim.subs({x: c - z, y: c + z})
rhs3 = m * (1 - c + z * sp.coth(z)) + 2 * sp.exp(-c) * (sp.cosh(z) + z / sp.sinh(z))
check("(3) N / (2 e^{-c} sinh z) identity", N_cz / (2 * sp.exp(-c) * sp.sinh(z)) - rhs3, (c, z, m))

# --- auxiliary monotonicity lemmas (derivative identities) ------------------
check("d/dz [z cosh z - sinh z] = z sinh z",
      sp.diff(z * sp.cosh(z) - sp.sinh(z), z) - z * sp.sinh(z), (z,))
check("d/dz [sinh(2z)/2 + z - 2 sinh z] = 2 cosh z (cosh z - 1)",
      sp.diff(sp.sinh(2 * z) / 2 + z - 2 * sp.sinh(z), z) - 2 * sp.cosh(z) * (sp.cosh(z) - 1), (z,))
check("cosh z + z/sinh z - 2 = [sinh(2z)/2 + z - 2 sinh z]/sinh z",
      (sp.cosh(z) + z / sp.sinh(z) - 2) - (sp.sinh(2 * z) / 2 + z - 2 * sp.sinh(z)) / sp.sinh(z), (z,))
check("d/dr [(1 + r^2/3) sinh r - r cosh r] = (r/3)(r cosh r - sinh r)",
      sp.diff((1 + r ** 2 / 3) * sp.sinh(r) - r * sp.cosh(r), r) - (r / 3) * (r * sp.cosh(r) - sp.sinh(r)), (r,))
check("d/dr [tanh r - r + r^3/3] = r^2 - tanh^2 r",
      sp.diff(sp.tanh(r) - r + r ** 3 / 3, r) - (r ** 2 - sp.tanh(r) ** 2), (r,))
check("(cosh z - 1)/sinh z = tanh(z/2)", (sp.cosh(z) - 1) / sp.sinh(z) - sp.tanh(z / 2), (z,))
check("sinh z/(cosh z - 1) = coth(z/2)", sp.sinh(z) / (sp.cosh(z) - 1) - sp.coth(z / 2), (z,))
check("g'(c) = -m - 4 e^{-c}", sp.diff(m * (2 - c) + 4 * sp.exp(-c), c) + m + 4 * sp.exp(-c), (c, m))

# --- box necessity: Delta(c, z) with m zero coordinates, identity (4) -------
F_split = ((c - z) * sp.exp(-(c - z)) + (c + z) * sp.exp(-(c + z))) / (m + sp.exp(-(c - z)) + sp.exp(-(c + z)))
F_equal = 2 * c * sp.exp(-c) / (m + 2 * sp.exp(-c))
qq = sp.exp(-c)
Delta_claim = 2 * qq * (m * c * (sp.cosh(z) - 1) - z * sp.sinh(z) * (m + 2 * qq)) / ((m + 2 * qq * sp.cosh(z)) * (m + 2 * qq))
check("(4) Delta(c,z) closed form", F_split - F_equal - Delta_claim, (c, z, m))
ser = sp.series(Delta_claim, z, 0, 4).removeO()
coef2 = sp.simplify(ser.coeff(z, 2) - qq * (m * (c - 2) - 4 * qq) / (m + 2 * qq) ** 2)
print("Delta series: z^0,z^1,z^3 coefficients:", sp.simplify(ser.coeff(z, 0)), sp.simplify(ser.coeff(z, 1)), sp.simplify(ser.coeff(z, 3)), "; z^2 coefficient matches:", coef2 == 0)
if not (coef2 == 0 and sp.simplify(ser.coeff(z, 0)) == 0 and sp.simplify(ser.coeff(z, 1)) == 0 and sp.simplify(ser.coeff(z, 3)) == 0):
    FAILED.append("Delta series")
# Sign factorisation used for the interior violation.
check("numerator/(z sinh z) = mC tanh(z/2)/z - (m + 2q)",
      (m * c * (sp.cosh(z) - 1) - z * sp.sinh(z) * (m + 2 * q)) / (z * sp.sinh(z)) - (m * c * sp.tanh(z / 2) / z - (m + 2 * q)), (c, z, m, q))
eta = 1 - 2 * (m + 2 * q) / (m * c)
check("m C eta / 2 = m C / 2 - (m + 2q)", m * c * eta / 2 - (m * c / 2 - (m + 2 * q)), (c, m, q))
check("eta = -g(C)/(m C) with q = e^{-C}",
      (1 - 2 * (m + 2 * sp.exp(-c)) / (m * c)) + (m * (2 - c) + 4 * sp.exp(-c)) / (m * c), (c, m))

# --- n = 2 formula and the equal-vector split -------------------------------
check("n = 2: F(c - z, c + z) = c - z tanh z", F_split.subs(m, 0) - (c - z * sp.tanh(z)), (c, z))
split_pos = ((c - z) * sp.exp(c - z) + (c + z) * sp.exp(c + z) + m * c * sp.exp(c)) / (sp.exp(c - z) + sp.exp(c + z) + m * sp.exp(c))
check("B_{+1}(split of equal vector) = c + 2 z sinh z/(m + 2 cosh z)",
      split_pos - (c + 2 * z * sp.sinh(z) / (m + 2 * sp.cosh(z))), (c, z, m))
split_neg = ((c - z) * sp.exp(-(c - z)) + (c + z) * sp.exp(-(c + z)) + m * c * sp.exp(-c)) / (sp.exp(-(c - z)) + sp.exp(-(c + z)) + m * sp.exp(-c))
check("B_{-1}(split of equal vector) = c - 2 z sinh z/(m + 2 cosh z)",
      split_neg - (c - 2 * z * sp.sinh(z) / (m + 2 * sp.cosh(z))), (c, z, m))
# Local expansion near an interior all-equal vector: B_tau = x_1 + (2 tau/n) eps^2 + O(eps^4).
n_sym = sp.symbols("n", positive=True)
loc = 2 * eps * sp.sinh(tau * eps) / (2 * sp.cosh(tau * eps) + n_sym - 2)
loc_ser = sp.series(loc, eps, 0, 4).removeO()
print("local split expansion coefficient of eps^2 equals 2 tau/n:", sp.simplify(loc_ser.coeff(eps, 2) - 2 * tau / n_sym) == 0)
if sp.simplify(loc_ser.coeff(eps, 2) - 2 * tau / n_sym) != 0:
    FAILED.append("local expansion")

# --- simplex, positive temperature ------------------------------------------
Hv = (PE + 2 * eps * sp.exp(eps)) / (E + 2 * sp.exp(eps))
Hv2 = (PE + (eps - z) * sp.exp(eps - z) + (eps + z) * sp.exp(eps + z)) / (E + sp.exp(eps - z) + sp.exp(eps + z))
claim3 = 2 * sp.exp(eps) * (sp.cosh(z) - 1) / (E + 2 * sp.exp(eps) * sp.cosh(z)) * (eps - Hv + z * sp.coth(z / 2))
check("simplex (3): H(v') - H(v) closed form", Hv2 - Hv - claim3, (E, PE, eps, z))
check("f'(s) = e^s (2 + s - H) for f(s) = e^s (1 + s - H)",
      sp.diff(sp.exp(s) * (1 + s - H0), s) - sp.exp(s) * (2 + s - H0), (s, H0))
phi = K * sp.exp(K) / (sp.exp(K) + n_sym - 1)
check("phi'(K) = e^K [e^K + (n-1)(1+K)]/(e^K + n - 1)^2",
      sp.diff(phi, K) - sp.exp(K) * (sp.exp(K) + (n_sym - 1) * (1 + K)) / (sp.exp(K) + n_sym - 1) ** 2, (K, n_sym))
check("phi(K) <= 2 iff (K-2)e^K <= 2(n-1): (phi - 2)(e^K + n - 1) = (K-2)e^K - 2(n-1)",
      (phi - 2) * (sp.exp(K) + n_sym - 1) - ((K - 2) * sp.exp(K) - 2 * (n_sym - 1)), (K, n_sym))
check("z coth(z/2) bound: 2 + (2r)^2/6 = 2 + 2 r^2/3", 2 + (2 * r) ** 2 / 6 - (2 + 2 * r ** 2 / 3), (r,))
check("Lambert form: (n-2)(c-2)e^c = (n-2) e^2 (c-2) e^{c-2}",
      (n_sym - 2) * (c - 2) * sp.exp(c) - (n_sym - 2) * sp.exp(2) * (c - 2) * sp.exp(c - 2), (c, n_sym))
check("Lambert form: (d-2)e^d = e^2 (d-2) e^{d-2}",
      (c - 2) * sp.exp(c) - sp.exp(2) * (c - 2) * sp.exp(c - 2), (c,))

# --- Lehmer-mean limit used for the prior-art transfer (n = 3) ---------------
p = tau / eps
Lp = sum(sp.exp(eps * v) ** p for v in V3) / sum(sp.exp(eps * v) ** (p - 1) for v in V3)
Zx = lambda tt: sum(sp.exp(tt * v) for v in V3)
check("log L_p(e^{eps x})/eps = [log Z(tau) - log Z(tau - eps)]/eps",
      sp.log(Lp) / eps - (sp.log(Zx(tau)) - sp.log(Zx(tau - eps))) / eps, (u1, u2, u3, tau, eps))
lim = sp.limit((sp.log(Zx(tau)) - sp.log(Zx(tau - eps))) / eps, eps, 0)
check("limit as eps -> 0 equals B_tau(x)", lim - B(tau, V3), (u1, u2, u3, tau))

print("FAILED:", FAILED if FAILED else "none")
raise SystemExit(1 if FAILED else 0)
