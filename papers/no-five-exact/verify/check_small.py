"""Independent integer checks for constructions and layer inventories.

Run from any directory with Python 3.10+. This does not prove an upper bound.
No search-program imports are used. Determinants use the Leibniz formula.
"""
from itertools import combinations, permutations
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
PERMS = {n: [(p, (-1) ** sum(p[i] > p[j] for i in range(n) for j in range(i+1,n)))
             for p in permutations(range(n))] for n in (3, 4)}

def det(rows):
    total = 0
    for perm, sign in PERMS[len(rows)]:
        term = sign
        for i, j in enumerate(perm):
            term *= rows[i][j]
        total += term
    return total

def lifted(p):
    return (*p, sum(x*x for x in p))

def independent(points):
    q = [lifted(p) for p in points]
    return det([[a-b for a,b in zip(row,q[0])] for row in q[1:]])

def certificate(name, size):
    source = ROOT / 'research/spikes/no-five-exact/certificates' / name
    data = json.loads(source.read_text())
    pts = [tuple(p) for p in data['points']]
    assert len(pts) == len(set(pts)) == size
    assert all(len(p) == 3 and all(type(c) is int and 0 <= c < data['n'] for c in p) for p in pts)
    values = [abs(independent(q)) for q in combinations(pts, 5)]
    assert min(values) > 0
    print(f'PASS {name}: size={size}, determinants={len(values)}, min_abs={min(values)}')

def inventory(n, smallest, expected_subsets, expected_orbits):
    grid = list(__import__('itertools').product(range(n), repeat=2))
    def transform(p, k):
        x,y = p
        if k & 4: x,y = y,x
        if k & 1: x = n-1-x
        if k & 2: y = n-1-y
        return x,y
    reps = set()
    total = 0
    fours = 0
    for size in range(smallest, 5):
        for chosen in combinations(grid, size):
            if size == 4:
                vals = [(*p, sum(c*c for c in p)) for p in chosen]
                if not det([[a-b for a,b in zip(row,vals[0])] for row in vals[1:]]):
                    continue
                fours += 1
            total += 1
            reps.add(min(tuple(sorted(transform(p,k) for p in chosen)) for k in range(8)))
    assert (total, len(reps)) == (expected_subsets, expected_orbits), (n,total,len(reps))
    print(f'PASS layer n={n}: subsets={total}, fours={fours}, D4_orbits={len(reps)}')

if __name__ == '__main__':
    for name, size in [('n3_8.json',8),('n4_11.json',11),('n5_14_ls5x.json',14),('n6_18_ls5x.json',18)]:
        certificate(name,size)
    inventory(5,1,14449,1905)
    inventory(6,2,64184,8133)
    print('PASS: constructions and orbit inventories; no upper-bound traversal performed')
