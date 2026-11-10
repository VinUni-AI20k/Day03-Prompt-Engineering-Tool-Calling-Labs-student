from __future__ import annotations

import os
import sys
import time
from typing import Any

from providers.base import ModelResponse
from providers.openai_provider import OpenAIProvider


class OpenRouterProvider(OpenAIProvider):
    """OpenRouter uses an OpenAI-compatible Chat Completions surface.

    Team change: free (`:free`) models are often rate-limited upstream (HTTP 429).
    `complete` retries 429s with exponential backoff so a run is not invalidated by
    provider_error cases. This only changes how the API is called, not how cases are scored.
    Tune with OPENROUTER_MAX_RETRIES (default 6) and OPENROUTER_RETRY_BASE_SECONDS (default 5).
    """

    def __init__(self) -> None:
        super().__init__(
            api_key_env="OPENROUTER_API_KEY",
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            default_model="openai/gpt-4o-mini",
        )

    def complete(self, messages: list[dict[str, str]], tools: list[dict[str, Any]] | None = None, **kwargs: Any) -> ModelResponse:
        max_retries = int(os.getenv("OPENROUTER_MAX_RETRIES", "6"))
        base_delay = float(os.getenv("OPENROUTER_RETRY_BASE_SECONDS", "5"))
        attempt = 0
        while True:
            try:
                return super().complete(messages, tools, **kwargs)
            except Exception as exc:
                is_rate_limit = type(exc).__name__ == "RateLimitError" or getattr(exc, "status_code", None) == 429
                if not is_rate_limit or attempt >= max_retries:
                    raise
                delay = min(base_delay * (2 ** attempt), 60.0)
                attempt += 1
                print(f"  [openrouter] 429 rate limit, retry {attempt}/{max_retries} in {delay:.0f}s", file=sys.stderr)
                time.sleep(delay)
