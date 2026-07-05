# K-Vocab Guard — 분석기(Analyzer) 로직 Handoff (ChatGPT PRO용)

> **목적**: PySide6 데스크톱 앱의 **한국어 어휘/표현 검사 엔진** 재설계·수정.  
> UI/DB 스키마는 유지, **매칭·형태소·판정 파이프라인**을 정리하는 것이 핵심.

---

## 1. 프로젝트 한 줄

서울대 한국어 교재(2A/2B…) 기준으로 입력 문장의 어휘·표현이 **목표 단원까지 배운 범위인지** 검사한다.

- **엔진**: `kvocab_core/` (pure Python, UI 없음)
- **UI**: `kvocab_desktop/` (PySide6)
- **데이터**: SQLite + xlsx seed import

---

## 2. 절대 규칙 (하지 말 것)

| 금지 | 이유 |
|------|------|
| `Book` 중심 스키마 | 폐기됨. 단위는 `level + lesson + lemma` |
| UI/CSV에 영어 status 노출 | 한국어 라벨만 (`status_labels.py`) |
| `too_early` 이름/UI | **`before_introduced` / 「아직 이릅니다」** 만 |
| substring 매칭 | `방` ⊂ `방학` 오탐 금지 |
| xlsx 직접 수정/병합/OCR | **ChatGPT(별도)** 담당. 코드는 import만 |
| 분석 후 이슈 임의 삭제 후처리 | `_suppress_noun_with_nearby_verb` 같은 **땜빈 금지** (아래 참고) |
| 문장 전체를 하나의 lemma로 합치기 | `아주아파트가좋다` 같은 결과 금지 |

---

## 3. 확정 설계

### 3.1 핵심 단위
- `Level` + `Lesson` + `Lexeme` (lemma)
- `SurfaceForm`: observed / generated lookup key

### 3.2 order_index (전 레벨 비교 가능)

```
order_index = level_order * 1000 + unit_no * 10 + lesson_no
```

| level | prefix |
|-------|--------|
| 1A | 101 |
| 1B | 102 |
| 2A | 201 |
| 2B | 202 |
| … | … |

예: **2A 2-2** → `201 * 1000 + 2*10 + 2` = **201022**

### 3.3 판정

```
lex.first_order_index <= target_order_index  → allowed (사용 가능)
lex.first_order_index >  target_order_index  → before_introduced (아직 이릅니다)
DB에 없음                                   → unknown_* (교재 외)
```

### 3.4 UI 표시 (한국어)

| code | UI |
|------|-----|
| `allowed` | 사용 가능 (기본 테이블에서 **숨김**) |
| `before_introduced` | 아직 이릅니다 |
| `unknown_high` | 교재 외 · 난이도 높음 |
| `unknown_medium` | 교재 외 · 검토 필요 |
| `unknown_low` | 교재 외 · 참고 |
| `custom_allowed` | 허용 목록 (숨김) |

현재: `allowed`, `custom_allowed`만 숨김. **`unknown_low`는 표에 표시** (최근 변경).

### 3.5 normalize_key

- 공백·구두점 제거 후 붙임: `"가격이 비싸다"` → `"가격이비싸다"`
- import 시 `compute_lemma_key(lemma)`로 표현용 generated surface form 추가

---

## 4. 현재 분석 파이프라인 (의도)

```
입력 text
  │
  ├─① 어절 split + build_eojeol_match_keys
  │     → DB lookup (안 그래도, 이메일을→이메일, …)
  │     → covered span 기록
  │
  ├─② Kiwi 형태소 analyze → build_match_segments
  │     (조사 유지, 어미 제거, 용언 → …다)
  │
  ├─③ segment n-gram (최대 6) → segment_key → DB lookup
  │     (가격이+비싸다, 가입하다, …)
  │     → matched span consumed
  │
  ├─④ 남은 segment 단독 처리
  │     → allowlist / DB / classify_unknown
  │     → surface는 어절 단위 표시 (좋 → 좋아요)
  │
  ├─⑤ NNP → debug_ignored only
  │
  └─⑥ visible filter (allowed, custom_allowed 제외)
```

---

## 5. 관련 소스 파일 (전부 읽을 것)

| 파일 | 역할 |
|------|------|
| `src/kvocab_core/analyzer.py` | **메인**. LexemeIndex, analyze(), 어절/ ngram 매칭 |
| `src/kvocab_core/token_units.py` | Kiwi 토큰 → MatchSegment, segment_key, skip 규칙 |
| `src/kvocab_core/matching.py` | 어절 split, 조사 strip, eojeol n-gram keys |
| `src/kvocab_core/morph.py` | Kiwi singleton, restore_dictionary_form (먹→먹다) |
| `src/kvocab_core/normalization.py` | normalize_key, is_ignored_pattern |
| `src/kvocab_core/unknown_risk.py` | DB 없을 때 위험 점수 → unknown_high/medium/low |
| `src/kvocab_core/schemas.py` | AnalyzeRequest, Issue, IssueStatus |
| `src/kvocab_core/status_labels.py` | 한국어 UI 라벨 |
| `src/kvocab_core/config.py` | order_index, seed path |
| `src/kvocab_core/tools/import_xlsx.py` | xlsx → Lexeme/SurfaceForm, compute_lemma_key |
| `tests/test_analyzer_basic.py` | 분석기 회귀 테스트 |
| `tests/test_matching.py` | 어절/조사 strip 테스트 |

---

## 6. 🔴 현재 코드 버그 (즉시 수정 필요)

### 6.1 `_suppress_noun_with_nearby_verb` — **함수 삭제됐는데 호출만 남음**

`analyzer.py` 269행:
```python
issues = _suppress_noun_with_nearby_verb(issues)  # NameError
```

- **원래 의도**: `동호회`+`가입하다` 두 줄 → 한 줄로 (임시 땜빈)
- **실제**: `함께`+`좋아요` 같이 **무관한 조합도 삭제** → 사용자 분노
- **조치**: **호출 삭제**. 후처리로 이슈 지우지 말 것. 표현 매칭/consumed span으로 해결.

### 6.2 데이터 불완전

- seed xlsx: **어휘 색인 OCR draft ~375행** (`data/seed/snu2a_level_mapped_vocabulary.xlsx`)
- **단원 본문 어휘**(좋다, 함께, 이메일 등) **대부분 없음** → DB 없으면 무조건 교재 외
- 통합 xlsx `vocabulary_database.xlsx`는 **별도 ChatGPT 전사 후** import 예정

---

## 7. 사용자가 겪은 문제 (회귀 테스트로 만들 것)

| 입력 | 목표 | 기대 | 현재 문제 |
|------|------|------|-----------|
| `가격이 비싸요` | 2A 2-1 | `가격이 비싸다` → 아직 이릅니다 (표현 1건) | ✅ 대체로 OK |
| `동호회에 가입하고 싶어요` | 2A 2-1 | `가입하다` 최소 1건 | 동호회+가입하다 **중복** 가능 |
| `안녕하세요?` | 2A 2-1 | 경고 없음 (인사) | ✅ skip |
| `아주 아파트가 좋아요` | 2A 1-1 | 아주/아파트/가격 각각 판정, **좋아요 표시** | 좋다 DB 없음 → 교재 외·참고 |
| `아주 아파트가 가격이 좋아요` | 2A 1-1 | **`아주아파트가좋다` 같은 합성 lemma 금지** | ✅ eojeol 묶기 제거함 |
| `T: … S: (함께) 좋아요 함께 좋아요` | 2A 1-1 | **함께 반드시 표시** | suppress 로직이 가렸었음 |
| `안 그래도 …` | DB에 `안 그래도` 있을 때 | 통째로 1건 매칭, `안`/`그렇다` 쪼개기 X | DB 없으면 쪼개짐 |
| `방학이 시작됐어요` | 2A 9-2 | `방` 단독 before_introduced **금지** | ✅ substring 테스트 있음 |

---

## 8. token_units.py 핵심 규칙

```python
# 조사(J*) → segment에 surface=lemma=조사 (ngram에 포함)
# 어미(E*, SF, …) → 제거
# VV/VA → restore_dictionary_form → …다
# NNG + XSA/XSV "하" → …하다
# NNG + XSN(적/성/화) → 정합적
# should_skip_standalone: 조사 단독, 1글자, 인사(안녕하다)
```

**segment_key**: `normalize_key("".join(seg.lemma for seg in chunk))`  
예: `[가격, 이, 비싸다]` → `가격이비싸다`

---

## 9. matching.py 핵심

```python
split_eojeol(text)           # 공백 기준 (T:, S:, (함께) 도 어절)
strip_eojeol_particle()      # 이메일을 → 이메일
build_eojeol_match_keys()    # n-gram(2~5) + 단일 어절(+조사 strip)
```

---

## 10. unknown_risk.py

- 점수 ≥70 → unknown_high, ≥45 → medium, else **unknown_low**
- `좋다` → score 35 → **unknown_low** (DB 없을 때)
- 하드코딩: 정합적, 윤슬 등

---

## 11. 테스트 실행

```bash
cd kvocab-guard
.venv\Scripts\activate
pytest -q
```

---

## 12. ChatGPT PRO에게 요청할 작업 (제안)

1. **`_suppress_noun_with_nearby_verb` 호출 제거** (함수 재도입 금지)
2. **파이프라인 단순화** — ①어절 표현 매칭 ②morph ngram ③단어 판정, **후처리 삭제 없음**
3. **표현 매칭 시 하위 segment consumed** — 중복 이슈는 consumed/covered로만 해결
4. **다어절 표현** (`안 그래도`, `가격이 비싸다`): eojeol ngram + morph ngram, DB surface form과 일치
5. **표면형**: UI `surface` = 사용자 어절 (`좋아요`), `lemma` = 원형 (`좋다`)
6. **회귀 테스트** 위 §7 표 전부 추가
7. xlsx/데이터는 건드리지 말 것 — 로직만

---

## 13. analyzer.py 전체 (2025-07-05 스냅샷)

```python
# src/kvocab_core/analyzer.py — 395 lines
# ⚠️ line 269: _suppress_noun_with_nearby_verb(issues) → NameError
# 리포지토리에서 직접 읽을 것: kvocab-guard/src/kvocab_core/analyzer.py
```

---

## 14. token_units.py / matching.py / morph.py / unknown_risk.py

리포지토리 경로:
- `kvocab-guard/src/kvocab_core/token_units.py`
- `kvocab-guard/src/kvocab_core/matching.py`
- `kvocab-guard/src/kvocab_core/morph.py`
- `kvocab-guard/src/kvocab_core/unknown_risk.py`
- `kvocab-guard/src/kvocab_core/normalization.py`

---

## 15. 테스트 파일

- `kvocab-guard/tests/test_analyzer_basic.py`
- `kvocab-guard/tests/test_matching.py`

---

## 16. UI (로직과 분리, 참고만)

- `results_panel.py`: 테이블, 필터 칩, `status_label_ko`
- QFont: `table_font.py` + `app.py` app_default_font (13pt) — **UI 버그, 분석기와 무관**

---

*이 문서 + 위 파일들을 ChatGPT PRO에 붙여넣고 「§12 작업 수행」 요청.*
