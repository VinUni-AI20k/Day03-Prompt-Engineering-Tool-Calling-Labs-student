"""Count small-model failure patterns in run JSON files (README Step 7, group report B7).

Usage: python scripts/local_failure_patterns.py runs/v3-qwen7b_*.json runs/v3-llama3b_*.json ...
A case can hit several patterns; counts are per case.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

PATTERNS = [
    "hallucinated_tool",       # tool name not declared in tools.yaml
    "wrong_tool",              # declared tool, but not the expected one
    "invalid_json_args",       # provider kept raw text in args._invalid_json_arguments
    "bad_arg_type_or_enum",    # value outside the schema enum, or a string where an integer is declared
    "no_tool_call",            # answered in text when a tool call was expected
    "missed_clarify",          # expected clarify, did something else
    "tool_on_no_tool_case",    # called a tool on an out-of-scope / no-tool case
    "repeated_or_extra_call",  # same tool twice, or more calls than expected
]


def schema_of(tools_path: Path) -> dict[str, dict]:
    tools = yaml.safe_load(tools_path.read_text(encoding="utf-8"))["tools"]
    return {t["name"]: t.get("parameters", {}).get("properties", {}) for t in tools}


def bad_args(args: dict, props: dict) -> bool:
    for key, value in args.items():
        spec = props.get(key)
        if spec is None:
            return True  # unknown argument name
        if "enum" in spec and value not in spec["enum"]:
            return True
        if spec.get("type") == "integer" and not isinstance(value, int):
            return True
    return False


def classify(result: dict, tools_schema: dict) -> set[str]:
    hits: set[str] = set()
    res = result["result"]
    if res["passed"]:
        return hits
    calls = res.get("actual_tool_calls") or []
    expect = result["expect"]
    expected = [c["name"] for c in expect.get("tool_calls", [])]
    names = [c["name"] for c in calls]
    if expect.get("no_tool"):
        if calls:
            hits.add("tool_on_no_tool_case")
    elif not calls:
        hits.add("no_tool_call")
    if "clarify" in expected and "clarify" not in names:
        hits.add("missed_clarify")
    for call in calls:
        if call["name"] not in tools_schema:
            hits.add("hallucinated_tool")
            continue
        if expected and call["name"] not in expected:
            hits.add("wrong_tool")
        if "_invalid_json_arguments" in call["args"]:
            hits.add("invalid_json_args")
        elif bad_args(call["args"], tools_schema[call["name"]]):
            hits.add("bad_arg_type_or_enum")
    if len(names) != len(set(names)) or (expected and len(calls) > len(expected)):
        hits.add("repeated_or_extra_call")
    return hits


def main(paths: list[str]) -> None:
    print("run,version,model,case_accuracy," + ",".join(PATTERNS))
    for path in paths:
        run = json.loads(Path(path).read_text(encoding="utf-8"))
        tools_path = Path(run["tools"])
        if not tools_path.is_absolute():
            tools_path = ROOT / tools_path
        if not tools_path.exists():  # run recorded on another machine
            tools_path = ROOT / "artifacts" / tools_path.name
        schema = schema_of(tools_path)
        counts = {p: 0 for p in PATTERNS}
        examples: dict[str, str] = {}
        for result in run["results"]:
            for hit in classify(result, schema):
                counts[hit] += 1
                examples.setdefault(hit, result["id"])
        print(f"{Path(path).name},{run['version']},{run['model']},{run['summary']['case_accuracy']},"
              + ",".join(str(counts[p]) for p in PATTERNS))
        print("  examples: " + "; ".join(f"{k}={v}" for k, v in examples.items()), file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
