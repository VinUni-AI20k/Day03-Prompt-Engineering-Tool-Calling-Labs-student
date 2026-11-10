from __future__ import annotations

from typing import Any

from tools._shared import domain, err


TIER_DOMAINS: dict[str, tuple[str, float]] = {
    # Academic & research publications
    "arxiv.org": ("academic", 0.95),
    "nature.com": ("academic", 0.98),
    "science.org": ("academic", 0.98),
    "ieee.org": ("academic", 0.95),
    "acm.org": ("academic", 0.95),
    "biorxiv.org": ("academic", 0.95),
    "nih.gov": ("academic", 0.97),
    "edu": ("academic", 0.90),

    # Verified mainstream news agencies
    "reuters.com": ("verified_news", 0.92),
    "apnews.com": ("verified_news", 0.92),
    "bbc.com": ("verified_news", 0.90),
    "nytimes.com": ("verified_news", 0.88),
    "wsj.com": ("verified_news", 0.88),
    "bloomberg.com": ("verified_news", 0.89),
    "vnexpress.net": ("verified_news", 0.85),
    "tuoitre.vn": ("verified_news", 0.85),

    # Official tech labs and primary tech media
    "openai.com": ("tech_media", 0.88),
    "anthropic.com": ("tech_media", 0.88),
    "deepmind.google": ("tech_media", 0.90),
    "github.com": ("tech_media", 0.82),
    "techcrunch.com": ("tech_media", 0.80),
    "theverge.com": ("tech_media", 0.78),
    "wired.com": ("tech_media", 0.80),

    # Community and social media
    "x.com": ("community", 0.50),
    "twitter.com": ("community", 0.50),
    "reddit.com": ("community", 0.45),
}

TIER_ORDER: dict[str, int] = {
    "academic": 4,
    "verified_news": 3,
    "tech_media": 2,
    "community": 1,
    "unverified": 0,
}


def check_source_credibility(url: str = "", min_tier: str = "all") -> dict[str, Any]:
    """Assess the credibility, authority tier, and reliability of a web domain or URL."""
    try:
        if not url or not isinstance(url, str) or not url.strip():
            return {
                "tool": "source_credibility",
                "error": "ValueError",
                "message": "URL string must be provided and cannot be empty.",
            }

        cleaned_url = url.strip()
        if not cleaned_url.startswith(("http://", "https://")):
            cleaned_url = f"https://{cleaned_url}"

        parsed_domain = domain(cleaned_url).lower()
        if not parsed_domain:
            return {
                "tool": "source_credibility",
                "error": "ValueError",
                "message": f"Could not parse valid domain from url: {url!r}",
            }

        tier = "unverified"
        score = 0.30
        for known_domain, (known_tier, known_score) in TIER_DOMAINS.items():
            if parsed_domain == known_domain or parsed_domain.endswith(f".{known_domain}"):
                tier = known_tier
                score = known_score
                break

        min_tier_normalized = (min_tier or "all").strip().lower()
        required_level = TIER_ORDER.get(min_tier_normalized, 0)
        actual_level = TIER_ORDER.get(tier, 0)

        meets_min_tier = actual_level >= required_level
        is_reliable = score >= 0.75 and meets_min_tier

        if tier in ("academic", "verified_news"):
            recommendation = "Highly credible source. Safe for facts, citations, and reporting."
        elif tier == "tech_media":
            recommendation = "Reputable primary or tech source. Cross-reference when necessary."
        elif tier == "community":
            recommendation = "User-generated content. Requires external independent verification."
        else:
            recommendation = "Unverified source. Treat with caution and verify independently."

        return {
            "tool": "source_credibility",
            "url": url,
            "domain": parsed_domain,
            "tier": tier,
            "score": score,
            "min_tier": min_tier_normalized,
            "meets_min_tier": meets_min_tier,
            "is_reliable": is_reliable,
            "recommendation": recommendation,
        }
    except Exception as exc:
        return err("source_credibility", exc)
