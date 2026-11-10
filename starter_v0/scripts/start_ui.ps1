param([int]$Port = 8501)
$ErrorActionPreference = 'Stop'
$starterRoot = Split-Path $PSScriptRoot -Parent
$repoRoot = Split-Path $starterRoot -Parent
$python = Join-Path $repoRoot 'venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    $python = Join-Path $repoRoot '.venv/Scripts/python.exe'
}
if (-not (Test-Path -LiteralPath $python)) {
    $python = (Get-Command python -ErrorAction Stop).Source
}
Push-Location $starterRoot
try {
    & $python -m streamlit run app.py --server.address=127.0.0.1 --server.port=$Port --server.enableAgentApi=false
} finally {
    Pop-Location
}
