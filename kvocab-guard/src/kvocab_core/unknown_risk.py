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

# 교재 밖에서 특히 주의할 대표 예시 (점수 대신 고정 판정)
_HARDCODED: dict[str, tuple[IssueStatus, str, list[str]]] = {
    "정합적": (IssueStatus.unknown_high, "학술·추상 어휘", ["잘 맞는", "앞뒤가 맞는"]),
    "정합적인": (IssueStatus.unknown_high, "학술·추상 어휘", ["잘 맞는", "앞뒤가 맞는"]),
    "윤슬": (IssueStatus.unknown_high, "시·문학적 어휘", ["물 위에 빛이 반짝이는 것"]),
    "내재화": (IssueStatus.unknown_high, "학술·추상 어휘", []),
    "상호작용": (IssueStatus.unknown_medium, "복합 명사", []),
}

_TIER_ORDER = (
    IssueStatus.unknown_low,
    IssueStatus.unknown_medium,
    IssueStatus.unknown_high,
)

_SEVERITY = {
    IssueStatus.unknown_low: Severity.low,
    IssueStatus.unknown_medium: Severity.medium,
    IssueStatus.unknown_high: Severity.high,
}


def _apply_strictness(status: IssueStatus, strictness: Strictness) -> IssueStatus:
    idx = _TIER_ORDER.index(status)
    if strictness == Strictness.strict and idx < len(_TIER_ORDER) - 1:
        idx += 1
    elif strictness == Strictness.loose and idx > 0:
        idx -= 1
    return _TIER_ORDER[idx]


def _pack(status: IssueStatus, reason: str, suggestions: list[str] | None = None):
    return status, _SEVERITY[status], reason, suggestions or []


def classify_unknown(
    token: str,
    *,
    strictness: Strictness = Strictness.balanced,
) -> tuple[IssueStatus, Severity, str, list[str]]:
    norm = normalize_key(token)
    if norm in _HARDCODED:
        status, reason, suggestions = _HARDCODED[norm]
        status = _apply_strictness(status, strictness)
        return _pack(status, reason, suggestions)

    if is_english(token) or is_number(token):
        status = _apply_strictness(IssueStatus.unknown_low, strictness)
        return _pack(status, "외래어·숫자")

    if is_very_short_common(token):
        status = _apply_strictness(IssueStatus.unknown_low, strictness)
        return _pack(status, "흔한 짧은 표현")

    if any(s in token for s in _SINO_SUFFIXES):
        status = _apply_strictness(IssueStatus.unknown_high, strictness)
        return _pack(status, "한자어·학술어 형태")

    syllables = count_korean_syllables(token)
    if syllables >= 4 and not token.endswith(("하다", "되다", "이다")):
        status = _apply_strictness(IssueStatus.unknown_high, strictness)
        return _pack(status, "긴 어휘")

    if token.endswith("하다"):
        status = _apply_strictness(IssueStatus.unknown_medium, strictness)
        return _pack(status, "교재에 없는 동사")

    status = _apply_strictness(IssueStatus.unknown_medium, strictness)
    return _pack(status, "교재에 없는 어휘")
