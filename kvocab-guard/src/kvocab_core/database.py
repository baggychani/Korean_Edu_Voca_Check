from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from kvocab_core.config import DEFAULT_DB_PATH
from kvocab_core.models import (
    Base,
    CustomAllowlist,
    Lesson,
    Level,
    Lexeme,
    Occurrence,
    SurfaceForm,
    UnmappedStaging,
)


def get_engine(db_path: Path | str | None = None):
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{path}", echo=False)


def get_session_factory(db_path: Path | None = None) -> sessionmaker[Session]:
    engine = get_engine(db_path)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db(db_path: Path | None = None) -> sessionmaker[Session]:
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_counts(session: Session) -> dict[str, int]:
    def _count(model) -> int:
        return session.scalar(select(func.count()).select_from(model)) or 0

    return {
        "levels": _count(Level),
        "lessons": _count(Lesson),
        "lexemes": _count(Lexeme),
        "occurrences": _count(Occurrence),
        "surface_forms": _count(SurfaceForm),
        "allowlist": _count(CustomAllowlist),
        "unmapped": _count(UnmappedStaging),
    }


def reset_db(session: Session) -> None:
    for model in (
        SurfaceForm,
        Occurrence,
        Lexeme,
        Lesson,
        Level,
        CustomAllowlist,
        UnmappedStaging,
    ):
        session.query(model).delete()
    session.commit()
