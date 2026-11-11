"""Checks for data/eval_security.json (v5 security suite).

Kept out of test_tool_contract.py, which is the provided contract test.
"""
from __future__ import annotations

import json
from pathlib import Path

from tools import load_tool_declarations

ROOT = Path(__file__).resolve().parents[1]
DECLARED = {item["name"] for item in load_tool_declarations(ROOT / "artifacts" / "tools.yaml")}
SECURITY_EVAL = ROOT / "data" / "eval_security.json"
ALLOWED_FAILURE_TYPES = {"wrong_tool", "wrong_arg_value", "wrong_boundary", "unnecessary_tool", "out_of_scope", "missing_info"}


def _cases() -> list[dict]:
    return json.loads(SECURITY_EVAL.read_text(encoding="utf-8"))["cases"]


def test_security_eval_only_expects_declared_tools() -> None:
    for case in _cases():
        for call in case.get("expect", {}).get("tool_calls", []):
            assert call["name"] in DECLARED, f"{case['id']} expects undeclared tool '{call['name']}'"


def test_security_eval_cases_are_well_formed() -> None:
    cases = _cases()
    assert cases, "eval_security.json has no cases"
    for case in cases:
        assert case["phase"] == "B"
        assert ("query" in case) != ("turns" in case), case["id"]
        assert case["failure_type"] in ALLOWED_FAILURE_TYPES, case["id"]
        expect = case["expect"]
        assert expect.get("no_tool") or expect.get("tool_calls"), case["id"]


def test_security_eval_never_expects_send_without_confirmation() -> None:
    for case in _cases():
        for call in case.get("expect", {}).get("tool_calls", []):
            if call["name"] == "send":
                assert call.get("args", {}).get("confirmed") is True, case["id"]
