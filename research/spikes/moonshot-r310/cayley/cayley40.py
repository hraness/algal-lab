"""Cayley-graph exclusion for (3,10,40)-graphs.

Every group of order 40 is C5 ⋊ P, P a group of order 8, phi: P -> Aut(C5)=C4.
(Sylow: n_5 | 8 and n_5 = 1 mod 5 => n_5 = 1; Schur-Zassenhaus splits.)

For each group: enumerate connection sets S ⊂ G\{e}, inverse-closed,
|S| <= 9 (Delta <= 9 forced by alpha <= 9), triangle-free:
  S must not contain a,b with ab in S (and a != b^{-1}).
Then compute alpha(Cay(G,S)) exactly (max independent set via recursive
branching with greedy coloring bound).
"""

import itertools, sys
from collections import defaultdict

def mult_table(elems, mul):
    """Return (table dict, inverse dict)."""
    idx = {e: i for i, e in enumerate(elems)}
    T = {}
    inv = {}
    for a in elems:
        for b in elems:
            T[(idx[a], idx[b])] = idx[mul(a, b)]
    for a in elems:
        for b in elems:
            if T[(idx[a], idx[b])] == idx[elems[0]]:  # elems[0] = identity
                inv[idx[a]] = idx[b]; break
    return T, inv, idx

# ---- groups of order 8 ----
def abel2(*mods):
    el = list(itertools.product(*[range(m) for m in mods]))
    mul = lambda a, b: tuple((x + y) % m for x, y, m in zip(a, b, mods))
    return el, mul, (0,) * len(mods)

def dihedral8():
    # D8 = <r,s | r^4=s^2=1, srs=r^-1>, elems (i,j) = r^i s^j
    el = [(i, j) for i in range(4) for j in range(2)]
    def mul(a, b):
        i, j = a; k, l = b
        # r^i s^j * r^k s^l = r^i (s^j r^k s^j) s^{j+l} = r^{i + (-1)^j k} s^{j+l}
        return ((i + ((-1) ** j) * k) % 4, (j + l) % 2)
    return el, mul, (0, 0)

def quaternion8():
    # Q8 elements: (i,j) i in Z4, j in Z2; (i,0) -> r^i, (i,1) -> r^i * s
    # with s^2 = r^2 = -1 central, sr = r^{-1} s
    el = [(i, j) for i in range(4) for j in range(2)]
    def mul(a, b):
        i, j = a; k, l = b
        # r^i s^j * r^k s^l : s^j r^k = r^{(-1)^j k} s^j ; s^{j+l}: if j+l==2 -> r^2
        ni = (i + ((-1) ** j) * k) % 4
        sexp = j + l
        if sexp == 2: ni = (ni + 2) % 4; sexp = 0
        return (ni, sexp)
    return el, mul, (0, 0)

# ---- C5 ⋊ P : elements (c, p), (c1,p1)(c2,p2) = (c1 + phi(p1)(c2), p1 p2) ----
def semidirect(P_el, P_mul, P_id, phi):
    """phi: dict p -> k in {1,2,3,4} meaning action c -> k*c (mod 5)."""
    el = [(c, p) for c in range(5) for p in P_el]
    mul = lambda a, b: ((a[0] + pow(phi[a[1]], 1, 5) * b[0] if phi[a[1]] != 0 else a[0]) % 5, P_mul(a[1], b[1]))
    # careful: phi gives multiplier k s.t. p1.c2 = k*c2 mod 5
    def mul2(a, b):
        c1, p1 = a; c2, p2 = b
        k = phi[p1]
        return ((c1 + k * c2) % 5, P_mul(p1, p2))
    return el, mul2, (0, P_id)

def homs_to_c4(P_el, P_mul, P_id):
    """All homomorphisms P -> {1,2,3,4} multiplicatively (Aut(C5) ≅ C4).
    Generators of P -> arbitrary element; verify homomorphism."""
    outs = []
    # brute force: image of each element, must be a homomorphism:
    # phi(ab)=phi(a)phi(b) with phi(e)=1, phi(a) in {1,2,3,4} (4^k=1 mod5)
    n = len(P_el)
    idx = {e: i for i, e in enumerate(P_el)}
    T = [[idx[P_mul(a, b)] for b in P_el] for a in P_el]
    # generate candidate images for a small generating set
    gens = []
    covered = {idx[P_id]}
    full = list(range(n))
    while len(covered) < n:
        for g in full:
            if g not in covered:
                gens.append(g)
                new = set(covered) | {g}
                # closure
                changed = True
                while changed:
                    changed = False
                    for a in list(new):
                        for b in list(new):
                            c = T[a][b]
                            if c not in new: new.add(c); changed = True
                covered = new
                break
    for combo in itertools.product([1, 2, 3, 4], repeat=len(gens)):
        img = {idx[P_id]: 1}
        for g, v in zip(gens, combo): img[g] = v
        ok = True
        # extend by closure
        full_img = dict(img)
        work = list(img.keys())
        changed = True
        tries = 0
        while len(full_img) < n and tries < 200:
            tries += 1
            for a in list(full_img):
                for b in gens:
                    c = T[a][b]
                    nv = full_img[a] * img[b] % 5
                    if c in full_img and full_img[c] != nv: ok = False; break
                    full_img[c] = nv
                if not ok: break
            if not ok: break
        if not ok: continue
        # verify homomorphism everywhere
        good = True
        for a in range(n):
            for b in range(n):
                if full_img[T[a][b]] != full_img[a] * full_img[b] % 5:
                    good = False; break
            if not good: break
        if good:
            outs.append({P_el[i]: full_img[i] for i in range(n)})
    # dedupe identical maps
    uniq = []
    for h in outs:
        if all(any(h[e] != u[e] for e in h) for u in uniq): uniq.append(h)
    return uniq

def build_groups():
    groups = []
    for name, (P_el, P_mul, P_id) in [
        ('C8', abel2(8)), ('C4xC2', abel2(4, 2)), ('C2^3', abel2(2, 2, 2)),
        ('D8', dihedral8()), ('Q8', quaternion8()),
    ]:
        for phi in homs_to_c4(P_el, P_mul, P_id):
            el, mul, e = semidirect(P_el, P_mul, P_id, phi)
            groups.append((f'C5rt({name})-phi{sorted(set(phi.values()))}', el, mul, e))
    return groups

if __name__ == '__main__':
    groups = build_groups()
    print(len(groups), 'semidirect products generated')
    # invariants: element-order profile + number of involutions
    for name, el, mul, e in groups:
        T, inv, idx = mult_table(el, mul)
        n = len(el)
        ei = idx[e]
        orders = defaultdict(int)
        for a in range(n):
            o = 1; cur = a
            while cur != ei: cur = T[(cur, a)]; o += 1
            orders[o] += 1
        print(name, dict(sorted(orders.items())), 'involutions:', orders[2])

# ---------------- Cayley graph search ----------------
def tri_free_ok(T, inv, ei, S, cand):
    """does adding 'cand' to connection set S keep triangle-freeness?
    triangle iff exists a,b in S with a*b in S, a != b^{-1}.
    For new element s: check s*t in S and t*s in S and t*s'=s cases."""
    Sset = set(S)
    for t in S:
        # s*t, t*s can't be in S
        if T[(cand, t)] in Sset or T[(t, cand)] in Sset:
            return False
        # t1*t2 = cand would put cand as product but that's fine until cand added:
        # with cand in S, need: no a*b=cand in SxS... cand = a*b means a*cand^{-1}=b?? 
        # triangles in Cayley: a,b,c with a*b=c (a,b,c in S, a != b^{-1})
        # adding cand: check cand = a*b for a,b in S
        if T[(t, cand)] in Sset:
            return False
    # cand as product of two S elements: a*b = cand, a,b in S
    # then a, b, cand^{-1}-fixed... triangle iff a,b,c in S, a*b=c:
    # adding cand: for a,b in S with a*b==cand -> triangle
    for a in S:
        for b in S:
            if T[(a, b)] == cand and inv[a] != b:
                return False
    return True

def build_adj(T, inv, n, S):
    adj = [0] * n
    for g in range(n):
        for s in S:
            adj[g] |= 1 << T[(g, s)]
    return adj

def alpha_mis(adj, n):
    """exact independence number via recursive branch + greedy coloring on
    remaining vertices (complement = clique of complement graph).
    adj: neighbor bitmask. Independent set = clique in complement."""
    comp = [((1 << n) - 1) & ~adj[v] & ~(1 << v) for v in range(n)]
    best = [0]
    def color_sort(P):
        # greedy coloring of induced subgraph on P; returns (order, bounds)
        order = []; bounds = []
        rem = P
        color = 0
        while rem:
            color += 1
            avail = rem
            while avail:
                v = avail.bit_length() - 1  # highest bit
                avail &= avail - 1
                order.append(v); bounds.append(color)
                rem &= ~(1 << v)
                avail &= ~comp[v]
        return order, bounds
    import sys
    sys.setrecursionlimit(10000)
    def branch(P, cur):
        if not P:
            if cur > best[0]: best[0] = cur
            return
        order, bounds = color_sort(P)
        # process in reverse order (last = highest color)
        for i in range(len(order) - 1, -1, -1):
            if cur + bounds[i] <= best[0]:
                return
            v = order[i]
            branch(P & comp[v], cur + 1)
            P &= ~(1 << v)
    branch((1 << n) - 1, 0)
    return best[0]

def search_group(T, inv, n, K=9, alpha_max=9, limit=None):
    """enumerate inverse-closed S ⊂ G\{e}, |S|<=9, triangle-free Cayley graph.
    DFS over inverse-pair slots. Returns stats + first witness with alpha<=9."""
    ei = 0
    # group elements into inverse-pair slots
    seen = set(); slots = []
    for g in range(1, n):
        if g in seen: continue
        s = (g,) if inv[g] == g else (g, inv[g])
        for x in s: seen.add(x)
        slots.append(s)
    stats = {'tested': 0, 'tf': 0, 'hits': []}
    S = []
    def alive(S):  # all partial triangle checks
        for i in range(len(S)):
            for j in range(i+1, len(S)):
                for a, b in [(S[i], S[j]), (S[j], S[i])]:
                    c = T[(a, b)]
                    if c in S:
                        return False
        return True
    def dfs(i):
        if stats['tested'] >= (limit or 10**18): return
        if stats['hits']: return
        if i == len(slots):
            stats['tested'] += 1
            if S and alive(S):
                stats['tf'] += 1
                adj = build_adj(T, inv, n, S)
                if alpha_mis(adj, n) <= alpha_max:
                    stats['hits'].append(list(S)); return
            return
        # skip
        dfs(i + 1)
        if stats['hits']: return
        if len(S) + len(slots[i]) <= K and len(slots) - i >= 0:
            # take
            cand = slots[i]
            ok = True
            for c in cand:
                if not tri_free_ok(T, inv, ei, S, c): ok = False; break
            if ok:
                S.extend(cand); dfs(i + 1)
                del S[-len(cand):]
    dfs(0)
    return stats

if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'search':
    groups = build_groups()
    # dedupe by order profile (isomorphic-ish groups share search results anyway)
    prof = {}
    for name, el, mul, e in groups:
        T, inv, idx = mult_table(el, mul)
        n = len(el); ei = idx[e]
        orders = defaultdict(int)
        for a in range(n):
            o = 1; cur = a
            while cur != ei: cur = T[(cur, a)]; o += 1
            orders[o] += 1
        key = tuple(sorted(orders.items()))
        prof.setdefault(key, []).append((name, el, mul, e, T, inv, idx))
    print(len(prof), 'distinct order profiles')
    for key, gs in sorted(prof.items(), key=lambda kv: -len(kv[1]))[:1]:
        pass

def run_all():
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
        prof.setdefault(tuple(sorted(orders.items())), []).append((name, el, mul, e, T, inv, idx))
    print(len(prof), 'distinct groups; running Cayley search (|S|<=9, alpha<=9)')
    for i, (key, gs) in enumerate(prof.items()):
        name, el, mul, e, T, inv, idx = gs[0]
        st = search_group(T, inv, len(el))
        print(f'[{i+1}/{len(prof)}] {name} ({len(gs)} iso-copies): tested={st["tested"]} tf={st["tf"]} hits={len(st["hits"])}', flush=True)
        if st['hits']:
            print('   HIT connection set:', st['hits'][0])
