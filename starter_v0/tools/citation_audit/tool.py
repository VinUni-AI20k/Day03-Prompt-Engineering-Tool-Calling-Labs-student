from __future__ import annotations

from typing import Any

from tools._shared import err
from tools.deduplicate.tool import canonical_url


def audit_citations(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Check citation metadata locally, not factual accuracy or URL reachability."""
    try:
        if not isinstance(items, list) or len(items) > 100:
            raise ValueError("items must be a list of at most 100 objects")
        issues = []
        seen: set[str] = set()
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError("Each item must be an object")
            problems = []
            for field in ("title", "source", "url"):
                if not isinstance(item.get(field), str) or not item[field].strip():
                    problems.append(f"missing_{field}")
            if "missing_url" not in problems:
                try:
                    key = canonical_url(item["url"])
                    if key in seen:
                        problems.append("duplicate_url")
                    seen.add(key)
                except ValueError:
                    problems.append("invalid_url")
            if problems:
                issues.append({"index": index, "problems": problems})
        return {"tool": "citation_audit", "item_count": len(items), "issues": issues,
                "passed": not issues, "scope": "Metadata only; no fact checking or network requests."}
    except Exception as exc:
        return err("citation_audit", exc)
