"""Build markdown tables for report/team/group_report.md (Part B) from real logs.

Usage (from starter_v0/):
    python scripts/report_tables.py                 # print B1 + B2 + B3 + B4
    python scripts/report_tables.py --only B1 B3     # print selected tables

Sources:
    B1 <- artifacts/version_log.csv (+ summary of each run_file)
    B2 <- latest valid base run of the chosen version (default: v0)
    B3 <- data/eval_group.json + latest valid group run
    B4 <- transcripts/*.transcript.json

Only runs with provider_error_cases == 0 and measured_cases == total_cases are
treated as valid evidence; invalid runs are flagged, never silently used.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def cell(value: Any, limit: int = 120) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    text = " ".join(str(text).split()).replace("|", "\\|")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_valid(run: dict[str, Any]) -> bool:
    s = run.get("summary", {})
    return s.get("provider_error_cases") == 0 and s.get("measured_cases") == s.get("total_cases")


def latest_run(suite: str, version: str | None = None) -> tuple[Path, dict[str, Any]] | None:
    candidates = []
    for path in sorted((ROOT / "runs").glob("*.json")):
        try:
            run = load_json(path)
        except (json.JSONDecodeError, OSError):
            continue
        if run.get("suite") != suite or (version and run.get("version") != version):
            continue
        if is_valid(run):
            candidates.append((run.get("generated_at", ""), path, run))
    if not candidates:
        return None
    _, path, run = max(candidates, key=lambda item: item[0])
    return path, run


def metric_line(run: dict[str, Any]) -> str:
    s = run["summary"]
    return (f"case {s.get('case_accuracy')} · routing {s.get('tool_routing_accuracy')} · "
            f"args {s.get('argument_accuracy')} · multi {s.get('multiturn_accuracy')}")


def table_b1() -> str:
    log = ROOT / "artifacts" / "version_log.csv"
    rows = list(csv.DictReader(log.open(encoding="utf-8"))) if log.exists() else []
    out = ["| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |",
           "|---|---|---|---:|---:|---|"]
    notes = []
    for row in rows:
        run_file = (row.get("run_file") or "").strip()
        out.append(f"| {cell(row.get('version'))} | {cell(row.get('changed_artifact'))} | "
                   f"{cell(row.get('hypothesis'), 200)} | {cell(row.get('metric_before'))} | "
                   f"{cell(row.get('metric_after'))} | `starter_v0/{run_file}` |")
        path = ROOT / run_file
        if run_file and path.exists():
            run = load_json(path)
            flag = "" if is_valid(run) else " ⚠️ RUN KHÔNG HỢP LỆ (provider error / thiếu case)"
            notes.append(f"- {row.get('version')}: {metric_line(run)}{flag}")
        elif run_file:
            notes.append(f"- {row.get('version')}: ⚠️ không tìm thấy `{run_file}`")
    if not rows:
        out.append("| _(version_log.csv chưa có dòng nào)_ | | | | | |")
    return "### B1. Version Evidence\n\n" + "\n".join(out) + ("\n\nChi tiết metric từ run JSON:\n" + "\n".join(notes) if notes else "")


def table_b2(version: str) -> str:
    found = latest_run("base", version)
    header = f"### B2. Failure Analysis ({version})\n\n"
    if not found:
        return header + f"_(chưa có run base hợp lệ cho {version})_"
    path, run = found
    out = ["| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |", "|---|---|---|---|---|"]
    for item in run["results"]:
        res = item["result"]
        if res.get("passed"):
            continue
        calls = [f"{c['name']}({json.dumps(c.get('args', {}), ensure_ascii=False)})" for c in res.get("actual_tool_calls", [])]
        out.append(f"| {item['id']} | {res.get('case_failure_type')} / {res.get('observed_mismatch')} | "
                   f"{cell('; '.join(calls) or '(no tool)', 160)} | {cell('; '.join(res.get('failures', [])), 160)} | _TODO_ |")
    return header + f"Run: `starter_v0/{path.relative_to(ROOT).as_posix()}` — {metric_line(run)}\n\n" + "\n".join(out)


def table_b3() -> str:
    cases = load_json(ROOT / "data" / "eval_group.json")["cases"]
    found = latest_run("group")
    results = {item["id"]: item["result"] for item in found[1]["results"]} if found else {}
    out = ["| Case ID | Type | What It Tests | Expected Tool/Behavior | Result |", "|---|---|---|---|---|"]
    for case in cases:
        expect = case["expect"]
        if expect.get("no_tool"):
            expected = f"no tool ({expect.get('behavior', '')})"
        else:
            expected = "; ".join(f"{c['name']}({json.dumps(c.get('args', {}), ensure_ascii=False)})" for c in expect["tool_calls"])
        kind = "multi" if "turns" in case else "single"
        res = results.get(case["id"])
        if res is None:
            outcome = "_chưa chạy_"
        elif res.get("passed"):
            outcome = "PASS"
        else:
            outcome = "FAIL: " + cell("; ".join(res.get("failures", [])), 100)
        out.append(f"| {case['id']} | {kind} | {cell(case.get('metadata', {}).get('what_it_tests', ''), 160)} | "
                   f"`{cell(expected, 100)}` | {outcome} |")
    source = (f"Run: `starter_v0/{found[0].relative_to(ROOT).as_posix()}` — {metric_line(found[1])}\n\n"
              if found else "_(chưa có run group hợp lệ)_\n\n")
    return "### B3. Team Eval Cases\n\n" + source + "\n".join(out)


def table_b4() -> str:
    out = ["| Turn | User Request | Tool Calls | Version Evidence | Outcome |", "|---|---|---|---|---|"]
    paths = sorted((ROOT / "transcripts").glob("*.transcript.json"))
    for path in paths:
        tr = load_json(path)
        rel = f"`starter_v0/{path.relative_to(ROOT).as_posix()}`"
        for turn in tr.get("turns", []):
            calls = [f"{c['name']}({json.dumps(c.get('args', {}), ensure_ascii=False)})"
                     for r in turn.get("rounds", []) for c in r.get("tool_calls", [])]
            out.append(f"| {turn.get('turn_index')} | {cell(turn.get('user'), 80)} | {cell('; '.join(calls) or '(no tool)', 140)} | "
                       f"{tr.get('artifact_version')} · {rel} | {turn.get('status')}: {cell(turn.get('assistant_text') or turn.get('error') or '', 100)} |")
    if not paths:
        out.append("| | _(chưa có transcript)_ | | | |")
    return "### B4. Live Chat Evidence\n\n" + "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", nargs="*", choices=["B1", "B2", "B3", "B4"], default=["B1", "B2", "B3", "B4"])
    parser.add_argument("--b2-version", default="v0", help="Version used for the failure-analysis table (default v0).")
    args = parser.parse_args()
    builders = {"B1": table_b1, "B2": lambda: table_b2(args.b2_version), "B3": table_b3, "B4": table_b4}
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n\n".join(builders[key]() for key in args.only))


if __name__ == "__main__":
    main()
