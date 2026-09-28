"""Exhaust every degree-at-most-nine circulant on 40 vertices.

An independent neighborhood forces degree <= 9 in a triangle-free graph with
alpha <= 9. No external edge lower bound is required. Counts include the empty
connection set. The bounded C orbital search is the faster production route.
"""
import itertools

from vertex_transitive.checker import independent_set

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
    """True exactly when no independent set of size ten exists."""
    return independent_set(adj, 10) is None


def connection_sets():
    for pairs in range(5):
        for combo in itertools.combinations(range(1, 20), pairs):
            yield set(combo)
            yield set(combo) | {20}


def main():
    count = tf = 0
    hits = []
    for connection in connection_sets():
        count += 1
        adj, differences = adj_mask(connection)
        if not triangle_free(differences):
            continue
        tf += 1
        if alpha_ok(adj):
            hits.append(sorted(connection))
    print(f"checked {count} circulants of degree <= 9 (including empty); "
          f"triangle-free: {tf}; alpha<=9: {len(hits)}")
    for hit in hits:
        print("HIT C_40", hit)


if __name__ == '__main__':
    main()
