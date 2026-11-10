from __future__ import annotations

from typing import Any

from tools.datetime_window.tool import datetime_window as _datetime_window


def datetime_window(
    timeframe: str,
    reference_date: str | None = None,
    tz: str = "UTC",
) -> dict[str, Any]:
    return _datetime_window(timeframe=timeframe, reference_date=reference_date, tz=tz)


__all__ = ["datetime_window"]
