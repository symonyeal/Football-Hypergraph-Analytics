# Model

Notation and measures. Registered tests and settings: `HYPOTHESES.md`. Design review and sources: the proposal this
repository was built from (RESEARCH.md, 10 November 2026), summarized here.

## 1. Data objects

| Symbol | Meaning |
| --- | --- |
| $V$, $n$ | Players of one team in one window |
| $e$, $P(e)$ | Possession and its on-ball participants (actors and pass recipients) |
| $A_3(e)$ | Last three distinct players up to the first open-play shot of $e$ |
| $\mathcal F$, $w_A$ | Family of attacking groups (one per shot possession, duplicates kept), weight = open-play xG of the possession |

## 2. Attack measures (`fha/attack.py`, `src/main.rs`)

$T \subseteq V$ is a transversal of $\mathcal F$ when it meets every $A \in \mathcal F$.

$$
\tau = \min\Big\{\textstyle\sum_v x_v : \sum_{v\in A} x_v \ge 1\ \forall A,\ x \in \{0,1\}^V\Big\},\qquad
\tau^* = \nu^* = \max\Big\{\textstyle\sum_A y_A : \sum_{A \ni v} y_A \le 1\ \forall v,\ y \ge 0\Big\},
$$

$\nu$ the most pairwise disjoint members, and $\operatorname{cov}(b) = \max\{\sum_A w_A z_A : z_A \le \sum_{v\in A} x_v,\ \sum_v x_v = b,\ x, z \text{ binary}\}/\sum_A w_A$.
Then $\nu \le \tau^* \le \tau$. The players in every minimal transversal are exactly those forming a one-player group.

| Quantity | Computation | Check |
| --- | --- | --- |
| Minimum transversals, $\tau$ | MMCS (`mcs` crate, pinned) with cardinality bound $k = 0, 1, \dots$ until non-empty | Each set passes `mcs::chk::check` (covers every row; private witness per member) |
| $\tau^*$, $x^*$, $y^*$ | HiGHS LP (`scipy.optimize.linprog`) | Primal and dual feasibility and equal objectives within $10^{-7}$ |
| $\nu$ | HiGHS ILP (`scipy.optimize.milp`) | Status optimal; chosen sets pairwise disjoint |
| $\operatorname{cov}(b)$ | HiGHS ILP on the full weighted family | Status optimal |

## 3. Tie-breaks

$T_\tau$: the minimum transversal with the largest $\sum_{v\in T} x^*_v$, then the smallest sorted player-id list.
$v^*$: the largest $x^*_v$, then the most on-ball actions, then the smallest id.

## 4. Defensive measures (`fha/defence.py`)

$P \subset \mathbb R^2$: visible outfield defenders in metres.

- `gap`: the longest edge of the Euclidean minimum spanning tree of $P$. Under the radius convention it is twice the
  last $H_0$ death of the alpha filtration.
- `hole` $(r, o)$: the largest circumradius $r$ of a Delaunay triangle whose circumcentre $o$ lies in the convex hull.
- `h1`: $\max(\sqrt{d} - \sqrt{b})$ over $H_1$ intervals $[b, d)$ of GUDHI's alpha filtration (squared radii). The alpha
  complex is a subcomplex of the Delaunay triangulation, so `h1` is a function of the same triangles as `hole`.
- `width`, `depth`, `area`: range across, range along, convex-hull area.

## 5. Sources

- Murakami and Uno (2014), MMCS, *Discrete Applied Mathematics* 170; implementation `symonyeal/Minimal-Metabolic-Interventions` at `a807469`.
- Josephs and Upton, *Hypergraph adjusted plus-minus*, J. Quant. Anal. Sports 22(1), 2026, doi:10.1515/jqas-2024-0057 (lineup study, gated).
- Decroos, Bransen, Van Haaren and Davis, *Actions speak louder than goals*, KDD 2019 (VAEP; sequence study).
- GUDHI 3.13 alpha complex documentation.
