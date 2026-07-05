from __future__ import annotations

import os
from pathlib import Path

# level code -> global learning order prefix
LEVEL_ORDER: dict[str, int] = {
    "1A": 101,
    "1B": 102,
    "2A": 201,
    "2B": 202,
    "3A": 301,
    "3B": 302,
    "4A": 401,
    "4B": 402,
    "5A": 501,
    "5B": 502,
    "6A": 601,
    "6B": 602,
}

LEVEL_META: dict[str, dict[str, str | int]] = {
    "2A": {
        "series": "서울대 한국어",
        "title_ko": "서울대 한국어 2A",
        "title_en": "SNU Korean 2A",
        "sort_order": 3,
    },
    "2B": {
        "series": "서울대 한국어",
        "title_ko": "서울대 한국어 2B",
        "title_en": "SNU Korean 2B",
        "sort_order": 4,
    },
    "3A": {
        "series": "서울대 한국어",
        "title_ko": "서울대 한국어 3A",
        "title_en": "SNU Korean 3A",
        "sort_order": 5,
    },
}

PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = PACKAGE_ROOT.parent
VOCABULARY_DIR = REPO_ROOT / "vocabulary"
TEXTBOOKS_DIR = REPO_ROOT / "textbooks"
WORD_DIR = REPO_ROOT / "Word"
DEFAULT_DATA_DIR = Path(os.environ.get("KVOCAB_DATA_DIR", PACKAGE_ROOT / "data"))
DEFAULT_DB_PATH = DEFAULT_DATA_DIR / "kvocab.db"

# 범용 시드 파일명 (레벨 무관). 없으면 구버전 파일명으로 fallback.
_SEED_CANDIDATES = (
    "vocabulary_database.xlsx",
    "snu_vocabulary_database.xlsx",
    "snu2a_level_mapped_vocabulary.xlsx",
)


def find_seed_xlsx() -> Path:
    seed_dir = DEFAULT_DATA_DIR / "seed"
    for name in _SEED_CANDIDATES:
        candidate = seed_dir / name
        if candidate.exists():
            return candidate
    return seed_dir / _SEED_CANDIDATES[0]


DEFAULT_SEED_XLSX = find_seed_xlsx()

# v1: include OCR draft rows in matching
INCLUDE_DRAFT_DATA = True

USABLE_REVIEW_STATUSES = frozenset(
    {"approved", "manually_reviewed", "draft_ocr_needs_manual_review"}
)

EXCLUDED_REVIEW_STATUSES = frozenset({"unmapped", "rejected"})


def compute_order_index(level: str, unit_no: int, lesson_no: int) -> int:
    level_order = LEVEL_ORDER[level]
    return level_order * 1000 + unit_no * 10 + lesson_no
