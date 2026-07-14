"""react_app.py — KVocabGuard React + Tauri 진입점

app.py  : PySide6 데스크톱 앱 진입점 (현행 유지)
react_app.py : React + Tauri 앱을 위한 진입점

역할:
    1. Python sidecar(kvocab_core.cli_server) 를 직접 실행하는 모드
       → Tauri 가 sidecar 로 이 프로세스를 스폰하면 stdin/stdout JSON-RPC 루프로 진입
    2. 개발 보조 모드 (--dev-server)
       → Vite dev server 를 백그라운드에서 띄우고 기본 브라우저로 연다
    3. 스모크 테스트 모드 (--smoke)
       → Kiwi 형태소 분석기가 정상 동작하는지 확인 후 종료

사용 예시::

    # Tauri sidecar (Rust 에서 Command::sidecar 로 실행):
    python react_app.py

    # 개발 UI 미리보기 (Vite dev server 실행 + 브라우저 오픈):
    python react_app.py --dev-server

    # 스모크 테스트:
    python react_app.py --smoke
"""

from __future__ import annotations

import subprocess
import sys
import traceback
import webbrowser
from pathlib import Path

# ---------------------------------------------------------------------------
# Import path bootstrap (python react_app.py 로 직접 실행 시)
# ---------------------------------------------------------------------------

def _bootstrap_import_path() -> None:
    """패키지 없이 직접 실행할 때 src/ 를 sys.path 에 추가한다."""
    if __package__:
        return
    src_root = Path(__file__).resolve().parents[1]
    src_str = str(src_root)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)


_bootstrap_import_path()

from kvocab_core.runtime_paths import configure_frozen_dll_paths, crash_log_path  # noqa: E402

configure_frozen_dll_paths()


# ---------------------------------------------------------------------------
# 공통 유틸
# ---------------------------------------------------------------------------

def _write_crash_log(exc: BaseException) -> Path:
    log_path = crash_log_path()
    log_path.write_text(
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
        encoding="utf-8",
    )
    return log_path


# ---------------------------------------------------------------------------
# 모드 1: sidecar (기본) — stdin/stdout JSON-RPC 루프
# ---------------------------------------------------------------------------

def run_sidecar() -> None:
    """Tauri sidecar 로서 동작한다.

    stdin 으로 JSON 요청을 줄 단위로 받고 stdout 으로 JSON 응답을 내보낸다.
    EOF 수신 시 정상 종료한다.
    """
    from kvocab_core.cli_server import run  # noqa: PLC0415
    run()


# ---------------------------------------------------------------------------
# 모드 2: --dev-server — Vite dev server + 브라우저
# ---------------------------------------------------------------------------

def run_dev_server() -> None:
    """kvocab-ui Tauri 데스크톱 GUI 개발 서버를 실행한다.

    npm 과 Node.js, Rust 툴체인이 설치돼 있어야 합니다.
    """
    ui_dir = Path(__file__).resolve().parents[2] / "kvocab-ui"
    if not ui_dir.exists():
        print(f"[react_app] kvocab-ui 디렉토리를 찾을 수 없습니다: {ui_dir}", file=sys.stderr)
        sys.exit(1)

    print("[react_app] Tauri 데스크톱 GUI 창 실행 중…")
    proc = subprocess.Popen(
        ["npm", "run", "tauri", "dev"],
        cwd=ui_dir,
        shell=sys.platform == "win32",
    )

    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        print("\n[react_app] GUI 앱이 종료되었습니다.")


# ---------------------------------------------------------------------------
# 모드 3: --smoke — 형태소 분석기 스모크 테스트
# ---------------------------------------------------------------------------

def run_smoke() -> None:
    """Kiwi 형태소 분석기와 코어 로직이 정상 동작하는지 확인한다."""
    from kvocab_core.morph import KoreanMorphAnalyzer  # noqa: PLC0415

    analyzer = KoreanMorphAnalyzer()
    tokens = analyzer.analyze("축구 경기를 보는 건 재미있습니다.")
    lemmas = [t.lemma for t in tokens]

    if analyzer.backend_name != "kiwi" or "보다" not in lemmas:
        raise RuntimeError(
            f"Kiwi smoke test failed: backend={analyzer.backend_name}, lemmas={lemmas}"
        )

    print(f"[smoke] OK — backend={analyzer.backend_name}, lemmas sample={lemmas[:5]}")

    # cli_server ping 테스트
    import json  # noqa: PLC0415

    from kvocab_core.cli_server import _dispatch  # noqa: PLC0415, SLF001

    resp = json.loads(_dispatch({"id": 1, "method": "ping", "params": {}}))
    assert resp["ok"] is True and resp["data"] == "pong", f"ping failed: {resp}"
    print(f"[smoke] cli_server ping: {resp}")

    print("[smoke] 모든 검사 통과 ✅")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> None:
    args = set(sys.argv[1:])

    if "--smoke" in args:
        run_smoke()
        return

    if "--sidecar" in args:
        run_sidecar()
        return

    # 기본값: 브라우저와 Vite 개발 서버를 즉시 띄운다
    run_dev_server()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log_path = _write_crash_log(exc)
        print(f"[react_app] 오류 발생. 크래시 로그: {log_path}", file=sys.stderr)
        traceback.print_exc()
        raise SystemExit(1) from exc
