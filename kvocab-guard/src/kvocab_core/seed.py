from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from kvocab_core.config import (
    DEFAULT_SEED_XLSX,
    LEVEL_META,
    LEVEL_ORDER,
    compute_order_index,
)
from kvocab_core.database import reset_db
from kvocab_core.level_map_data import LEVEL_LESSONS
from kvocab_core.models import Lesson, Level
from kvocab_core.tools.import_xlsx import import_vocabulary_xlsx


def seed_levels_and_lessons(session: Session, level_code: str = "2A") -> None:
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
    session.commit()


def seed_all_levels(session: Session) -> None:
    for level_code in LEVEL_LESSONS:
        if level_code in LEVEL_META:
            seed_levels_and_lessons(session, level_code)


def page_to_lesson(session: Session, level: str, page: int) -> Lesson | None:
    lessons = (
        session.query(Lesson)
        .filter(Lesson.level == level, Lesson.page_start <= page, Lesson.page_end >= page)
        .all()
    )
    return lessons[0] if lessons else None


def full_seed(session: Session, xlsx_path: Path | None = None) -> dict:
    reset_db(session)
    seed_all_levels(session)
    path = xlsx_path or DEFAULT_SEED_XLSX
    stats = import_vocabulary_xlsx(session, path)
    return stats


def main() -> None:
    from kvocab_core.database import init_db

    factory = init_db()
    with factory() as session:
        stats = full_seed(session)
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
