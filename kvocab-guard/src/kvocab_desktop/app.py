from __future__ import annotations

import sys
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

from PySide6.QtCore import QTimer, QUrl  # noqa: E402
from PySide6.QtGui import QDesktopServices  # noqa: E402
from PySide6.QtWidgets import QApplication, QDialog  # noqa: E402

from kvocab_core.config import APP_VERSION  # noqa: E402
from kvocab_desktop.icons import app_icon  # noqa: E402
from kvocab_desktop.main_window import MainWindow  # noqa: E402
from kvocab_desktop.prefs import load_prefs, save_prefs  # noqa: E402
from kvocab_desktop.update_manager import UpdateManager  # noqa: E402
from kvocab_desktop.widgets.table_font import app_default_font  # noqa: E402
from kvocab_desktop.widgets.update_dialog import UpdateDialog  # noqa: E402


def main() -> None:
    app = QApplication(sys.argv)
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
    main()
