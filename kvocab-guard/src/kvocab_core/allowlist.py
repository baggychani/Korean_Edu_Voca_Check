from __future__ import annotations

from sqlalchemy.orm import Session

from kvocab_core.models import CustomAllowlist
from kvocab_core.normalization import normalize_key

# 서울대 한국어 교재 고정 등장인물 — 기본 허용
DEFAULT_CHARACTER_NAMES: tuple[str, ...] = (
    "테오",
    "마리",
    "나나",
    "엥흐",
    "크리스",
    "소날",
    "제니",
    "김민우",
    "닛쿤",
    "이유진",
    "하이",
    "아야나",
    "안나",
    "다니엘",
    "에릭",
    "자밀라",
)

_DEFAULT_ALLOWLIST_NOTE = "교재 고정 등장인물"


def _default_allowlist_norms() -> set[str]:
    return {normalize_key(name) for name in DEFAULT_CHARACTER_NAMES if normalize_key(name)}


def is_protected_allowlist_norm(normalized_text: str) -> bool:
    return normalized_text in _default_allowlist_norms()


def get_allowlist_set(session: Session) -> set[str]:
    rows = session.query(CustomAllowlist.normalized_text).all()
    return {r[0] for r in rows} | _default_allowlist_norms()


def add_allowlist_item(
    session: Session,
    text: str,
    allow_type: str = "global",
    note: str | None = None,
) -> CustomAllowlist:
    norm = normalize_key(text)
    existing = (
        session.query(CustomAllowlist).filter(CustomAllowlist.normalized_text == norm).one_or_none()
    )
    if existing:
        return existing
    item = CustomAllowlist(
        text=text.strip(),
        normalized_text=norm,
        allow_type=allow_type,
        note=note,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_allowlist_item(session: Session, item_id: int) -> bool:
    item = session.get(CustomAllowlist, item_id)
    if not item:
        return False
    if is_protected_allowlist_norm(item.normalized_text):
        return False
    session.delete(item)
    session.commit()
    return True


def list_allowlist(session: Session) -> list[CustomAllowlist]:
    return session.query(CustomAllowlist).order_by(CustomAllowlist.id).all()


def ensure_default_allowlist(session: Session, *, commit: bool = True) -> int:
    """교재 고정 등장인물을 DB 허용 목록에 넣는다 (이미 있으면 건너뜀)."""
    added = 0
    for name in DEFAULT_CHARACTER_NAMES:
        norm = normalize_key(name)
        if not norm:
            continue
        existing = (
            session.query(CustomAllowlist)
            .filter(CustomAllowlist.normalized_text == norm)
            .one_or_none()
        )
        if existing:
            continue
        session.add(
            CustomAllowlist(
                text=name,
                normalized_text=norm,
                allow_type="global",
                note=_DEFAULT_ALLOWLIST_NOTE,
            )
        )
        added += 1
    if added and commit:
        session.commit()
    return added
