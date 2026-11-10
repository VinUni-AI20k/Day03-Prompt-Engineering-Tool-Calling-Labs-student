"""Redact sensitive data (PII / secrets) from a block of text.

Local tool: no API key, no network. The model should call this BEFORE handing
text to any live tool (lookup, fetch, timeline, social_search, send) when the
user pasted something sensitive.

Trust boundary: the returned `findings` only carry the *type* and the *count*
of each redaction. Raw secret values are never echoed back, so the tool output
is safe to log in a transcript or a report.
"""
from __future__ import annotations

import re
from typing import Any

from tools._shared import err


TOOL_NAME = "redact_text"

# (type, regex). Order matters: the whole text is scanned in ONE pass, so the
# first pattern that matches a span wins.
#   - bearer_token before secret_assignment: otherwise "Authorization: Bearer <tok>"
#     would be masked only up to the word "Bearer" and leak the token.
#   - url_credentials before email: a URL like https://u:p@h must be masked whole.
DEFAULT_PATTERNS: list[tuple[str, str]] = [
    ("bearer_token", r"(?:\b[Aa]uthorization\s*:\s*)?\bBearer\s+[A-Za-z0-9._\-]{8,}"),
    ("api_key", r"\b(?:sk-[A-Za-z0-9_\-]{8,}|tvly-[A-Za-z0-9_\-]{8,}|fc-[A-Za-z0-9_\-]{8,}|ghp_[A-Za-z0-9]{8,}|AKIA[A-Z0-9]{8,}|xox[baprs]-[A-Za-z0-9\-]{8,})"),
    ("url_credentials", r"\b[a-zA-Z][a-zA-Z0-9+.\-]*://[^\s/:@]+:[^\s/@]+@"),
    ("secret_assignment", r"\b(?:api[_-]?key|secret|token|password|passwd|pwd|authorization)\b\s*[:=]\s*[\"']?[A-Za-z0-9._\-]{6,}[\"']?"),
    ("email", r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
    ("phone", r"(?<![\w])(?:\+?84|0)(?:[\s.\-]?\d){8,10}(?![\w])"),
]


def _normalize_extra_patterns(extra_patterns: Any) -> list[str]:
    """Validate the model's extra_patterns argument and return it as a list."""
    if extra_patterns is None:
        return []
    if isinstance(extra_patterns, str):
        # The model sent a bare string instead of a list of strings.
        extra_patterns = [extra_patterns]
    elif not isinstance(extra_patterns, (list, tuple)):
        raise TypeError(
            f"extra_patterns must be a list of regex strings, got {type(extra_patterns).__name__}"
        )
    patterns = list(extra_patterns)
    for pattern in patterns:
        if not isinstance(pattern, str):
            raise TypeError(
                f"extra_patterns entries must be strings, got {type(pattern).__name__}"
            )
    return patterns


def _build_matcher(extra_patterns: list[str]) -> tuple[re.Pattern[str], list[str]]:
    """Build ONE combined regex: custom patterns first, then the defaults.

    A single pass means custom patterns can never partially consume a default
    match (which would leak the rest of a secret), and the replacement text
    can never be re-matched by another pattern (no nested placeholders).
    """
    parts: list[str] = []
    custom_names: list[str] = []
    for index, pattern in enumerate(extra_patterns):
        name = f"custom_{index}"
        parts.append(f"(?P<{name}>{pattern})")
        custom_names.append(name)
    for name, pattern in DEFAULT_PATTERNS:
        parts.append(f"(?P<{name}>{pattern})")
    try:
        return re.compile("|".join(parts), re.IGNORECASE), custom_names
    except re.error as exc:
        raise ValueError(f"Invalid regex in extra_patterns: {exc}") from exc


def redact_text(text: str = "", extra_patterns: list[str] | None = None) -> dict[str, Any]:
    """Mask PII and secrets in `text`.

    Returns an error dict (never raises) on bad input from the model.
    """
    try:
        if not isinstance(text, str):
            raise TypeError(f"text must be a string, got {type(text).__name__}")
        if not text.strip():
            raise ValueError("text is empty - nothing to redact")

        custom = _normalize_extra_patterns(extra_patterns)
        matcher, custom_names = _build_matcher(custom)

        counts: dict[str, int] = {}

        def _replace(match: re.Match[str]) -> str:
            groups = match.groupdict()
            label: str | None = None
            # Defaults win over custom patterns when both match the same span.
            for name, _ in DEFAULT_PATTERNS:
                if groups.get(name) is not None:
                    label = name
                    break
            if label is None:
                for name in custom_names:
                    if groups.get(name) is not None:
                        label = "custom"
                        break
            if label is None:
                label = "unknown"
            counts[label] = counts.get(label, 0) + 1
            return f"[REDACTED:{label}]"

        redacted = matcher.sub(_replace, text)

        return {
            "tool": TOOL_NAME,
            "redacted_text": redacted,
            "redaction_count": sum(counts.values()),
            "findings": [
                {"type": name, "count": count}
                for name, count in sorted(counts.items())
            ],
            "chars_in": len(text),
            "chars_out": len(redacted),
            "note": "Raw secret values are never echoed back; findings carry only type and count.",
        }
    except Exception as exc:
        return err(TOOL_NAME, exc)
