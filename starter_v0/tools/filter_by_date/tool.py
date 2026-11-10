from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from tools._shared import err


ALLOWED_DATE_FIELDS = {"published", "updated", "created_at", "updated_at"}


def _parse_date(value: str, label: str) -> date:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty ISO date string")
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(timezone.utc)
        return parsed.date()
    except ValueError:
        try:
            return date.fromisoformat(normalized)
        except ValueError as exc:
            raise ValueError(f"{label} must use ISO format YYYY-MM-DD or an ISO datetime") from exc


def filter_sources_by_date(
    items: list[dict[str, Any]] | None = None,
    start_date: str = "",
    end_date: str = "",
    date_field: str = "published",
    include_undated: bool = False,
) -> dict[str, Any]:
    """Filter research sources to an inclusive ISO date range."""
    try:
        if not isinstance(items, list):
            raise ValueError("items must be a list of source objects")
        if date_field not in ALLOWED_DATE_FIELDS:
            raise ValueError(f"date_field must be one of: {', '.join(sorted(ALLOWED_DATE_FIELDS))}")
        if not isinstance(include_undated, bool):
            raise ValueError("include_undated must be a boolean")
        if not start_date and not end_date:
            raise ValueError("at least one of start_date or end_date is required")

        lower = _parse_date(start_date, "start_date") if start_date else None
        upper = _parse_date(end_date, "end_date") if end_date else None
        if lower and upper and lower > upper:
            raise ValueError("start_date must not be after end_date")

        matched: list[dict[str, Any]] = []
        excluded: list[dict[str, Any]] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError(f"items[{index}] must be an object")
            value = item.get(date_field)
            if value in (None, ""):
                if include_undated:
                    matched.append(item)
                else:
                    excluded.append({"index": index, "reason": "missing_date", "item": item})
                continue
            if not isinstance(value, str):
                raise ValueError(f"items[{index}].{date_field} must be an ISO date string")
            try:
                item_date = _parse_date(value, f"items[{index}].{date_field}")
            except ValueError:
                excluded.append({"index": index, "reason": "invalid_date", "item": item})
                continue
            if lower and item_date < lower:
                excluded.append({"index": index, "reason": "before_start", "item": item})
            elif upper and item_date > upper:
                excluded.append({"index": index, "reason": "after_end", "item": item})
            else:
                matched.append(item)

        return {
            "tool": "filter_by_date",
            "date_field": date_field,
            "start_date": start_date,
            "end_date": end_date,
            "input_count": len(items),
            "matched_count": len(matched),
            "excluded_count": len(excluded),
            "items": matched,
            "excluded": excluded,
        }
    except Exception as exc:
        return err("filter_by_date", exc)
