"""StatsBomb event parsing on a hand-built possession."""

from fha.sb import attack_groups, cutoff, metres


def ev(i, typ, team, player, poss=1, **kw):
    e = {"index": i, "type": {"name": typ}, "team": {"id": team}, "possession": poss,
         "possession_team": {"id": 10}, "player": {"id": player}, "location": [60.0, 40.0]}
    e.update(kw)
    return e


def P(i, player, to):
    return ev(i, "Pass", 10, player, **{"pass": {"recipient": {"id": to}}})


SHOT = {"shot": {"statsbomb_xg": 0.3, "type": {"name": "Open Play"}}}

# 1 -> 2, 2 carries, 2 -> 3, opponent pressure, 3 -> 1, 1 shoots, rebound by 4.
SEQ = [P(0, 1, 2), ev(1, "Carry", 10, 2), P(2, 2, 3), ev(3, "Pressure", 20, 9), P(4, 3, 1),
       ev(5, "Shot", 10, 1, **SHOT), ev(6, "Shot", 10, 4, **SHOT)]


def test_metres():
    assert metres([120.0, 80.0]) == (105.0, 68.0)


def test_attack_group_last_three_distinct_up_to_first_shot():
    (g,) = attack_groups(SEQ)
    assert g["team"] == 10
    assert g["A"] == frozenset({1, 3, 2})
    assert abs(g["xg"] - 0.6) < 1e-12


def test_no_group_without_open_play_shot():
    pen = ev(5, "Shot", 10, 1, shot={"statsbomb_xg": 0.76, "type": {"name": "Penalty"}})
    assert attack_groups([P(0, 1, 2), pen]) == []


def test_cutoff_after_third_non_shot_action():
    c = cutoff(SEQ)
    assert c["alive"] and c["y"] == 1 and c["P"] == frozenset({1, 2, 3})
    early = [P(0, 1, 2), ev(1, "Shot", 10, 2, **SHOT), P(2, 2, 3), P(3, 3, 1)]
    assert not cutoff(early)["alive"]
    short = [P(0, 1, 2), ev(1, "Carry", 10, 2)]
    assert not cutoff(short)["alive"]
    quiet = [P(0, 1, 2), ev(1, "Carry", 10, 2), P(2, 2, 3), ev(3, "Carry", 10, 3)]
    assert cutoff(quiet)["alive"] and cutoff(quiet)["y"] == 0
