from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def send_telegram(text: str = "", confirmed: bool = False, **kwargs) -> dict[str, Any]:

    if not confirmed:
        return {
            "tool": "send",
            "status": "needs_confirmation",
            "message": "CẢNH BÁO: Bạn chưa xác nhận gửi tin nhắn. Vui lòng hỏi lại người dùng hoặc yêu cầu xác nhận trước khi gọi lại tool này.",
        }
    
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not token or not chat_id:
            raise RuntimeError("Missing TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID env var")
            
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        
        response = requests.post(url, json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        
        res_data = response.json()
        message_id = res_data.get("result", {}).get("message_id")
        
        return {
            "tool": "send",
            "status": "sent",
            "telegram_message_id": message_id,
            "message": "Đã gửi tin nhắn thành công lên Telegram!"
        }
        
    except Exception as exc:
        return err("send", exc)