from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err

HF_MODELS_API_URL = "https://huggingface.co/api/models"
ALLOWED_SORTS = {"downloads", "likes", "lastModified"}


def _parse_limit(limit: Any, *, default: int = 5, max_limit: int = 20) -> int:
    """Validate and normalize the limit argument from model output."""
    if isinstance(limit, bool):
        raise ValueError("limit must be an integer, not bool")
    parsed = int(default if limit is None else limit)
    if parsed < 1:
        raise ValueError("limit must be >= 1")
    return min(parsed, max_limit)


def _format_hf_item(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize a raw Hugging Face model entry to a standard research item."""
    model_id = str(raw.get("id") or raw.get("modelId") or "").strip()
    pipeline_tag = raw.get("pipeline_tag") or "unspecified"
    downloads = raw.get("downloads", 0)
    likes = raw.get("likes", 0)
    url = f"https://huggingface.co/{model_id}" if model_id else ""

    return {
        "model_id": model_id,
        "title": model_id or "Unknown Hugging Face model",
        "url": url,
        "source": "huggingface.co",
        "summary": f"Task: {pipeline_tag} | Downloads: {downloads} | Likes: {likes}",
        "author": raw.get("author") or (model_id.split("/")[0] if "/" in model_id else ""),
        "pipeline_tag": raw.get("pipeline_tag"),
        "downloads": downloads,
        "likes": likes,
        "last_modified": raw.get("lastModified"),
        "tags": raw.get("tags") or [],
    }


def search_hf_models(
    query: str = "",
    task: str = "",
    sort_by: str = "downloads",
    limit: int = 5,
) -> dict[str, Any]:
    """Search public models on Hugging Face Hub via its REST API."""
    try:
        # Validate inputs provided by the model before making a network call.
        if not isinstance(query, str):
            raise ValueError("query must be a string")
        cleaned_query = query.strip()
        if not cleaned_query:
            raise ValueError("query must not be empty")

        if not isinstance(task, str):
            raise ValueError("task must be a string")
        cleaned_task = task.strip()

        if not isinstance(sort_by, str) or sort_by not in ALLOWED_SORTS:
            raise ValueError(f"Invalid sort_by={sort_by!r}. Allowed: {sorted(ALLOWED_SORTS)}")

        parsed_limit = _parse_limit(limit)

        params: dict[str, Any] = {
            "search": cleaned_query,
            "sort": sort_by,
            "direction": -1,
            "limit": parsed_limit,
        }
        if cleaned_task:
            params["pipeline_tag"] = cleaned_task

        # Call requests.get directly so offline tests can intercept via fake_http.
        response = requests.get(HF_MODELS_API_URL, params=params, timeout=TIMEOUT)
        response.raise_for_status()

        raw_models = response.json()
        if not isinstance(raw_models, list):
            raise ValueError("Unexpected response format from Hugging Face API: expected a JSON list")

        items = [
            _format_hf_item(model)
            for model in raw_models
            if isinstance(model, dict) and (model.get("id") or model.get("modelId"))
        ][:parsed_limit]

        return {
            "tool": "search_hf_models",
            "query": cleaned_query,
            "task": cleaned_task or None,
            "sort_by": sort_by,
            "items": items,
        }
    except Exception as exc:
        return err("search_hf_models", exc)

