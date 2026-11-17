"""Second-round estimators on synthetic data with planted effects."""

from collections import Counter

import numpy as np

from fha import protocol


def test_pass_strength_and_ranking():
    Q = Counter({(1, 2): 5, (2, 3): 1, (3, 1): 2})
    assert protocol.strength(Q) == {1: 7, 2: 6, 3: 3}
    assert protocol.ranked({1: 7, 2: 7, 3: 3}, 2) == [1, 2]


def synthetic(beta, delta, g, teams=30, per=24):
    """Matches with team and opponent effects, home advantage and planted absence effects."""
    al, ga = g.normal(0, 0.3, teams), g.normal(0, 0.3, teams)
    C = g.uniform(0.5, 0.9, teams)
    rows = []
    for t in range(teams):
        for k in range(per):
            o = (t + 1 + k % (teams - 1)) % teams
            a = g.uniform(0, 0.4) if g.random() < 0.4 else 0.0
            m = np.exp(0.2 + al[t] + ga[o] + 0.15 * (k % 2) - beta * a - delta * C[t] * a)
            rows.append({"team": t, "opp": o, "home": k % 2, "a": a, "C": C[t], "y": g.gamma(m / 0.3, 0.3)})
    return rows


def test_fit4_recovers_planted_absence_effect():
    g = np.random.default_rng(0)
    b, d, _, disp = protocol.fit4(synthetic(1.0, 0.0, g))
    assert abs(b + 0.7 * d - 1.0) < 0.3 and 0.15 < disp < 0.5


def test_power_rises_with_effect():
    g = np.random.default_rng(1)
    p = protocol.power4(synthetic(0.0, 0.0, g), [0.5, 6.0], 30, g)
    assert p["power"][6.0] >= p["power"][0.5] and p["power"][6.0] > 0.8


def test_loo_r2():
    x = np.arange(20.0)
    assert protocol.loo_r2(x[:, None], 2 * x + 1) > 0.999
    g = np.random.default_rng(2)
    assert protocol.loo_r2(g.normal(size=(40, 1)), g.normal(size=40)) < 0.1


def test_icc_power_extremes():
    g = np.random.default_rng(3)
    assert protocol.icc_power(0.9, 60, 0.3, 10, 100, g) == 1.0
    assert protocol.icc_power(0.0, 60, 0.3, 10, 100, g) == 0.0
