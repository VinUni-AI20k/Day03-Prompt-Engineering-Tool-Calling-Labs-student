$ErrorActionPreference = 'Stop'

$starterRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$venvPath = Join-Path $starterRoot '.venv'
$pythonPath = Join-Path $venvPath 'Scripts\python.exe'

if (-not (Test-Path -LiteralPath $venvPath -PathType Container) -or -not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    Write-Error "Không tìm thấy venv ở '$venvPath'. Hãy tạo/cài venv trong starter_v0 trước."
    exit 1
}

$cloudflared = Get-Command cloudflared -ErrorAction SilentlyContinue
if (-not $cloudflared) {
    Write-Error 'Không tìm thấy cloudflared trong PATH. Cài bằng: winget install --id Cloudflare.cloudflared; sau đó mở PowerShell mới và chạy lại script.'
    exit 1
}

$quotedRoot = $starterRoot.Replace("'", "''")
$uiCommand = 'Set-Location -LiteralPath "{0}"; & ".\.venv\Scripts\python.exe" -m streamlit run app.py --server.headless true' -f $quotedRoot
$tunnelCommand = 'Set-Location -LiteralPath "{0}"; cloudflared tunnel --url http://localhost:8501' -f $quotedRoot

Start-Process -FilePath 'powershell.exe' -ArgumentList @(
    '-NoExit', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', $uiCommand
)
Start-Process -FilePath 'powershell.exe' -ArgumentList @(
    '-NoExit', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', $tunnelCommand
)

Write-Host 'Đã mở hai terminal. Lấy URL trycloudflare.com từ terminal cloudflared.'
Write-Host 'Giữ cả hai terminal mở trong buổi thử; máy không được sleep. Tắt tunnel bằng Ctrl+C sau buổi thử.'
