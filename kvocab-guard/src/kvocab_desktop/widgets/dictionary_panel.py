from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from kvocab_core.schemas import LexemeSearchResult
from kvocab_core.status_labels import review_label_ko, source_label_ko
from kvocab_desktop.widgets.table_font import bold_font


class DictionaryPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(12)

        row = QHBoxLayout()
        row.setSpacing(8)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("어휘 검색  (예: 가입하다)")
        self.search_btn = QPushButton("검색")
        self.search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        row.addWidget(self.search_input)
        row.addWidget(self.search_btn)
        layout.addLayout(row)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["표제어", "처음 등장", "페이지", "뜻", "출처", "검토 상태"]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table, stretch=1)

        detail_card = QFrame()
        detail_card.setObjectName("card")
        dlay = QVBoxLayout(detail_card)
        dlay.setContentsMargins(16, 12, 16, 12)
        dlay.setSpacing(6)
        self.detail_title = QLabel("상세 정보")
        self.detail_title.setObjectName("detailTitle")
        self.detail = QLabel("검색 결과를 선택하세요.")
        self.detail.setWordWrap(True)
        self.detail.setStyleSheet("color: #475569;")
        self.detail.setTextFormat(Qt.TextFormat.RichText)
        dlay.addWidget(self.detail_title)
        dlay.addWidget(self.detail)
        layout.addWidget(detail_card)

        self.search_btn.clicked.connect(lambda: self.search_requested())
        self.search_input.returnPressed.connect(lambda: self.search_requested())
        self.table.itemSelectionChanged.connect(self._on_select)
        self._results: list[LexemeSearchResult] = []
        self._search_callback = None

    def set_search_callback(self, cb) -> None:
        self._search_callback = cb

    def search_requested(self) -> None:
        if self._search_callback:
            self._search_callback(self.search_input.text().strip())

    def show_results(self, results: list[LexemeSearchResult]) -> None:
        self._results = results
        self.table.setRowCount(len(results))
        for row, r in enumerate(results):
            first = f"{r.first_level} {r.first_lesson}" if r.first_level else "-"
            page = f"p.{r.first_page}" if r.first_page else "-"
            src = source_label_ko(r.source_type)
            rev = review_label_ko(r.review_status)
            for col, val in enumerate([r.lemma, first, page, r.gloss_en or "", src, rev]):
                item = QTableWidgetItem(val)
                if col == 0:
                    item.setFont(bold_font(self.table))
                if col == 5 and r.review_status == "draft_ocr_needs_manual_review":
                    from PySide6.QtGui import QColor

                    item.setForeground(QColor("#ca8a04"))
                self.table.setItem(row, col, item)
            self.table.setRowHeight(row, 34)

    def _on_select(self) -> None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self._results):
            return
        r = self._results[row]
        verdict = r.verdict_label_ko or "-"
        verdict_color = "#16a34a" if verdict == "사용 가능" else "#dc2626"
        others = (
            "<br>".join(f"&nbsp;&nbsp;· {o}" for o in r.other_occurrences)
            if r.other_occurrences
            else "&nbsp;&nbsp;없음"
        )
        badge = ""
        if r.review_status == "draft_ocr_needs_manual_review":
            badge = " <span style='color:#ca8a04; font-size:11px;'>[검토 중]</span>"
        self.detail_title.setText(r.lemma)
        self.detail.setText(
            f"<b>{r.first_level} {r.first_lesson}</b> · p.{r.first_page}{badge}<br>"
            f"뜻: {r.gloss_en or '-'}<br>"
            f"판정: <b style='color:{verdict_color};'>{verdict}</b><br>"
            f"다른 등장:<br>{others}"
        )
