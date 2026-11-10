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
| 0: context | 0.01 | 0.3516 | 0.1012 |
| 1: context + players + pass pairs | 0.001 | 0.4839 | 0.1266 |
| 2: context + VAEP action features | 0.1 | 0.3355 | 0.0965 |
| 3: 1 + pass motif | 0.001 | 0.4859 | 0.1263 |
| 4: 2 ∪ 3 (full rival) | 0.001 | 0.4673 | 0.1219 |
| 5: 4 + player set | 0.001 | 0.4827 | 0.1244 |

| Added information | Change in log loss | Interval |
| --- | --- | --- |
| players and pass pairs over context | 0.13223 | 0.12725 to 0.13749 |
| VAEP action features over context | -0.01611 | -0.01726 to -0.01491 |
| pass motif over players | 0.00207 | 0.00165 to 0.00249 |
| players, pairs, motif over VAEP | 0.13182 | 0.12690 to 0.13698 |
| VAEP over players and motif | -0.01859 | -0.02008 to -0.01714 |
| player set over the full rival (who_gain) | 0.01533 | 0.01403 to 0.01663 |

**H4.** Registered threshold: improvement of at least 0.00234. Does not hold: no demonstrated value of player-set information.

## Calibration of the full rival (model 4), deciles

| Mean predicted | Observed |
| --- | --- |
| 0.002 | 0.076 |
| 0.006 | 0.085 |
| 0.012 | 0.094 |
| 0.020 | 0.096 |
| 0.033 | 0.104 |
| 0.053 | 0.109 |
| 0.082 | 0.114 |
| 0.129 | 0.134 |
| 0.221 | 0.165 |
| 0.542 | 0.196 |
