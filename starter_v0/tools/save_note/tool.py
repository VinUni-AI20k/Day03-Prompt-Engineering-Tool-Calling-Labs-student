from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from tools import _shared


def save_note(
    filename: str = "",
    content: str = "",
    confirmed: bool = False,
    overwrite_confirmed: bool = False,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    """Save research content to a local Markdown file under the notes/ directory.

    Requires confirmation before writing to disk.
    """
    if not isinstance(filename, str) or not filename.strip():
        return {
            "tool": "save_note",
            "error": "invalid_filename",
            "message": "Filename cannot be empty.",
        }

    # Guard against directory traversal or separator injection
    if "/" in filename or "\\" in filename or any(part in (".", "..") for part in Path(filename.strip()).parts):
        return {
            "tool": "save_note",
            "error": "invalid_filename",
            "message": "Directory path separators or traversal parts are not allowed in filename.",
        }

    clean_name = Path(filename.strip()).name
    if not (clean_name.endswith(".md") or clean_name.endswith(".txt")):
        clean_name += ".md"

    if not isinstance(content, str) or not content.strip():
        return {
            "tool": "save_note",
            "error": "empty_content",
            "message": "Note content cannot be empty.",
        }

    # Strict boolean check: strings like "false" or truthy objects must not bypass confirmation
    if confirmed is not True:
        return {
            "tool": "save_note",
            "status": "needs_confirmation",
            "message": "Only save the note after the user explicitly confirms.",
            "preview": {
                "filename": clean_name,
                "chars": len(content),
            },
        }

    notes_dir = (base_dir or _shared.ROOT) / "notes"
    target_path = notes_dir / clean_name

    try:
        existed = target_path.exists()
        if existed and overwrite_confirmed is not True:
            return {
                "tool": "save_note",
                "status": "needs_overwrite_confirmation",
                "message": "A note with this filename already exists. Ask the user before replacing it.",
                "preview": {
                    "filename": clean_name,
                    "chars": len(content),
                    "will_overwrite": True,
                },
            }

        notes_dir.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8")
        return {
            "tool": "save_note",
            "status": "saved",
            "filename": clean_name,
            "path": str(target_path),
            "chars": len(content),
            "overwritten": existed,
        }
    except Exception as exc:
        return _shared.err("save_note", exc)
