from __future__ import annotations

from kvocab_core.normalization import (
    count_korean_syllables,
    is_english,
    is_number,
    is_very_short_common,
    normalize_key,
)
from kvocab_core.schemas import IssueStatus, Severity, Strictness

_SINO_SUFFIXES = (
    "적",
    "성",
    "화",
    "론",
    "주의",
    "체계",
    "정합",
    "내재",
    "상호",
    "인식",
    "구조",
)

_HARDCODED: dict[str, tuple[IssueStatus, list[str]]] = {
    "정합적": (IssueStatus.unknown_high, ["잘 맞는", "앞뒤가 맞는"]),
    "정합적인": (IssueStatus.unknown_high, ["잘 맞는", "앞뒤가 맞는"]),
    "윤슬": (IssueStatus.unknown_high, ["물 위에 빛이 반짝이는 것"]),
    "내재화": (IssueStatus.unknown_high, []),
    "상호작용": (IssueStatus.unknown_medium, []),
}


def classify_unknown(
    token: str,
    *,
    strictness: Strictness = Strictness.balanced,
) -> tuple[IssueStatus, Severity, str, list[str]]:
    norm = normalize_key(token)
    if norm in _HARDCODED:
        status, suggestions = _HARDCODED[norm]
        if norm == "상호작용" and strictness == Strictness.strict:
            status = IssueStatus.unknown_high
        sev = Severity.high if status == IssueStatus.unknown_high else Severity.medium
        return status, sev, "하드코딩 규칙", suggestions

    score = 35
    if any(s in token for s in _SINO_SUFFIXES):
        score += 30
    if count_korean_syllables(token) >= 4 and not token.endswith(("하다", "되다", "이다")):
        score += 20
    if token.endswith("하다"):
        score += 15
    if strictness == Strictness.strict:
        score += 20
    elif strictness == Strictness.loose:
        score -= 20

    if is_english(token) or is_number(token):
        score -= 30
    if is_very_short_common(token):
        score -= 30

    if score >= 70:
        return IssueStatus.unknown_high, Severity.high, f"위험 점수 {score}", []
    if score >= 45:
        return IssueStatus.unknown_medium, Severity.medium, f"위험 점수 {score}", []
    return IssueStatus.unknown_low, Severity.low, f"위험 점수 {score}", []
