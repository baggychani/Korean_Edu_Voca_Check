from __future__ import annotations

from kvocab_core.runtime_paths import desktop_assets_dir

APP_ICON_PATH = desktop_assets_dir() / "app_icon.ico"


def app_icon():
    from PySide6.QtGui import QIcon

    if APP_ICON_PATH.exists():
        return QIcon(str(APP_ICON_PATH))
    return QIcon()
