from __future__ import annotations

from kvocab_core.normalization import lemma_gana_sort_key, normalize_key


def test_normalize_key_spaces_and_punctuation():
    assert normalize_key("가격이 비싸다") == "가격이비싸다"
    assert normalize_key("가격 이 비싸다") == "가격이비싸다"
    assert normalize_key("비밀번호를 누르다") == "비밀번호를누르다"


def test_normalize_key_nfc():
    assert normalize_key("  테스트  ") == "테스트"


def test_lemma_gana_sort_key_parenthesized():
    assert lemma_gana_sort_key("(간판이) 떨어지다") == "떨어지다"
    assert lemma_gana_sort_key("가게") == "가게"
