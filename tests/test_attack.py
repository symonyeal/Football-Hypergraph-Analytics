"""Attack-structure measures on families whose values are known by construction."""

from math import isclose

from fha.attack import cov, covered, minimum, nu, tau_star

C4 = [{0, 1}, {1, 2}, {2, 3}, {0, 3}]
K3 = [{0, 1}, {1, 2}, {0, 2}]
FANO = [{0, 1, 2}, {0, 3, 4}, {0, 5, 6}, {1, 3, 5}, {1, 4, 6}, {2, 3, 6}, {2, 4, 5}]
STAR = [{0, 1}, {0, 2}, {0, 3}]


def test_minimum_transversals():
    assert minimum(C4, 4) == [(0, 2), (1, 3)]
    assert minimum(K3, 3) == [(0, 1), (0, 2), (1, 2)]
    assert len(minimum(FANO, 7)) == 7 and all(len(t) == 3 for t in minimum(FANO, 7))
    assert minimum([{0}, {0, 1}, {2, 3}], 4) == [(0, 2), (0, 3)]
    assert minimum([], 3) == [()]


def test_tau_star_and_dual():
    for F, n, v in [(C4, 4, 2.0), (K3, 3, 1.5), (FANO, 7, 7 / 3), (STAR, 4, 1.0)]:
        t, x, y = tau_star(F, n)
        assert isclose(t, v, abs_tol=1e-9)
        assert isclose(sum(x), sum(y), abs_tol=1e-9)
    _, x, _ = tau_star(STAR, 4)
    assert isclose(x[0], 1.0, abs_tol=1e-9) and max(x[1:]) < 1e-9


def test_nu():
    assert nu(C4, 4)[0] == 2
    assert nu(K3, 3)[0] == 1
    assert nu(FANO, 7)[0] == 1
    assert nu([{0}, {1}, {0, 1}], 2)[0] == 2


def test_cov_weighted_uses_full_family():
    F = [{0, 1}, {2}, {3}, {0, 1}]
    w = [3.0, 2.0, 1.0, 1.0]
    s, T = cov(F, w, 4, 1)
    assert isclose(s, 4 / 7) and T in [(0,), (1,)]
    s, T = cov(F, w, 4, 2)
    assert isclose(s, 6 / 7) and set(T) in [{0, 2}, {1, 2}]
    assert isclose(covered((0, 2), F, w), 6 / 7)
    assert covered((), F, w) == 0.0


def test_agg_sums_possessions_and_xg_per_distinct_group():
    from fha.attack import agg
    G = [(frozenset({3, 1}), 0.2), (frozenset({1, 3}), 0.1), (frozenset({2}), 0.5)]
    assert sorted(agg(G)) == [[[1, 3], 2, 0.30000000000000004], [[2], 1, 0.5]]
