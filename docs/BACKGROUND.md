# Background

What prior work measures, the baseline it supplies to this project, and where this project differs. Sources are
those listed in `REVIEW.md` section 7. Most were read at abstract level only, and the **Read** column says so for each.
A source marked "catalogue" or "not opened" is cited for its bibliographic record only; nothing here rests on its
content.

## Football networks and values

| Source | What it measures | Baseline it supplies | Read |
| --- | --- | --- | --- |
| Grund, *Social Networks* 34(4), 682–690 (2012), doi:10.1016/j.socnet.2012.08.004 | Pass networks of Premier League teams (283,259 passes; 76 repeated observations of 23 teams), with mixed-effects models of performance. Higher interaction intensity and lower centralisation go with better performance | Centralisation of the weighted pass network: the pairwise rival to $c(b)$ and $D_q$ | Abstract |
| López Peña and Touchette, arXiv:1206.6904 (2012); in *Sports Physics*, École Polytechnique (2013), 517–528 | Weighted directed pass networks of 2010 World Cup teams; centralities rank players and estimate the effect of removing one | Player centrality in the pass network: the rival ranking for R3 | Abstract |
| Buldú, Busquets, Echegoyen and Seirul·lo, *Scientific Reports* 9, 13602 (2019), doi:10.1038/s41598-019-49969-2 | Passing networks (Opta, all 380 La Liga 2009/10 matches); Barcelona differs from opponents in clustering, path length, eigenvalues, algebraic connectivity and centrality dispersion. Part of the difference comes from Barcelona's higher pass count | Network metrics compared under a false-discovery-rate correction; a warning that volume drives network statistics, as exposure drives $\tau$ here | Full text, through a summarising reader |
| Duch, Waitzman and Amaral, *PLoS ONE* 5(6), e10937 (2010), doi:10.1371/journal.pone.0010937 | Flow centrality of players in pass-to-shot networks, Euro 2008 (30 matches). The mean of a team's top two players separates wins from other results (AUC 0.825) | Flow centrality: a player measure on paths ending in shots, the nearest pairwise analogue of $\varphi$; and an outcome test of the kind R5 asks for | Full text, through a summarising reader |
| Gyarmati, Kwak and Rodriguez, arXiv:1409.0308 (2014), KDD Workshop on Large-Scale Sports Analytics | Flow motifs: significant pass-sequence patterns per team; most teams play similar styles | Motif counts: the sequence baseline H4 used | Abstract |
| Bekkers and Dabadghao, *Journal of Sports Analytics* 5(4), 299–311 (2019), doi:10.3233/JSA-190290 | — | — | Not opened |
| Decroos, Bransen, Van Haaren and Davis, KDD 2019, doi:10.1145/3292500.3330758; arXiv:1802.07127 | SPADL action language and VAEP: each action valued by its change in the probabilities of scoring and conceding | Action values: the model H4 conditioned on | Abstract |
| Singh, "Introducing Expected Threat (xT)", karun.in (undated; uses 2017/18 Premier League data) | Grid of scoring probabilities within the next actions (16 × 12 zones, event data); a move is valued by its change in xT | Location-based possession value: credit spread along a possession, an alternative to equal-split credit $\varphi$ | Full page |
| Spearman, "Beyond expected goals", Sloan 2018 | — | — | Not opened |
| Fernández and Bornn, "Wide open spaces", Sloan 2018 | — | — | Not opened |

## Plus-minus

| Source | Content | Read |
| --- | --- | --- |
| Kharrat, McHale and López Peña, *EJOR* 283(2), 726–736 (2020), doi:10.1016/j.ejor.2019.11.026 | Plus-minus for football; content not read | Catalogue |
| Hvattum, *IJCSS* 18(1), 1–23 (2019), doi:10.2478/ijcss-2019-0001 | Review of plus-minus ratings, which distribute team performance onto players | Abstract |
| Matano et al., arXiv:1810.08032 (2018) | Bayesian adjusted plus-minus with FIFA video-game ratings as prior; better prediction and less collinearity than plain APM | Abstract |

The withdrawn H6 ratings were ridge plus-minus with one penalty and no prior. Matano et al. address the collinearity
that made those ratings measure team strength (`REVIEW.md` 3.5).

## Methods

| Source | Used for | Read |
| --- | --- | --- |
| Chodrow, *J. Complex Networks* 8(3), cnaa018 (2020), doi:10.1093/comnet/cnaa018 | Null hypergraphs with fixed degrees and edge sizes, and an MCMC sampler. N0 fixes the same quantities but samples by stub re-dealing with repair, which is not uniform over such hypergraphs | Abstract |
| Benson et al., *PNAS* 115(48), E11221–E11230 (2018), doi:10.1073/pnas.1800683115 | Higher-order structure in 19 data sets of group interactions; higher-order link prediction | Abstract |
| Battiston et al., *Physics Reports* 874, 1–92 (2020), doi:10.1016/j.physrep.2020.05.004 | Review of hypergraph and simplicial representations and measures | Abstract |
| Bishop, Fienberg and Holland, *Discrete Multivariate Analysis* (1975) | No-three-way-interaction log-linear models (N2) | Not opened |
| Hill, *Ecology* 54(2), 427–432 (1973), doi:10.2307/1934352 | Hill numbers: effective numbers unifying richness, Shannon and Simpson ($D_q$) | Abstract |
| Gotelli and Colwell, *Ecology Letters* 4(4), 379–391 (2001), doi:10.1046/j.1461-0248.2001.00230.x | Rarefaction of richness | Catalogue |
| Shrout and Fleiss, *Psychological Bulletin* 86(2), 420–428 (1979), doi:10.1037/0033-2909.86.2.420 | Six forms of the intraclass correlation; ICC(2,1) is used for R1 | Abstract |
| Schuirmann, *J. Pharmacokinetics and Biopharmaceutics* 15(6), 657–680 (1987), doi:10.1007/BF01068419 | Two one-sided tests for equivalence | Abstract (truncated) |
| DerSimonian and Laird, *Controlled Clinical Trials* 7(3), 177–188 (1986), doi:10.1016/0197-2456(86)90046-2 | Random-effects pooling (R2) | Catalogue |
| Lovász, *Discrete Mathematics* 13(4), 383–390 (1975), doi:10.1016/0012-365X(75)90058-8; Füredi, *Graphs and Combinatorics* 4(1), 115–206 (1988), doi:10.1007/BF01864160; Nemhauser, Wolsey and Fisher, *Mathematical Programming* 14(1), 265–294 (1978), doi:10.1007/BF01588971 | Integral against fractional covers; matchings and covers in hypergraphs; the $1 - 1/e$ guarantee for greedy submodular maximisation | Catalogue |

## Where this project differs

- **Object.** The pass-network papers model pairs (passer, receiver). This project models the set of the last three
  players before a shot. Duch et al. come closest, scoring players on paths that end in shots. None of the opened
  sources tests whether sets of three carry information beyond the pairwise network, which is the null N2 and the
  question of `REVIEW.md` 4.1.
- **Exposure.** Buldú et al. note that Barcelona's network metrics partly reflect its higher pass count; here $\tau$
  and $\nu$ rise with chances observed (review D1, D6). Both point to functionals with limits, or to rarefaction.
- **Credit.** VAEP and xT spread credit along a possession by location and action. $\varphi$ splits a chance's xG
  equally among its group, which needs no model but ignores who did what.
- **Outcome tests.** Duch et al. and Grund relate network measures to results. This project has not yet done so (R5).

Not yet read in full: every source except Buldú et al., Duch et al. and Singh. A source must be read in full before
a claim beyond the content stated here rests on it.
