"""Tauri sidecar 진입점 — stdin/stdout JSON-RPC 루프.

Tauri 에서 sidecar 로 실행되면, 이 프로세스가 뜨고
stdin 으로 JSON 요청을 줄 단위로 받아 stdout 으로 JSON 응답을 내보낸다.

Protocol::

    → {"id": 1, "method": "analyze_text", "params": {"request_json": "...", "db_path": null}}
    ← {"id": 1, "ok": true, "data": {...}}

    → {"id": 2, "method": "ping", "params": {}}
    ← {"id": 2, "ok": true, "data": "pong"}

Unknown method::

    ← {"id": 3, "ok": false, "error": "unknown method: foo"}

stdin EOF 수신 시 프로세스 종료.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable

from kvocab_core import api

_METHODS: dict[str, Callable[..., str]] = {
    "ping": lambda **_: api._ok("pong"),  # noqa: SLF001
    "init": api.init,
    "run_seed": api.run_seed,
    "get_db_counts": api.get_db_counts,
    "list_levels_and_lessons": api.list_levels_and_lessons,
    "analyze_text": api.analyze_text,
    "search_dictionary": api.search_dictionary,
    "get_allowlist": api.get_allowlist,
    "add_to_allowlist": api.add_to_allowlist,
    "remove_from_allowlist": api.remove_from_allowlist,
    "extract_text_from_file": api.extract_text_from_file,
    "get_cover_base64": api.get_cover_base64,
}


def _dispatch(request: dict) -> str:
    req_id = request.get("id", 0)
    method = request.get("method", "")
    params = request.get("params") or {}

    fn = _METHODS.get(method)
    if fn is None:
        payload = json.dumps(
            {"id": req_id, "ok": False, "error": f"unknown method: {method}"},
            ensure_ascii=False,
        )
        return payload

    try:
        raw = fn(**params)
        inner = json.loads(raw)
        inner["id"] = req_id
        return json.dumps(inner, ensure_ascii=False)
    except Exception as exc:
        return json.dumps(
            {"id": req_id, "ok": False, "error": str(exc)},
            ensure_ascii=False,
        )


def run() -> None:
    """stdin 줄 단위 JSON-RPC 루프."""
    # stdout 을 라인 버퍼 모드로 전환 (Tauri 파이프 통신)
    sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]

    # 사람이 터미널에서 직접 실행한 경우 안내 메시지 출력
    if sys.stdin.isatty() or sys.stdout.isatty():
        print(
            "[KVocabGuard-Sidecar] 대기 중... (Tauri 용 JSON-RPC 입력 대기 중. 종료하려면 Ctrl+C)",
            file=sys.stderr,
            flush=True,
        )

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as exc:
            response = json.dumps(
                {"id": None, "ok": False, "error": f"JSON parse error: {exc}"},
                ensure_ascii=False,
            )
            print(response, flush=True)
            continue

        response = _dispatch(request)
        print(response, flush=True)


if __name__ == "__main__":
    run()
