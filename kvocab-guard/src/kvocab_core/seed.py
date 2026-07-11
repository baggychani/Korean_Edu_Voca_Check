from __future__ import annotations

import hashlib
import json
from pathlib import Path

from sqlalchemy.orm import Session

from kvocab_core.allowlist import ensure_default_allowlist
from kvocab_core.config import DEFAULT_SEED_XLSX, LEVEL_META, LEVEL_ORDER, compute_order_index
from kvocab_core.database import reset_db
from kvocab_core.level_map_data import LEVEL_LESSONS
from kvocab_core.models import AppMeta, Lesson, Level
from kvocab_core.tools.import_xlsx import import_vocabulary_xlsx


def seed_levels_and_lessons(
    session: Session,
    level_code: str = "2A",
    *,
    commit: bool = True,
) -> None:
    meta = LEVEL_META.get(level_code)
    lessons = LEVEL_LESSONS.get(level_code)
    if not meta or not lessons:
        raise ValueError(f"No metadata for level {level_code}")

    level_order = LEVEL_ORDER[level_code]
    existing = session.get(Level, level_code)
    if existing:
        session.delete(existing)
        session.flush()

    session.add(
        Level(
            level=level_code,
            series=str(meta["series"]),
            title_ko=str(meta["title_ko"]),
            title_en=str(meta["title_en"]),
            level_order=level_order,
            sort_order=int(meta.get("sort_order", 0)),
        )
    )

    session.query(Lesson).filter(Lesson.level == level_code).delete()
    session.flush()

    for entry in lessons:
        oi = compute_order_index(level_code, entry["unit_no"], entry["lesson_no"])
        session.add(
            Lesson(
                level=level_code,
                lesson=entry["lesson"],
                unit_no=entry["unit_no"],
                lesson_no=entry["lesson_no"],
                unit_topic=entry["unit_topic"],
                unit_title=entry["unit_title"],
                page_start=entry["page_start"],
                page_end=entry["page_end"],
                order_index=oi,
            )
        )
    if commit:
        session.commit()


def seed_all_levels(session: Session, *, commit: bool = True) -> None:
    for level_code in LEVEL_LESSONS:
        if level_code in LEVEL_META:
            seed_levels_and_lessons(session, level_code, commit=False)
    if commit:
        session.commit()


def page_to_lesson(session: Session, level: str, page: int) -> Lesson | None:
    lessons = (
        session.query(Lesson)
        .filter(Lesson.level == level, Lesson.page_start <= page, Lesson.page_end >= page)
        .all()
    )
    return lessons[0] if lessons else None


SEED_FINGERPRINT_KEY = "seed_fingerprint"


def current_seed_fingerprint(xlsx_path: Path | None = None) -> str:
    path = xlsx_path or DEFAULT_SEED_XLSX
    h = hashlib.sha256()
    h.update(path.read_bytes())
    h.update(json.dumps(LEVEL_META, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    h.update(json.dumps(LEVEL_LESSONS, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    return h.hexdigest()


def get_seed_fingerprint(session: Session) -> str | None:
    row = session.get(AppMeta, SEED_FINGERPRINT_KEY)
    return row.value if row else None


def is_seed_current(session: Session, xlsx_path: Path | None = None) -> bool:
    return get_seed_fingerprint(session) == current_seed_fingerprint(xlsx_path)


def set_seed_fingerprint(session: Session, fingerprint: str, *, commit: bool = True) -> None:
    row = session.get(AppMeta, SEED_FINGERPRINT_KEY)
    if row:
        row.value = fingerprint
    else:
        session.add(AppMeta(key=SEED_FINGERPRINT_KEY, value=fingerprint))
    if commit:
        session.commit()


def full_seed(
    session: Session,
    xlsx_path: Path | None = None,
    *,
    preserve_allowlist: bool = True,
) -> dict:
    path = xlsx_path or DEFAULT_SEED_XLSX
    fingerprint = current_seed_fingerprint(path)
    try:
        reset_db(session, preserve_allowlist=preserve_allowlist, commit=False)
        seed_all_levels(session, commit=False)
        stats = import_vocabulary_xlsx(session, path, commit=False)
        ensure_default_allowlist(session, commit=False)
        set_seed_fingerprint(session, fingerprint, commit=False)
        stats["seed_fingerprint"] = fingerprint[:12]
        session.commit()
        return stats
    except Exception:
        session.rollback()
        raise


def main() -> None:
    from kvocab_core.database import init_db

    factory = init_db()
    with factory() as session:
        stats = full_seed(session)
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
