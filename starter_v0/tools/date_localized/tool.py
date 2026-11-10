from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from tools._shared import err


CITY_TIMEZONES = {
    "hanoi": "Asia/Ho_Chi_Minh",
    "ho chi minh city": "Asia/Ho_Chi_Minh",
    "ho chi minh": "Asia/Ho_Chi_Minh",
    "london": "Europe/London",
    "new york": "America/New_York",
    "san francisco": "America/Los_Angeles",
    "singapore": "Asia/Singapore",
    "tokyo": "Asia/Tokyo",
    "utc": "UTC",
}


def date_localized(timezone: str = "UTC") -> dict[str, Any]:
    try:
        if not isinstance(timezone, str) or not timezone.strip():
            raise ValueError("timezone must be a non-empty IANA timezone or city name")

        requested = timezone.strip()
        zone_name = CITY_TIMEZONES.get(requested.casefold(), requested)
        zone = ZoneInfo(zone_name)
        now = datetime.now(zone)
        return {
            "tool": "date_localized",
            "location": requested,
            "timezone": zone.key,
            "datetime": now.isoformat(timespec="seconds"),
            "formatted": now.strftime("%Y-%m-%d %H:%M:%S %Z (UTC%z)"),
        }
    except Exception as exc:
        return err("date_localized", exc)
