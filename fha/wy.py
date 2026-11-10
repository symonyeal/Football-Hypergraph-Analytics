"""Wyscout public events (Pappalardo et al. 2019, CC BY 4.0): possessions, attacking groups, shot features.

Wyscout has no possession ids and no xG. A possession is a maximal run of on-ball events by one team within a
period; duels, fouls, interruptions and saves do not end it, an on-ball event by the other team does. Player ids are
prefixed 'w' so they never collide with StatsBomb ids.

Legend: ev one event; positions x, y in 0-100 percent of the pitch, attacking towards x = 100.
"""

import json
from math import atan2, hypot

ONBALL = {"Pass", "Shot", "Others on the ball", "Free Kick"}
GOAL_W = 7.32


def onball(e):
    return e["eventName"] in ONBALL or e["subEventName"] == "Ground attacking duel"


def control(e):
    """An event that shows the team has the ball: an accurate pass (tag 1801), a shot or a restart."""
    return e["eventName"] in ("Shot", "Free Kick") or (e["eventName"] == "Pass" and any(t["id"] == 1801 for t in e["tags"]))


def possessions(ev):
    """Runs of on-ball events by one team. The other team takes over only with control or two consecutive on-ball
    events; a lone uncontrolled touch between two events of the same team (a deflection) is dropped."""
    E = [e for e in sorted(ev, key=lambda e: (e["matchPeriod"], e["eventSec"], e["id"])) if onball(e)]
    out, cur = [], []
    for i, e in enumerate(E):
        if cur and e["matchPeriod"] != cur[-1]["matchPeriod"]:
            out.append(cur)
            cur = []
        if cur and e["teamId"] != cur[-1]["teamId"]:
            nxt = E[i + 1] if i + 1 < len(E) else None
            if not control(e) and nxt is not None and nxt["teamId"] == cur[-1]["teamId"] and nxt["matchPeriod"] == e["matchPeriod"]:
                continue
            out.append(cur)
            cur = []
        cur.append(e)
    return out + ([cur] if cur else [])


def shot(e):
    """(distance to goal centre m, angle subtended by the goal mouth rad, header 0/1, goal 0/1) on a 105 x 68 pitch."""
    p = e["positions"][0]
    dx, dy = 105 - p["x"] * 105 / 100, 34 - p["y"] * 68 / 100
    tags = {t["id"] for t in e["tags"]}
    return (hypot(dx, dy), abs(atan2(GOAL_W * dx, dx * dx + dy * dy - (GOAL_W / 2) ** 2)), int(403 in tags), int(101 in tags))


def unescape(s):
    """Wyscout names arrive with JSON escapes left in the text (P\\u00e9rez); decode them once."""
    return json.loads(f'"{s}"') if "\\u" in s else s


def attack_groups(ev, k=3):
    """One record per possession with an open-play shot (eventName Shot): the last k distinct actors up to the first one."""
    out = []
    for P in possessions(ev):
        s = next((i for i, e in enumerate(P) if e["eventName"] == "Shot"), None)
        if s is None:
            continue
        A = []
        for e in reversed(P[: s + 1]):
            v = f"w{e['playerId']}"
            if e["playerId"] and v not in A:
                A.append(v)
            if len(A) == k:
                break
        out.append({"team": P[s]["teamId"], "A": frozenset(A), "shots": [shot(e) for e in P if e["eventName"] == "Shot"]})
    return out
