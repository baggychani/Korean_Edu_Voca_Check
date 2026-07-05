"""Global stylesheet and status colors for the desktop UI."""

APP_STYLESHEET = """
* {
    font-family: "Malgun Gothic", "Segoe UI", sans-serif;
    font-size: 13px;
}

QMainWindow, QWidget {
    background: #f1f5f9;
    color: #0f172a;
}

/* ---------- Sidebar ---------- */
QFrame#sidebar {
    background: #0f172a;
    border: none;
}
QFrame#sidebar QWidget {
    background: transparent;
    color: #cbd5e1;
}
QFrame#sidebar QLabel {
    color: #cbd5e1;
    background: transparent;
}
QLabel#sidebarTitle {
    font-size: 19px;
    font-weight: 700;
    color: #ffffff;
    padding: 4px 0 14px 0;
}
QLabel#sidebarSection {
    font-size: 11px;
    font-weight: 700;
    color: #64748b;
    letter-spacing: 1px;
    padding-top: 12px;
}
QFrame#sidebar QComboBox {
    background: #1e293b;
    color: #e2e8f0;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 7px 10px;
}
QFrame#sidebar QComboBox:hover { border-color: #475569; }
QFrame#sidebar QComboBox::drop-down { border: none; width: 24px; }
QFrame#sidebar QComboBox QAbstractItemView {
    background: #1e293b;
    color: #e2e8f0;
    border: 1px solid #334155;
    selection-background-color: #4f46e5;
}
QFrame#sidebar QCheckBox {
    color: #cbd5e1;
    background: transparent;
    spacing: 8px;
    padding: 3px 0;
}
QFrame#sidebar QCheckBox::indicator {
    width: 16px; height: 16px;
    border: 1px solid #475569;
    border-radius: 4px;
    background: #1e293b;
}
QFrame#sidebar QCheckBox::indicator:checked {
    background: #6366f1;
    border-color: #6366f1;
}

/* ---------- Tabs ---------- */
QTabWidget::pane {
    border: none;
    background: #f1f5f9;
    top: -1px;
}
QTabBar::tab {
    background: transparent;
    color: #64748b;
    padding: 9px 20px;
    margin-right: 4px;
    border: none;
    border-bottom: 2px solid transparent;
    font-weight: 600;
}
QTabBar::tab:selected {
    color: #4f46e5;
    border-bottom: 2px solid #4f46e5;
}
QTabBar::tab:hover:!selected { color: #334155; }

/* ---------- Cards ---------- */
QFrame#card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}
QFrame#statCard {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}
QLabel#statValue {
    font-size: 22px;
    font-weight: 700;
    background: transparent;
}
QLabel#statLabel {
    font-size: 11px;
    color: #64748b;
    background: transparent;
}
QLabel#detailTitle {
    font-size: 14px;
    font-weight: 700;
    background: transparent;
}
QFrame#card QLabel { background: transparent; }

/* ---------- Buttons ---------- */
QPushButton {
    background: #4f46e5;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
    font-weight: 600;
}
QPushButton:hover { background: #4338ca; }
QPushButton:pressed { background: #3730a3; }
QPushButton:disabled { background: #c7d2fe; color: #eef2ff; }

QPushButton[variant="secondary"] {
    background: #ffffff;
    color: #334155;
    border: 1px solid #cbd5e1;
}
QPushButton[variant="secondary"]:hover { background: #f8fafc; border-color: #94a3b8; }

QPushButton[variant="chip"] {
    background: #ffffff;
    color: #475569;
    border: 1px solid #cbd5e1;
    border-radius: 15px;
    padding: 6px 14px;
    font-weight: 600;
}
QPushButton[variant="chip"]:hover { border-color: #818cf8; color: #4f46e5; }
QPushButton[variant="chip"]:checked {
    background: #4f46e5;
    color: #ffffff;
    border-color: #4f46e5;
}

/* ---------- Inputs ---------- */
QLineEdit, QTextEdit {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 9px;
    selection-background-color: #c7d2fe;
}
QLineEdit:focus, QTextEdit:focus { border: 1px solid #6366f1; }

QComboBox {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 7px 10px;
}
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    selection-background-color: #eef2ff;
    selection-color: #1e1b4b;
}

/* ---------- Table ---------- */
QTableWidget {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    gridline-color: transparent;
    alternate-background-color: #f8fafc;
    selection-background-color: #eef2ff;
    selection-color: #1e1b4b;
}
QTableWidget::item {
    padding: 6px 10px;
    border: none;
}
QTableWidget::item:selected {
    background: #eef2ff;
    color: #1e1b4b;
}
QHeaderView::section {
    background: #f8fafc;
    color: #475569;
    padding: 9px 10px;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    font-weight: 700;
    font-size: 12px;
}
QTableCornerButton::section { background: #f8fafc; border: none; }

/* ---------- Scrollbars ---------- */
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #94a3b8; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 2px;
}
QScrollBar::handle:horizontal {
    background: #cbd5e1;
    border-radius: 5px;
    min-width: 30px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

QMessageBox { background: #ffffff; }
"""

STATUS_COLORS = {
    "before_introduced": "#dc2626",
    "unknown_high": "#ea580c",
    "unknown_medium": "#ca8a04",
    "unknown_low": "#64748b",
    "allowed": "#16a34a",
    "custom_allowed": "#0891b2",
}

STATUS_BG_COLORS = {
    "before_introduced": "#fef2f2",
    "unknown_high": "#fff7ed",
    "unknown_medium": "#fefce8",
    "unknown_low": "#f8fafc",
    "allowed": "#f0fdf4",
    "custom_allowed": "#ecfeff",
}
