"""react_app.py — React + Tauri 앱 실행 진입점 (루트 단축키)

더블클릭하거나:
    python react_app.py              # Tauri sidecar 모드 (stdin/stdout JSON-RPC)
    python react_app.py --dev-server # Vite dev server 실행 + 브라우저 오픈
    python react_app.py --smoke      # 스모크 테스트

내부적으로 .venv 의 Python 으로 kvocab_desktop.react_app:main 을 실행한다.

    app.py        →  PySide6 데스크톱 앱  (현행 유지)
    react_app.py  →  React + Tauri 앱    (마이그레이션 대상)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT    = Path(__file__).resolve().parent
VENV_PY = ROOT / ".venv" / "Scripts" / "python.exe"


def _resolve_python() -> Path:
    if VENV_PY.exists():
        return VENV_PY
    return Path(sys.executable)


def main() -> None:
    py = _resolve_python()
    # --dev-server / --smoke 등 추가 인수를 그대로 전달
    extra = sys.argv[1:]
    subprocess.check_call(
        [str(py), "-m", "kvocab_desktop.react_app", *extra],
        cwd=ROOT,
    )


if __name__ == "__main__":
    main()
