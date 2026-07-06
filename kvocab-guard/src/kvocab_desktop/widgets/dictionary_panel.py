from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
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

from kvocab_core.normalization import lemma_gana_sort_key
from kvocab_core.schemas import LexemeSearchResult
from kvocab_desktop.widgets.table_font import TABLE_ROW_HEIGHT, configure_data_table

# 레벨·단원·페이지 고정, 뜻 2배, 표제어는 Stretch
_COL_WIDTHS = {1: 84, 2: 72, 3: 80, 4: 336}
_COL_LEMMA = 0
_COL_LEVEL = 1
_SORTABLE_COLUMNS = frozenset({_COL_LEMMA, _COL_LEVEL})


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
        self.search_input.setPlaceholderText("표제어 검색")
        self.search_btn = QPushButton("검색")
        self.search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        search_layout.addWidget(self.search_input, stretch=1)
        search_layout.addWidget(self.search_btn)
        layout.addWidget(search_card)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["표제어", "레벨", "단원", "페이지", "뜻"])
        configure_data_table(self.table)
        header = self.table.horizontalHeader()
        header.setSortIndicatorShown(True)
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self._on_header_clicked)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in (1, 2, 3, 4):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            header.resizeSection(col, _COL_WIDTHS[col])
        layout.addWidget(self.table, stretch=1)

        self._sort_column = _COL_LEMMA
        self._sort_ascending = True
        self._update_sort_indicator()

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
        self._display_results: list[LexemeSearchResult] = []
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
        self._render_table()

    def _on_header_clicked(self, column: int) -> None:
        if column not in _SORTABLE_COLUMNS:
            self._update_sort_indicator()
            return
        if self._sort_column == column:
            self._sort_ascending = not self._sort_ascending
        else:
            self._sort_column = column
            self._sort_ascending = True
        self._update_sort_indicator()
        self._render_table()

    def _update_sort_indicator(self) -> None:
        order = (
            Qt.SortOrder.AscendingOrder if self._sort_ascending else Qt.SortOrder.DescendingOrder
        )
        self.table.horizontalHeader().setSortIndicator(self._sort_column, order)

    def _sorted_results(self) -> list[LexemeSearchResult]:
        rows = list(self._results)
        if self._sort_column == _COL_LEMMA:
            rows.sort(
                key=lambda r: lemma_gana_sort_key(r.lemma),
                reverse=not self._sort_ascending,
            )
        elif self._sort_column == _COL_LEVEL:
            rows.sort(
                key=lambda r: (
                    r.first_order_index if r.first_order_index is not None else 999_999,
                    r.first_level or "",
                ),
                reverse=not self._sort_ascending,
            )
        return rows

    def _render_table(self) -> None:
        rows = self._sorted_results()
        self._display_results = rows
        self.table.setRowCount(len(rows))
        for row, r in enumerate(rows):
            level = r.first_level or "-"
            lesson = r.first_lesson or "-"
            page = f"p.{r.first_page}" if r.first_page else "-"
            for col, val in enumerate([r.lemma, level, lesson, page, r.gloss_en or ""]):
                item = QTableWidgetItem(val)
                if col == 0:
                    item.setData(Qt.ItemDataRole.UserRole, r)
                self.table.setItem(row, col, item)
            self.table.setRowHeight(row, TABLE_ROW_HEIGHT)

    def _on_select(self) -> None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self._display_results):
            return
        item = self.table.item(row, 0)
        r = item.data(Qt.ItemDataRole.UserRole) if item else self._display_results[row]
        if not r:
            r = self._display_results[row]
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
