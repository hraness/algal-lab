"""Independent C3 confirmation for doi:10.2298/FIL2104315D refutations.

Each refuted record is re-checked with a STRICT interval enclosure of the
harness's order expression at an interior point found by independent
mpmath scanning.  The formulas are re-derived from the printed df
    F_{n:n}(t) = prod_i [1 - p_i (1 - F^{a_i}((t-l_i)/s_i))]
and the paper's printed counterexample/example parameters.
"""
import sympy as sp
import closedform as cf
from closedform import x, Closed, iv_eval, iv

R = sp.Rational
iv.dps = 120

results = []


def dfU(pr, al, lam, th, base):
    F = R(1)
    for p, a, l, s in zip(pr, al, lam, th):
        F *= 1 - p * (1 - base((x - l) / s) ** a)
    return F


def probe(E, lo, pts, label):
    """strict negative enclosure at some interior point > lo."""
    for pt in pts:
        if pt <= lo:
            continue
        for dps in (60, 150, 400):
            iv.dps = dps
            try:
                v = iv_eval(E, pt)
            except Exception:
                continue
            if v.b < 0:
                results.append((label, str(pt)))
                print(f"{label}: confirmed witness x={pt} "
                      f"E<0 interval=({float(v.a)},{float(v.b)})")
                return True
            break
    print(f"{label}: NOT confirmed")
    return False


def GLFR(yy):
    return 1 - sp.exp(-sp.sqrt(yy))


def LOM5(yy):
    return 1 - (1 + 5 * yy) ** R(-1, 5)


def DEC1(yy):
    # y>=1: r(y)=2/y+1/y^2 -> Fbar=y^{-2} e^{1/y-1}; satisfies C2,C4,C5,C7,C8
    return 1 - yy ** (-2) * sp.exp(1 / yy - 1)


def MOQL(yy):
    a, b, d = R(1, 10), R(-9, 10), R(4, 5)
    q_ = (b + 1 + d * yy) / (b + 1) * sp.exp(-d * yy)
    return (1 - q_) / (1 - (1 - a) * q_)


def check(label, order, pU, aU, lU, tU, pV, aV, lV, tV, base, lo, pts,
          direction="U>=V"):
    FU = dfU(pU, aU, lU, tU, base)
    FV = dfU(pV, aV, lV, tV, base)
    DU, DV = Closed(1 - FU, lo), Closed(1 - FV, lo)
    if direction == "U>=V":
        X, Y = DV, DU      # claim U >=ord V  <=>  V <=ord U
    else:
        X, Y = DU, DV
    if order == "st":
        E = Y.survival - X.survival
    elif order == "rh":
        E = Y.density * (1 - X.survival) - X.density * (1 - Y.survival)
    probe(E, lo, pts, label)


def main():
    G, L5, D1 = GLFR, LOM5, DEC1

    # ---- Theorem 3.1(i): n=2, psi=p^2, theta shared; (psi_p,lam) in M2,
    # T_{1/2} averaging.  Verified interior F_U-F_V>0 at t=10.
    p = [R(1, 2), R(9, 10)]
    lam = [R(2, 5), R(6, 5)]
    wq = [(R(1, 4) + R(81, 100)) / 2] * 2       # T_{1/2} on psi row
    mu = [(R(2, 5) + R(6, 5)) / 2] * 2
    q = [sp.sqrt(wq[0])] * 2
    check("Thm 3.1(i)", "st", p, [R(1, 2)] * 2, lam, [R(1)] * 2,
          q, [R(1, 2)] * 2, mu, [R(1)] * 2, G, R(6, 5),
          [R(10), R(30), R(137)])

    # ---- Theorem 3.2(i) / Corollary 3.1(i): n=3, T_{1/2} on cols (0,1)
    wp = [R(9, 100), R(25, 100), R(64, 100)]
    p3 = [sp.sqrt(w_) for w_ in wp]
    lam3 = [R(1, 5), R(7, 10), R(3, 2)]
    wq3 = [(wp[0] + wp[1]) / 2, (wp[0] + wp[1]) / 2, wp[2]]
    mu3 = [(lam3[0] + lam3[1]) / 2, (lam3[0] + lam3[1]) / 2, lam3[2]]
    q3 = [sp.sqrt(w_) for w_ in wq3]
    check("Thm 3.2(i)", "st", p3, [R(1, 2)] * 3, lam3, [R(1)] * 3,
          q3, [R(1, 2)] * 3, mu3, [R(1)] * 3, G, R(3, 2),
          [R(4), R(140)])

    # ---- Theorem 3.3(i): two different-structure T-transforms
    wp = [R(9, 100), R(25, 100), R(64, 100)]
    w, ww = R(3, 5), R(3, 5)
    # T1 swaps cols 0,1; T2 swaps cols 1,2 (weights 3/5)
    c1 = [w * wp[0] + (1 - w) * wp[1], w * wp[1] + (1 - w) * wp[0], wp[2]]
    l1 = [w * lam3[0] + (1 - w) * lam3[1], w * lam3[1] + (1 - w) * lam3[0],
          lam3[2]]
    wq4 = [c1[0], ww * c1[1] + (1 - ww) * c1[2],
           ww * c1[2] + (1 - ww) * c1[1]]
    mu4 = [l1[0], ww * l1[1] + (1 - ww) * l1[2],
           ww * l1[2] + (1 - ww) * l1[1]]
    q4 = [sp.sqrt(w_) for w_ in wq4]
    check("Thm 3.3(i)", "st", p3, [R(1, 2)] * 3, lam3, [R(1)] * 3,
          q4, [R(1, 2)] * 3, mu4, [R(1)] * 3, G, R(3, 2),
          [R(20), R(100)])

    # ---- Theorem 3.4(ii): rh; LOM5 baseline (C1,C8); psi=p^2.
    wp = [R(1, 4), R(81, 100)]
    p2 = [sp.sqrt(w_) for w_ in wp]
    lam2 = [R(2, 5), R(6, 5)]
    wq2 = [(wp[0] + wp[1]) / 2] * 2
    mu2 = [(lam2[0] + lam2[1]) / 2] * 2
    q2 = [sp.sqrt(wq2[0])] * 2
    check("Thm 3.4(ii)", "rh", p2, [R(1)] * 2, lam2, [R(1)] * 2,
          q2, [R(1)] * 2, mu2, [R(1)] * 2, L5, R(6, 5),
          [R(50), R(200)])

    # ---- Theorem 3.5(ii) / Corollary 3.2(ii): n=3, T_{1/2} cols (0,2)
    wp = [R(9, 100), R(25, 100), R(64, 100)]
    wq5 = [(wp[0] + wp[2]) / 2, wp[1], (wp[0] + wp[2]) / 2]
    mu5 = [(lam3[0] + lam3[2]) / 2, lam3[1], (lam3[0] + lam3[2]) / 2]
    q5 = [sp.sqrt(w_) for w_ in wq5]
    check("Thm 3.5(ii)", "rh", p3, [R(1)] * 3, lam3, [R(1)] * 3,
          q5, [R(1)] * 3, mu5, [R(1)] * 3, L5, R(3, 2),
          [R(20), R(50)])
    check("Cor 3.2(ii)", "rh", p3, [R(1)] * 3, lam3, [R(1)] * 3,
          q5, [R(1)] * 3, mu5, [R(1)] * 3, D1, R(5, 2),
          [R(3), R(6), R(20)])

    # ---- Theorem 3.6(ii): two different Ts on (lam,psi_p) in M3
    c1 = [w * wp[0] + (1 - w) * wp[1], w * wp[1] + (1 - w) * wp[0], wp[2]]
    l1 = [w * lam3[0] + (1 - w) * lam3[1], w * lam3[1] + (1 - w) * lam3[0],
          lam3[2]]
    wq6 = [c1[0], ww * c1[1] + (1 - ww) * c1[2],
           ww * c1[2] + (1 - ww) * c1[1]]
    mu6 = [l1[0], ww * l1[1] + (1 - ww) * l1[2],
           ww * l1[2] + (1 - ww) * l1[1]]
    q6 = [sp.sqrt(w_) for w_ in wq6]
    check("Thm 3.6(ii)", "rh", p3, [R(1)] * 3, lam3, [R(1)] * 3,
          q6, [R(1)] * 3, mu6, [R(1)] * 3, L5, R(3, 2),
          [R(20), R(50), R(8000)])

    # ---- Theorem 4.1: claim U <=st V (direction reversed in print);
    # premise: alpha >>w beta, p desc, lam shared.
    alp = [R(1), R(3), R(5)]
    bet = [R(1, 2), R(7, 2), R(4)]
    pp = [R(9, 10), R(6, 10), R(3, 10)]
    check("Thm 4.1", "st", pp, alp, [R(1)] * 3, [R(1)] * 3,
          pp, bet, [R(1)] * 3, [R(1)] * 3, G, R(1),
          [R(11, 10), R(3)], direction="U<=V")

    # ---- Theorem 4.2: psi_p >>w psi_q, psi=p^2; MOQL baseline (no
    # baseline C-condition needed for Thm 4.2).
    wp = [R(25, 100), R(49, 100), R(81, 100)]
    wq7 = [R(16, 100), R(36, 100), R(64, 100)]
    p7 = [sp.sqrt(w_) for w_ in wp]
    q7 = [sp.sqrt(w_) for w_ in wq7]
    lam7 = [R(1), R(2), R(3)]
    th7 = [R(1), R(2), R(3)]
    al7 = [R(1, 2), R(7, 10), R(9, 10)]
    check("Thm 4.2", "st", p7, al7, lam7, th7,
          q7, al7, lam7, th7, MOQL, R(3), [R(31, 10), R(4)])

    # ---- Theorem 4.3(i): 1/th p-larger 1/del on DEC1 (C2).
    pp = [R(2, 10), R(5, 10), R(8, 10)]
    lam8 = [R(1), R(3, 2), R(2)]
    check("Thm 4.3(i)", "st", pp, [R(1, 2)] * 3, lam8,
          [R(1), R(3), R(5)], pp, [R(1, 2)] * 3, lam8,
          [R(2), R(3), R(6)], D1, R(8), [R(10), R(15)])

    # ---- Theorem 4.5(i): all three heterogeneous, DEC1 (C2)
    th9, dl9 = [R(1), R(3), R(5)], [R(2), R(3), R(6)]
    lam9, mu9 = [R(1), R(3), R(6)], [R(1, 2), R(5, 2), R(4)]
    check("Thm 4.5(i)", "st", p7, [R(1, 2)] * 3, lam9, th9,
          q7, [R(1, 2)] * 3, mu9, dl9, D1, R(11), [R(30), R(60)])

    # ---- Theorem 4.8(i): rh, 1/th >>w 1/del, DEC1 (C2,C5)
    check("Thm 4.8(i)", "rh", pp, [R(1)] * 3, lam8,
          [R(1), R(3), R(5)], pp, [R(1)] * 3, lam8,
          [R(2), R(3), R(6)], D1, R(8), [R(9), R(15)])

    # ---- Theorem 4.11(i): rh, all three maj constraints, DEC1 (C2,C5)
    check("Thm 4.11(i)", "rh", p7, [R(1)] * 3, lam9, th9,
          q7, [R(1)] * 3, mu9, dl9, D1, R(11), [R(40), R(90)])

    # ---- Example 5.2: printed concrete claim U2:2 >=st V2:2 fails on
    # the paper's own numbers (MOQL baseline stipulated).
    pE = [sp.sqrt(R(2, 10)), sp.sqrt(R(1, 2))]
    qE = [sp.sqrt(R(32, 100)), sp.sqrt(R(38, 100))]
    check("Example 5.2", "st", pE, [R(52, 100)] * 2,
          [R(5), R(61, 10)], [R(1, 100)] * 2,
          qE, [R(52, 100)] * 2, [R(544, 100), R(566, 100)],
          [R(1, 100)] * 2, MOQL, R(61, 10), [R(611, 100)])

    print()
    if len(results) == 14:
        print("ALL CONFIRMED (14 probes over 15 refuted records; Cor 3.1(i) shares Thm 3.2(i)'s instance)")
    else:
        print("MISSING:", 14 - len(results))


if __name__ == "__main__":
    main()
