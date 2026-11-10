"""Streamlit UI cho Research Agent.

Chạy từ starter_v0/:
    streamlit run app.py

Tab "Chat" tái dùng vòng lặp model -> tool trong chat.py và ghi transcript cùng format
(transcripts/*.transcript.json). Tab "Eval runs" đọc runs/*.json do run_eval.py sinh ra
và hiển thị summary + từng case (PASS/FAIL, expected vs actual tool calls).
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

RUNS_DIR = ROOT / "runs"
TRANSCRIPTS_DIR = ROOT / "transcripts"
VERSION_LOG = ARTIFACTS_DIR / "version_log.csv"
PROVIDERS = ["openrouter", "openai", "anthropic", "gemini", "ollama"]

STATUS_LABEL = {
    "answered": "✅ Đã trả lời",
    "waiting_for_user": "❓ Agent đang hỏi lại, chờ bạn bổ sung",
    "max_tool_rounds": "⚠️ Dừng vì vượt số vòng tool tối đa",
    "provider_error": "❌ Lỗi provider",
}

st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="wide")


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_provider(name: str):
    return make_provider(name)


def pretty(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def tool_calls_str(calls: list[dict[str, Any]] | None) -> str:
    if not calls:
        return "—"
    return "\n".join(
        f"{c.get('name')}({json.dumps(c.get('args', {}), ensure_ascii=False, sort_keys=True)})"
        for c in calls
    )


def render_tool_events(events: list[dict[str, Any]]) -> None:
    """Hiện mọi tool call và kết quả thật, kể cả error dict. Không che lỗi tool."""
    if not events:
        return
    for event in events:
        result = event.get("result")
        is_error = isinstance(result, dict) and "error" in result
        icon = "🔴" if is_error else "🔧"
        args_text = json.dumps(event.get("args", {}), ensure_ascii=False, sort_keys=True)
        with st.expander(f"{icon} {event.get('tool')}({args_text})", expanded=is_error):
            if is_error:
                st.error(f"{result.get('error')}: {result.get('message', '')}")
            st.code(pretty(result), language="json")


def new_session(version: str, provider_name: str, model: str | None, history_window: int, max_tool_rounds: int) -> None:
    prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    artifact_version = build_artifact_version(version, prompt_path, tools_path)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), "ui", timestamp])
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(prompt_path),
        "tools": str(tools_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "ui": "streamlit",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    st.session_state.history = []          # list[{"role","content"}] gửi lại cho model
    st.session_state.display = []          # list[dict] để render lại khung chat
    st.session_state.turn_index = 0


def run_turn(user_text: str, provider_name: str, model: str | None, history_window: int, max_tool_rounds: int) -> dict[str, Any]:
    system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
    openai_tools = to_openai_tools(load_tool_declarations(ARTIFACTS_DIR / "tools.yaml"))

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, history_window),
        {"role": "user", "content": user_text},
    ]
    st.session_state.turn_index += 1
    turn_record: dict[str, Any] = {
        "turn_index": st.session_state.turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    try:
        provider = get_provider(provider_name)
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=openai_tools,
            model=model,
            max_tool_rounds=max_tool_rounds,
        )
        turn_record.update(result)
        st.session_state.history.append({"role": "user", "content": user_text})
        st.session_state.history.append({"role": "assistant", "content": result["assistant_text"]})
    except Exception as exc:  # lỗi provider là bằng chứng, ghi vào transcript thay vì sập UI
        turn_record.update({
            "status": "provider_error",
            "error": f"{type(exc).__name__}: {exc}",
            "assistant_text": None,
        })

    turn_record["ended_at"] = now_iso()
    st.session_state.transcript["turns"].append(turn_record)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)
    return turn_record


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    st.title("🔎 Research Agent")
    provider_name = st.selectbox("Provider", PROVIDERS, index=0)
    model_input = st.text_input("Model (bỏ trống = mặc định của provider)", value="")
    model = model_input.strip() or None
    version = st.text_input("Version label", value="v0", help="Nhãn ghi vào transcript, ví dụ v0, v1, v3.")
    history_window = st.number_input("History window (cặp lượt)", min_value=0, max_value=20, value=5)
    max_tool_rounds = st.number_input("Max tool rounds", min_value=1, max_value=10, value=4)

    if st.button("🆕 Phiên chat mới", width="stretch") or "transcript" not in st.session_state:
        new_session(version, provider_name, model, int(history_window), int(max_tool_rounds))

    st.divider()
    t = st.session_state.transcript
    st.caption("Artifact version")
    st.code(t["artifact_version"], language=None)
    st.caption("Transcript")
    st.code(str(Path(st.session_state.transcript_path).relative_to(ROOT)), language=None)
    if t["version"] != version or t["provider"] != provider_name or t["model"] != model:
        st.warning("Bạn đã đổi version/provider/model. Bấm **Phiên chat mới** để áp dụng.")


tab_chat, tab_runs = st.tabs(["💬 Chat", "📊 Eval runs"])


# ----------------------------------------------------------------------------
# Tab 1: Chat
# ----------------------------------------------------------------------------
with tab_chat:
    st.markdown(
        "Agent chọn tool thật (search web, đọc URL, xem tweet, …) và gọi API thật. "
        "Mọi tool call và kết quả, kể cả lỗi, đều hiện bên dưới câu trả lời."
    )

    for item in st.session_state.display:
        with st.chat_message("user"):
            st.markdown(item["user"])
        with st.chat_message("assistant"):
            st.caption(STATUS_LABEL.get(item["status"], item["status"]))
            render_tool_events(item.get("tool_events", []))
            if item["status"] == "provider_error":
                st.error(item.get("error", "provider_error"))
            elif item.get("assistant_text"):
                st.markdown(item["assistant_text"])

    user_text = st.chat_input("Nhập yêu cầu research…")
    if user_text and user_text.strip():
        user_text = user_text.strip()
        with st.chat_message("user"):
            st.markdown(user_text)
        with st.chat_message("assistant"):
            with st.spinner("Agent đang chọn tool và gọi API…"):
                record = run_turn(user_text, provider_name, model, int(history_window), int(max_tool_rounds))
            st.caption(STATUS_LABEL.get(record["status"], record["status"]))
            render_tool_events(record.get("tool_events", []))
            if record["status"] == "provider_error":
                st.error(record.get("error", "provider_error"))
            elif record.get("assistant_text"):
                st.markdown(record["assistant_text"])
        st.session_state.display.append(record)
        st.toast(f"Đã lưu transcript: {Path(st.session_state.transcript_path).name}")


# ----------------------------------------------------------------------------
# Tab 2: Eval runs
# ----------------------------------------------------------------------------
def load_runs() -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    if not RUNS_DIR.exists():
        return runs
    for path in sorted(RUNS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            st.warning(f"Không đọc được {path.name}: {exc}")
            continue
        data["_path"] = path
        runs.append(data)
    return runs


def is_valid_run(summary: dict[str, Any]) -> bool:
    return summary.get("provider_error_cases", 1) == 0 and summary.get("measured_cases") == summary.get("total_cases")


def pct(value: Any) -> str:
    return "—" if value is None else f"{value * 100:.0f}%"


def case_input_text(case: dict[str, Any]) -> str:
    raw = case.get("input")
    if isinstance(raw, list):
        return " ⟶ ".join(m.get("content", "") for m in raw if isinstance(m, dict))
    return str(raw or "")


with tab_runs:
    runs = load_runs()
    if not runs:
        st.info("Chưa có file nào trong `runs/`. Chạy `python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json` trước.")
    else:
        # --- Bảng so sánh mọi run (phục vụ version_log / B1) ---
        st.subheader("Tất cả run")
        overview = []
        for r in runs:
            s = r.get("summary", {})
            overview.append({
                "run_file": r["_path"].name,
                "version": r.get("version"),
                "suite": r.get("suite"),
                "model": r.get("model"),
                "hợp lệ": "✅" if is_valid_run(s) else "❌",
                "case_acc": s.get("case_accuracy"),
                "routing_acc": s.get("tool_routing_accuracy"),
                "arg_acc": s.get("argument_accuracy"),
                "multiturn_acc": s.get("multiturn_accuracy"),
                "passed/total": f"{s.get('passed_cases')}/{s.get('total_cases')}",
                "generated_at": r.get("generated_at"),
            })
        st.dataframe(overview, width="stretch", hide_index=True)

        # --- Chi tiết một run ---
        st.subheader("Chi tiết run")
        names = [r["_path"].name for r in runs]
        chosen = st.selectbox("Chọn run", names, index=0)
        run = next(r for r in runs if r["_path"].name == chosen)
        summary = run.get("summary", {})

        if is_valid_run(summary):
            st.success("Run hợp lệ: provider_error_cases == 0 và measured_cases == total_cases. Dùng được làm bằng chứng.")
        else:
            st.error("Run KHÔNG hợp lệ (có provider error hoặc thiếu case đo). Không dùng làm bằng chứng, hãy chạy lại.")

        meta_cols = st.columns(4)
        meta_cols[0].markdown(f"**Version**\n\n`{run.get('version')}`")
        meta_cols[1].markdown(f"**Suite / phase**\n\n`{run.get('suite')}` / `{run.get('phase')}`")
        meta_cols[2].markdown(f"**Provider / model**\n\n`{run.get('provider')}` / `{run.get('model')}`")
        meta_cols[3].markdown(f"**Generated at**\n\n`{run.get('generated_at')}`")
        st.markdown(f"**artifact_version:** `{run.get('artifact_version')}`")
        with st.expander("prompt_hash / tools_hash đầy đủ"):
            st.code(f"prompt_hash: {run.get('prompt_hash')}\ntools_hash:  {run.get('tools_hash')}", language=None)

        m = st.columns(5)
        m[0].metric("Case accuracy", pct(summary.get("case_accuracy")))
        m[1].metric("Tool routing", pct(summary.get("tool_routing_accuracy")))
        m[2].metric("Argument", pct(summary.get("argument_accuracy")))
        m[3].metric("Multiturn", pct(summary.get("multiturn_accuracy")))
        m[4].metric("Passed / total", f"{summary.get('passed_cases')} / {summary.get('total_cases')}")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Failure type của case FAIL**")
            fc = summary.get("failure_counts") or {}
            st.dataframe([{"failure_type": k, "count": v} for k, v in fc.items()] or [{"failure_type": "—", "count": 0}],
                         width="stretch", hide_index=True)
        with c2:
            st.markdown("**Observed mismatch**")
            oc = summary.get("observed_mismatch_counts") or {}
            st.dataframe([{"observed_mismatch": k, "count": v} for k, v in oc.items()] or [{"observed_mismatch": "—", "count": 0}],
                         width="stretch", hide_index=True)

        # --- Bảng case ---
        st.subheader("Từng case")
        only_fail = st.checkbox("Chỉ hiện case FAIL", value=True)
        results = run.get("results", [])
        rows = []
        for case in results:
            res = case.get("result", {})
            if only_fail and res.get("passed"):
                continue
            expect = case.get("expect", {})
            expected = "no_tool" if expect.get("no_tool") else tool_calls_str(expect.get("tool_calls"))
            rows.append({
                "PASS": "✅" if res.get("passed") else "❌",
                "id": case.get("id"),
                "multi": "🔁" if case.get("is_multiturn") else "",
                "input": case_input_text(case),
                "expected": expected,
                "actual": tool_calls_str(res.get("actual_tool_calls")),
                "failure_type": res.get("failure_type") or "",
                "observed_mismatch": res.get("observed_mismatch") or "",
                "failures": " | ".join(res.get("failures") or []),
            })
        if rows:
            st.dataframe(rows, width="stretch", hide_index=True)
        else:
            st.success("Không có case FAIL trong run này.")

        # --- Chi tiết một case ---
        case_ids = [c.get("id") for c in results]
        picked = st.selectbox("Xem chi tiết case", case_ids)
        case = next(c for c in results if c.get("id") == picked)
        res = case.get("result", {})
        st.markdown(
            f"{'✅ PASS' if res.get('passed') else '❌ FAIL'} · **{case.get('id')}** · "
            f"{case.get('metadata', {}).get('what_it_tests', '')}"
        )
        d1, d2 = st.columns(2)
        with d1:
            st.markdown("**Input**")
            st.code(pretty(case.get("input")), language="json")
            st.markdown("**Expected**")
            st.code(pretty(case.get("expect")), language="json")
        with d2:
            st.markdown("**Actual tool calls**")
            st.code(pretty(res.get("actual_tool_calls")), language="json")
            st.markdown("**Chấm**")
            st.code(pretty({k: res.get(k) for k in (
                "routing_correct", "args_correct", "failure_type", "observed_mismatch", "failures", "actual_text")}), language="json")
        with st.expander("Tool results thật (kết quả API)"):
            st.code(pretty(case.get("tool_results")), language="json")

    # --- version_log.csv ---
    st.subheader("version_log.csv")
    if VERSION_LOG.exists():
        lines = [l for l in VERSION_LOG.read_text(encoding="utf-8").splitlines() if l.strip()]
        if len(lines) <= 1:
            st.caption("Chưa có dòng version nào. Lead (A) điền sau mỗi run.")
        else:
            import csv
            from io import StringIO
            st.dataframe(list(csv.DictReader(StringIO("\n".join(lines)))), width="stretch", hide_index=True)
    else:
        st.caption("Không tìm thấy artifacts/version_log.csv.")
