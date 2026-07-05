from __future__ import annotations

"""Internal status codes and Korean UI labels."""

STATUS_LABELS_KO: dict[str, str] = {
    "allowed": "사용 가능",
    "before_introduced": "아직 이릅니다",
    "unknown_high": "교재 외 · 난이도 높음",
    "unknown_medium": "교재 외 · 검토 필요",
    "unknown_low": "교재 외 · 참고",
    "custom_allowed": "허용 목록",
    "ignored_nnp": "표시하지 않음",
    "ignored_pattern": "표시하지 않음",
}

REVIEW_STATUS_LABELS_KO: dict[str, str] = {
    "approved": "확정",
    "manually_reviewed": "수동 검토 완료",
    "draft_ocr_needs_manual_review": "검토 중",
    "unmapped": "매핑 불가",
    "rejected": "제외",
}

SOURCE_TYPE_LABELS_KO: dict[str, str] = {
    "glossary_index": "색인",
    "glossary_index_ocr": "색인 OCR",
    "vocab_box": "어휘 상자",
    "grammar_box": "문법 상자",
    "expression_box": "표현 상자",
    "custom": "사용자 추가",
}


def status_label_ko(code: str) -> str:
    return STATUS_LABELS_KO.get(code, code)


def review_label_ko(code: str) -> str:
    return REVIEW_STATUS_LABELS_KO.get(code, code)


def source_label_ko(code: str) -> str:
    return SOURCE_TYPE_LABELS_KO.get(code, code)
