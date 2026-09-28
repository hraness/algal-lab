"""C3 second evaluation for arxiv_2604.26026 refutations -- pure mpmath,
independent of sympy/closedform.

Transformation model: margins X_i ~ T(alpha_i, F); Te(beta,F)=1-(1-F)^beta,
Tc(beta,F)=F^beta, To(beta,F)=beta F^2/(beta F^2+Fbar^2); baseline
Fbar=(1+x)^{-1}.  Archimedean: cdf(Xn:n)=phi2(sum psi2(cdf_i)),
surv(X1:n)=phi1(sum psi1(surv_i)).
"""
from mpmath import mp, mpf, iv

mp.dps = 90; iv.dps = 90
L = mp


def gen(name, L):
    if name == "indep":
        return (lambda u: -L.log(u), lambda t: L.exp(-t))
    if name == "clayton1":
        return (lambda u: u ** -1 - 1, lambda t: (1 + t) ** (-1))
    if name == "gumbel2":
        return (lambda u: (L.log(u)) ** 2, lambda t: L.exp(-L.sqrt(t)))
    if name == "amh12":
        return (lambda u: L.log((L.mpf('1.5') - L.mpf('0.5') * u) / u),
                lambda t: L.mpf('0.5') / (L.exp(t) - L.mpf('0.5')))
    raise ValueError


FB = lambda xx, L: (1 + xx) ** (-1)


def msurv(a, T, xx, L):
    if T == "te":  return FB(xx, L) ** a
    if T == "tc":  return 1 - (1 - FB(xx, L)) ** a
    if T == "to":
        F = 1 - FB(xx, L)
        return 1 - a * F ** 2 / (a * F ** 2 + FB(xx, L) ** 2)


def mcdf(a, T, xx, L):
    return 1 - msurv(a, T, xx, L)


def sysmax(aa, T, cop, xx, L):
    psi, phi = gen(cop, L)
    t = 0
    for a in aa:
        t += psi(mcdf(a, T, xx, L))
    return 1 - phi(t)


def sysmin(aa, T, cop, xx, L):
    psi, phi = gen(cop, L)
    t = 0
    for a in aa:
        t += psi(msurv(a, T, xx, L))
    return phi(t)


A_MAJ = [mpf('0.3'), mpf(1), mpf('1.7')]   # alpha (more spread; ~>^m)
B_MAJ = [mpf('0.6'), mpf(1), mpf('0.8')]   # beta
A_LE = [mpf('0.5'), mpf('0.8')]
B_LE = [mpf('0.7'), mpf(1)]


def run(tag, f, pts):
    print(tag, [mp.nstr(f(mpf(t)), 6) for t in pts])


PTS = ['1e-12', '1e-6', '0.01', '0.05', '0.2', '0.5', '1', '5', '50']

# Theorem 3.3 / Example 3.5: Xn:n(alpha) >=st Yn:n(beta), alpha ~>^m beta;
# same copula on both sides (phi2 o psi1 = id, super-additive). E = SY-SX.
for cop in ["clayton1", "gumbel2", "amh12", "indep"]:
    run("Thm3.3 %s" % cop,
        lambda t, c=cop: sysmax(B_MAJ, "te", c, t, mp) - sysmax(A_MAJ, "te", c, t, mp),
        PTS)

# Theorem 3.8 / Cor 3.9: X1:n(alpha) <=st Y1:n(beta), beta ~>^m alpha. E=SY-SX
for cop in ["clayton1", "gumbel2", "amh12"]:
    run("Thm3.8 %s" % cop,
        lambda t, c=cop: sysmin(B_MAJ, "te", c, t, mp) - sysmin(A_MAJ, "te", c, t, mp),
        PTS)

# Cor 3.10: X1:n(alpha*) <=st X1:n(alpha) <=st X1:n(alphabar), te, clayton1/amh
astar = [mpf('0.5')] * 3; abar = [mpf(2)] * 3
amid = [mpf('0.4'), mpf(1), mpf('1.6')]
for cop in ["clayton1", "amh12"]:
    run("Cor3.10 left %s" % cop,
        lambda t, c=cop: sysmin(amid, "te", c, t, mp) - sysmin(astar, "te", c, t, mp), PTS)
    run("Cor3.10 right %s" % cop,
        lambda t, c=cop: sysmin(abar, "te", c, t, mp) - sysmin(amid, "te", c, t, mp), PTS)

# Cor 3.6: Xn:n(alpha*) >=st Xn:n(alpha) >=st Xn:n(alphabar), te
for cop in ["clayton1", "gumbel2"]:
    run("Cor3.6 left %s" % cop,
        lambda t, c=cop: sysmax(astar, "te", c, t, mp) - sysmax(amid, "te", c, t, mp), PTS)
    run("Cor3.6 right %s" % cop,
        lambda t, c=cop: sysmax(amid, "te", c, t, mp) - sysmax(abar, "te", c, t, mp), PTS)

# Prop 4.6: tc margins, alpha_i <= beta_i, X <=st Y; E = SY - SX (psi1=indep,
# psi2=gumbel2 -> phi1 o psi2 = (-log) o psi2 super-additive per Ex 2.5/2.6)
run("Prop4.6 indep-gumbel2",
    lambda t: sysmax(B_LE, "tc", "gumbel2", t, mp) - sysmax(A_LE, "tc", "indep", t, mp),
    PTS)

# Prop 4.14/4.15: To margins, alpha<=beta; X1:n >=st X1:n Y (4.14), <=st (4.15)
run("Prop4.14 indep-clayton",
    lambda t: sysmin(B_LE, "to", "clayton1", t, mp) - sysmin(A_LE, "to", "indep", t, mp),
    PTS)
run("Prop4.15 clayton-indep",
    lambda t: sysmin(B_MAJ, "to", "indep", t, mp) - sysmin(A_MAJ, "to", "clayton1", t, mp),
    PTS)
