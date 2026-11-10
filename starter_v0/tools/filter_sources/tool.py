from copy import deepcopy
from urllib.parse import urlsplit


def filter_sources(items=None, allowed_domains=None, blocked_domains=None):
    """Filter collected items by hostname; block rules take precedence."""
    try:
        if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
            raise ValueError("items must be a list of objects")

        def domains(values):
            if values is None:
                return []
            if not isinstance(values, list):
                raise ValueError("domain filters must be lists")
            result = []
            for value in values:
                if not isinstance(value, str):
                    raise ValueError("domains must be bare hostnames")
                value = value.lower().rstrip(".")
                labels = value.split(".")
                if not value or any(not label or not all(c.isascii() and (c.isalnum() or c == "-") for c in label)
                                    or label.startswith("-") or label.endswith("-") for label in labels):
                    raise ValueError("domains must be bare hostnames without URL paths or ports")
                result.append(value)
            return result

        allowed, blocked = domains(allowed_domains), domains(blocked_domains)
        kept = []
        for index, item in enumerate(items):
            url = item.get("url")
            if not isinstance(url, str) or any(c.isspace() for c in url):
                raise ValueError(f"items[{index}].url must be an HTTP(S) URL")
            parsed = urlsplit(url)
            if parsed.scheme not in ("http", "https") or not parsed.hostname:
                raise ValueError(f"items[{index}].url must be an HTTP(S) URL")
            _ = parsed.port
            host = parsed.hostname.lower().rstrip(".")
            def matches(domain):
                return host == domain or host.endswith("." + domain)
            if (not allowed or any(map(matches, allowed))) and not any(map(matches, blocked)):
                kept.append(deepcopy(item))
        return {"tool": "filter_sources", "items": kept, "removed_count": len(items) - len(kept)}
    except ValueError as exc:
        return {"tool": "filter_sources", "error": "invalid_input", "message": str(exc)}
