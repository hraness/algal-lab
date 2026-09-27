"""C3 for Kw-G Theorem 3.7: direct hazard evaluation (independent of ratdist).
Exponential baseline, alpha = beta = 1, N uniform on {2, 3}. The random minimum's
survival is (s^{G2} + s^{G3})/2 with s = e^{-x}, so its hazard is
(G2 s^{G2} + G3 s^{G3}) / (s^{G2} + s^{G3}). Claim: X_{1:N} >=hr Y_{1:N}, i.e.
h_X(x) <= h_Y(x) for all x."""
from fractions import Fraction as Fr


def hazard(G2, G3, s):
    return (G2 * s ** G2 + G3 * s ** G3) / (s ** G2 + s ** G3)


for label, gX, gY in [("printed reading", (4, Fr(9, 2)), (2, 5)), ("reading R2", (2, 3), (2, 20))]:
    s = Fr(4, 5) if label == "reading R2" else Fr(1, 2)
    hX, hY = hazard(*gX, s), hazard(*gY, s)
    print(f"{label}: at s = {s}: h_X = {float(hX):.6f}, h_Y = {float(hY):.6f}; claim needs h_X <= h_Y: {hX <= hY}")
