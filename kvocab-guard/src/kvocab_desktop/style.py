"""Global stylesheet and status colors for the desktop UI."""

APP_STYLESHEET = """
* {
    font-family: "Pretendard", "Malgun Gothic", "Segoe UI", sans-serif;
    font-size: 10pt;
}

QMainWindow {
    background: #f0f3f8;
    color: #111827;
}

QWidget {
    background: transparent;
    color: #111827;
}

/* ---------- Sidebar ---------- */
QFrame#sidebar {
    background: #151b26;
    border: none;
    border-right: 1px solid #252d3b;
}
QFrame#sidebar QWidget {
    background: transparent;
}
QFrame#sidebar QLabel {
    background: transparent;
}
QFrame#sidebarLogo {
    background: #192131;
    border-left: 3px solid #2d7dd2;
    border-radius: 10px;
    padding: 0;
    margin: 0 0 2px 0;
}
QLabel#sidebarTag {
    font-size: 11px;
    font-weight: 600;
    color: #7bb7ff;
    letter-spacing: 0.6px;
}
QLabel#sidebarTitle {
    font-size: 20px;
    font-weight: 700;
    color: #ffffff;
    padding: 0;
}
QLabel#sidebarSubtitle {
    font-size: 10px;
    color: #8794a8;
    padding: 4px 0 0 0;
}
QFrame#sidebarDivider {
    background: #2a3344;
    border: none;
    min-height: 1px;
    max-height: 1px;
    margin: 3px 0 6px 0;
}
QLabel#sidebarSection {
    font-size: 10px;
    font-weight: 700;
    color: #6d7a91;
    letter-spacing: 0.6px;
    padding: 12px 0 7px 0;
}
QLabel#sidebarFieldLabel {
    font-size: 12px;
    font-weight: 600;
    color: #a8b4c4;
    padding: 0 0 4px 2px;
}
QWidget#coverPreview {
    background: transparent;
}
QLabel#sidebarVersion {
    font-size: 10px;
    color: #6d7a91;
    padding-top: 8px;
}
QLabel#sidebarCopyright {
    font-size: 9px;
    color: #566278;
    padding-top: 2px;
}
QFrame#sidebar QComboBox {
    background: #202838;
    color: #edf1f7;
    border: 1px solid #38445a;
    border-radius: 9px;
    padding: 9px 12px;
    min-height: 18px;
}
QFrame#sidebar QComboBox:hover {
    border-color: #58708f;
    background: #242e40;
}
QFrame#sidebar QComboBox::drop-down {
    border: none;
    width: 26px;
}
QFrame#sidebar QComboBox QAbstractItemView {
    background: #222a38;
    color: #edf1f7;
    border: 1px solid #343f52;
    selection-background-color: #1a6fdb;
    padding: 4px;
}
QFrame#sidebar QCheckBox {
    color: #b8c2d0;
    spacing: 10px;
    padding: 5px 0;
    font-size: 12px;
}
QFrame#sidebar QCheckBox::indicator {
    width: 17px;
    height: 17px;
    border: 1px solid #4a5a72;
    border-radius: 4px;
    background: #222a38;
}
QFrame#sidebar QCheckBox::indicator:checked {
    background: #1a6fdb;
    border-color: #1a6fdb;
}

/* ---------- Content area ---------- */
QWidget#contentArea {
    background: #f0f3f8;
}
QTabWidget::pane {
    border: none;
    background: #f0f3f8;
    top: 0;
}
QTabBar {
    background: #f0f3f8;
}
QTabBar::tab {
    background: transparent;
    color: #6b7280;
    padding: 12px 22px 10px 22px;
    margin-right: 2px;
    border: none;
    border-bottom: 2px solid transparent;
    font-weight: 600;
    font-size: 13px;
}
QTabBar::tab:selected {
    color: #1a6fdb;
    border-bottom: 2px solid #1a6fdb;
}
QTabBar::tab:hover:!selected {
    color: #374151;
}

/* ---------- Section titles ---------- */
QLabel#sectionTitle {
    font-size: 14px;
    font-weight: 700;
    color: #1f2937;
    background: transparent;
    padding: 0;
}
QLabel#sectionHint {
    font-size: 12px;
    color: #6b7280;
    background: transparent;
}

/* ---------- Cards ---------- */
QFrame#card {
    background: #ffffff;
    border: 1px solid #dde3ec;
    border-radius: 12px;
}
QFrame#statCard {
    background: #ffffff;
    border: 1px solid #dde3ec;
    border-radius: 10px;
}
QLabel#completionStatus {
    color: #15803d;
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12px;
}
QLabel#statValue {
    font-size: 19px;
    font-weight: 700;
    background: transparent;
}
QLabel#statLabel {
    font-size: 10px;
    color: #6b7280;
    background: transparent;
    font-weight: 500;
}
QLabel#detailTitle {
    font-size: 15px;
    font-weight: 700;
    background: transparent;
    color: #1f2937;
}
QFrame#card QLabel {
    background: transparent;
}

/* ---------- Selection bar ---------- */
QFrame#selectionBar {
    background: #ffffff;
    border: 1px solid #dde3ec;
    border-radius: 10px;
}
QLabel#selectionHint {
    font-size: 11px;
    font-weight: 600;
    color: #6b7280;
    background: transparent;
}
QLabel#selectedExpression {
    font-size: 18px;
    font-weight: 700;
    color: #111827;
    background: transparent;
}

/* ---------- Buttons ---------- */
QWidget#analyzeActions QPushButton,
QFrame#selectionBar QPushButton {
    padding: 8px 16px;
    min-height: 18px;
    border-radius: 7px;
}
QPushButton {
    background: #1a6fdb;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    min-height: 20px;
}
QPushButton:hover {
    background: #1558b0;
}
QPushButton:pressed {
    background: #124a96;
}
QPushButton:disabled {
    background: #b8d4f5;
    color: #eef4fc;
}

QPushButton[variant="secondary"] {
    background: #ffffff;
    color: #374151;
    border: 1px solid #cdd5e0;
}
QPushButton[variant="secondary"]:hover {
    background: #f8fafc;
    border-color: #9aa8ba;
}
QPushButton[variant="secondary"]:disabled {
    background: #f3f5f8;
    color: #9aa8ba;
    border-color: #dde3ec;
}

QPushButton[variant="chip"] {
    background: #ffffff;
    color: #4b5563;
    border: 1px solid #cdd5e0;
    border-radius: 16px;
    padding: 7px 14px;
    font-weight: 600;
    font-size: 12px;
}
QPushButton[variant="chip"]:hover {
    border-color: #7eb3ef;
    color: #1a6fdb;
}
QPushButton[variant="chip"]:checked {
    background: #1a6fdb;
    color: #ffffff;
    border-color: #1a6fdb;
}

/* ---------- Inputs ---------- */
QLineEdit, QTextEdit, QPlainTextEdit {
    background: #ffffff;
    border: 1px solid #cdd5e0;
    border-radius: 10px;
    padding: 10px 12px;
    color: #111827;
    selection-background-color: #c5ddfa;
}
QFrame#inputFrame {
    background: #ffffff;
    border: 1px solid #cdd5e0;
    border-radius: 10px;
}
QTextEdit QWidget,
QPlainTextEdit QWidget,
QTextEdit QAbstractScrollArea,
QPlainTextEdit QAbstractScrollArea,
QTextEdit::viewport,
QPlainTextEdit::viewport {
    background: #ffffff;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #1a6fdb;
}
QTextEdit#inputArea {
    font-size: 14px;
    line-height: 1.5;
    background: #ffffff;
    border: none;
    border-radius: 9px;
}
QTextEdit#inputArea:focus {
    border: none;
}

QComboBox {
    background: #ffffff;
    border: 1px solid #cdd5e0;
    border-radius: 10px;
    padding: 10px 12px;
    min-height: 18px;
}
QComboBox::drop-down {
    border: none;
    width: 26px;
}
QComboBox QAbstractItemView {
    background: #ffffff;
    border: 1px solid #cdd5e0;
    selection-background-color: #e8f2fd;
    selection-color: #0f3460;
    padding: 4px;
}
QListView#comboPopup {
    background: #222a38;
    color: #edf1f7;
    border: 1px solid #343f52;
    padding: 6px;
    outline: 0;
}
QListView#comboPopup::item {
    min-height: 28px;
    padding: 7px 10px;
    border-radius: 6px;
}
QListView#comboPopup::item:selected {
    background: #1d4f8f;
    color: #ffffff;
}

/* ---------- Table ---------- */
QTableWidget {
    background: #ffffff;
    border: 1px solid #dde3ec;
    border-radius: 10px;
    gridline-color: transparent;
    alternate-background-color: #f8fafc;
    selection-background-color: #e8f2fd;
    selection-color: #0f3460;
}
QTableWidget::item {
    padding: 10px 12px;
    border: none;
}
QTableWidget::item:selected {
    background: #e8f2fd;
    color: #0f3460;
}
QHeaderView::section {
    background: #f5f7fa;
    color: #4b5563;
    padding: 4px 10px;
    border: none;
    border-bottom: 1px solid #dde3ec;
    font-weight: 700;
    font-size: 12px;
}
QTableCornerButton::section {
    background: #f5f7fa;
    border: none;
}

/* ---------- Scrollbars ---------- */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #c5cdd8;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #9aa8ba;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: transparent;
    height: 8px;
    margin: 2px;
}
QScrollBar::handle:horizontal {
    background: #c5cdd8;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

QMessageBox {
    background: #ffffff;
}
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
