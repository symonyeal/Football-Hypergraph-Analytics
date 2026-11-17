"""Audit of the attack, lineup, defence and sequence results from the committed aggregates (results/*.json); no raw
data and no Rust binary. Every number in docs/REVIEW.md section 2 is printed here.

Usage: python -m fha.audit      prints D1-D9 (and D10 when results/structure.json exists); seed 0, about two minutes.

Legend: F distinct groups (player sets) with c possessions and w xG; s support (players in any group);
m chances; tau, nu as in docs/MODEL.md; phi Shapley share of the coverage game = sum_{A ni v} w_A / |A|.
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

from fha import attack, mu

R = Path(__file__).resolve().parents[1] / "results"
g = np.random.default_rng(0)
def load(s):
    return json.loads((R / f"{s}.json").read_text(encoding="utf-8"))


def rho(a, b):
    return float(spearmanr(a, b).statistic)


def unit(E):
    return [(frozenset(e), 1.0) for e in {frozenset(e) for e in E}]


def tau(E):
    return mu.tau_a(unit(E), 1.0)


def nu(E):
    _, F, _ = mu.index(unit(E))
    return attack.nu(F, max(map(max, F)) + 1)[0]


def expand(G):
    """Aggregated [players, possessions, xG] to one (set, xG) per possession (xG split evenly within a group)."""
    return [(frozenset(p), x / c) for p, c, x in G for _ in range(c)]


def ch(G):
    """Aggregated groups as weighted chances."""
    return [(frozenset(p), x) for p, _, x in G]


def phi(G):
    return mu.phi(ch(G))


hill = mu.hill


def covered(S, G):
    return mu.c(S, ch(G))


def greedy(G, b):
    return mu.greedy(ch(G), b)


def tau_a(G, a=0.9):
    """Greedy upper bound on the fewest players meeting share a of xG."""
    b = 1
    while covered(greedy(G, b), G) < a:
        b += 1
    return b


def null(E):
    """N0 (fha.mu.redeal): same player degrees and group sizes, memberships re-dealt."""
    return [A for A, _ in mu.redeal([(e, 1.0) for e in E], g)]


A, Z, Y, L, D, Q = (load(s) for s in ("attack", "seasons", "wyscout", "lineup", "defence", "sequence"))

print("== D1 exposure and saturation, every team-season (seasons + wyscout)")
T = Z["teams"] + Y["teams"]
s = [len({v for p, _, _ in t["groups"] for v in p}) for t in T]
m = [t["m"] for t in T]
for k in ("tau", "nu"):
    v = [t[k] for t in T]
    print(f"{k}: n={len(T)}  rho(m)={rho(v, m):.2f}  rho(matches)={rho(v, [t['matches'] for t in T]):.2f}  rho(support)={rho(v, s):.2f}")
big = [i for i, t in enumerate(T) if t["matches"] >= 30]
print(f"full leagues only (matches >= 30, n={len(big)}): rho(tau, support)={rho([T[i]['tau'] for i in big], [s[i] for i in big]):.2f}  "
      f"rho(tau, m)={rho([T[i]['tau'] for i in big], [m[i] for i in big]):.2f}")
print(f"tau - nu: {dict(sorted(Counter(t['tau'] - t['nu'] for t in T).items()))}")
print(f"nu / floor(support/3): median {np.median([t['nu'] / (si // 3) for t, si in zip(T, s)]):.2f}; "
      f"tau / support: median {np.median([t['tau'] / si for t, si in zip(T, s)]):.2f}")

print("\n== D2 provider agreement, 2018 World Cup")
def norm(x):
    return x.lower().replace(" ", "")


a = {norm(t["team"]): t for t in Z["teams"] if t["key"] == "43/3"}
b = {norm(t["team"]): t for t in Y["teams"] if t["key"] == "wy/World_Cup"}
K = sorted(set(a) & set(b))
print([(a[k]["team"], a[k]["matches"], a[k]["tau"], b[k]["tau"]) for k in K])
print(f"rho(tau_SB, tau_WY)={rho([a[k]['tau'] for k in K], [b[k]['tau'] for k in K]):.2f}  "
      f"rho(tau_SB, matches)={rho([a[k]['tau'] for k in K], [a[k]['matches'] for k in K]):.2f}  "
      f"rho(tau_WY, matches)={rho([b[k]['tau'] for k in K], [a[k]['matches'] for k in K]):.2f}")

print("\n== D3 H2 baselines: held-out xG coverage of b = tau players chosen on the training half (80 teams)")
c = defaultdict(list)
for t in A["teams"].values():
    tr, te = t["train"], t["test"]
    bb = tr["tau"]
    ph = phi(tr["groups"])
    deg = Counter()
    for p, n, x in tr["groups"]:
        for v in p:
            deg[v] += n
    c["T transversal"].append(covered(tr["T_tau"], te["groups"]))
    c["C exact cover"].append(covered(tr["cov"][str(bb)][1], te["groups"]))
    c["U on-ball actions"].append(covered(tr["usage"][:bb], te["groups"]))
    c["top-b by chance count"].append(covered(sorted(deg, key=lambda v: -deg[v])[:bb], te["groups"]))
    c["top-b by Shapley xG share"].append(covered(sorted(ph, key=lambda v: -ph[v])[:bb], te["groups"]))
    c["greedy cover"].append(covered(greedy(tr["groups"], bb), te["groups"]))
for k, v in c.items():
    d = np.array(c["T transversal"]) - np.array(v)
    bs = [d[g.integers(0, len(d), len(d))].mean() for _ in range(2000)]
    print(f"{k:28s} mean {np.mean(v):.3f}   T minus it {d.mean():+.3f} ({np.percentile(bs, 2.5):+.3f} to {np.percentile(bs, 97.5):+.3f})")

print("\n== D4 split-half Spearman across the 80 teams, registered and alternative summaries")
W = {w: [t[w] for t in A["teams"].values()] for w in ("train", "test")}
f = {"tau": lambda t: t["tau"], "nu": lambda t: t["nu"], "cov2": lambda t: t["cov"]["2"][0],
     "support s": lambda t: len({v for p, _, _ in t["groups"] for v in p}), "chances m": lambda t: t["m"], "xG": lambda t: t["xg"],
     "Hill D1 of phi": lambda t: hill(phi(t["groups"]).values(), 1), "Hill D2 of phi": lambda t: hill(phi(t["groups"]).values(), 2),
     "tau_0.9 (greedy)": lambda t: tau_a(t["groups"]), "top phi": lambda t: max(phi(t["groups"]).values())}
val = {k: {w: np.array([h(t) for t in W[w]], float) for w in W} for k, h in f.items()}
for k in f:
    x, y = val[k]["train"], val[k]["test"]
    bs = [rho(x[i], y[i]) for i in (g.integers(0, 80, 80) for _ in range(2000))]
    print(f"{k:18s} {rho(x, y):.2f} ({np.nanpercentile(bs, 2.5):.2f} to {np.nanpercentile(bs, 97.5):.2f})   "
          f"same-half rho with support {rho(x, val['support s']['train']):+.2f}, with xG {rho(x, val['xG']['train']):+.2f}")

print("\n== D5 degree-preserving null (20 re-deals per team, training half)")
zt, zn, nt, nn, xt = [], [], [], [], []
for t, u in zip(W["train"], W["test"]):
    E = [p for p, _ in expand(t["groups"])]
    N = [null(E) for _ in range(20)]
    a_, b_ = np.array([tau(x) for x in N]), np.array([nu(x) for x in N])
    nt.append(a_.mean()), nn.append(b_.mean())
    zt.append((t["tau"] - a_.mean()) / max(a_.std(), 0.25)), zn.append((t["nu"] - b_.mean()) / max(b_.std(), 0.25))
    E = [p for p, _ in expand(u["groups"])]
    xt.append(u["tau"] - np.mean([tau(null(E)) for _ in range(20)]))
ex = np.array(val["tau"]["train"]) - np.array(nt)
bs = [rho(ex[i], np.array(xt)[i]) for i in (g.integers(0, 80, 80) for _ in range(2000))]
print(f"split-half Spearman of the excess tau - null mean: {rho(ex, xt):.2f} ({np.nanpercentile(bs, 2.5):.2f} to {np.nanpercentile(bs, 97.5):.2f}); "
      f"of the null mean itself: {rho(nt, np.array(val['tau']['test']) - np.array(xt)):.2f}")
ot, on = val["tau"]["train"], val["nu"]["train"]
print(f"tau: observed mean {ot.mean():.2f}, null mean {np.mean(nt):.2f}, rho(observed, null mean) {rho(ot, nt):.2f}, "
      f"mean |observed - null| {np.abs(ot - nt).mean():.2f}, teams with |z| > 2: {sum(abs(z) > 2 for z in zt)}/80")
print(f"nu:  observed mean {on.mean():.2f}, null mean {np.mean(nn):.2f}, rho(observed, null mean) {rho(on, nn):.2f}, "
      f"mean |observed - null| {np.abs(on - nn).mean():.2f}, teams with |z| > 2: {sum(abs(z) > 2 for z in zn)}/80")
print(f"observed minus null, tau: {dict(sorted(Counter(int(round(o - x)) for o, x in zip(ot, nt)).items()))}")

print("\n== D6 rarefaction: mean tau over 80 training halves at a common number of chances (10 subsamples each)")
for k in (25, 50, 100, 130):
    v = []
    for t in W["train"]:
        E = [p for p, _ in expand(t["groups"])]
        v.append(np.mean([tau([E[i] for i in g.choice(len(E), k, replace=False)]) for _ in range(10)]))
    print(f"m = {k:3d}: mean tau {np.mean(v):.2f}")
print(f"full (m from {int(val['chances m']['train'].min())} to {int(val['chances m']['train'].max())}): mean tau {ot.mean():.2f}")

print("\n== D7 season-to-season pairs")
meta = {c["key"]: c for c in Z["competitions"]}
by = defaultdict(list)
for t in Z["teams"]:
    by[(meta[t["key"]]["competition"], t["team"])].append((int(meta[t["key"]]["season"][:4]), t["matches"]))
P = Counter()
mm = []
for (comp, team), v in by.items():
    v.sort()
    for (y0, m0), (y1, m1) in zip(v, v[1:]):
        if y1 - y0 == 1:
            P[team if team in ("Barcelona", "Paris Saint-Germain") else comp] += 1
            mm.append((m0, m1))
print(dict(P), "matches per season in pairs: min", min(min(x) for x in mm), "max", max(max(x) for x in mm))

print("\n== D8 lineup ratings: share of rating variance between teams (team = the training-half usage list holding the player)")
team = {str(v): n for n, t in A["teams"].items() for v in t["train"]["usage"]}
r = [(team[v], (x[0] + x[1]) / 2) for v, x in L["ratings"].items() if v in team]
gm = np.mean([x for _, x in r])
bt = defaultdict(list)
for k, x in r:
    bt[k].append(x)
ssb = sum(len(v) * (np.mean(v) - gm) ** 2 for v in bt.values())
sst = sum((x - gm) ** 2 for _, x in r)
print(f"players {len(r)}, teams {len(bt)}, eta^2 = {ssb / sst:.2f}")
for w in ("train", "test"):
    print(w, "cv mse by lambda:", {k: round(v, 3) for k, v in L["windows"][w]["cv_mse"].items()})

print("\n== D9 effect sizes in log loss")
def h(p):
    return -(p * np.log(p) + (1 - p) * np.log(1 - p))


ll = D["logloss"]
print(f"defence: base rate {h(D['rate']['test']):.4f}; base {ll['base']:.4f}; shape {ll['shape']:.4f}; gaps {ll['gaps']:.4f}; topology {ll['topology']:.4f}")
print(f"  gain of ball position {h(D['rate']['test']) - ll['base']:.4f}; shape {ll['base'] - ll['shape']:.4f}; gap+hole {ll['shape'] - ll['gaps']:.4f}")
ql = Q["logloss"]
print(f"sequence: base rate {h(Q['rate']['test']):.4f}; " + "; ".join(f"model {k} {v:.4f}" for k, v in ql.items()))

print("\n== D11 Wyscout rebuild against StatsBomb, 2018 World Cup, exposure-free measures (review 4.5)")
for k_, f_ in (("c(2)", lambda G: mu.cb(ch(G), 2)[0]), ("D1 of phi", lambda G: hill(phi(G).values(), 1))):
    x_, y_ = np.array([f_(a[k]["groups"]) for k in K]), np.array([f_(b[k]["groups"]) for k in K])
    mt = [a[k]["matches"] for k in K]
    print(f"{k_:10s} rho(SB, WY)={rho(x_, y_):.2f}  mean WY - SB {np.mean(y_ - x_):+.3f} (range {np.min(y_ - x_):+.3f} to {np.max(y_ - x_):+.3f})  "
          f"rho(SB, matches)={rho(x_, mt):.2f}  rho(WY, matches)={rho(y_, mt):.2f}")

if (R / "structure.json").exists():
    X = load("structure")
    print("\n== D10 structure stage (exploratory; python -m fha.run structure): R1 reliability between halves, ICC(2,1) and Spearman")
    for lv, r1 in X["R1"].items():
        for k, v in r1.items():
            print(f"{lv:6s} {k:24s} ICC {v['icc'][0]:+.2f} ({v['icc'][1][0]:+.2f} to {v['icc'][1][1]:+.2f})   Spearman {v['spearman'][0]:+.2f}   teams {v['teams']}")
    print("R2 pooled excess over each null, full seasons (random-effects mean +- se; teams with z > 2 and z < -2)")
    for lv, r2 in X["R2"].items():
        for n, v in r2.items():
            print(f"{lv:6s} {n}  " + "   ".join(f"{k} {x['mean_excess']:+.3f} +- {x['se']:.3f} ({x['z_above_2']}, {x['z_below_-2']})" for k, x in v.items()))

