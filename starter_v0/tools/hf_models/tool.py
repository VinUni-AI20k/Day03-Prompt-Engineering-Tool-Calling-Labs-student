"""hf_models: tìm model AI/LLM open-weight trên Hugging Face Hub (tool mới phần Bonus).

Nguyên tắc thiết kế (theo RUBRIC C4 & Bonus):
- Không bao giờ raise exception ra ngoài: mọi lỗi (input rỗng, sai kiểu, limit <= 0,
  HTTP 4xx/5xx, timeout) đều trả về dict có "error" và "next_step".
- Kiểm tra tham số đầu vào TRƯỚC khi gọi mạng để không tốn request vô ích.
- Chuẩn hóa kết quả về khuôn chung {"tool", "query", "items": [...]} để tương thích với `format`.
"""
from __future__ import annotations

import os
from typing import Any

import requests

HF_MODELS_URL = "https://huggingface.co/api/models"
DEFAULT_LIMIT = 5
MAX_LIMIT = 10  # Giới hạn tối đa 10 model mỗi lần gọi để tránh tràn ngữ cảnh.


def _error(query: str, message: str, next_step: str) -> dict[str, Any]:
    """Tạo error dict thống nhất cho mọi nhánh lỗi của hf_models."""
    return {
        "tool": "hf_models",
        "query": query,
        "items": [],
        "error": message,
        "next_step": next_step,
    }


def hf_models(query: str, task: str = "", limit: int = DEFAULT_LIMIT) -> dict[str, Any]:
    """Tìm model trên Hugging Face Hub theo từ khóa và tác vụ (pipeline_tag)."""

    # 1) Kiểm tra `query`: bắt buộc là chuỗi không rỗng.
    clean_query = query.strip() if isinstance(query, str) else ""
    if not clean_query:
        return _error(
            "",
            "missing_required_param: query must be a non-empty string",
            "Call clarify to ask the user which model name or topic to search on Hugging Face.",
        )

    # 2) Kiểm tra `limit`: None -> mặc định 5; <= 0 -> báo lỗi; > 10 -> ép về 10.
    try:
        parsed_limit = DEFAULT_LIMIT if limit is None else int(limit)
    except (TypeError, ValueError):
        parsed_limit = DEFAULT_LIMIT
    if parsed_limit <= 0:
        return _error(
            clean_query,
            f"invalid_param: limit must be a positive integer, got {limit!r}",
            f"Retry hf_models with limit between 1 and {MAX_LIMIT}.",
        )
    clamped_limit = min(parsed_limit, MAX_LIMIT)

    # 3) Chuẩn bị query params cho Hugging Face Hub API.
    clean_task = task.strip() if isinstance(task, str) else ""
    params: dict[str, Any] = {
        "search": clean_query,
        "sort": "downloads",
        "direction": "-1",
        "limit": clamped_limit,
    }
    if clean_task:
        params["filter"] = clean_task

    # 4) HF_TOKEN là tùy chọn: có thì gắn Bearer token, không có vẫn gọi public API bình thường.
    headers = {"Accept": "application/json", "User-Agent": "research-agent-lab"}
    token = os.getenv("HF_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # 5) Gọi API và bắt mọi lỗi mạng / HTTP / JSON.
    try:
        response = requests.get(
            HF_MODELS_URL,
            params=params,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        return _error(
            clean_query,
            f"hf_api_error: {exc}",
            "Tell the user Hugging Face Hub search is temporarily unavailable, or fall back to lookup.",
        )

    # 6) API của Hugging Face trả về một list các dict model.
    raw_items = payload if isinstance(payload, list) else []

    items = []
    for model in raw_items[:clamped_limit]:
        if not isinstance(model, dict):
            continue
        model_id = str(model.get("id") or model.get("modelId") or "unknown").strip()
        pipeline_tag = str(model.get("pipeline_tag") or clean_task or "unknown").strip()
        try:
            downloads = int(model.get("downloads") or 0)
        except (TypeError, ValueError):
            downloads = 0
        try:
            likes = int(model.get("likes") or 0)
        except (TypeError, ValueError):
            likes = 0
        items.append({
            "title": model_id,
            "url": f"https://huggingface.co/{model_id}" if model_id != "unknown" else "",
            "source": "huggingface.co",
            "task": pipeline_tag,
            "downloads": downloads,
            "likes": likes,
            "summary": f"Hugging Face model ({pipeline_tag}) — {downloads} downloads, {likes} likes.",
        })

    return {"tool": "hf_models", "query": clean_query, "task": clean_task, "items": items}
