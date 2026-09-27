import itertools, random, json
import sympy as sp
from closedform import Closed, check, x, expression, iv_eval
from mpmath import iv
R = sp.Rational

def clfrd(a, b, lam):
    w = sp.exp(-a * x - b * x ** 2 / 2)
    return Closed(sp.exp(-a * x - b * x ** 2 / 2 - lam + lam * w))

# Theorem 3.2 (joint reading): a1<=a2, b1<=b2, l1<=l2  =>  Y <=lr X, X=(a1,b1,l1), Y=(a2,b2,l2)
X, Y = clfrd(1, 1, 1), clfrd(1, 2, 1)
holds, w, und = check("lr", Y, X)
print("instance a=(1,1) b=(1,2) l=(1,1): Y <=lr X holds_on_grid =", holds, "witness x0 =", w)
E = expression("lr", Y, X)
iv.dps = 80
print("  enclosure of f_X' f_Y - f_X f_Y' at witness:", iv_eval(E, w))
# exact log-derivative of g_X/g_Y at 0+ (should be (b1-b2)/a = -1)
gX, gY = X.density, Y.density
d0 = sp.limit(sp.diff(sp.log(gX) - sp.log(gY), x), x, 0, "+")
print("  d/dx log(g_X/g_Y) at 0+ (exact):", d0)

# Bounded random search over admissible instances for each implied order in Remark 3.3
random.seed(7)
vals = [R(1, 2), R(1), R(3, 2), R(2), R(3)]
results = {o: {"tested": 0, "refuted": 0, "example": None} for o in ("st", "hr", "rh", "lr")}
for _ in range(40):
    a1, a2 = sorted(random.sample(vals, 2)) if random.random() < 0.7 else (random.choice(vals),) * 2
    b1, b2 = sorted(random.sample(vals, 2)) if random.random() < 0.7 else (random.choice(vals),) * 2
    l1, l2 = sorted(random.sample(vals, 2)) if random.random() < 0.7 else (random.choice(vals),) * 2
    Xi, Yi = clfrd(a1, b1, l1), clfrd(a2, b2, l2)
    for o in results:
        h, wit, _ = check(o, Yi, Xi)
        results[o]["tested"] += 1
        if not h:
            results[o]["refuted"] += 1
            results[o]["example"] = results[o]["example"] or {"a": [str(a1), str(a2)], "b": [str(b1), str(b2)], "l": [str(l1), str(l2)], "x0": str(wit)}
print(json.dumps(results, indent=1))
