#!/usr/bin/env bash
set -euo pipefail

starter_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
venv_python="$starter_root/.venv/bin/python"

if [[ ! -x "$venv_python" ]]; then
  echo "Không tìm thấy Python executable trong venv: $venv_python" >&2
  exit 1
fi
if ! command -v cloudflared >/dev/null 2>&1; then
  echo "Không tìm thấy cloudflared trong PATH." >&2
  exit 1
fi

cd "$starter_root"
"$venv_python" -m streamlit run app.py --server.headless true &
ui_pid=$!
cleanup() {
  kill "$ui_pid" 2>/dev/null || true
}
trap cleanup EXIT INT TERM
cloudflared tunnel --url http://localhost:8501
