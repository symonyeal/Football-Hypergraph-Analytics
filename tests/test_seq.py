"""Sequence features at the cutoff (H4) on hand-built actions."""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

from fha.seq import design, features, motif, zone


def test_design_keeps_indicators_binary():
    Xtr, Xte, names = design([{"p=1": 1, "v:x": 50.0}, {"v:x": -100.0}], [{"p=1": 1, "v:x": 10.0}])
    j, k = names.index("p=1"), names.index("v:x")
    assert Xtr[0, j] == 1 and Xte[0, j] == 1
    assert np.isclose(abs(Xtr[:, [k]].toarray()).max(), 1.0)


def test_rare_noise_indicators_do_not_wreck_held_out_loss():
    # 2,000 rows, one informative context indicator, 400 noise indicators seen about 5 times each.
    g = np.random.default_rng(0)
    def rows(n):
        D, y = [], []
        for _ in range(n):
            c = int(g.random() < 0.5)
            d = {"ctx": 1} if c else {}
            d[f"p={g.integers(400)}"] = 1
            D.append(d)
            y.append(int(g.random() < (0.3 if c else 0.1)))
        return D, np.array(y)
    Dtr, ytr = rows(2000)
    Dte, yte = rows(2000)
    Xtr, Xte, names = design(Dtr, Dte)
    full = LogisticRegression(C=0.01, max_iter=2000).fit(Xtr, ytr).predict_proba(Xte)[:, 1]
    c = names.index("ctx")
    base = LogisticRegression(C=0.01, max_iter=2000).fit(Xtr[:, [c]], ytr).predict_proba(Xte[:, [c]])[:, 1]
    assert log_loss(yte, full) < log_loss(yte, base) + 0.01


def a(player, typ="Pass", to=None, loc=(30.0, 50.0)):
    e = {"type": {"name": typ}, "player": {"id": player}, "location": list(loc)}
    if to:
        e["pass"] = {"recipient": {"id": to}}
    return e


FIRST = [a(1, to=2, loc=(10.0, 70.0)), a(2, "Carry"), a(2, to=7)]


def test_zone_grid_6_by_4():
    assert zone([0.0, 0.0]) == "z0_0" and zone([119.9, 79.9]) == "z5_3" and zone([120.0, 80.0]) == "z5_3"


def test_motif_is_actor_pattern():
    assert motif(FIRST) == "ABB"
    assert motif([a(1), a(2), a(1)]) == "ABA"


def test_feature_blocks():
    ctx = {"pattern": "Regular Play", "diff": 3, "minute": 47, "home": 1}
    f = features(FIRST, ctx, frozenset({1, 2, 7}))
    assert f[0] == {"z0_3": 1, "pp=Regular Play": 1, "diff=2": 1, "min=3": 1, "home": 1}
    assert f[1] == {"p=1": 1, "p=2": 1, "p=7": 1, "1>2": 1, "2>7": 1}
    assert f[3] == {"motif=ABB": 1}
    assert f[5] == {"set=1,2,7": 1}
