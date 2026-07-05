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
from kvocab_desktop.widgets.table_font import bold_font
from kvocab_desktop.style import STATUS_BG_COLORS, STATUS_COLORS


def _stat_card(label: str, accent: str = "#0f172a") -> tuple[QFrame, QLabel]:
    card = QFrame()
    card.setObjectName("statCard")
    lay = QVBoxLayout(card)
    lay.setContentsMargins(16, 12, 16, 12)
    lay.setSpacing(2)
    value = QLabel("-")
    value.setObjectName("statValue")
    value.setStyleSheet(f"color: {accent};")
    caption = QLabel(label)
    caption.setObjectName("statLabel")
    lay.addWidget(value)
    lay.addWidget(caption)
    return card, value


class ResultsPanel(QWidget):
    issue_selected = Signal(object)
    allow_requested = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # --- summary stat cards (horizontal) ---
        stats_row = QHBoxLayout()
        stats_row.setSpacing(10)
        card, self.lbl_target = _stat_card("목표 단원", "#4f46e5")
        stats_row.addWidget(card, 1)
        card, self.lbl_issues = _stat_card("경고", "#0f172a")
        stats_row.addWidget(card, 1)
        card, self.lbl_early = _stat_card("아직 이릅니다", STATUS_COLORS["before_introduced"])
        stats_row.addWidget(card, 1)
        card, self.lbl_high = _stat_card("교재 외 · 난이도 높음", STATUS_COLORS["unknown_high"])
        stats_row.addWidget(card, 1)
        card, self.lbl_max = _stat_card("확인된 최고 단원", "#0f172a")
        stats_row.addWidget(card, 1)
        layout.addLayout(stats_row)

        # --- filter chips ---
        chip_row = QHBoxLayout()
        chip_row.setSpacing(8)
        self.filter_buttons: dict[str, QPushButton] = {}
        for key, label in [
            ("all", "전체"),
            ("before_introduced", "아직 이릅니다"),
            ("unknown_high", "교재 외 · 난이도 높음"),
            ("unknown_medium", "교재 외 · 검토 필요"),
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

        # --- issue table ---
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
        self.table.setWordWrap(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.table.itemSelectionChanged.connect(self._on_select)
        layout.addWidget(self.table, stretch=1)

        # --- detail card ---
        detail = QFrame()
        detail.setObjectName("card")
        dlay = QVBoxLayout(detail)
        dlay.setContentsMargins(16, 12, 16, 12)
        dlay.setSpacing(8)
        self.detail_title = QLabel("상세 정보")
        self.detail_title.setObjectName("detailTitle")
        self.detail_label = QLabel("항목을 선택하면 상세 정보가 표시됩니다.")
        self.detail_label.setWordWrap(True)
        self.detail_label.setStyleSheet("color: #475569; line-height: 150%;")
        dlay.addWidget(self.detail_title)
        dlay.addWidget(self.detail_label)
        btn_row = QHBoxLayout()
        self.allow_btn = QPushButton("이번부터 항상 허용")
        self.copy_btn = QPushButton("복사")
        self.copy_btn.setProperty("variant", "secondary")
        btn_row.addWidget(self.allow_btn)
        btn_row.addWidget(self.copy_btn)
        btn_row.addStretch()
        dlay.addLayout(btn_row)
        layout.addWidget(detail)

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
            for lbl in (self.lbl_target, self.lbl_issues, self.lbl_early, self.lbl_high, self.lbl_max):
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
            self.table.setRowHeight(row, 36)

    def _on_select(self) -> None:
        items = self.table.selectedItems()
        if not items:
            return
        issue: Issue = items[0].data(Qt.ItemDataRole.UserRole)
        self._selected = issue
        sug = ", ".join(issue.suggestions) if issue.suggestions else "-"
        color = STATUS_COLORS.get(issue.status.value, "#0f172a")
        self.detail_title.setText(issue.surface)
        self.detail_label.setText(
            f"원형: {issue.lemma}    ·    "
            f"판정: <b style='color:{color};'>{status_label_ko(issue.status.value)}</b><br>"
            f"이유: {issue.reason}<br>"
            f"처음 나오는 곳: {issue.first_seen_display or '-'}<br>"
            f"제안: {sug}"
        )
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
        self.detail_title.setText("상세 정보")
        self.detail_label.setText("항목을 선택하면 상세 정보가 표시됩니다.")
