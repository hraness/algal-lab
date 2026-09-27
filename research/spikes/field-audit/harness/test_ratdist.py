"""Known-true orderings must hold; flipped versions must be refuted with a witness.

Run: /Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python -m pytest -q test_ratdist.py
(or run this file directly).
"""
import sympy as sp

from ratdist import exp_mixture, hr, lr, order_statistic_exponentials, rh, st, z


def exponential(rate, D=1):
    return exp_mixture([1], [rate], D)


def refuted(result):
    holds, witness = result
    return (not holds) and witness is not None


def test_exponential_rates_order_every_way():
    fast, slow = exponential(2), exponential(1)
    for order in (st, hr, rh, lr):
        assert order(fast, slow)[0], order.__name__
        assert refuted(order(slow, fast)), order.__name__


def test_pledger_proschan_maxima():
    # (1,3) majorizes (2,2): the heterogeneous maximum is stochastically larger.
    het = order_statistic_exponentials([1, 3], 2, 1)
    hom = order_statistic_exponentials([2, 2], 2, 1)
    assert st(hom, het)[0]
    assert refuted(st(het, hom))


def test_minima_with_equal_rate_sums_are_equal_in_law():
    a = order_statistic_exponentials([1, 3], 1, 1)
    b = order_statistic_exponentials([2, 2], 1, 1)
    assert sp.expand(a.survival - b.survival) == 0
    assert st(a, b)[0] and st(b, a)[0]


def test_dykstra_kochar_rojo_parallel_hazard_rate():
    # Heterogeneous exponential parallel system versus the homogeneous one at
    # the arithmetic mean rate: X_{n:n} >=hr Y_{n:n}.
    het = order_statistic_exponentials([1, 2, 6], 3, 1)
    hom = order_statistic_exponentials([3, 3, 3], 3, 1)
    assert hr(hom, het)[0]
    assert refuted(hr(het, hom))


def test_mixture_hazard_crossing_is_detected():
    # Two exponential mixtures whose survival functions cross: neither is
    # st-smaller than the other, and each claim comes back with a witness.
    X = exp_mixture([sp.Rational(1, 2), sp.Rational(1, 2)], [1, 9], 1)
    Y = exp_mixture([1], [2], 1)
    assert refuted(st(X, Y)) and refuted(st(Y, X))


def test_witness_is_exact():
    X = exp_mixture([sp.Rational(1, 2), sp.Rational(1, 2)], [1, 9], 1)
    Y = exp_mixture([1], [2], 1)
    holds, w = st(X, Y)
    assert not holds and 0 < w < 1
    assert (Y.survival - X.survival).subs(z, w) < 0


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("pass", name)
