# Does who is involved predict danger beyond what happens?

Data: StatsBomb open data, commit `4b73468` of `hudl/open-data`. Analysis is this repository's, not StatsBomb's.

![StatsBomb](https://raw.githubusercontent.com/hudl/open-data/4b73468fc5b0f1950f9f66fada70ad3a4f9327cb/img/SB%20-%20Icon%20Lockup%20-%20Colour%20positive.png)

Possessions alive after three on-ball actions: 107375 training, 107158 test; shot rate 0.118 and 0.117.

## What the metrics mean

| Metric | Meaning |
| --- | --- |
| `p_shot` | Probability that a possession still alive after three on-ball actions produces an open-play shot |
| Log loss | Average penalty for the predicted probabilities; lower is better. Differences between models are the information a feature block adds |
| `who_gain` | Log-loss improvement from adding the set of players involved (model 5) to everything about what happened and where (model 4). Above the threshold: who is on the ball matters beyond the actions themselves |

| Model | Penalty C | Test log loss | Brier |
| --- | --- | --- | --- |
| 0: context | 1.0 | 0.3517 | 0.1012 |
| 1: context + players + pass pairs | 0.01 | 0.3515 | 0.1012 |
| 2: context + VAEP action features | 1.0 | 0.3357 | 0.0965 |
| 3: 1 + pass motif | 0.01 | 0.3514 | 0.1011 |
| 4: 2 ∪ 3 (full rival) | 0.01 | 0.3371 | 0.0971 |
| 5: 4 + player set | 0.01 | 0.3371 | 0.0971 |

| Added information | Change in log loss | Interval |
| --- | --- | --- |
| players and pass pairs over context | -0.00017 | -0.00050 to 0.00016 |
| VAEP action features over context | -0.01598 | -0.01711 to -0.01480 |
| pass motif over players | -0.00014 | -0.00035 to 0.00007 |
| players, pairs, motif over VAEP | 0.00144 | 0.00103 to 0.00182 |
| VAEP over players and motif | -0.01423 | -0.01519 to -0.01330 |
| player set over the full rival (who_gain) | -0.00003 | -0.00004 to -0.00001 |

**H4.** Registered threshold: improvement of at least 0.00169. Does not hold: no demonstrated value of player-set information.

## Calibration of the full rival (model 4), deciles

| Mean predicted | Observed |
| --- | --- |
| 0.036 | 0.043 |
| 0.056 | 0.066 |
| 0.069 | 0.072 |
| 0.082 | 0.076 |
| 0.096 | 0.087 |
| 0.111 | 0.103 |
| 0.129 | 0.113 |
| 0.151 | 0.128 |
| 0.182 | 0.169 |
| 0.271 | 0.317 |
