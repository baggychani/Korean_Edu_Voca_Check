from __future__ import annotations

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QColor, QFontMetrics, QPalette
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from kvocab_core.schemas import AnalyzeResult, Issue
from kvocab_core.status_labels import STATUS_LABELS_KO, status_label_ko
from kvocab_desktop.style import STATUS_BG_COLORS, STATUS_COLORS
from kvocab_desktop.widgets.table_font import app_default_font, bold_font

# Fixed: 판정·처음 나오는 곳 / Flex: 표현·원형·문장 (문장만 지분 15% 축소)
_COL_SURFACE = 0
_COL_LEMMA = 1
_COL_VERDICT = 2
_COL_FIRST = 3
_COL_SENTENCE = 4
_STRETCH_MIN_WIDTH = {_COL_SURFACE: 72, _COL_LEMMA: 80, _COL_SENTENCE: 100}
_ROW_HEIGHT = 42
_CELL_HPAD = 16
_VERDICT_EXTRA_PAD = 28
_SENTENCE_FLEX_WEIGHT = 0.85  # 표현·원형과 균등 분배 대비 15% 적음


def _fixed_column_widths(table: QTableWidget) -> dict[int, int]:
    regular = table.fontMetrics()
    bold = QFontMetrics(bold_font(table))

    verdict_w = max(bold.horizontalAdvance(text) for text in STATUS_LABELS_KO.values())
    verdict_w = max(verdict_w, bold.horizontalAdvance("판정"))

    levels = (
        "1A",
        "1B",
        "2A",
        "2B",
        "3A",
        "3B",
        "4A",
        "4B",
        "5A",
        "5B",
        "6A",
        "6B",
    )
    first_seen_w = max(
        regular.horizontalAdvance(f"{level} {lesson}")
        for level in levels
        for lesson in ("1-1", "4-1", "12-1", "12-2")
    )
    first_seen_w = max(first_seen_w, regular.horizontalAdvance("처음 나오는 곳"))

    return {
        _COL_VERDICT: int(verdict_w * 1.05) + _CELL_HPAD + _VERDICT_EXTRA_PAD,
        _COL_FIRST: first_seen_w + _CELL_HPAD,
    }


def _apply_flex_column_widths(table: QTableWidget) -> None:
    header = table.horizontalHeader()
    header.setStretchLastSection(False)
    header.setMinimumSectionSize(56)
    header.setFixedHeight(34)

    fixed = _fixed_column_widths(table)
    viewport_w = table.viewport().width()
    fixed_total = fixed[_COL_VERDICT] + fixed[_COL_FIRST]
    flex = max(0, viewport_w - fixed_total)

    flex_weight_sum = 1.0 + 1.0 + _SENTENCE_FLEX_WEIGHT
    surf_w = max(_STRETCH_MIN_WIDTH[_COL_SURFACE], int(flex * 1.0 / flex_weight_sum))
    lemma_w = max(_STRETCH_MIN_WIDTH[_COL_LEMMA], int(flex * 1.0 / flex_weight_sum))
    sent_w = max(
        _STRETCH_MIN_WIDTH[_COL_SENTENCE],
        int(flex * _SENTENCE_FLEX_WEIGHT / flex_weight_sum),
    )

    # 최소 너비 합이 flex를 넘으면 비율 유지하며 축소
    flex_used = surf_w + lemma_w + sent_w
    if flex_used > flex and flex_used > 0:
        scale = flex / flex_used
        surf_w = max(_STRETCH_MIN_WIDTH[_COL_SURFACE], int(surf_w * scale))
        lemma_w = max(_STRETCH_MIN_WIDTH[_COL_LEMMA], int(lemma_w * scale))
        sent_w = max(_STRETCH_MIN_WIDTH[_COL_SENTENCE], int(sent_w * scale))

    for col in range(table.columnCount()):
        header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)

    header.resizeSection(_COL_VERDICT, fixed[_COL_VERDICT])
    header.resizeSection(_COL_FIRST, fixed[_COL_FIRST])
    header.resizeSection(_COL_SURFACE, surf_w)
    header.resizeSection(_COL_LEMMA, lemma_w)
    header.resizeSection(_COL_SENTENCE, sent_w)


def _sentence_display(table: QTableWidget, text: str) -> tuple[str, bool]:
    if not text:
        return text, False
    width = table.columnWidth(_COL_SENTENCE) - _CELL_HPAD
    if width <= 0:
        return text, False
    elided = table.fontMetrics().elidedText(text, Qt.TextElideMode.ElideRight, width)
    return elided, elided != text


class _VerdictItemDelegate(QStyledItemDelegate):
    """행 선택 시에도 판정 열 글자색·배경색 유지."""

    def paint(self, painter, option, index) -> None:
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        fg = index.data(Qt.ItemDataRole.ForegroundRole)
        bg = index.data(Qt.ItemDataRole.BackgroundRole)
        if isinstance(fg, QColor):
            opt.palette.setColor(QPalette.ColorRole.Text, fg)
            opt.palette.setColor(QPalette.ColorRole.HighlightedText, fg)
        if isinstance(bg, QColor):
            opt.palette.setColor(QPalette.ColorRole.Base, bg)
            opt.palette.setColor(QPalette.ColorRole.Highlight, bg)
        super().paint(painter, opt, index)


def _stat_card(label: str, accent: str = "#111827") -> tuple[QFrame, QLabel]:
    card = QFrame()
    card.setObjectName("statCard")
    lay = QVBoxLayout(card)
    lay.setContentsMargins(12, 8, 12, 8)
    lay.setSpacing(2)
    value = QLabel("-")
    value.setObjectName("statValue")
    value.setStyleSheet(f"color: {accent};")
    caption = QLabel(label)
    caption.setObjectName("statLabel")
    caption.setWordWrap(True)
    lay.addWidget(value)
    lay.addWidget(caption)
    return card, value


def _selection_display(issue: Issue) -> str:
    if issue.lemma and issue.lemma != issue.surface:
        return f"{issue.surface}({issue.lemma})"
    return issue.surface


class ResultsPanel(QWidget):
    issue_selected = Signal(object)
    allow_requested = Signal(str, str, str)  # lemma, surface, first_seen
    sentence_highlight_requested = Signal(object)
    lemma_lookup_requested = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(0)

        title = QLabel("검사 결과")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        layout.addSpacing(10)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(10)
        card, self.lbl_target = _stat_card("목표 단원", "#1a6fdb")
        stats_row.addWidget(card, 1)
        card, self.lbl_issues = _stat_card("경고", "#111827")
        stats_row.addWidget(card, 1)
        card, self.lbl_early = _stat_card("아직 이릅니다", STATUS_COLORS["before_introduced"])
        stats_row.addWidget(card, 1)
        card, self.lbl_high = _stat_card("교재 외 · 난이도 높음", STATUS_COLORS["unknown_high"])
        stats_row.addWidget(card, 1)
        card, self.lbl_max = _stat_card("확인된 최고 단원", "#111827")
        stats_row.addWidget(card, 1)
        layout.addLayout(stats_row)
        layout.addSpacing(12)

        chip_row = QHBoxLayout()
        chip_row.setContentsMargins(0, 0, 0, 0)
        chip_row.setSpacing(6)
        self.filter_buttons: dict[str, QPushButton] = {}
        for key, label in [
            ("all", "전체"),
            ("allowed", "👍 사용 가능"),
            ("before_introduced", "⚠️ 아직 이릅니다"),
            ("unknown_high", "교재 외 · 높음"),
            ("unknown_medium", "교재 외 · 검토"),
            ("unknown_low", "교재 외 · 참고"),
        ]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setProperty("variant", "chip")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self._set_filter(k))
            chip_row.addWidget(btn)
            self.filter_buttons[key] = btn
        self.filter_buttons["all"].setChecked(True)
        chip_row.addStretch()

        table_section = QVBoxLayout()
        table_section.setContentsMargins(0, 0, 0, 0)
        table_section.setSpacing(9)
        table_section.addLayout(chip_row)

        self.completion_label = QLabel("")
        self.completion_label.setObjectName("completionStatus")
        self.completion_label.setWordWrap(True)
        self.completion_label.setVisible(False)
        table_section.addWidget(self.completion_label)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["표현", "원형", "판정", "처음 나오는 곳", "문장"])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFont(app_default_font())
        self.table.setWordWrap(False)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setItemDelegateForColumn(_COL_VERDICT, _VerdictItemDelegate(self.table))
        _apply_flex_column_widths(self.table)
        self.table.viewport().installEventFilter(self)

        self.table.itemSelectionChanged.connect(self._on_select)
        self.table.cellClicked.connect(self._on_cell_clicked)
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        table_section.addWidget(self.table, stretch=1)
        layout.addLayout(table_section, stretch=1)
        layout.addSpacing(12)

        selection_bar = QFrame()
        selection_bar.setObjectName("selectionBar")
        sel_layout = QHBoxLayout(selection_bar)
        sel_layout.setContentsMargins(16, 10, 16, 10)
        sel_layout.setSpacing(10)
        sel_text_col = QVBoxLayout()
        sel_text_col.setSpacing(2)
        sel_hint = QLabel("선택한 표현")
        sel_hint.setObjectName("selectionHint")
        self.selected_label = QLabel("")
        self.selected_label.setObjectName("selectedExpression")
        self.selected_label.setWordWrap(True)
        sel_text_col.addWidget(sel_hint)
        sel_text_col.addWidget(self.selected_label)
        sel_layout.addLayout(sel_text_col, stretch=1)
        btn_col = QHBoxLayout()
        btn_col.setSpacing(8)
        self.allow_btn = QPushButton("허용 목록에 추가")
        self.allow_btn.setToolTip(
            "선택한 표현의 원형을 허용 목록에 넣습니다. "
            "목표 단원과 관계없이 이후 검사에서 경고하지 않습니다."
        )
        self.allow_btn.setEnabled(False)
        self.copy_btn = QPushButton("복사")
        self.copy_btn.setProperty("variant", "secondary")
        self.copy_btn.setEnabled(False)
        btn_col.addWidget(self.allow_btn)
        btn_col.addWidget(self.copy_btn)
        sel_layout.addLayout(btn_col)
        layout.addWidget(selection_bar)

        self._issues: list[Issue] = []
        self._allowed: list[Issue] = []
        self._filter = "all"
        self._selected: Issue | None = None

        self.allow_btn.clicked.connect(self._allow)
        self.copy_btn.clicked.connect(self._copy)

    def _set_filter(self, key: str) -> None:
        self._filter = key
        for k, btn in self.filter_buttons.items():
            btn.setChecked(k == key)
        self._refresh_table()

    def show_result(self, result: AnalyzeResult | None) -> None:
        if not result:
            self._issues = []
            self._allowed = []
            self.completion_label.setVisible(False)
            for lbl in (
                self.lbl_target,
                self.lbl_issues,
                self.lbl_early,
                self.lbl_high,
                self.lbl_max,
            ):
                lbl.setText("-")
            self._refresh_table()
            return

        s = result.summary
        self.lbl_target.setText(s.target_display)
        self.lbl_issues.setText(str(s.issue_count))
        self.lbl_early.setText(str(s.before_introduced_count))
        self.lbl_high.setText(str(s.unknown_high_count))
        self.lbl_max.setText(s.max_known_display or "-")
        self._issues = result.issues
        self._allowed = result.allowed

        if s.issue_count == 0:
            self.completion_label.setText(f"검사 완료 — {s.target_display} 기준 문제 없음")
            self.completion_label.setVisible(True)
        else:
            self.completion_label.setVisible(False)

        self._refresh_table()

    def eventFilter(self, watched, event) -> bool:
        if watched is self.table.viewport() and event.type() == QEvent.Type.Resize:
            _apply_flex_column_widths(self.table)
            self._refresh_sentence_column()
        return super().eventFilter(watched, event)

    def _filtered_issues(self) -> list[Issue]:
        if self._filter == "all":
            return self._issues
        if self._filter == "allowed":
            return self._allowed
        return [i for i in self._issues if i.status.value == self._filter]

    def _refresh_table(self) -> None:
        filtered = self._filtered_issues()
        self.table.setRowCount(len(filtered))

        for row, issue in enumerate(filtered):
            label = status_label_ko(issue.status.value)
            values = [
                issue.surface,
                issue.lemma,
                label,
                issue.first_seen_display,
                issue.sentence,
            ]
            fg = STATUS_COLORS.get(issue.status.value)
            bg = STATUS_BG_COLORS.get(issue.status.value)

            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, issue)

                if col == _COL_SURFACE:
                    item.setFont(bold_font(self.table))

                if col == _COL_VERDICT:
                    if fg:
                        item.setForeground(QColor(fg))
                    if bg:
                        item.setBackground(QColor(bg))
                    item.setFont(bold_font(self.table))

                if col == _COL_SENTENCE:
                    item.setForeground(QColor("#1a6fdb"))

                self.table.setItem(row, col, item)
            self.table.setRowHeight(row, _ROW_HEIGHT)

        _apply_flex_column_widths(self.table)
        self._refresh_sentence_column()

    def _refresh_sentence_column(self) -> None:
        for row in range(self.table.rowCount()):
            item = self.table.item(row, _COL_SENTENCE)
            if not item:
                continue
            issue: Issue | None = item.data(Qt.ItemDataRole.UserRole)
            if not issue:
                continue
            full = issue.sentence
            display, truncated = _sentence_display(self.table, full)
            item.setText(display)
            item.setToolTip(full if truncated else "")

    def _on_select(self) -> None:
        items = self.table.selectedItems()
        if not items:
            self._selected = None
            self.selected_label.setText("—")
            self.allow_btn.setEnabled(False)
            self.copy_btn.setEnabled(False)
            return

        issue: Issue = items[0].data(Qt.ItemDataRole.UserRole)
        self._selected = issue
        self.selected_label.setText(_selection_display(issue))
        self.copy_btn.setEnabled(True)
        can_allow = issue.status.value not in ("allowed", "custom_allowed")
        self.allow_btn.setEnabled(can_allow)
        self.issue_selected.emit(issue)

    def _on_cell_clicked(self, row: int, col: int) -> None:
        if col != _COL_SENTENCE:
            return
        item = self.table.item(row, col)
        if not item:
            return
        issue: Issue = item.data(Qt.ItemDataRole.UserRole)
        if issue:
            self.sentence_highlight_requested.emit(issue)

    def _on_cell_double_clicked(self, row: int, col: int) -> None:
        if col != _COL_SURFACE:
            return
        item = self.table.item(row, col)
        if not item:
            return
        issue: Issue | None = item.data(Qt.ItemDataRole.UserRole)
        if issue and issue.lemma:
            self.lemma_lookup_requested.emit(issue.lemma)

    def _allow(self) -> None:
        if self._selected:
            self.allow_requested.emit(
                self._selected.lemma,
                self._selected.surface,
                self._selected.first_seen_display or "",
            )

    def _copy(self) -> None:
        if self._selected:
            from PySide6.QtWidgets import QApplication

            QApplication.clipboard().setText(_selection_display(self._selected))

    def clear(self) -> None:
        self.show_result(None)
        self._selected = None
        self.selected_label.setText("—")
        self.allow_btn.setEnabled(False)
        self.copy_btn.setEnabled(False)
