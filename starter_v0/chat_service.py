
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from chat import (
    now_iso,
    safe_slug,
    trim_history,
    run_model_tool_loop,
    write_transcript,
)

from providers import make_provider

from tools import (
    load_tool_declarations,
    to_openai_tools,
)

from versioning import (
    artifact_version_dict,
    build_artifact_version,
)


# Project paths
ROOT = Path(__file__).resolve().parent
ARTIFACTS_DIR = ROOT / "artifacts"


class ChatSession:

    def __init__(
        self,
        provider_name: str = "openrouter",
        version: str = "v0",
        model: str | None = None,
        history_window: int = 5,
        max_tool_rounds: int = 4,
    ):
        self.provider_name = provider_name
        self.version = version
        self.model = model
        self.history_window = history_window
        self.max_tool_rounds = max_tool_rounds

        # Load system prompt
        self.system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
        self.tools_path = ARTIFACTS_DIR / "tools.yaml"

        self.system_prompt = self.system_prompt_path.read_text(
            encoding="utf-8"
        )

        # Load tool declarations
        tool_declarations = load_tool_declarations(self.tools_path)
        self.openai_tools = to_openai_tools(tool_declarations)

        # Initialize provider
        self.provider = make_provider(provider_name)

        self.selected_model = (
            model or getattr(self.provider, "default_model", None)
        )

        # Build artifact version
        self.artifact_version = build_artifact_version(
            version,
            self.system_prompt_path,
            self.tools_path,
        )

        # Conversation history
        self.history: list[dict[str, str]] = []

        # Create transcript
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")

        self.transcript_id = "_".join([
            safe_slug(version),
            safe_slug(provider_name),
            timestamp,
            uuid.uuid4().hex[:8],
        ])

        self.transcript_path = (
            ROOT / "transcripts" /
            f"{self.transcript_id}.transcript.json"
        )

        self.turn_index = 0

        self.transcript: dict[str, Any] = {
            "transcript_id": self.transcript_id,
            **artifact_version_dict(self.artifact_version),
            "provider": provider_name,
            "model": self.selected_model,
            "system_prompt": str(self.system_prompt_path),
            "tools": str(self.tools_path),
            "history_window": history_window,
            "max_tool_rounds": max_tool_rounds,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": [],
        }

        write_transcript(self.transcript_path, self.transcript)

    def send_message(self, user_text: str) -> dict[str, Any]:

        user_text = user_text.strip()

        if not user_text:
            raise ValueError("Message cannot be empty.")

        self.turn_index += 1

        messages = [
            {"role": "system", "content": self.system_prompt},
            *trim_history(self.history, self.history_window),
            {"role": "user", "content": user_text},
        ]

        turn_record: dict[str, Any] = {
            "turn_index": self.turn_index,
            "started_at": now_iso(),
            "user": user_text,
            "status": "started",
            "assistant_text": None,
            "rounds": [],
            "tool_events": [],
        }

        try:
            result = run_model_tool_loop(
                provider=self.provider,
                messages=messages,
                tools=self.openai_tools,
                model=self.model,
                max_tool_rounds=self.max_tool_rounds,
            )

            turn_record.update(result)

            assistant_text = result.get("assistant_text") or ""

            self.history.append({
                "role": "user",
                "content": user_text,
            })

            self.history.append({
                "role": "assistant",
                "content": assistant_text,
            })

        except Exception as exc:
            turn_record.update({
                "status": "provider_error",
                "error": f"{type(exc).__name__}: {str(exc)}",
            })

        turn_record["ended_at"] = now_iso()

        self.transcript["turns"].append(turn_record)

        write_transcript(
            self.transcript_path,
            self.transcript,
        )

        return turn_record
