"""StatsBomb open-data events: attacking groups and sequence cutoffs (docs/HYPOTHESES.md, Definitions).

Legend: ev one event (StatsBomb JSON), on the possession team's on-ball actions in event order.
"""

from collections import defaultdict

ON = {"Pass", "Carry", "Dribble", "Shot"}


def metres(l):
    """StatsBomb 120 x 80 units to metres on a 105 x 68 pitch."""
    return l[0] * 105 / 120, l[1] * 68 / 80


def openplay(ev):
    return ev["type"]["name"] == "Shot" and ev["shot"]["type"]["name"] == "Open Play"


def onball(poss):
    """On-ball actions of the possession team, in event order."""
    return [e for e in sorted(poss, key=lambda e: e["index"]) if e["type"]["name"] in ON and e["team"]["id"] == e["possession_team"]["id"]]


def involved(on):
    """Players in order of involvement: each actor, then the pass recipient."""
    for e in on:
        yield e["player"]["id"]
        r = e.get("pass", {}).get("recipient")
        if r:
            yield r["id"]


def possessions(events):
    p = defaultdict(list)
    for e in events:
        p[e["possession"]].append(e)
    return [p[k] for k in sorted(p)]


def attack_groups(events, k=3):
    """One record per possession with an open-play shot: A = the last k distinct players up to the first such shot."""
    out = []
    for poss in possessions(events):
        on = onball(poss)
        s = next((i for i, e in enumerate(on) if openplay(e)), None)
        if s is None:
            continue
        A = []
        for v in reversed(list(involved(on[: s + 1]))):
            if v not in A:
                A.append(v)
            if len(A) == k:
                break
        out.append({"team": on[s]["team"]["id"], "possession": on[s]["possession"], "A": frozenset(A),
                    "xg": sum(e["shot"]["statsbomb_xg"] for e in on if openplay(e))})
    return out


def cutoff(poss, a=3):
    """State after the a-th non-shot on-ball action: alive (no shot before it), y (open-play shot after), P (players so far)."""
    on = onball(poss)
    c = None
    seen = 0
    for i, e in enumerate(on):
        if e["type"]["name"] == "Shot":
            break
        seen += 1
        if seen == a:
            c = i
            break
    if c is None:
        return {"alive": False, "y": 0, "P": frozenset(), "first": on}
    return {"alive": True, "y": int(any(openplay(e) for e in on[c + 1:])), "P": frozenset(involved(on[: c + 1])), "first": on[: c + 1]}
