"""앱 로컬 설정 (업데이트 확인 시각, 마지막 목표 단원 등)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from kvocab_core.runtime_paths import writable_data_dir

_PREFS_NAME = "prefs.json"


def _legacy_qt_prefs_path() -> Path | None:
    """이전 버전: QStandardPaths.AppDataLocation 아래 prefs."""
    try:
        from PySide6.QtCore import QStandardPaths

        base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        if not base:
            return None
        return Path(base) / _PREFS_NAME
    except Exception:
        return None


def app_data_dir() -> Path:
    """DB와 동일한 writable_data_dir 사용 (%LOCALAPPDATA%/KVocabGuard 등)."""
    path = writable_data_dir()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _migrate_legacy_prefs(dest: Path) -> None:
    if dest.is_file():
        return
    legacy = _legacy_qt_prefs_path()
    if legacy is None or not legacy.is_file():
        return
    try:
        shutil.copy2(legacy, dest)
    except OSError:
        return


def load_prefs() -> dict:
    fp = app_data_dir() / _PREFS_NAME
    _migrate_legacy_prefs(fp)
    if not fp.is_file():
        return {}
    try:
        data = json.loads(fp.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_prefs(prefs: dict) -> None:
    fp = app_data_dir() / _PREFS_NAME
    try:
        fp.write_text(json.dumps(prefs, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        return
