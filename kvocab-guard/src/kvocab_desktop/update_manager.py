"""GitHub Releases API 기반 업데이트 확인."""

from __future__ import annotations

import json
from datetime import datetime, timedelta

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from kvocab_core.config import GITHUB_API_LATEST_RELEASE, GITHUB_RELEASE_URL

CHECK_INTERVAL = timedelta(hours=12)


class UpdateManager(QObject):
    update_available = Signal(str, str, str)  # latest_version, download_url, release_notes

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.network_manager = QNetworkAccessManager(self)
        self.reply: QNetworkReply | None = None
        self.on_success_callback = None

    def check_for_updates(self, current_version: str, last_check_str: str | None = None) -> bool:
        now = datetime.now()
        last_check = None
        if last_check_str:
            try:
                last_check = datetime.fromisoformat(last_check_str)
            except ValueError:
                pass

        if last_check is not None and now - last_check < CHECK_INTERVAL:
            return False

        request = QNetworkRequest(QUrl(GITHUB_API_LATEST_RELEASE))
        request.setRawHeader(b"User-Agent", b"KVocabGuard-App")
        self.reply = self.network_manager.get(request)
        self.reply.finished.connect(lambda: self._on_check_finished(current_version, now))
        return True

    def _on_check_finished(self, current_version: str, check_time: datetime) -> None:
        try:
            if self.reply is None:
                return
            if self.reply.error() != QNetworkReply.NetworkError.NoError:
                return

            data = json.loads(self.reply.readAll().data().decode("utf-8"))
            latest_tag = data.get("tag_name", "").strip()
            latest_version = latest_tag.lstrip("vV")
            html_url = data.get("html_url", GITHUB_RELEASE_URL)
            body = data.get("body", "") or ""

            if self._is_newer(current_version, latest_version):
                self.update_available.emit(latest_version, html_url, body)
        except (json.JSONDecodeError, KeyError, TypeError, UnicodeDecodeError):
            pass
        finally:
            # 성공/실패 모두 시각 저장 → 오프라인에서 매 실행마다 API 재시도 방지
            if self.on_success_callback:
                self.on_success_callback(check_time.isoformat())
            if self.reply is not None:
                self.reply.deleteLater()
                self.reply = None

    @staticmethod
    def _is_newer(current: str, latest: str) -> bool:
        try:
            c_parts = [int(p) for p in current.split(".") if p.strip().isdigit()]
            l_parts = [int(p) for p in latest.split(".") if p.strip().isdigit()]
            for i in range(max(len(c_parts), len(l_parts))):
                cv = c_parts[i] if i < len(c_parts) else 0
                lv = l_parts[i] if i < len(l_parts) else 0
                if lv > cv:
                    return True
                if lv < cv:
                    return False
            return False
        except ValueError:
            return False
