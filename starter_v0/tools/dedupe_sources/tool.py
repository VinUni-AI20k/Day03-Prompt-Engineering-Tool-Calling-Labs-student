from __future__ import annotations

from urllib.parse import urlsplit


def dedupe_sources(urls: list[str]) -> dict[str, list[str] | int | str]:
    if not isinstance(urls, list) or any(not isinstance(url, str) for url in urls):
        return {"error": "invalid_input", "message": "urls must be a list of strings."}

    for index, url in enumerate(urls):
        try:
            parsed = urlsplit(url)
        except ValueError:
            parsed = None
        if (
            parsed is None
            or parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or any(character.isspace() for character in url)
        ):
            return {"error": "invalid_url", "message": f"urls[{index}] must be an HTTP(S) URL with a host."}

    unique_urls = list(dict.fromkeys(urls))
    return {"urls": unique_urls, "duplicate_count": len(urls) - len(unique_urls)}
