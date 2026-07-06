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


TABLE_ROW_HEIGHT = 38


def configure_data_table(table) -> None:
    """어휘 사전·허용어 등 데이터 테이블 공통 레이아웃."""
    from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget

    if not isinstance(table, QTableWidget):
        return
    table.setFont(app_default_font())
    table.setSortingEnabled(False)
    table.verticalHeader().setVisible(False)
    table.setAlternatingRowColors(True)
    table.setShowGrid(False)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    header = table.horizontalHeader()
    header.setStretchLastSection(False)
    header.setFixedHeight(34)
