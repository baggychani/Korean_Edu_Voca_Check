from __future__ import annotations

import os
import re
from concurrent.futures import ThreadPoolExecutor
from threading import local

from sqlalchemy.orm import Session

from kvocab_core.allowlist import get_allowlist_set
from kvocab_core.config import INCLUDE_DRAFT_DATA, USABLE_REVIEW_STATUSES
from kvocab_core.matching import build_eojeol_match_keys, is_particle_lemma, split_eojeol
from kvocab_core.models import Lesson, Lexeme, SurfaceForm
from kvocab_core.morph import KoreanMorphAnalyzer, RegexFallbackAnalyzer
from kvocab_core.normalization import is_ignored_pattern, normalize_key
from kvocab_core.schemas import (
    AnalyzeRequest,
    AnalyzeResult,
    AnalyzeSummary,
    Issue,
    IssueStatus,
    Severity,
)
from kvocab_core.token_units import (
    MatchSegment,
    build_match_segments,
    segment_key,
    should_skip_standalone,
)
from kvocab_core.unknown_risk import classify_unknown

_morph_for_index = KoreanMorphAnalyzer()


class LexemeIndex:
    def __init__(self, session: Session) -> None:
        self.by_norm_lemma: dict[str, Lexeme] = {}
        self.by_norm_surface: dict[str, Lexeme] = {}
        q = session.query(Lexeme)
        if not INCLUDE_DRAFT_DATA:
            q = q.filter(Lexeme.review_status.in_(USABLE_REVIEW_STATUSES))
        for lex in q.all():
            if lex.review_status not in USABLE_REVIEW_STATUSES:
                continue
            self.by_norm_lemma[lex.normalized_lemma] = lex
            content_key = _content_lookup_key(lex.lemma)
            if content_key and content_key != lex.normalized_lemma:
                self.by_norm_surface.setdefault(content_key, lex)
        for sf, lex in (
            session.query(SurfaceForm, Lexeme)
            .join(Lexeme, SurfaceForm.lexeme_id == Lexeme.id)
            .all()
        ):
            if lex.review_status not in USABLE_REVIEW_STATUSES:
                continue
            self.by_norm_surface[sf.normalized_surface] = lex

    def lookup(self, norm: str) -> Lexeme | None:
        return self.by_norm_lemma.get(norm) or self.by_norm_surface.get(norm)


_INDEX_CACHE: LexemeIndex | None = None


def get_lexeme_index(session: Session) -> LexemeIndex:
    global _INDEX_CACHE
    if _INDEX_CACHE is None:
        _INDEX_CACHE = LexemeIndex(session)
    return _INDEX_CACHE


def invalidate_lexeme_index() -> None:
    global _INDEX_CACHE
    _INDEX_CACHE = None


def _content_lookup_key(lemma: str) -> str:
    """표제어 구(전화를 받다) → 내용어 key(전화받다) for phrase matching."""
    if _morph_for_index.backend_name != "kiwi":
        return ""
    segs = build_match_segments(_morph_for_index.analyze(lemma))
    return segment_key(segs) if segs else ""


def _segments_in_span(segs: list[MatchSegment], start: int, end: int) -> list[MatchSegment]:
    return [s for s in segs if s.start >= start and s.end <= end]


def _content_segments(segs: list[MatchSegment]) -> list[MatchSegment]:
    return [s for s in segs if not is_particle_lemma(s.lemma)]


def _single_eojeol_key_matches_segments(key: str, segs: list[MatchSegment]) -> bool:
    content = _content_segments(segs)
    return bool(content) and segment_key(content) == key


_SENTENCE_END = re.compile(r"[.!?。\n]+")
_PARALLEL_MIN_SENTENCES = 2
_PARALLEL_MIN_CHARS = 120
_MAX_PARALLEL_WORKERS = 8

_morph_local = local()


def _thread_morph(use_morph: bool) -> KoreanMorphAnalyzer | RegexFallbackAnalyzer:
    if not use_morph:
        if not hasattr(_morph_local, "fallback"):
            _morph_local.fallback = RegexFallbackAnalyzer()
        return _morph_local.fallback
    if not hasattr(_morph_local, "morph"):
        _morph_local.morph = KoreanMorphAnalyzer()
    return _morph_local.morph


def split_sentence_spans(text: str) -> list[tuple[int, int]]:
    """문장 경계(. ? ! 줄바꿈) 기준 (start, end) 목록. 전체 텍스트 좌표."""
    if not text.strip():
        return []
    spans: list[tuple[int, int]] = []
    start = 0
    for m in _SENTENCE_END.finditer(text):
        end = m.end()
        chunk = text[start:end]
        left = len(chunk) - len(chunk.lstrip())
        right = len(chunk) - len(chunk.rstrip())
        s, e = start + left, end - right
        if s < e:
            spans.append((s, e))
        start = end
    if start < len(text):
        chunk = text[start:]
        left = len(chunk) - len(chunk.lstrip())
        right = len(chunk) - len(chunk.rstrip())
        s, e = start + left, len(text) - right
        if s < e:
            spans.append((s, e))
    return spans or [(0, len(text))]


def _shift_issues(issues: list[Issue], offset: int, full_text: str) -> list[Issue]:
    if not offset:
        return issues
    shifted: list[Issue] = []
    for issue in issues:
        data = issue.model_dump()
        data["start"] = issue.start + offset
        data["end"] = issue.end + offset
        data["sentence"] = _sentence_at(full_text, data["start"], data["end"])
        shifted.append(Issue(**data))
    return shifted


def _sentence_at(text: str, start: int, end: int) -> str:
    left = max(text.rfind(ch, 0, start) for ch in ".?!\n")
    right_candidates = [text.find(ch, end) for ch in ".?!\n"]
    right_candidates = [r for r in right_candidates if r >= 0]
    right = min(right_candidates) + 1 if right_candidates else len(text)
    return text[left + 1 : right].strip()


def _issue_from_lexeme(
    lex: Lexeme,
    *,
    surface: str,
    norm: str,
    pos: str,
    target_oi: int,
    text: str,
    start: int,
    end: int,
) -> Issue:
    if lex.first_order_index is not None and lex.first_order_index <= target_oi:
        status, severity, reason = IssueStatus.allowed, Severity.none, "목표 내"
    elif lex.first_order_index is not None and lex.first_order_index > target_oi:
        status, severity, reason = (
            IssueStatus.before_introduced,
            Severity.high,
            "뒤 단원",
        )
    else:
        status, severity, reason = IssueStatus.unknown_medium, Severity.medium, "단원 미등록"

    return Issue(
        surface=surface,
        lemma=lex.lemma,
        normalized=norm,
        pos=pos,
        status=status,
        severity=severity,
        reason=reason,
        first_level=lex.first_level,
        first_lesson=lex.first_lesson,
        first_page=lex.first_page,
        sentence=_sentence_at(text, start, end),
        start=start,
        end=end,
        review_status=lex.review_status,
    )


def _eojeol_surface_at(
    eojeol: list[str], starts: list[int], ends: list[int], pos: int
) -> str | None:
    for i, start in enumerate(starts):
        if start <= pos < ends[i]:
            return eojeol[i]
    return None


def _display_surface(
    text: str,
    start: int,
    end: int,
    *,
    eojeol: list[str],
    eo_starts: list[int],
    eo_ends: list[int],
) -> str:
    """형태소 구간이 한 어절 안에 있으면 사용자가 쓴 어절 전체를 표현으로 쓴다."""
    for i, eo_start in enumerate(eo_starts):
        eo_end = eo_ends[i]
        if eo_start <= start < eo_end and end <= eo_end:
            return eojeol[i].rstrip(".!?")
    return text[start:end]


class Analyzer:
    MAX_EXPR_SEGS = 6

    def __init__(self, session: Session) -> None:
        self.session = session
        self.morph = KoreanMorphAnalyzer()

    def analyze(self, request: AnalyzeRequest) -> AnalyzeResult:
        lesson = (
            self.session.query(Lesson)
            .filter(
                Lesson.level == request.target_level,
                Lesson.lesson == request.target_lesson,
            )
            .one_or_none()
        )
        if not lesson:
            raise ValueError(f"Unknown target {request.target_level} {request.target_lesson}")

        target_oi = lesson.order_index
        text = request.text or ""
        index = get_lexeme_index(self.session)
        allowlist = get_allowlist_set(self.session)

        spans = split_sentence_spans(text)
        use_parallel = len(spans) >= _PARALLEL_MIN_SENTENCES and len(text) >= _PARALLEL_MIN_CHARS

        if use_parallel:
            issues, debug_ignored, total_segs = self._analyze_parallel(
                text, spans, target_oi, allowlist, index, request
            )
        else:
            morph = self.morph if request.use_morph else RegexFallbackAnalyzer()
            issues, debug_ignored, total_segs = self._analyze_chunk(
                text, 0, text, target_oi, allowlist, index, request, morph
            )

        visible = [
            i
            for i in issues
            if i.status
            not in (
                IssueStatus.allowed,
                IssueStatus.custom_allowed,
            )
        ]
        allowed_items = [
            i for i in issues if i.status in (IssueStatus.allowed, IssueStatus.custom_allowed)
        ]

        max_known_oi, max_known_display = None, ""
        lesson_cache: dict[tuple[str, str], int | None] = {}
        for i in issues:
            if not i.first_level or not i.first_lesson or i.status == IssueStatus.custom_allowed:
                continue
            ck = (i.first_level, i.first_lesson)
            if ck not in lesson_cache:
                ls = (
                    self.session.query(Lesson)
                    .filter(Lesson.level == i.first_level, Lesson.lesson == i.first_lesson)
                    .one_or_none()
                )
                lesson_cache[ck] = ls.order_index if ls else None
            oi = lesson_cache[ck]
            if oi and (max_known_oi is None or oi > max_known_oi):
                max_known_oi = oi
                max_known_display = f"{i.first_level} {i.first_lesson}"

        summary = AnalyzeSummary(
            target_display=f"{request.target_level} {request.target_lesson}",
            total_tokens=total_segs,
            issue_count=len(visible),
            before_introduced_count=sum(
                1 for i in issues if i.status == IssueStatus.before_introduced
            ),
            unknown_high_count=sum(1 for i in issues if i.status == IssueStatus.unknown_high),
            unknown_medium_count=sum(1 for i in issues if i.status == IssueStatus.unknown_medium),
            unknown_low_count=sum(1 for i in issues if i.status == IssueStatus.unknown_low),
            ignored_count=len(debug_ignored),
            allowed_count=sum(1 for i in issues if i.status == IssueStatus.allowed),
            max_known_order_index=max_known_oi,
            max_known_display=max_known_display,
        )
        return AnalyzeResult(
            summary=summary,
            issues=visible if not request.show_debug_ignored else issues,
            allowed=allowed_items,
            debug_ignored=debug_ignored if request.show_debug_ignored else [],
        )

    def _analyze_parallel(
        self,
        full_text: str,
        spans: list[tuple[int, int]],
        target_oi: int,
        allowlist: set[str],
        index: LexemeIndex,
        request: AnalyzeRequest,
    ) -> tuple[list[Issue], list[Issue], int]:
        workers = min(len(spans), os.cpu_count() or 4, _MAX_PARALLEL_WORKERS)
        issues: list[Issue] = []
        debug_ignored: list[Issue] = []
        total_segs = 0

        def _run(span: tuple[int, int]) -> tuple[list[Issue], list[Issue], int]:
            s, e = span
            chunk = full_text[s:e]
            morph = _thread_morph(request.use_morph)
            return self._analyze_chunk(
                chunk, s, full_text, target_oi, allowlist, index, request, morph
            )

        with ThreadPoolExecutor(max_workers=workers) as pool:
            for chunk_issues, chunk_debug, seg_count in pool.map(_run, spans):
                issues.extend(chunk_issues)
                debug_ignored.extend(chunk_debug)
                total_segs += seg_count

        return issues, debug_ignored, total_segs

    def _analyze_chunk(
        self,
        text: str,
        offset: int,
        full_text: str,
        target_oi: int,
        allowlist: set[str],
        index: LexemeIndex,
        request: AnalyzeRequest,
        morph: KoreanMorphAnalyzer | RegexFallbackAnalyzer,
    ) -> tuple[list[Issue], list[Issue], int]:
        issues: list[Issue] = []
        debug_ignored: list[Issue] = []
        covered: list[tuple[int, int]] = []

        tokens = morph.analyze(text)
        segs = build_match_segments(tokens)

        def is_covered(s: int, e: int) -> bool:
            return any(a <= s and e <= b for a, b in covered)

        eojeol = split_eojeol(text)
        eo_starts, eo_ends = self._eojeol_bounds(text, eojeol)
        for key, start, end in self._eojeol_lexeme_spans(
            text, eojeol, eo_starts, eo_ends, index, segs
        ):
            if is_covered(start, end):
                continue
            lex = index.lookup(key)
            if not lex:
                continue
            covered.append((start, end))
            issues.append(
                self._lex_issue(
                    lex,
                    key,
                    text,
                    start,
                    end,
                    target_oi,
                    allowlist,
                    "EXPR",
                    eojeol,
                    eo_starts,
                    eo_ends,
                )
            )

        consumed = [False] * len(segs)

        for size in range(min(self.MAX_EXPR_SEGS, len(segs)), 1, -1):
            for i in range(len(segs) - size + 1):
                if any(consumed[i : i + size]):
                    continue
                chunk = segs[i : i + size]
                if any(chunk[k + 1].start - chunk[k].end > 8 for k in range(len(chunk) - 1)):
                    continue
                key = segment_key(chunk)
                lex = index.lookup(key)
                if not lex:
                    continue
                content = _content_segments(chunk)
                if not content:
                    continue
                start, end = content[0].start, content[-1].end
                if is_covered(start, end):
                    for k in range(i, i + size):
                        consumed[k] = True
                    continue
                covered.append((start, end))
                for k in range(i, i + size):
                    consumed[k] = True
                issues.append(
                    self._lex_issue(
                        lex,
                        key,
                        text,
                        start,
                        end,
                        target_oi,
                        allowlist,
                        "EXPR",
                        eojeol,
                        eo_starts,
                        eo_ends,
                    )
                )

        for i, seg in enumerate(segs):
            if consumed[i] or is_covered(seg.start, seg.end):
                continue
            if is_ignored_pattern(seg.surface):
                continue
            if should_skip_standalone(seg):
                continue

            norm = normalize_key(seg.lemma)
            if not norm:
                continue

            surface = _display_surface(
                text,
                seg.start,
                seg.end,
                eojeol=eojeol,
                eo_starts=eo_starts,
                eo_ends=eo_ends,
            )

            if norm in allowlist:
                issues.append(
                    Issue(
                        surface=surface,
                        lemma=seg.lemma,
                        normalized=norm,
                        pos="",
                        status=IssueStatus.custom_allowed,
                        severity=Severity.none,
                        reason="허용 목록",
                        sentence=_sentence_at(text, seg.start, seg.end),
                        start=seg.start,
                        end=seg.end,
                    )
                )
                continue

            lex = index.lookup(norm)
            if lex:
                issues.append(
                    _issue_from_lexeme(
                        lex,
                        surface=surface,
                        norm=norm,
                        pos="",
                        target_oi=target_oi,
                        text=text,
                        start=seg.start,
                        end=seg.end,
                    )
                )
                continue

            status, severity, reason, suggestions = classify_unknown(
                seg.lemma, strictness=request.strictness
            )
            issues.append(
                Issue(
                    surface=surface,
                    lemma=seg.lemma,
                    normalized=norm,
                    pos="",
                    status=status,
                    severity=severity,
                    reason=reason,
                    suggestions=suggestions,
                    sentence=_sentence_at(text, seg.start, seg.end),
                    start=seg.start,
                    end=seg.end,
                )
            )

        for tok in tokens:
            if tok.pos == "NNP":
                debug_ignored.append(
                    Issue(
                        surface=tok.surface,
                        lemma=tok.lemma,
                        normalized=normalize_key(tok.lemma),
                        pos=tok.pos,
                        status=IssueStatus.ignored_nnp,
                        sentence=_sentence_at(text, tok.start, tok.end),
                        start=tok.start,
                        end=tok.end,
                    )
                )

        return (
            _shift_issues(issues, offset, full_text),
            _shift_issues(debug_ignored, offset, full_text),
            len(segs),
        )

    def _eojeol_bounds(self, text: str, eojeol: list[str]) -> tuple[list[int], list[int]]:
        starts: list[int] = []
        ends: list[int] = []
        pos = 0
        for eo in eojeol:
            idx = text.find(eo, pos)
            if idx < 0:
                idx = pos
            starts.append(idx)
            ends.append(idx + len(eo))
            pos = idx + len(eo)
        return starts, ends

    def _eojeol_lexeme_spans(
        self,
        text: str,
        eojeol: list[str],
        starts: list[int],
        ends: list[int],
        index: LexemeIndex,
        all_segs: list[MatchSegment],
    ):
        seen: set[tuple[int, int]] = set()
        for key, i, j in build_eojeol_match_keys(eojeol):
            start, end = starts[i], ends[j - 1]
            span = (start, end)
            if span in seen or not index.lookup(key):
                continue
            if j - i == 1 and key != normalize_key(eojeol[i]):
                sub_segs = _segments_in_span(all_segs, start, end)
                if sub_segs and not _single_eojeol_key_matches_segments(key, sub_segs):
                    continue
            seen.add(span)
            yield key, start, end

        for size in range(min(5, len(eojeol)), 1, -1):
            for i in range(len(eojeol) - size + 1):
                start, end = starts[i], ends[i + size - 1]
                span = (start, end)
                if span in seen:
                    continue
                sub_segs = _segments_in_span(all_segs, start, end)
                mkey = segment_key(sub_segs) if sub_segs else ""
                if mkey and index.lookup(mkey):
                    seen.add(span)
                    yield mkey, start, end

    def _eojeol_matches(self, text: str, index: LexemeIndex):
        eojeol = split_eojeol(text)
        if not eojeol:
            return
        starts, ends = self._eojeol_bounds(text, eojeol)
        yield from (
            (key, start, end)
            for key, start, end in self._eojeol_lexeme_spans(text, eojeol, starts, ends, index, [])
        )

    def _lex_issue(
        self,
        lex: Lexeme,
        key: str,
        text: str,
        start: int,
        end: int,
        target_oi: int,
        allowlist: set[str],
        pos: str,
        eojeol: list[str],
        eo_starts: list[int],
        eo_ends: list[int],
    ) -> Issue:
        surface = _display_surface(
            text,
            start,
            end,
            eojeol=eojeol,
            eo_starts=eo_starts,
            eo_ends=eo_ends,
        )
        issue = _issue_from_lexeme(
            lex,
            surface=surface,
            norm=key,
            pos=pos,
            target_oi=target_oi,
            text=text,
            start=start,
            end=end,
        )
        if key in allowlist or lex.normalized_lemma in allowlist:
            issue.status = IssueStatus.custom_allowed
            issue.severity = Severity.none
            issue.reason = "허용 목록"
        return issue
