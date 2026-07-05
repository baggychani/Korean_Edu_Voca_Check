from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
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
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)

        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        title = QLabel("텍스트 입력")
        title.setObjectName("sectionTitle")
        hint = QLabel("검사할 한국어 문장·지문을 붙여넣거나 파일을 여세요.")
        hint.setObjectName("sectionHint")
        header_row.addWidget(title)
        header_row.addStretch()
        header_row.addWidget(hint)
        layout.addLayout(header_row)

        self.text_edit = QTextEdit()
        self.text_edit.setObjectName("inputArea")
        self.text_edit.setPlaceholderText("검사할 한국어 텍스트를 붙여넣으세요…")
        self.text_edit.setMinimumHeight(117)
        self.text_edit.setMaximumHeight(180)
        layout.addWidget(self.text_edit)

        btn_wrap = QWidget()
        btn_wrap.setObjectName("analyzeActions")
        btn_row = QHBoxLayout(btn_wrap)
        btn_row.setContentsMargins(0, 0, 0, 0)
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
        layout.addWidget(btn_wrap)

        outer.addWidget(card)

        self.run_btn.clicked.connect(self.analyze_requested.emit)
        self.open_btn.clicked.connect(self._open_file)
        self.clear_btn.clicked.connect(self._clear)
        self.text_edit.textChanged.connect(self.clear_highlight)

    def get_text(self) -> str:
        return self.text_edit.toPlainText()

    def set_text(self, text: str) -> None:
        self.text_edit.setPlainText(text)
        self.clear_highlight()

    def clear_highlight(self) -> None:
        self.text_edit.setExtraSelections([])

    def highlight_issue(self, issue) -> None:
        """입력창에서 해당 이슈의 문장 구간을 하이라이트한다."""
        text = self.get_text()
        span = self._sentence_span(text, issue)
        if not span:
            return
        start, end = span

        hl = QTextCursor(self.text_edit.document())
        hl.setPosition(start)
        hl.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#fff176"))
        fmt.setForeground(QColor("#111827"))
        selection = QTextEdit.ExtraSelection()
        selection.cursor = hl
        selection.format = fmt
        self.text_edit.setExtraSelections([selection])

        view = self.text_edit.textCursor()
        view.setPosition(start)
        view.clearSelection()
        self.text_edit.setTextCursor(view)
        self.text_edit.ensureCursorVisible()

    @staticmethod
    def _sentence_span(text: str, issue) -> tuple[int, int] | None:
        sent = (issue.sentence or "").strip()
        if sent:
            pos = 0
            fallback: tuple[int, int] | None = None
            while True:
                idx = text.find(sent, pos)
                if idx < 0:
                    break
                span = (idx, idx + len(sent))
                if 0 <= issue.start < issue.end and idx <= issue.start < idx + len(sent):
                    return span
                fallback = fallback or span
                pos = idx + 1
            if fallback:
                return fallback
        if issue.start < 0 or issue.end <= issue.start or issue.end > len(text):
            return None
        left = max(text.rfind(ch, 0, issue.start) for ch in ".?!\n")
        right_candidates = [text.find(ch, issue.end) for ch in ".?!\n"]
        right_candidates = [r for r in right_candidates if r >= 0]
        right = min(right_candidates) + 1 if right_candidates else len(text)
        start, end = left + 1, right
        end = min(end, len(text))
        if start >= end:
            return issue.start, issue.end
        return start, end

    def _clear(self) -> None:
        self.text_edit.clear()
        self.clear_highlight()
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
