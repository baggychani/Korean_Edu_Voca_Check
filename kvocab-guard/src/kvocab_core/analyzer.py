from __future__ import annotations

from sqlalchemy.orm import Session

from kvocab_core.allowlist import get_allowlist_set
from kvocab_core.config import INCLUDE_DRAFT_DATA, USABLE_REVIEW_STATUSES
from kvocab_core.matching import build_eojeol_match_keys, split_eojeol
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
        status, severity, reason = IssueStatus.allowed, Severity.none, "교재 어휘"
    elif lex.first_order_index is not None and lex.first_order_index > target_oi:
        status, severity, reason = (
            IssueStatus.before_introduced,
            Severity.high,
            "목표 단원보다 뒤에 나오는 교재 어휘",
        )
    else:
        status, severity, reason = IssueStatus.unknown_medium, Severity.medium, "단원 정보 없음"

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
        index = LexemeIndex(self.session)
        allowlist = get_allowlist_set(self.session)
        issues: list[Issue] = []
        debug_ignored: list[Issue] = []
        covered: list[tuple[int, int]] = []

        def is_covered(s: int, e: int) -> bool:
            return any(a <= s and e <= b for a, b in covered)

        # 어절·표현 우선 매칭 (안 그래도, 이메일을 …)
        eojeol = split_eojeol(text)
        eo_starts, eo_ends = self._eojeol_bounds(text, eojeol)
        for key, start, end in self._eojeol_lexeme_spans(text, eojeol, eo_starts, eo_ends, index):
            if is_covered(start, end):
                continue
            lex = index.lookup(key)
            if not lex:
                continue
            covered.append((start, end))
            issues.append(self._lex_issue(lex, key, text, start, end, target_oi, allowlist, "EXPR"))

        tokens = (
            self.morph.analyze(text)
            if request.use_morph
            else RegexFallbackAnalyzer().analyze(text)
        )
        segs = build_match_segments(tokens)
        consumed = [False] * len(segs)

        # 원형 시퀀스 n-gram (가격이+비싸다, 가입하다 …)
        for size in range(min(self.MAX_EXPR_SEGS, len(segs)), 0, -1):
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
                start, end = chunk[0].start, chunk[-1].end
                if is_covered(start, end):
                    for k in range(i, i + size):
                        consumed[k] = True
                    continue
                covered.append((start, end))
                for k in range(i, i + size):
                    consumed[k] = True
                issues.append(
                    self._lex_issue(lex, key, text, start, end, target_oi, allowlist, "EXPR")
                )

        # 남은 단일 내용어
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

            surface = (
                _eojeol_surface_at(eojeol, eo_starts, eo_ends, seg.start)
                or text[seg.start : seg.end]
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

        # NNP → debug only
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


        visible = [
            i
            for i in issues
            if i.status
            not in (
                IssueStatus.allowed,
                IssueStatus.custom_allowed,
            )
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
            total_tokens=len(segs),
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
            debug_ignored=debug_ignored if request.show_debug_ignored else [],
        )

    def _eojeol_bounds(
        self, text: str, eojeol: list[str]
    ) -> tuple[list[int], list[int]]:
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
    ):
        seen: set[tuple[int, int]] = set()
        for key, i, j in build_eojeol_match_keys(eojeol):
            start, end = starts[i], ends[j - 1]
            span = (start, end)
            if span in seen or not index.lookup(key):
                continue
            seen.add(span)
            yield key, start, end

        for size in range(min(5, len(eojeol)), 1, -1):
            for i in range(len(eojeol) - size + 1):
                start, end = starts[i], ends[i + size - 1]
                span = (start, end)
                if span in seen:
                    continue
                sub = text[start:end]
                segs = build_match_segments(self.morph.analyze(sub))
                mkey = segment_key(segs) if segs else ""
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
            for key, start, end in self._eojeol_lexeme_spans(text, eojeol, starts, ends, index)
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
    ) -> Issue:
        issue = _issue_from_lexeme(
            lex, surface=text[start:end], norm=key, pos=pos,
            target_oi=target_oi, text=text, start=start, end=end,
        )
        if key in allowlist or lex.normalized_lemma in allowlist:
            issue.status = IssueStatus.custom_allowed
            issue.severity = Severity.none
            issue.reason = "허용 목록"
        return issue
