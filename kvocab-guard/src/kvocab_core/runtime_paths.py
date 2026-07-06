from __future__ import annotations

import os
import sys
from pathlib import Path


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def bundle_root() -> Path:
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parent.parent.parent


def app_install_root() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return bundle_root()


def bundled_data_dir() -> Path:
    override = os.environ.get("KVOCAB_BUNDLE_DATA_DIR")
    if override:
        return Path(override)
    return bundle_root() / "data"


def writable_data_dir() -> Path:
    override = os.environ.get("KVOCAB_DATA_DIR")
    if override:
        path = Path(override)
        path.mkdir(parents=True, exist_ok=True)
        return path
    if is_frozen():
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if base:
            path = Path(base) / "KVocabGuard"
        else:
            path = app_install_root() / "data"
        path.mkdir(parents=True, exist_ok=True)
        return path
    path = bundle_root() / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def desktop_assets_dir() -> Path:
    if is_frozen():
        return bundle_root() / "kvocab_desktop" / "assets"
    return Path(__file__).resolve().parent.parent / "kvocab_desktop" / "assets"


def repo_root() -> Path:
    if is_frozen():
        return bundle_root()
    return bundle_root().parent


def configure_frozen_dll_paths() -> None:
    """Windows PyInstaller: PySide6 DLL 검색 경로 등록."""
    if not is_frozen() or not hasattr(os, "add_dll_directory"):
        return
    meipass = getattr(sys, "_MEIPASS", None)
    if not meipass:
        return
    for sub in ("PySide6", "shiboken6"):
        dll_dir = os.path.join(meipass, sub)
        if os.path.isdir(dll_dir):
            os.add_dll_directory(dll_dir)


def crash_log_path() -> Path:
    if is_frozen():
        return app_install_root() / "KVocabGuard-crash.log"
    return bundle_root() / "KVocabGuard-crash.log"
