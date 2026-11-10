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


def team_block(name, v, N):
    """One team: per window the groups, the published sets and measures. Certificate: cov(b) recomputed from groups."""
    out = {"league": v["league"]}
    for W in ("train", "test"):
        a = v[W]
        G = a["groups"]
        F, w = [set(g[0]) for g in G], [g[2] for g in G]
        for b, (share, T) in a["cov"].items():
            assert abs(attack.covered(T, F, w) - share) < 1e-9, (name, W, b)
        assert abs(sum(w) - a["xg"]) < 1e-6, (name, W)
        out[W] = {"groups": G, "tau": a["tau"], "tau_star": a["tau_star"], "nu": a["nu"], "m": a["m"], "xg": a["xg"],
                  "T": a["T_tau"], "cov": {b: c for b, c in a["cov"].items()}, "usage": a["usage"][:25], "solo": a["solo"]}
    ids = {p for W in ("train", "test") for g in out[W]["groups"] for p in g[0]} | set(out["train"]["usage"])
    return out, {str(p): N[str(p)] for p in ids if str(p) in N}


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
    A, D, S, L = load("attack"), load("defence"), load("sequence"), load("lineup")
    data = {"meta": {"source": "StatsBomb open data, hudl/open-data commit 4b73468"}}
    if A:
        N, teams, names = A["names"], {}, {}
        for t, v in A["teams"].items():
            teams[t], nm = team_block(t, v, N)
            names.update(nm)
        data["attack"] = {"teams": teams, "names": names, "H1": A["H1"], "H1_q01": A["sensitivity_q0.1"], "H2": A["H2"], "H3": A["H3"]}
    if D:
        data["defence"] = {k: D[k] for k in D if k != "coef"}
        chk = checks(D["model"]["gaps"])
    if S:
        data["sequence"] = S
    if L:
        data["lineup"] = L
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
