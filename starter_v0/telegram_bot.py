"""Chat with the research agent from Telegram (long polling, no webhook needed).

Run from starter_v0/:
    python telegram_bot.py --provider openai --version v3

Then open the bot in Telegram (private chat) and press Start.

Only chats listed in TELEGRAM_ALLOWED_CHAT_IDS (comma separated) may talk to the
agent, so strangers cannot spend the team's API credits. Send /start to the bot to
see your chat id, add it to starter_v0/.env, and restart this script.

The agent's `send` tool still posts to the team's private channel
(TELEGRAM_CHAT_ID) and only after the user confirms.
"""
from __future__ import annotations

import argparse
import os
import time
from pathlib import Path
from typing import Any

import requests

import server
from server import redact, settings

API_URL = "https://api.telegram.org/bot{token}/{method}"
MAX_MESSAGE_LEN = 4000  # Telegram hard limit is 4096
POLL_TIMEOUT = 25

HELP_TEXT = (
    "Mình là Research Agent của nhóm Ban5. Nhắn câu hỏi, mình sẽ chọn công cụ và chạy thật.\n\n"
    "/new  bắt đầu cuộc trò chuyện mới\n"
    "/help xem lại hướng dẫn này\n\n"
    "Ví dụ:\n"
    "• Tin tức AI hôm nay có gì nổi bật?\n"
    "• Tóm tắt 5 tweet mới nhất giúp mình\n"
    "• Đăng lên Telegram: Test từ nhóm Ban5"
)


def parse_allowed(value: str | None) -> set[int]:
    allowed: set[int] = set()
    for part in (value or "").split(","):
        part = part.strip()
        if part.lstrip("-").isdigit():
            allowed.add(int(part))
    return allowed


def split_message(text: str, limit: int = MAX_MESSAGE_LEN) -> list[str]:
    """Split on paragraph/line/space boundaries so long answers fit Telegram's limit."""
    text = text.strip() or "(trống)"
    chunks: list[str] = []
    while len(text) > limit:
        cut = max(text.rfind("\n\n", 0, limit), text.rfind("\n", 0, limit), text.rfind(" ", 0, limit))
        if cut < limit // 2:
            cut = limit
        chunks.append(text[:cut].rstrip())
        text = text[cut:].lstrip()
    chunks.append(text)
    return chunks


class TelegramBot:
    def __init__(self, token: str, allowed: set[int]) -> None:
        self.token = token
        self.allowed = allowed
        self.sessions: dict[int, dict[str, Any]] = {}
        self.pending_options: dict[int, list[str]] = {}

    # ------------------------------------------------------------ Telegram API
    def call(self, method: str, **payload: Any) -> dict[str, Any]:
        response = requests.post(
            API_URL.format(token=self.token, method=method),
            json=payload,
            timeout=POLL_TIMEOUT + 10,
        )
        try:
            data = response.json()
        except ValueError:
            data = {"ok": False, "description": f"HTTP {response.status_code}"}
        if not data.get("ok"):
            raise RuntimeError(f"{method} failed: {data.get('description')}")
        return data

    def reply(self, chat_id: int, text: str, keyboard: list[list[dict[str, str]]] | None = None) -> None:
        print(f"[gửi]  chat={chat_id} {text[:70]!r}")
        chunks = split_message(text)
        for index, chunk in enumerate(chunks):
            payload: dict[str, Any] = {"chat_id": chat_id, "text": chunk, "disable_web_page_preview": True}
            if keyboard and index == len(chunks) - 1:
                payload["reply_markup"] = {"inline_keyboard": keyboard}
            self.call("sendMessage", **payload)

    def typing(self, chat_id: int) -> None:
        try:
            self.call("sendChatAction", chat_id=chat_id, action="typing")
        except RuntimeError:
            pass  # cosmetic only

    # ------------------------------------------------------------ agent turn
    def run_turn(self, chat_id: int, text: str) -> None:
        session = self.sessions.get(chat_id)
        if session is None:
            session = self.sessions[chat_id] = server.new_session(source="telegram")
        self.pending_options.pop(chat_id, None)

        used_tools: list[str] = []
        final: dict[str, Any] | None = None
        for event in server.turn_events(session, text):
            kind = event.get("type")
            if kind == "thinking":
                self.typing(chat_id)
            elif kind == "tool_call":
                used_tools.append(event["name"])
            elif kind in ("final", "error"):
                final = event

        if final is None:
            self.reply(chat_id, "Agent không trả lời. Thử lại nhé.")
            return
        if final["type"] == "error":
            self.reply(chat_id, f"Agent gặp lỗi: {final['message']}")
            return

        answer = final["text"] or "(agent không có nội dung trả lời)"
        if used_tools:
            answer += "\n\nCông cụ đã dùng: " + ", ".join(dict.fromkeys(used_tools))

        keyboard = None
        ask = final.get("ask")
        if ask and ask["response_type"] == "yes_no":
            keyboard = [[
                {"text": "Đồng ý", "callback_data": "yn:yes"},
                {"text": "Không, hủy", "callback_data": "yn:no"},
            ]]
        elif ask and ask["response_type"] == "choice" and ask["options"]:
            self.pending_options[chat_id] = ask["options"]
            keyboard = [[{"text": option[:60], "callback_data": f"opt:{i}"}] for i, option in enumerate(ask["options"])]
        self.reply(chat_id, answer, keyboard)

    # ------------------------------------------------------------ updates
    def handle_message(self, message: dict[str, Any]) -> None:
        chat = message.get("chat", {})
        chat_id = chat.get("id")
        text = (message.get("text") or "").strip()
        if chat.get("type") != "private" or chat_id is None or not text:
            return  # ignore channel posts, groups and non-text messages

        command = text.split()[0].split("@")[0].lower() if text.startswith("/") else ""
        if command == "/start":
            if chat_id in self.allowed:
                self.reply(chat_id, HELP_TEXT)
            else:
                self.reply(
                    chat_id,
                    f"Chat id của bạn là {chat_id}.\n"
                    "Nhờ người quản trị thêm số này vào TELEGRAM_ALLOWED_CHAT_IDS trong .env rồi khởi động lại bot.",
                )
            return
        if chat_id not in self.allowed:
            self.reply(chat_id, "Bạn chưa được cấp quyền dùng bot này. Gửi /start để lấy chat id.")
            return
        if command == "/help":
            self.reply(chat_id, HELP_TEXT)
        elif command == "/new":
            self.sessions.pop(chat_id, None)
            self.reply(chat_id, "Đã bắt đầu cuộc trò chuyện mới.")
        else:
            self.run_turn(chat_id, text)

    def handle_callback(self, callback: dict[str, Any]) -> None:
        chat_id = callback.get("message", {}).get("chat", {}).get("id")
        message_id = callback.get("message", {}).get("message_id")
        data = callback.get("data", "")
        try:
            self.call("answerCallbackQuery", callback_query_id=callback["id"])
        except RuntimeError:
            pass
        if chat_id not in self.allowed:
            return

        answer: str | None = None
        if data == "yn:yes":
            answer = "Có, đồng ý."
        elif data == "yn:no":
            answer = "Không, hủy."
        elif data.startswith("opt:") and data[4:].isdigit():
            options = self.pending_options.get(chat_id, [])
            index = int(data[4:])
            answer = options[index] if index < len(options) else None
        if answer is None:
            return
        try:  # remove the buttons so a confirmation cannot be pressed twice
            self.call("editMessageReplyMarkup", chat_id=chat_id, message_id=message_id,
                      reply_markup={"inline_keyboard": []})
        except RuntimeError:
            pass
        self.reply(chat_id, f"➜ {answer}")
        self.run_turn(chat_id, answer)

    def process(self, update: dict[str, Any]) -> None:
        incoming = update.get("message") or update.get("callback_query", {}).get("message") or {}
        who = incoming.get("chat", {})
        print(f"[nhận] chat={who.get('id')} loại={who.get('type')} "
              f"{(update.get('message') or {}).get('text') or update.get('callback_query', {}).get('data')!r}")
        try:
            if "message" in update:
                self.handle_message(update["message"])
            elif "callback_query" in update:
                self.handle_callback(update["callback_query"])
        except Exception as exc:  # keep the bot alive; show the user something useful
            print(f"[error] {redact(f'{type(exc).__name__}: {exc}')}")
            chat_id = (update.get("message") or update.get("callback_query", {}).get("message") or {}).get("chat", {}).get("id")
            if chat_id in self.allowed:
                try:
                    self.reply(chat_id, f"Có lỗi khi xử lý: {redact(str(exc))[:300]}")
                except Exception:
                    pass

    def run(self) -> None:
        me = self.call("getMe")["result"]
        # A leftover webhook blocks getUpdates; this bot polls instead.
        self.call("deleteWebhook", drop_pending_updates=False)
        print(f"Bot @{me['username']} đang chạy. Chat được phép: {sorted(self.allowed) or 'chưa có (chỉ /start hoạt động)'}")
        offset = 0
        while True:
            try:
                updates = self.call(
                    "getUpdates",
                    offset=offset,
                    timeout=POLL_TIMEOUT,
                    allowed_updates=["message", "callback_query"],
                )["result"]
            except (requests.RequestException, RuntimeError) as exc:
                text = redact(str(exc))
                if "Conflict" in text:
                    print("[warn] Có chương trình khác đang đọc tin của bot này (getUpdates). Chỉ chạy một bản.")
                else:
                    print(f"[warn] {text}")
                time.sleep(5)
                continue
            for update in updates:
                offset = update["update_id"] + 1
                self.process(update)


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat with the research agent from Telegram.")
    parser.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini", "ollama"], required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--version", default="telegram", help="Artifact version label stored in transcripts, e.g. v3.")
    parser.add_argument("--system-prompt", type=Path, default=settings.system_prompt_path)
    parser.add_argument("--tools", type=Path, default=settings.tools_path)
    parser.add_argument("--transcripts-dir", type=Path, default=settings.transcripts_dir)
    args = parser.parse_args()

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Thiếu TELEGRAM_BOT_TOKEN trong starter_v0/.env")

    settings.provider_name = args.provider
    settings.model = args.model
    settings.version = args.version
    settings.system_prompt_path = args.system_prompt
    settings.tools_path = args.tools
    settings.transcripts_dir = args.transcripts_dir
    TelegramBot(token, parse_allowed(os.getenv("TELEGRAM_ALLOWED_CHAT_IDS"))).run()


if __name__ == "__main__":
    main()
