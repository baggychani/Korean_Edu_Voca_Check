from __future__ import annotations

import pytest

from kvocab_core.analyzer import Analyzer
from kvocab_core.config import DEFAULT_SEED_XLSX
from kvocab_core.database import init_db
from kvocab_core.models import Lexeme
from kvocab_core.schemas import AnalyzeRequest, IssueStatus, Strictness
from kvocab_core.seed import full_seed


@pytest.fixture
def analyzer(tmp_path):
    xlsx = DEFAULT_SEED_XLSX
    if not xlsx.exists():
        pytest.skip("seed xlsx missing")
    factory = init_db(tmp_path / "test.db")
    with factory() as session:
        full_seed(session, xlsx)
    return factory


def _analyze(factory, text: str, lesson: str) -> list:
    with factory() as session:
        result = Analyzer(session).analyze(
            AnalyzeRequest(
                text=text,
                target_level="2A",
                target_lesson=lesson,
                strictness=Strictness.balanced,
            )
        )
    return result.issues


def test_yori_allowed_at_2_1(analyzer):
    issues = _analyze(analyzer, "저는 요리하는 걸 좋아해요.", "2-1")
    high = [i for i in issues if i.status == IssueStatus.unknown_high and "요리" in i.surface]
    assert not high


def test_gaiip_before_introduced_at_2_1(analyzer):
    issues = _analyze(analyzer, "동호회에 가입하고 싶어요.", "2-1")
    statuses = {i.normalized for i in issues if i.status == IssueStatus.before_introduced}
    assert "가입하다" in statuses or any(
        "가입" in i.surface for i in issues if i.status == IssueStatus.before_introduced
    )


def test_gaiip_allowed_at_2_2(analyzer):
    issues = _analyze(analyzer, "동호회에 가입하고 싶어요.", "2-2")
    before = [
        i for i in issues if "가입" in i.surface and i.status == IssueStatus.before_introduced
    ]
    assert not before


def test_jeonghap_unknown_high(analyzer):
    issues = _analyze(analyzer, "정합적인 설명입니다.", "2-1")
    high = [i for i in issues if i.status == IssueStatus.unknown_high]
    norms = {i.normalized for i in high}
    assert "정합적" in norms or "정합적인" in norms


def test_nnp_not_in_default_issues(analyzer):
    issues = _analyze(analyzer, "김민수는 서울대에 갔어요.", "2-1")
    assert not any(i.status == IssueStatus.ignored_nnp for i in issues)


def test_no_substring_bang_hak(analyzer):
    with analyzer() as session:
        session.add(
            Lexeme(
                lemma="방",
                normalized_lemma="방",
                gloss_en="room",
                review_status="approved",
                first_level="2A",
                first_lesson="1-1",
                first_page=22,
                first_order_index=201011,
            )
        )
        session.commit()
    issues = _analyze(analyzer, "방학이 시작됐어요.", "9-2")
    before = [i for i in issues if i.surface == "방" and i.status == IssueStatus.before_introduced]
    assert not before

