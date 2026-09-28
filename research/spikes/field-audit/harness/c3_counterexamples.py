"""C3 independent verification of confirmed printed counterexamples.

Each printed counterexample asserts that an ordering FAILS.  The primary
evaluators found strict-enclosure witnesses via closedform; here each is
re-verified by direct interval evaluation of the defining expressions, coded
independently (no closedform import).

NP = new Pareto:  S_i(x) = 2 beta_i^a / (x^a + beta_i^a),  x > beta_i.
JMI PI  = Pareto I :  S_i(x) = (b_i / x)^a,  x >= b_i.
JMI PII = Pareto II:  S_i(x) = (b_i / (x + b_i))^a, x >= 0.
Series (min): S = prod S_i;  parallel (max): S = 1 - prod(1 - S_i).
"""
from mpmath import iv, nstr

iv.dps = 100
V = iv.mpf


def np_s(a, b, xx):
    return 2 * b ** a / (xx ** a + b ** a)


def np_f(a, b, xx):
    return 2 * a * b ** a * xx ** (a - 1) / (xx ** a + b ** a) ** 2


def np_ser(params, xx):
    s = iv.mpf(1)
    for a, b in params:
        s *= np_s(a, b, xx)
    return s


def np_par(params, xx):
    s = iv.mpf(1)
    for a, b in params:
        s *= 1 - np_s(a, b, xx)
    return 1 - s


def np_ser_h(params, xx):       # hazard of the min = sum of component hazards
    return sum(np_f(a, b, xx) / np_s(a, b, xx) for a, b in params)


def pi_min_rh(params, xx):      # reversed hazard of PI minimum = (sum a)/x * 1/F
    s = iv.mpf(1)
    for a, b in params:
        s *= (b / xx) ** a
    return s * sum(a / xx for a, b in params) / (1 - s)


def pii_min_h(params, xx):      # hazard of PII minimum = sum a_i/(x+b_i)
    return sum(a / (xx + b) for a, b in params)


def neg(v):
    return "STRICT NEG (ordering fails here)" if v.b < 0 else (
        "pos" if v.a > 0 else "UNDECIDED")


print("== NP CE 3.1(i): alpha=3/2, beta=(1,8,11/10), beta*=(8,11/10,4); "
      "claim X3:3 NOT >=st Y3:3, i.e. S_X - S_Y < 0 somewhere ==")
a = V(3) / 2
X = [(a, V(1)), (a, V(8)), (a, V(11) / 10)]
Y = [(a, V(8)), (a, V(11) / 10), (a, V(4))]
for t in ["8.000000000001", "8.5", "9", "10", "15", "30"]:
    xx = V(t)
    d = np_par(X, xx) - np_par(Y, xx)
    print("  x =", t, "S_X-S_Y in", nstr(d.a, 10), nstr(d.b, 10), neg(d))

print("== NP CE 3.1(ii): alpha=4/5, beta=(1/10,1,9), beta*=(1/10,4,6); "
      "claim X3:3 NOT >=st Y3:3 ==")
a = V(4) / 5
X = [(a, V(1) / 10), (a, V(1)), (a, V(9))]
Y = [(a, V(1) / 10), (a, V(4)), (a, V(6))]
for t in [V(1049647) / 120, V("9.5"), V("12"), V("20"), V("40")]:
    d = np_par(X, t) - np_par(Y, t)
    print("  x =", nstr(t, 10), "S_X-S_Y in", nstr(d.a, 10), nstr(d.b, 10), neg(d))

print("== NP CE 3.2: alpha=1/2, beta=(21/10,1,9/5), beta*=(7/2,4/5,9/10); "
      "claim X1:3 NOT <=st Y1:3, i.e. S_X - S_Y > 0 somewhere (X too big) ==")
a = V(1) / 2
X = [(a, V(21) / 10), (a, V(1)), (a, V(9) / 5)]
Y = [(a, V(7) / 2), (a, V(4) / 5), (a, V(9) / 10)]
for t in ["3.500000000001", "4", "5", "7", "12"]:
    xx = V(t)
    d = np_ser(X, xx) - np_ser(Y, xx)
    print("  x =", t, "S_X-S_Y in", nstr(d.a, 10), nstr(d.b, 10), neg(d))

print("== NP CE 3.3: alpha=1/2, beta=(1/5,1/2,7/10), beta*=(2/5,3/10,6/5); "
      "claim X3:3 NOT >=st Y3:3 ==")
a = V(1) / 2
X = [(a, V(1) / 5), (a, V(1) / 2), (a, V(7) / 10)]
Y = [(a, V(2) / 5), (a, V(3) / 10), (a, V(6) / 5)]
for t in ["1.200000000001", "1.5", "2", "3", "5"]:
    xx = V(t)
    d = np_par(X, xx) - np_par(Y, xx)
    print("  x =", t, "S_X-S_Y in", nstr(d.a, 10), nstr(d.b, 10), neg(d))

print("== NP CE 3.4: alpha=4/5, beta=(6/5,1/2,17/10), beta*=(2/5,4/5,6/5); "
      "claim Y1:3 NOT >=st X1:3, i.e. S_Y - S_X < 0 ==")
a = V(4) / 5
X = [(a, V(6) / 5), (a, V(1) / 2), (a, V(17) / 10)]
Y = [(a, V(2) / 5), (a, V(4) / 5), (a, V(6) / 5)]
for t in ["1.700000000001", "2", "3", "5", "9"]:
    xx = V(t)
    d = np_ser(Y, xx) - np_ser(X, xx)
    print("  x =", t, "S_Y-S_X in", nstr(d.a, 10), nstr(d.b, 10), neg(d))

print("== NP CE 3.5: beta=8/5, a=(3/5,19/10,3/10,9/5), a*=(2/5,21/10,4/5,8/5); "
      "claim X1:4 NOT <=hr Y1:4, i.e. h_X - h_Y < 0 ==")
bb = V(8) / 5
X = [(a, bb) for a in [V(3) / 5, V(19) / 10, V(3) / 10, V(9) / 5]]
Y = [(a, bb) for a in [V(2) / 5, V(21) / 10, V(4) / 5, V(8) / 5]]
for t in ["16.000000000001", "17", "20", "30", "60"]:
    xx = V(t)
    d = np_ser_h(X, xx) - np_ser_h(Y, xx)
    print("  x =", t, "h_X-h_Y in", nstr(d.a, 10), nstr(d.b, 10), neg(d))

print("== NP CE 3.6: n=2 hetero, (a;b)X=(3/2,4/5;3/5,2/5), "
      "Y=(101/100,129/100;23/50,27/50); claim X1:2 NOT <=st Y1:2, i.e. S_X - S_Y > 0 ==")
X = [(V(3) / 2, V(3) / 5), (V(4) / 5, V(2) / 5)]
Y = [(V(101) / 100, V(23) / 50), (V(129) / 100, V(27) / 50)]
for t in ["0.600000000001", "0.8", "1", "2", "4"]:
    xx = V(t)
    d = np_ser(X, xx) - np_ser(Y, xx)
    print("  x =", t, "S_X-S_Y in", nstr(d.a, 10), nstr(d.b, 10), neg(d))

print("== JMI Example 2.3: PI minima (1,6),(2,12) vs (17/10,51/5),(13/10,39/5); "
      "claim Y1:2 NOT >=rh X1:2, i.e. rh_Y - rh_X < 0 ==")
X = [(V(1), V(6)), (V(2), V(12))]
Y = [(V(17) / 10, V(51) / 5), (V(13) / 10, V(39) / 5)]
for t in ["12.000000000001", "15", "20", "40", "100"]:
    xx = V(t)
    d = pi_min_rh(Y, xx) - pi_min_rh(X, xx)
    print("  x =", t, "rh_Y-rh_X in", nstr(d.a, 10), nstr(d.b, 10), neg(d))

print("== JMI Example 2.4: PII minima (3,4),(2,1) vs (12/5,11/5),(13/5,14/5); "
      "claim Y1:2 NOT >=hr X1:2, i.e. h_X - h_Y < 0 ==")
X = [(V(3), V(4)), (V(2), V(1))]
Y = [(V(12) / 5, V(11) / 5), (V(13) / 5, V(14) / 5)]
for t in ["6", "8738", "8738.133", "50000"]:
    xx = V(t)
    d = pii_min_h(X, xx) - pii_min_h(Y, xx)
    print("  x =", t, "h_X-h_Y in", nstr(d.a, 10), nstr(d.b, 10), neg(d))
