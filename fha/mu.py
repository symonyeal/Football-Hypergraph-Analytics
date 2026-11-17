"""The chance measure and its functionals, null models and resampling (docs/REVIEW.md 4.2-4.4).

A window's chances G define the empirical chance measure mu(A) = share of xG from chances whose group is A. Every
statistic here is a functional of mu; d, phi and D_q depend on it only through one-player marginals, while c, c(b),
tau_alpha and o see which players share chances.

Legend:
    G      chances, list of (A, w): A frozenset of players (any hashable ids), w > 0 its xG
    S      player set; b budget |S|; alpha share in (0, 1]
    R      stratum label of each member of each group, list of dicts {player: label} parallel to G
    g      numpy Generator
"""

from collections import Counter
from itertools import combinations

import numpy as np
from scipy.optimize import LinearConstraint, milp

from fha import attack


def d(G):
    """Involvement share d_v = mu{A : v in A}."""
    W = sum(w for _, w in G)
    out = Counter()
    for A, w in G:
        for v in A:
            out[v] += w / W
    return dict(out)


def phi(G):
    """Shapley value of the coverage game: phi_v = sum_{A ni v} mu(A)/|A|; sums to 1."""
    W = sum(w for _, w in G)
    out = Counter()
    for A, w in G:
        for v in A:
            out[v] += w / (W * len(A))
    return dict(out)


def hill(p, q):
    """Hill number D_q of shares p: (sum p^q)^(1/(1-q)); D_1 = exp(entropy); D_0 counts the support."""
    p = np.array([x for x in p if x > 0])
    p = p / p.sum()
    return float(np.exp(-(p * np.log(p)).sum())) if q == 1 else float((p ** q).sum() ** (1 / (1 - q)))


def c(S, G):
    """Coverage c(S) = mu{A : A meets S}."""
    S = set(S)
    return sum(w for A, w in G if A & S) / sum(w for _, w in G)


def index(G):
    """Players 0..n-1 (sorted ids), groups as index sets, weights."""
    ids = sorted({v for A, _ in G for v in A})
    ix = {v: i for i, v in enumerate(ids)}
    return ids, [{ix[v] for v in A} for A, _ in G], [w for _, w in G]


def cb(G, b):
    """Concentration curve c(b) = max_{|S| = b} c(S), exact (HiGHS ILP); returns (share, S)."""
    ids, F, w = index(G)
    if b >= len(ids):
        return 1.0, tuple(ids)
    s, T = attack.cov(F, w, len(ids), b)
    return s, tuple(ids[i] for i in T)


def tau_a(G, alpha):
    """Partial transversal number tau_alpha = min{b : c(b) >= alpha}, exact by one ILP:
    min sum x  s.t.  sum_i w_i z_i >= alpha W,  z_i <= sum_{v in A_i} x_v,  x, z binary."""
    ids, F, w = index(G)
    n, m = len(ids), len(F)
    A = attack.M(F, n)
    w = np.asarray(w, float)
    hit = LinearConstraint(np.hstack([-A, np.eye(m)]), -np.inf, 0)
    mass = LinearConstraint(np.concatenate([np.zeros(n), w])[None, :], alpha * w.sum() * (1 - 1e-12), np.inf)
    r = milp(np.concatenate([np.ones(n), np.zeros(m)]), constraints=[hit, mass], integrality=1, bounds=(0, 1))
    if r.status != 0:
        raise RuntimeError(f"tau_a: HiGHS status {r.status}")
    return int(round(r.fun))


def greedy(G, b):
    """Greedy maximum coverage: b players, each adding the most coverage (ties: smallest id); within 1 - 1/e of c(b)."""
    V = {v for A, _ in G for v in A}
    S = []
    for _ in range(min(b, len(V))):
        S.append(max(sorted(V - set(S)), key=lambda v: c(S + [v], G)))
    return S


def o(S, G):
    """Overlap among S: 1 - c(S) / sum_{v in S} d_v; 0 when S's members never share a chance."""
    dv = d(G)
    return 1 - c(S, G) / sum(dv.get(v, 0) for v in S)


def rarefy(G, m, f, r, g):
    """Mean of statistic f over r subsamples of m chances drawn without replacement: f at a common exposure."""
    return float(np.mean([f([G[i] for i in g.choice(len(G), m, replace=False)]) for _ in range(r)]))


def boot(Gm, f, B, g):
    """Within-team standard error of f: chances grouped by match (list of per-match chance lists), matches resampled."""
    k = len(Gm)
    return float(np.std([f([x for i in g.integers(0, k, k) for x in Gm[i]]) for _ in range(B)], ddof=1))


def redeal(G, g, R=None):
    """Null N0 (R None) or N1 (R strata): every player keeps their number of chances within each stratum and every
    chance keeps its size, stratum slots and xG; memberships are re-dealt (stub matching), and groups that repeat a
    player are repaired by swaps with a random member of the same stratum."""
    E = [list(A) for A, _ in G]
    L = np.array([R[i][v] if R else 0 for i, e in enumerate(E) for v in e])
    stubs = np.array([v for e in E for v in e], dtype=object)
    cut = np.cumsum([len(e) for e in E])
    lo = np.concatenate([[0], cut[:-1]])
    for _ in range(200):
        for s in sorted(set(L.tolist())):
            ix = np.flatnonzero(L == s)
            sub = stubs[ix]
            g.shuffle(sub)
            stubs[ix] = sub
        P = [list(stubs[a:b]) for a, b in zip(lo, cut)]
        for _ in range(20000):
            bad = [i for i, e in enumerate(P) if len(set(e)) < len(e)]
            if not bad:
                return [(frozenset(e), w) for e, (_, w) in zip(P, G)]
            i = bad[0]
            while True:   # draw order j, a, b matches fha.audit's original N0, so its figures reproduce
                j = int(g.integers(len(P)))
                a, b = int(g.integers(len(P[i]))), int(g.integers(len(P[j])))
                if L[lo[j] + b] == L[lo[i] + a]:
                    break
            P[i][a], P[j][b] = P[j][b], P[i][a]
    raise RuntimeError("redeal: no simple re-deal found")


def fit3(G, tol=1e-8, it=5000):
    """Log-linear model with no three-way interaction for the groups of three in G: p(T) proportional to
    prod_{uv in T} theta_uv over triples whose three pairs all occur, fitted by generalised iterative scaling so that
    expected pair counts match the observed ones (Bishop, Fienberg and Holland 1975). Returns (triples, p)."""
    E3 = [sorted(A, key=str) for A, _ in G if len(A) == 3]
    n = Counter(frozenset(q) for e in E3 for q in combinations(e, 2))
    V = sorted({v for q in n for v in q}, key=str)
    T = [t for t in combinations(V, 3) if all(frozenset(q) in n for q in combinations(t, 2))]
    P = sorted(n, key=lambda q: sorted(q, key=str))
    pi = {q: k for k, q in enumerate(P)}
    K = np.array([[pi[frozenset(q)] for q in combinations(t, 2)] for t in T])
    y = np.array([n[q] for q in P], float)
    N = len(E3)
    th = np.ones(len(P))
    for _ in range(it):
        p = th[K].prod(axis=1)
        p /= p.sum()
        e = np.bincount(K.ravel(), weights=np.repeat(N * p, 3), minlength=len(P))
        if np.abs(e - y).max() < tol * N:
            break
        th *= (y / e) ** (1 / 3)
    return T, p


def pairwise(G, g):
    """Null N2: the groups of three are redrawn from fit3(G), the pairwise model of their co-involvement; smaller groups
    and every xG are kept, the xG of the groups of three permuted among the new triples."""
    I3 = [i for i, (A, _) in enumerate(G) if len(A) == 3]
    if not I3:
        return list(G)
    T, p = fit3(G)
    draw = g.choice(len(T), len(I3), p=p)
    w3 = g.permutation([G[i][1] for i in I3])
    return [x for x in G if len(x[0]) != 3] + [(frozenset(T[k]), w) for k, w in zip(draw, w3)]


def excess(x, null, F, r, g):
    """For each statistic f in F: observed f(x), mean and sd over r draws of null(x, g) (shared by all f), and the
    standardised excess z = (observed - mean) / sd."""
    N = [null(x, g) for _ in range(r)]
    out = {}
    for k, f in F.items():
        v = np.array([f(y) for y in N], float)
        y, sd = f(x), float(v.std(ddof=1))
        out[k] = {"obs": y, "mean": float(v.mean()), "sd": sd, "z": (y - v.mean()) / sd if sd > 0 else 0.0}
    return out


def top(G, b):
    """The b most involved players (largest d_v; ties by id)."""
    return [v for v, _ in sorted(d(G).items(), key=lambda kv: (-kv[1], str(kv[0])))[:b]]


def icc(x, y):
    """ICC(2,1) of two measurements per unit: two-way random effects, absolute agreement (Shrout and Fleiss 1979)."""
    X = np.column_stack([x, y]).astype(float)
    n, k = X.shape
    gm = X.mean()
    msr = k * ((X.mean(axis=1) - gm) ** 2).sum() / (n - 1)
    msc = n * ((X.mean(axis=0) - gm) ** 2).sum() / (k - 1)
    mse = ((X - X.mean(axis=1, keepdims=True) - X.mean(axis=0) + gm) ** 2).sum() / ((n - 1) * (k - 1))
    return float((msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n))


def brown(r, k):
    """Spearman-Brown: reliability of a measure k times as long as one of reliability r."""
    return k * r / (1 + (k - 1) * r)


def pool(y, v):
    """Random-effects mean of estimates y with variances v (DerSimonian and Laird): (mean, se, tau^2)."""
    y, v = np.asarray(y, float), np.asarray(v, float)
    w = 1 / v
    m0 = (w * y).sum() / w.sum()
    Q = (w * (y - m0) ** 2).sum()
    t2 = max(0.0, (Q - (len(y) - 1)) / (w.sum() - (w ** 2).sum() / w.sum()))
    w = 1 / (v + t2)
    return float((w * y).sum() / w.sum()), float(np.sqrt(1 / w.sum())), float(t2)
