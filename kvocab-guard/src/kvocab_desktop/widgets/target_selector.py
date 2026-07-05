from __future__ import annotations

from PySide6.QtCore import QRect, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from kvocab_core.config import cover_image_path
from kvocab_core.models import Lesson, Level

_STRICTNESS_LABELS = [
    ("loose", "느슨하게"),
    ("balanced", "보통"),
    ("strict", "엄격하게"),
]

# 원본 표지 500×~670 (비율 약 3:4) 기준
_BOOK_W = 148
_BOOK_H = 198
_COVER_FRAME_W = 162
_COVER_FRAME_H = 210


class CoverPreview(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("coverPreview")
        self.setFixedSize(_COVER_FRAME_W, _COVER_FRAME_H)
        self._pixmap = QPixmap()

    def set_cover(self, pixmap: QPixmap) -> None:
        self._pixmap = pixmap
        self.update()

    def clear_cover(self) -> None:
        self._pixmap = QPixmap()
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setPen(Qt.PenStyle.NoPen)

        if self._pixmap.isNull():
            return

        book_x = 5
        book_y = 5
        front_rect = QRect(book_x, book_y, _BOOK_W, _BOOK_H)

        painter.fillRect(front_rect.adjusted(4, 5, 5, 6), QColor(0, 0, 0, 36))

        scaled = self._pixmap.scaled(
            _BOOK_W,
            _BOOK_H,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = front_rect.x() + (front_rect.width() - scaled.width()) // 2
        y = front_rect.y() + (front_rect.height() - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)
        painter.setPen(QPen(QColor("#e5e7eb"), 1))
        painter.drawRect(QRect(x, y, scaled.width(), scaled.height()).adjusted(0, 0, -1, -1))


def _section(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("sidebarSection")
    return lbl


def _field_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("sidebarFieldLabel")
    return lbl


class TargetSelector(QWidget):
    changed = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("targetSelector")
        self.setAutoFillBackground(False)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.level_combo = QComboBox()
        self.lesson_combo = QComboBox()
        self.strictness_combo = QComboBox()
        for code, label in _STRICTNESS_LABELS:
            self.strictness_combo.addItem(label, code)
        self.strictness_combo.setCurrentIndex(1)

        self.morph_cb = QCheckBox("형태소 분석 사용")
        self.morph_cb.setChecked(True)
        self.morph_cb.setAutoFillBackground(False)
        self.debug_cb = QCheckBox("무시된 항목 표시 (디버그)")
        self.debug_cb.setChecked(False)
        self.debug_cb.setAutoFillBackground(False)

        layout.addWidget(_section("목표"))
        layout.addWidget(_field_label("레벨"))
        layout.addWidget(self.level_combo)
        layout.addSpacing(10)
        layout.addWidget(_field_label("단원"))
        layout.addWidget(self.lesson_combo)

        self.cover_label = CoverPreview()
        layout.addSpacing(12)
        layout.addWidget(self.cover_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(_section("검사 설정"))
        layout.addWidget(_field_label("엄격도"))
        layout.addWidget(self.strictness_combo)
        layout.addSpacing(12)
        layout.addWidget(self.morph_cb)
        layout.addWidget(self.debug_cb)

        self._lessons_by_level: dict[str, list[Lesson]] = {}
        self.level_combo.currentIndexChanged.connect(self._on_level_changed)
        self.lesson_combo.currentIndexChanged.connect(lambda: self.changed.emit())
        self.strictness_combo.currentIndexChanged.connect(lambda: self.changed.emit())

    def load_levels(self, levels: list[Level], lessons_by_level: dict[str, list[Lesson]]) -> None:
        self._lessons_by_level = lessons_by_level
        self.level_combo.blockSignals(True)
        self.level_combo.clear()
        for lv in sorted(levels, key=lambda x: x.sort_order):
            self.level_combo.addItem(lv.title_ko, lv.level)
        self.level_combo.blockSignals(False)
        self._on_level_changed()

    def _on_level_changed(self) -> None:
        code = self.level_combo.currentData()
        self.lesson_combo.blockSignals(True)
        self.lesson_combo.clear()
        for ls in self._lessons_by_level.get(code, []):
            self.lesson_combo.addItem(f"{ls.lesson}  ·  {ls.unit_topic}", ls.lesson)
        self.lesson_combo.blockSignals(False)
        self._update_cover(code)
        self.changed.emit()

    def _update_cover(self, level: str | None) -> None:
        self.cover_label.clear_cover()
        if not level:
            return
        path = cover_image_path(level)
        if not path:
            return
        pix = QPixmap(str(path))
        if pix.isNull():
            return
        self.cover_label.set_cover(pix)

    @property
    def target_level(self) -> str:
        return self.level_combo.currentData() or "2A"

    @property
    def target_lesson(self) -> str:
        return self.lesson_combo.currentData() or "2-1"

    @property
    def strictness(self) -> str:
        return self.strictness_combo.currentData() or "balanced"

    @property
    def use_morph(self) -> bool:
        return self.morph_cb.isChecked()

    @property
    def show_debug(self) -> bool:
        return self.debug_cb.isChecked()
