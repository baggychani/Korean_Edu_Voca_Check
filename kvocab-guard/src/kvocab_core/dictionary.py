from __future__ import annotations

from sqlalchemy import or_
from sqlalchemy.orm import Session

from kvocab_core.config import INCLUDE_DRAFT_DATA, USABLE_REVIEW_STATUSES
from kvocab_core.models import Lexeme, Occurrence
from kvocab_core.normalization import lemma_gana_sort_key, normalize_key
from kvocab_core.schemas import LexemeSearchResult
from kvocab_core.status_labels import status_label_ko


def _verdict_for_target(
    first_order_index: int | None,
    target_order_index: int | None,
) -> str:
    if first_order_index is None or target_order_index is None:
        return ""
    if first_order_index <= target_order_index:
        return status_label_ko("allowed")
    return status_label_ko("before_introduced")


def search_lexemes(
    session: Session,
    query: str,
    *,
    target_level: str | None = None,
    target_lesson: str | None = None,
    target_order_index: int | None = None,
    limit: int = 50,
) -> list[LexemeSearchResult]:
    q = normalize_key(query)
    if not q:
        return []

    base = session.query(Lexeme)
    if not INCLUDE_DRAFT_DATA:
        base = base.filter(Lexeme.review_status.in_(USABLE_REVIEW_STATUSES))

    exact = base.filter(Lexeme.normalized_lemma == q).all()
    fuzzy = (
        base.filter(
            Lexeme.normalized_lemma != q,
            or_(
                Lexeme.normalized_lemma.contains(q),
                Lexeme.lemma.contains(query.strip()),
            ),
        )
        .limit(limit)
        .all()
    )

    seen: set[int] = set()
    ordered: list[Lexeme] = []
    for row in exact + fuzzy:
        if row.id not in seen:
            seen.add(row.id)
            ordered.append(row)

    results: list[LexemeSearchResult] = []
    for lex in ordered[:limit]:
        occs = (
            session.query(Occurrence)
            .filter(Occurrence.lexeme_id == lex.id)
            .order_by(Occurrence.order_index, Occurrence.page)
            .all()
        )
        occ_dicts = [
            {
                "level": o.level,
                "lesson": o.lesson,
                "page": o.page,
                "order_index": o.order_index,
            }
            for o in occs
        ]
        other = [
            f"{o.level} {o.lesson} · p.{o.page}"
            for o in occs
            if not (
                o.level == lex.first_level
                and o.lesson == lex.first_lesson
                and o.page == lex.first_page
            )
        ]
        results.append(
            LexemeSearchResult(
                lemma=lex.lemma,
                gloss_en=lex.gloss_en,
                gloss_ko=lex.gloss_ko,
                first_level=lex.first_level,
                first_lesson=lex.first_lesson,
                first_page=lex.first_page,
                first_order_index=lex.first_order_index,
                source_type=lex.source_type,
                review_status=lex.review_status,
                item_type=lex.item_type,
                normalized_lemma=lex.normalized_lemma,
                occurrences=occ_dicts,
                verdict_label_ko=_verdict_for_target(lex.first_order_index, target_order_index),
                other_occurrences=other,
            )
        )
    return results


def list_lexemes(
    session: Session,
    *,
    target_order_index: int | None = None,
    limit: int = 5000,
) -> list[LexemeSearchResult]:
    base = session.query(Lexeme)
    if not INCLUDE_DRAFT_DATA:
        base = base.filter(Lexeme.review_status.in_(USABLE_REVIEW_STATUSES))

    rows = base.limit(limit).all()
    rows.sort(key=lambda lex: lemma_gana_sort_key(lex.lemma))
    results: list[LexemeSearchResult] = []
    for lex in rows:
        occs = (
            session.query(Occurrence)
            .filter(Occurrence.lexeme_id == lex.id)
            .order_by(Occurrence.order_index, Occurrence.page)
            .all()
        )
        other = [
            f"{o.level} {o.lesson} · p.{o.page}"
            for o in occs
            if not (
                o.level == lex.first_level
                and o.lesson == lex.first_lesson
                and o.page == lex.first_page
            )
        ]
        results.append(
            LexemeSearchResult(
                lemma=lex.lemma,
                gloss_en=lex.gloss_en,
                gloss_ko=lex.gloss_ko,
                first_level=lex.first_level,
                first_lesson=lex.first_lesson,
                first_page=lex.first_page,
                first_order_index=lex.first_order_index,
                source_type=lex.source_type,
                review_status=lex.review_status,
                item_type=lex.item_type,
                normalized_lemma=lex.normalized_lemma,
                occurrences=[
                    {
                        "level": o.level,
                        "lesson": o.lesson,
                        "page": o.page,
                        "order_index": o.order_index,
                    }
                    for o in occs
                ],
                verdict_label_ko=_verdict_for_target(lex.first_order_index, target_order_index),
                other_occurrences=other,
            )
        )
    return results
