# Lineup ratings (gated)

Data: StatsBomb open data, commit `4b73468` of `hudl/open-data`. Analysis is this repository's, not StatsBomb's.

![StatsBomb](https://raw.githubusercontent.com/hudl/open-data/4b73468fc5b0f1950f9f66fada70ad3a4f9327cb/img/SB%20-%20Icon%20Lockup%20-%20Colour%20positive.png)

A player's rating is the change in the team's open-play xG difference per 90 minutes with the player on the pitch, other players, manpower and score held fixed (ridge regression over stints of constant personnel). A player is rated only with at least 900 minutes and at least 270 team minutes without the player over 5 or more matches.

| Half | Stints | Players | Eligible | Penalty | Home advantage (xG/90) | Per extra player (xG/90) | Per goal of lead (xG/90) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| train | 8724 | 1924 | 596 | 10000 | 0.200 | 0.022 | -0.032 |
| test | 8707 | 1969 | 592 | 10000 | 0.307 | 0.049 | -0.025 |

**H6.** Players eligible in both halves: 283. Split-half Spearman 0.52 (0.42 to 0.61): holds.

| Highest rated | xG/90 | Lowest rated | xG/90 |
| --- | --- | --- | --- |
| Zlatan Ibrahimović | 0.095 | Lossémy Karaboué | -0.050 |
| Karim Benzema | 0.071 | Rubén Rochina Naixes | -0.048 |
| Edinson Roberto Cavani Gómez | 0.067 | Fabien Camus | -0.046 |
| Ángel Fabián Di María Hernández | 0.066 | Paolo Sammarco | -0.044 |
| Jordi Alba Ramos | 0.064 | Benjamin Nivet | -0.044 |
| Ivan Rakitić | 0.063 | Jordan Ayew | -0.044 |
| Alexis Alejandro Sánchez Sánchez | 0.063 | Corentin Jean | -0.044 |
| Thiago Motta | 0.061 | Leonardo Blanchard | -0.041 |
| Marcelo Vieira da Silva Júnior | 0.057 | Mirko Gori | -0.037 |
| David Luiz Moreira Marinho | 0.056 | Leandro Bacuna | -0.037 |
| Kléper Laveran Lima Ferreira | 0.056 | Federico Dionisi | -0.035 |
| Gerard Piqué Bernabéu | 0.055 | François Modesto | -0.033 |
| Lucas Rodrigues Moura da Silva | 0.053 | Isaac Ajayi Success | -0.033 |
| Maxwell Scherrer Cabelino Andrade | 0.053 | Rubén Salvador Pérez Del Mármol | -0.032 |
| Paulo Bruno Exequiel Dybala | 0.052 | Matthieu Saunier | -0.030 |
