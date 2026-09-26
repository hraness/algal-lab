"""shape-sweep battery: runs the instance sweep. Machinery in mixlib.py."""
import sys
sys.path.insert(0, "/Users/bg/Documents/algal-lab/research/spikes/context/runs/shape-sweep")
from mixlib import *
import itertools, random

UGRID = [R(k, 40) for k in range(1, 40)]
UGRID_FINE = UGRID + [R(k, 400) for k in (1, 2, 3, 397, 398, 399)]
UPAIRS = [(R(a, 24), R(b, 24)) for a in range(1, 23) for b in range(a + 1, 24)]
PGRID = [R(k, 24) for k in range(1, 24)]


def show(name, mixA, mixB, tagA, tagB):
    print("-" * 70)
    print(name)
    nr, vh = st_cert(mixA, mixB)
    print("  st cert: SF_A - SF_B roots on (0,1) =", nr,
          "| sign at s=1/2:", sp.sign(vh),
          "=>", ("A st>= B unbroken" if nr == 0 and vh > 0 else
                 "B st>= A unbroken" if nr == 0 and vh < 0 else
                 "SFs CROSS (no st order either way)" if nr > 0 else "?"))
    vAB = disp_scan(mixA, mixB, UGRID_FINE)
    vBA = disp_scan(mixB, mixA, UGRID_FINE)
    print(f"  disp {tagA}<=disp {tagB}: violations = {len(vAB)}",
          vAB[:4] if vAB else "(none on grid)")
    print(f"  disp {tagB}<=disp {tagA}: violations = {len(vBA)}",
          vBA[:4] if vBA else "(none on grid)")
    sAB = star_scan(mixA, mixB, UPAIRS)
    sBA = star_scan(mixB, mixA, UPAIRS)
    print(f"  star {tagA}<=* {tagB}: violations = {len(sAB)}")
    for u, v, RX, RY in sAB[:4]:
        print("      u=%s v=%s  RX=%s  RY=%s" % (u, v, RX, RY))
    print(f"  star {tagB}<=* {tagA}: violations = {len(sBA)}")
    for u, v, RX, RY in sBA[:4]:
        print("      u=%s v=%s  RY=%s  RX=%s" % (u, v, RY, RX))
    lAB = lorenz_scan(mixA, mixB, PGRID)
    lBA = lorenz_scan(mixB, mixA, PGRID)
    print(f"  lorenz {tagA}<=L {tagB}: violations = {len(lAB)}",
          [(str(p), str(L)) for p, L, _ in lAB[:4]])
    print(f"  lorenz {tagB}<=L {tagA}: violations = {len(lBA)}",
          [(str(p), str(L)) for p, L, _ in lBA[:4]])


print("=" * 70)
print("INSTANCE 1: CERT A  p=(39/86,18/43,11/86)  lam=(4,6,9)  gam=(4,7,8)")
print("U_3 + majorization: lam >maj gam")
print("=" * 70)
pA = (R(39, 86), R(18, 43), R(11, 86))
lamA = (R(4), R(6), R(9))
gamA = (R(4), R(7), R(8))
print("hypotheses: in_Un(p,lam):", in_Un(list(pA), list(lamA)),
      "| in_Un(p,gam):", in_Un(list(pA), list(gamA)),
      "| lam >maj gam:", majorizes(list(lamA), list(gamA)))
mLam = ExpMix(pA, lamA)
mGam = ExpMix(pA, gamA)
show("CERT-A pair  (A=lam-mixture, B=gam-mixture)", mLam, mGam, "lam", "gam")

print()
print("=" * 70)
print("INSTANCE 2: CERT B  V_3 single T-transform pair")
print("p=(1/8,29/72,17/36) lam=(9,5,4) -> q=(2/9,11/36,17/36) gam=(38/5,32/5,4)")
print("=" * 70)
pB = (R(1, 8), R(29, 72), R(17, 36))
lamB = (R(9), R(5), R(4))
qB = (R(2, 9), R(11, 36), R(17, 36))
gamB = (R(38, 5), R(32, 5), R(4))
print("hypotheses: in_Vn(p,lam):", in_Vn(list(pB), list(lamB)),
      "| in_Vn(q,gam):", in_Vn(list(qB), list(gamB)))
mP = ExpMix(pB, lamB)
mQ = ExpMix(qB, gamB)
show("CERT-B pair  (A=(p,lam), B=(q,gam))", mP, mQ, "p;lam", "q;gam")

print()
print("=" * 70)
print("SEARCH: n=3 integer rate pairs lam >maj gam, decreasing integer weights")
print("(U_3 admissible for both), disp direction gam <=disp lam")
print("=" * 70)
found_disp = []
found_star = []
found_lor = []
checked = 0
rates = [R(i) for i in range(2, 13)]
wtrips = [(a, b, c) for a in range(1, 8) for b in range(1, 8) for c in range(1, 8)
          if a >= b >= c]
ugrid_q = [R(k, 20) for k in range(1, 20)]
upairs_q = [(R(a, 16), R(b, 16)) for a in range(1, 15) for b in range(a + 1, 16)]
pgrid_q = [R(k, 16) for k in range(1, 16)]
import random
random.seed(7)
cands = []
for lamt in itertools.combinations(sorted(rates), 3):
    for gamt in itertools.combinations(sorted(rates), 3):
        if majorizes(list(lamt), list(gamt)) and lamt != gamt:
            cands.append((lamt, gamt))
random.shuffle(cands)
cands = cands[:40]
found_disp_rev = []
for lamt, gamt in cands:
    wlist = random.sample(wtrips, 6)
    if (1, 1, 1) not in wlist:
        wlist[0] = (1, 1, 1)
    for wt in wlist:
        pw = tuple(R(w, sum(wt)) for w in wt)
        if not (in_Un(list(pw), list(lamt)) and in_Un(list(pw), list(gamt))):
            continue
        mX = ExpMix(pw, gamt)   # gam mixture (claimed less dispersed)
        mY = ExpMix(pw, lamt)   # lam mixture
        checked += 1
        vd = disp_scan(mX, mY, ugrid_q, iters=34)
        if vd:
            found_disp.append(("gam<=disp lam", lamt, gamt, wt, vd[0]))
        vd2 = disp_scan(mY, mX, ugrid_q, iters=34)
        if vd2:
            found_disp_rev.append(("lam<=disp gam", lamt, gamt, wt, vd2[0]))
        vs = star_scan(mX, mY, upairs_q, iters=34)
        if vs:
            found_star.append((lamt, gamt, wt, vs[0]))
        vl = lorenz_scan(mX, mY, pgrid_q, iters=34)
        if vl:
            found_lor.append((lamt, gamt, wt, vl[0]))
print("instances checked:", checked)
print("disp violations (gam<=disp lam):", len(found_disp))
for d, lamt, gamt, wt, v in found_disp[:8]:
    print("   lam=%s gam=%s w=%s first viol %s" % (lamt, gamt, wt, v))
print("disp violations (lam<=disp gam):", len(found_disp_rev))
for d, lamt, gamt, wt, v in found_disp_rev[:8]:
    print("   lam=%s gam=%s w=%s first viol %s" % (lamt, gamt, wt, v))
print("star violations (gam<=* lam):", len(found_star))
for lamt, gamt, wt, v in found_star[:8]:
    print("   lam=%s gamt=%s w=%s first viol u=%s v=%s" % (lamt, gamt, wt, v[0], v[1]))
print("lorenz violations (gam<=L lam):", len(found_lor))
for lamt, gamt, wt, v in found_lor[:8]:
    print("   lam=%s gam=%s w=%s first viol p=%s" % (lamt, gamt, wt, v[0]))
