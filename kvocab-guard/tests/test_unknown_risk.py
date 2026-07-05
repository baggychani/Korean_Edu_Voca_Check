from __future__ import annotations

from kvocab_core.schemas import IssueStatus, Strictness
from kvocab_core.unknown_risk import classify_unknown


def test_jeonghap_high():
    status, _, reason, _ = classify_unknown("정합적")
    assert status == IssueStatus.unknown_high
    assert "학술" in reason


def test_yunseul_high():
    status, _, _, suggestions = classify_unknown("윤슬")
    assert status == IssueStatus.unknown_high
    assert suggestions


def test_strictness_bumps_tier():
    lo, _, _, _ = classify_unknown("상호작용", strictness=Strictness.loose)
    mid, _, _, _ = classify_unknown("상호작용", strictness=Strictness.balanced)
    hi, _, _, _ = classify_unknown("상호작용", strictness=Strictness.strict)
    assert lo == IssueStatus.unknown_low
    assert mid == IssueStatus.unknown_medium
    assert hi == IssueStatus.unknown_high


def test_no_numeric_score_in_reason():
    _, _, reason, _ = classify_unknown("국제화하다")
    assert "위험 점수" not in reason


def test_english_is_low():
    status, _, reason, _ = classify_unknown("email")
    assert status == IssueStatus.unknown_low
    assert reason == "외래어·숫자"
