@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  where py >nul 2>&1
  if %ERRORLEVEL%==0 (
    py -3 -m venv .venv
  ) else (
    python -m venv .venv
  )
)
call .venv\Scripts\pip install -e ".[dev]" -q
call .venv\Scripts\python -m kvocab_core.seed
call .venv\Scripts\python -m kvocab_desktop.app
