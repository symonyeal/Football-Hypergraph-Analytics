"""Verdict rules of docs/PROTOCOL.md."""

from fha.report import holm, three


def test_three_verdicts():
    assert three(0.05, 0.2, 0.02) == "supported"
    assert three(0.005, 0.015, 0.02) == "supported, below the margin"
    assert three(-0.2, -0.05, 0.02) == "reversed"
    assert three(-0.01, 0.015, 0.02) == "equivalent to none"
    assert three(-0.01, 0.05, 0.02) == "undetermined"


def test_holm_matches_hand_calculation():
    assert [round(x, 10) for x in holm([0.01, 0.04, 0.03])] == [0.03, 0.06, 0.06]
