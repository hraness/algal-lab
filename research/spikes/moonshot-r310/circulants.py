"""Exhaustive check: circulant (3,10,40)-graphs.

A circulant C_40(S), S subset of {1..20}, edges i ~ i+s mod 40. Triangle-free and
alpha <= 9 iff it witnesses R(3,10) >= 41. e(3,10,40) >= 161 forces degree >= 9
(regular degree d, e = 20d >= 161 => d >= 9) and triangle-free forces d <= 9, so
d = 9; odd degree needs the self-inverse generator 20 in S, plus 4 of {1..19}.
"""
import itertools, sys

N = 40

def adj_mask(S):
    D = set()
    for s in S:
        D.add(s % N); D.add((-s) % N)
    adj = [0]*N
    for i in range(N):
        for s in D:
            adj[i] |= 1 << ((i+s) % N)
    return adj, D

def triangle_free(D):
    for a in D:
        for b in D:
            if (a+b) % N in D:
                return False
    return True

def alpha_ok(adj):
    """True iff no independent set of size 10 (i.e., alpha <= 9).
    Independent in G = clique in complement. Tomita-style max-clique with
    early stop at 10."""
    comp = [0]*N
    full = (1 << N) - 1
    for i in range(N):
        comp[i] = full & ~adj[i] & ~(1 << i)
    # greedy coloring bound, Tomita
    best = [0]
    def color_sort(P):
        # returns lists of vertices (order) and color bounds
        order, bounds = [], []
        colors = {}
        U = P
        c = 0
        while U:
            c += 1
            Q = U
            while Q:
                v = (Q & -Q).bit_length() - 1
                order.append(v); bounds.append(c)
                U &= ~(1 << v)
                Q &= ~(1 << v)
                Q &= ~comp[v]
            Q = U  # next color class over remaining U
        return order, bounds
    def expand(C_size, P):
        if not P:
            return
        order, bounds = color_sort(P)
        for i in range(len(order)-1, -1, -1):
            if best[0] >= 10:
                return
            if C_size + bounds[i] <= best[0]:
                return
            v = order[i]
            if not (P >> v) & 1:
                continue
            best[0] = max(best[0], C_size + 1)
            if best[0] >= 10:
                return
            expand(C_size + 1, P & comp[v] & ((1 << v) - 1))
            P &= ~(1 << v)
    expand(0, full)
    return best[0] <= 9

count = tf = ok = 0
hits = []
for combo in itertools.combinations(range(1, 20), 4):
    S = set(combo) | {20}
    count += 1
    adj, D = adj_mask(S)
    if not triangle_free(D):
        continue
    tf += 1
    if alpha_ok(adj):
        ok += 1
        hits.append(sorted(S))
print(f"checked {count} 9-regular circulants; triangle-free: {tf}; alpha<=9: {ok}")
for h in hits:
    print("HIT C_40", h)
