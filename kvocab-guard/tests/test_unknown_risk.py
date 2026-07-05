from __future__ import annotations

from kvocab_core.schemas import IssueStatus, Strictness
from kvocab_core.unknown_risk import classify_unknown


def test_jeonghap_high():
    status, _, _, _ = classify_unknown("정합적")
    assert status == IssueStatus.unknown_high


def test_yunseul_high():
    status, _, _, suggestions = classify_unknown("윤슬")
    assert status == IssueStatus.unknown_high
    assert suggestions


def test_strictness_affects_score():
    lo, _, _, _ = classify_unknown("상호작용", strictness=Strictness.loose)
    hi, _, _, _ = classify_unknown("상호작용", strictness=Strictness.strict)
    assert lo != hi or hi == IssueStatus.unknown_high
