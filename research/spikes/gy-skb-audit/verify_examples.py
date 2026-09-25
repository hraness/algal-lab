"""Verify papers' own examples exactly (Fraction arithmetic on y-grid)."""
from fractions import Fraction
import sympy as sp
from fast_eval import gy_Cker_val, skb_Aker_val, skb_Bker_val, GRIDF
from audit_mphr import in_Vn

F = Fraction

def signs(vals):
    return set((v > 0) - (v < 0) for v in vals)


print("== SKB2026 Example 6 (Thm 7: W2<=hr V2, a=-1, beta=2, exp base) ==")
p = [F(3, 10), F(7, 10)]; th = [F(6), F(4)]
q = [F(46, 100), F(54, 100)]; gm = [F(52, 10), F(48, 10)]
w = F(3, 5)
print("V2:", in_Vn(p, th), "in_Vn(q,gm):", in_Vn(q, gm))
print("T check:", q[0] == w * p[0] + (1 - w) * p[1], gm[0] == w * th[0] + (1 - w) * th[1])
d = [skb_Aker_val(p, th, -1, v) - skb_Aker_val(q, gm, -1, v) for v in GRIDF]
print("hW - hV kernel diffs (claim >=0):", signs(d), d[:5])

print("\n== SKB2026 Example 8 (Thm 10: W2<=rh V2, a=5) ==")
d = [skb_Bker_val(p, th, 5, v) - skb_Bker_val(q, gm, 5, v) for v in GRIDF]
print("rW - rV kernel diffs (claim <=0):", signs(d), d[:5])

print("\n== SKB2026 Example 10 (Thm 19 MPRHR: W~2>=hr V~2, a=20) ==")
d = [skb_Bker_val(p, th, 20, v) - skb_Bker_val(q, gm, 20, v) for v in GRIDF]
print("hW~ - hV~ kernel diffs (claim <=0):", signs(d))

print("\n== GY2024 Example 6 (Thm 5 n=2: V2>=hr W2) ==")
p = [F(3, 10), F(7, 10)]; a = [F(7, 10), F(3, 10)]
q = [F(34, 100), F(66, 100)]; b = [F(66, 100), F(34, 100)]
w = F(9, 10)
print("p.a equal:", p[0] * a[0] == p[1] * a[1], "K2:", in_Vn(p, a))
print("T check:", q[0] == w * p[0] + (1 - w) * p[1], b[0] == w * a[0] + (1 - w) * a[1])
d = [gy_Cker_val(p, a, v) - gy_Cker_val(q, b, v) for v in GRIDF]
print("rV - rW diffs (claim >=0):", signs(d))

print("\n== GY2024 Example 1 (Thm1(i): V2<=st W2, lam=0.1) ==")
p = [F(6, 10), F(4, 10)]; a = [F(3, 10), F(4, 10)]
q = [F(48, 100), F(52, 100)]; b = [F(36, 100), F(34, 100)]
print("K2:", in_Vn(p, a))
w = F(2, 5)
print("T check:", q[0] == w * p[0] + (1 - w) * p[1], b[0] == w * a[0] + (1 - w) * a[1])
from fast_eval import gy_sf_val
d = [gy_sf_val(p, a, v) - gy_sf_val(q, b, v) for v in GRIDF]
print("FV - FW diffs (claim <=0):", signs(d))

print("\n== GY2024 Example 2 (Cor1(i) n=3 same-structure chain, V3<=st W3) ==")
p = [F(1, 5), F(3, 10), F(1, 2)]; a = [F(1, 2), F(3, 10), F(1, 10)]
# T1: cols(2,3) w=0.4 ; T2: cols(2,3) w=0.2
def appT(r, i, j, w):
    r = list(r); ri, rj = w * r[i] + (1 - w) * r[j], w * r[j] + (1 - w) * r[i]
    r[i], r[j] = ri, rj
    return r
p1 = appT(p, 1, 2, F(2, 5)); a1 = appT(a, 1, 2, F(2, 5))
q = appT(p1, 1, 2, F(1, 5)); b = appT(a1, 1, 2, F(1, 5))
print("q =", q, " b =", b)
print("paper says q=(0.2,0.388,0.412), b=(0.5,0.212,0.188):",
      q == [F(1, 5), F(388, 1000), F(412, 1000)], b == [F(1, 2), F(212, 1000), F(188, 1000)])
d = [gy_sf_val(p, a, v) - gy_sf_val(q, b, v) for v in GRIDF]
print("FV - FW diffs (claim <=0):", signs(d))

print("\n== GY2024 Example 3 (Cor2(i) diff-structure chain) ==")
p = [F(1, 10), F(4, 10), F(5, 10)]; a = [F(7, 10), F(5, 10), F(3, 10)]
print("K3:", in_Vn(p, a))
p1 = appT(p, 1, 2, F(3, 10)); a1 = appT(a, 1, 2, F(3, 10))
print("(p,a)T1 in K3:", in_Vn(p1, a1))
p2 = appT(p1, 0, 1, F(2, 5)); a2 = appT(a1, 0, 1, F(2, 5))
print("(p,a)T1T2 in K3:", in_Vn(p2, a2))
p3 = appT(p2, 0, 2, F(1, 10)); a3 = appT(a2, 0, 2, F(1, 10))
print("q =", [float(v) for v in p3], " b =", [float(v) for v in a3])
d = [gy_sf_val(p, a, v) - gy_sf_val(p3, a3, v) for v in GRIDF]
print("FV - FW diffs (claim <=0):", signs(d))

print("\n== GY2024 Example 4 (Thm3(i): Z2>=st Y2, (p,lam) in K2, alpha=0.2) ==")
# Z_n(p,lam): SF = sum p_i * al*Fbar^{l_i}/(1-albar*Fbar^{l_i}); y_i = Fbar^{l_i}
al = F(1, 5)
p = [F(1, 5), F(4, 5)]; lam = [F(1, 2), F(1, 4)]
q = [F(62, 100), F(38, 100)]; tht = [F(13, 40), F(17, 40)]
print("K2:", in_Vn(p, lam))
w = F(3, 10)
print("T check:", q[0] == w * p[0] + (1 - w) * p[1], tht[0] == w * lam[0] + (1 - w) * lam[1])
# SF in s=Fbar: SF_Z = sum p_i al s^{l_i}/(1-albar s^{l_i}); l_i = 1/2,1/4 -> use s^(1/4)
def sfZ_val(p_, l_, al_, s4):
    # s4 = Fbar^{1/4}; l in quarters
    return sum(pi * al_ * s4 ** int(4 * li) / (1 - (1 - al_) * s4 ** int(4 * li))
               for pi, li in zip(p_, l_))
d = [sfZ_val(p, lam, al, v) - sfZ_val(q, tht, al, v) for v in GRIDF]
print("FZ - FY diffs (claim >=0):", signs(d))
