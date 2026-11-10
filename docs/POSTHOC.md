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
