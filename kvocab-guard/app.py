"""app.py — PySide6 데스크톱 앱 실행 진입점 (루트 단축키)

더블클릭하거나:
    python app.py

내부적으로 .venv 의 Python 으로 kvocab_desktop.app:main 을 실행한다.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT   = Path(__file__).resolve().parent
VENV_PY = ROOT / ".venv" / "Scripts" / "python.exe"


def _resolve_python() -> Path:
    if VENV_PY.exists():
        return VENV_PY
    # venv 가 없으면 현재 인터프리터로 폴백 (CI / 개발 환경)
    return Path(sys.executable)


def main() -> None:
    py = _resolve_python()
    # 추가 인수(--smoke 등)를 그대로 전달
    extra = sys.argv[1:]
    subprocess.check_call(
        [str(py), "-m", "kvocab_desktop.app", *extra],
        cwd=ROOT,
    )


if __name__ == "__main__":
    main()
