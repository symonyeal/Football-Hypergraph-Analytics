# Defensive shape at the moment of a pass

Data: StatsBomb open data, commit `4b73468` of `hudl/open-data`. Analysis is this repository's, not StatsBomb's.

![StatsBomb](https://raw.githubusercontent.com/hudl/open-data/4b73468fc5b0f1950f9f66fada70ad3a4f9327cb/img/SB%20-%20Icon%20Lockup%20-%20Colour%20positive.png)

Passes: open play, attacking team, starting in the opponent half outside the box, at least 6 outfield defenders visible in the 360 frame. Label: the attacking team has an event in the box within 10 s in the same possession. Training: Euro 2020 and World Cup 2022; test: Euro 2024.

## What the metrics mean

| Metric | What it measures (metres) | High value means | It is not |
| --- | --- | --- | --- |
| `gap` | Longest link of the shortest network joining the visible outfield defenders | One defender is far from every teammate: a wide hole between neighbours | Distance to the ball |
| `hole` | Radius of the largest circle inside the defensive block that touches three defenders and contains none | Large empty space inside the block | Space behind or beside the block |
| `h1` | Lifetime of the longest-lived ring of defenders in the alpha filtration | A ring of defenders around a gap that stays open over a range of distances | A new kind of space: it is computed from the same triangles as `hole` |
| `width`, `depth`, `area` | Spread across and along the pitch, area of the block | Stretched block | — |

Passes: 40334 training, 19307 test. Box-entry rate: 0.217 training, 0.220 test.

## H5. Do gaps and holes predict box entries, and does topology add anything?

| Model | Test log loss |
| --- | --- |
| base | 0.4607 |
| shape | 0.4591 |
| gaps | 0.4586 |
| topology | 0.4586 |

**Shape over ball position.** Change in log loss -0.0017 (-0.0028 to -0.0004): holds.

**H5a: gap and hole over shape.** Change in log loss -0.0005 (-0.0009 to -0.0001): holds.

**H5b: h1 over gap and hole.** Change in log loss -0.0000 (-0.0001 to 0.0000): not resolved (interval contains 0) — registered expectation is 'not resolved'.

## How box-entry rate changes with each measure

All passes, quartiles of the measure.

| Measure | Q1 range (m) | Q1 rate | Q2 rate | Q3 rate | Q4 rate | Q4 range (m) |
| --- | --- | --- | --- | --- | --- | --- |
| `gap` | 1.6–11.1 | 0.306 | 0.206 | 0.183 | 0.178 | 14.7–37.5 |
| `hole` | 0.0–7.3 | 0.328 | 0.202 | 0.178 | 0.165 | 9.7–21.9 |
| `h1` | 0.0–0.4 | 0.313 | 0.223 | 0.189 | 0.148 | 1.2–5.6 |

Passes ending inside the largest hole: 0.102 of all passes, 0.115 of box-entry passes. Box-entry rate 0.245 when the pass ends in the hole, 0.215 otherwise.

## Standardised coefficients

| Model | Coefficients |
| --- | --- |
| base | x 0.088, yy 0.026, dist -0.822 |
| shape | x 0.145, yy 0.027, dist -0.695, width -0.140, depth 0.014, area -0.040 |
| gaps | x 0.129, yy 0.027, dist -0.703, width -0.166, depth -0.028, area -0.051, gap 0.074, hole 0.019 |
| topology | x 0.128, yy 0.027, dist -0.703, width -0.167, depth -0.028, area -0.043, gap 0.073, hole 0.017, h1 -0.011 |
