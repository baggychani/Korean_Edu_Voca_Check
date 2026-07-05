"""Double-click or: python run.py"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_PY = ROOT / ".venv" / "Scripts" / "python.exe"


def main() -> None:
    py = VENV_PY if VENV_PY.exists() else Path(sys.executable)
    subprocess.check_call([str(py), "-m", "pip", "install", "-e", ".[dev]", "-q"], cwd=ROOT)
    subprocess.check_call([str(py), "-m", "kvocab_core.seed"], cwd=ROOT)
    subprocess.check_call([str(py), "-m", "kvocab_desktop.app"], cwd=ROOT)


if __name__ == "__main__":
    main()
