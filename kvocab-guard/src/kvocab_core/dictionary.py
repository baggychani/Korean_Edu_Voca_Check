from __future__ import annotations

from sqlalchemy import or_
from sqlalchemy.orm import Session

from kvocab_core.config import INCLUDE_DRAFT_DATA, USABLE_REVIEW_STATUSES
from kvocab_core.equivalent_forms import canonical_form, equivalent_forms_for
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

    canonical = canonical_form(q)
    exact_keys = [q]
    if canonical and canonical not in exact_keys:
        exact_keys.append(canonical)
    exact = base.filter(Lexeme.normalized_lemma.in_(exact_keys)).all()
    exact.sort(key=lambda lex: exact_keys.index(lex.normalized_lemma))
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
                equivalent_forms=equivalent_forms_for(lex.normalized_lemma),
            )
        )
    return results


def search_lexemes_multi(
    session: Session,
    query: str,
    *,
    target_level: str | None = None,
    target_lesson: str | None = None,
    target_order_index: int | None = None,
    limit: int = 50,
) -> list[LexemeSearchResult]:
    """쉼표로 구분된 여러 표제어를 각각 검색해 합친다."""
    terms = [part.strip() for part in query.split(",") if part.strip()]
    if not terms:
        return []
    if len(terms) == 1:
        return search_lexemes(
            session,
            terms[0],
            target_level=target_level,
            target_lesson=target_lesson,
            target_order_index=target_order_index,
            limit=limit,
        )

    seen: set[str] = set()
    merged: list[LexemeSearchResult] = []
    per_term = max(limit // len(terms), 10)
    for term in terms:
        for row in search_lexemes(
            session,
            term,
            target_level=target_level,
            target_lesson=target_lesson,
            target_order_index=target_order_index,
            limit=per_term,
        ):
            key = row.normalized_lemma or row.lemma
            if key in seen:
                continue
            seen.add(key)
            merged.append(row)
            if len(merged) >= limit:
                return merged
    return merged


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
                equivalent_forms=equivalent_forms_for(lex.normalized_lemma),
            )
        )
    return results
