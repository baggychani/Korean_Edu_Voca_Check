from __future__ import annotations

from PySide6.QtGui import QFont, QFontInfo
from PySide6.QtWidgets import QWidget

DEFAULT_APP_POINT_SIZE = 13


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
    return font


def bold_font(widget: QWidget) -> QFont:
    info = QFontInfo(widget.font())
    font = QFont(info.family())
    font.setPointSize(resolve_point_size(widget))
    font.setBold(True)
    return font
