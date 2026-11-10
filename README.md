# Football Hypergraph Analytics

Which players is a team's attack built around, how many separate routes to a shot does it have, and what does a
defence look like just before it is broken?

Each chance is treated as the group of the last three players involved before the shot. From a team's chances over a
half-season the project measures:

- how few players took part in every chance (concentration),
- how many chances shared no player at all (separate routes),
- how much of the team's expected goals two players were involved in,
- which player most chances depend on.

It then checks, on the other half of the season, whether those numbers are stable. It also checks whether teams with
fewer separate routes create less when their key player is missing.

For defences, it measures the widest gap between neighbouring defenders and the largest empty circle inside the block
at each pass. It then tests whether these predict the ball reaching the penalty box in the next ten seconds.

Every test was written down before the data was opened: [registered hypotheses](docs/HYPOTHESES.md). Results:
[attack](results/attack.md), [defence](results/defence.md), once the data workflow has run.

Data: StatsBomb open data (2015/16 Premier League, La Liga, Serie A and Ligue 1; Euro 2020, World Cup 2022 and Euro
2024 360 frames). The data is streamed, never stored or redistributed here; only aggregate results are committed.

![StatsBomb](https://raw.githubusercontent.com/hudl/open-data/4b73468fc5b0f1950f9f66fada70ad3a4f9327cb/img/SB%20-%20Icon%20Lockup%20-%20Colour%20positive.png)

## Project map

| Path | Holds |
| --- | --- |
| `fha/sb.py` | StatsBomb events to attacking groups and sequence cutoffs |
| `fha/attack.py` | Concentration and route measures (LP/ILP by HiGHS, minimum transversals by the Rust `tr`) |
| `fha/defence.py` | Gap, hole, persistence and shape of the defenders |
| `fha/run.py`, `fha/report.py` | Registered tests and the results pages |
| `src/main.rs` | `tr`: minimal transversals by MMCS (`mcs` crate) |
| `docs/MODEL.md` | Notation, measures and checks |

```text
cargo build --release && pip install -r requirements.txt && python -m pytest -q
python -m fha.run attack     # streams about 1,500 matches; run by the "derive" GitHub workflow
python -m fha.report
```

Licence: MIT. StatsBomb data remains subject to the StatsBomb Public Data User Agreement.
