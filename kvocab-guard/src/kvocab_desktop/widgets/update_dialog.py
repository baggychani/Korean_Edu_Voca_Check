"""GitHub Release 업데이트 안내 다이얼로그."""

from __future__ import annotations

import html

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
)

from kvocab_core.config import APP_VERSION


class UpdateDialog(QDialog):
    def __init__(self, parent, version: str, url: str, notes: str) -> None:
        super().__init__(parent)
        self._url = url
        self.setWindowTitle("업데이트가 준비되었습니다")
        self.setFixedWidth(440)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(0)

        title = QLabel("업데이트가 준비되었습니다")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        subtitle = QLabel("GitHub Releases에서 최신 설치 파일을 받을 수 있습니다.")
        subtitle.setObjectName("sectionHint")
        layout.addWidget(subtitle)
        layout.addSpacing(16)

        version_row = QHBoxLayout()
        version_row.setSpacing(10)
        for text, style in (
            (f"현재  {APP_VERSION}", "muted"),
            ("→", "arrow"),
            (f"최신  {version}", "latest"),
        ):
            lbl = QLabel(text)
            lbl.setObjectName(f"updateBadge_{style}")
            version_row.addWidget(lbl)
        version_row.addStretch()
        layout.addLayout(version_row)

        if notes.strip():
            layout.addSpacing(14)
            layout.addWidget(QLabel("릴리스 노트"))
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setMaximumHeight(132)
            body = html.escape(notes.strip()).replace("\n", "<br>")
            notes_lbl = QLabel(f'<div style="line-height:148%;">{body}</div>')
            notes_lbl.setWordWrap(True)
            notes_lbl.setTextFormat(Qt.TextFormat.RichText)
            notes_lbl.setContentsMargins(12, 10, 12, 10)
            scroll.setWidget(notes_lbl)
            layout.addWidget(scroll)

        layout.addSpacing(18)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        later = QPushButton("나중에")
        later.setProperty("variant", "secondary")
        later.clicked.connect(self.reject)
        update = QPushButton("지금 업데이트")
        update.setDefault(True)
        update.clicked.connect(self.accept)
        btn_row.addWidget(later)
        btn_row.addWidget(update)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.setStyleSheet("""
            QLabel#updateBadge_muted {
                color: #606266; background: #f5f7fa; border: 1px solid #e4e7ed;
                border-radius: 4px; padding: 6px 10px;
            }
            QLabel#updateBadge_arrow { color: #c0c4cc; padding: 6px 4px; }
            QLabel#updateBadge_latest {
                color: #2563eb; background: #eff6ff; border: 1px solid #bfdbfe;
                border-radius: 4px; padding: 6px 10px;
            }
        """)
