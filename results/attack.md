# Attack structure: concentration and redundancy

Data: StatsBomb open data, commit `4b73468` of `hudl/open-data`. Analysis is this repository's, not StatsBomb's.

![StatsBomb](https://raw.githubusercontent.com/hudl/open-data/4b73468fc5b0f1950f9f66fada70ad3a4f9327cb/img/SB%20-%20Icon%20Lockup%20-%20Colour%20positive.png)

Windows: training = match weeks 1–19 of 2015/16, test = weeks 20–38. Registered tests: `docs/HYPOTHESES.md`.

## What the metrics mean

| Metric | What it counts | High value means | Low value means | It is not |
| --- | --- | --- | --- | --- |
| `tau` | Fewest players such that every dangerous attack (open-play shot possession) involved at least one of them, counting the last three players before the shot | Danger comes from many separate places; no small group is behind every chance | A few players are behind every chance | A rating of those players; marking them would not necessarily stop attacks |
| `tau*` | Fractional version of `tau`: the least total weight on players so that every attack carries weight at least 1 | As `tau` | As `tau` | — |
| `nu` | Most dangerous attacks that share no player at all | Many fully separate routes to a shot; stopping all of them needs at least `nu` players | Attacks overlap in the same people | A count of attacks |
| `cov(2)` | Largest share of the team's open-play xG in which at least one of two players took part | The attack depends on two players | Danger is spread | Those players' xG; involvement is any of the last three |
| `x*` share | A player's part of the fractional `tau*` | The player is a bottleneck: many attacks have few alternatives to them | The player's attacks have alternatives | Touches or usage |
| `solo` | Share of xG from attacks where one player was the only one involved | Individual creation (dribble-and-shoot, loose-ball finishes) | Combination play | — |

## H1. Are these team properties?

Spearman correlation of each metric between the two half-seasons across teams, with a 95% bootstrap interval.

| Metric | Correlation | Interval | Verdict | Same with xG ≥ 0.1 attacks only |
| --- | --- | --- | --- | --- |
| `tau` | 0.42 | 0.22 to 0.58 | holds | 0.40 (0.19 to 0.57) |
| `tau_star` | 0.48 | 0.29 to 0.62 | holds | 0.34 (0.11 to 0.54) |
| `nu` | 0.42 | 0.23 to 0.57 | holds | 0.27 (0.04 to 0.49) |
| `cov2` | 0.43 | 0.22 to 0.61 | holds | — |

## H2. Do transversal sets find the key players better than usage?

Share of test-period dangerous xG involving the chosen players. Each set has `tau` players, chosen on the training half.

| Set | Mean held-out coverage |
| --- | --- |
| Minimum transversal `T` | 0.94 |
| Exact best coverage `C` | 0.94 |
| Most on-ball actions `U` | 0.89 |

`C − U` = 0.052 (interval 0.035 to 0.071): holds. `T − U` = 0.058 (interval 0.042 to 0.074): holds.

## H3. Do teams with fewer separate routes suffer more when their bottleneck player is missing?

Drop = 1 − (team xG relative to the opponent's usual concession, in matches the player missed) / (the same, in matches the player started). Observational: rotation and injury are not random.

**Top `x*` player.** 32 eligible teams.
 Correlation of drop with training `nu`: -0.25 (-0.56 to 0.10), not resolved (interval contains 0); with `cov(2)`: 0.06 (-0.32 to 0.41), not resolved (interval contains 0).

| Team | Player | Missed | Started | Drop |
| --- | --- | --- | --- | --- |
| Villarreal | Samuel Castillejo Azuaga | 3 | 10 | 0.57 |
| Lazio | Antonio Candreva | 4 | 14 | 0.50 |
| Stoke City | Marko Arnautović | 3 | 16 | 0.46 |
| Paris Saint-Germain | Javier Matías Pastore | 10 | 5 | 0.39 |
| Atalanta | Alejandro Darío Gómez | 4 | 15 | 0.35 |
| Levante UD | Víctor Camarasa Ferrando | 4 | 6 | 0.30 |
| Nantes | Adryan Oliveira Tavares | 3 | 13 | 0.29 |
| Lille | Sofiane Boufal | 5 | 12 | 0.25 |
| Gazélec Ajaccio | David Ducourtioux | 3 | 13 | 0.14 |
| Las Palmas | Sergio Ezequiel Araújo | 8 | 3 | 0.13 |
| Crystal Palace | Jason Puncheon | 7 | 12 | 0.11 |
| Hellas Verona | Federico Viviani | 11 | 7 | 0.09 |
| Sassuolo | Domenico Berardi | 3 | 15 | 0.05 |
| Chievo | Valter Birsa | 3 | 15 | 0.03 |
| Watford | Allan Romeo Nyom | 6 | 11 | 0.03 |
| Guingamp | Yannis Salibur | 5 | 14 | 0.01 |
| Liverpool | James Philip Milner | 6 | 13 | -0.03 |
| Celta Vigo | Fabián Ariel Orellana Valenzuela | 5 | 14 | -0.06 |
| Tottenham Hotspur | Bamidele Alli | 3 | 14 | -0.08 |
| AC Milan | Giacomo Bonaventura | 4 | 14 | -0.10 |
| Sevilla | Víctor Machín Pérez | 9 | 6 | -0.11 |
| Valencia | Francisco Alcácer García | 3 | 12 | -0.21 |
| Atlético Madrid | Diego Roberto Godín Leal | 7 | 12 | -0.24 |
| Frosinone | Daniel Pavlovic | 5 | 14 | -0.26 |
| Lyon | Mathieu Valbuena | 7 | 7 | -0.29 |
| Fiorentina | Matías Vecino Falero | 4 | 13 | -0.33 |
| Manchester City | Aleksandar Kolarov | 7 | 8 | -0.35 |
| Torino | Cesare Bovo | 13 | 6 | -0.37 |
| Angers | Thomas Mangani | 5 | 12 | -0.39 |
| Udinese | Francesco Lodi | 8 | 8 | -0.40 |
| Bologna | Adam Masina | 4 | 12 | -0.50 |
| Inter Milan | Gary Alexis Medel Soto | 5 | 12 | -0.77 |

**Top usage player.** 28 eligible teams.
 Correlation of drop with training `nu`: -0.08 (-0.43 to 0.30), not resolved (interval contains 0); with `cov(2)`: 0.24 (-0.14 to 0.56), not resolved (interval contains 0).

| Team | Player | Missed | Started | Drop |
| --- | --- | --- | --- | --- |
| Chievo | Massimo Gobbi | 3 | 15 | 0.47 |
| Getafe | Damián Nicolás Suárez Suárez | 5 | 14 | 0.38 |
| Newcastle United | Daryl Janmaat | 5 | 14 | 0.37 |
| Atalanta | Alejandro Darío Gómez | 4 | 15 | 0.35 |
| Real Madrid | Toni Kroos | 4 | 15 | 0.20 |
| Udinese | Edenílson Andrade dos Santos | 8 | 9 | 0.18 |
| Manchester City | Bacary Sagna | 9 | 9 | 0.17 |
| Genoa | Tomás Eduardo Rincón Hernández | 4 | 15 | 0.17 |
| Liverpool | Nathaniel Edwin Clyne | 5 | 14 | 0.16 |
| Gazélec Ajaccio | David Ducourtioux | 3 | 13 | 0.14 |
| Stade de Reims | Franck Signorino | 7 | 12 | 0.12 |
| Crystal Palace | Jason Puncheon | 7 | 12 | 0.11 |
| Atlético Madrid | Filipe Luís Kasmirski | 3 | 16 | 0.03 |
| Frosinone | Danilo Soddimo | 8 | 6 | 0.03 |
| Celta Vigo | Fabián Ariel Orellana Valenzuela | 5 | 14 | -0.06 |
| AC Milan | Giacomo Bonaventura | 4 | 14 | -0.10 |
| Paris Saint-Germain | Thiago Motta | 5 | 12 | -0.11 |
| Lazio | Dušan Basta | 11 | 6 | -0.13 |
| Levante UD | Antonio García Aranda | 10 | 8 | -0.15 |
| Bastia | Seko Fofana | 6 | 8 | -0.15 |
| Watford | Etienne Capoue | 5 | 14 | -0.26 |
| Angers | Thomas Mangani | 5 | 12 | -0.39 |
| Lorient | Didier Ndong Ibrahim | 3 | 16 | -0.40 |
| Lyon | Jordan Ferri | 3 | 12 | -0.42 |
| Málaga | Roberto José Rosales Altuve | 3 | 16 | -0.44 |
| Bologna | Adam Masina | 4 | 12 | -0.50 |
| Sevilla | Grzegorz Krychowiak | 11 | 7 | -0.72 |
| Inter Milan | Gary Alexis Medel Soto | 5 | 12 | -0.77 |

## Teams

Training half; test-half value in brackets. `cov(2)` names the two players.

| Team | League | Attacks | `tau` | `nu` | `cov(2)` | Two players | Bottleneck (`x*` share) | Solo xG |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Athletic Club | La Liga | 205 | 9 (10) | 8 (9) | 0.71 (0.55) | Beñat Etxebarria Urkiaga, Aritz Aduriz Zubeldia | Beñat Etxebarria Urkiaga (0.12) | 0.01 |
| Atlético Madrid | La Liga | 216 | 10 (9) | 8 (8) | 0.71 (0.73) | Jorge Resurrección Merodio, Antoine Griezmann | Diego Roberto Godín Leal (0.11) | 0.00 |
| Barcelona | La Liga | 260 | 7 (6) | 6 (5) | 0.87 (0.86) | Neymar da Silva Santos Junior, Luis Alberto Suárez Díaz | Neymar da Silva Santos Junior (0.15) | 0.00 |
| Celta Vigo | La Liga | 207 | 6 (9) | 6 (8) | 0.87 (0.71) | Manuel Agudo Durán, Iago Aspas Juncal | Fabián Ariel Orellana Valenzuela (0.17) | 0.01 |
| Eibar | La Liga | 193 | 8 (8) | 7 (8) | 0.71 (0.66) | Saúl Berjón Pérez, Borja González Tomás | Saúl Berjón Pérez (0.14) | 0.03 |
| Espanyol | La Liga | 151 | 9 (10) | 9 (8) | 0.73 (0.67) | Marco Asensio Willemsen, Felipe Salvador Caicedo Corozo | Marco Asensio Willemsen (0.11) | 0.00 |
| Getafe | La Liga | 165 | 9 (11) | 9 (10) | 0.69 (0.75) | Víctor Rodríguez Romero, Álvaro Vázquez García | Álvaro Vázquez García (0.11) | 0.00 |
| Granada | La Liga | 186 | 10 (9) | 10 (9) | 0.60 (0.78) | Rubén Rochina Naixes, Youssef El-Arabi | Rubén Rochina Naixes (0.10) | 0.00 |
| Las Palmas | La Liga | 183 | 9 (9) | 8 (9) | 0.81 (0.65) | Jonathan Viera Ramos, Sergio Ezequiel Araújo | Sergio Ezequiel Araújo (0.12) | 0.00 |
| Levante UD | La Liga | 183 | 8 (10) | 8 (9) | 0.62 (0.63) | José Luis Morales Nogales, José Antonio García Rabasco | Víctor Camarasa Ferrando (0.12) | 0.07 |
| Málaga | La Liga | 201 | 12 (10) | 10 (9) | 0.64 (0.67) | Sérgio Paulo Barbosa Valente, Charles Días Barbosa de Oliveira | Nordin Amrabat (0.09) | 0.00 |
| RC Deportivo La Coruña | La Liga | 195 | 8 (8) | 8 (7) | 0.85 (0.85) | Fayçal Fajr, Lucas Pérez Martínez | Pedro Mosquera Parada (0.12) | 0.00 |
| Rayo Vallecano | La Liga | 205 | 10 (9) | 9 (8) | 0.66 (0.78) | Jozabed Sánchez Ruiz, Javier Guerra Rodríguez | Roberto Trashorras Gayoso (0.10) | 0.00 |
| Real Betis | La Liga | 182 | 11 (11) | 10 (10) | 0.73 (0.71) | Rubén Castro Martín, Joaquín Sánchez Rodríguez | Cristiano Piccini (0.10) | 0.01 |
| Real Madrid | La Liga | 336 | 10 (10) | 9 (9) | 0.71 (0.77) | Cristiano Ronaldo dos Santos Aveiro, Gareth Frank Bale | Cristiano Ronaldo dos Santos Aveiro (0.11) | 0.02 |
| Real Sociedad | La Liga | 217 | 11 (9) | 10 (9) | 0.61 (0.68) | Armindo Tué Na Bangna, Imanol Agirretxe Arruti | Asier Illarramendi Andonegi (0.10) | 0.00 |
| Sevilla | La Liga | 226 | 10 (12) | 8 (11) | 0.58 (0.63) | Yevhen Konoplyanka, Kevin Gameiro | Víctor Machín Pérez (0.12) | 0.03 |
| Sporting Gijón | La Liga | 173 | 10 (10) | 10 (9) | 0.70 (0.78) | Alen Halilović, Jonathan Rodríguez Menéndez | Alen Halilović (0.10) | 0.03 |
| Valencia | La Liga | 160 | 10 (11) | 9 (10) | 0.59 (0.66) | Rodrigo Javier De Paul, Francisco Alcácer García | Francisco Alcácer García (0.10) | 0.06 |
| Villarreal | La Liga | 152 | 9 (9) | 7 (8) | 0.69 (0.65) | Roberto Soldado Rillo, Cédric Bakambu | Samuel Castillejo Azuaga (0.10) | 0.00 |
| AS Monaco | Ligue 1 | 181 | 10 (11) | 9 (11) | 0.52 (0.55) | João Filipe Iria Santos Moutinho, Bernardo Mota Veiga de Carvalho e Silva | Fábio Henrique Tavares (0.10) | 0.00 |
| Angers | Ligue 1 | 179 | 8 (8) | 7 (8) | 0.66 (0.68) | Thomas Mangani, Billy Ketkeophomphone | Thomas Mangani (0.14) | 0.00 |
| Bastia | Ligue 1 | 130 | 8 (7) | 7 (7) | 0.74 (0.76) | Floyd Ayité, Gaël Danic | Gaël Danic (0.13) | 0.07 |
| Bordeaux | Ligue 1 | 187 | 11 (11) | 10 (10) | 0.73 (0.63) | Wahbi Khazri, Enzo Crivelli | Henri Saivet (0.10) | 0.00 |
| Gazélec Ajaccio | Ligue 1 | 176 | 9 (9) | 8 (7) | 0.62 (0.62) | Mohamed Larbi, Jacques Zoua Daogari | David Ducourtioux (0.12) | 0.00 |
| Guingamp | Ligue 1 | 183 | 9 (9) | 9 (9) | 0.74 (0.78) | Yannis Salibur, Jimmy Briand | Yannis Salibur (0.11) | 0.01 |
| Lille | Ligue 1 | 217 | 11 (10) | 10 (9) | 0.72 (0.62) | Sofiane Boufal, Éric Bauthéac | Sofiane Boufal (0.10) | 0.00 |
| Lorient | Ligue 1 | 194 | 9 (9) | 9 (8) | 0.68 (0.65) | Benjamin Moukandjo Bilé, Benjamin Jeannot | Denis Bouanga (0.11) | 0.00 |
| Lyon | Ligue 1 | 236 | 11 (7) | 10 (7) | 0.66 (0.79) | Mathieu Valbuena, Claudio Beauvue | Mathieu Valbuena (0.10) | 0.00 |
| Montpellier | Ligue 1 | 171 | 10 (8) | 9 (8) | 0.86 (0.78) | Ryad Boudebouz, Rodrigue Casimir Ninga | Ryad Boudebouz (0.11) | 0.00 |
| Nantes | Ligue 1 | 189 | 11 (9) | 10 (9) | 0.61 (0.65) | Adrien Thomasson, Yacine Bammou | Adryan Oliveira Tavares (0.10) | 0.00 |
| OGC Nice | Ligue 1 | 173 | 8 (9) | 7 (7) | 0.79 (0.82) | Jean Michaël Seri, Hatem Ben Arfa | Jean Michaël Seri (0.13) | 0.01 |
| Olympique de Marseille | Ligue 1 | 222 | 11 (9) | 10 (8) | 0.77 (0.67) | Abdelaziz Barrada, Michy Batshuayi Tunga | Michy Batshuayi Tunga (0.10) | 0.00 |
| Paris Saint-Germain | Ligue 1 | 240 | 10 (8) | 9 (8) | 0.75 (0.75) | Ángel Fabián Di María Hernández, Zlatan Ibrahimović | Javier Matías Pastore (0.11) | 0.00 |
| Rennes | Ligue 1 | 181 | 11 (10) | 9 (10) | 0.60 (0.68) | Abdoulaye Doucouré, Giovanni-Guy Yann Sio | Sylvain Armand (0.10) | 0.05 |
| Saint-Étienne | Ligue 1 | 200 | 10 (11) | 10 (9) | 0.74 (0.55) | Valentin Eysseric, Romain Hamouma | Fabien Lemoine (0.10) | 0.01 |
| Stade Malherbe Caen | Ligue 1 | 202 | 7 (9) | 7 (9) | 0.74 (0.78) | Julien Féret, Andy Delort | Julien Féret (0.14) | 0.00 |
| Stade de Reims | Ligue 1 | 175 | 10 (10) | 9 (10) | 0.65 (0.81) | Nicolas de Roussel de Préville, David N"Gog | Nicolas de Roussel de Préville (0.11) | 0.02 |
| Toulouse | Ligue 1 | 189 | 8 (7) | 8 (7) | 0.70 (0.73) | Wissam Ben Yedder, Martin Braithwaite Christensen | Óscar Guido Trejo (0.13) | 0.01 |
| Troyes | Ligue 1 | 206 | 10 (8) | 8 (8) | 0.63 (0.61) | Fabien Camus, Corentin Jean | Fabien Camus (0.12) | 0.00 |
| AFC Bournemouth | Premier League | 219 | 10 (9) | 10 (8) | 0.60 (0.60) | Matt Ritchie, Junior Stanislas | Simon Francis (0.10) | 0.02 |
| Arsenal | Premier League | 262 | 7 (9) | 7 (9) | 0.77 (0.74) | Mesut Özil, Alexis Alejandro Sánchez Sánchez | Mesut Özil (0.14) | 0.00 |
| Aston Villa | Premier League | 181 | 10 (10) | 9 (10) | 0.49 (0.58) | Jordan Veretout, Rudy Gestede | Idrissa Gana Gueye (0.06) | 0.00 |
| Chelsea | Premier League | 229 | 7 (9) | 7 (7) | 0.72 (0.68) | Francesc Fàbregas i Soler, Willian Borges da Silva | Francesc Fàbregas i Soler (0.14) | 0.01 |
| Crystal Palace | Premier League | 205 | 9 (11) | 9 (9) | 0.66 (0.49) | Jason Puncheon, Yohan Cabaye | Jason Puncheon (0.11) | 0.01 |
| Everton | Premier League | 219 | 9 (10) | 8 (9) | 0.85 (0.67) | Ross Barkley, Romelu Lukaku Menama | Ross Barkley (0.12) | 0.00 |
| Leicester City | Premier League | 215 | 8 (10) | 8 (9) | 0.77 (0.68) | Marc Albrighton, Jamie Vardy | Danny Drinkwater (0.12) | 0.01 |
| Liverpool | Premier League | 270 | 10 (11) | 9 (10) | 0.64 (0.56) | Philippe Coutinho Correia, Christian Benteke Liolo | James Philip Milner (0.11) | 0.00 |
| Manchester City | Premier League | 279 | 9 (11) | 9 (11) | 0.69 (0.68) | Kevin De Bruyne, Raheem Sterling | Aleksandar Kolarov (0.11) | 0.00 |
| Manchester United | Premier League | 184 | 9 (8) | 8 (8) | 0.67 (0.71) | Juan Manuel Mata García, Anthony Martial | Juan Manuel Mata García (0.12) | 0.02 |
| Newcastle United | Premier League | 157 | 9 (9) | 7 (8) | 0.66 (0.73) | Moussa Sissoko, Ayoze Pérez Gutiérrez | Moussa Sissoko (0.13) | 0.00 |
| Norwich City | Premier League | 185 | 9 (10) | 8 (8) | 0.67 (0.68) | Robert Brady, Jonathan Howson | Robert Brady (0.12) | 0.00 |
| Southampton | Premier League | 247 | 10 (9) | 9 (8) | 0.68 (0.62) | Sadio Mané, Dušan Tadić | José Miguel da Rocha Fonte (0.11) | 0.01 |
| Stoke City | Premier League | 174 | 9 (11) | 8 (10) | 0.71 (0.66) | Glen Johnson, Marko Arnautović | Marko Arnautović (0.12) | 0.01 |
| Sunderland | Premier League | 178 | 10 (11) | 9 (10) | 0.59 (0.68) | Yann Gérard M''Vila, Jermain Defoe | Yann Gérard M''Vila (0.11) | 0.00 |
| Swansea City | Premier League | 187 | 9 (9) | 8 (8) | 0.73 (0.78) | Jonjo Shelvey, André Ayew Pelé | Jonjo Shelvey (0.12) | 0.00 |
| Tottenham Hotspur | Premier League | 245 | 10 (8) | 8 (8) | 0.69 (0.74) | Christian Dannemann Eriksen, Harry Kane | Bamidele Alli (0.12) | 0.00 |
| Watford | Premier League | 189 | 7 (9) | 7 (8) | 0.74 (0.80) | José Manuel Jurado Marín, Odion Jude Ighalo | Allan Romeo Nyom (0.14) | 0.00 |
| West Bromwich Albion | Premier League | 148 | 10 (9) | 9 (9) | 0.63 (0.67) | Chris Brunt, José Salomón Rondón Giménez | James McClean (0.11) | 0.00 |
| West Ham United | Premier League | 213 | 10 (9) | 10 (9) | 0.61 (0.68) | Dimitri Payet, Cheikhou Kouyaté | Mark Noble (0.10) | 0.06 |
| AC Milan | Serie A | 244 | 10 (10) | 10 (9) | 0.70 (0.71) | Giacomo Bonaventura, Carlos Arturo Bacca Ahumada | Giacomo Bonaventura (0.10) | 0.03 |
| AS Roma | Serie A | 226 | 8 (8) | 8 (7) | 0.57 (0.71) | Miralem Pjanić, Edin Džeko | Miralem Pjanić (0.12) | 0.00 |
| Atalanta | Serie A | 209 | 7 (9) | 7 (9) | 0.85 (0.78) | Alejandro Darío Gómez, Maximiliano Nicol Moralez | Alejandro Darío Gómez (0.14) | 0.01 |
| Bologna | Serie A | 156 | 9 (9) | 9 (9) | 0.67 (0.66) | Emanuele Giaccherini, Mattia Destro | Adam Masina (0.07) | 0.00 |
| Carpi | Serie A | 200 | 12 (11) | 11 (10) | 0.55 (0.67) | Gaetano Letizia, Ryder Matos Santos | Ryder Matos Santos (0.09) | 0.06 |
| Chievo | Serie A | 194 | 9 (11) | 8 (10) | 0.73 (0.58) | Valter Birsa, Alberto Paloschi | Valter Birsa (0.12) | 0.01 |
| Empoli | Serie A | 229 | 8 (8) | 8 (7) | 0.75 (0.75) | Riccardo Saponara, Massimo Maccarone | Mário Rui Silva Duarte (0.12) | 0.00 |
| Fiorentina | Serie A | 242 | 11 (11) | 9 (10) | 0.69 (0.58) | Borja Valero Iglesias, Nikola Kalinić | Matías Vecino Falero (0.11) | 0.01 |
| Frosinone | Serie A | 206 | 12 (11) | 10 (11) | 0.70 (0.70) | Danilo Soddimo, Federico Dionisi | Daniel Pavlovic (0.09) | 0.00 |
| Genoa | Serie A | 207 | 11 (9) | 10 (9) | 0.60 (0.61) | Tomás Eduardo Rincón Hernández, Leonardo Pavoletti | Alberto Facundo Costa (0.10) | 0.01 |
| Hellas Verona | Serie A | 191 | 11 (12) | 10 (10) | 0.64 (0.59) | Federico Viviani, Luca Toni | Federico Viviani (0.10) | 0.02 |
| Inter Milan | Serie A | 223 | 11 (9) | 9 (7) | 0.68 (0.72) | Stevan Jovetić, Mauro Emanuel Icardi Rivero | Gary Alexis Medel Soto (0.07) | 0.00 |
| Juventus | Serie A | 259 | 10 (10) | 9 (8) | 0.74 (0.77) | Paul Pogba, Paulo Bruno Exequiel Dybala | Paul Pogba (0.11) | 0.00 |
| Lazio | Serie A | 215 | 10 (11) | 8 (10) | 0.55 (0.61) | Antonio Candreva, Keita Baldé Diao | Antonio Candreva (0.12) | 0.03 |
| Napoli | Serie A | 289 | 9 (9) | 8 (8) | 0.78 (0.75) | Marek Hamšík, Gonzalo Gerardo Higuaín | Jorge Luiz Frello Filho (0.12) | 0.00 |
| Palermo | Serie A | 209 | 9 (9) | 8 (9) | 0.75 (0.71) | Franco Damián Vázquez, Achraf Lazaar | Franco Damián Vázquez (0.12) | 0.00 |
| Sampdoria | Serie A | 170 | 8 (8) | 8 (7) | 0.72 (0.65) | Roberto Soriano, Eder Citadin Martins | Fernando Lucas Martins (0.12) | 0.00 |
| Sassuolo | Serie A | 201 | 9 (8) | 9 (8) | 0.57 (0.70) | Nicola Sansone, Gregoire Defrel | Domenico Berardi (0.11) | 0.03 |
| Torino | Serie A | 208 | 11 (12) | 9 (11) | 0.64 (0.64) | Fabio Quagliarella, Andrea Belotti | Cesare Bovo (0.10) | 0.00 |
| Udinese | Serie A | 212 | 9 (9) | 9 (9) | 0.71 (0.67) | Francesco Lodi, Cyril Théréau | Francesco Lodi (0.11) | 0.01 |

## League medians (training half)

| League | `tau` | `nu` | `cov(2)` |
| --- | --- | --- | --- |
| La Liga | 9.5 | 8.5 | 0.71 |
| Ligue 1 | 10.0 | 9.0 | 0.71 |
| Premier League | 9.0 | 8.0 | 0.67 |
| Serie A | 9.5 | 9.0 | 0.69 |
