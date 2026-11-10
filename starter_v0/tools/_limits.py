from __future__ import annotations

from typing import Any


def clamp_int(value: Any, default: int, low: int = 1, high: int = 20) -> int:
    """Models often send '5', 0, -1 or None for a count. Coerce to a sane int in [low, high]."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(low, min(high, number))


def pick(value: Any, allowed: tuple[str, ...], default: str) -> str:
    """Return value if it is one of the allowed enum values (case-insensitive), else default."""
    text = str(value or "").strip()
    for option in allowed:
        if text.lower() == option.lower():
            return option
    return default
