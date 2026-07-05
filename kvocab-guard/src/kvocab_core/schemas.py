from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class Strictness(StrEnum):
    loose = "loose"
    balanced = "balanced"
    strict = "strict"


class IssueStatus(StrEnum):
    allowed = "allowed"
    before_introduced = "before_introduced"
    unknown_high = "unknown_high"
    unknown_medium = "unknown_medium"
    unknown_low = "unknown_low"
    custom_allowed = "custom_allowed"
    ignored_nnp = "ignored_nnp"
    ignored_pattern = "ignored_pattern"


class Severity(StrEnum):
    none = "none"
    low = "low"
    medium = "medium"
    high = "high"


class AnalyzeRequest(BaseModel):
    text: str
    target_level: str = "2A"
    target_lesson: str = "2-1"
    strictness: Strictness = Strictness.balanced
    use_morph: bool = True
    show_debug_ignored: bool = False


class Issue(BaseModel):
    surface: str
    lemma: str
    normalized: str
    pos: str = ""
    status: IssueStatus
    severity: Severity = Severity.none
    reason: str = ""
    first_level: str | None = None
    first_lesson: str | None = None
    first_page: int | None = None
    sentence: str = ""
    start: int = 0
    end: int = 0
    suggestions: list[str] = Field(default_factory=list)
    review_status: str | None = None

    @property
    def status_label_ko(self) -> str:
        from kvocab_core.status_labels import status_label_ko

        return status_label_ko(self.status.value)

    @property
    def first_seen_display(self) -> str:
        if self.first_level and self.first_lesson:
            page = f", p.{self.first_page}" if self.first_page else ""
            return f"{self.first_level} {self.first_lesson}{page}"
        return ""


class AnalyzeSummary(BaseModel):
    target_display: str = ""
    total_tokens: int = 0
    issue_count: int = 0
    before_introduced_count: int = 0
    unknown_high_count: int = 0
    unknown_medium_count: int = 0
    unknown_low_count: int = 0
    ignored_count: int = 0
    allowed_count: int = 0
    max_known_order_index: int | None = None
    max_known_display: str = ""


class AnalyzeResult(BaseModel):
    summary: AnalyzeSummary
    issues: list[Issue] = Field(default_factory=list)
    debug_ignored: list[Issue] = Field(default_factory=list)


class LexemeSearchResult(BaseModel):
    lemma: str
    gloss_en: str | None = None
    gloss_ko: str | None = None
    first_level: str | None = None
    first_lesson: str | None = None
    first_page: int | None = None
    first_order_index: int | None = None
    source_type: str = ""
    review_status: str = ""
    item_type: str = "vocab"
    normalized_lemma: str = ""
    occurrences: list[dict] = Field(default_factory=list)
    verdict_label_ko: str = ""
    other_occurrences: list[str] = Field(default_factory=list)


class AllowlistItem(BaseModel):
    id: int
    text: str
    normalized_text: str
    allow_type: str
    note: str | None = None


class ExtractedPage(BaseModel):
    page_no: int
    text: str


class ExtractedDocument(BaseModel):
    text: str
    pages: list[ExtractedPage] = Field(default_factory=list)
    message: str | None = None
