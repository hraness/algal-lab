"""Independent audit of eval_doi_10.1214_18-bjps410 refutations.

Paper conventions (verified from PDF text layer):
  Def 2(ii): u ~<^w_p v on Dn^pi (Gn^pi): u,v in the cone (x_{pi1} >= ... >= x_{pin},
             >0 for G) and  sum_{j=i}^n p_{pi_j} u_{pi_j} >= sum_{j=i}^n p_{pi_j} v_{pi_j}
             for i=1..n.   (SUFFIX sums, >=)  -- the PRINTED reading.
             The eval docstring used prefix <= (weak SUBmajorization).
  Def 3:     u ~<^uo v: sum_{i=1}^k u_i <= sum_{i=1}^k v_i (k=1..n-1), totals equal.
             Positional, no rearrangement.
  EGG CDF:   F(t;a,nu,tau,lam) = [ P(tau/nu, (lam t)^nu) ]^a  where P is the
             regularized lower incomplete gamma ratio  gamma(s,z)/Gamma(s)
             with s = tau/nu (printed: int_0^t nu lam^tau u^{tau-1} e^{-(lam u)^nu}
             du / Gamma(tau/nu), all to the power alpha).
             Checks: nu=tau=1 -> (1-e^{-lam t})^a (GE);  tau=nu -> (1-e^{-(lam t)^nu})^a
             (exponentiated Weibull); nu=1 -> exponentiated gamma.

All numerics at 110 dps with mpmath; no reuse of eval model code.
"""
import json
import mpmath as mp

mp.mp.dps = 110


# ---------------- EGG model (analytic) ----------------
def egg_cdf(t, a, nu, tau, lam):
    t, a, nu, tau, lam = map(mp.mpf, (t, a, nu, tau, lam))
    z = (lam * t) ** nu
    return mp.gammainc(tau / nu, 0, z, regularized=True) ** a


def egg_pdf(t, a, nu, tau, lam):
    """d/dt g^a = a g^{a-1} g', g'(t) = nu lam^tau t^{tau-1} e^{-(lam t)^nu}/Gamma(tau/nu)."""
    t, a, nu, tau, lam = map(mp.mpf, (t, a, nu, tau, lam))
    z = (lam * t) ** nu
    P = mp.gammainc(tau / nu, 0, z, regularized=True)
    base = nu * lam ** tau * t ** (tau - 1) * mp.exp(-z) / mp.gamma(tau / nu)
    return a * P ** (a - 1) * base


def max_cdf(t, alphas, nu, tau, lams):
    p = mp.mpf(1)
    for a, l in zip(alphas, lams):
        p *= egg_cdf(t, a, nu, tau, l)
    return p


def max_surv(t, alphas, nu, tau, lams):
    return 1 - max_cdf(t, alphas, nu, tau, lams)


def max_pdf(t, alphas, nu, tau, lams):
    F = max_cdf(t, alphas, nu, tau, lams)
    s = mp.mpf(0)
    for a, l in zip(alphas, lams):
        Fi = egg_cdf(t, a, nu, tau, l)
        s += egg_pdf(t, a, nu, tau, l) / Fi
    return F * s


def max_rh(t, alphas, nu, tau, lams):
    """reversed hazard rate f/F of the max."""
    return sum(egg_pdf(t, a, nu, tau, l) / egg_cdf(t, a, nu, tau, l)
               for a, l in zip(alphas, lams))


def max_hr(t, alphas, nu, tau, lams):
    return max_pdf(t, alphas, nu, tau, lams) / max_surv(t, alphas, nu, tau, lams)


# ---------------- printed majorization definitions ----------------
def cone_member(v, perm, positive=False):
    seq = [mp.mpf(v[p - 1]) for p in perm]
    if any(seq[i] < seq[i + 1] for i in range(len(seq) - 1)):
        return False
    return (not positive) or all(s > 0 for s in seq)


def weak_maj_printed(u, v, p, perm):
    """printed Def 2(ii): suffix sums >= on the permuted order, plus cone membership
    checked by caller."""
    n = len(u)
    res = []
    for i in range(1, n + 1):
        su = sum(p[perm[j - 1] - 1] * mp.mpf(u[perm[j - 1] - 1]) for j in range(i, n + 1))
        sv = sum(p[perm[j - 1] - 1] * mp.mpf(v[perm[j - 1] - 1]) for j in range(i, n + 1))
        res.append(bool(su >= sv))
    return all(res), res


def weak_maj_prefix(u, v, p, perm):
    """evaluator's convention: prefix sums <= on the permuted order."""
    n = len(u)
    res = []
    for i in range(1, n + 1):
        su = sum(p[perm[j - 1] - 1] * mp.mpf(u[perm[j - 1] - 1]) for j in range(1, i + 1))
        sv = sum(p[perm[j - 1] - 1] * mp.mpf(v[perm[j - 1] - 1]) for j in range(1, i + 1))
        res.append(bool(su <= sv))
    return all(res), res


def uo_maj(a, b):
    n = len(a)
    conds = [bool(sum(mp.mpf(str(t)) for t in a[:k]) <= sum(mp.mpf(str(t)) for t in b[:k]))
             for k in range(1, n)]
    tot = mp.almosteq(sum(mp.mpf(str(t)) for t in a), sum(mp.mpf(str(t)) for t in b))
    return all(conds) and tot, conds + [bool(tot)]


# ---------------- order scans ----------------
def scan_min(fn, lo, hi, npts=2000):
    lo, hi = mp.mpf(lo), mp.mpf(hi)
    best = (mp.inf, None)
    for i in range(npts):
        t = lo * (hi / lo) ** (mp.mpf(i) / (npts - 1))
        v = fn(t)
        if v < best[0]:
            best = (v, t)
    return best


def scan_monotonic(ratio_fn, lo, hi, npts=1500):
    """returns (min successive difference, t-where) for ratio_fn over grid;
    negative => ratio decreases somewhere => monotonicity fails."""
    lo, hi = mp.mpf(lo), mp.mpf(hi)
    prev_t, prev_v = None, None
    worst = (mp.inf, None)
    for i in range(npts):
        t = lo * (hi / lo) ** (mp.mpf(i) / (npts - 1))
        v = ratio_fn(t)
        if prev_v is not None:
            d = v - prev_v
            if d < worst[0]:
                worst = (d, (prev_t, t))
        prev_t, prev_v = t, v
    return worst


GE = ('1', '1')  # (nu, tau) for GE sub-model


def systems(name):
    """(nu, tau, alpha, beta, lambdas, mus, perm) for each printed eval scenario."""
    R = mp.mpf
    if name == 'FIG1':      # Theorem 6 example: nu=.4 tau=.8
        return (R('0.4'), R('0.8'), [R('1'), R('3'), R('5'), R('0.6')],
                [R('4.6'), R('4.4'), R('0.5'), R('0.1')],
                [R('9'), R('6'), R('1'), R('0.7')], [R('8'), R('5'), R('0.8'), R('0.75')],
                (1, 2, 3, 4))
    if name == 'FIG2':      # Remark 4 example: nu=.5 tau=2, pi=(4,3,2,1)
        return (R('0.5'), R('2'), [R('4'), R('0.8'), R('3.3'), R('5')],
                [R('1'), R('3'), R('2.1'), R('7')],
                [R('2'), R('11'), R('12'), R('13')], [R('5'), R('6'), R('10'), R('14')],
                (4, 3, 2, 1))
    if name == 'EXTRA':     # eval's extra st/rh case
        return (R('1'), R('1'), [R('1'), R('2'), R('3')], [R('3'), R('2'), R('1')],
                [R('9'), R('6'), R('1')], [R('8'), R('5'), R('0.5')], (1, 2, 3))
    if name == 'THM9_eval':  # eval's synthetic Theorem-9 instance
        return (R('1'), R('1'), [R('2'), R('3')], [R('4'), R('1')],
                [R('10'), R('9')], [R('8'), R('5')], (1, 2))
    if name == 'THM9_print':  # printed Theorem-9 example, nu=0.5 tau=0.8
        return (R('0.5'), R('0.8'), [R('4'), R('0.8'), R('3.3'), R('5')],
                [R('1'), R('3'), R('2.1'), R('7')],
                [mp.sqrt(2), mp.sqrt(11), mp.sqrt(12), mp.sqrt(13)],
                [mp.sqrt(5), mp.sqrt(6), mp.sqrt(10), mp.sqrt(14)], (1, 2, 3, 4))
    if name == 'LEMMA8iii':
        return (R('1'), R('1'), [R('2'), R('3'), R('1')], None,
                [R('8'), R('2'), R('2')], [R('5'), R('2'), R('2')], (1, 2, 3))
    raise KeyError(name)


def premise_report(name, use_log, perm=None, positive=None):
    nu, tau, a, b, lam, mu, pi0 = systems(name)
    perm = perm or pi0
    if positive is None:
        positive = use_log is False   # Gn for raw scales, Dn for log scales
    u = [mp.log(m) for m in mu] if use_log else list(mu)
    v = [mp.log(l) for l in lam] if use_log else list(lam)
    mem = cone_member(u, perm, positive) and cone_member(v, perm, positive)
    okP, detP = weak_maj_printed(u, v, a, perm)
    okE, detE = weak_maj_prefix(u, v, a, perm)
    if b is not None:
        ap = [a[p - 1] for p in perm]; bp = [b[p - 1] for p in perm]
        okU, detU = uo_maj(ap, bp)
        okU0, detU0 = uo_maj(list(a), list(b))
    else:
        okU, detU, okU0, detU0 = None, None, None, None
    return dict(member=mem, printed_suffix=okP, detP=detP,
                eval_prefix=okE, detE=detE, uo_permuted=okU, uo_plain=okU0,
                detU=detU)


def conclusion_scan(name, order):
    """Test claim Y <=order X (mu,beta system <= lambda,alpha system)."""
    nu, tau, a, b, lam, mu, pi = systems(name)
    bb = b if b is not None else a
    if order == 'st':
        fn = lambda t: max_surv(t, a, nu, tau, lam) - max_surv(t, bb, nu, tau, mu)
        return scan_min(fn, '1e-8', '1e5')
    if order == 'rh':
        fn = lambda t: max_rh(t, a, nu, tau, lam) - max_rh(t, bb, nu, tau, mu)
        return scan_min(fn, '1e-8', '1e5')
    if order == 'hr':
        fn = lambda t: max_hr(t, bb, nu, tau, mu) - max_hr(t, a, nu, tau, lam)
        return scan_min(fn, '1e-8', '1e4')
    if order == 'lr':
        return scan_monotonic(lambda t: max_pdf(t, a, nu, tau, lam)
                              / max_pdf(t, bb, nu, tau, mu), '1e-6', '1e4')
    raise KeyError(order)


if __name__ == '__main__':
    # sanity of the EGG implementation: GE sub-model vs closed form
    t = mp.mpf('1.7')
    got = egg_cdf(t, '3.5', '1', '1', '2.5')
    want = (1 - mp.e ** (-mp.mpf('2.5') * t)) ** mp.mpf('3.5')
    assert abs(got - want) < mp.mpf('1e-90')
    got3 = egg_cdf(t, '2', '2', '2', '0.7')
    want3 = (1 - mp.e ** (-(mp.mpf('0.7') * t) ** 2)) ** 2
    assert abs(got3 - want3) < mp.mpf('1e-90')
    print('model sanity OK')

    for nm, use_log in [('FIG1', True), ('EXTRA', True), ('FIG2', False),
                        ('THM9_eval', False)]:
        print('=' * 70)
        print(nm, 'premises:', premise_report(nm, use_log))
        print('  st scan (min S_X - S_Y, t):', conclusion_scan(nm, 'st'))
        print('  rh scan (min rh_X - rh_Y):', conclusion_scan(nm, 'rh'))
    print('=' * 70)
    print('THM9 printed example (nu=tau=0.5? printed nu=0.5,tau=0.8):')
    print('  premises raw powered (mu^nu vs lam^nu under suffix>=, G4):')
    nu, tau, a, b, lam, mu, pi = systems('THM9_print')
    mn = [m ** nu for m in mu]; ln = [l ** nu for l in lam]
    print('   mu^nu, lam^nu sorted desc?', mn == sorted(mn, reverse=True),
          ln == sorted(ln, reverse=True))
    print('   suffix>=:', weak_maj_printed(mn, ln, a, pi),
          ' prefix<=:', weak_maj_prefix(mn, ln, a, pi))
    print('   uo:', uo_maj(list(a), list(b)))
    print('  rh scan:', conclusion_scan('THM9_print', 'rh'))
    print('=' * 70)
    print('LEMMA8iii lr scan (Z<=lr X: f_X/f_Z increasing):')
    nu, tau, a, b, lam, mu, pi = systems('LEMMA8iii')
    worst = scan_monotonic(lambda t: max_pdf(t, a, nu, tau, lam)
                           / max_pdf(t, a, nu, tau, mu), '1e-6', '1e4')
    print('  min successive diff of f_X/f_Z:', worst)
    # also check at the eval witness x=1e-12 style small points
    for tt in ['1e-12', '1e-9', '0.001', '0.01', '0.1', '0.5', '1', '5']:
        tv = mp.mpf(tt)
        print('  t=%s fX/fZ=%s' % (tt, mp.nstr(max_pdf(tv, a, nu, tau, lam)
              / max_pdf(tv, a, nu, tau, mu), 25)))
