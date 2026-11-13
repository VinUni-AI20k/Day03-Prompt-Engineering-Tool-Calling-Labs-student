"""Frozen versions (artifacts/versions/vN) must stay identical to what the evidence runs used."""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import pytest

import server

ARTIFACTS = Path(__file__).resolve().parent.parent / "artifacts"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v0_to_v3_are_frozen() -> None:
    assert server.available_versions()[:4] == ["v0", "v1", "v2", "v3"]


@pytest.mark.parametrize("version", ["v0", "v1", "v2", "v3"])
def test_frozen_version_hashes_match_version_log(version: str) -> None:
    rows = {r["version"]: r for r in csv.DictReader((ARTIFACTS / "version_log.csv").open(encoding="utf-8"))}
    base = ARTIFACTS / "versions" / version
    assert sha(base / "system_prompt.md") == rows[version]["prompt_hash"]
    assert sha(base / "tools.yaml") == rows[version]["tools_hash"]


@pytest.mark.parametrize("bad", ["v99", "../artifacts", "v1/../v0", "latest", ""])
def test_unknown_or_unsafe_version_is_rejected(bad: str) -> None:
    with pytest.raises(ValueError):
        server.version_paths(bad)


def test_none_means_live_files() -> None:
    label, prompt, tools = server.version_paths(None)
    assert prompt == server.settings.system_prompt_path and tools == server.settings.tools_path


def test_session_uses_the_chosen_versions_prompt_and_tools(monkeypatch) -> None:
    class FakeProvider:
        default_model = "fake-model"

    monkeypatch.setattr(server, "get_provider", lambda: FakeProvider())
    old = server.new_session(version="v0")
    new = server.new_session(version="v3")
    assert old["system_prompt"] != new["system_prompt"] or old["tools"] != new["tools"]
    assert old["system_prompt"] == (ARTIFACTS / "versions" / "v0" / "system_prompt.md").read_text(encoding="utf-8")
    tool_names = lambda s: {t["function"]["name"] for t in s["tools"]}  # noqa: E731
    assert "stats" not in tool_names(old) and "stats" in tool_names(new)
    assert old["transcript"]["version"] == "v0" and new["transcript"]["version"] == "v3"
    assert old["transcript"]["artifact_version"].startswith("v0+")
