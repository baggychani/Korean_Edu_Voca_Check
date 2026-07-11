from __future__ import annotations

import pytest

from kvocab_core.config import DEFAULT_SEED_XLSX
from kvocab_core.database import init_db
from kvocab_core.dictionary import search_lexemes, search_lexemes_multi
from kvocab_core.models import Lesson, Lexeme
from kvocab_core.seed import full_seed


@pytest.fixture
def db_with_seed(tmp_path):
    xlsx = DEFAULT_SEED_XLSX
    if not xlsx.exists():
        pytest.skip("seed xlsx missing")
    factory = init_db(tmp_path / "test.db")
    with factory() as session:
        full_seed(session, xlsx)
    return factory


def test_search_gaiip(db_with_seed):
    with db_with_seed() as session:
        target_oi = (
            session.query(Lesson)
            .filter(Lesson.level == "2A", Lesson.lesson == "2-2")
            .one()
            .order_index
        )
        results = search_lexemes(session, "가입하다", target_order_index=target_oi)
    assert results
    r = results[0]
    assert r.first_page == 44
    assert r.first_lesson == "2-2"
    assert r.verdict_label_ko == "사용 가능"


def test_search_cup(db_with_seed):
    with db_with_seed() as session:
        results = search_lexemes(session, "컵")
    assert results
    r = results[0]
    assert r.first_page in (42, 43)
    assert r.first_lesson == "2-1"


def test_search_password_expression(db_with_seed):
    with db_with_seed() as session:
        results = search_lexemes(session, "비밀번호를 누르다")
    if not results:
        pytest.skip("expression not in seed")
    r = results[0]
    assert r.first_page == 92
    assert r.first_lesson == "5-2"


def test_search_multi_terms(db_with_seed):
    with db_with_seed() as session:
        results = search_lexemes_multi(session, "가입하다, 컵")
    lemmas = {r.lemma for r in results}
    assert "가입하다" in lemmas
    assert "컵" in lemmas


def test_equivalent_form_search_returns_canonical_without_adding_lemma(db_with_seed):
    with db_with_seed() as session:
        results = search_lexemes(session, "안녕")
        stored_alias = session.query(Lexeme).filter(Lexeme.normalized_lemma == "안녕").one_or_none()

    assert results
    assert results[0].lemma == "안녕하세요"
    assert results[0].equivalent_forms == ["안녕"]
    assert stored_alias is None
