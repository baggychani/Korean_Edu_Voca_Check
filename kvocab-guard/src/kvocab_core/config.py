from __future__ import annotations

from pathlib import Path

from kvocab_core.runtime_paths import (
    bundled_data_dir,
    repo_root,
    writable_data_dir,
)

# =============================================================================
# App info & update
# =============================================================================
APP_VERSION = "0.0.0"
APP_TITLE = f"한국어교육 단어 검사기 {APP_VERSION}"

GITHUB_OWNER = "baggychani"
GITHUB_REPO = "Korean_Edu_Voca_Check"
GITHUB_RELEASE_URL = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases"
GITHUB_API_LATEST_RELEASE = (
    f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
)

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
    "1A": {
        "series": "서울대 한국어",
        "title_ko": "서울대 한국어 1A",
        "title_en": "SNU Korean 1A",
        "sort_order": 1,
    },
    "1B": {
        "series": "서울대 한국어",
        "title_ko": "서울대 한국어 1B",
        "title_en": "SNU Korean 1B",
        "sort_order": 2,
    },
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
    "3B": {
        "series": "서울대 한국어",
        "title_ko": "서울대 한국어 3B",
        "title_en": "SNU Korean 3B",
        "sort_order": 6,
    },
    "4A": {
        "series": "서울대 한국어",
        "title_ko": "서울대 한국어 4A",
        "title_en": "SNU Korean 4A",
        "sort_order": 7,
    },
    "4B": {
        "series": "서울대 한국어",
        "title_ko": "서울대 한국어 4B",
        "title_en": "SNU Korean 4B",
        "sort_order": 8,
    },
}

PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = repo_root()
VOCABULARY_DIR = REPO_ROOT / "vocabulary"
TEXTBOOKS_DIR = REPO_ROOT / "textbooks"
VOCA_PDF_IMAGE_DIR = REPO_ROOT / "voca_pdf_image"
COVERS_DIR = REPO_ROOT / "covers"
DEFAULT_DATA_DIR = bundled_data_dir()
DEFAULT_DB_PATH = writable_data_dir() / "kvocab.db"

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


def cover_image_path(level: str) -> Path | None:
    """Return ``covers/{level}.{ext}`` if present."""
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        candidate = COVERS_DIR / f"{level}{ext}"
        if candidate.exists():
            return candidate
    return None


def compute_order_index(level: str, unit_no: int, lesson_no: int) -> int:
    level_order = LEVEL_ORDER[level]
    return level_order * 1000 + unit_no * 10 + lesson_no
