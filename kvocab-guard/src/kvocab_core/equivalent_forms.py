from __future__ import annotations

from kvocab_core.normalization import normalize_key

# 교재 표제어를 늘리지 않고 입력·검색 단계에서만 동일하게 처리하는 표현.
_CANONICAL_BY_FORM: dict[str, str] = {
    "안녕": "안녕하세요",
}


def canonical_form(text: str) -> str | None:
    """Return the textbook lemma linked to ``text``, if one is configured."""
    return _CANONICAL_BY_FORM.get(normalize_key(text))


def equivalent_forms_for(canonical: str) -> list[str]:
    """Return non-textbook forms linked to a textbook lemma."""
    canonical_norm = normalize_key(canonical)
    return [form for form, target in _CANONICAL_BY_FORM.items() if target == canonical_norm]
