from __future__ import annotations

import pytest

from kvocab_core.analyzer import Analyzer, _sentence_at, split_sentence_spans
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
    unknown = [i for i in issues if i.status == IssueStatus.unknown and "요리" in i.surface]
    assert not unknown


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


def test_jeonghap_unknown(analyzer):
    issues = _analyze(analyzer, "정합적인 설명입니다.", "2-1")
    unknown = [i for i in issues if i.status == IssueStatus.unknown]
    norms = {i.normalized for i in unknown}
    assert "정합적" in norms or "정합적인" in norms


def test_nnp_not_in_default_issues(analyzer):
    issues = _analyze(analyzer, "김민수는 서울대에 갔어요.", "2-1")
    assert not any(i.status == IssueStatus.ignored_nnp for i in issues)


def test_split_sentence_spans():
    text = "안녕하세요. 저는 학생입니다! 한국어를 공부해요."
    spans = split_sentence_spans(text)
    assert len(spans) == 3
    assert text[spans[0][0] : spans[0][1]] == "안녕하세요."
    assert text[spans[1][0] : spans[1][1]] == "저는 학생입니다!"
    assert text[spans[2][0] : spans[2][1]] == "한국어를 공부해요."


def test_sentence_at_stops_when_issue_span_includes_period():
    text = "통장에 돈이 없어요. 책은 가격이 비싸요. 가끔이 들었습니다!"
    start = text.index("가격")
    end = text.index("요.", start) + len("요.")
    assert _sentence_at(text, start, end) == "책은 가격이 비싸요."


def test_parallel_multi_sentence_finds_issues(analyzer):
    text = "토스트에 잼을 발라 먹어요. 동호회에 가입하고 싶어요. 정합적인 설명입니다."
    assert len(split_sentence_spans(text)) >= 2
    with analyzer() as session:
        result = Analyzer(session).analyze(
            AnalyzeRequest(
                text=text,
                target_level="2A",
                target_lesson="2-1",
                strictness=Strictness.balanced,
            )
        )
    assert result.summary.issue_count >= 1
    lemmas = {i.lemma for i in result.issues}
    assert "가입하다" in lemmas or "정합적" in lemmas or "먹다" in lemmas


def test_surface_shows_eojeol_not_stem(analyzer):
    with analyzer() as session:
        result = Analyzer(session).analyze(
            AnalyzeRequest(
                text="토스트에 잼을 발라 먹어요.",
                target_level="1A",
                target_lesson="1-1",
            )
        )
    by_lemma = {i.lemma: i.surface for i in result.issues}
    assert by_lemma.get("먹다") == "먹어요"
    assert by_lemma.get("바르다") == "발라"


def test_single_word_surface_does_not_pull_neighboring_eojeol(analyzer):
    with analyzer() as session:
        result = Analyzer(session).analyze(
            AnalyzeRequest(
                text="제 이름은 김민수입니다. 김밥을 먹고 싶어요. 가뭄이 심해요.",
                target_level="1A",
                target_lesson="1-1",
            )
        )
    by_lemma = {i.lemma: i.surface for i in result.issues + result.allowed}
    assert by_lemma.get("이름") == "이름은"
    assert by_lemma.get("먹다") == "먹고"
    assert by_lemma.get("가뭄") == "가뭄이"


def test_adnominal_verb_is_not_particle_stripped_to_stem_noun(analyzer):
    with analyzer() as session:
        result = Analyzer(session).analyze(
            AnalyzeRequest(
                text="축구 경기를 보는 건 재미있습니다.",
                target_level="1A",
                target_lesson="5-1",
            )
        )
    assert not any(i.surface == "보는" and i.lemma == "보" for i in result.issues)


def test_phrase_jeonhwa_bada_matches_expression(analyzer):
    from kvocab_core.analyzer import invalidate_lexeme_index

    invalidate_lexeme_index()
    with analyzer() as session:
        result = Analyzer(session).analyze(
            AnalyzeRequest(
                text="황정민이야 나~ 전화 받어~",
                target_level="1B",
                target_lesson="12-1",
            )
        )
    matched = [i for i in result.issues + result.allowed if i.lemma == "전화를 받다"]
    assert matched
    assert matched[0].surface == "전화 받어~"


def test_unlisted_noun_hada_phrase_is_not_reported_as_unknown_expression(analyzer):
    from kvocab_core.analyzer import invalidate_lexeme_index

    invalidate_lexeme_index()
    with analyzer() as session:
        result = Analyzer(session).analyze(
            AnalyzeRequest(
                text="밥 해 좀",
                target_level="1A",
                target_lesson="1-1",
            )
        )
    assert not any(i.normalized == "밥하다" for i in result.issues)


def test_unlisted_hada_derivative_does_not_fall_back_to_hada(analyzer):
    from kvocab_core.analyzer import invalidate_lexeme_index

    invalidate_lexeme_index()
    with analyzer() as session:
        result = Analyzer(session).analyze(
            AnalyzeRequest(
                text="채용하다 수정하다 보강하다",
                target_level="1A",
                target_lesson="1-1",
            )
        )
    by_surface = {i.surface: i.lemma for i in result.issues + result.allowed}
    assert by_surface.get("보강하다") == "보강하다"
    assert by_surface.get("수정하다") != "하다"
    assert not any(i.surface in {"보강하다", "수정하다"} and i.lemma == "하다" for i in result.issues)


def test_auxiliary_hada_after_eoya_is_not_reported(analyzer):
    from kvocab_core.analyzer import invalidate_lexeme_index

    invalidate_lexeme_index()
    with analyzer() as session:
        result = Analyzer(session).analyze(
            AnalyzeRequest(
                text="팁을 보강해야 합니다.",
                target_level="2A",
                target_lesson="1-1",
            )
        )
    items = result.issues + result.allowed
    assert any(i.lemma == "보강하다" for i in items)
    assert not any(i.surface == "합니다" and i.lemma == "하다" for i in items)


def test_expression_sentence_does_not_eat_next_sentence(analyzer):
    from kvocab_core.analyzer import invalidate_lexeme_index

    invalidate_lexeme_index()
    text = (
        "안녕하세요? 제 이름은 크리스티아노 호날두이며 축구선수입니다. "
        "통장에 돈이 없어요. 책은 가격이 비싸요. 가끔이 들었습니다!"
    )
    with analyzer() as session:
        result = Analyzer(session).analyze(
            AnalyzeRequest(
                text=text,
                target_level="2A",
                target_lesson="1-1",
            )
        )
    matched = [i for i in result.issues + result.allowed if i.lemma == "가격이 비싸다"]
    assert matched
    assert matched[0].sentence == "책은 가격이 비싸요."


def test_known_single_syllable_word_is_checked_before_skip(analyzer):
    from kvocab_core.analyzer import invalidate_lexeme_index

    invalidate_lexeme_index()
    with analyzer() as session:
        result = Analyzer(session).analyze(
            AnalyzeRequest(
                text="이거 뭐예요?",
                target_level="1A",
                target_lesson="1-1",
            )
        )
    matched = [i for i in result.issues + result.allowed if i.lemma == "뭐"]
    assert matched
    assert matched[0].surface == "뭐예요"


def test_display_surface_strips_trailing_comma(analyzer):
    from kvocab_core.analyzer import invalidate_lexeme_index

    invalidate_lexeme_index()
    with analyzer() as session:
        result = Analyzer(session).analyze(
            AnalyzeRequest(
                text="안녕하세요, 리센느 원이입니다.",
                target_level="1A",
                target_lesson="1-1",
            )
        )
    matched = [i for i in result.issues + result.allowed if i.lemma == "안녕하세요"]
    assert matched
    assert matched[0].surface == "안녕하세요"


def test_equivalent_annyeong_uses_textbook_annyeonghaseyo(analyzer):
    from kvocab_core.analyzer import invalidate_lexeme_index

    invalidate_lexeme_index()
    with analyzer() as session:
        result = Analyzer(session).analyze(
            AnalyzeRequest(
                text="안녕",
                target_level="1A",
                target_lesson="1-1",
            )
        )
    matched = [i for i in result.issues + result.allowed if i.lemma == "안녕"]
    assert matched
    assert matched[0].equivalent_lemma == "안녕하세요"
    assert matched[0].status == IssueStatus.allowed


def test_standalone_single_syllable_unknown_noun_is_reported(analyzer):
    from kvocab_core.analyzer import invalidate_lexeme_index

    invalidate_lexeme_index()
    with analyzer() as session:
        result = Analyzer(session).analyze(
            AnalyzeRequest(
                text="레몬을 즙 짜서 먹어요.",
                target_level="2B",
                target_lesson="10-1",
            )
        )
    assert any(i.surface == "즙" and i.lemma == "즙" for i in result.issues)


def test_one_syllable_unknown_stems_inside_noise_are_not_reported(analyzer):
    from kvocab_core.analyzer import invalidate_lexeme_index

    invalidate_lexeme_index()
    with analyzer() as session:
        result = Analyzer(session).analyze(
            AnalyzeRequest(
                text="띠요잉띠요잉 우리는 완전",
                target_level="2B",
                target_lesson="10-1",
            )
        )
    assert not any(i.lemma == "띠다" for i in result.issues + result.allowed)


def test_no_substring_bang_hak(analyzer):
    with analyzer() as session:
        lex = session.query(Lexeme).filter(Lexeme.normalized_lemma == "방").one_or_none()
        if lex:
            lex.first_level = "2A"
            lex.first_lesson = "1-1"
            lex.first_page = 22
            lex.first_order_index = 201011
        else:
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
