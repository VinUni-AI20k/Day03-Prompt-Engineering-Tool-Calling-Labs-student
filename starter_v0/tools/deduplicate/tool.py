from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err


def deduplicate(items: list[dict[str, Any]]) -> dict[str, Any]:
    # Kiểm tra input
    if not isinstance(items, list):
        return {
            "tool": "deduplicate",
            "error": "invalid_input",
            "message": "items phải là một list.",
        }
    seen_urls =set()
    unique_items = []
    removed_count= 0
    for item in items:
        if not isinstance(item, dict):
            return{
                "tool": "deduplicate",
                "error": "invalid_input",
                "message": "Mỗi item phải là một dictionary.",
            }
        
        url = item.get("url")
    
        if url is not None and not isinstance(url,str):
            return {
                    "tool": "deduplicate",
                    "error": "invalid_input",
                    "message": "url phải là chuỗi hoặc None.",
                }
        if not url:
            unique_items.append(item)
            continue

        if url in seen_urls: 
            removed_count+=1
            continue
        
        seen_urls.add(url)
        unique_items.append(item)
    return {
        "tool": "deduplicate",
        "items": unique_items,
        "removed_count": removed_count,
    }

