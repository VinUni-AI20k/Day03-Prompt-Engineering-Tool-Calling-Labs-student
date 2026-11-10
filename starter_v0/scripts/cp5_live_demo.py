"""Run a disclosed scripted CLI demo with the real provider/tools (not a mock)."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUESTS = [
    "Tìm 2 repository Python về research agent trên GitHub, sắp theo số sao. Trả ngắn và kèm URL.",
    "Tôi muốn lấy 2 bài đăng mới nhất nhưng chưa chọn tài khoản.",
    "Tài khoản NASA trên X, lấy 2 bài đăng mới nhất.",
    "Tôi muốn gửi nội dung 'Bản tin demo của nhóm Hehehe' lên Telegram. Hãy hỏi xác nhận trước và chưa gửi.",
    "Không, hủy gửi. Không gửi bất kỳ nội dung nào.",
]

if __name__ == "__main__":
    result = subprocess.run(
        [sys.executable, "chat.py", "--provider", "openai", "--model", "gpt-4o-mini",
         "--version", "cp5-team-live"],
        input="\n".join([*REQUESTS, "/exit", ""]),
        capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=240,
    )
    output = "Scripted inputs by Codex; live OpenAI and real tools, not a human usability test.\n" + result.stdout + result.stderr
    (ROOT / "analysis/cp5_team_cli_live.txt").write_text(output, encoding="utf-8")
    print(output)
    raise SystemExit(result.returncode)
