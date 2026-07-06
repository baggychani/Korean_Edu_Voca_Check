from __future__ import annotations

import re
from dataclasses import dataclass

_TOKEN_RE = re.compile(r"[가-힣A-Za-z0-9]+|[.,!?;:\"'()\[\]{}]")

# 용언류: 사전형 복원 시 "다"를 붙인다 (먹 -> 먹다)
_VERBAL_PREFIXES = ("VV", "VA", "VX", "VCN", "XSV", "XSA")


@dataclass
class MorphToken:
    surface: str
    lemma: str
    pos: str
    start: int
    end: int


def restore_dictionary_form(form: str, tag: str) -> str:
    """어간을 사전형으로 복원한다. 먹/VV -> 먹다."""
    if tag.startswith(_VERBAL_PREFIXES) and not form.endswith("다"):
        return form + "다"
    return form


class RegexFallbackAnalyzer:
    def analyze(self, text: str) -> list[MorphToken]:
        tokens: list[MorphToken] = []
        for m in _TOKEN_RE.finditer(text):
            surf = m.group()
            if not re.search(r"[가-힣A-Za-z0-9]", surf):
                continue
            pos = "NNG"
            if re.fullmatch(r"[A-Za-z]+", surf):
                pos = "SL"
            elif re.fullmatch(r"\d+", surf):
                pos = "SN"
            tokens.append(
                MorphToken(surface=surf, lemma=surf, pos=pos, start=m.start(), end=m.end())
            )
        return tokens


class KiwiMorphAnalyzer:
    def __init__(self) -> None:
        from kiwipiepy import Kiwi

        self._kiwi = Kiwi()

    def analyze(self, text: str) -> list[MorphToken]:
        tokens: list[MorphToken] = []
        for tok in self._kiwi.tokenize(text):
            form = tok.form
            lemma = restore_dictionary_form(getattr(tok, "lemma", None) or form, tok.tag)
            start = tok.start
            tokens.append(
                MorphToken(
                    surface=form,
                    lemma=lemma,
                    pos=tok.tag,
                    start=start,
                    end=start + len(form),
                )
            )
        return tokens


_SHARED_BACKEND: KiwiMorphAnalyzer | RegexFallbackAnalyzer | None = None
_SHARED_BACKEND_NAME = "fallback"


def _get_backend() -> tuple[KiwiMorphAnalyzer | RegexFallbackAnalyzer, str]:
    global _SHARED_BACKEND, _SHARED_BACKEND_NAME
    if _SHARED_BACKEND is None:
        try:
            _SHARED_BACKEND = KiwiMorphAnalyzer()
            _SHARED_BACKEND_NAME = "kiwi"
        except Exception:
            _SHARED_BACKEND = RegexFallbackAnalyzer()
            _SHARED_BACKEND_NAME = "fallback"
    return _SHARED_BACKEND, _SHARED_BACKEND_NAME


class KoreanMorphAnalyzer:
    """Kiwi 우선, 실패 시 정규식 fallback. 백엔드는 프로세스 내 공유(싱글톤)."""

    def __init__(self) -> None:
        self._backend, self.backend_name = _get_backend()

    def analyze(self, text: str) -> list[MorphToken]:
        return self._backend.analyze(text)
