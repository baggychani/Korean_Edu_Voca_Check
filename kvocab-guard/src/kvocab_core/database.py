from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import Session, sessionmaker

from kvocab_core.config import DEFAULT_DB_PATH
from kvocab_core.models import (
    AppMeta,
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
    engine = create_engine(
        f"sqlite:///{path}",
        echo=False,
        connect_args={"timeout": 30},
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragmas(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

    return engine


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


def reset_db(
    session: Session,
    *,
    preserve_allowlist: bool = False,
    commit: bool = True,
) -> None:
    models = [
        SurfaceForm,
        Occurrence,
        Lexeme,
        Lesson,
        Level,
        UnmappedStaging,
        AppMeta,
    ]
    if not preserve_allowlist:
        models.append(CustomAllowlist)
    for model in models:
        session.query(model).delete()
    if commit:
        session.commit()
