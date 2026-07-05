from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QIcon

_ASSETS_DIR = Path(__file__).resolve().parent / "assets"
APP_ICON_PATH = _ASSETS_DIR / "app_icon.ico"


def app_icon() -> QIcon:
    if APP_ICON_PATH.exists():
        return QIcon(str(APP_ICON_PATH))
    return QIcon()
