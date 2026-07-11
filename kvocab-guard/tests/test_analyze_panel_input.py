from __future__ import annotations

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QMimeData, Qt
from PySide6.QtTest import QSignalSpy, QTest
from PySide6.QtWidgets import QApplication

from kvocab_desktop.widgets.analyze_panel import AnalyzePanel


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv[:1])
    return app


def test_analyze_panel_undo_redo_buttons_and_shortcuts() -> None:
    app = _app()
    panel = AnalyzePanel()
    panel.show()
    edit = panel.text_edit
    edit.setFocus()

    edit.insertPlainText("abc")
    app.processEvents()

    assert edit.toPlainText() == "abc"
    assert panel.undo_btn.isEnabled()
    assert not panel.redo_btn.isEnabled()

    QTest.keySequence(panel, "Ctrl+Z")
    app.processEvents()

    assert edit.toPlainText() == ""
    assert not panel.undo_btn.isEnabled()
    assert panel.redo_btn.isEnabled()

    QTest.keySequence(panel, "Ctrl+Y")
    app.processEvents()

    assert edit.toPlainText() == "abc"
    assert panel.undo_btn.isEnabled()
    assert not panel.redo_btn.isEnabled()

    panel.undo_btn.click()
    app.processEvents()

    assert edit.toPlainText() == ""
    assert panel.redo_btn.isEnabled()

    panel.redo_btn.click()
    app.processEvents()

    assert edit.toPlainText() == "abc"
    assert panel.undo_btn.isEnabled()


def test_analyze_panel_reflects_unicode_text_changes() -> None:
    app = _app()
    panel = AnalyzePanel()
    panel.show()
    edit = panel.text_edit
    seen: list[str] = []
    edit.textChanged.connect(lambda: seen.append(edit.toPlainText()))

    text = "\ud55c\uae00 \ud14c\uc2a4\ud2b8 abc"
    edit.insertPlainText(text)
    app.processEvents()

    assert edit.toPlainText() == text
    assert seen[-1] == text
    assert panel.undo_btn.isEnabled()

    edit.undo()
    app.processEvents()

    assert edit.toPlainText() == ""
    assert panel.redo_btn.isEnabled()

    edit.redo()
    app.processEvents()

    assert edit.toPlainText() == text
    assert panel.undo_btn.isEnabled()


def test_analyze_panel_ctrl_enter_requests_analysis() -> None:
    app = _app()
    panel = AnalyzePanel()
    panel.show()
    panel.text_edit.setFocus()
    spy = QSignalSpy(panel.analyze_requested)

    QTest.keyClick(panel.text_edit, Qt.Key.Key_Return, Qt.KeyboardModifier.ControlModifier)
    app.processEvents()

    assert spy.count() == 1


def test_analyze_panel_content_edited_emits_on_text_change() -> None:
    app = _app()
    panel = AnalyzePanel()
    panel.show()
    spy = QSignalSpy(panel.content_edited)

    panel.text_edit.insertPlainText("가")
    app.processEvents()

    assert spy.count() >= 1


def test_analyze_panel_paste_discards_rich_text_formatting() -> None:
    _app()
    panel = AnalyzePanel()
    mime = QMimeData()
    mime.setText("서식 없는 텍스트")
    mime.setHtml('<p style="font-size: 30px"><b>서식 없는 텍스트</b></p>')

    panel.text_edit.insertFromMimeData(mime)

    assert panel.text_edit.toPlainText() == "서식 없는 텍스트"
    assert "font-size: 30px" not in panel.text_edit.toHtml()
