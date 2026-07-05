# K-Vocab Guard

서울대 한국어 교재 기준 **어휘·표현 검사** 데스크톱 프로그램입니다.

- **핵심 데이터**: `level + lesson + page + lemma`
- **판정**: `first_order_index <= target_order_index` → 사용 가능, 그렇지 않으면 아직 이릅니다
- **Engine** (`kvocab_core`)과 **UI** (`kvocab_desktop`) 분리

## 실행 방법

**가장 쉬운 방법 (Windows):** `kvocab-guard` 폴더에서 `run.bat` 더블클릭 또는:

```powershell
cd kvocab-guard
.\run.bat
```

> `app.py`를 Python으로 **직접** 실행하면 `No module named kvocab_desktop` 오류가 납니다.  
> 반드시 아래처럼 **패키지 설치 후 `-m`으로** 실행하세요.

```bash
cd kvocab-guard
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e ".[dev]"
python -m kvocab_core.seed
python -m kvocab_desktop.app
```

## lint / test

```bash
ruff check --fix src tests
ruff format src tests
pytest
```

## CLI

```bash
python -m kvocab_core.seed
python -m kvocab_core.tools.import_xlsx data/seed/snu2a_level_mapped_vocabulary.xlsx
python -m kvocab_core.analyzer_cli --level 2A --lesson 2-1 --text "저는 요리하는 걸 좋아해요."
```

## order_index

```
order_index = level_order * 1000 + unit_no * 10 + lesson_no
```

| level | level_order |
|-------|-------------|
| 1A | 101 |
| 1B | 102 |
| 2A | 201 |
| 2B | 202 |
| … | … |

예: **2A 2-2** → `201022`

## Seed 데이터

`data/seed/snu2a_level_mapped_vocabulary.xlsx` (시트: `Level_Map`, `Vocabulary`)

import 시 xlsx의 `order_index`는 **재계산** 후 검증합니다.

## 테스트

```bash
pytest
```

## 문제 해결

- **kiwipiepy 설치 실패**: 자동으로 regex fallback 형태소 분석기를 사용합니다.
- **HWP 추출 실패**: HWPX 또는 PDF로 저장 후 다시 열어 주세요.
- **PDF 텍스트가 비어 있음**: 이미지 PDF입니다. OCR이 필요합니다.

## UI 판정 표시 (한국어만)

| 내부 코드 | 화면 |
|-----------|------|
| allowed | 사용 가능 |
| before_introduced | 아직 이릅니다 |
| unknown_high | 교재 외 · 난이도 높음 |
| unknown_medium | 교재 외 · 검토 필요 |
| unknown_low | 교재 외 · 참고 |

OCR draft 데이터는 사전·데이터 탭에 **검토 중** 뱃지로 표시됩니다.
