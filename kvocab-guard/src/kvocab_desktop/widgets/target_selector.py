from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from kvocab_core.models import Lesson, Level

_STRICTNESS_LABELS = [
    ("loose", "느슨하게"),
    ("balanced", "보통"),
    ("strict", "엄격하게"),
]


class TargetSelector(QWidget):
    changed = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("targetSelector")
        self.setAutoFillBackground(False)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

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

        def section(text: str) -> QLabel:
            lbl = QLabel(text)
            lbl.setObjectName("sidebarSection")
            return lbl

        layout.addWidget(section("목표"))
        layout.addWidget(QLabel("레벨"))
        layout.addWidget(self.level_combo)
        layout.addWidget(QLabel("단원"))
        layout.addWidget(self.lesson_combo)
        layout.addWidget(section("검사 설정"))
        layout.addWidget(QLabel("엄격도"))
        layout.addWidget(self.strictness_combo)
        layout.addSpacing(6)
        layout.addWidget(self.morph_cb)
        layout.addWidget(self.debug_cb)

        self._lessons_by_level: dict[str, list[Lesson]] = {}
        self.level_combo.currentIndexChanged.connect(self._on_level_changed)
        self.lesson_combo.currentIndexChanged.connect(lambda: self.changed.emit())
        self.strictness_combo.currentIndexChanged.connect(lambda: self.changed.emit())

    def load_levels(
        self, levels: list[Level], lessons_by_level: dict[str, list[Lesson]]
    ) -> None:
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
        self.changed.emit()

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
