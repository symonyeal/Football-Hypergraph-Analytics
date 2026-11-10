"""Registered tests H1-H3 and H5 (docs/HYPOTHESES.md) on StatsBomb open data, streamed at a pinned commit.

Usage: python -m fha.run attack|defence [--limit N]   (writes results/<stage>.json; --limit is a smoke test)
Raw data is never written to disk (StatsBomb Public Data User Agreement 1.2.1).

Legend: W window ('train' weeks 1-19 or 'test' 20-38), F family of attacking groups, w xG weights.
"""

import json
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from fha import attack, defence, sb

SHA = "4b73468fc5b0f1950f9f66fada70ad3a4f9327cb"
RAW = f"https://raw.githubusercontent.com/hudl/open-data/{SHA}/data"
LEAGUES = [(2, 27), (11, 27), (12, 27), (7, 27)]
D_TRAIN, D_TEST = [(55, 43), (43, 106)], [(55, 282)]
OUT = Path(__file__).resolve().parents[1] / "results"
B, SEED = 2000, 0


def get(path):
    for t in range(5):
        try:
            with urllib.request.urlopen(f"{RAW}/{path}", timeout=120) as r:
                return json.loads(r.read())
        except Exception:
            if t == 4:
                raise
            time.sleep(2 ** t)


def boot(f, n, seed=SEED):
    """Percentile 95% interval of statistic f over B resamples of n units."""
    g = np.random.default_rng(seed)
    v = [f(g.integers(0, n, n)) for _ in range(B)]
    return [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))]


def rho(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(spearmanr(a, b).statistic), boot(lambda i: spearmanr(a[i], b[i]).statistic, len(a))


# ---------------------------------------------------------------- attack (H1-H3)

def collect(limit):
    """Per team and window: attacking groups, usage, names; per match: lineups and open-play xG."""
    G = defaultdict(list)            # (team, W) -> [(A, xg)]
    U = defaultdict(Counter)         # (team, W) -> player -> on-ball actions
    names, league = {}, {}
    games = []                       # (team, opp, W, xg, started set, appeared set)
    for c, s in LEAGUES:
        ms = sorted(get(f"matches/{c}/{s}.json"), key=lambda m: m["match_date"])
        for m in ms[:limit] + ms[-limit:] if limit else ms:
            W = "train" if m["match_week"] <= 19 else "test"
            ev = get(f"events/{m['match_id']}.json")
            lu = get(f"lineups/{m['match_id']}.json")
            h, a = m["home_team"]["home_team_id"], m["away_team"]["away_team_id"]
            names[h], names[a] = m["home_team"]["home_team_name"], m["away_team"]["away_team_name"]
            league[h] = league[a] = m["competition"]["competition_name"]
            for g in sb.attack_groups(ev):
                G[(g["team"], W)].append((g["A"], g["xg"]))
            xg = Counter()
            for e in ev:
                if "player" in e:
                    names[e["player"]["id"]] = e["player"]["name"]
                if e["type"]["name"] in sb.ON and e["team"]["id"] == e["possession_team"]["id"]:
                    U[(e["team"]["id"], W)][e["player"]["id"]] += 1
                if sb.openplay(e):
                    xg[e["team"]["id"]] += e["shot"]["statsbomb_xg"]
            for t in lu:
                st = {p["player_id"] for p in t["lineup"] if any(q["start_reason"] == "Starting XI" for q in p["positions"])}
                ap = {p["player_id"] for p in t["lineup"] if p["positions"]}
                o = a if t["team_id"] == h else h
                games.append((t["team_id"], o, W, xg[t["team_id"]], st, ap))
    return G, U, names, league, games


def measures(Fw, U):
    """Attack measures of one team window. Players are indexed by on-ball actions, then id."""
    ids = sorted(set(U) | {v for A, _ in Fw for v in A}, key=lambda v: (-U[v], v))
    ix = {v: i for i, v in enumerate(ids)}
    F = [frozenset(ix[v] for v in A) for A, _ in Fw]
    w = [x for _, x in Fw]
    n = len(ids)
    ts, x, _ = attack.tau_star(F, n)
    T = attack.minimum(F, n)
    Tt = min(T, key=lambda t: (-sum(x[i] for i in t), [ids[i] for i in t]))
    nv, _ = attack.nu(F, n)
    cv = {b: attack.cov(F, w, n, b) for b in sorted({1, 2, 3, 4, 5, len(Tt)})}
    solo = sum(wi for A, wi in Fw if len(A) == 1) / sum(w)
    vs = max(range(n), key=lambda i: (x[i], U[ids[i]], -ids[i]))
    return {"n": n, "m": len(F), "xg": sum(w), "tau": len(Tt), "tau_star": ts, "nu": nv, "count_min": len(T),
            "T_tau": [ids[i] for i in Tt], "cov": {b: [s, [ids[i] for i in t]] for b, (s, t) in cv.items()},
            "x_star": {ids[i]: x[i] for i in range(n) if x[i] > 1e-9}, "v_star": ids[vs],
            "usage": ids, "solo": solo}


def stage_attack(limit=None):
    G, U, names, league, games = collect(limit)
    teams = sorted({t for t, W in G if (t, "test") in G and (t, "train") in G})
    R = {}
    for q in (0.0, 0.1):
        R[q] = {}
        for t in teams:
            R[q][t] = {}
            for W in ("train", "test"):
                Fw = [(A, x) for A, x in G[(t, W)] if x >= q]
                R[q][t][W] = measures(Fw, U[(t, W)]) if Fw else None
    M = R[0.0]
    out = {"teams": {}, "H1": {}, "H2": {}, "H3": {}, "sensitivity_q0.1": {}}
    for t in teams:
        out["teams"][names[t]] = {"league": league[t], **{W: M[t][W] for W in ("train", "test")}}
    # H1: split-half stability
    for k in ("tau", "tau_star", "nu"):
        out["H1"][k] = rho([M[t]["train"][k] for t in teams], [M[t]["test"][k] for t in teams])
        ok = [t for t in teams if R[0.1][t]["train"] and R[0.1][t]["test"]]
        out["sensitivity_q0.1"][k] = rho([R[0.1][t]["train"][k] for t in ok], [R[0.1][t]["test"][k] for t in ok])
    out["H1"]["cov2"] = rho([M[t]["train"]["cov"][2][0] for t in teams], [M[t]["test"]["cov"][2][0] for t in teams])
    # H2: held-out coverage of transversal, exact-coverage and usage sets of equal size
    cT, cC, cU = [], [], []
    for t in teams:
        tr, Ft = M[t]["train"], [(set(A), x) for A, x in G[(t, "test")]]
        b = tr["tau"]
        Fs, w = [A for A, _ in Ft], [x for _, x in Ft]
        cT.append(attack.covered(tr["T_tau"], Fs, w))
        cC.append(attack.covered(tr["cov"][b][1], Fs, w))
        cU.append(attack.covered(tr["usage"][:b], Fs, w))
    cT, cC, cU = map(np.array, (cT, cC, cU))
    for k, d in (("C_minus_U", cC - cU), ("T_minus_U", cT - cU)):
        out["H2"][k] = [float(d.mean()), boot(lambda i: d[i].mean(), len(d))]
    out["H2"]["mean_coverage"] = {"T": float(cT.mean()), "C": float(cC.mean()), "U": float(cU.mean())}
    # H3: absence of the top bottleneck player
    conceded = defaultdict(list)
    for t, o, W, xg, _, _ in games:
        if W == "train":
            conceded[o].append(xg)
    cbar = {o: float(np.mean(v)) for o, v in conceded.items()}
    for key, pick in (("bottleneck", lambda t: M[t]["train"]["v_star"]), ("usage", lambda t: M[t]["train"]["usage"][0])):
        rows = []
        for t in teams:
            v = pick(t)
            a_abs = [xg / cbar[o] for tt, o, W, xg, st, ap in games if tt == t and W == "test" and v not in ap and cbar.get(o)]
            a_st = [xg / cbar[o] for tt, o, W, xg, st, ap in games if tt == t and W == "test" and v in st and cbar.get(o)]
            if len(a_abs) >= 3 and len(a_st) >= 3:
                rows.append((t, names[v], len(a_abs), len(a_st), 1 - np.mean(a_abs) / np.mean(a_st)))
        out["H3"][key] = {"teams": [[names[t], p, na, ns, float(d)] for t, p, na, ns, d in rows]}
        if len(rows) >= 5:
            d = [r[4] for r in rows]
            out["H3"][key]["rho_nu"] = rho([M[r[0]]["train"]["nu"] for r in rows], d)
            out["H3"][key]["rho_cov2"] = rho([M[r[0]]["train"]["cov"][2][0] for r in rows], d)
    out["names"] = {str(k): v for k, v in names.items()}
    return out


# ---------------------------------------------------------------- defence (H5)

def secs(e):
    h, m, s = e["timestamp"].split(":")
    return (e["period"], int(h) * 3600 + int(m) * 60 + float(s))


def inbox(l):
    return l[0] >= 102 and 18 <= l[1] <= 62


def passes(m):
    """Feature rows of one match: open-play passes in the opponent half, outside the box, >= 6 visible defenders."""
    ev = get(f"events/{m['match_id']}.json")
    ff = {f["event_uuid"]: f for f in get(f"three-sixty/{m['match_id']}.json")}
    byp = defaultdict(list)
    for e in ev:
        byp[e["possession"]].append(e)
    rows = []
    for e in ev:
        if e["type"]["name"] != "Pass" or "type" in e["pass"] or e["team"]["id"] != e["possession_team"]["id"]:
            continue
        l = e["location"]
        if l[0] < 60 or inbox(l) or e["id"] not in ff:
            continue
        D = np.array([sb.metres(p["location"]) for p in ff[e["id"]]["freeze_frame"] if not p["teammate"] and not p["keeper"]])
        if len(D) < 6:
            continue
        p0, t0 = secs(e)
        y = int(any(x["team"]["id"] == e["team"]["id"] and "location" in x and inbox(x["location"])
                    and secs(x)[0] == p0 and t0 < secs(x)[1] <= t0 + 10 for x in byp[e["possession"]]))
        bx, by = sb.metres(l)
        r, o = defence.hole(D)
        end = np.array(sb.metres(e["pass"]["end_location"]))
        rows.append({"match": m["match_id"], "y": y, "x": bx, "yy": by, "dist": float(np.hypot(105 - bx, 34 - by)),
                     **dict(zip(("width", "depth", "area"), defence.shape(D))), "gap": defence.gap(D), "hole": r,
                     "h1": defence.h1(D), "in_hole": bool(o is not None and np.linalg.norm(end - o) <= r)})
    return rows


def stage_defence(limit=None):
    data = {}
    for W, comps in (("train", D_TRAIN), ("test", D_TEST)):
        data[W] = []
        for c, s in comps:
            ms = get(f"matches/{c}/{s}.json")
            for m in ms[:limit] if limit else ms:
                data[W] += passes(m)
    sets = {"base": ["x", "yy", "dist"], "shape": ["x", "yy", "dist", "width", "depth", "area"],
            "gaps": ["x", "yy", "dist", "width", "depth", "area", "gap", "hole"],
            "topology": ["x", "yy", "dist", "width", "depth", "area", "gap", "hole", "h1"]}
    tr, te = data["train"], data["test"]
    ytr, yte = np.array([r["y"] for r in tr]), np.array([r["y"] for r in te])
    mt = np.array([r["match"] for r in te])
    L = {}
    for k, cols in sets.items():
        X = lambda R: np.array([[r[c] for c in cols] for r in R])
        f = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=1000)).fit(X(tr), ytr)
        p = f.predict_proba(X(te))[:, 1]
        L[k] = -(yte * np.log(p) + (1 - yte) * np.log(1 - p))
        coef = dict(zip(cols, f[-1].coef_[0].tolist()))
        L[k + "_coef"] = coef
    u = np.unique(mt)
    idx = {g: np.flatnonzero(mt == g) for g in u}

    def paired(a, b):
        d = L[a] - L[b]
        return [float(d.mean()), boot(lambda i: np.concatenate([d[idx[u[j]]] for j in i]).mean(), len(u))]

    out = {"n": {"train": len(tr), "test": len(te)}, "rate": {"train": float(ytr.mean()), "test": float(yte.mean())},
           "logloss": {k: float(L[k].mean()) for k in sets},
           "H5a_gaps_vs_shape": paired("gaps", "shape"), "H5b_topology_vs_gaps": paired("topology", "gaps"),
           "shape_vs_base": paired("shape", "base"), "coef": {k: L[k + "_coef"] for k in sets}}
    allr = tr + te
    for k in ("gap", "hole", "h1"):
        v = np.array([r[k] for r in allr])
        y = np.array([r["y"] for r in allr])
        qs = np.quantile(v, [0, .25, .5, .75, 1])
        out[f"{k}_quartiles_m"] = qs.tolist()
        out[f"{k}_entry_rate_by_quartile"] = [float(y[(v >= qs[i]) & (v <= qs[i + 1])].mean()) for i in range(4)]
    ih = np.array([r["in_hole"] for r in allr])
    y = np.array([r["y"] for r in allr])
    out["in_hole_share"] = {"entry": float(ih[y == 1].mean()), "all": float(ih.mean()),
                            "entry_rate_in_hole": float(y[ih].mean()) if ih.any() else None, "entry_rate_outside": float(y[~ih].mean())}
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    limit = int(a[a.index("--limit") + 1]) if "--limit" in a else None
    OUT.mkdir(exist_ok=True)
    for s in [x for x in a if x in ("attack", "defence")]:
        r = {"attack": stage_attack, "defence": stage_defence}[s](limit)
        name = f"{s}{'-smoke' if limit else ''}.json"
        (OUT / name).write_text(json.dumps(r, indent=1, default=str, ensure_ascii=False), encoding="utf-8")
        print(s, "written", OUT / name)
