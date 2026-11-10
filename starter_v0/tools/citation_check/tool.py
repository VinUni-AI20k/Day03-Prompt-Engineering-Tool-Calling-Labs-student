from __future__ import annotations

import re
from typing import Any

from tools._shared import err

ALLOWED_CHECK_TYPES = {"all", "citation", "privacy"}
URL_PATTERN = re.compile(r"https?://[^\s)\]>\"']+", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
SECRET_PATTERN = re.compile(
    r"\b(?:sk-[A-Za-z0-9_-]{10,}|tvly-[A-Za-z0-9_-]{8,}|fc-[A-Za-z0-9_-]{8,}|\d{8,10}:AA[A-Za-z0-9_-]{20,})\b"
)


def check_draft_compliance(
    draft_text: str = "",
    check_type: str = "all",
) -> dict[str, Any]:
    try:
        if not isinstance(draft_text, str) or not draft_text.strip():
            raise ValueError("draft_text must be a non-empty string")

        mode = (check_type or "all").strip().lower()
        if mode not in ALLOWED_CHECK_TYPES:
            raise ValueError(f"Invalid check_type {check_type!r}; must be one of {sorted(ALLOWED_CHECK_TYPES)}")

        urls = URL_PATTERN.findall(draft_text)
        violations: list[dict[str, str]] = []

        if mode in {"all", "citation"}:
            if not urls:
                violations.append({
                    "rule": "missing_source_url",
                    "message": "Draft does not contain any http/https source citation URL.",
                })

        if mode in {"all", "privacy"}:
            emails = EMAIL_PATTERN.findall(draft_text)
            if emails:
                violations.append({
                    "rule": "pii_email_detected",
                    "message": f"Draft contains {len(emails)} email address(es), which may leak PII.",
                })
            secrets = SECRET_PATTERN.findall(draft_text)
            if secrets:
                violations.append({
                    "rule": "secret_key_detected",
                    "message": "Draft appears to contain an API key or bot token.",
                })

        return {
            "tool": "check_draft_compliance",
            "check_type": mode,
            "passed": len(violations) == 0,
            "url_count": len(urls),
            "violations": violations,
        }
    except Exception as exc:
        return err("check_draft_compliance", exc)
