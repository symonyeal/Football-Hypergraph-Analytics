# Design review and improvement plan

16 November 2026. Scope: every document, every source file (`fha/`, `src/main.rs`, `site/`, `tests/`, workflows) and
every committed result at `7adde3b`. Section 2 reports an audit run on the committed aggregates
(`python -m fha.audit`, seed 0); it reopens no raw data. All audit results are post hoc, computed on the 80 team-seasons
the registered tests already used, and carry that status. This review was not independently checked.

## 1. Verdict

The engineering is sound: exact solvers with certificates, a pinned data commit, registered and post hoc results kept
apart, a withdrawn run documented. The research design is not. Four defects decide the matter.

1. **The headline measures are not properties of the attack.** $\tau$ and $\nu$ are unweighted, worst-case invariants
   of a set family. They grow with the number of chances observed, they are fixed mostly by how many players appear,
   and the part of $\tau$ not explained by players' involvement counts does not repeat between half-seasons
   (0.13, interval −0.10 to 0.33). The registered stability result (H1) is carried by first-order counts.
2. **No test asks whether the hypergraph is needed.** Every measure is compared with zero or with a weak baseline,
   never with the degree sequence or the pass network. Against the natural baseline, the players most often involved in
   chances, the transversal set of H2 loses its advantage (0.944 against 0.951 held-out coverage).
3. **Null results are read as evidence of absence.** H4 ("who is on the ball adds nothing") and H5b ("topology adds
   nothing") use instruments with no demonstrated sensitivity and no equivalence bound. H3 could only have detected a
   correlation near 0.5.
4. **The project is three unrelated studies.** Set covers of attacking groups, point-set geometry of defenders and
   plus-minus ratings share a title and no question, model or literature. Only the first uses a hypergraph. The source
   list has four entries and none from the football network literature.

The data cannot be enlarged, so the remedy is a narrower question, measures that are functionals of a weighted
distribution, null models, baselines, and a confirmation cohort that has not been tested yet. Sections 3 and 4 give
the defects and the revised design; section 5 the plan; section 6 the statements to correct now.

## 2. Audit results

| Check | Result | Bears on |
| --- | --- | --- |
| D1 Exposure | Across the 403 team-seasons, Spearman of $\tau$ with matches played 0.79, with chances $m$ 0.68, with players appearing in any group 0.79; $\nu$ with matches 0.82. Among the 210 team-seasons of 30 or more matches, $\tau$ with players appearing 0.48, with $m$ −0.16 | Cross-competition comparisons, the site's rankings |
| D1 Redundancy of measures | $\tau - \nu$ is 0 in 183 team-seasons, 1 in 177, 2 or more in 43 | "Three numbers" |
| D2 Provider agreement | 2018 World Cup, 8 teams: $\tau$ agrees at 0.94 between providers, and each provider's $\tau$ correlates 0.80 and 0.83 with matches played (5 or 7) | README finding 5 |
| D3 H2 baselines | Held-out xG coverage with $b = \tau$ players chosen on the first half: transversal 0.944, exact cover 0.938, greedy cover 0.942, top $b$ by Shapley xG share 0.947, top $b$ by chances involved in 0.951, top $b$ by on-ball actions 0.885. Transversal minus chance count: −0.007 (−0.019 to 0.003) | README finding 2 |
| D4 Split-half reliability | $\tau$ 0.42, $\nu$ 0.42, $\operatorname{cov}(2)$ 0.43; players appearing 0.32; Hill numbers of the Shapley shares 0.32 and 0.31; $\tau_{0.9}$ 0.35; largest share 0.37; chances 0.67; xG 0.68 | H1; choice of replacement measures |
| D5 Degree-preserving null | Re-dealing group memberships with every player's number of chances and every group size fixed (20 draws a team): null mean of $\tau$ 9.97 against 9.41 observed; Spearman of observed with null mean 0.79 across teams; observed minus null is −1 or 0 in 60 of 80 teams. Split-half reliability of the null mean 0.55; of the excess (observed minus null) 0.13 (−0.10 to 0.33) | H1, the case for a hypergraph |
| D6 Rarefaction | Mean $\tau$ over the 80 first halves at 25, 50, 100, 130 chances drawn without replacement: 5.28, 6.69, 8.05, 8.59; at the full 130 to 336 chances: 9.41 | Comparability of $\tau$ |
| D7 Season pairs | Of 38 consecutive-season pairs, 21 are Women's Super League, 16 Barcelona, 1 Paris Saint-Germain; seasons in the pairs hold 7 to 38 matches | README finding 4 |
| D8 Lineup ratings | 87% of the variance of the 283 published ratings lies between teams ($\eta^2 = 0.87$, 78 teams). Cross-validated error falls monotonically to the largest penalty in both halves (train 9.54, 5.78, 5.09, 5.05) | H6 |
| D9 Effect sizes | Defence, test log loss: no information 0.5270, ball position 0.4607, plus shape 0.4591, plus gap and hole 0.4586. Sequence: no information 0.3617, context 0.3517, VAEP 0.3357, VAEP plus players 0.3371 | H4, H5 |

## 3. Defects

### 3.1 Framing

**The object is never defined as a mathematical object with a sampling model.** $\mathcal F$ is a multiset of subsets
of $V$ of size at most 3 with weights; it is a sample of $m$ chances from a team's chance-generating process, and $m$
varies from 15 to several hundred. Nothing states which quantities are parameters of the process and which are
statistics of the sample. $\tau$, $\tau^*$ and $\nu$ are monotone under inclusion of families,

$$\mathcal F \subseteq \mathcal F' \implies \tau(\mathcal F) \le \tau(\mathcal F'),\quad \nu(\mathcal F) \le \nu(\mathcal F'),\quad \tau^*(\mathcal F) \le \tau^*(\mathcal F'),$$

so each increases with exposure and has no finite limit short of the squad. D6 shows $\tau$ still rising at 130
chances. They behave as species richness does in ecology: a count that measures sampling effort unless rarefied. The
README sentence "most teams need nine or ten; Barcelona needed seven" compares half-seasons of equal length and is
defensible; the site's ranking of 403 team-seasons from 5 to 38 matches is not.

**The interpretations are counterfactual and the measures are accounting.** "Stopping all of them would take at least
that many players" and the site's marking tool read $\operatorname{cov}(S)$ as the danger removed when $S$ is marked.
$\operatorname{cov}(S)$ is the share of realised chances in which a member of $S$ took part. A marked team re-routes;
no possession is deleted. A removal claim needs absence data or a behavioural model, and H3, the only test of it, is
unresolved. "Separate routes" for $\nu$ is likewise a name, not a finding: pairwise disjoint chances are not routes in
any spatial or tactical sense.

**The hyperedge is an untested convention.** $A_3$ takes the last three distinct players, counting pass recipients.
The size cap fixes the scale of every measure ($\nu \le \tau \le 3\nu$ for groups of size at most 3; D1 shows the two
within 1 of each other in 360 of 403 cases, so they are one measurement). No sensitivity to $k \in \{2, 3, 4, \text{all}\}$,
to excluding the shooter, or to weighting by xG was registered beyond the single threshold $q = 0.1$, under which the
reliability of $\nu$ falls to 0.27.

**No prior work is engaged.** Pass networks, centralisation and flow centrality, pass motifs, expected threat,
possession value and pitch control each address a question this project asks (section 7). Without them the reader
cannot tell what is new, and the baselines that literature supplies are missing from every test.

### 3.2 Attack study (H1 to H3)

**$\tau$ and $\nu$ have breakdown point zero.** They ignore xG. One chance of 0.02 xG among three fringe players
raises $\tau$ by one; ten chances of 0.5 xG through the same pair leave it unchanged. A statistic of an attack that
weights a deflected 30-metre shot as it weights a tap-in is not measuring danger.

**H1 does not show an attacking shape.** D5: 62% of the between-team rank variance of $\tau$ is reproduced by a null
that keeps only each player's number of chances and the group sizes ($0.79^2$). The null mean is itself reliable
between halves (0.55); the excess over it is not (0.13). What repeats is how many players a team uses and how evenly;
D4 shows the number of players appearing has reliability 0.32 and correlates 0.44 with $\tau$ in the same half. The
registered conclusion "holds" is correct as registered and its reading as higher-order structure is unsupported.

**Reliability is low for every composition summary.** At 0.42, more than half the variance of a half-season value is
noise; by Spearman–Brown a full season would reach about 0.59. D4 shows the weighted alternatives (Hill numbers,
$\tau_{0.9}$) are no better at 0.31 to 0.37, while volume (chances, xG) reaches 0.68. The constraint is 130 to 336
chances per window, not the choice of functional. Any correlation with an outcome is attenuated by the square root of
the reliability, which H3 ignores.

**H2's baseline is a strawman.** On-ball actions rank centre-backs and holding midfielders first; they are not a
candidate for "players behind the chances". D3: ranking players by the number of chances they were involved in covers
0.951 of held-out xG, the transversal 0.944. With $b \approx 9$ or 10 of the regular eleven, any sensible rule covers
about 94%. The comparison should be made at small $b$, where rules can differ, and against degree.

**The exact solvers answer questions that need no exact answer.** $\operatorname{cov}(S)$ is monotone submodular, so
greedy selection is within $1 - 1/e$ of optimal in the worst case and, here, indistinguishable out of sample (0.942
against 0.938). Enumerating all minimum transversals by MMCS in Rust serves only the tie-break of $T_\tau$. The
dependency is justified if minimal transversals are themselves the object of study; at present they are not.

**H3 cannot answer its question.** With 32 teams, 80% power requires a true correlation of about 0.48. The outcome is
a ratio of two means over as few as 3 matches each. The player is the solver's choice among tied optima in 66 of 80
teams (POSTHOC P1). The predictor has reliability 0.42. Selection into absence is not modelled. The same data support
a far stronger design (section 4, R4).

**The season-to-season view is not interpretable.** D7: 16 of 38 pairs are one club, serially dependent, drawn from
seasons of 7 to 38 matches, on a measure that grows with matches. The bootstrap treats the pairs as independent.

**The provider agreement is exposure.** D2: both providers' $\tau$ track whether a team played 5 or 7 matches.
Agreement on the top-two share, 0.62, is the informative figure and it is modest.

### 3.3 Sequence study (H4)

**The instrument has no demonstrated sensitivity.** Model 1 adds player indicators, which identify the team, to
context, and gains nothing (−0.00017, interval containing 0), although teams differ by a factor of 2.6 in chances per
half-season. Adding the player blocks to VAEP makes the fit significantly worse (+0.00144, interval 0.00103 to
0.00182). One L2 penalty is shared by blocks of very different sparsity, so the penalty that suits 4,327 set
indicators with a handful of observations each shrinks them to zero. The outcome "no demonstrated value" was close to
certain before any data were read. A registered threshold does not repair this: no positive control, no planted-effect
power calculation, no equivalence bound.

**The estimand is not the one of interest.** A group effect on the probability of a shot, after three actions,
conditional on action features that already encode where skilled players take the ball, is a narrow quantity.
Conditioning on VAEP features blocks the path by which players matter. "Who is on the ball adds nothing to predicting
a shot" in the README is stronger than the test.

### 3.4 Defence study (H5)

**The baseline is too weak to attribute increments.** Ball position enters as a linear logit in $x$, $y$ and distance;
$y$ linear is not symmetric about the pitch axis. Shape, gap and hole may be recovering nonlinearity in location. The
increments are 0.0017 and 0.0005 in log loss against 0.066 for position: 2.6% and 0.8% of it. "Holds" is true and of
no practical size; the site's headline is accurate, the README's "measurable" needs the magnitude.

**The features ignore the ball and the camera.** `gap` and `hole` are computed over all visible defenders wherever
the ball is. A hole 40 m from the ball is irrelevant to the next 10 s. The 360 frame shows only players in the
broadcast view; with a floor of 6 defenders, the measures partly record which defenders are in shot. StatsBomb
supplies the visible-area polygon; it is unused.

**H5b was constructed to succeed.** The alpha complex is a subcomplex of the Delaunay triangulation, so on 6 to 10
points the longest $H_1$ bar is nearly a function of the circumradii already in `hole`, as MODEL.md states. Registering
"topology adds nothing" with success defined as an interval containing zero tests nothing. A null claim needs an
equivalence margin; a fair test of topology needs a setting where it could add something (full tracking data, more
points, persistence of sublevel sets of a pitch-control surface).

### 3.5 Lineup study (H6)

**The ratings are team strength.** D8: 87% of rating variance is between teams. The penalty sits at the edge of the
grid in both halves with error still falling, so the fit is asking for more shrinkage, toward a model with no player
effects. The nuisance covariates share the penalty: an extra player on the pitch is estimated at 0.02 to 0.05 xG per
90 minutes, an implausibly small value for a red card. Split-half 0.52 therefore measures the stability of team
strength (xG itself: 0.68). The gate "publish if the interval is above zero" let through a table that POSTHOC P2
already disowns. The study cites hypergraph adjusted plus-minus and implements ordinary ridge plus-minus.

### 3.6 Inference and protocol

- **Registration cannot be verified from the history.** The commit that adds `HYPOTHESES.md` also adds all the
  measurement code and is dated 20:12 UTC on 10 November; the first results commit is dated 20:15 UTC, and the whole
  repository, six stages and the site, was committed by 23:02 UTC. A registration is credible when the protocol is
  committed alone, tagged, before code touches the cohort.
- **The confirmation cohort is spent.** Every further test on the 2015/16 leagues, including section 2, is
  exploratory.
- **Verdict rule.** "Holds if the 95% interval excludes zero" equates detectability with importance. H5a passes with
  an effect under 1% of the baseline's; four metrics are tested in H1 without a stated family.
- **Units of resampling.** Teams are resampled as independent, though opponents are shared; season pairs from one
  club are resampled as independent. Within-team sampling error (resampling matches) is never estimated, so no
  metric has a standard error.
- **Reproducibility.** `requirements.txt` is unpinned; socceraction is installed in the workflow only; solver
  versions are not recorded in the results. MODEL.md defers to a `RESEARCH.md` that is not in the repository.

## 4. Revised design

### 4.1 Question

One question, which the title promises and the current tests do not ask:

> Does the group structure of chance creation carry information about a team that is (a) reproducible, (b) absent
> from first-order involvement and from the pairwise pass network, and (c) related to an outcome outside the
> structure itself?

On present evidence: (a) weakly, (b) no, (c) untested. A clear negative answer, properly powered, is a publishable
result. The defence and lineup studies do not serve this question; section 5 moves them out.

### 4.2 Objects

Let $V$ be the vertices and $\mu$ the chance measure: a probability measure on nonempty subsets of $V$, with
$\mu(A)$ the share of the team's open-play xG created by possessions whose group is $A$. A window gives an empirical
$\hat\mu$ from $m$ chances. Every reported quantity is a functional of $\mu$, estimated from $\hat\mu$ with a
standard error from resampling matches.

| Symbol | Definition | Property |
| --- | --- | --- |
| $d_v$ | $\mu\{A : v \in A\}$ | Involvement share; first-order |
| $\varphi_v$ | $\sum_{A \ni v} \mu(A)/\lvert A\rvert$ | Shapley value of the coverage game $c$; sums to 1; linear in $\mu$, hence unique and stable |
| $c(S)$ | $\mu\{A : A \cap S \ne \emptyset\}$ | Monotone, submodular; $c(S) \le \sum_{v \in S} d_v$ |
| $c(b)$ | $\max_{\lvert S\rvert = b} c(S)$ | Concentration curve; the current $\operatorname{cov}(b)$ |
| $\tau_\alpha$ | $\min\{b : c(b) \ge \alpha\}$ | Partial transversal number; $\tau_1$ on the support is the current $\tau$. Insensitive to any mass below $1 - \alpha$ |
| $D_q$ | $\big(\sum_v \varphi_v^q\big)^{1/(1-q)}$, $D_1 = \exp(-\sum \varphi_v \log \varphi_v)$ | Effective number of creators (Hill number); $q = 0$ is richness and exposure-dependent, $q \ge 1$ is not |
| $o(S)$ | $1 - c(S)/\sum_{v \in S} d_v$ | Overlap among $S$: how far their involvement is in the same chances |

Two facts replace current content. First, $\varphi$ is the unique-by-construction player measure POSTHOC P1 asks for.
Each indicator game $S \mapsto [A \cap S \ne \emptyset]$ is symmetric in the members of $A$ and null outside it, so
by symmetry, the null-player axiom, efficiency and linearity each member receives $\mu(A)/\lvert A\rvert$. It is the
equal-split chance credit already used in practice under other names; the LP vertex $x^*$ is retired. Second, $d$,
$\varphi$, $D_q$ are first-order: they depend on $\mu$ only through its one-player marginals. Only $c$, $\tau_\alpha$
and $o$ see which players share chances. Reporting the two classes separately is the point of the redesign.

**Vertices.** Player identity gives 130 to 336 chances over about 20 vertices per window, too few for any
higher-order estimate (D4). A second vertex set, positional roles (StatsBomb position at the time of the action,
merged to about ten roles), makes hypergraphs comparable across teams and seasons and allows pooling. Player-level
results stay descriptive; inference is at role level or on full seasons.

**Edges.** $A_k$ for $k \in \{2, 3, 4\}$ and the whole possession, with and without the shooter, declared in advance
as a sensitivity family with $k = 3$ primary.

**Exposure.** Every count-like statistic is reported at a common number of chances by rarefaction (mean over
subsamples of fixed $m$) with its rarefaction curve, or replaced by a functional of $\mu$ that has a limit.

### 4.3 Null models

| Null | Preserves | Answers |
| --- | --- | --- |
| N0 degree and size | Each player's number of chances; each group's size (stub re-dealing, as in the hypergraph configuration model) | Is the statistic more than involvement counts? |
| N1 role-stratified | N0 within role classes (attackers re-dealt among attackers) | Is it more than counts plus position? |
| N2 pairwise | Pairwise co-involvement counts, by sampling triples from a fitted model with no three-way interaction | Is the triple structure more than the pass network? |

Each structural statistic is reported as observed, null mean, and standardised excess. N2 is the test that justifies
the word hypergraph: under it a team's chance structure is determined by its weighted graph.

### 4.4 Hypotheses for a second round

Each names its baseline, its rival and a decision rule with a smallest effect of interest. Thresholds are fixed in the
protocol after a power simulation and before the confirmation cohort is opened.

**R1. Reliability and its source.** Estimand: intraclass correlation between half-seasons of $D_1$, $c(2)$,
$\tau_{0.9}$ (rarefied), and of their excess over N0. Rival: the excess has zero reliability (the D5 result).
Reported with the within-team standard error and the Spearman–Brown projection to a full season. Decision: a measure
is carried forward only if the lower bound of its reliability exceeds 0.3.

**R2. Higher-order structure.** Estimand: the standardised excess of $c(2)$, $c(3)$ and $\tau_{0.9}$ over N0, N1 and
N2, pooled across teams by a random-effects mean, at player level on full seasons and at role level. Rival: zero mean
excess under N2. A positive result is the first evidence that a hypergraph adds to a pass network; a negative one
closes the question for event data of this size.

**R3. Selection at small budgets.** Held-out $c(S)$ for $b = 1, \dots, 5$: greedy or exact cover against top-$b$ by
$d$, by $\varphi$, and by pass-network centrality. Rival: degree selects as well (D3 suggests it does). Paired
difference with a margin of 2 points of xG share.

**R4. Absence.** A match-level model over all players, not one player per team:

$$\log \mathbb E[\text{xG}_{t,g}] = \alpha_t + \gamma_{\text{opp}(t,g)} + \eta\,\text{home} - \beta \sum_{v \text{ absent}} \varphi_v - \delta\, C_t \sum_{v \text{ absent}} \varphi_v ,$$

with $\varphi$ and concentration $C_t$ (for example $c(2)$) from the first half, outcomes from the second, team and
opponent effects random. $\beta$ asks whether losing involvement share costs xG; $\delta$ asks whether it costs more
in concentrated teams, which is H3's question with every absence used. Still observational; reported as association.
Power is computed by simulation before fitting.

**R5. External validity.** Does first-half structure predict second-half xG per match, or points, beyond first-half
xG per match? Incremental out-of-sample $R^2$ with team-level cross-validation. Rival: no increment. This is the
test a practitioner would ask for and the project lacks.

**Group effects (replacing H4)**, only if R2 is positive: a mixed model with variance components for players, pairs
and groups in place of ridge indicators under one penalty; a positive control (team effects must be detected); a
planted-effect simulation giving the smallest detectable variance; conclusion stated as an equivalence bound.

### 4.5 Cohorts

| Cohort | Use |
| --- | --- |
| StatsBomb 2015/16, four leagues, 80 teams | Exploration only: definitions, power simulations, thresholds |
| Wyscout 2017/18, five leagues, 98 teams | Confirmation. Descriptive $\tau$, $\nu$, $\operatorname{cov}$ for full seasons have been computed and shown on the site; no split-half or model test has been run. The protocol states this |
| Tournaments, partial seasons | Descriptive, rarefied; never ranked against leagues |

Wyscout lacks possession ids and xG. The rebuild rule and the xG transfer model (75% of goals predicted, POSTHOC P4)
must be validated on the one competition both providers cover before confirmation, using exposure-free measures
($c(2)$, $D_1$), not $\tau$.

## 5. Plan

Each phase ends at a gate; a failed gate stops the work and is reported.

**Phase 0. Corrections (no new analysis).** Apply section 6 to the README, results pages and site text. Remove the
cross-competition rankings of $\tau$ and $\nu$ or rarefy them. Pin dependency versions. Gate: no public sentence
contradicted by section 2.

**Phase 1. Literature and scope.** Read the sources in section 7 and write `docs/BACKGROUND.md`: what each measures,
what baseline it supplies, where this project differs. Move the defence and lineup studies to an appendix of negative
and null results with the limits in sections 3.4 and 3.5, or remove them; remove H4's README claim. Decide whether
minimal-transversal enumeration remains (it does only if R2 or R3 use it). Gate: one question, stated as in 4.1, and
every retained stage serves it.

**Phase 2. Measures.** Implement $\mu$, $\varphi$, $c$, $\tau_\alpha$, $D_q$, $o$, rarefaction, within-team
resampling of matches, and N0 to N2, each with a test on families whose values are known. Extend `fha.audit` to print
the role-level versions. Gate: every statistic has a standard error and a null distribution on the exploration cohort.

**Phase 3. Protocol.** Power simulations on the exploration cohort for R1 to R5; fix estimands, margins, families and
resampling units; validate the Wyscout rebuild. Commit the protocol alone and tag it. Gate: tag exists and predates
any confirmation run in the workflow log.

**Phase 4. Confirmation.** Run R1 to R5 once on Wyscout 2017/18. Report every result with effect size, interval,
margin and verdict among "supported", "equivalent to none", "undetermined". Gate: results pages regenerate from one
command.

**Phase 5. Write-up.** README and site lead with the answer to 4.1. If R2 is negative, the title result is that
chance-creation hypergraphs from event data reduce to involvement counts at this sample size, with the bound.

Order of value if time is short: Phase 0, then R2 with N0 (largely built in `fha.audit`), then R4.

## 6. Statements to correct now

| Where | Statement | Correction |
| --- | --- | --- |
| README, site | "A team's attack has a shape that lasts the season"; site: "a property of the team, not chance" | Split-half 0.42 to 0.48; reproduced by involvement counts (null mean 0.55); the excess over counts is 0.13 (−0.10 to 0.33) |
| README, site facts | Transversal sets cover 94% against 89% for touches | Players ranked by chances involved in cover 95%; the transversal adds nothing over that ranking |
| README | "The two data providers agree … 0.94" | $\tau$ tracks matches played (0.80, 0.83); agreement on top-two share is 0.62 over 8 teams |
| README, site | "Stopping all of them would take at least that many players"; marking tool | Involvement in realised chances, not danger removed |
| README | "Separate routes" | "Chances sharing no player"; within 1 of $\tau$ in 360 of 403 team-seasons |
| Site | Rankings and percentile sentences over all 403 team-seasons | $\tau$ and $\nu$ rise with matches (0.79, 0.82); compare within a competition or rarefy |
| README | "Who is on the ball adds nothing" | The same test gains nothing from player indicators, which identify the team; it supports no conclusion |
| README | Gaps add "a small, measurable amount" | 0.0005 log loss, 0.8% of the gain from ball position, against a linear baseline |
| README, POSTHOC P3 | Season to season "does not clearly carry over" | 16 of 38 pairs are Barcelona, seasons of 7 to 38 matches; not interpretable |
| README, lineup page | Ratings published | 87% of variance is between teams; withdraw the table |

## 7. Reading list

Cited from memory; none was opened for this review. Each must be read before it is relied on or cited.

| Topic | Source |
| --- | --- |
| Pass networks, centralisation and performance | Grund, *Social Networks* 34 (2012); Peña and Touchette, arXiv:1206.6904 (2012); Buldú et al., *Scientific Reports* 9 (2019) |
| Player flow centrality | Duch, Waitzman and Amaral, *PLoS ONE* 5(6) (2010) |
| Pass motifs | Gyarmati, Kwak and Rodriguez, arXiv:1409.0308 (2014); Bekkers and Dabadghao, *Journal of Sports Analytics* 5 (2019) |
| Possession value | Decroos et al., KDD 2019 (VAEP, already cited); Singh, expected threat (2019) |
| Space and pitch control | Spearman, "Beyond expected goals", Sloan 2018; Fernández and Bornn, "Wide open spaces", Sloan 2018 |
| Plus-minus in football | Kharrat, McHale and López Peña, *EJOR* 283 (2020); Hvattum, *IJCSS* 18 (2019); Matano et al., arXiv:1810.08032; Josephs and Upton (already cited) |
| Covers and matchings | Berge, *Hypergraphs* (1989); Lovász, *Discrete Mathematics* 13 (1975); Füredi, *Graphs and Combinatorics* 4 (1988) |
| Submodular coverage | Nemhauser, Wolsey and Fisher, *Mathematical Programming* 14 (1978) |
| Hypergraph null models, higher-order structure | Chodrow, *Journal of Complex Networks* 8 (2020); Benson et al., *PNAS* 115 (2018); Battiston et al., *Physics Reports* 874 (2020) |
| No-three-way-interaction models | Bishop, Fienberg and Holland, *Discrete Multivariate Analysis* (1975) |
| Diversity and rarefaction | Hill, *Ecology* 54 (1973); Gotelli and Colwell, *Ecology Letters* 4 (2001) |
| Reliability, equivalence | Shrout and Fleiss, *Psychological Bulletin* 86 (1979); Schuirmann, *J. Pharmacokinetics and Biopharmaceutics* 15 (1987) |

## 8. Limits of this review

- The audit uses aggregates: groups per team and window. Match-level resampling, the role-level hypergraph, N1 and N2
  need the event data and were not run.
- N0 was drawn 20 times per team; the excess is an integer minus a mean of integers and is coarse. Its low
  reliability (0.13) is bounded above by that of $\tau$ (0.42); the comparison with the null mean (0.55) is the
  informative one.
- The H3 power figure uses the Fisher approximation for a Pearson correlation.
- Defects in 3.3 and 3.4 are read from the code and the published results; no sequence or defence model was refitted.
