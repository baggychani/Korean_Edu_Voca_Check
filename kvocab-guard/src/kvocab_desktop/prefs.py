"""앱 로컬 설정 (업데이트 확인 시각 등)."""

from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QStandardPaths

_PREFS_NAME = "prefs.json"


def app_data_dir() -> Path:
    base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    path = Path(base)
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_prefs() -> dict:
    fp = app_data_dir() / _PREFS_NAME
    if not fp.is_file():
        return {}
    try:
        return json.loads(fp.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_prefs(prefs: dict) -> None:
    fp = app_data_dir() / _PREFS_NAME
    fp.write_text(json.dumps(prefs, ensure_ascii=False, indent=2), encoding="utf-8")
