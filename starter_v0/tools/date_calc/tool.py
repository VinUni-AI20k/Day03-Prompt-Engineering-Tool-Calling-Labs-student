
from datetime import date, datetime, timedelta
import re


def _parse_date(value):
    """Parse a strict YYYY-MM-DD date string."""
    if value == "today":
        return date.today()
    
    if not isinstance(value, str):
        raise ValueError("Date must be a string in YYYY-MM-DD format")

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError(f"Invalid date format: {value}. Expected YYYY-MM-DD")

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid calendar date: {value}")


def date_calc(op, date1=None, date2=None, days=None) -> dict:
    """
    Calculate dates and date differences.

    Operations:
        today: Return today's date.
        diff_days: Return date2 - date1 in days.
        add_days: Add days to date1.
        weekday: Return the weekday name of date1.

    Invalid inputs return an error dictionary.
    """
    try:
        if op == "today":
            return {"result": date.today().isoformat()}

        elif op == "diff_days":
            if date1 is None or date2 is None:
                raise ValueError("diff_days requires date1 and date2")

            start = _parse_date(date1)
            end = _parse_date(date2)

            return {"result": (end - start).days}

        elif op == "add_days":
            if date1 is None or days is None:
                raise ValueError("add_days requires date1 and days")

            if isinstance(days, bool) or not isinstance(days, int):
                raise ValueError("days must be an integer")

            start = _parse_date(date1)
            result = start + timedelta(days=days)

            return {"result": result.isoformat()}

        elif op == "weekday":
            if date1 is None:
                raise ValueError("weekday requires date1")

            parsed = _parse_date(date1)
            return {"result": parsed.strftime("%A")}

        else:
            raise ValueError(
                f"Unsupported operation: {op}. "
                "Supported operations: today, diff_days, add_days, weekday"
            )

    except (ValueError, OverflowError, TypeError) as exc:
        return {"error": str(exc)}
