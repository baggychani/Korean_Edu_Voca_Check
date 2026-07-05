from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from kvocab_core.schemas import AnalyzeResult, Issue
from kvocab_core.status_labels import status_label_ko
from kvocab_desktop.style import STATUS_BG_COLORS, STATUS_COLORS
from kvocab_desktop.widgets.table_font import app_default_font, bold_font

# 표현만 약간 넓게, 문장(Stretch)은 남은 공간에서 자동으로 줄어듦
_EXPRESSION_COL_WIDTH = 112


def _stat_card(label: str, accent: str = "#111827") -> tuple[QFrame, QLabel]:

    card = QFrame()

    card.setObjectName("statCard")

    lay = QVBoxLayout(card)

    lay.setContentsMargins(14, 10, 14, 10)
    lay.setSpacing(3)

    value = QLabel("-")

    value.setObjectName("statValue")

    value.setStyleSheet(f"color: {accent};")

    caption = QLabel(label)

    caption.setObjectName("statLabel")

    caption.setWordWrap(True)

    lay.addWidget(value)

    lay.addWidget(caption)

    return card, value


class ResultsPanel(QWidget):
    issue_selected = Signal(object)

    allow_requested = Signal(str)

    def __init__(self, parent=None) -> None:

        super().__init__(parent)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(0, 4, 0, 0)

        layout.setSpacing(16)

        summary_title = QLabel("검사 요약")

        summary_title.setObjectName("sectionTitle")

        layout.addWidget(summary_title)

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

        list_header = QHBoxLayout()

        list_header.setSpacing(8)

        list_title = QLabel("검사 결과")

        list_title.setObjectName("sectionTitle")

        list_header.addWidget(list_title)

        list_header.addStretch()

        layout.addLayout(list_header)

        chip_row = QHBoxLayout()

        chip_row.setSpacing(6)

        self.filter_buttons: dict[str, QPushButton] = {}

        for key, label in [
            ("all", "전체"),
            ("before_introduced", "아직 이릅니다"),
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

        layout.addLayout(chip_row)

        self.completion_label = QLabel("")
        self.completion_label.setObjectName("completionStatus")
        self.completion_label.setWordWrap(True)
        self.completion_label.setVisible(False)
        layout.addWidget(self.completion_label)

        self.table = QTableWidget(0, 6)

        self.table.setHorizontalHeaderLabels(
            ["표현", "원형", "판정", "처음 나오는 곳", "이유", "문장"]
        )

        self.table.verticalHeader().setVisible(False)

        self.table.setAlternatingRowColors(True)

        self.table.setShowGrid(False)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFont(app_default_font())

        self.table.setWordWrap(False)

        header = self.table.horizontalHeader()

        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        for col in (1, 2, 3, 4):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.resizeSection(0, _EXPRESSION_COL_WIDTH)

        self.table.itemSelectionChanged.connect(self._on_select)

        layout.addWidget(self.table, stretch=1)

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
        self.allow_btn = QPushButton("이번부터 항상 허용")
        self.allow_btn.setEnabled(False)
        self.copy_btn = QPushButton("복사")
        self.copy_btn.setProperty("variant", "secondary")
        self.copy_btn.setEnabled(False)
        btn_col.addWidget(self.allow_btn)
        btn_col.addWidget(self.copy_btn)
        sel_layout.addLayout(btn_col)
        layout.addWidget(selection_bar)

        self._issues: list[Issue] = []

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

        if s.issue_count == 0:
            self.completion_label.setText(f"검사 완료 — {s.target_display} 기준 문제 없음")
            self.completion_label.setVisible(True)
        else:
            self.completion_label.setVisible(False)

        self._refresh_table()

    def _refresh_table(self) -> None:

        filtered = self._issues

        if self._filter != "all":
            filtered = [i for i in self._issues if i.status.value == self._filter]

        self.table.setRowCount(len(filtered))

        for row, issue in enumerate(filtered):
            label = status_label_ko(issue.status.value)

            values = [
                issue.surface,
                issue.lemma,
                label,
                issue.first_seen_display,
                issue.reason,
                issue.sentence,
            ]

            fg = STATUS_COLORS.get(issue.status.value)

            bg = STATUS_BG_COLORS.get(issue.status.value)

            for col, val in enumerate(values):
                item = QTableWidgetItem(val)

                item.setData(Qt.ItemDataRole.UserRole, issue)

                if col == 0:
                    item.setFont(bold_font(self.table))

                if col == 2:
                    if fg:
                        item.setForeground(QColor(fg))

                    if bg:
                        item.setBackground(QColor(bg))

                    item.setFont(bold_font(self.table))

                self.table.setItem(row, col, item)

            self.table.setRowHeight(row, 38)

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

        self.selected_label.setText(issue.surface)

        self.allow_btn.setEnabled(True)

        self.copy_btn.setEnabled(True)

        self.issue_selected.emit(issue)

    def _allow(self) -> None:

        if self._selected:
            self.allow_requested.emit(self._selected.surface)

    def _copy(self) -> None:

        if self._selected:
            from PySide6.QtWidgets import QApplication

            QApplication.clipboard().setText(self._selected.surface)

    def clear(self) -> None:

        self.show_result(None)

        self._selected = None

        self.selected_label.setText("—")

        self.allow_btn.setEnabled(False)

        self.copy_btn.setEnabled(False)
