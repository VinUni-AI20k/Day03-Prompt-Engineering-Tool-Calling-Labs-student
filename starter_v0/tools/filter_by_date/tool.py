from copy import deepcopy
from datetime import date


def _date(value):
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError("dates must use YYYY-MM-DD")
    return date.fromisoformat(value)


def filter_by_date(items=None, start_date=None, end_date=None):
    """Keep items within an inclusive calendar-date range."""
    try:
        start, end = _date(start_date), _date(end_date)
        if start > end:
            raise ValueError("start_date must not be after end_date")
        if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
            raise ValueError("items must be a list of objects")
        kept, excluded = [], []
        for index, item in enumerate(items):
            try:
                published = _date(item.get("date"))
            except ValueError:
                excluded.append({"index": index, "reason": "missing_or_invalid_date"})
                continue
            if start <= published <= end:
                kept.append(deepcopy(item))
            else:
                excluded.append({"index": index, "reason": "outside_range"})
        return {"tool": "filter_by_date", "items": kept, "removed_count": len(excluded), "excluded": excluded}
    except ValueError as exc:
        return {"tool": "filter_by_date", "error": "invalid_input", "message": str(exc)}
