from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Level(Base):
    __tablename__ = "levels"

    level: Mapped[str] = mapped_column(String(8), primary_key=True)
    series: Mapped[str] = mapped_column(String(64))
    title_ko: Mapped[str] = mapped_column(String(128))
    title_en: Mapped[str] = mapped_column(String(128))
    level_order: Mapped[int] = mapped_column(Integer)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    lessons: Mapped[list[Lesson]] = relationship(back_populates="level_ref")


class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (UniqueConstraint("level", "lesson", name="uq_level_lesson"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    level: Mapped[str] = mapped_column(String(8), ForeignKey("levels.level"))
    lesson: Mapped[str] = mapped_column(String(16))
    unit_no: Mapped[int] = mapped_column(Integer)
    lesson_no: Mapped[int] = mapped_column(Integer)
    unit_topic: Mapped[str] = mapped_column(String(128))
    unit_title: Mapped[str] = mapped_column(String(256))
    page_start: Mapped[int] = mapped_column(Integer)
    page_end: Mapped[int] = mapped_column(Integer)
    order_index: Mapped[int] = mapped_column(Integer, index=True)

    level_ref: Mapped[Level] = relationship(back_populates="lessons")


class Lexeme(Base):
    __tablename__ = "lexemes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lemma: Mapped[str] = mapped_column(String(256), index=True)
    normalized_lemma: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    gloss_en: Mapped[str | None] = mapped_column(String(512), nullable=True)
    gloss_ko: Mapped[str | None] = mapped_column(String(512), nullable=True)
    item_type: Mapped[str] = mapped_column(String(32), default="vocab")
    source_type: Mapped[str] = mapped_column(String(64), default="glossary_index")
    review_status: Mapped[str] = mapped_column(String(64), default="draft_ocr_needs_manual_review")
    first_level: Mapped[str | None] = mapped_column(String(8), nullable=True)
    first_lesson: Mapped[str | None] = mapped_column(String(16), nullable=True)
    first_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    first_order_index: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    raw_source_metadata: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    occurrences: Mapped[list[Occurrence]] = relationship(back_populates="lexeme")
    surface_forms: Mapped[list[SurfaceForm]] = relationship(back_populates="lexeme")


class Occurrence(Base):
    __tablename__ = "occurrences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lexeme_id: Mapped[int] = mapped_column(Integer, ForeignKey("lexemes.id"), index=True)
    level: Mapped[str] = mapped_column(String(8))
    lesson: Mapped[str] = mapped_column(String(16))
    page: Mapped[int] = mapped_column(Integer)
    order_index: Mapped[int] = mapped_column(Integer, index=True)
    source_type: Mapped[str] = mapped_column(String(64))
    review_status: Mapped[str] = mapped_column(String(64))
    raw_source_metadata: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    lexeme: Mapped[Lexeme] = relationship(back_populates="occurrences")


class SurfaceForm(Base):
    __tablename__ = "surface_forms"
    __table_args__ = (
        UniqueConstraint("lexeme_id", "normalized_surface", name="uq_lexeme_surface"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lexeme_id: Mapped[int] = mapped_column(Integer, ForeignKey("lexemes.id"), index=True)
    surface: Mapped[str] = mapped_column(String(256))
    normalized_surface: Mapped[str] = mapped_column(String(256), index=True)
    source: Mapped[str] = mapped_column(String(32), default="generated")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    lexeme: Mapped[Lexeme] = relationship(back_populates="surface_forms")


class CustomAllowlist(Base):
    __tablename__ = "custom_allowlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String(256))
    normalized_text: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    allow_type: Mapped[str] = mapped_column(String(32), default="global")
    note: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class UnmappedStaging(Base):
    """Rows that failed import validation — not used in analysis."""

    __tablename__ = "unmapped_staging"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lemma: Mapped[str | None] = mapped_column(String(256), nullable=True)
    level: Mapped[str | None] = mapped_column(String(8), nullable=True)
    lesson: Mapped[str | None] = mapped_column(String(16), nullable=True)
    first_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reason: Mapped[str] = mapped_column(String(256))
    raw_source_metadata: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
