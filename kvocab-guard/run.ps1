# K-Vocab Guard launcher (Windows)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    py -3 -m venv .venv
}

& .\.venv\Scripts\pip install -e ".[dev]" -q
& .\.venv\Scripts\python -m kvocab_core.seed
& .\.venv\Scripts\python -m kvocab_desktop.app
