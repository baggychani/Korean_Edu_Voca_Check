from __future__ import annotations

import sys
import traceback
from pathlib import Path


def _bootstrap_import_path() -> None:
    """Allow running this file directly (Cursor Run / python app.py)."""
    if __package__:
        return
    src_root = Path(__file__).resolve().parents[1]
    src_str = str(src_root)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)


_bootstrap_import_path()

from kvocab_core.runtime_paths import configure_frozen_dll_paths, crash_log_path  # noqa: E402

configure_frozen_dll_paths()

from PySide6.QtCore import QTimer, QUrl  # noqa: E402
from PySide6.QtGui import QDesktopServices  # noqa: E402
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox  # noqa: E402

from kvocab_core.config import APP_VERSION  # noqa: E402
from kvocab_desktop.icons import app_icon  # noqa: E402
from kvocab_desktop.main_window import MainWindow  # noqa: E402
from kvocab_desktop.prefs import load_prefs, save_prefs  # noqa: E402
from kvocab_desktop.update_manager import UpdateManager  # noqa: E402
from kvocab_desktop.widgets.table_font import app_default_font  # noqa: E402
from kvocab_desktop.widgets.update_dialog import UpdateDialog  # noqa: E402


def _write_crash_log(exc: BaseException) -> Path:
    log_path = crash_log_path()
    log_path.write_text(
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
        encoding="utf-8",
    )
    return log_path


def _show_fatal_error(exc: BaseException, log_path: Path) -> None:
    message = (
        f"{exc}\n\n"
        f"자세한 내용은 다음 파일에 저장되었습니다.\n{log_path}"
    )
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    QMessageBox.critical(None, "한국어교육 단어 검사기 실행 오류", message)


def _run_smoke_analyze() -> None:
    from kvocab_core.morph import KoreanMorphAnalyzer

    analyzer = KoreanMorphAnalyzer()
    tokens = analyzer.analyze("축구 경기를 보는 건 재미있습니다.")
    lemmas = [token.lemma for token in tokens]
    if analyzer.backend_name != "kiwi" or "보다" not in lemmas:
        raise RuntimeError(
            f"Kiwi smoke test failed: backend={analyzer.backend_name}, lemmas={lemmas}"
        )


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("KVocabGuard")
    app.setOrganizationName("Bae Gichan")
    app.setFont(app_default_font())
    app.setApplicationVersion(APP_VERSION)

    icon = app_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)

    window = MainWindow()
    if not icon.isNull():
        window.setWindowIcon(icon)

    pending_update: list[tuple[str, str, str]] = []
    update_manager = UpdateManager(app)

    def on_update_success(check_time_iso: str) -> None:
        prefs = load_prefs()
        prefs["last_update_check"] = check_time_iso
        save_prefs(prefs)

    update_manager.on_success_callback = on_update_success

    def handle_update(version: str, url: str, notes: str) -> None:
        pending_update.clear()
        pending_update.append((version, url, notes))

    def show_update_if_pending() -> None:
        if not pending_update:
            return
        version, url, notes = pending_update[0]
        dlg = UpdateDialog(window, version, url, notes)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            QDesktopServices.openUrl(QUrl(url))

    update_manager.update_available.connect(handle_update)

    prefs = load_prefs()
    update_manager.check_for_updates(APP_VERSION, prefs.get("last_update_check"))

    window.show()
    QTimer.singleShot(300, show_update_if_pending)
    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        if "--smoke-analyze" in sys.argv:
            _run_smoke_analyze()
            raise SystemExit(0)
        main()
    except Exception as exc:
        log_path = _write_crash_log(exc)
        try:
            _show_fatal_error(exc, log_path)
        except Exception:
            pass
        raise SystemExit(1) from exc
