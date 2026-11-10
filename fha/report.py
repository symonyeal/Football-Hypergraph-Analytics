"""Readable results pages from results/<stage>.json: glossary, registered verdicts, tables.

Usage: python -m fha.report   (rewrites results/attack.md and results/defence.md when their JSON exists)
"""

import json
from pathlib import Path
from statistics import median

R = Path(__file__).resolve().parents[1] / "results"
LOGO = "![StatsBomb](https://raw.githubusercontent.com/hudl/open-data/4b73468fc5b0f1950f9f66fada70ad3a4f9327cb/img/SB%20-%20Icon%20Lockup%20-%20Colour%20positive.png)"
SRC = ("Data: StatsBomb open data, commit `4b73468` of `hudl/open-data`. Analysis is this repository's, not StatsBomb's.\n\n"
       + LOGO + "\n")


def verdict(ci, want=">"):
    lo, hi = ci
    if lo > 0:
        return "holds" if want == ">" else "reversed"
    if hi < 0:
        return "holds" if want == "<" else "reversed"
    return "not resolved (interval contains 0)"


def f(x, d=2):
    return f"{x:.{d}f}"


ATTACK_GLOSSARY = """| Metric | What it counts | High value means | Low value means | It is not |
| --- | --- | --- | --- | --- |
| `tau` | Fewest players such that every dangerous attack (open-play shot possession) involved at least one of them, counting the last three players before the shot | Danger comes from many separate places; no small group is behind every chance | A few players are behind every chance | A rating of those players; marking them would not necessarily stop attacks |
| `tau*` | Fractional version of `tau`: the least total weight on players so that every attack carries weight at least 1 | As `tau` | As `tau` | — |
| `nu` | Most dangerous attacks that share no player at all | Many fully separate routes to a shot; stopping all of them needs at least `nu` players | Attacks overlap in the same people | A count of attacks |
| `cov(2)` | Largest share of the team's open-play xG in which at least one of two players took part | The attack depends on two players | Danger is spread | Those players' xG; involvement is any of the last three |
| `x*` share | A player's part of the fractional `tau*` | The player is a bottleneck: many attacks have few alternatives to them | The player's attacks have alternatives | Touches or usage |
| `solo` | Share of xG from attacks where one player was the only one involved | Individual creation (dribble-and-shoot, loose-ball finishes) | Combination play | — |
"""


def attack():
    r = json.loads((R / "attack.json").read_text(encoding="utf-8"))
    N = r["names"]
    nm = lambda ids: ", ".join(N[str(i)] for i in ids)
    L = ["# Attack structure: concentration and redundancy", "", SRC,
         "Windows: training = match weeks 1–19 of 2015/16, test = weeks 20–38. Registered tests: `docs/HYPOTHESES.md`.", "",
         "## What the metrics mean", "", ATTACK_GLOSSARY,
         "## H1. Are these team properties?", "",
         "Spearman correlation of each metric between the two half-seasons across teams, with a 95% bootstrap interval.", "",
         "| Metric | Correlation | Interval | Verdict | Same with xG ≥ 0.1 attacks only |", "| --- | --- | --- | --- | --- |"]
    for k in ("tau", "tau_star", "nu", "cov2"):
        v, ci = r["H1"][k]
        s = r["sensitivity_q0.1"].get(k)
        L.append(f"| `{k}` | {f(v)} | {f(ci[0])} to {f(ci[1])} | {verdict(ci)} | {f(s[0]) + ' (' + f(s[1][0]) + ' to ' + f(s[1][1]) + ')' if s else '—'} |")
    h2 = r["H2"]
    L += ["", "## H2. Do transversal sets find the key players better than usage?", "",
          "Share of test-period dangerous xG involving the chosen players. Each set has `tau` players, chosen on the training half.", "",
          "| Set | Mean held-out coverage |", "| --- | --- |",
          f"| Minimum transversal `T` | {f(h2['mean_coverage']['T'])} |",
          f"| Exact best coverage `C` | {f(h2['mean_coverage']['C'])} |",
          f"| Most on-ball actions `U` | {f(h2['mean_coverage']['U'])} |", "",
          f"`C − U` = {f(h2['C_minus_U'][0], 3)} (interval {f(h2['C_minus_U'][1][0], 3)} to {f(h2['C_minus_U'][1][1], 3)}): {verdict(h2['C_minus_U'][1])}. "
          f"`T − U` = {f(h2['T_minus_U'][0], 3)} (interval {f(h2['T_minus_U'][1][0], 3)} to {f(h2['T_minus_U'][1][1], 3)}): {verdict(h2['T_minus_U'][1])}.", "",
          "## H3. Do teams with fewer separate routes suffer more when their bottleneck player is missing?", "",
          "Drop = 1 − (team xG relative to the opponent's usual concession, in matches the player missed) / (the same, in matches the player started). "
          "Observational: rotation and injury are not random.", ""]
    for key, lab in (("bottleneck", "Top `x*` player"), ("usage", "Top usage player")):
        h = r["H3"][key]
        L.append(f"**{lab}.** {len(h['teams'])} eligible teams.")
        if "rho_nu" in h:
            v, ci = h["rho_nu"]
            c, cc = h["rho_cov2"]
            L.append(f" Correlation of drop with training `nu`: {f(v)} ({f(ci[0])} to {f(ci[1])}), {verdict(ci, '<')}; "
                     f"with `cov(2)`: {f(c)} ({f(cc[0])} to {f(cc[1])}), {verdict(cc)}.")
        L += ["", "| Team | Player | Missed | Started | Drop |", "| --- | --- | --- | --- | --- |"]
        L += [f"| {t} | {p} | {a} | {s} | {f(d)} |" for t, p, a, s, d in sorted(h["teams"], key=lambda x: -x[4])]
        L.append("")
    L += ["## Teams", "", "Training half; test-half value in brackets. `cov(2)` names the two players.", "",
          "| Team | League | Attacks | `tau` | `nu` | `cov(2)` | Two players | Bottleneck (`x*` share) | Solo xG |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for t, v in sorted(r["teams"].items(), key=lambda kv: (kv[1]["league"], kv[0])):
        a, b = v["train"], v["test"]
        vs = a["v_star"]
        share = a["x_star"][str(vs)] / a["tau_star"]
        L.append(f"| {t} | {v['league']} | {a['m']} | {a['tau']} ({b['tau']}) | {a['nu']} ({b['nu']}) | "
                 f"{f(a['cov']['2'][0])} ({f(b['cov']['2'][0])}) | {nm(a['cov']['2'][1])} | {N[str(vs)]} ({f(share)}) | {f(a['solo'])} |")
    L += ["", "## League medians (training half)", "", "| League | `tau` | `nu` | `cov(2)` |", "| --- | --- | --- | --- |"]
    for lg in sorted({v["league"] for v in r["teams"].values()}):
        T = [v["train"] for v in r["teams"].values() if v["league"] == lg]
        L.append(f"| {lg} | {median(x['tau'] for x in T)} | {median(x['nu'] for x in T)} | {f(median(x['cov']['2'][0] for x in T))} |")
    (R / "attack.md").write_text("\n".join(L) + "\n", encoding="utf-8")


DEF_GLOSSARY = """| Metric | What it measures (metres) | High value means | It is not |
| --- | --- | --- | --- |
| `gap` | Longest link of the shortest network joining the visible outfield defenders | One defender is far from every teammate: a wide hole between neighbours | Distance to the ball |
| `hole` | Radius of the largest circle inside the defensive block that touches three defenders and contains none | Large empty space inside the block | Space behind or beside the block |
| `h1` | Lifetime of the longest-lived ring of defenders in the alpha filtration | A ring of defenders around a gap that stays open over a range of distances | A new kind of space: it is computed from the same triangles as `hole` |
| `width`, `depth`, `area` | Spread across and along the pitch, area of the block | Stretched block | — |
"""


def defence():
    r = json.loads((R / "defence.json").read_text(encoding="utf-8"))
    L = ["# Defensive shape at the moment of a pass", "", SRC,
         "Passes: open play, attacking team, starting in the opponent half outside the box, at least 6 outfield defenders visible in the 360 frame. "
         "Label: the attacking team has an event in the box within 10 s in the same possession. Training: Euro 2020 and World Cup 2022; test: Euro 2024.", "",
         "## What the metrics mean", "", DEF_GLOSSARY,
         f"Passes: {r['n']['train']} training, {r['n']['test']} test. Box-entry rate: {f(r['rate']['train'], 3)} training, {f(r['rate']['test'], 3)} test.", "",
         "## H5. Do gaps and holes predict box entries, and does topology add anything?", "",
         "| Model | Test log loss |", "| --- | --- |"]
    L += [f"| {k} | {f(v, 4)} |" for k, v in r["logloss"].items()]
    for k, lab, want in (("shape_vs_base", "Shape over ball position", "<"), ("H5a_gaps_vs_shape", "H5a: gap and hole over shape", "<"),
                         ("H5b_topology_vs_gaps", "H5b: h1 over gap and hole", "<")):
        d, ci = r[k]
        L.append(f"\n**{lab}.** Change in log loss {f(d, 4)} ({f(ci[0], 4)} to {f(ci[1], 4)}): {verdict(ci, want)}"
                 + (" — registered expectation is 'not resolved'." if k.startswith("H5b") else "."))
    L += ["", "## How box-entry rate changes with each measure", "", "All passes, quartiles of the measure.", "",
          "| Measure | Q1 range (m) | Q1 rate | Q2 rate | Q3 rate | Q4 rate | Q4 range (m) |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for k in ("gap", "hole", "h1"):
        q, e = r[f"{k}_quartiles_m"], r[f"{k}_entry_rate_by_quartile"]
        L.append(f"| `{k}` | {f(q[0], 1)}–{f(q[1], 1)} | {f(e[0], 3)} | {f(e[1], 3)} | {f(e[2], 3)} | {f(e[3], 3)} | {f(q[3], 1)}–{f(q[4], 1)} |")
    ih = r["in_hole_share"]
    L += ["", f"Passes ending inside the largest hole: {f(ih['all'], 3)} of all passes, {f(ih['entry'], 3)} of box-entry passes. "
          f"Box-entry rate {f(ih['entry_rate_in_hole'], 3) if ih['entry_rate_in_hole'] is not None else '—'} when the pass ends in the hole, "
          f"{f(ih['entry_rate_outside'], 3)} otherwise.", "",
          "## Standardised coefficients", "", "| Model | Coefficients |", "| --- | --- |"]
    L += [f"| {k} | " + ", ".join(f"{c} {f(v, 3)}" for c, v in cs.items()) + " |" for k, cs in r["coef"].items()]
    (R / "defence.md").write_text("\n".join(L) + "\n", encoding="utf-8")


SEQ_GLOSSARY = """| Metric | Meaning |
| --- | --- |
| `p_shot` | Probability that a possession still alive after three on-ball actions produces an open-play shot |
| Log loss | Average penalty for the predicted probabilities; lower is better. Differences between models are the information a feature block adds |
| `who_gain` | Log-loss improvement from adding the set of players involved (model 5) to everything about what happened and where (model 4). Above the threshold: who is on the ball matters beyond the actions themselves |
"""

MODEL_NAMES = {0: "context", 1: "context + players + pass pairs", 2: "context + VAEP action features", 3: "1 + pass motif",
               4: "2 ∪ 3 (full rival)", 5: "4 + player set"}


def sequence():
    r = json.loads((R / "sequence.json").read_text(encoding="utf-8"))
    L = ["# Does who is involved predict danger beyond what happens?", "", SRC,
         f"Possessions alive after three on-ball actions: {r['n']['train']} training, {r['n']['test']} test; "
         f"shot rate {f(r['rate']['train'], 3)} and {f(r['rate']['test'], 3)}.", "", "## What the metrics mean", "", SEQ_GLOSSARY,
         "| Model | Penalty C | Test log loss | Brier |", "| --- | --- | --- | --- |"]
    L += [f"| {k}: {MODEL_NAMES[int(k)]} | {r['C'][k]} | {f(r['logloss'][k], 4)} | {f(r['brier'][k], 4)} |" for k in r["logloss"]]
    L += ["", "| Added information | Change in log loss | Interval |", "| --- | --- | --- |"]
    for k, lab in (("d10", "players and pass pairs over context"), ("d20", "VAEP action features over context"),
                   ("d31", "pass motif over players"), ("d42", "players, pairs, motif over VAEP"), ("d43", "VAEP over players and motif"),
                   ("d54", "player set over the full rival (who_gain)")):
        d, ci = r[k]
        L.append(f"| {lab} | {f(d, 5)} | {f(ci[0], 5)} to {f(ci[1], 5)} |")
    h = r["H4"]
    L += ["", f"**H4.** Registered threshold: improvement of at least {f(h['threshold'], 5)}. "
          + ("Holds: the set of players carries information beyond the actions." if h["holds"] else
             "Does not hold: no demonstrated value of player-set information."), "",
          "## Calibration of the full rival (model 4), deciles", "", "| Mean predicted | Observed |", "| --- | --- |"]
    L += [f"| {f(a, 3)} | {f(b, 3)} |" for a, b in r["calibration"]["4"]]
    (R / "sequence.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    for s, g in (("attack", attack), ("defence", defence), ("sequence", sequence)):
        if (R / f"{s}.json").exists():
            g()
