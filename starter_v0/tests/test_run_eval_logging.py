from __future__ import annotations

import json

from run_eval import write_run_log


def test_run_log_keeps_completed_results_at_each_checkpoint(tmp_path) -> None:
    path = tmp_path / "run.json"
    payload = {
        "status": "running",
        "completed_cases": 1,
        "results": [{"id": "case-1"}],
    }

    write_run_log(path, payload)

    payload["completed_cases"] = 2
    payload["results"].append({"id": "case-2"})
    write_run_log(path, payload)

    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["status"] == "running"
    assert saved["completed_cases"] == 2
    assert [item["id"] for item in saved["results"]] == ["case-1", "case-2"]
    assert not path.with_suffix(".json.tmp").exists()
