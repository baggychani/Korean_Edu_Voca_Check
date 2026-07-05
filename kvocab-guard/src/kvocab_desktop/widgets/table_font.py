from __future__ import annotations

from PySide6.QtGui import QFont, QFontInfo
from PySide6.QtWidgets import QWidget

DEFAULT_APP_POINT_SIZE = 10


def resolve_point_size(widget: QWidget) -> int:
    info = QFontInfo(widget.font())
    pt = info.pointSize()
    if pt > 0:
        return pt
    px = info.pixelSize()
    if px > 0:
        return max(1, round(px * 72 / 96))
    return DEFAULT_APP_POINT_SIZE


def app_default_font(family: str = "Malgun Gothic") -> QFont:
    font = QFont(family, DEFAULT_APP_POINT_SIZE)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    return font


def bold_font(widget: QWidget | None = None) -> QFont:
    font = QFont(widget.font()) if widget is not None else app_default_font()
    font.setWeight(QFont.Weight.Bold)
    return font
