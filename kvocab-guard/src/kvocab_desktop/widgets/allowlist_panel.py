from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

_ALLOW_TYPE_LABELS = [
    ("global", "전체"),
    ("project", "프로젝트"),
    ("document", "문서"),
]


class AllowlistPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(16)

        title = QLabel("허용어 관리")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        form_card = QFrame()
        form_card.setObjectName("card")
        form = QHBoxLayout(form_card)
        form.setContentsMargins(16, 14, 16, 14)
        form.setSpacing(8)
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("허용할 표현")
        self.type_combo = QComboBox()
        for code, label in _ALLOW_TYPE_LABELS:
            self.type_combo.addItem(label, code)
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("메모 (선택)")
        self.add_btn = QPushButton("추가")
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.del_btn = QPushButton("삭제")
        self.del_btn.setProperty("variant", "secondary")
        self.del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        form.addWidget(self.text_input, 2)
        form.addWidget(self.type_combo, 1)
        form.addWidget(self.note_input, 2)
        form.addWidget(self.add_btn)
        form.addWidget(self.del_btn)
        layout.addWidget(form_card)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["텍스트", "유형", "메모", "ID"])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnHidden(3, True)
        layout.addWidget(self.table, stretch=1)

        self._add_cb = None
        self._delete_cb = None
        self.add_btn.clicked.connect(self._add)
        self.del_btn.clicked.connect(self._delete)
        self.text_input.returnPressed.connect(self._add)

    def set_callbacks(self, refresh, add, delete) -> None:
        self._add_cb = add
        self._delete_cb = delete

    def show_items(self, items) -> None:
        type_labels = dict(_ALLOW_TYPE_LABELS)
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.table.setItem(row, 0, QTableWidgetItem(item.text))
            self.table.setItem(
                row, 1, QTableWidgetItem(type_labels.get(item.allow_type, item.allow_type))
            )
            self.table.setItem(row, 2, QTableWidgetItem(item.note or ""))
            self.table.setItem(row, 3, QTableWidgetItem(str(item.id)))
            self.table.setRowHeight(row, 34)

    def _add(self) -> None:
        if self._add_cb and self.text_input.text().strip():
            self._add_cb(
                self.text_input.text().strip(),
                self.type_combo.currentData(),
                self.note_input.text().strip() or None,
            )
            self.text_input.clear()
            self.note_input.clear()

    def _delete(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return
        id_item = self.table.item(row, 3)
        if id_item and self._delete_cb:
            self._delete_cb(int(id_item.text()))
