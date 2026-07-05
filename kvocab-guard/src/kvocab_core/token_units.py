from __future__ import annotations

from dataclasses import dataclass

from kvocab_core.morph import MorphToken, restore_dictionary_form
from kvocab_core.normalization import normalize_key

# 조사·어미·기호 — 판정 스트림에서 제외
_SKIP_POS = ("E", "SF", "SP", "SE", "SO", "SW", "SB", "SS", "XPN", "UN", "W", "Z")

# 인사·관용 — 교재 외로 단독 경고하지 않음
_SKIP_GREETING_LEMMAS = frozenset({"안녕하다", "감사하다", "고맙다", "반갑다"})

# 1글자 조사/대명사 — 단독 unknown 판정 제외
_SKIP_STANDALONE = frozenset(
    {
        "이",
        "가",
        "을",
        "를",
        "에",
        "에서",
        "와",
        "과",
        "도",
        "만",
        "로",
        "으로",
        "의",
        "은",
        "는",
        "께",
        "한",
        "후",
        "전",
        "때",
    }
)


@dataclass
class MatchSegment:
    surface: str
    lemma: str
    start: int
    end: int


def _skip_pos(pos: str) -> bool:
    if pos.startswith(("SL", "SN", "SH")):
        return False
    return pos.startswith(_SKIP_POS)


def build_match_segments(tokens: list[MorphToken]) -> list[MatchSegment]:
    """조사는 유지, 어미·기호는 제거. 용언은 사전형(…다)으로."""
    segs: list[MatchSegment] = []
    i, n = 0, len(tokens)
    while i < n:
        tok = tokens[i]

        # 명사 + 하 → …하다
        if (
            tok.pos.startswith(("NNG", "NNB", "NR", "NP", "XR"))
            and i + 1 < n
            and tokens[i + 1].surface == "하"
            and tokens[i + 1].pos.startswith(("XSV", "XSA"))
        ):
            lemma = tok.lemma + "하다"
            segs.append(MatchSegment(tok.surface + "하", lemma, tok.start, tokens[i + 1].end))
            i += 2
            continue

        if _skip_pos(tok.pos):
            i += 1
            continue

        # 명사 + 접사(적/성/화 …) → 복합 어휘
        if tok.pos.startswith("XSN") and segs and not segs[-1].lemma.endswith("다"):
            prev = segs[-1]
            segs[-1] = MatchSegment(
                prev.surface + tok.surface,
                prev.lemma + tok.lemma,
                prev.start,
                tok.end,
            )
            i += 1
            continue

        if tok.pos.startswith("J"):
            segs.append(MatchSegment(tok.surface, tok.surface, tok.start, tok.end))
            i += 1
            continue

        if tok.pos == "NNP":
            segs.append(MatchSegment(tok.surface, tok.lemma, tok.start, tok.end))
            i += 1
            continue

        if tok.pos.startswith(
            ("VV", "VA", "VX", "VCN", "NNG", "NNB", "NR", "NP", "MM", "MAG", "MAJ", "IC", "XR")
        ):
            lemma = restore_dictionary_form(tok.lemma or tok.surface, tok.pos)
            segs.append(MatchSegment(tok.surface, lemma, tok.start, tok.end))
        i += 1
    return segs


def segment_key(parts: list[MatchSegment]) -> str:
    return normalize_key("".join(p.lemma for p in parts))


def should_skip_standalone(seg: MatchSegment) -> bool:
    if seg.lemma in _SKIP_GREETING_LEMMAS:
        return True
    if seg.lemma in _SKIP_STANDALONE:
        return True
    if len(normalize_key(seg.lemma)) <= 1 and not seg.lemma.endswith("다"):
        return True
    return False
