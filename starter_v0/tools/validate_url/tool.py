from __future__ import annotations

import ipaddress
import os
import re
from typing import Any
from urllib.parse import urlsplit

from tools._shared import err


SHORTENER_DOMAINS = {
    "bit.ly",
    "buff.ly",
    "is.gd",
    "ow.ly",
    "t.co",
    "tiny.cc",
    "tinyurl.com",
}
DOMAIN_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


def _normalize_domain(value: str) -> str:
    domain = value.strip().rstrip(".").lower()
    if not domain:
        raise ValueError("domain must not be empty")
    try:
        return str(ipaddress.ip_address(domain))
    except ValueError:
        try:
            ascii_domain = domain.encode("idna").decode("ascii")
        except UnicodeError as exc:
            raise ValueError(f"invalid domain: {value}") from exc
        labels = ascii_domain.split(".")
        if any(not DOMAIN_LABEL.fullmatch(label) for label in labels):
            raise ValueError(f"invalid domain: {value}")
        return ascii_domain


def validate_url(url: str = "") -> dict[str, Any]:
    try:
        if not isinstance(url, str) or not url.strip():
            raise ValueError("url must be a non-empty string")

        raw_url = url.strip()
        try:
            parsed = urlsplit(raw_url)
            host = parsed.hostname
            parsed.port
        except ValueError as exc:
            return {
                "tool": "validate_url",
                "url": raw_url,
                "valid": False,
                "is_shortened": False,
                "is_blocked": False,
                "blacklist_configured": bool(os.getenv("URL_BLACKLIST_DOMAINS", "").strip()),
                "domain": None,
                "reason": str(exc),
            }

        if parsed.scheme.lower() not in {"http", "https"} or not host:
            return {
                "tool": "validate_url",
                "url": raw_url,
                "valid": False,
                "is_shortened": False,
                "is_blocked": False,
                "blacklist_configured": bool(os.getenv("URL_BLACKLIST_DOMAINS", "").strip()),
                "domain": host,
                "reason": "URL must use http or https and include a hostname",
            }
        if parsed.username is not None or parsed.password is not None:
            return {
                "tool": "validate_url",
                "url": raw_url,
                "valid": False,
                "is_shortened": False,
                "is_blocked": False,
                "blacklist_configured": bool(os.getenv("URL_BLACKLIST_DOMAINS", "").strip()),
                "domain": host,
                "reason": "URLs containing embedded credentials are not accepted",
            }

        try:
            normalized_host = _normalize_domain(host)
        except ValueError as exc:
            return {
                "tool": "validate_url",
                "url": raw_url,
                "valid": False,
                "is_shortened": False,
                "is_blocked": False,
                "blacklist_configured": bool(os.getenv("URL_BLACKLIST_DOMAINS", "").strip()),
                "domain": host,
                "reason": str(exc),
            }
        configured_domains = [
            _normalize_domain(item)
            for item in os.getenv("URL_BLACKLIST_DOMAINS", "").split(",")
            if item.strip()
        ]
        is_shortened = any(
            normalized_host == item or normalized_host.endswith(f".{item}")
            for item in SHORTENER_DOMAINS
        )
        is_blocked = any(
            normalized_host == item or normalized_host.endswith(f".{item}")
            for item in configured_domains
        )
        return {
            "tool": "validate_url",
            "url": raw_url,
            "valid": True,
            "is_shortened": is_shortened,
            "is_blocked": is_blocked,
            "blacklist_configured": bool(configured_domains),
            "domain": normalized_host,
            "reason": None,
        }
    except Exception as exc:
        return err("validate_url", exc)
