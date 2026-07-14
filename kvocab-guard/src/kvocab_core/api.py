"""kvocab_core public API — Tauri sidecar 및 CLI 진입점용.

모든 함수는 ``str`` (JSON) 을 받아 ``str`` (JSON) 을 반환한다.
UI 레이어나 PySide6 에 대한 의존이 전혀 없어야 한다.
"""

from __future__ import annotations

import json
import traceback
from pathlib import Path
from typing import Any

from kvocab_core.allowlist import (
    add_allowlist_item,
    delete_allowlist_item,
    ensure_default_allowlist,
    is_protected_allowlist_norm,
    list_allowlist,
)
from kvocab_core.analyzer import Analyzer, invalidate_lexeme_index
from kvocab_core.config import DEFAULT_DB_PATH
from kvocab_core.database import get_counts, init_db
from kvocab_core.dictionary import list_lexemes, search_lexemes_multi
from kvocab_core.document_extractors import extract_document
from kvocab_core.models import CustomAllowlist, Lesson, Level, Lexeme
from kvocab_core.schemas import AllowlistItem, AnalyzeRequest, Strictness
from kvocab_core.seed import full_seed, is_seed_current

# ---------------------------------------------------------------------------
# 내부 헬퍼
# ---------------------------------------------------------------------------

_session_factory = None


def _get_factory(db_path: str | None = None):
    """세션 팩토리를 반환한다. db_path 가 None 이면 기본 경로를 사용."""
    global _session_factory
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    if _session_factory is None:
        _session_factory = init_db(path)
    return _session_factory


def _ok(data: Any) -> str:
    return json.dumps({"ok": True, "data": data}, ensure_ascii=False)


def _err(msg: str) -> str:
    return json.dumps({"ok": False, "error": msg}, ensure_ascii=False)


def _safe(fn, *args, **kwargs) -> str:
    """예외를 잡아 JSON error 응답으로 변환하는 래퍼."""
    try:
        return fn(*args, **kwargs)
    except Exception:
        return _err(traceback.format_exc())


# ---------------------------------------------------------------------------
# DB / 초기화
# ---------------------------------------------------------------------------


def init(db_path: str | None = None) -> str:
    """DB 초기화 및 seed 확인. 앱 시작 시 한 번 호출한다.

    Returns:
        JSON ``{"ok": true, "data": {"seeded": bool}}``
    """
    def _run() -> str:
        factory = _get_factory(db_path)
        with factory() as session:
            ensure_default_allowlist(session)
            count = session.query(Lexeme).count()
            seed_current = is_seed_current(session) if count else False
            seeded = count > 0 and seed_current
        return _ok({"seeded": seeded, "lexeme_count": count})

    return _safe(_run)


def run_seed(db_path: str | None = None, *, preserve_allowlist: bool = True) -> str:
    """DB를 초기화하고 seed 데이터를 로드한다.

    Returns:
        JSON ``{"ok": true, "data": {"stats": str}}``
    """
    def _run() -> str:
        factory = _get_factory(db_path)
        with factory() as session:
            stats = full_seed(session, preserve_allowlist=preserve_allowlist)
        invalidate_lexeme_index()
        return _ok({"stats": str(stats)})

    return _safe(_run)


def get_db_counts(db_path: str | None = None) -> str:
    """DB 통계(어휘 수, 레벨 수 등)를 반환한다."""
    def _run() -> str:
        factory = _get_factory(db_path)
        with factory() as session:
            counts = get_counts(session)
        return _ok(counts)

    return _safe(_run)


# ---------------------------------------------------------------------------
# 레벨 / 단원
# ---------------------------------------------------------------------------


def list_levels_and_lessons(db_path: str | None = None) -> str:
    """레벨 및 단원 목록을 반환한다.

    Returns:
        JSON ``{"ok": true, "data": {"levels": [...], "lessons": {level: [...]}}}``
    """
    def _run() -> str:
        factory = _get_factory(db_path)
        with factory() as session:
            levels = session.query(Level).order_by(Level.sort_order).all()
            lessons = session.query(Lesson).order_by(Lesson.order_index).all()

        level_data = [
            {
                "level": lv.level,
                "series": lv.series,
                "title_ko": lv.title_ko,
                "title_en": lv.title_en,
                "sort_order": lv.sort_order,
            }
            for lv in levels
        ]
        lesson_data: dict[str, list[dict]] = {}
        for ls in lessons:
            lesson_data.setdefault(ls.level, []).append(
                {
                    "lesson": ls.lesson,
                    "unit_no": ls.unit_no,
                    "lesson_no": ls.lesson_no,
                    "unit_topic": ls.unit_topic,
                    "unit_title": ls.unit_title,
                    "order_index": ls.order_index,
                }
            )
        return _ok({"levels": level_data, "lessons": lesson_data})

    return _safe(_run)


# ---------------------------------------------------------------------------
# 텍스트 분석
# ---------------------------------------------------------------------------


def analyze_text(request_json: str, db_path: str | None = None) -> str:
    """텍스트를 분석하고 결과를 반환한다.

    Args:
        request_json: ``AnalyzeRequest`` 필드를 담은 JSON 문자열.
            예) ``'{"text": "안녕하세요", "target_level": "1A",
                     "target_lesson": "1-1"}'``
        db_path: DB 경로 (None 이면 기본 경로).

    Returns:
        JSON ``{"ok": true, "data": <AnalyzeResult as dict>}``
    """
    def _run() -> str:
        params = json.loads(request_json)
        if "strictness" in params:
            params["strictness"] = Strictness(params["strictness"])
        request = AnalyzeRequest(**params)
        factory = _get_factory(db_path)
        with factory() as session:
            result = Analyzer(session).analyze(request)
        return _ok(result.model_dump(mode="json"))

    return _safe(_run)


# ---------------------------------------------------------------------------
# 어휘 사전
# ---------------------------------------------------------------------------


def search_dictionary(
    query: str, db_path: str | None = None, target_level: str = "", target_lesson: str = ""
) -> str:
    """어휘 사전을 검색한다.

    Args:
        query: 검색어. 빈 문자열이면 전체 목록을 반환.
        target_level / target_lesson: 목표 단원 (단원 내/후 표시에 사용).

    Returns:
        JSON ``{"ok": true, "data": [<LexemeSearchResult>, ...]}``
    """
    def _run() -> str:
        factory = _get_factory(db_path)
        with factory() as session:
            # 목표 단원의 order_index 조회
            target_oi: int | None = None
            if target_level and target_lesson:
                ls = (
                    session.query(Lesson)
                    .filter(Lesson.level == target_level, Lesson.lesson == target_lesson)
                    .one_or_none()
                )
                target_oi = ls.order_index if ls else None

            if query.strip():
                results = search_lexemes_multi(
                    session, query.strip(), target_order_index=target_oi
                )
            else:
                results = list_lexemes(session, target_order_index=target_oi)
        return _ok([r.model_dump(mode="json") for r in results])

    return _safe(_run)


# ---------------------------------------------------------------------------
# 허용어
# ---------------------------------------------------------------------------


def get_allowlist(db_path: str | None = None) -> str:
    """허용어 목록을 반환한다."""
    def _run() -> str:
        factory = _get_factory(db_path)
        with factory() as session:
            items = list_allowlist(session)
        data = [
            AllowlistItem(
                id=i.id,
                text=i.text,
                normalized_text=i.normalized_text,
                allow_type=i.allow_type,
                note=i.note,
                is_protected=is_protected_allowlist_norm(i.normalized_text),
            ).model_dump(mode="json")
            for i in items
        ]
        return _ok(data)

    return _safe(_run)


def add_to_allowlist(
    text: str, allow_type: str = "global", note: str | None = None, db_path: str | None = None
) -> str:
    """허용어를 추가한다."""
    def _run() -> str:
        factory = _get_factory(db_path)
        with factory() as session:
            item = add_allowlist_item(session, text, allow_type=allow_type, note=note)
        return _ok({"id": item.id, "text": item.text, "normalized_text": item.normalized_text})

    return _safe(_run)


def remove_from_allowlist(item_id: int, db_path: str | None = None) -> str:
    """허용어를 삭제한다. 보호된 항목은 삭제할 수 없다."""
    def _run() -> str:
        factory = _get_factory(db_path)
        with factory() as session:
            item = session.get(CustomAllowlist, item_id)
            if item and is_protected_allowlist_norm(item.normalized_text):
                return _err("교재 고정 등장인물은 삭제할 수 없습니다.")
            deleted = delete_allowlist_item(session, item_id)
        if not deleted:
            return _err(f"항목 ID {item_id}를 찾을 수 없습니다.")
        return _ok({"deleted_id": item_id})

    return _safe(_run)


# ---------------------------------------------------------------------------
# 문서 추출 및 표지 이미지
# ---------------------------------------------------------------------------


def get_cover_base64(level: str) -> str:
    """교재 레벨의 표지 이미지(covers/{level}.jpg 등)를 Base64 인코딩하여 반환한다.

    Returns:
        JSON ``{"ok": true, "data": {"base64": str|null}}``
    """
    import base64  # noqa: PLC0415

    from kvocab_core.config import cover_image_path  # noqa: PLC0415

    def _run() -> str:
        path = cover_image_path(level)
        if not path or not path.exists():
            return _ok({"base64": None})
        try:
            with open(path, "rb") as f:
                data = f.read()
            b64_str = base64.b64encode(data).decode("utf-8")
            ext = path.suffix[1:]  # e.g., 'jpg', 'png'
            if ext == "jpg":
                ext = "jpeg"
            return _ok({"base64": f"data:image/{ext};base64,{b64_str}"})
        except Exception as exc:
            return _err(f"이미지 변환 실패: {exc}")

    return _safe(_run)


def extract_text_from_file(file_path: str) -> str:
    """문서(PDF, DOCX, HWP/HWPX, TXT)에서 텍스트를 추출한다.

    Returns:
        JSON ``{"ok": true, "data": {"text": str, "message": str|null}}``
    """
    def _run() -> str:
        doc = extract_document(file_path)
        return _ok(
            {
                "text": doc.text,
                "message": doc.message,
                "page_count": len(doc.pages),
            }
        )

    return _safe(_run)
