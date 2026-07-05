from __future__ import annotations

from kvocab_core.normalization import normalize_key

# 어절 끝 조사·어미 — lookup 시 제거 후보 (긴 것부터)
_EOJEOL_PARTICLE_SUFFIXES = (
    "이라고",
    "라고",
    "처럼",
    "까지",
    "부터",
    "에서",
    "으로",
    "한테",
    "에게",
    "이랑",
    "하고",
    "이나",
    "든지",
    "밖에",
    "마다",
    "에게",
    "께서",
    "이라",
    "이랑",
    "과",
    "와",
    "을",
    "를",
    "은",
    "는",
    "이",
    "가",
    "의",
    "에",
    "도",
    "만",
    "로",
    "께",
    "한",
)


def split_eojeol(text: str) -> list[str]:
    return [p for p in text.split() if p.strip()]


def strip_eojeol_particle(eojeol: str) -> str:
    """이메일을 → 이메일, 원고와 → 원고 (lookup용 stem)."""
    for suf in _EOJEOL_PARTICLE_SUFFIXES:
        if eojeol.endswith(suf) and len(eojeol) > len(suf):
            return eojeol[: -len(suf)]
    return eojeol


def eojeol_lookup_keys(eojeol: str) -> list[str]:
    """어절 하나에서 시도할 normalized lookup key 목록 (중복 제거, 순서 유지)."""
    keys: list[str] = []
    for candidate in (eojeol, strip_eojeol_particle(eojeol)):
        key = normalize_key(candidate)
        if key and key not in keys:
            keys.append(key)
    return keys


def build_ngram_keys(
    tokens: list[str], min_n: int = 2, max_n: int = 5
) -> list[tuple[str, int, int]]:
    """Return (normalized_key, start_token_idx, end_token_idx_exclusive)."""
    results: list[tuple[str, int, int]] = []
    n = len(tokens)
    for size in range(min(max_n, n), min_n - 1, -1):
        for i in range(n - size + 1):
            span = tokens[i : i + size]
            key = normalize_key(" ".join(span))
            if key:
                results.append((key, i, i + size))
    return results


def build_eojeol_match_keys(eojeol: list[str], max_n: int = 5) -> list[tuple[str, int, int]]:
    """다어절 n-gram + 단일 어절(조사 제거 포함) lookup key."""
    results: list[tuple[str, int, int]] = []
    seen: set[tuple[str, int, int]] = set()
    n = len(eojeol)

    for size in range(min(max_n, n), 1, -1):
        for i in range(n - size + 1):
            span = eojeol[i : i + size]
            key = normalize_key(" ".join(span))
            if key:
                item = (key, i, i + size)
                if item not in seen:
                    seen.add(item)
                    results.append(item)

    for i, eo in enumerate(eojeol):
        for key in eojeol_lookup_keys(eo):
            item = (key, i, i + 1)
            if item not in seen:
                seen.add(item)
                results.append(item)

    return results


def exact_token_match(token_norm: str, known: set[str]) -> bool:
    return token_norm in known
