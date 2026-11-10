"""Attack structure of a family of attacking groups (docs/MODEL.md §2).

Legend:
    F   list of player sets, players 0..n-1        w   weight of each set (xG)
    n   players                                     b   budget of players
    x   fractional transversal, R^n, x >= 0         y   fractional matching, R^|F|, y >= 0
"""

import json
import os
import subprocess
from pathlib import Path

import numpy as np
from scipy.optimize import LinearConstraint, linprog, milp

TR = os.environ.get("FHA_TR") or str(Path(__file__).resolve().parents[1] / "target" / "release" / ("tr.exe" if os.name == "nt" else "tr"))


def M(F, n):
    """Edge-by-player incidence, |F| x n."""
    A = np.zeros((len(F), n))
    for i, e in enumerate(F):
        A[i, list(e)] = 1.0
    return A


def minimum(F, n):
    """Every minimum transversal of F, sorted; tau(F) is the length of each. Enumerated by MMCS (Rust `tr`)."""
    s = f"{n}\n" + "".join(" ".join(map(str, sorted(e))) + "\n" for e in F)
    for k in range(n + 1):
        out = subprocess.run([TR, "--k", str(k)], input=s, capture_output=True, text=True, check=True).stdout
        T = [tuple(t) for t in json.loads(out)["sets"]]
        if T:
            return T
    return []


def tau_star(F, n):
    """tau*(F) = nu*(F) by LP duality; returns (value, x, y) after checking both certificates."""
    if not F:
        return 0.0, [0.0] * n, []
    A = M(F, n)
    r = linprog(np.ones(n), A_ub=-A, b_ub=-np.ones(len(F)), bounds=(0, None), method="highs")
    x, y = r.x, -r.ineqlin.marginals
    eps = 1e-7
    if not ((A @ x >= 1 - eps).all() and (A.T @ y <= 1 + eps).all() and (y >= -eps).all() and abs(x.sum() - y.sum()) < eps):
        raise RuntimeError(f"tau* certificate failed: status {r.status}")
    return float(r.fun), x.tolist(), y.tolist()


def nu(F, n):
    """nu(F): most pairwise disjoint sets; returns (value, indices of a maximum matching)."""
    if not F:
        return 0, []
    A = M(F, n)
    r = milp(-np.ones(len(F)), constraints=LinearConstraint(A.T, -np.inf, 1), integrality=1, bounds=(0, 1))
    if r.status != 0:
        raise RuntimeError(f"nu: HiGHS status {r.status}")
    I = [i for i, v in enumerate(r.x) if v > 0.5]
    if any(F[i] & F[j] for a, i in enumerate(I) for j in I[a + 1:]):
        raise RuntimeError("nu: chosen sets are not disjoint")
    return len(I), I


def covered(T, F, w):
    """Share of the weight of F carried by sets meeting T."""
    W = sum(w)
    return sum(wi for e, wi in zip(F, w) if e & set(T)) / W if W else 0.0


def cov(F, w, n, b):
    """Maximum coverage: the b players meeting the most weight of F (full family, exact ILP); returns (share, T)."""
    m = len(F)
    A = M(F, n)
    c = np.concatenate([np.zeros(n), -np.asarray(w, float)])
    hit = LinearConstraint(np.hstack([-A, np.eye(m)]), -np.inf, 0)
    size = LinearConstraint(np.concatenate([np.ones(n), np.zeros(m)])[None, :], b, b)
    r = milp(c, constraints=[hit, size], integrality=1, bounds=(0, 1))
    if r.status != 0:
        raise RuntimeError(f"cov: HiGHS status {r.status}")
    T = tuple(v for v in range(n) if r.x[v] > 0.5)
    return covered(T, F, w), T
