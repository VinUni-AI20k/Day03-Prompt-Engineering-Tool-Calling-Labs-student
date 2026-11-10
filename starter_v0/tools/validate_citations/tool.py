from urllib.parse import urlsplit


def validate_citations(items=None):
    """Check citation fields only; never verify source content or truth."""
    if not isinstance(items, list):
        return {"tool": "validate_citations", "error": "invalid_input", "message": "items must be a list"}
    errors = []
    for index, item in enumerate(items):
        issues = []
        if not isinstance(item, dict):
            issues.append("item must be an object")
        else:
            for field in ("title", "source"):
                if not isinstance(item.get(field), str) or not item[field].strip():
                    issues.append(f"{field} must be a nonempty string")
            try:
                url = item.get("url")
                if not isinstance(url, str) or any(c.isspace() for c in url):
                    raise ValueError()
                parsed = urlsplit(url)
                if parsed.scheme not in ("http", "https") or not parsed.hostname:
                    raise ValueError()
                _ = parsed.port
            except ValueError:
                issues.append("url must be a valid HTTP(S) URL")
        if issues:
            errors.append({"index": index, "issues": issues})
    return {"tool": "validate_citations", "valid": not errors, "item_count": len(items), "errors": errors}
