from __future__ import annotations

import pytest

from kvocab_core.allowlist import (
    DEFAULT_CHARACTER_NAMES,
    add_allowlist_item,
    delete_allowlist_item,
    ensure_default_allowlist,
    get_allowlist_set,
    is_protected_allowlist_norm,
)
from kvocab_core.config import DEFAULT_SEED_XLSX
from kvocab_core.database import init_db
from kvocab_core.models import CustomAllowlist
from kvocab_core.normalization import normalize_key
from kvocab_core.seed import full_seed, get_seed_fingerprint, is_seed_current


@pytest.fixture
def db_with_seed(tmp_path):
    xlsx = DEFAULT_SEED_XLSX
    if not xlsx.exists():
        pytest.skip("seed xlsx missing")
    factory = init_db(tmp_path / "test.db")
    with factory() as session:
        full_seed(session, xlsx)
    return factory


def test_default_character_allowlist_in_set(db_with_seed):
    with db_with_seed() as session:
        allow = get_allowlist_set(session)
    for name in DEFAULT_CHARACTER_NAMES:
        assert normalize_key(name) in allow


def test_ensure_default_allowlist_idempotent(db_with_seed):
    with db_with_seed() as session:
        assert ensure_default_allowlist(session) == 0
        count = session.query(CustomAllowlist).count()
    assert count >= len(DEFAULT_CHARACTER_NAMES)


def test_delete_default_character_blocked(db_with_seed):
    with db_with_seed() as session:
        item = (
            session.query(CustomAllowlist)
            .filter(CustomAllowlist.text == DEFAULT_CHARACTER_NAMES[0])
            .one()
        )
        assert is_protected_allowlist_norm(item.normalized_text)
        assert delete_allowlist_item(session, item.id) is False
        assert session.get(CustomAllowlist, item.id) is not None


def test_full_seed_preserves_user_allowlist(db_with_seed):
    with db_with_seed() as session:
        add_allowlist_item(session, "배기찬", note="user item")
        full_seed(session)
        allow = get_allowlist_set(session)
        item = (
            session.query(CustomAllowlist)
            .filter(CustomAllowlist.normalized_text == normalize_key("배기찬"))
            .one_or_none()
        )
    assert normalize_key("배기찬") in allow
    assert item is not None
    assert item.note == "user item"


def test_full_seed_records_current_seed_fingerprint(db_with_seed):
    with db_with_seed() as session:
        assert get_seed_fingerprint(session)
        assert is_seed_current(session)
