from __future__ import annotations

from sqlalchemy.orm import Session

from kvocab_core.models import CustomAllowlist
from kvocab_core.normalization import normalize_key


def get_allowlist_set(session: Session) -> set[str]:
    rows = session.query(CustomAllowlist.normalized_text).all()
    return {r[0] for r in rows}


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
    session.delete(item)
    session.commit()
    return True


def list_allowlist(session: Session) -> list[CustomAllowlist]:
    return session.query(CustomAllowlist).order_by(CustomAllowlist.id).all()
