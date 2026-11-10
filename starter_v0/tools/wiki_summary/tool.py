from __future__ import annotations

import urllib.parse
from typing import Any

import requests

from tools._shared import TIMEOUT, err

API = "https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
USER_AGENT = "AI20k-Day03-Research-Agent/1.0 (educational lab)"


def _fail(code: str, message: str, **extra: Any) -> dict[str, Any]:
    return {"tool": "wiki_summary", "error": code, "message": message, **extra}


def get_wiki_summary(title: str = "", lang: str = "en") -> dict[str, Any]:
    try:
        # 1. Validate
        clean_title = (title or "").strip()
        if not clean_title:
            return _fail("invalid_title", "Tiêu đề Wikipedia không được để trống")

        target_lang = (lang or "en").strip().lower()
        warning = None
        if target_lang not in ("en", "vi"):
            warning = f"Ngôn ngữ '{lang}' không được hỗ trợ, mặc định dùng 'en'"
            target_lang = "en"

        # Wikipedia dùng dấu gạch dưới thay khoảng trắng
        encoded_title = urllib.parse.quote(clean_title.replace(" ", "_"), safe=":/")
        url = API.format(lang=target_lang, title=encoded_title)

        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}

        # 2. Gọi HTTP
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        if resp.status_code == 404:
            return _fail("not_found", f"Không tìm thấy bài viết '{clean_title}' trên Wikipedia ({target_lang})", title=clean_title, lang=target_lang)
        resp.raise_for_status()
        data = resp.json()

        page_type = data.get("type", "standard")
        res: dict[str, Any] = {
            "tool": "wiki_summary",
            "title": data.get("title", clean_title),
            "lang": target_lang,
            "description": data.get("description"),
            "extract": data.get("extract"),
            "url": (data.get("content_urls", {}).get("desktop", {}) or {}).get("page"),
            "page_type": page_type,
        }
        if page_type == "disambiguation":
            res["note"] = "ambiguous, ask user to specify"
        if warning:
            res["warning"] = warning

        return res
    except Exception as exc:
        return err("wiki_summary", exc)