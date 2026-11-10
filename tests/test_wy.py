"""Wyscout event parsing: possessions rebuilt from consecutive on-ball events, attacking groups, shot features."""

from math import atan2, hypot, isclose

from fha.wy import attack_groups, possessions, shot


def e(i, name, team, player, sub="", period="1H", tags=(), pos=((50, 50),)):
    return {"id": i, "eventName": name, "subEventName": sub, "teamId": team, "playerId": player, "matchPeriod": period,
            "eventSec": float(i), "tags": [{"id": t} for t in tags], "positions": [{"x": x, "y": y} for x, y in pos]}


# Team 1: pass 11, pass 12, defending duel by team 2 (ignored), attacking duel 13, pass 13, shot 14.
# Team 2 then completes a pass: a new possession. Team 1 again: pass 11 then penalty (not open play).
EV = [e(1, "Pass", 1, 11), e(2, "Pass", 1, 12), e(3, "Duel", 2, 21, "Ground defending duel"), e(4, "Duel", 1, 13, "Ground attacking duel"),
      e(5, "Pass", 1, 13), e(6, "Shot", 1, 14, "Shot", tags=(101, 403), pos=((90, 50),)), e(7, "Pass", 2, 22, "Simple pass", tags=(1801,)),
      e(8, "Pass", 1, 11), e(9, "Free Kick", 1, 15, "Penalty")]


def test_possessions_split_on_team_change_and_period():
    P = possessions(EV)
    assert [[x["id"] for x in p] for p in P] == [[1, 2, 4, 5, 6], [7], [8, 9]]
    two = [e(1, "Pass", 1, 11, period="1H"), e(2, "Pass", 1, 12, period="2H")]
    assert len(possessions(two)) == 2


def test_a_lone_uncontrolled_opponent_touch_does_not_end_the_possession():
    # team 1 passes, team 2 deflects once (a touch, not an accurate pass), team 1 recovers and shoots
    ev = [e(1, "Pass", 1, 11), e(2, "Others on the ball", 2, 21, "Touch"), e(3, "Pass", 1, 12), e(4, "Shot", 1, 13, "Shot")]
    (p,) = possessions(ev)
    assert [x["id"] for x in p] == [1, 3, 4]
    (g,) = attack_groups(ev)
    assert g["A"] == frozenset({"w11", "w12", "w13"})
    # an accurate pass by team 2 is control: the possession changes
    ev2 = [e(1, "Pass", 1, 11), e(2, "Pass", 2, 21, tags=(1801,)), e(3, "Pass", 1, 12)]
    assert len(possessions(ev2)) == 3


def test_attack_group_last_three_distinct_actors_up_to_first_open_play_shot():
    (g,) = attack_groups(EV)
    assert g["team"] == 1 and g["A"] == frozenset({"w14", "w13", "w12"})
    assert g["shots"] == [shot(EV[5])]


def test_unescape_names():
    from fha.wy import unescape
    assert unescape("Ayoze P" + chr(92) + "u00e9rez") == "Ayoze Pérez"
    assert unescape("Neymar") == "Neymar"


def test_shot_features_in_metres():
    d, a, head, goal = shot(EV[5])
    x, y = 90 * 105 / 100, 50 * 68 / 100
    assert isclose(d, hypot(105 - x, 34 - y)) and head == 1 and goal == 1
    # angle subtended by the 7.32 m goal mouth
    assert isclose(a, abs(atan2(7.32 * (105 - x), (105 - x) ** 2 + (34 - y) ** 2 - (7.32 / 2) ** 2)))
