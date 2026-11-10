"""Defensive-shape measures on point sets whose values are known by construction."""

from math import isclose, sqrt

import numpy as np

from fha.defence import gap, h1, hole, shape

SQUARE = np.array([[0, 0], [2, 0], [2, 2], [0, 2]], float)
EQUI = np.array([[0, 0], [2, 0], [1, sqrt(3)]], float)
OBTUSE = np.array([[0, 0], [4, 0], [2, 0.5]], float)


def test_gap_is_longest_mst_edge():
    assert isclose(gap(np.array([[0, 0], [3, 0], [3, 4]], float)), 4.0)
    assert isclose(gap(SQUARE), 2.0)


def test_hole_is_largest_inner_circumradius():
    r, u = hole(SQUARE)
    assert isclose(r, sqrt(2)) and np.allclose(u, [1, 1])
    assert isclose(hole(EQUI)[0], 2 / sqrt(3))
    # The obtuse triangle's circumcentre lies outside it: no hole inside the block.
    assert hole(OBTUSE)[0] == 0.0


def test_h1_longest_alpha_bar_in_metres():
    assert isclose(h1(SQUARE), sqrt(2) - 1, abs_tol=1e-9)
    assert isclose(h1(EQUI), 2 / sqrt(3) - 1, abs_tol=1e-9)
    assert h1(OBTUSE) == 0.0


def test_shape():
    w, d, a = shape(SQUARE)
    assert (w, d) == (2.0, 2.0) and isclose(a, 4.0)
