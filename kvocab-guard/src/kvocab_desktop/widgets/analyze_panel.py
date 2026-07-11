from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QKeySequence, QShortcut, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from kvocab_core.document_extractors import extract_document
from kvocab_desktop.layout_metrics import ANALYZE_INPUT_MAX_HEIGHT, ANALYZE_INPUT_MIN_HEIGHT
from kvocab_desktop.style import STATUS_COLORS


class PlainTextEdit(QTextEdit):
    """Text editor that discards rich-text formatting when content is pasted."""

    analyze_requested = Signal()

    def insertFromMimeData(self, source) -> None:  # noqa: N802
        if source.hasText():
            self.insertPlainText(source.text())
            return
        super().insertFromMimeData(source)

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if (
            event.modifiers() & Qt.KeyboardModifier.ControlModifier
            and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
        ):
            self.analyze_requested.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class AnalyzePanel(QWidget):
    analyze_requested = Signal()
    file_loaded = Signal(str)
    clear_requested = Signal()
    content_edited = Signal()

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

        input_frame = QFrame()
        input_frame.setObjectName("inputFrame")
        input_frame.setMinimumHeight(ANALYZE_INPUT_MIN_HEIGHT + 2)
        input_frame.setMaximumHeight(ANALYZE_INPUT_MAX_HEIGHT + 2)
        input_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        input_frame_layout = QVBoxLayout(input_frame)
        input_frame_layout.setContentsMargins(1, 1, 1, 1)
        input_frame_layout.setSpacing(0)

        self.text_edit = PlainTextEdit()
        self.text_edit.setAcceptRichText(False)
        self.text_edit.setObjectName("inputArea")
        self.text_edit.setFrameShape(QFrame.Shape.NoFrame)
        self.text_edit.setPlaceholderText("검사할 한국어 텍스트를 붙여넣으세요…")
        self.text_edit.setMinimumHeight(ANALYZE_INPUT_MIN_HEIGHT)
        self.text_edit.setMaximumHeight(ANALYZE_INPUT_MAX_HEIGHT)
        self.text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        input_frame_layout.addWidget(self.text_edit)
        layout.addWidget(input_frame)

        btn_wrap = QWidget()
        btn_wrap.setObjectName("analyzeActions")
        btn_row = QHBoxLayout(btn_wrap)
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(8)
        self.run_btn = QPushButton("텍스트 검사")
        self.run_btn.setObjectName("primaryAnalyzeButton")
        self.run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_btn = QPushButton("파일 열기")
        self.open_btn.setProperty("variant", "secondary")
        self.open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn = QPushButton("결과 지우기")
        self.clear_btn.setProperty("variant", "secondary")
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.undo_btn = QPushButton("되돌리기")
        self.undo_btn.setProperty("variant", "secondary")
        self.undo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.undo_btn.setEnabled(False)
        self.redo_btn = QPushButton("다시 실행")
        self.redo_btn.setProperty("variant", "secondary")
        self.redo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.redo_btn.setEnabled(False)
        btn_row.addWidget(self.open_btn)
        btn_row.addWidget(self.clear_btn)
        btn_row.addWidget(self.undo_btn)
        btn_row.addWidget(self.redo_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.run_btn)
        layout.addWidget(btn_wrap)

        outer.addWidget(card)

        self._red_selections: list[QTextEdit.ExtraSelection] = []
        self._sentence_selection: QTextEdit.ExtraSelection | None = None

        self.run_btn.clicked.connect(self.analyze_requested.emit)
        self.open_btn.clicked.connect(self._open_file)
        self.clear_btn.clicked.connect(self._clear)
        self.undo_btn.clicked.connect(self._undo_text)
        self.redo_btn.clicked.connect(self._redo_text)
        self.text_edit.undoAvailable.connect(self.undo_btn.setEnabled)
        self.text_edit.redoAvailable.connect(self.redo_btn.setEnabled)
        self.text_edit.textChanged.connect(self._on_text_changed)
        self.text_edit.analyze_requested.connect(self.analyze_requested.emit)

        self._undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        self._undo_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self._undo_shortcut.activated.connect(self._undo_text)
        self._redo_shortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        self._redo_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self._redo_shortcut.activated.connect(self._redo_text)
        self._redo_alt_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Z"), self)
        self._redo_alt_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self._redo_alt_shortcut.activated.connect(self._redo_text)

    def get_text(self) -> str:
        return self.text_edit.toPlainText()

    def set_text(self, text: str) -> None:
        self.text_edit.setPlainText(text)
        self.clear_marks()
        self._sync_history_buttons()

    def _apply_extra_selections(self) -> None:
        # 노란 문장 배경 먼저, 빨간 글자를 위에 올려 겹침 구간도 색 유지
        selections: list[QTextEdit.ExtraSelection] = []
        if self._sentence_selection is not None:
            selections.append(self._sentence_selection)
        selections.extend(self._red_selections)
        self.text_edit.setExtraSelections(selections)

    def clear_highlight(self) -> None:
        self._sentence_selection = None
        self._apply_extra_selections()

    def clear_before_introduced_marks(self) -> None:
        self._red_selections = []

    def clear_marks(self) -> None:
        if not self._red_selections and self._sentence_selection is None:
            return
        self._red_selections = []
        self._sentence_selection = None
        self.text_edit.setExtraSelections([])

    def _on_text_changed(self) -> None:
        self.clear_marks()
        self.content_edited.emit()

    def _sync_history_buttons(self) -> None:
        doc = self.text_edit.document()
        self.undo_btn.setEnabled(doc.isUndoAvailable())
        self.redo_btn.setEnabled(doc.isRedoAvailable())

    def _undo_text(self) -> None:
        if self.text_edit.document().isUndoAvailable():
            self.text_edit.undo()
            self.text_edit.setFocus()
        self._sync_history_buttons()

    def _redo_text(self) -> None:
        if self.text_edit.document().isRedoAvailable():
            self.text_edit.redo()
            self.text_edit.setFocus()
        self._sync_history_buttons()

    def apply_before_introduced_marks(self, issues) -> None:
        from kvocab_core.schemas import IssueStatus

        self._red_selections = []
        text = self.get_text()
        if not text:
            self._apply_extra_selections()
            return

        fmt = QTextCharFormat()
        fmt.setForeground(QColor(STATUS_COLORS["before_introduced"]))
        doc = self.text_edit.document()
        for issue in issues:
            if issue.status != IssueStatus.before_introduced:
                continue
            span = self._surface_span(text, issue)
            if not span:
                continue
            start, end = span
            cursor = QTextCursor(doc)
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            sel = QTextEdit.ExtraSelection()
            sel.cursor = cursor
            sel.format = fmt
            self._red_selections.append(sel)
        self._apply_extra_selections()

    def highlight_issue(self, issue) -> None:
        """입력창에서 해당 이슈 문장 구간을 노란 배경으로 표시한다."""
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
        fmt.clearForeground()
        selection = QTextEdit.ExtraSelection()
        selection.cursor = hl
        selection.format = fmt
        self._sentence_selection = selection
        self._apply_extra_selections()

        view = self.text_edit.textCursor()
        view.setPosition(start)
        view.clearSelection()
        self.text_edit.setTextCursor(view)
        self.text_edit.ensureCursorVisible()

    @staticmethod
    def _surface_span(text: str, issue) -> tuple[int, int] | None:
        """표현(어절) 단위 구간 — issue.surface 기준."""
        surface = (issue.surface or "").strip()
        if not surface:
            if 0 <= issue.start < issue.end <= len(text):
                return issue.start, issue.end
            return None

        search_from = max(0, issue.start - len(surface))
        pos = search_from
        while True:
            idx = text.find(surface, pos)
            if idx < 0:
                break
            end = idx + len(surface)
            if idx <= issue.start < end:
                return idx, end
            pos = idx + 1

        idx = text.find(surface)
        if idx >= 0:
            return idx, idx + len(surface)

        if 0 <= issue.start < issue.end <= len(text):
            return issue.start, issue.end
        return None

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
        self.clear_marks()
        self._sync_history_buttons()
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
            QMessageBox.critical(self, "파일 열기 오류", f"파일을 열 수 없습니다:\n{exc}")
