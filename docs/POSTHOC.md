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
