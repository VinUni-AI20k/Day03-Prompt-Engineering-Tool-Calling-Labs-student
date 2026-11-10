from __future__ import annotations

from typing import Any

from tools._shared import err


ALLOWED_FIELDS = {"title", "url", "source", "summary", "author", "authors", "published", "updated_at"}
DEFAULT_FIELDS = ["title", "url", "source", "published", "summary"]


def compare_sources(
    sources: list[dict[str, Any]] | None = None,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Build a deterministic side-by-side metadata comparison of research sources."""
    try:
        if not isinstance(sources, list) or len(sources) < 2:
            raise ValueError("sources must be a list containing at least 2 source objects")
        if any(not isinstance(source, dict) for source in sources):
            raise ValueError("every source must be an object")
        selected_fields = DEFAULT_FIELDS if fields is None else fields
        if not isinstance(selected_fields, list) or not selected_fields:
            raise ValueError("fields must be a non-empty list")
        if any(not isinstance(field, str) for field in selected_fields):
            raise ValueError("every field must be a string")
        invalid = set(selected_fields) - ALLOWED_FIELDS
        if invalid:
            raise ValueError(f"unsupported fields: {', '.join(sorted(invalid))}")
        if len(selected_fields) != len(set(selected_fields)):
            raise ValueError("fields must not contain duplicates")

        comparisons = []
        for index, source in enumerate(sources):
            values = {field: source.get(field) for field in selected_fields}
            present = sum(value not in (None, "", [], {}) for value in values.values())
            comparisons.append({
                "index": index,
                "label": source.get("title") or source.get("url") or f"Source {index + 1}",
                "values": values,
                "present_fields": present,
                "completeness": round(present / len(selected_fields), 3),
            })

        field_analysis = []
        for field in selected_fields:
            values = [source.get(field) for source in sources]
            populated = [value for value in values if value not in (None, "", [], {})]
            field_analysis.append({
                "field": field,
                "values": values,
                "all_present": len(populated) == len(sources),
                "all_equal": len(populated) == len(sources) and all(value == populated[0] for value in populated),
            })

        return {
            "tool": "compare_sources",
            "source_count": len(sources),
            "fields": selected_fields,
            "comparisons": comparisons,
            "field_analysis": field_analysis,
        }
    except Exception as exc:
        return err("compare_sources", exc)
