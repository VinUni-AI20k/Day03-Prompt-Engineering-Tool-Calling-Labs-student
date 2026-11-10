"""Local descriptive statistics for numeric research data."""
from __future__ import annotations

import math
import statistics
from typing import Any

from tools._shared import err


def summarize_stats(values: list[float] | None = None, statistic: str = "mean") -> dict[str, Any]:
    """Return mean, median, or sample stdev; malformed inputs return errors."""
    try:
        operations = {
            "mean": statistics.mean,
            "median": statistics.median,
            "stdev": statistics.stdev,
        }
        if not isinstance(statistic, str) or statistic not in operations:
            raise ValueError("statistic must be mean, median, or stdev")
        if not isinstance(values, list) or not values:
            raise ValueError("values must be a non-empty list of finite numbers")
        if any(type(value) not in (int, float) or not math.isfinite(value) for value in values):
            raise ValueError("values must contain only finite numbers, not booleans or strings")
        value = operations[statistic](values)
        if not math.isfinite(value):
            raise ValueError("result must be finite")
        return {"tool": "stats", "statistic": statistic, "count": len(values), "value": value}
    except Exception as exc:
        return err("stats", exc)
