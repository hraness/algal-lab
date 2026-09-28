"""Independent check: arxiv:2103.00763 counterexamples 3.2, 3.3.

Poisson(mu): S(u)=1-e^{-mu} sum_{r<=u} mu^r/r!.
Geometric(q): S(u)=q^{u+1}, F(u)=1-q^{u+1}.
Min hazard h(u)=[S(u)-S(u+1)]/S(u); max reversed hazard
rh(u)=[F(u)-F(u-1)]/F(u).
CE3.2 claims h16-h*16=-0.00024431, h6-h*6=+0.0124328.
CE3.3 claims rh1-rh*1=-0.0010584, rh4-rh*4=+0.00628996;
also q=(.99,.96,.57) vs q*=(.9,.78,.57): sums 2.52!=2.25.
"""
import mpmath as mp
mp.mp.dps = 120


def pois_S(mu, u):
    mu, u = mp.mpf(mu), int(u)
    term = mp.mpf(1); s = mp.mpf(1)
    for r in range(1, u + 1):
        term *= mu / r
        s += term
    return 1 - mp.e ** (-mu) * s


def h_min(mus, u):
    S = mp.fprod(pois_S(m, u) for m in mus)
    S1 = mp.fprod(pois_S(m, u + 1) for m in mus)
    return (S - S1) / S


def geom_rh_max(qs, u):
    F = mp.fprod(1 - mp.mpf(q) ** (u + 1) for q in qs)
    Fm = mp.fprod(1 - mp.mpf(q) ** u for q in qs)   # F(u-1)
    return (F - Fm) / F


mu = [mp.mpf('28'), mp.mpf('0.8'), mp.mpf('0.1')]
mus = [mp.mpf('27'), mp.mpf('1'), mp.mpf('0.9')]
print("CE3.2 majorization mu>=^m mu* (equal totals):", sum(mu) == sum(mus))
print("  desc partials:", sorted(mu, reverse=True), sorted(mus, reverse=True))
for u in (6, 16):
    d = h_min(mu, u) - h_min(mus, u)
    print(f"  u={u}: h-h* = {mp.nstr(d, 15)}  (printed {'+0.0124328' if u==6 else '-0.00024431'})")
neg = [u for u in range(1, 400) if h_min(mu, u) - h_min(mus, u) < -mp.mpf('1e-40')]
pos = [u for u in range(1, 400) if h_min(mu, u) - h_min(mus, u) > mp.mpf('1e-40')]
print("  u in 1..399: negative diff at", neg[:5], "count", len(neg),
      "| positive count", len(pos))
print("  diff at u=200:", mp.nstr(h_min(mu, 200) - h_min(mus, 200), 8),
      "| u=399:", mp.nstr(h_min(mu, 399) - h_min(mus, 399), 8))

print("CE3.3:")
q = [mp.mpf('0.99'), mp.mpf('0.96'), mp.mpf('0.57')]
qs = [mp.mpf('0.9'), mp.mpf('0.78'), mp.mpf('0.57')]
print("  sums:", mp.nstr(sum(q), 5), "vs", mp.nstr(sum(qs), 5),
      "-> equal-total majorization:", abs(sum(q) - sum(qs)) < mp.mpf('1e-60'))
A = sorted(q, reverse=True); B = sorted(qs, reverse=True)
print("  weak supermaj (asc sums q <= q*)?:",
      all(sum(sorted(q)[:k]) <= sum(sorted(qs)[:k]) for k in range(1, 4)),
      "| desc partial sums q>=q*:", [sum(A[:k]) >= sum(B[:k]) for k in (1, 2, 3)])
for u in (1, 4):
    d = geom_rh_max(q, u) - geom_rh_max(qs, u)
    print(f"  u={u}: rh-rh* = {mp.nstr(d, 15)}  (printed {'-0.0010584' if u==1 else '+0.00628996'})")
neg = [u for u in range(1, 1000) if geom_rh_max(q, u) - geom_rh_max(qs, u) < -mp.mpf('1e-40')]
pos = [u for u in range(1, 1000) if geom_rh_max(q, u) - geom_rh_max(qs, u) > mp.mpf('1e-40')]
print("  u in 1..999: neg count", len(neg), neg[:5], "| pos count", len(pos))
