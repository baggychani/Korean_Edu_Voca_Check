"""Double-click or: python run.py"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"
VENV_PY = VENV_DIR / "Scripts" / "python.exe"


def _ensure_venv() -> Path:
    if VENV_PY.exists():
        return VENV_PY
    subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)], cwd=ROOT)
    if not VENV_PY.exists():
        raise RuntimeError(f"venv created but python missing: {VENV_PY}")
    return VENV_PY


def main() -> None:
    py = _ensure_venv()
    subprocess.check_call([str(py), "-m", "pip", "install", "-e", ".[dev]", "-q"], cwd=ROOT)
    subprocess.check_call([str(py), "-m", "kvocab_core.seed"], cwd=ROOT)
    subprocess.check_call([str(py), "-m", "kvocab_desktop.app"], cwd=ROOT)


if __name__ == "__main__":
    main()
