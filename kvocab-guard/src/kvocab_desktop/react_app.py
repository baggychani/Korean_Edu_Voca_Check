"""react_app.py — KVocabGuard React + Tauri 진입점

app.py       → PySide6 데스크톱 (현행)
react_app.py → React + Tauri 데스크톱 (마이그레이션 중)

모드::

    python react_app.py              # Tauri 데스크톱 창 (기본)
    python react_app.py --tauri      # 위와 동일
    python react_app.py --browser    # Vite만 + Chrome 미리보기
    python react_app.py --dev-server # --browser 와 동일
    python react_app.py --sidecar    # Tauri용 stdin/stdout JSON-RPC
    python react_app.py --smoke      # Kiwi / cli_server 스모크 테스트
"""

from __future__ import annotations

import subprocess
import sys
import traceback
import webbrowser
from pathlib import Path

# ---------------------------------------------------------------------------
# Import path bootstrap (python -m / 직접 실행)
# ---------------------------------------------------------------------------


def _bootstrap_import_path() -> None:
    if __package__:
        return
    src_root = Path(__file__).resolve().parents[1]
    src_str = str(src_root)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)


_bootstrap_import_path()

from kvocab_core.runtime_paths import configure_frozen_dll_paths, crash_log_path  # noqa: E402

configure_frozen_dll_paths()

UI_DIR = Path(__file__).resolve().parents[2] / "kvocab-ui"
DEV_URL = "http://localhost:1420/"


def _write_crash_log(exc: BaseException) -> Path:
    log_path = crash_log_path()
    log_path.write_text(
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
        encoding="utf-8",
    )
    return log_path


def _ensure_ui_dir() -> Path:
    if not UI_DIR.exists():
        print(f"[react_app] kvocab-ui 디렉토리를 찾을 수 없습니다: {UI_DIR}", file=sys.stderr)
        sys.exit(1)
    return UI_DIR


def _npm_cmd(*args: str) -> list[str]:
    """Windows 에서 npm.cmd 를 우선 사용한다."""
    if sys.platform == "win32":
        return ["npm.cmd", *args]
    return ["npm", *args]


def _run_npm(args: list[str], *, cwd: Path) -> int:
    cmd = _npm_cmd(*args)
    print(f"[react_app] {' '.join(cmd)}  (cwd={cwd})")
    # shell=False + npm.cmd 가 Windows 에서 더 안정적
    proc = subprocess.Popen(cmd, cwd=cwd)
    try:
        return proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("\n[react_app] 종료되었습니다.")
        return 130


# ---------------------------------------------------------------------------
# 모드: Vite + 브라우저
# ---------------------------------------------------------------------------


def _port_in_use(port: int = 1420) -> bool:
    """Vite 가 host:false 일 때 ::1 만 listen 하는 경우도 잡는다."""
    import socket  # noqa: PLC0415

    targets: list[tuple[int, str]] = [
        (socket.AF_INET, "127.0.0.1"),
        (socket.AF_INET6, "::1"),
    ]
    for family, host in targets:
        try:
            with socket.socket(family, socket.SOCK_STREAM) as s:
                s.settimeout(0.4)
                if s.connect_ex((host, port)) == 0:
                    return True
        except OSError:
            continue
    return False


def _open_browser(url: str = DEV_URL) -> None:
    try:
        webbrowser.open(url)
    except Exception:
        pass


def run_dev_server() -> None:
    """Vite 개발 서버를 띄우고 브라우저로 UI를 연다 (mock UI 미리보기)."""
    ui_dir = _ensure_ui_dir()

    # 이미 1420 이 떠 있으면 새 서버를 띄우지 않고 브라우저만 연다
    if _port_in_use(1420):
        print(f"[react_app] 포트 1420 이 이미 사용 중입니다 → 기존 서버로 연결")
        print(f"[react_app] {DEV_URL}")
        _open_browser()
        print("[react_app] 브라우저를 열었습니다. (서버는 이미 실행 중)")
        return

    print(f"[react_app] Vite 개발 서버 시작 → {DEV_URL}")
    print("[react_app] 브라우저가 안 열리면 위 주소를 직접 여세요.")

    import threading  # noqa: PLC0415

    def _open() -> None:
        import time  # noqa: PLC0415
        time.sleep(1.2)
        _open_browser()

    threading.Thread(target=_open, daemon=True).start()
    code = _run_npm(["run", "dev"], cwd=ui_dir)
    if code not in (0, 130):
        sys.exit(code)


# ---------------------------------------------------------------------------
# 모드: Tauri 데스크톱
# ---------------------------------------------------------------------------


def _free_port(port: int = 1420) -> None:
    """Windows 에서 포트를 점유한 프로세스를 종료한다 (Tauri 재실행용)."""
    if sys.platform != "win32":
        return
    try:
        out = subprocess.check_output(
            ["netstat", "-ano"],
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
    except (OSError, subprocess.CalledProcessError):
        return

    pids: set[int] = set()
    needle = f":{port}"
    for line in out.splitlines():
        if needle not in line or "LISTENING" not in line:
            continue
        parts = line.split()
        if not parts:
            continue
        try:
            pids.add(int(parts[-1]))
        except ValueError:
            continue

    for pid in pids:
        if pid <= 0:
            continue
        print(f"[react_app] 포트 {port} 점유 프로세스 종료 (PID {pid})")
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/F"],
            capture_output=True,
            check=False,
        )


def run_tauri_dev() -> None:
    """Tauri 데스크톱 GUI 창을 실행한다 (Node + Rust 툴체인 필요)."""
    ui_dir = _ensure_ui_dir()
    if _port_in_use(1420):
        print("[react_app] 포트 1420 이 사용 중이라 기존 프로세스를 정리합니다…")
        _free_port(1420)
        import time  # noqa: PLC0415
        time.sleep(0.6)
    print("[react_app] Tauri 데스크톱 창 실행 중…")
    print("[react_app] (브라우저가 아니라 프로그램 창이 열립니다)")
    code = _run_npm(["run", "tauri", "dev"], cwd=ui_dir)
    if code not in (0, 130):
        sys.exit(code)


# ---------------------------------------------------------------------------
# 모드: sidecar JSON-RPC
# ---------------------------------------------------------------------------


def run_sidecar() -> None:
    """Tauri sidecar — stdin JSON 요청 / stdout JSON 응답."""
    from kvocab_core.cli_server import run  # noqa: PLC0415
    run()


# ---------------------------------------------------------------------------
# 모드: smoke
# ---------------------------------------------------------------------------


def run_smoke() -> None:
    from kvocab_core.morph import KoreanMorphAnalyzer  # noqa: PLC0415

    analyzer = KoreanMorphAnalyzer()
    tokens = analyzer.analyze("축구 경기를 보는 건 재미있습니다.")
    lemmas = [t.lemma for t in tokens]

    if analyzer.backend_name != "kiwi" or "보다" not in lemmas:
        raise RuntimeError(
            f"Kiwi smoke test failed: backend={analyzer.backend_name}, lemmas={lemmas}"
        )

    print(f"[smoke] OK — backend={analyzer.backend_name}, lemmas sample={lemmas[:5]}")

    import json  # noqa: PLC0415
    from kvocab_core.cli_server import _dispatch  # noqa: PLC0415, SLF001

    resp = json.loads(_dispatch({"id": 1, "method": "ping", "params": {}}))
    assert resp["ok"] is True and resp["data"] == "pong", f"ping failed: {resp}"
    print(f"[smoke] cli_server ping: {resp}")
    print("[smoke] 모든 검사 통과")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> None:
    args = set(sys.argv[1:])

    if "--help" in args or "-h" in args:
        print(__doc__)
        return

    if "--smoke" in args:
        run_smoke()
        return

    if "--sidecar" in args:
        run_sidecar()
        return

    # Chrome 미리보기는 명시할 때만
    if "--browser" in args or "--dev-server" in args:
        run_dev_server()
        return

    # 기본 / --tauri → 데스크톱 창
    run_tauri_dev()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log_path = _write_crash_log(exc)
        print(f"[react_app] 오류 발생. 크래시 로그: {log_path}", file=sys.stderr)
        traceback.print_exc()
        raise SystemExit(1) from exc
