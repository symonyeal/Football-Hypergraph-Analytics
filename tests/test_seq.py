"""Sequence features at the cutoff (H4) on hand-built actions."""

from fha.seq import features, motif, zone


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
