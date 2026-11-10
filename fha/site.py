"""Build site/data.js (window.DATA) from results/*.json. The page filters and draws; the two calculations it repeats
in the browser (coverage of a chosen player set; the defence model's probability) are certified here first.

Usage: python -m fha.site
"""

import json
import math
from pathlib import Path

import numpy as np

from fha import attack, defence

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"


def plain(o, nd=5):
    if isinstance(o, dict):
        return {str(k): plain(v, nd) for k, v in o.items()}
    if isinstance(o, (list, tuple, np.ndarray)):
        return [plain(v, nd) for v in o]
    if isinstance(o, (float, np.floating)):
        return None if math.isnan(o) else float(f"{o:.{nd}g}")
    if isinstance(o, np.integer):
        return int(o)
    return o


def load(s):
    p = R / f"{s}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def certify(t):
    """cov(b) recomputed from the aggregated groups equals the published value; group xG sums to the total."""
    F, w = [set(g[0]) for g in t["groups"]], [g[2] for g in t["groups"]]
    for b, (share, P) in t["cov"].items():
        assert abs(attack.covered(P, F, w) - share) < 1e-9, (t["team"], t["key"], b)
    assert abs(sum(w) - t["xg"]) < 1e-6, (t["team"], t["key"])


def s2s(teams, comps):
    """Consecutive seasons of the same team in the same competition: pairs and Spearman with a bootstrap interval."""
    from scipy.stats import spearmanr
    meta = {c["key"]: c for c in comps}
    by = {}
    for t in teams:
        c = meta[t["key"]]
        by.setdefault((c["competition"], t["team_id"]), []).append((int(c["season"][:4]), c["season"], t))
    out = {}
    for k, get in (("tau", lambda t: t["tau"]), ("nu", lambda t: t["nu"]), ("top2", lambda t: t["cov"]["2"][0])):
        P, used = [], set()
        for (comp, _), L in by.items():
            L.sort(key=lambda r: r[0])
            for (y0, s0, a), (y1, s1, b) in zip(L, L[1:]):
                if y1 - y0 == 1:
                    P.append([a["team"], f"{comp} {s0} to {s1}", get(a), get(b)])
                    used.add(comp)
        rho = None
        if len(P) >= 8:
            x, y = np.array([p[2] for p in P], float), np.array([p[3] for p in P], float)
            g = np.random.default_rng(0)
            v = [spearmanr(x[i], y[i]).statistic for i in (g.integers(0, len(P), len(P)) for _ in range(2000))]
            rho = [float(spearmanr(x, y).statistic), [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))]]
        out[k] = {"pairs": P, "rho": rho, "comps": sorted(used)}
    return out


def checks(model):
    """Synthetic defender frames (never real data) scored in Python; the browser recomputes and compares."""
    g = np.random.default_rng(7)
    out = []
    for _ in range(6):
        P = np.round(np.column_stack([g.uniform(60, 100, 9), g.uniform(8, 60, 9)]), 3)   # rounded before scoring,
        bx, by = round(float(g.uniform(55, 85)), 3), round(float(g.uniform(10, 58)), 3)  # so data.js holds the exact inputs
        w, d, a = defence.shape(P)
        r, _ = defence.hole(P)
        f = {"x": bx, "yy": by, "dist": float(np.hypot(105 - bx, 34 - by)), "width": w, "depth": d, "area": a,
             "gap": defence.gap(P), "hole": r}
        z = model["intercept"] + sum(c * (f[k] - m) / s for k, c, m, s in zip(model["cols"], model["coef"], model["mean"], model["scale"]))
        out.append({"P": P.tolist(), "ball": [bx, by], "f": {k: float(f"{v:.9g}") for k, v in f.items()}, "p": float(f"{1 / (1 + math.exp(-z)):.9g}")})
    return out


def main():
    A, D, S, L, Z = load("attack"), load("defence"), load("sequence"), load("lineup"), load("seasons")
    names = {}
    for src in (A and A["names"], L and L.get("names"), Z and Z["names"]):   # later sources: common names
        names.update({str(k): v for k, v in (src or {}).items()})
    data = {"meta": {"source": "StatsBomb open data, hudl/open-data commit 4b73468"}, "names": names}
    if Z:
        for t in Z["teams"]:
            certify(t)
        keys = ("key", "team", "team_id", "matches", "xg_per_match", "groups", "m", "xg", "tau", "tau_star", "nu", "cov", "solo")
        data["seasons"] = {"competitions": Z["competitions"], "teams": [{k: t[k] for k in keys} for t in Z["teams"]]}
        data["s2s"] = s2s(Z["teams"], Z["competitions"])
    if A:
        full = {v: k for k, v in A["names"].items()}
        nick = lambda n: names.get(full.get(n, ""), n)
        halves = [{"team": t, "league": v["league"], **{W: {"tau": v[W]["tau"], "nu": v[W]["nu"], "top2": v[W]["cov"]["2"][0]}
                                                        for W in ("train", "test")}} for t, v in A["teams"].items()]
        H3 = {k: {**h, "teams": [[r[0], nick(r[1]), r[2], r[3], r[4]] for r in h["teams"]]} for k, h in A["H3"].items()}
        data["attack"] = {"halves": halves, "H1": A["H1"], "H1_q01": A["sensitivity_q0.1"], "H2": A["H2"], "H3": H3}
    if D:
        data["defence"] = {k: D[k] for k in D if k != "coef"}
        chk = checks(D["model"]["gaps"])
    if S:
        data["sequence"] = S
    if L:
        data["lineup"] = {k: L[k] for k in L if k != "names"}
    data = plain(data)
    if D:
        data["defence"]["model"] = D["model"]   # full precision: the browser recomputes with these
        data["defence"]["checks"] = chk         # exact inputs and 9-digit outputs, not rounded by plain()
    out = ROOT / "site" / "data.js"
    out.write_text("window.DATA = " + json.dumps(data, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + ";\n",
                   encoding="utf-8")
    print(f"{out}  {out.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
