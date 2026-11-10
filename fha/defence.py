"""Shape of the visible outfield defenders at a pass (docs/MODEL.md §4).

Legend: P defender positions, k x 2, metres (x along the pitch, y across).
"""

import gudhi
import numpy as np
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.spatial import ConvexHull, Delaunay
from scipy.spatial.distance import pdist, squareform


def shape(P):
    """(width across, depth along, convex-hull area)."""
    return float(np.ptp(P[:, 1])), float(np.ptp(P[:, 0])), float(ConvexHull(P).volume)


def gap(P):
    """Longest edge of the Euclidean minimum spanning tree: the widest gap between neighbouring defenders."""
    return float(minimum_spanning_tree(squareform(pdist(P))).data.max())


def hole(P):
    """Largest circumradius of a Delaunay triangle whose circumcentre lies inside the hull, and that centre:
    the largest unguarded circle. (0, None) when no circumcentre lies inside."""
    D = Delaunay(P)
    r, o = 0.0, None
    for s in D.simplices:
        a, b, c = P[s]
        d = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
        u = np.array([
            (a @ a) * (b[1] - c[1]) + (b @ b) * (c[1] - a[1]) + (c @ c) * (a[1] - b[1]),
            (a @ a) * (c[0] - b[0]) + (b @ b) * (a[0] - c[0]) + (c @ c) * (b[0] - a[0]),
        ]) / d
        q = float(np.linalg.norm(u - a))
        if q > r and D.find_simplex(u, tol=1e-9) >= 0:
            r, o = q, u
    return r, o


def h1(P):
    """Longest H1 bar of the alpha filtration, in metres (GUDHI filtration values are squared radii)."""
    st = gudhi.AlphaComplex(points=P).create_simplex_tree()
    st.compute_persistence()
    bars = st.persistence_intervals_in_dimension(1)
    return float(max((np.sqrt(d) - np.sqrt(b) for b, d in bars), default=0.0))
