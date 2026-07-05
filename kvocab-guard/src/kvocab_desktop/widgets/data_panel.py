from __future__ import annotations

import os
import subprocess
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from kvocab_core.config import DEFAULT_DB_PATH

_COUNT_LABELS = {
    "levels": "레벨",
    "lessons": "단원",
    "lexemes": "어휘",
    "occurrences": "등장 위치",
    "surface_forms": "표면형",
    "allowlist": "허용어",
    "unmapped": "매핑 실패",
}


def _stat_card(label: str) -> tuple[QFrame, QLabel]:
    card = QFrame()
    card.setObjectName("statCard")
    lay = QVBoxLayout(card)
    lay.setContentsMargins(16, 12, 16, 12)
    lay.setSpacing(2)
    value = QLabel("-")
    value.setObjectName("statValue")
    caption = QLabel(label)
    caption.setObjectName("statLabel")
    lay.addWidget(value)
    lay.addWidget(caption)
    return card, value


class DataPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(12)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.seed_btn = QPushButton("DB 초기화 및 seed 불러오기")
        self.seed_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.import_btn = QPushButton("XLSX 가져오기")
        self.import_btn.setProperty("variant", "secondary")
        self.import_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_btn = QPushButton("DB 위치 열기")
        self.open_btn.setProperty("variant", "secondary")
        self.open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(self.seed_btn)
        btn_row.addWidget(self.import_btn)
        btn_row.addWidget(self.open_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._value_labels: dict[str, QLabel] = {}
        grid = QGridLayout()
        grid.setSpacing(10)
        for i, (key, label) in enumerate(_COUNT_LABELS.items()):
            card, value = _stat_card(label)
            self._value_labels[key] = value
            grid.addWidget(card, i // 4, i % 4)
        layout.addLayout(grid)

        self.db_path_label = QLabel(f"DB 경로: {DEFAULT_DB_PATH}")
        self.db_path_label.setStyleSheet("color: #64748b; font-size: 11px;")
        self.db_path_label.setWordWrap(True)
        layout.addWidget(self.db_path_label)
        layout.addStretch()

        self._seed_cb = None
        self._import_cb = None
        self.seed_btn.clicked.connect(lambda: self._seed_cb and self._seed_cb())
        self.import_btn.clicked.connect(lambda: self._import_cb and self._import_cb())
        self.open_btn.clicked.connect(self._open_db_folder)

    def set_callbacks(self, seed_cb, import_cb) -> None:
        self._seed_cb = seed_cb
        self._import_cb = import_cb

    def show_counts(self, counts: dict[str, int]) -> None:
        for key, value in counts.items():
            if key in self._value_labels:
                self._value_labels[key].setText(str(value))

    def _open_db_folder(self) -> None:
        folder = str(DEFAULT_DB_PATH.parent)
        if sys.platform == "win32":
            os.startfile(folder)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.run(["open", folder], check=False)
        else:
            subprocess.run(["xdg-open", folder], check=False)
