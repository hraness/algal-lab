"""Compositions of survival functions for system/order-statistic claims.

Each function returns a sympy expression in x built from the component
survival expressions, suitable for Closed(). All assume independent
components unless noted.
"""
import sympy as sp
from closedform import x  # shared symbol


def series(survivals):
    """Smallest order statistic: P(min > x) = prod S_i."""
    return sp.prod(survivals)


def parallel(survivals):
    """Largest order statistic: P(max <= x) = prod (1 - S_i)."""
    return 1 - sp.prod([1 - S for S in survivals])


def order_stat(survivals, k, n):
    """k-th smallest of n iid components sharing survival S (or given list).

    P(X_{k:n} <= x) = sum_{j=k}^{n} C(n,j) F^j (1-F)^{n-j}.
    For heterogeneous components pass a list; we fall back to the
    permanent-like elementary symmetric sum over failure subsets.
    """
    from itertools import combinations
    from math import comb
    if len(set(map(str, survivals))) == 1:
        S = survivals[0]
        F = 1 - S
        cdf = sum(comb(n, j) * F**j * (1 - F)**(n - j) for j in range(k, n + 1))
        return 1 - cdf
    # heterogeneous: P(X_{k:n} <= x) = sum over subsets A with |A|>=k of
    # prod_{i in A} F_i prod_{j not in A} S_j
    Fs = [1 - S for S in survivals]
    cdf = 0
    for j in range(k, n + 1):
        for A in combinations(range(n), j):
            term = 1
            for i in range(n):
                term *= Fs[i] if i in A else survivals[i]
            cdf += term
    return 1 - cdf


def mixture(weights, survivals):
    """Mixture over components: S = sum p_i S_i."""
    assert abs(sum(weights) - 1) < 1e-9
    return sum(w * S for w, S in zip(weights, survivals))


def random_extreme(survivals_by_size, pmf):
    """X_{1:N} or X_{N:N} over random N: sum_m P(N=m) * (composition at m)."""
    return sum(p * s for p, s in zip(pmf, survivals_by_size))
