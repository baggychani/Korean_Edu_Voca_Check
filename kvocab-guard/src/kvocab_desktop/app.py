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

from PySide6.QtWidgets import QApplication  # noqa: E402

from kvocab_desktop.main_window import MainWindow  # noqa: E402
from kvocab_desktop.widgets.table_font import app_default_font  # noqa: E402


def main() -> None:
    app = QApplication(sys.argv)
    app.setFont(app_default_font())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
