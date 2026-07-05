from __future__ import annotations

import re
import unicodedata

_STRIP_FOR_KEY = re.compile(r"[\s\.,;:!?\"'()\[\]{}·…—–\-_/\\]+")
_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_DATE_RE = re.compile(r"\d{4}[-/.년]\s*\d{1,2}[-/.월]\s*\d{1,2}일?|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}")
_TIME_RE = re.compile(r"\d{1,2}:\d{2}(:\d{2})?|\d{1,2}시(\s*\d{1,2}분)?")
_NUMBER_RE = re.compile(r"^[+-]?\d+(?:[.,]\d+)?%?$")
_ENGLISH_RE = re.compile(r"^[A-Za-z][A-Za-z0-9\s\-']*$")
_HANGUL_RE = re.compile(r"[가-힣]")
_COMMON_SHORT = frozenset(
    {"네", "예", "아니요", "음", "어", "네네", "감사", "안녕", "저", "나", "우리"}
)


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "")
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_key(text: str) -> str:
    text = normalize_text(text)
    text = _STRIP_FOR_KEY.sub("", text)
    return text


def is_url(text: str) -> bool:
    return bool(_URL_RE.search(text))


def is_email(text: str) -> bool:
    return bool(_EMAIL_RE.fullmatch(text.strip()))


def is_date(text: str) -> bool:
    return bool(_DATE_RE.search(text))


def is_time(text: str) -> bool:
    return bool(_TIME_RE.search(text))


def is_number(text: str) -> bool:
    return bool(_NUMBER_RE.match(text.strip()))


def is_english(text: str) -> bool:
    t = text.strip()
    return bool(t) and bool(_ENGLISH_RE.match(t))


def is_ignored_pattern(text: str) -> bool:
    t = text.strip()
    if not t:
        return True
    return is_url(t) or is_email(t) or is_date(t) or is_time(t) or is_number(t)


def count_korean_syllables(text: str) -> int:
    return len(_HANGUL_RE.findall(text))


def is_very_short_common(text: str) -> bool:
    return normalize_key(text) in _COMMON_SHORT


def lemma_gana_sort_key(lemma: str) -> str:
    """괄호로 시작하는 표제어는 닫는 괄호 뒤 본표제어 기준으로 정렬."""
    text = normalize_text(lemma)
    if text.startswith("("):
        close = text.find(")")
        if close != -1:
            tail = text[close + 1 :].strip()
            if tail:
                return tail
    return text
