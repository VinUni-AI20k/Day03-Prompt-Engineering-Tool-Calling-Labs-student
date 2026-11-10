from __future__ import annotations

import os

from providers.openai_provider import OpenAIProvider


class GroqProvider(OpenAIProvider):
    """Groq OpenAI-compatible Chat Completions API (tool calling supported)."""

    def __init__(self) -> None:
        super().__init__(
            api_key_env="GROQ_API_KEY",
            base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
            # Free-tier accounts often lack llama-3.3-70b; gpt-oss models support tool calling.
            default_model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),

        )
