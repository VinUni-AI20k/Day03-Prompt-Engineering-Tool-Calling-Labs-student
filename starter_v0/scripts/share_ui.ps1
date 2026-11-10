param([int]$Port = 8501)
$ErrorActionPreference = 'Stop'
$tool = Get-Command cloudflared -ErrorAction SilentlyContinue
if ($tool) {
    & $tool.Source tunnel --url "http://127.0.0.1:$Port"
} else {
    $localTool = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) '.tools/cloudflared.exe'
    if (-not (Test-Path -LiteralPath $localTool)) {
        throw 'Cài cloudflared hoặc đặt binary tại .tools/cloudflared.exe, rồi chạy lại.'
    }
    & $localTool tunnel --url "http://127.0.0.1:$Port"
}
