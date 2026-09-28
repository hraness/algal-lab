"""C3 second evaluation for doi_10.66224/jss.20.1.06 refutations --
independent mpmath/interval implementation (no sympy, no closedform).

Margins: S_i(x) = Fbar(x/a_i)^{a_i} * e^{-t_i x};  shock margin v_i = p_i S_i.
Parallel-system survival: 1 - C_phi(1 - v_1, ...) = 1 - phi(sum psi(1-v_i)).
Series-system survival: phi(sum psi(v_i)).
Copulas: indep psi=-log u, phi=e^{-t};  AMH(0.8): psi=log((0.2+0.8u)/u),
phi=0.2/(e^t-0.8);  ex5gen: psi=log((2-u)/u), phi=2/(1+e^t).
Baselines: PARX Fbar=1/x (x>=1);  WB5 Fbar=e^{-x^5};  PAR2 Fbar=(1+x)^{-2}.
"""
from mpmath import mp, mpf, iv

COPS = {
    "indep": (lambda u, L: -L.log(u), lambda t, L: L.exp(-t)),
    "amh":   (lambda u, L: L.log((L.mpf('0.2') + L.mpf('0.8') * u) / u),
              lambda t, L: L.mpf('0.2') / (L.exp(t) - L.mpf('0.8'))),
    "ex5":   (lambda u, L: L.log((2 - u) / u), lambda t, L: 2 / (1 + L.exp(t))),
}
BAS = {"parx": lambda x, L: 1 / x,          # valid for x >= 1
       "wb5": lambda x, L: L.exp(-x ** 5),
       "par2": lambda x, L: (1 + x) ** (-2),
       "exp": lambda x, L: L.exp(-x)}


def marg(a, t, Fb, xx, L):
    return Fb(xx / a, L) ** a * L.exp(-t * xx)


def series(ps, av, tv, Fb, cop, xx, L):
    psi, phi = COPS[cop]
    V = 0
    for p, a, t in zip(ps, av, tv):
        V += psi(p * marg(a, t, Fb, xx, L), L)
    return phi(V, L)


def parallel(ps, av, tv, Fb, cop, xx, L):
    psi, phi = COPS[cop]
    V = 0
    for p, a, t in zip(ps, av, tv):
        V += psi(1 - p * marg(a, t, Fb, xx, L), L)
    return 1 - phi(V, L)


mp.dps = 80


def scan(label, sysf, A, B, xpts):
    """A, B = dict(ps,av,tv,Fb,cop); prints S_B - S_A... we test claim
    S_left <=st S_right i.e. S_right - S_left >= 0."""
    out = []
    for xp in xpts:
        d = sysf(**B, xx=mpf(xp), L=mp) - sysf(**A, xx=mpf(xp), L=mp)
        out.append(mp.nstr(d, 6))
    print(label, out)


# ---- Example 1 / Theorem 2 (parallel, a ~<^w l): a=(37,24,5), l=(7,4,2) ----
P = lambda v: [mpf(str(w)) for w in v]
scan("Ex1 amh", parallel,
     dict(ps=P([.72,.18,.02]), av=P([37,24,5]), tv=P([.1]*3), Fb=BAS['parx'], cop='amh'),
     dict(ps=P([.72,.18,.02]), av=P([7,4,2]),   tv=P([.1]*3), Fb=BAS['parx'], cop='amh'),
     ['37.0001','38','40','50','80','200'])
scan("Ex1 indep", parallel,
     dict(ps=P([.72,.18,.02]), av=P([37,24,5]), tv=P([.1]*3), Fb=BAS['parx'], cop='indep'),
     dict(ps=P([.72,.18,.02]), av=P([7,4,2]),   tv=P([.1]*3), Fb=BAS['parx'], cop='indep'),
     ['37.0001','38','40','50','80','200'])

# ---- Theorem 1 (parallel, p vector comparison) ----
scan("Thm1 indep", parallel,
     dict(ps=P([.4,.5,.6]), av=P([3]*3), tv=P([.1]*3), Fb=BAS['parx'], cop='indep'),
     dict(ps=P([.3,.4,.5]), av=P([3]*3), tv=P([.1]*3), Fb=BAS['parx'], cop='indep'),
     ['3.0001','4','10','50','200'])

# ---- Theorem 3 / 9 (parallel) ----
for cop in ['indep','amh']:
    scan('Thm3 '+cop, parallel,
         dict(ps=P([.5]*3), av=P([5,7,9]), tv=P([.1]*3), Fb=BAS['parx'], cop=cop),
         dict(ps=P([.5]*3), av=P([3,5,11]), tv=P([.1]*3), Fb=BAS['parx'], cop=cop),
         ['9.0001','10','20','50','200'])
for cop in ['indep','ex5']:
    scan('Thm9 '+cop, parallel,
         dict(ps=P([.5]*3), av=P([5,7,9]), tv=P([.1]*3), Fb=BAS['parx'], cop=cop),
         dict(ps=P([.5]*3), av=P([3,5,11]), tv=P([.1]*3), Fb=BAS['parx'], cop=cop),
         ['9.0001','10','20','50','200'])

# ---- Theorem 8 / Example 5 (series, WB5 baseline) ----
for cop in ['indep','ex5']:
    scan('Thm8 '+cop, series,
         dict(ps=P([.5]*3), av=P([5,7,9]), tv=P([.1]*3), Fb=BAS['wb5'], cop=cop),
         dict(ps=P([.5]*3), av=P([3,5,11]), tv=P([.1]*3), Fb=BAS['wb5'], cop=cop),
         ['0.001','0.05','0.2','0.5','1','3'])

# ---- Theorem 6(a) (series, Pareto decreasing-in-alpha baseline, theta ~<^w eta)
for cop in ['indep','amh']:
    scan('Thm6a '+cop, series,
         dict(ps=P([.9]*3), av=P([2]*3), tv=P([.3,.4,.5]), Fb=BAS['par2'], cop=cop),
         dict(ps=P([.9]*3), av=P([2]*3), tv=P([.1,.4,.6]), Fb=BAS['par2'], cop=cop),
         ['0.001','0.05','0.2','0.5','1','3'])
