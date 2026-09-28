"""Shared helpers for the field audit evaluators (claim-test harness add-on).

Builds survival functions for the parametric families used in the audited
papers, both in exact rational form (ratdist, variable z = e^{-x/D}) and in
closed form (closedform, symbol x on (0, oo)).  Also provides the majorization
predicates needed to verify printed hypotheses and a small driver that maps a
printed claim onto a bounded test of the order-defining expression.
"""
import json
import math
import sympy as sp

import closedform as cf
from ratdist import Dist, ORDERS, z
import syscomp

R = sp.Rational
x = cf.x          # shared symbol used by closedform
e = sp.E


# --------------------------------------------------------------------------
# rational helpers (exact, via ratdist)
# --------------------------------------------------------------------------

def toq(v):
    return R(v)


def exp_poly(terms):
    """sum_k a_k z^{b_k} as a sympy expression in z.  terms = {b: a}."""
    return sum(a * z ** b for b, a in terms.items() if a != 0)


def ge_surv_rat(alpha, lam):
    """Dist for GE(alpha, lam): S = 1 - (1 - z^lam)^alpha, integer alpha, lam."""
    return Dist(sp.expand(1 - (1 - z ** lam) ** alpha), 0, 1, False)


def dist_from_sf(S_z, increasing=False):
    return Dist(S_z, 0, 1, increasing)


def rseries(dists):
    return Dist(sp.expand(sp.prod([d.survival for d in dists])), 0, 1, dists[0].increasing)


def rparallel(dists):
    return Dist(sp.expand(1 - sp.prod([1 - d.survival for d in dists])), 0, 1, dists[0].increasing)


def rmix(weights, dists):
    return Dist(sp.expand(sum(R(w) * d.survival for w, d in zip(weights, dists))), 0, 1,
                dists[0].increasing)


def test_rat(order, A, B):
    """exact test A <=order B for rational Dists -> (holds, witness)."""
    h, w = ORDERS[order](A, B)
    return h, w


# --------------------------------------------------------------------------
# closed-form helpers
# --------------------------------------------------------------------------

def C(survival, lo=0, hi=sp.oo):
    return cf.Closed(survival, lo, hi)


def test_cf(order, A, B, precisions=(60, 150, 400)):
    return cf.check(order, A, B, precisions=precisions)


def S_exp(lam):
    return e ** (-lam * x)


def S_weibull(lam, k):
    return e ** (-(lam * x) ** k)


def S_ge(alpha, lam):
    return 1 - (1 - e ** (-lam * x)) ** alpha


def S_es(alpha, lam, G):
    """exponentiated scale: survival 1 - G(lam*x)^alpha; G(u) is a cdf expression in u."""
    u = lam * x
    return 1 - G.subs(x, u) ** alpha


def S_scale(lam, G):
    return 1 - G.subs(x, lam * x)


def S_frechet(mu, lam, alpha):
    """Frechet with cdf exp(-((x-mu)/lam)^(-alpha)), support x > mu."""
    return 1 - e ** (-(((x - mu) / lam) ** (-alpha)))


def S_phr(Fbar, lam):
    """proportional hazard survival Fbar^lam."""
    return Fbar ** lam


def S_prhr(F, lam):
    """proportional reversed-hazard survival 1 - F^lam (lambda>=1 typically)."""
    return 1 - F ** lam


def S_po(Fbar, a):
    """proportional-odds component survival a*Fbar/(1-(1-a)*Fbar)."""
    return a * Fbar / (1 - (1 - a) * Fbar)


def po_series(Fbar, alphas):
    """S1(Fbar, a, phi) for PO generator phi(u)=a u/(1-(1-a)u)-style model:
    S_{1:n} = prod_i a_i * Fbar / prod_i (1-(1-a_i)Fbar)."""
    a = sp.Integer(1)
    den = sp.Integer(1)
    for ai in alphas:
        a = a * ai
        den = den * (1 - (1 - ai) * Fbar)
    return sp.simplify(a * Fbar / den)


def po_parallel(F, alphas):
    """S2(F, a): P(max<=x) = prod_i F_i where F_i = a_i F/(a_i F + (1-a_i)) is the
    PO cdf; survival 1 - prod_i [a_i F/(1-(1-a_i)(1-F))]."""
    prod = sp.Integer(1)
    for ai in alphas:
        prod = prod * (ai * F / (1 - (1 - ai) * (1 - F)))
    return sp.simplify(1 - prod)


def shocked_series_surv(S_series, p):
    """P(X*_{1:n} > x) = S_series(x) * prod p_i (all components survive shocks)."""
    q = R(1)
    for pi in p:
        q = q * pi
    return sp.simplify(q * S_series)


def shocked_series_members(Fbar, alphas, p):
    """componentwise shocked-PO marginals: Xi* = I_i * Xi; survival p_i S_i."""
    return [R(pi) * A_po_marginal(Fbar, a) for pi, a in zip(p, alphas)]


def A_po_marginal(Fbar, a):
    return a * Fbar / (1 - (1 - a) * Fbar)


def po_series_copula(phi_fn, Fbar, alphas):
    """Fbar_{X1:n} = phi(sum_i psi(Fbar_{ai})), psi = phi^{-1}.
    phi_fn, psi_fn are callables on sympy expressions."""
    raise NotImplementedError("use explicit generator expressions per evaluator")


def shocked_parallel_surv(S_parallel_parts, p):
    """parallel system under shocks: X_i = I_i T_i, I_i=1 (survives) w.p. p_i;
    F_{Xn:n} = prod_i (1 - p_i S_i(x)) -> survival = 1 - prod(1 - p_i S_i)."""
    prod = sp.Integer(1)
    for Si, pi in zip(S_parallel_parts, p):
        prod = prod * (1 - pi * Si)
    return sp.simplify(1 - prod)


# --------------------------------------------------------------------------
# family builders (closed form)
# --------------------------------------------------------------------------

def glfr_F(alpha, beta, lam):
    """GLFR cdf (1 - e^{-(a x + b x^2/2)})^lambda."""
    return (1 - e ** (-(alpha * x + beta * x ** 2 / 2))) ** lam


def enh_surv(alpha, beta, lam):
    """ENH( alpha, beta, lambda ) survival: 1 - [1 - exp(1-(1+lam x)^alpha)]^beta."""
    return 1 - (1 - e ** (1 - (1 + lam * x) ** alpha)) ** beta


def lindley_surv(lam):
    """standard Lindley survival."""
    return e ** (-lam * x) * (1 + lam * x / (1 + lam))


def burr_surv(alpha, beta, lam):
    """Burr XII: S = (1 + (beta x)^lambda)^{-alpha}."""
    return (1 + (beta * x) ** lam) ** (-alpha)


def harris_surv(alpha, beta, Sbar):
    """Harris: S = [beta Sbar^alpha / (1 - (1-beta) Sbar^alpha)]^{1/alpha}."""
    Sa = Sbar ** alpha
    return (beta * Sa / (1 - (1 - beta) * Sa)) ** (1 / alpha)


def es_scale_F(lam, G_expr):
    """scale cdf G(lam x)."""
    return G_expr.subs(x, lam * x)


def exp_cdf():
    return 1 - e ** (-x)


def gamma_surv(shape, scale):
    """gamma survival for integer shape >=1: e^{-x/scale} sum_{k<shape} (x/scale)^k/k!."""
    t = x / scale
    return e ** (-t) * sum(t ** k / math.factorial(k) for k in range(shape))


def beta_half_surv_poly(alpha):
    """survival of U ~ Beta(1/2, alpha), integer alpha>=1, as a polynomial in
    w = sqrt(1-u).  S_U(u) = P_α(w) where P_α(w) = c * ∫_0^w (1-s^2)^{a-1} ds
    with c = 1/∫_0^1 (1-s^2)^{a-1} ds.  Returns dict {power: coeff} in w."""
    s = sp.Symbol('s')
    poly = sp.expand((1 - s ** 2) ** (alpha - 1))
    integ = sp.Poly(sp.integrate(poly, (s, 0, s)), s)
    total = sp.integrate(poly, (s, 0, 1))
    return {b[0]: R(c) / total for (b,), c in integ.terms()}


def beta_half_surv(alpha):
    """Dist for Beta(1/2, alpha) survival in decreasing coordinate w (lo=0,hi=1)."""
    terms = beta_half_surv_poly(alpha)
    return Dist(exp_poly(terms), 0, 1, False)


def giw_cdf(alpha, theta, lam, beta):
    """GIW cdf (18): alpha^theta (1 - [1-(1-alpha)e^{-(lam/y)^beta}]^theta) /
    ((1-alpha^theta) [1-(1-alpha)e^{-(lam/y)^beta}]^theta)."""
    t = e ** (-((lam / x) ** beta))
    v = 1 - (1 - alpha) * t
    return alpha ** theta * (1 - v ** theta) / ((1 - alpha ** theta) * v ** theta)


def ixgd_surv(theta):
    """IXGD survival: 1 - (1 + theta/((1+theta)x) + theta/(2(1+theta)x^2)) e^{-theta/x}."""
    return 1 - (1 + theta / ((1 + theta) * x) + theta / (2 * (1 + theta) * x ** 2)) * e ** (-theta / x)


def kwee_surv(alpha, beta, lam):
    """KwEE survival {1 - (1 - e^{-lam x})^alpha}^beta."""
    return (1 - (1 - e ** (-lam * x)) ** alpha) ** beta


def oelg_cdf(p, beta, G):
    """OEL-G cdf: 1 - (1/log p) log[1 - (1-p) exp(-beta G/(1-G))]  (G = baseline cdf)."""
    return 1 - (1 / sp.log(p)) * sp.log(1 - (1 - p) * e ** (-beta * G / (1 - G)))


def doublexrama_surv(theta):
    D = theta ** 3 + 6
    return e ** (-theta * x) * (1 + 36 * (theta ** 3 * x ** 3 + 3 * theta ** 2 * x ** 2 + 6 * theta * x) / D ** 3)


def llogl_cdf(sigma, lam):
    """log-Lindley cdf on (0,1): x^sigma (1 + sigma(lam - log x))/(1+lam sigma)."""
    return x ** sigma * (1 + sigma * (lam - sp.log(x))) / (1 + lam * sigma)


def hlil_cdf(alpha, lam, beta):
    """half-logistic inverse Lomax cdf: G = w^alpha with w = x/(x+lam);
    F = (1-(1-G)^beta)/(1+(1-G)^beta)."""
    w = x / (x + lam)
    G = w ** alpha
    return (1 - (1 - G) ** beta) / (1 + (1 - G) ** beta)


def il_cdf(alpha, lam):
    return (1 + lam / x) ** (-alpha)


def gm_surv(alpha, beta, lam):
    """Gompertz-modified (GM) survival e^{-lam x - (alpha/beta)(e^{beta x}-1)}."""
    return e ** (-lam * x - (alpha / beta) * (e ** (beta * x) - 1))


def gmw_surv(alpha, beta, lam):
    """Gompertz-modified Weibull GM(a,b,l) with F = 1 - e^{-l x - (a/b)(e^{b x}-1)};
    same as gm_surv -- kept for paper naming."""
    return gm_surv(alpha, beta, lam)


def wg_surv(alpha, beta, gamma, w_fn):
    """W-G family: H(x) = 1 - exp(-alpha (w(gamma x))^beta); w(u) = F(u)/(1-F(u)).
    w_fn: function mapping a sympy cdf expr in x to the odds expression."""
    u = gamma * x
    wu = w_fn(u)
    return e ** (-alpha * wu ** beta)


def weibull_odds(u):
    """w(u) for W-Weibull/exponential baseline F(u)=1-e^{-u}: odds = e^{u}-1."""
    return e ** u - 1


def mphrs_surv(alpha, lam, mu, Fbar):
    """MPHRS: S = alpha Fbar(x mu)^lam / (1 - abar Fbar(x mu)^lam), abar=1-alpha."""
    Fu = Fbar.subs(x, mu * x) ** lam
    return alpha * Fu / (1 - (1 - alpha) * Fu)


# --------------------------------------------------------------------------
# Archimax / Archimedean order statistics (arxiv_2402.02945, arxiv_2407.18801)
# --------------------------------------------------------------------------

def amax_max_cdf(u_expr, n, A_n):
    """F_{Xn:n} = phi(n u A_n) where u = psi(F(x)); caller supplies phi applied
    symbolically: here phi, A fixed by closure in caller."""
    raise NotImplementedError


def second_min_surv(phi, psi_expr_list, n):
    """Fbar_{X2:n} under Archimedean *survival* copula:
    sum_i psi( sum_{j != i} phi(Sbar_j) ) - (n-1) psi( sum_i phi(Sbar_j) )."""
    from sympy import Rational as Rat
    tot = sum(psi_expr_list)
    s = 0
    for i in range(n):
        s = s + phi(tot - psi_expr_list[i])
    return sp.simplify(s - (n - 1) * phi(tot))


def second_min_surv_iid(psi_sym, phi_sym, Sbars, n):
    """same but psi applied to each marginal survival; psi_sym/phi_sym are sympy
    unapplied functions (use sympy.Function or lambdas)."""
    psis = [phi_sym(Sb) for Sb in Sbars]   # phi = psi^{-1} applied to survivals
    tot = sum(psis)
    s = sum(psi_sym(tot - pj) for pj in psis)
    return sp.simplify(s - (n - 1) * psi_sym(tot))


# --------------------------------------------------------------------------
# majorization predicates (exact rational checks; z-order vectors)
# --------------------------------------------------------------------------

def asc(v):
    return sorted(R(t) for t in v)


def desc(v):
    return sorted((R(t) for t in v), reverse=True)


def weak_sub(a, b):
    """a weakly SUBmajorized by b (a ~_w b): sums of largest j of a <= those of b."""
    na, nb = len(a), len(b)
    da, db = desc(a), desc(b)
    return all(sum(da[:j]) <= sum(db[:j]) for j in range(1, min(na, nb) + 1))


def weak_super(a, b):
    """a weakly SUPERmajorized by b (a ~^w b): sums of smallest j of a <= b's."""
    aa, ab = asc(a), asc(b)
    return all(sum(aa[:j]) <= sum(ab[:j]) for j in range(1, min(len(a), len(b)) + 1))


def majorized(a, b):
    return weak_sub(a, b) and sum(a) == sum(b)


def p_larger(a, b):
    """a is p-larger than b: prod of smallest j of a <= prod of smallest j of b."""
    import functools, operator
    aa, ab = asc(a), asc(b)
    for j in range(1, len(a) + 1):
        pa = functools.reduce(operator.mul, aa[:j], R(1))
        pb = functools.reduce(operator.mul, ab[:j], R(1))
        if pa > pb:
            return False
    return True


def f_majorize(a, b, f, kind="sub"):
    """a weakly f-sub/supermajorized by b: compare partial sums of f-values."""
    fa = [f(R(t)) for t in a]
    fb = [f(R(t)) for t in b]
    return weak_sub(fa, fb) if kind == "sub" else weak_super(fa, fb)


# --------------------------------------------------------------------------
# closed-form aggregate sums (Bernoulli mixtures of exponentials / uniforms)
# --------------------------------------------------------------------------

def exp_sum_surv_piece(scales):
    """survival of sum of independent Exp(scale_i) (rate 1/scale_i) as a linear
    combination of exponentials e^{-x/scale_i} with rational coefficients.
    Requires pairwise distinct scales.  Returns {scale_i: coeff}."""
    out = {}
    n = len(scales)
    for i in range(n):
        li = scales[i]
        c = R(1)
        for j in range(n):
            if j != i:
                # coefficient for e^{-x/li} in hypoexponential survival:
                # prod_{j!=i} lj/(lj - li)
                c = c * R(scales[j]) / R(scales[j] - li)
        out[li] = c
    return out


def bern_exp_sum_terms(probs, scales):
    """survival of sum_i I_i X_i, I_i ~ Bern(p_i), X_i ~ Exp(scale_i), as dict
    {exponent_denominator_scale: coeff} in z = e^{-x/D}; caller multiplies
    exponent D/scale.  Returns terms dict {scale: coeff} summing over subsets
    (empty subset contributes point mass at 0 => coeff with scale = oo)."""
    import itertools
    terms = {}
    n = len(scales)
    for mask in range(2 ** n):
        idx = [i for i in range(n) if mask & (1 << i)]
        w = R(1)
        for i in range(n):
            w = w * (probs[i] if i in idx else (1 - probs[i]))
        if not idx:
            # sum = 0: survival = 1 for x<0? for x>0 P(sum>x)=0 except x=0.
            continue
        for li, c in exp_sum_surv_piece([scales[i] for i in idx]).items():
            terms[li] = terms.get(li, R(0)) + w * c
    return terms


def bern_unif_sum_pieces(probs, scales):
    """survival of sum_i I_i U_i, U_i ~ Uniform(0, scales[i]), as a list of
    (lo, hi, sympy poly in x) pieces covering (0, sum scales).  n must be <= 3
    (only single and double convolutions supported exactly)."""
    import itertools
    pieces = []
    n = len(scales)
    total = sum(R(s) for s in scales)
    for mask in range(2 ** n):
        idx = [i for i in range(n) if mask & (1 << i)]
        w = R(1)
        for i in range(n):
            w = w * (probs[i] if i in idx else (1 - probs[i]))
        if w == 0:
            continue
        if not idx:
            pieces.append(((R(0), total), w))          # mass at 0 -> S = w*1
        elif len(idx) == 1:
            a = scales[idx[0]]
            pieces.append(((R(0), R(a)), w * (1 - x / a)))
        elif len(idx) == 2:
            a, b = sorted(R(scales[i]) for i in idx)
            pieces.append(((R(0), a), w * (1 - x ** 2 / (2 * a * b))))
            pieces.append(((a, b), w * (1 - (2 * a * x - a * a) / (2 * a * b))))
            pieces.append(((b, a + b), w * (a + b - x) ** 2 / (2 * a * b)))
        else:
            raise NotImplementedError("aggregate sum convolution limited to pairs")
    return pieces


def piecewise_st(piecesX, piecesY):
    """exact sign check of S_Y - S_X >= 0 on (0, supp): evaluate difference on a
    rational grid inside each break-interval using mpmath interval arithmetic;
    returns (holds, witness, n_undecided)."""
    cuts = sorted(set(b for pieces in (piecesX, piecesY) for (lo, hi), _ in pieces
                      for b in (lo, hi)))
    holds = True
    wit = None
    und = 0
    for lo, hi in zip(cuts, cuts[1:]):
        if lo == hi:
            continue
        # grid inside (lo, hi)
        for k in range(1, 9):
            t = R(lo) + (R(hi) - R(lo)) * R(k) / 9
            eX = sum(c.subs(x, t) for (rg, c) in piecesX if rg[0] <= t <= rg[1])
            eY = sum(c.subs(x, t) for (rg, c) in piecesY if rg[0] <= t <= rg[1])
            v = sp.nsimplify(eY - eX)
            if v < 0:
                holds = False
                wit = str(t)
            elif v == 0:
                und += 1
    return holds, wit, und


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------

def rec(record, status, order=None, instances=0, witness=None, undecided=0, note=None):
    d = {
        "claim": record["claim"],
        "order": order or record["conclusion"]["order"],
        "status": status,
        "instances": instances,
        "witness": witness,
        "undecided_points": undecided,
    }
    if note:
        d["note"] = note
    return d


def emit(path, results):
    with open(path, "w") as fh:
        json.dump(results, fh, indent=1)


def check_dist(order, A, B, precisions=(60, 150, 400)):
    """unified check for either Closed or Dist arguments."""
    if isinstance(A, Dist):
        h, w = ORDERS[order](A, B)
        return h, w, 0
    return cf.check(order, A, B, precisions=precisions)
