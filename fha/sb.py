"""StatsBomb open-data events: attacking groups and sequence cutoffs (docs/HYPOTHESES.md, Definitions).

Legend: ev one event (StatsBomb JSON), on the possession team's on-ball actions in event order.
"""

from collections import Counter, defaultdict

ON = {"Pass", "Carry", "Dribble", "Shot"}

# StatsBomb positions merged to nine roles (docs/REVIEW.md 4.2); left and right sides are one role
ROLE = {"Goalkeeper": "GK", "Center Back": "CB", "Left Center Back": "CB", "Right Center Back": "CB",
        "Left Back": "FB", "Right Back": "FB", "Left Wing Back": "FB", "Right Wing Back": "FB",
        "Center Defensive Midfield": "DM", "Left Defensive Midfield": "DM", "Right Defensive Midfield": "DM",
        "Center Midfield": "CM", "Left Center Midfield": "CM", "Right Center Midfield": "CM",
        "Left Midfield": "WM", "Right Midfield": "WM",
        "Center Attacking Midfield": "AM", "Left Attacking Midfield": "AM", "Right Attacking Midfield": "AM",
        "Left Wing": "W", "Right Wing": "W",
        "Center Forward": "CF", "Left Center Forward": "CF", "Right Center Forward": "CF", "Striker": "CF", "Secondary Striker": "CF"}


def roles(events):
    """Each player's role in one match: the role of the position most often on their events (events tagged with
    no playing position, such as 'Substitute', are skipped)."""
    n = defaultdict(Counter)
    for e in events:
        r = ROLE.get(e.get("position", {}).get("name"))
        if "player" in e and r:
            n[e["player"]["id"]][r] += 1
    return {v: c.most_common(1)[0][0] for v, c in n.items()}


def metres(l):
    """StatsBomb 120 x 80 units to metres on a 105 x 68 pitch."""
    return l[0] * 105 / 120, l[1] * 68 / 80


def openplay(ev):
    return ev["type"]["name"] == "Shot" and ev["shot"]["type"]["name"] == "Open Play"


def goal(ev):
    """A goal for ev's team: a scored shot or an own goal by the opponent."""
    return (ev["type"]["name"] == "Shot" and ev["shot"]["outcome"]["name"] == "Goal") or ev["type"]["name"] == "Own Goal For"


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


def clock(s):
    """'MM:SS' match clock to minutes."""
    m, x = s.split(":")
    return int(m) + int(x) / 60


def u(c, period):
    """Time axis with one 100-minute block per period, so first-half stoppage never overlaps the second half."""
    return c + 100 * (period - 1)


def intervals(lu, h, a, end):
    """On-pitch intervals from lineups JSON lu: team id -> [(player, start, stop)] on the u axis, open stops at end."""
    on = {h: [], a: []}
    for t in lu:
        for p in t["lineup"]:
            for q in p["positions"]:
                b = u(clock(q["from"]), q.get("from_period") or 1)
                c = u(clock(q["to"]), q.get("to_period") or 1) if q["to"] else end
                on[t["team_id"]].append((p["player_id"], b, c))
    return on


def stints(lu, h, a, shots, spans):
    """Intervals of constant personnel within the played spans (start, end) on the u axis.
    lu: lineups JSON; h, a: team ids; shots: (u, team, xG). Each stint: t0, t1, home and away player sets,
    open-play xG of each side, manpower = |home| - |away|."""
    end = max(b for _, b in spans)
    on = intervals(lu, h, a, end)
    cuts = sorted({x for sp in spans for x in sp} | {x for v in on.values() for _, b, c in v for x in (b, c) if 0 < x < end})
    S = []
    for t0, t1 in zip(cuts, cuts[1:]):
        mid = (t0 + t1) / 2
        if not any(a0 <= mid < a1 for a0, a1 in spans):
            continue
        H, A = ({i for i, b, c in on[s] if b <= mid < c} for s in (h, a))
        xh, xa = (sum(x for m, t, x in shots if t == s and t0 <= m < t1) for s in (h, a))
        S.append({"t0": t0, "t1": t1, "home": H, "away": A, "manpower": len(H) - len(A), "xg_home": xh, "xg_away": xa})
    return S
