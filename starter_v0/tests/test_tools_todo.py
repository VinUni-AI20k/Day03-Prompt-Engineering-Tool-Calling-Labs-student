"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO CP3 (student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    pytest.skip(TODO)


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    pytest.skip(TODO)


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    pytest.skip(TODO)


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    pytest.skip(TODO)


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    pytest.skip(TODO)


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    pytest.skip(TODO)


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    # timeframe=None -> request body has no "time_range" key.
    pytest.skip(TODO)


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    pytest.skip(TODO)


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    pytest.skip(TODO)


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    pytest.skip(TODO)


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    pytest.skip(TODO)


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    pytest.skip(TODO)


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    pytest.skip(TODO)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    pytest.skip(TODO)


# ---------------- save_note (YOUR NEW TOOL) ----------------
# Follows rubric C4 & project rules:
# 1. happy path (confirmed write)
# 2. guardrail (confirmed=False or string "false" does not write to disk)
# 3. bad input / path traversal safety (empty filename, empty content, traversal blocked)
# 4. error branch (filesystem error returns error dict instead of raising)

save_note_tool = TOOL_FUNCTIONS["save_note"]


def test_save_note_without_confirmation_does_not_write(tmp_path) -> None:
    result = save_note_tool(filename="research_ai.md", content="# AI Summary", confirmed=False, base_dir=tmp_path)

    assert result["status"] == "needs_confirmation"
    assert result["preview"]["filename"] == "research_ai.md"
    assert not (tmp_path / "notes" / "research_ai.md").exists()


def test_save_note_string_false_confirmation_does_not_write(tmp_path) -> None:
    # Small models like Ollama may send string "false" instead of boolean False.
    result = save_note_tool(filename="research_ai.md", content="# AI Summary", confirmed="false", base_dir=tmp_path)

    assert result["status"] == "needs_confirmation"
    assert not (tmp_path / "notes" / "research_ai.md").exists()


def test_save_note_happy_path(tmp_path) -> None:
    result = save_note_tool(filename="research_ai", content="# AI Summary\nKey findings.", confirmed=True, base_dir=tmp_path)

    assert result["status"] == "saved"
    assert result["filename"] == "research_ai.md"
    assert result["overwritten"] is False
    target_file = tmp_path / "notes" / "research_ai.md"
    assert target_file.is_file()
    assert target_file.read_text(encoding="utf-8") == "# AI Summary\nKey findings."


def test_save_note_existing_file_requires_overwrite_confirmation(tmp_path) -> None:
    target_file = tmp_path / "notes" / "research_ai.md"
    target_file.parent.mkdir()
    target_file.write_text("original", encoding="utf-8")

    result = save_note_tool(
        filename="research_ai.md",
        content="replacement",
        confirmed=True,
        base_dir=tmp_path,
    )

    assert result["status"] == "needs_overwrite_confirmation"
    assert result["preview"]["will_overwrite"] is True
    assert target_file.read_text(encoding="utf-8") == "original"


def test_save_note_overwrites_only_after_explicit_confirmation(tmp_path) -> None:
    target_file = tmp_path / "notes" / "research_ai.md"
    target_file.parent.mkdir()
    target_file.write_text("original", encoding="utf-8")

    result = save_note_tool(
        filename="research_ai.md",
        content="replacement",
        confirmed=True,
        overwrite_confirmed=True,
        base_dir=tmp_path,
    )

    assert result["status"] == "saved"
    assert result["overwritten"] is True
    assert target_file.read_text(encoding="utf-8") == "replacement"


def test_save_note_empty_filename_returns_error(tmp_path) -> None:
    result = save_note_tool(filename="", content="test", confirmed=True, base_dir=tmp_path)
    assert result.get("error") == "invalid_filename"


def test_save_note_empty_content_returns_error(tmp_path) -> None:
    result = save_note_tool(filename="test.md", content="", confirmed=True, base_dir=tmp_path)
    assert result.get("error") == "empty_content"


def test_save_note_path_traversal_blocked(tmp_path) -> None:
    result = save_note_tool(filename="../../passwords.txt", content="secret", confirmed=True, base_dir=tmp_path)
    assert result.get("error") == "invalid_filename"
    assert not (tmp_path / "passwords.txt").exists()


def test_save_note_filename_with_dots_allowed(tmp_path) -> None:
    result = save_note_tool(filename="v1..v2.md", content="comparison", confirmed=True, base_dir=tmp_path)
    assert result.get("status") == "saved"
    assert (tmp_path / "notes" / "v1..v2.md").is_file()


def test_save_note_write_error_returns_error_dict(tmp_path) -> None:
    (tmp_path / "notes").write_text("not a dir", encoding="utf-8")
    result = save_note_tool(filename="a.md", content="x", confirmed=True, base_dir=tmp_path)
    assert result.get("error") == "FileExistsError"
