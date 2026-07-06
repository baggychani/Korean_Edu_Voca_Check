from __future__ import annotations

from kvocab_core.matching import (
    build_eojeol_match_keys,
    eojeol_lookup_keys,
    strip_eojeol_particle,
)
from kvocab_core.morph import KoreanMorphAnalyzer
from kvocab_core.token_units import build_match_segments, segment_key


def test_strip_eojeol_particle():
    assert strip_eojeol_particle("이메일을") == "이메일"
    assert strip_eojeol_particle("원고와") == "원고"


def test_eojeol_lookup_keys_email():
    assert "이메일" in eojeol_lookup_keys("이메일을")


def test_build_eojeol_match_keys_phrase():
    keys = build_eojeol_match_keys(["안", "그래도"])
    norms = [k for k, _, _ in keys]
    assert "안그래도" in norms


def test_segment_key_strips_particles():
    morph = KoreanMorphAnalyzer()
    segs = build_match_segments(morph.analyze("전화를 받다"))
    assert segment_key(segs) == "전화받다"
