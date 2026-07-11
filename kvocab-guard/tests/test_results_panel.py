from __future__ import annotations

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from kvocab_core.schemas import AnalyzeResult, AnalyzeSummary, Issue, IssueStatus
from kvocab_desktop.widgets.results_panel import ResultsPanel


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv[:1])
    return app


def test_results_panel_uses_requested_unknown_label() -> None:
    _app()
    panel = ResultsPanel()

    assert panel.filter_buttons["unknown"].text() == "❌ 교재에 없습니다"
    assert panel.allow_btn.text() == "허용어 목록에 추가"
    assert list(panel.filter_buttons) == [
        "all",
        "allowed",
        "before_introduced",
        "unknown",
    ]


def test_completion_message_is_rendered_as_a_table_row() -> None:
    _app()
    panel = ResultsPanel()
    result = AnalyzeResult(
        summary=AnalyzeSummary(target_display="1A 1-1", issue_count=0),
    )

    panel.show_result(result)

    assert panel.table.item(0, 0).text() == "✓  검사 완료 — 1A 1-1 기준 문제 없음"
    assert panel.table.columnSpan(0, 0) == panel.table.columnCount()


def test_equivalent_lemma_is_shown_with_arrow() -> None:
    _app()
    panel = ResultsPanel()
    result = AnalyzeResult(
        summary=AnalyzeSummary(target_display="1A 1-1"),
        allowed=[
            Issue(
                surface="안녕",
                lemma="안녕",
                normalized="안녕",
                equivalent_lemma="안녕하세요",
                status=IssueStatus.allowed,
            )
        ],
    )

    panel.show_result(result)
    panel._set_filter("allowed")

    assert panel.table.item(0, 1).text() == "안녕 → 안녕하세요"


def test_results_panel_clear_resets_selection_without_error() -> None:
    _app()
    panel = ResultsPanel()

    panel.clear()

    assert panel.selected_label.text() == "—"
    assert not panel.allow_btn.isEnabled()


def test_all_filter_includes_allowed_and_warning_rows() -> None:
    _app()
    panel = ResultsPanel()
    result = AnalyzeResult(
        summary=AnalyzeSummary(target_display="1A 1-1", issue_count=1),
        issues=[
            Issue(
                surface="가뭄",
                lemma="가뭄",
                normalized="가뭄",
                status=IssueStatus.unknown,
                start=3,
                end=5,
            )
        ],
        allowed=[
            Issue(
                surface="안녕하세요",
                lemma="안녕하세요",
                normalized="안녕하세요",
                status=IssueStatus.allowed,
                start=0,
                end=5,
            )
        ],
    )

    panel.show_result(result)

    assert panel.table.rowCount() == 2
    assert {panel.table.item(row, 0).text() for row in range(2)} == {"가뭄", "안녕하세요"}
