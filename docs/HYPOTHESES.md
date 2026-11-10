# Registered hypotheses

Frozen 10 November 2026, before any metric was computed on real matches. Anything added after a result is seen goes
in `docs/POSTHOC.md`, never here. Notation follows `docs/MODEL.md`.

## Data

| Item | Value |
| --- | --- |
| Source | StatsBomb open data, `hudl/open-data` commit `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb` (7 September 2026) |
| Event cohort | 2015/16 Premier League (2/27), La Liga (11/27), Serie A (12/27), Ligue 1 (7/27): 1,517 matches, 80 team-seasons |
| Split | Training: match weeks 1–19. Test: match weeks 20–38 |
| Defence cohort | 360 frames. Training: UEFA Euro 2020 (55/43) and FIFA World Cup 2022 (43/106), 115 matches. Test: UEFA Euro 2024 (55/282), 51 matches |
| Terms | StatsBomb Public Data User Agreement (8 September 2023): no redistribution of the data (1.2.1); analysis may be published with the StatsBomb logo (1.4). The repository holds code and aggregate results only. |
| Units | StatsBomb pitch 120 × 80 units, converted to metres on a 105 × 68 m pitch (x · 105/120, y · 68/80) |

## Definitions

| Symbol | Definition |
| --- | --- |
| Possession $e$ | StatsBomb `possession` id within a match; its team is `possession_team` |
| On-ball action | Pass, Carry, Dribble or Shot by a player of the possession team |
| $P(e)$ | Actors of on-ball actions and recipients of passes in $e$ |
| $A_3(e)$ | The last 3 distinct players, in order of last involvement, among the actors and recipients of $e$ up to and including the shooter |
| $\mathcal F$ | $\{A_3(e)\}$ over possessions ending in an open-play shot (shot type Open Play), one entry per shot possession, weight $w$ = summed StatsBomb xG of its open-play shots. Sensitivity: possessions whose xG is at least 0.1 |
| Window | One team, one half-season (training or test) |
| $\operatorname{cov}(b)$ | Largest share of $\mathcal F$'s xG involving at least one of $b$ players, exact by ILP; primary $b = 2$, reported for $b = 1,\dots,5$ |

## H1. Attack concentration and redundancy are team properties

- **Metrics.** $\tau$, $\tau^*$, $\nu$, $\operatorname{cov}(2)$ per team window.
- **Test.** Spearman correlation of each metric between the training and test windows across the 80 team-seasons, with a
  95% bootstrap interval over teams (2,000 resamples, seed 0).
- **Holds** if the interval lies above 0. **Rival** (noise) holds if it contains 0.

## H2. Transversal sets beat usage on held-out attacks

- **Sets.** $T_\tau$: the minimum transversal of training $\mathcal F$, ties broken by larger training $\tau^*$ weight,
  then smaller player id. $C_b$: the exact $\operatorname{cov}(b)$ maximiser on training $\mathcal F$, $b = \lvert T_\tau\rvert$.
  $U_b$: the $b$ players with most on-ball actions in training.
- **Test.** Held-out weighted coverage of $T_\tau$ and $C_b$ against $U_b$; paired mean difference across teams with a
  bootstrap interval.
- **Holds** if the interval for $C_b - U_b$ lies above 0. **Rival:** usage selects the same coverage.

## H3. Low redundancy means larger losses when the main player is missing (mechanism)

- **Player.** $v^*$: the largest training $x^*_v$ (optimal fractional transversal), ties by on-ball actions.
- **Outcome.** For each test match, team open-play xG divided by the opponent's training mean open-play xG conceded per
  match. Drop $= 1 - \bar a_{\text{absent}}/\bar a_{\text{started}}$, where absent means $v^*$ did not appear and started
  means $v^*$ was in the starting XI.
- **Eligible teams.** At least 3 test matches in each condition.
- **Test.** Spearman correlation between training $\nu$ and the drop, bootstrap over eligible teams.
- **Holds** if the interval lies below 0. Also reported: the same correlation with training $\operatorname{cov}(2)$
  (expected above 0), and with $v^*$ replaced by the top-usage player.
- Observational: rotation, injury and suspension are not random.

## H4. Who is involved predicts danger beyond what happens and where

- **Unit.** Possessions alive at the cutoff $c$ (the completion of the third on-ball action that is not a shot), with no
  shot, possession change or stoppage at or before $c$. Label: an open-play shot later in the same possession.
- **Models** (L2 logistic regression, the penalty tuned by 5-fold grouped cross-validation over training matches):
  - 0: context (start zone 6 × 4 grid, play pattern, score difference clipped to ±2, 15-minute bin, home).
  - 1: 0 plus player indicators for $P_c(e)$ and ordered passer→receiver pairs.
  - 2: 0 plus VAEP action features of the first three actions (socceraction).
  - 3: 1 plus the counts of 3-node pass-motif types among the first three actions.
  - 4: the union of 2 and 3.
  - 5: 4 plus indicators of the unordered player set $P_c(e)$ (sets seen at least 5 times in training; otherwise none).
- **Test.** $\Delta = \bar\ell_5 - \bar\ell_4$ on test matches, with a match-bootstrap interval.
- **Holds** if $-\Delta \ge 0.005\,\bar\ell_4$ and the interval lies below 0. Otherwise the result is "no demonstrated value
  of player-set information".

## H5. Defensive gaps and holes predict box entries; topology adds nothing

- **Unit.** Open-play passes by the attacking team starting in the opponent half, outside the penalty area, with a 360
  frame showing at least 6 outfield defenders.
- **Label.** An event of the attacking team located in the penalty area within 10 s of the pass, in the same possession.
- **Features.** Base: pass start $(x, y)$, distance to goal. Shape: width, depth, convex-hull area of visible outfield
  defenders. `gap`: longest minimum-spanning-tree edge. `hole`: largest circumradius among Delaunay triangles whose
  circumcentre lies in the hull. `h1`: longest $H_1$ bar of the alpha filtration, in metres.
- **Models.** Logistic: base; base + shape; base + shape + gap + hole; base + shape + gap + hole + h1.
- **Holds (H5a)** if gap and hole reduce test log loss relative to base + shape, with a match-bootstrap interval below 0.
  **H5b** (topology adds nothing beyond gap and hole) holds if the interval for adding h1 contains 0.
- Also reported: the share of passes ending inside the hole circle, box-entry passes against all passes.

## H6. Lineup ratings (gated)

- A player is rated only with at least 900 minutes played and at least 270 team minutes without the player over at
  least 5 matches. A pair is rated only with at least 450 minutes together and at least 270 minutes for each player
  without the other.
- RAPM ($\lambda$ by grouped cross-validation) on xG difference per 90; split-half Spearman of ratings for eligible
  players. Holds if the bootstrap interval lies above 0; otherwise no ratings are published.
