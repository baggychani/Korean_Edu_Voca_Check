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
from kvocab_desktop.widgets.table_font import app_default_font

# 교재·단원·페이지 고정, 뜻 2배(168→336), 표제어는 Stretch로 남은 공간
_COL_WIDTHS = {1: 72, 2: 72, 3: 80, 4: 336}


class DictionaryPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(16)

        title = QLabel("어휘 검색")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        search_card = QFrame()
        search_card.setObjectName("card")
        search_layout = QHBoxLayout(search_card)
        search_layout.setContentsMargins(16, 14, 16, 14)
        search_layout.setSpacing(10)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("표제어 검색  (예: 가입하다)")
        self.search_btn = QPushButton("검색")
        self.search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        search_layout.addWidget(self.search_input, stretch=1)
        search_layout.addWidget(self.search_btn)
        layout.addWidget(search_card)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["표제어", "교재", "단원", "페이지", "뜻"])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFont(app_default_font())
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in (1, 2, 3, 4):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            header.resizeSection(col, _COL_WIDTHS[col])
        layout.addWidget(self.table, stretch=1)

        detail_card = QFrame()
        detail_card.setObjectName("card")
        dlay = QVBoxLayout(detail_card)
        dlay.setContentsMargins(18, 14, 18, 14)
        dlay.setSpacing(8)
        self.detail_title = QLabel("상세 정보")
        self.detail_title.setObjectName("detailTitle")
        self.detail = QLabel("검색 결과를 선택하세요.")
        self.detail.setWordWrap(True)
        self.detail.setStyleSheet("color: #4b5563; font-size: 13px;")
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

    def search_for(self, query: str) -> None:
        self.search_input.setText(query)
        self.search_requested()

    def show_results(self, results: list[LexemeSearchResult]) -> None:
        self._results = results
        self.table.setRowCount(len(results))
        for row, r in enumerate(results):
            level = r.first_level or "-"
            lesson = r.first_lesson or "-"
            page = f"p.{r.first_page}" if r.first_page else "-"
            for col, val in enumerate([r.lemma, level, lesson, page, r.gloss_en or ""]):
                self.table.setItem(row, col, QTableWidgetItem(val))
            self.table.setRowHeight(row, 38)

    def _on_select(self) -> None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self._results):
            return
        r = self._results[row]
        verdict = r.verdict_label_ko or "-"
        verdict_color = "#16a34a" if verdict == "사용 가능" else "#dc2626"
        if r.other_occurrences:
            others = " · ".join(r.other_occurrences)
        else:
            others = "없음"
        self.detail_title.setText(r.lemma)
        self.detail.setText(
            f"판정: <b style='color:{verdict_color};'>{verdict}</b><br>다른 등장: {others}"
        )
