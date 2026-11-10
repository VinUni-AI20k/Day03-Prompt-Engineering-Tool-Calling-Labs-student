"""Lưu bản sao system_prompt.md + tools.yaml hiện tại vào artifacts/versions/<version>/.

Chạy từ starter_v0/ ngay sau khi chạy eval cho một version:
    python scripts/snapshot_version.py v3

UI (app.py) đọc các thư mục này để chat lại với version cũ.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from versioning import build_artifact_version  # noqa: E402

ARTIFACTS_DIR = ROOT / "artifacts"
VERSIONS_DIR = ARTIFACTS_DIR / "versions"
FILES = ("system_prompt.md", "tools.yaml")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("version", help="Nhãn version, ví dụ v3")
    parser.add_argument("--force", action="store_true", help="Ghi đè nếu snapshot đã tồn tại")
    args = parser.parse_args()

    target = VERSIONS_DIR / args.version
    if target.exists() and not args.force:
        print(f"{target.relative_to(ROOT)} đã tồn tại. Thêm --force nếu muốn ghi đè.", file=sys.stderr)
        return 1
    target.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        shutil.copy2(ARTIFACTS_DIR / name, target / name)

    av = build_artifact_version(args.version, target / "system_prompt.md", target / "tools.yaml")
    print(f"Saved {target.relative_to(ROOT)}  ->  {av.artifact_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
