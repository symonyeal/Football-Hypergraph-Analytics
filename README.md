# Football Hypergraph Analytics

**Interactive site: https://symonyeal.github.io/Football-Hypergraph-Analytics/**

Does the group structure of chance creation carry information about a team that is reproducible, absent from how
often each player is involved, and related to an outcome outside the structure itself? This project asks that question
of 403 team-seasons from two public data sets: StatsBomb open data (complete 2015/16 Premier League, La Liga, Serie A
and Ligue 1; four Women's Super League seasons and other women's leagues; World Cups, Euros, Copa América 2024, AFCON
2023; Barcelona's La Liga matches 2004/05 to 2020/21; 360 freeze frames for eleven competitions) and the Wyscout public
data set (complete 2017/18 Premier League, La Liga, Bundesliga, Serie A and Ligue 1, the 2018 World Cup and Euro 2016).

**Answer.** Confirmed on the 98 teams of the Wyscout 2017/18 leagues, under a protocol frozen and tagged before
that data was opened ([protocol](docs/PROTOCOL.md), [results](results/confirm.md)):

- **Reproducible, weakly.** How concentrated a team's chance creation is repeats between half-seasons: reliability
  0.38 for the effective number of creators, 0.33 for the share two players touch, 0.29 for the players needed to
  touch 90% of the danger. All three intervals lie above zero.
- **Beyond involvement and the pass network, but by little.** Chances are more concentrated than a model that keeps
  only how often each pair of players shares a chance: by 1.7 points of xG share (interval 1.0 to 2.5), under the
  2 points the protocol set as the smallest effect of interest. Team by team, the part beyond each player's
  involvement count does not repeat between halves.
- **Not related to results.** Adding these measures to a team's first-half xG does not improve the prediction of its
  second-half xG or points (equivalent to no improvement within the protocol's margin).

In practice, ranking players by how many chances they are involved in picks the key players as well as the exact
set-cover optimum; ranking by passes made and received does much worse. Whether missing key players costs xG could
not be resolved with this data. The StatsBomb 2015/16 leagues used to build the tests gave the same answers, with a
larger excess over the pairwise model (2.5 points).

How the project got here: a first round of tests ([registered hypotheses](docs/HYPOTHESES.md), [post hoc
notes](docs/POSTHOC.md)) was reviewed on 16 November 2026 ([design review](docs/REVIEW.md); `python -m fha.audit`
reproduces its numbers). The review found that the first round's measures rose with the number of chances observed
and were largely reproduced by involvement counts, and set out the measures, null models and protocol used for the
answer above. One deviation from the protocol is recorded (post hoc note P6).

## What a chance is

A chance is any possession that ends in an open-play shot, and the people behind it are the last three players
involved before the shot. A team's half-season of chances is then a list of small groups of players, each with the
expected goals (xG) it produced. The first round summarised that list by three numbers:

- **Fewest players touching every chance** ($\tau$). Most teams need nine or ten in a half-season; Barcelona needed
  seven. The count rises with the number of chances observed (mean 5.3 at 25 chances, 8.6 at 130), so it compares
  teams only over equal numbers of chances or within one competition.
- **Chances sharing no player** ($\nu$). The largest number of chances with no player in common. It is within one of
  $\tau$ in 360 of 403 team-seasons, so the two are close to one measurement.
- **Share of danger two players touch** ($\operatorname{cov}(2)$). Barcelona's Neymar and Suárez were involved in
  87% of the team's open-play xG in the first half of 2015/16; the typical team's best pair touches about 70%.

Each counts involvement in chances that happened. None measures how much danger would be removed if those players
were marked or missing: a marked team re-routes.

## What was found

Registered tests on the 80 teams of the 2015/16 leagues, first half of the season against the second, with the
review's qualifications (exploratory, computed on the same teams).

**The three numbers repeat between half-seasons, but mostly through involvement counts.** Each correlates 0.42 to
0.48 between halves (every 95% interval above zero). Re-dealing each team's chances among its players, keeping how
many chances each player was in, reproduces most of this: that baseline repeats at 0.55, and the part of $\tau$ beyond
it repeats at 0.13 (interval −0.10 to 0.33).

**The players behind a team's chances can be picked out from the first half, but simple counting does as well.**
The fewest players who touched every first-half chance cover 94% of second-half danger. The same number of players
ranked by how many chances they were involved in cover 95%; ranked by touches, 89%.

**Teams with fewer chances sharing no player did not clearly lose more when their key player was missing.** Correlation
−0.25, interval −0.56 to 0.10, 32 teams. With 32 teams the test could detect only a correlation near 0.5, and the
"key player" is often one of several tied players.

**Season-to-season comparisons cannot be read.** Of 38 pairs of consecutive seasons, 16 are Barcelona and 21 the
Women's Super League, with seasons of 7 to 38 matches; the correlations (−0.31 to 0.34) are not interpretable.

**The two data providers agree mainly on how many matches a team played.** Eight teams at the 2018 World Cup are in
both sources. Their $\tau$ agrees at 0.94, but each provider's $\tau$ also tracks matches played (0.80 and 0.83).
Agreement on the top-two share is 0.62.

## Appendix: defence, sequence and lineup studies

These studies do not address the question above and are kept as registered, with their limits.

- **Who is on the ball (sequence, H4).** Adding the players involved to a model of 214,000 possessions did not improve
  predictions of a shot. The same test also gains nothing from player indicators, which identify the team, so it had
  no demonstrated sensitivity and supports no conclusion about players.
- **Gaps in a defence (H5).** For 60,000 passes from 360 frames, ball position carries most of the information. Gaps
  and holes in the block improve test log loss by 0.0005, 0.8% of the gain from ball position, against a baseline
  linear in location. The topological summary added nothing, but that test could not have found otherwise.
- **Lineup ratings (H6).** Ratings of 283 regulars repeat between halves (0.52), but 87% of their variance lies between
  teams and the fitted penalty sat at the edge of its grid. They measure team strength; the table is withdrawn.

## Data and terms

StatsBomb open data, `hudl/open-data` commit `4b73468`, streamed by a GitHub workflow and never stored or
redistributed here, as the StatsBomb Public Data User Agreement requires. Wyscout public data set: Pappalardo et al.,
"A public data set of spatio-temporal match events in soccer competitions", *Scientific Data* 6, 236 (2019), figshare,
CC BY 4.0. Wyscout has no possession ids or xG: possessions are rebuilt and shots are weighted by an xG model fitted on
StatsBomb shots, which predicts about 75% of Wyscout's goals ([post hoc notes](docs/POSTHOC.md), P4). Only aggregate
results are committed.

![StatsBomb](https://raw.githubusercontent.com/hudl/open-data/4b73468fc5b0f1950f9f66fada70ad3a4f9327cb/img/SB%20-%20Icon%20Lockup%20-%20Colour%20positive.png)

## Project map

| Path | Holds |
| --- | --- |
| `site/` | The interactive site; `site/data.js` is generated by `python -m fha.site` |
| `results/` | Registered results as JSON and readable pages: [attack](results/attack.md), [defence](results/defence.md), [sequence](results/sequence.md), [lineup](results/lineup.md) |
| `fha/sb.py` | StatsBomb events to attacking groups, sequence cutoffs and lineup stints |
| `fha/wy.py` | Wyscout events to rebuilt possessions, attacking groups and shot features |
| `fha/mu.py` | Functionals of the chance measure, null models N0 to N2, match resampling, reliability (review section 4) |
| `fha/protocol.py` | Second-round estimators and power simulations: selection rules (R3), absence model (R4), incremental prediction (R5), ICC power (R1) |
| `fha/attack.py` | Fewest-players, separate-routes and coverage measures (LP and ILP by HiGHS, minimum transversals by the Rust `tr`) |
| `fha/defence.py` | Gap, hole, persistence and shape of the defenders |
| `fha/seq.py` | Sequence features and the design matrix |
| `fha/run.py`, `fha/report.py`, `fha/site.py` | Registered tests, results pages, site data |
| `src/main.rs` | `tr`: minimal transversals by MMCS (`mcs` crate) |
| `docs/MODEL.md` | Notation, measures and checks |
| `docs/BACKGROUND.md` | Prior work: what it measures, the baseline it supplies, how far each source was read |
| `docs/REVIEW.md`, `fha/audit.py` | Design review and improvement plan; the audit of the committed results it rests on |

```text
cargo build --release && pip install -r requirements.txt && python -m pytest -q
python -m fha.run attack      # or defence, sequence, lineup, seasons, wyscout, structure, explore; run in full by the "derive" workflow
python -m fha.report && python -m fha.site
```

Licence: MIT. StatsBomb data remains subject to the StatsBomb Public Data User Agreement.
