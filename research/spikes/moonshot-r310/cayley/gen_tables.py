"""Emit all 14 groups of order 40 as multiplication tables + inverse maps
for the C enumerator. Groups = C5 rt P (all homs P -> Aut(C5) = C4), deduped
by element-order profile (all 14 distinct profiles present)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cayley40 import build_groups, mult_table
from collections import defaultdict

groups = build_groups()
prof = {}
for name, el, mul, e in groups:
    T, inv, idx = mult_table(el, mul)
    n = len(el); ei = idx[e]
    orders = defaultdict(int)
    for a in range(n):
        o = 1; cur = a
        while cur != ei: cur = T[(cur, a)]; o += 1
        orders[o] += 1
    prof.setdefault(tuple(sorted(orders.items())), []).append((name, T, inv, idx))
print(len(prof), 'distinct groups')
with open('groups40.txt', 'w') as f:
    for key, gs in prof.items():
        name, T, inv, idx = gs[0]
        n = 40
        f.write(f'# {name} n=40 involutions={[v for k,v in key if k==2][0]}\n')
        f.write(' '.join(str(inv[i]) for i in range(n)) + '\n')
        for a in range(n):
            f.write(' '.join(str(T[(a, b)]) for b in range(n)) + '\n')
print('wrote groups40.txt')
