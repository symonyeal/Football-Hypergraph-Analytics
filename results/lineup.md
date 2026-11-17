# Lineup ratings (gated)

Data: StatsBomb open data, commit `4b73468` of `hudl/open-data`. Analysis is this repository's, not StatsBomb's.

![StatsBomb](https://raw.githubusercontent.com/hudl/open-data/4b73468fc5b0f1950f9f66fada70ad3a4f9327cb/img/SB%20-%20Icon%20Lockup%20-%20Colour%20positive.png)

A player's rating is the change in the team's open-play xG difference per 90 minutes with the player on the pitch, other players, manpower and score held fixed (ridge regression over stints of constant personnel). A player is rated only with at least 900 minutes and at least 270 team minutes without the player over 5 or more matches.

| Half | Stints | Players | Eligible | Penalty | Home advantage (xG/90) | Per extra player (xG/90) | Per goal of lead (xG/90) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| train | 8724 | 1924 | 596 | 10000 | 0.200 | 0.022 | -0.032 |
| test | 8707 | 1969 | 592 | 10000 | 0.307 | 0.049 | -0.025 |

**H6.** Players eligible in both halves: 283. Split-half Spearman 0.52 (0.42 to 0.61): holds.

**Withdrawn (review 3.5).** 87% of the variance of the ratings lies between teams, and cross-validation chose the largest penalty in both halves with error still falling. The split-half correlation measures the stability of team strength, so no ratings table is published.
