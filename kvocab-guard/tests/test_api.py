"""kvocab_core.api JSON 라운드트립 테스트.

PySide6 없이 코어 API 레이어가 올바르게 동작하는지 검증한다.
"""

from __future__ import annotations

import json

import pytest

from kvocab_core.config import DEFAULT_SEED_XLSX
from kvocab_core.database import init_db
from kvocab_core.seed import full_seed


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def db_path(tmp_path):
    """시드 데이터가 로드된 임시 DB 경로를 반환."""
    xlsx = DEFAULT_SEED_XLSX
    if not xlsx.exists():
        pytest.skip("seed xlsx missing")
    path = tmp_path / "test_api.db"
    factory = init_db(path)
    with factory() as session:
        full_seed(session, xlsx)
    return str(path)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _import_api():
    """api 모듈의 전역 세션 팩토리 캐시를 테스트마다 리셋하기 위해 지연 임포트."""
    import importlib
    import kvocab_core.api as _api_mod  # noqa: PLC0415

    # 테스트 간 캐시 오염 방지
    _api_mod._session_factory = None  # noqa: SLF001
    importlib.reload(_api_mod)
    _api_mod._session_factory = None  # noqa: SLF001
    return _api_mod


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------


def test_init_returns_ok(db_path):
    api = _import_api()
    raw = api.init(db_path=db_path)
    result = json.loads(raw)
    assert result["ok"] is True
    assert result["data"]["seeded"] is True
    assert result["data"]["lexeme_count"] > 0


# ---------------------------------------------------------------------------
# list_levels_and_lessons
# ---------------------------------------------------------------------------


def test_list_levels_has_known_levels(db_path):
    api = _import_api()
    raw = api.list_levels_and_lessons(db_path=db_path)
    result = json.loads(raw)
    assert result["ok"] is True
    level_codes = {lv["level"] for lv in result["data"]["levels"]}
    assert "1A" in level_codes
    assert "2A" in level_codes


def test_list_lessons_has_lessons_for_each_level(db_path):
    api = _import_api()
    raw = api.list_levels_and_lessons(db_path=db_path)
    result = json.loads(raw)
    lessons = result["data"]["lessons"]
    assert "1A" in lessons
    assert len(lessons["1A"]) > 0


# ---------------------------------------------------------------------------
# analyze_text
# ---------------------------------------------------------------------------


def test_analyze_text_basic(db_path):
    api = _import_api()
    request_json = json.dumps(
        {
            "text": "동호회에 가입하고 싶어요.",
            "target_level": "2A",
            "target_lesson": "2-1",
            "strictness": "balanced",
        }
    )
    raw = api.analyze_text(request_json=request_json, db_path=db_path)
    result = json.loads(raw)
    assert result["ok"] is True
    data = result["data"]
    assert "summary" in data
    assert "issues" in data
    assert data["summary"]["issue_count"] >= 0


def test_analyze_text_returns_valid_issue_fields(db_path):
    api = _import_api()
    request_json = json.dumps(
        {
            "text": "동호회에 가입하고 싶어요.",
            "target_level": "2A",
            "target_lesson": "2-1",
        }
    )
    raw = api.analyze_text(request_json=request_json, db_path=db_path)
    result = json.loads(raw)
    issues = result["data"]["issues"]
    for issue in issues:
        assert "surface" in issue
        assert "lemma" in issue
        assert "status" in issue
        assert "sentence" in issue


def test_analyze_text_bad_json_returns_error(db_path):
    api = _import_api()
    # 잘못된 레벨
    request_json = json.dumps(
        {
            "text": "테스트",
            "target_level": "INVALID",
            "target_lesson": "1-1",
        }
    )
    raw = api.analyze_text(request_json=request_json, db_path=db_path)
    result = json.loads(raw)
    assert result["ok"] is False
    assert "error" in result


# ---------------------------------------------------------------------------
# search_dictionary
# ---------------------------------------------------------------------------


def test_search_dictionary_returns_results(db_path):
    api = _import_api()
    raw = api.search_dictionary(query="안녕", db_path=db_path)
    result = json.loads(raw)
    assert result["ok"] is True
    assert isinstance(result["data"], list)


def test_search_dictionary_empty_returns_all(db_path):
    api = _import_api()
    raw = api.search_dictionary(query="", db_path=db_path)
    result = json.loads(raw)
    assert result["ok"] is True
    assert len(result["data"]) > 0


# ---------------------------------------------------------------------------
# allowlist CRUD
# ---------------------------------------------------------------------------


def test_allowlist_add_and_get(db_path):
    api = _import_api()
    add_raw = api.add_to_allowlist(text="테스트단어", note="테스트용", db_path=db_path)
    add_result = json.loads(add_raw)
    assert add_result["ok"] is True
    assert add_result["data"]["text"] == "테스트단어"

    get_raw = api.get_allowlist(db_path=db_path)
    get_result = json.loads(get_raw)
    assert get_result["ok"] is True
    texts = [item["text"] for item in get_result["data"]]
    assert "테스트단어" in texts


def test_allowlist_delete(db_path):
    api = _import_api()
    add_raw = api.add_to_allowlist(text="삭제테스트", db_path=db_path)
    item_id = json.loads(add_raw)["data"]["id"]

    del_raw = api.remove_from_allowlist(item_id=item_id, db_path=db_path)
    del_result = json.loads(del_raw)
    assert del_result["ok"] is True
    assert del_result["data"]["deleted_id"] == item_id


def test_allowlist_delete_nonexistent_returns_error(db_path):
    api = _import_api()
    raw = api.remove_from_allowlist(item_id=99999, db_path=db_path)
    result = json.loads(raw)
    assert result["ok"] is False


# ---------------------------------------------------------------------------
# cli_server dispatch
# ---------------------------------------------------------------------------


def test_cli_server_dispatch_ping():
    from kvocab_core.cli_server import _dispatch  # noqa: PLC0415

    response = json.loads(_dispatch({"id": 1, "method": "ping", "params": {}}))
    assert response["id"] == 1
    assert response["ok"] is True
    assert response["data"] == "pong"


def test_cli_server_dispatch_unknown_method():
    from kvocab_core.cli_server import _dispatch  # noqa: PLC0415

    response = json.loads(_dispatch({"id": 2, "method": "does_not_exist", "params": {}}))
    assert response["id"] == 2
    assert response["ok"] is False
    assert "unknown method" in response["error"]
