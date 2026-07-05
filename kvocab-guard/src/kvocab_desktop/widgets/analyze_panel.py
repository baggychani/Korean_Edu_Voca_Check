from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from kvocab_core.document_extractors import extract_document


class AnalyzePanel(QWidget):
    analyze_requested = Signal()
    file_loaded = Signal(str)
    clear_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("검사할 한국어 텍스트를 붙여넣으세요…")
        self.text_edit.setMinimumHeight(140)
        self.text_edit.setMaximumHeight(220)
        layout.addWidget(self.text_edit)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.run_btn = QPushButton("텍스트 검사")
        self.run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_btn = QPushButton("파일 열기")
        self.open_btn.setProperty("variant", "secondary")
        self.open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn = QPushButton("결과 지우기")
        self.clear_btn.setProperty("variant", "secondary")
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.open_btn)
        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.run_btn.clicked.connect(self.analyze_requested.emit)
        self.open_btn.clicked.connect(self._open_file)
        self.clear_btn.clicked.connect(self._clear)

    def get_text(self) -> str:
        return self.text_edit.toPlainText()

    def set_text(self, text: str) -> None:
        self.text_edit.setPlainText(text)

    def _clear(self) -> None:
        self.text_edit.clear()
        self.clear_requested.emit()

    def _open_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "파일 열기",
            "",
            "문서 (*.txt *.pdf *.hwpx *.hwp *.docx);;모든 파일 (*.*)",
        )
        if not path:
            return
        try:
            doc = extract_document(path)
            if doc.message:
                self.set_text(doc.message)
            else:
                self.set_text(doc.text)
            self.file_loaded.emit(path)
        except Exception as exc:
            self.set_text(f"파일을 열 수 없습니다: {exc}")
