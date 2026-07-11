from __future__ import annotations

import re
from dataclasses import dataclass


_TOKEN_RE = re.compile(r"[가-힣A-Za-z0-9]+|[.,!?;:\"'()\[\]{}]")

# 용언류: 사전형 복원 시 "다"를 붙인다 (먹 -> 먹다)
_VERBAL_PREFIXES = ("VV", "VA", "VX", "VCN", "XSV", "XSA")


class MorphInitializationError(RuntimeError):
    """Raised when the required Kiwi analyzer cannot be initialized."""


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

        # 스레드당 1코어: 앱 쪽에서 문장 단위 병렬을 담당한다.
        self._kiwi = Kiwi(num_workers=1)

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


_SHARED_BACKEND: KiwiMorphAnalyzer | None = None
_SHARED_BACKEND_NAME = "unavailable"


def _get_backend() -> tuple[KiwiMorphAnalyzer, str]:
    global _SHARED_BACKEND, _SHARED_BACKEND_NAME
    if _SHARED_BACKEND is None:
        try:
            _SHARED_BACKEND = KiwiMorphAnalyzer()
            _SHARED_BACKEND_NAME = "kiwi"
        except Exception as exc:
            _SHARED_BACKEND_NAME = "unavailable"
            raise MorphInitializationError(
                "Kiwi 형태소 분석기를 초기화할 수 없습니다. "
                "kiwipiepy와 kiwipiepy_model이 올바르게 설치/포함되어 있는지 확인하세요."
            ) from exc
    return _SHARED_BACKEND, _SHARED_BACKEND_NAME


class KoreanMorphAnalyzer:
    """Kiwi 형태소 분석기.

    shared=True(기본): 프로세스 내 싱글톤 — UI 단일 스레드·인덱스용.
    shared=False: 스레드별 독립 인스턴스 — 병렬 문장 분석용.
    """

    def __init__(self, *, shared: bool = True) -> None:
        if shared:
            self._backend, self.backend_name = _get_backend()
            return
        try:
            self._backend = KiwiMorphAnalyzer()
            self.backend_name = "kiwi"
        except Exception as exc:
            raise MorphInitializationError(
                "Kiwi 형태소 분석기를 초기화할 수 없습니다. "
                "kiwipiepy와 kiwipiepy_model이 올바르게 설치/포함되어 있는지 확인하세요."
            ) from exc

    def analyze(self, text: str) -> list[MorphToken]:
        return self._backend.analyze(text)
