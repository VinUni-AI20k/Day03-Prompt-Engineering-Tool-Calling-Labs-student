from __future__ import annotations

import math
from typing import Any

from tools._shared import err


def rank_sources(items: list[dict[str, Any]] | None = None, limit: int = 5) -> dict[str, Any]:
    """Rank already-collected source items by their numeric relevance score."""
    try:
        if not isinstance(items, list):
            raise TypeError("items must be a list of research item objects")
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("limit must be a positive integer")

        scored: list[tuple[float, int, dict[str, Any]]] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise TypeError(f"items[{index}] must be an object")
            score = item.get("score")
            if score is None:
                numeric_score = -math.inf
            elif isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score):
                raise ValueError(f"items[{index}].score must be a finite number or null")
            else:
                numeric_score = float(score)
            scored.append((numeric_score, index, item))

        ranked = [item for _, _, item in sorted(scored, key=lambda entry: (-entry[0], entry[1]))[:limit]]
        return {"tool": "rank_sources", "items": ranked, "item_count": len(ranked), "limit": limit}
    except Exception as exc:
        return err("rank_sources", exc)
