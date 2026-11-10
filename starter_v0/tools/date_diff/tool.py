from __future__ import annotations

from datetime import date
from typing import Any

from tools._shared import err


def date_diff(start_date: str = "", end_date: str = "") -> dict[str, Any]:
    """Number of days from start_date to end_date. Both dates use the ISO format YYYY-MM-DD."""
    try:
        start = date.fromisoformat((start_date or "").strip())
        end = date.fromisoformat((end_date or "").strip())
        days = (end - start).days
        return {
            "tool": "date_diff",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "days": days,
            "weeks": round(days / 7, 1),
        }
    except Exception as exc:
        return err("date_diff", exc)
