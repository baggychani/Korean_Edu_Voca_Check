from __future__ import annotations

from kvocab_core.schemas import IssueStatus, Strictness
from kvocab_core.unknown_risk import classify_unknown


def test_jeonghap_is_unknown_without_heuristic_tier():
    status, _, reason, _ = classify_unknown("정합적")
    assert status == IssueStatus.unknown
    assert reason == "교재에 없는 어휘"


def test_unknown_has_no_heuristic_suggestions():
    status, _, _, suggestions = classify_unknown("윤슬")
    assert status == IssueStatus.unknown
    assert suggestions == []


def test_strictness_no_longer_changes_unknown_status():
    lo, _, _, _ = classify_unknown("상호작용", strictness=Strictness.loose)
    mid, _, _, _ = classify_unknown("상호작용", strictness=Strictness.balanced)
    hi, _, _, _ = classify_unknown("상호작용", strictness=Strictness.strict)
    assert lo == mid == hi == IssueStatus.unknown


def test_no_numeric_score_in_reason():
    _, _, reason, _ = classify_unknown("국제화하다")
    assert "위험 점수" not in reason


def test_english_is_neutral_unknown():
    status, _, reason, _ = classify_unknown("email")
    assert status == IssueStatus.unknown
    assert reason == "교재에 없는 어휘"
