"""Estimators and power simulations for the second-round hypotheses R1, R3, R4 and R5 (docs/REVIEW.md 4.4).

Legend:
    G      chances of one team window, list of (A, xG) as in fha.mu
    Q      completed passes of one team window, Counter {(passer, recipient): count}
    rows   R4 match rows, dicts: team, opp, home (0/1), y (open-play xG), a (sum of absent players' phi), C (team's c(2))
    g      numpy Generator
"""

from collections import Counter

import numpy as np
from sklearn.linear_model import PoissonRegressor

from fha import mu


def strength(Q):
    """Weighted degree in the completed-pass network: passes made plus passes received."""
    s = Counter()
    for (u, v), k in Q.items():
        s[u] += k
        s[v] += k
    return s


def ranked(score, b):
    """The b players with the largest score (ties: smaller id)."""
    return [v for v, _ in sorted(score.items(), key=lambda kv: (-kv[1], str(kv[0])))[:b]]


def select(G, Q, b):
    """R3 selection rules on a training window: each returns b players."""
    return {"exact": list(mu.cb(G, b)[1]), "greedy": mu.greedy(G, b), "involvement": ranked(mu.d(G), b),
            "shapley": ranked(mu.phi(G), b), "pass strength": ranked(strength(Q), b)}


def design(rows):
    """R4 design: team and opponent indicators, home, absent share a, and a x C; returns (X, y, columns)."""
    T = sorted({r["team"] for r in rows}, key=str)
    O = sorted({r["opp"] for r in rows}, key=str)
    it, io = {t: i for i, t in enumerate(T)}, {o: i for i, o in enumerate(O)}
    X = np.zeros((len(rows), len(T) + len(O) + 3))
    for i, r in enumerate(rows):
        X[i, it[r["team"]]] = 1
        X[i, len(T) + io[r["opp"]]] = 1
        X[i, -3:] = r["home"], r["a"], r["a"] * r["C"]
    return X, np.array([r["y"] for r in rows], float)


def fit4(rows):
    """R4: log E[y] = alpha_team + gamma_opp + eta home - beta a - delta C a (quasi-Poisson, unpenalised in effect).
    Returns (beta, delta, fitted means, Pearson dispersion)."""
    X, y = design(rows)
    m = PoissonRegressor(alpha=1e-8, max_iter=3000, tol=1e-10).fit(X, y)
    mu_ = m.predict(X)
    disp = float(((y - mu_) ** 2 / mu_).sum() / max(len(y) - X.shape[1] - 1, 1))
    return -float(m.coef_[-2]), -float(m.coef_[-1]), mu_, disp


def boot4(rows, B, g):
    """Percentile 95% intervals of (beta, delta), teams resampled with their matches (each copy its own team)."""
    by = {}
    for r in rows:
        by.setdefault(r["team"], []).append(r)
    T = sorted(by, key=str)
    v = []
    for _ in range(B):
        R = [{**r, "team": (k, r["team"])} for k, i in enumerate(g.integers(0, len(T), len(T))) for r in by[T[i]]]
        v.append(fit4(R)[:2])
    v = np.array(v)
    return [list(np.percentile(v[:, j], [2.5, 97.5])) for j in (0, 1)]


def power4(rows, betas, sims, g):
    """R4 power by simulation: outcomes drawn from the fitted model with the absence terms removed, times
    exp(-beta a), with gamma noise of the fitted dispersion; beta refitted each time. SE is the sd of the estimate
    under beta = 0; power is the share of |beta_hat| / SE > 1.96 at each planted beta."""
    b0, d0, m0, disp = fit4(rows)
    a = np.array([r["a"] for r in rows])
    C = np.array([r["C"] for r in rows])
    base = m0 * np.exp(b0 * a + d0 * C * a)
    est = {}
    for b in [0.0, *betas]:
        mean = base * np.exp(-b * a)
        est[b] = np.array([fit4([{**r, "y": y} for r, y in zip(rows, g.gamma(mean / disp, disp))])[0] for _ in range(sims)])
    se = float(est[0.0].std(ddof=1))
    return {"se": se, "dispersion": disp, "power": {b: float((np.abs(est[b]) / se > 1.96).mean()) for b in betas}}


def loo_r2(X, y):
    """Leave-one-out R^2 of least squares with intercept."""
    X = np.column_stack([np.ones(len(y)), X])
    e = []
    for i in range(len(y)):
        k = np.arange(len(y)) != i
        c, *_ = np.linalg.lstsq(X[k], y[k], rcond=None)
        e.append(y[i] - X[i] @ c)
    return float(1 - np.sum(np.square(e)) / np.sum((y - y.mean()) ** 2))


def icc_power(r, n, lo, sims, B, g):
    """R1 power: share of simulated studies of n units (two measurements, true ICC r, bivariate normal) whose
    percentile-bootstrap lower bound of ICC(2,1) exceeds lo."""
    S = np.array([[1, r], [r, 1]])
    hit = 0
    for _ in range(sims):
        x = g.multivariate_normal([0, 0], S, n)
        v = [mu.icc(*x[g.integers(0, n, n)].T) for _ in range(B)]
        hit += np.percentile(v, 2.5) > lo
    return hit / sims


def mde(se, n0, n1):
    """Smallest pooled effect detectable with 80% power at two-sided 5%, rescaling a standard error from n0 to n1 units."""
    return 2.80 * se * np.sqrt(n0 / n1)
