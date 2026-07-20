"""react_app.py — React + Tauri 데스크톱 실행 진입점 (루트 단축키)

더블클릭하거나:

    python react_app.py              # Tauri 데스크톱 창 (기본)
    python react_app.py --browser    # Chrome으로 UI만 미리보기
    python react_app.py --sidecar    # Tauri sidecar JSON-RPC
    python react_app.py --smoke      # 스모크 테스트

    app.py        →  PySide6 데스크톱 앱  (현행 유지)
    react_app.py  →  React + Tauri 앱
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_PY = ROOT / ".venv" / "Scripts" / "python.exe"


def _resolve_python() -> Path:
    if VENV_PY.exists():
        return VENV_PY
    return Path(sys.executable)


def main() -> None:
    py = _resolve_python()
    extra = sys.argv[1:]
    subprocess.check_call(
        [str(py), "-m", "kvocab_desktop.react_app", *extra],
        cwd=ROOT,
    )


if __name__ == "__main__":
    main()
