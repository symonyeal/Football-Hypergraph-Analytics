# Confirmation protocol

Status: frozen

Frozen 17 November 2026 at tag `protocol-v1`, before any statistic was computed on the confirmation cohort. The
estimators are `fha/mu.py`, `fha/protocol.py` and `fha/run.py` (`structure`, `explore`, `confirm`) at commit
`9eb0cd4`; the verdicts are computed by `fha/report.py` (`verdicts`) at the same commit. Nothing here may change
after the confirmation run; anything noticed afterwards goes in `docs/POSTHOC.md`.

## Question

Does the group structure of chance creation carry information about a team that is (a) reproducible, (b) absent
from first-order involvement and from the pairwise pass network, and (c) related to an outcome outside the structure
itself? (`REVIEW.md` 4.1.)

## Cohort

| Item | Value |
| --- | --- |
| Data | Wyscout public data set (Pappalardo et al. 2019, figshare files 14464685, 14464622, 15073721, 15073697), CC BY 4.0 |
| Teams | Every team of the 2017/18 Premier League, La Liga, Bundesliga, Serie A and Ligue 1 with chances in both halves (98 expected) |
| Halves | First: gameweeks up to half the league's last gameweek; second: the rest |
| Chances | Possessions rebuilt by `wy.possessions` that contain a Shot event; group = last three distinct actors up to the first shot |
| xG | Logistic model on distance, angle and header fitted to StatsBomb 2015/16 Premier League and La Liga open-play shots (`xg_model`) |
| Roles | Wyscout player role: GK, DF, MD, FW. Exploration used nine StatsBomb roles; role-level results are not compared numerically between cohorts |
| Passes | A completed pass's recipient is the player of the next event of the same possession, when a teammate |
| Run | Once, by the `sharded` workflow with stage `confirm` (16 structure parts and one explore part), seed 0 |

The rebuild was checked against StatsBomb on the 8 teams of the 2018 World Cup present in both (audit D11): rank
agreement 0.95 for $D_1$ and 0.62 for $c(2)$, Wyscout $c(2)$ higher by 0.046 on average. Player-level results
therefore carry the rebuild as a stated limitation.

## Verdicts

Each result is reported with its estimate and 95% interval and one verdict. With margin $m$: **supported** when the
interval lies above 0; **reversed** when below 0; **equivalent to none** when it lies within $(-m, m)$;
**undetermined** otherwise. A supported or reversed interval inside $(-m, m)$ is marked "below the margin". Each
hypothesis has one primary quantity; secondary quantities are reported and, where stated, Holm-corrected.

## Hypotheses

**R1. Reliability.** ICC(2,1) between the two halves across teams, percentile bootstrap over teams (2,000 resamples).
Primary: player-level $D_1$, $c(2)$, $\tau_{0.9}$, each its own verdict. Secondary: the same at role level, and the
excess of $c(2)$ and $\tau_{0.9}$ over N0. Margin 0.2. Power at 98 teams to find the lower bound above 0: 0.87 at a
true ICC of 0.3, 0.99 at 0.4 (simulation, `protocol.icc_power`). Exploration: 0.34, 0.47, 0.31, all supported.

**R2. Structure beyond the pairwise model.** Excess of a full-season statistic over a null (observed minus the mean of
20 draws), pooled across teams by a DerSimonian–Laird random-effects mean, variance per team = match-resampling
variance (50 resamples) plus null-draw variance of the mean. Primary: player-level $c(2)$ over N2. Margin 0.02 (two
points of xG share). Secondary: $c(2)$, $c(3)$, $\tau_{0.9}$, $o(2)$ over N0, N1, N2 at player and role level; within
each level and null the four are Holm-corrected, and a supported or reversed verdict needs Holm p < 0.05. Exploration:
+0.025 ± 0.004, supported; smallest pooled effect detectable with 80% power at 98 teams about 0.010.

**R3. Selection at small budgets.** Second-half coverage of $b$ players chosen on the first half, exact $c(b)$
maximiser minus each rival (involvement $d$, Shapley $\varphi$, pass-network strength), mean over teams, bootstrap
interval. Primary: $b = 2$ against involvement. Margin 0.02. Exploration: −0.001 (−0.020 to 0.018), equivalent to none.

**R4. Absence.** Second-half matches: log E[open-play xG] = team + opponent + home − β a − δ C a, with a the summed
first-half $\varphi$ of squad players absent from the match and C the first-half $c(2)$; quasi-Poisson, teams
bootstrapped (500). Descriptive only, no verdict: simulated power at 80 teams was 0.20 at β = 1 and 0.44 at β = 2.

**R5. Outcome.** Leave-one-out $R^2$ of second-half xG per match (primary) and points per match (secondary) from
first-half xG per match, with and without first-half $D_1$ and $c(2)$; increment with a bootstrap interval over
teams. Margin 0.05. Exploration: −0.016 (−0.023 to 0.025) for xG, equivalent to none.

## Reading of the answer

The answer to the question is read from the primary verdicts only. (a) is yes if R1's primaries are supported. (b) is
yes if R2's primary is supported and not below the margin, and no if it is equivalent to none or below the margin; R3
says whether that structure matters for choosing players and does not change (b). (c) is yes if R5's primary is
supported and no if it is equivalent to none. Any other result is reported as undetermined.
