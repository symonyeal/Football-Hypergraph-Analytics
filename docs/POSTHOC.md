# Post hoc observations

Recorded after registered results were seen. Nothing here changes a registered test or verdict.

## P1. The bottleneck player `v*` is mostly a tie-break (10 November 2026)

The fractional transversal $x^*$ is not unique: the LP is degenerate. In the training half, the largest $x^*_v$ is shared
by two or more players in 66 of 80 teams (two players: 16 teams; five or more: 46 teams; one team ties 18 players).
HiGHS returns one optimal vertex, and the registered tie-break (largest $x^*_v$, then most on-ball actions) then picks
`v*`.

Consequences:

- H3's "top `x*` player" is often a solver-vertex choice rather than a property of the team. Defenders appear as `v*`
  (Godín, Atlético Madrid, $x^* = 1$; Medel, Inter Milan, one of six players at $2/3$). The H3 result (correlation
  −0.25, interval −0.56 to 0.10, 32 teams) is reported as registered, but its player selection is weak.
- `x*` share is not a usable player metric as defined. $\tau^*$, $\tau$, $\nu$ and $\operatorname{cov}(b)$ are
  unaffected: they are optimal values, unique by definition.

Candidate for a future registered round (not run): a player measure that is unique by construction, e.g. the drop in
$\operatorname{cov}(b)$ or in $\tau^*$ when the player's groups are removed.

## C1. Withdrawn: first H4 run (10 November 2026)

The first full sequence run (workflow run 42894182016) standardized sparse 0/1 indicators (`StandardScaler`, no
centring). A player seen in few possessions had its column multiplied by about $1/\sqrt{p}$, which defeats the L2
penalty. Every model with player indicators then scored worse than context alone on the test half (log loss 0.484
for model 1 against 0.352 for model 0) and model 4 was badly overconfident (top decile predicted 0.54, observed 0.20).
Its verdict ("does not hold", $\Delta_{54} = +0.0153$) is withdrawn.

Fix: `fha.seq.design` uses max-abs scaling, which leaves indicators at 0/1. `tests/test_seq.py` reproduces the defect
on synthetic noise indicators (old design: 0.5625 against 0.4668 for context alone; the test fails) and passes with the
fix. The registered models, grid, split and threshold are unchanged; H4 was rerun.

## P2. Lineup ratings repeat between halves, but the penalty sits at the grid edge and top players cluster by team

H6 holds as registered (split-half Spearman 0.52, interval 0.42 to 0.61, 283 players). Two observations limit what
the ratings mean:

- Cross-validation chose $\lambda = 10^4$, the largest value in the registered grid, in both halves. A larger penalty
  might fit better; the grid was not extended after the result.
- The fifteen highest-rated players are almost all from Paris Saint-Germain, Barcelona and Real Madrid. With few
  substitutions, heavy shrinkage spreads a team's xG difference across its regulars, so split-half stability can come
  from team strength rather than individual contribution.

Candidate for a future registered round (not run): the same test on ratings centred within each team.

## P3. Season to season, the attack shape does not clearly carry over (10 November 2026)

Descriptive, not registered. Pairs of consecutive seasons of the same team in the same competition (38 pairs:
Women's Super League, Barcelona in La Liga, Paris Saint-Germain in Ligue 1). Spearman correlation from one season to
the next, 95% bootstrap interval: top-two share 0.34 (−0.03 to 0.64), players needed to cover every chance −0.26
(−0.55 to 0.05), separate routes −0.31 (−0.61 to 0.01). None is distinguishable from zero. Within a season the
shape holds (H1, 80 teams); across seasons these few pairs do not show it.

## P4. Wyscout source: possession rebuild, xG transfer and provider agreement (10 November 2026)

- Wyscout has no possession ids. Possessions are rebuilt as runs of on-ball events by one team; a lone uncontrolled
  touch by the other team between two of the first team's events does not end a possession. On Serie A 2017/18 this
  gives 174 possessions a match and attacking groups of 1, 2, 3 players in 4.9%, 8.7%, 86.4% of chances, against
  StatsBomb 2015/16 Serie A's 0.9%, 19.5%, 79.6%. The providers differ; the rule is a reconstruction.
- Wyscout has no xG. A logistic model on distance, angle and header, fitted to 18,076 StatsBomb 2015/16 Premier
  League and La Liga open-play shots (1,804 goals; the fit predicts 1,802), predicts about 75% of Wyscout open-play
  goals in every competition (Premier League 698 against 914). A uniform scale leaves every share and player count
  unchanged; Wyscout xG per match is understated by about a quarter.
- The 2018 World Cup is in both sources. For the 8 teams measured in both, the rank agreement is 0.94 for players
  needed to cover every chance and 0.62 for the top-two share.
- One StatsBomb 360 file (match 3845506) does not parse at the pinned commit; the defence stage skips and lists it.
