# Local dev server — watches app/ only (avoids scanning .venv on Windows).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Error "Create the venv first: python -m venv .venv && .\.venv\Scripts\pip install -r requirements.txt"
}

& $py -m uvicorn app.main:app `
    --host 127.0.0.1 `
    --port 8000 `
    --reload `
    --reload-dir app
