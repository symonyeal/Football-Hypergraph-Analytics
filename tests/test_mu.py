"""Functionals of the chance measure, null models and resampling on families whose values are known."""

from collections import Counter
from itertools import combinations
from math import isclose

import numpy as np

from fha import mu

FANO = [frozenset(e) for e in ({0, 1, 2}, {0, 3, 4}, {0, 5, 6}, {1, 3, 5}, {1, 4, 6}, {2, 3, 6}, {2, 4, 5})]
G = [(frozenset({0, 1}), 1.0), (frozenset({1}), 1.0), (frozenset({2, 3}), 2.0)]


def unit(F):
    return [(A, 1.0) for A in F]


def test_involvement_and_shapley():
    d, p = mu.d(G), mu.phi(G)
    assert d == {0: 0.25, 1: 0.5, 2: 0.5, 3: 0.5}
    assert p == {0: 0.125, 1: 0.375, 2: 0.25, 3: 0.25}
    assert isclose(sum(p.values()), 1.0)


def test_hill_numbers_of_uniform_shares_count_them():
    for q in (0, 1, 2):
        assert isclose(mu.hill([0.25] * 4, q), 4.0)
    assert mu.hill([1.0, 0.0], 1) == 1.0


def test_concentration_curve_and_partial_transversal_on_fano():
    F = unit(FANO)
    assert isclose(mu.cb(F, 1)[0], 3 / 7) and isclose(mu.cb(F, 2)[0], 5 / 7) and isclose(mu.cb(F, 3)[0], 1.0)
    assert [mu.tau_a(F, a) for a in (0.4, 5 / 7, 0.8, 1.0)] == [1, 2, 3, 3]
    assert mu.cb(F, 9) == (1.0, tuple(range(7)))


def test_tau_alpha_counts_weight_not_chances():
    H = [(frozenset({0}), 9.0), (frozenset({1}), 0.5), (frozenset({2}), 0.5)]
    assert mu.tau_a(H, 0.9) == 1 and mu.tau_a(H, 0.95) == 2 and mu.tau_a(H, 1.0) == 3


def test_greedy_and_overlap():
    assert mu.greedy(G, 2) == [1, 2] and isclose(mu.c([1, 2], G), 1.0)
    assert isclose(mu.o([1, 2], G), 0.0)                 # never in the same chance
    assert isclose(mu.o([0, 1], G), 1 - 0.5 / 0.75)      # share the chance {0, 1}


def test_rarefy_at_full_size_and_boot_of_a_constant():
    g = np.random.default_rng(0)
    F = unit(FANO)
    assert mu.rarefy(F, 7, lambda x: mu.tau_a(x, 1.0), 3, g) == 3.0
    assert mu.rarefy(F, 1, lambda x: mu.tau_a(x, 1.0), 5, g) == 1.0
    assert mu.boot([F[:3], F[3:]], lambda x: 1.0, 50, g) == 0.0


def degrees(H):
    return Counter(v for A, _ in H for v in A)


def test_redeal_keeps_degrees_sizes_xg_and_strata():
    g = np.random.default_rng(1)
    H = [(frozenset(e), float(i + 1)) for i, e in enumerate(FANO)]
    for _ in range(20):
        N = mu.redeal(H, g)
        assert degrees(N) == degrees(H)
        assert [(len(A), w) for A, w in N] == [(3, w) for _, w in H]
    R = [{v: "a" if v < 3 else "b" for v in A} for A, _ in H]
    for _ in range(20):
        N = mu.redeal(H, g, R)
        assert degrees(N) == degrees(H)
        for (A, _), (B, _), r in zip(H, N, R):   # each chance keeps its count of members per stratum
            assert sorted(r.values()) == sorted("a" if v < 3 else "b" for v in B)


def test_pairwise_model_matches_pair_counts():
    H = unit([frozenset(e) for e in ({0, 1, 2}, {0, 1, 3}, {0, 2, 3}, {0, 1, 2}, {1, 2, 3}, {0, 1, 4})]) + [(frozenset({5}), 1.0)]
    T, p = mu.fit3(H)
    obs = Counter(frozenset(q) for A, _ in H if len(A) == 3 for q in combinations(sorted(A), 2))
    exp = Counter()
    for t, x in zip(T, p):
        for q in combinations(t, 2):
            exp[frozenset(q)] += 6 * x
    assert all(isclose(exp[q], obs[q], abs_tol=1e-6) for q in obs)
    N = mu.pairwise(H, np.random.default_rng(2))
    assert len(N) == len(H) and (frozenset({5}), 1.0) in N and all(len(A) in (1, 3) for A, _ in N)


def test_pairwise_on_k4_triples_is_uniform():
    H = unit([frozenset(t) for t in combinations(range(4), 3)])
    T, p = mu.fit3(H)
    assert len(T) == 4 and np.allclose(p, 0.25)


def test_reliability_helpers():
    x = np.arange(10.0)
    assert isclose(mu.icc(x, x), 1.0)
    assert isclose(mu.brown(0.42, 2), 0.84 / 1.42)
    m, se, t2 = mu.pool([0.3, 0.3, 0.3], [0.01, 0.04, 0.01])
    assert isclose(m, 0.3) and t2 == 0.0 and isclose(se, (1 / (100 + 25 + 100)) ** 0.5)


def test_swap_chain_keeps_degrees_sizes_strata_and_simplicity():
    g = np.random.default_rng(4)
    H = unit(FANO) * 3 + [(frozenset({0, 4}), 1.0)] * 2
    E = [list(A) for A, _ in H]
    L = np.array([0 if v < 3 else 1 for e in E for v in e])
    lo = np.concatenate([[0], np.cumsum([len(e) for e in E])[:-1]])
    seen = set()
    for _ in range(20):
        N = mu.swap(E, L, lo, H, g)
        assert degrees(N) == degrees(H) and [len(A) for A, _ in N] == [len(A) for A, _ in H]
        for (A, _), e in zip(N, E):   # each group keeps its stratum counts
            assert sorted(v < 3 for v in A) == sorted(v < 3 for v in e) and len(A) == len(e)
        seen.add(tuple(sorted(tuple(sorted(A)) for A, _ in N)))
    assert len(seen) > 1   # the chain moves
