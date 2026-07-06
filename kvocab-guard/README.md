# kvocab-guard

사용자용 안내는 레포 루트의 [README.md](../README.md)를 참고하세요.

## 빠른 실행 (Windows)

```powershell
cd kvocab-guard
.\run.bat
```

또는:

```powershell
cd kvocab-guard
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
python -m kvocab_core.seed
python -m kvocab_desktop.app
```

> `app.py`를 직접 실행하면 `No module named kvocab_desktop` 오류가 날 수 있습니다. 패키지 설치 후 `-m`으로 실행하세요.

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

## 배포

GitHub Actions **Release** 워크플로를 수동 실행하면 Windows portable zip이 [Releases](https://github.com/baggychani/Korean_Edu_Voca_Check/releases)에 올라갑니다.

```bash
python scripts/sync_version.py --set 0.0.1   # 버전 일괄 동기화
python scripts/sync_version.py --check
```

## 구조

- `kvocab_core` — 어휘 DB, 형태소 분석, 검사 엔진
- `kvocab_desktop` — PySide6 데스크톱 UI

판정: `first_order_index <= target_order_index` → 사용 가능, 그렇지 않으면 아직 이릅니다.
