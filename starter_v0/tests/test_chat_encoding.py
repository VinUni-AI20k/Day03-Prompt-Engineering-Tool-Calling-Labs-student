import io
from types import SimpleNamespace

from chat import run_model_tool_loop
from providers.base import ModelResponse, ToolCall


def test_tool_loop_handles_vietnamese_with_legacy_console(monkeypatch):
    responses = iter([
        ModelResponse(tool_calls=[ToolCall("lookup", {"query": "trí tuệ nhân tạo"})]),
        ModelResponse(text="Đã tìm thấy nguồn.")])
    provider = SimpleNamespace(complete=lambda *args, **kwargs: next(responses))
    stream = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict")
    monkeypatch.setattr("sys.stdout", stream)
    calls = []

    def execute(call):
        calls.append(call)
        return {"tool": call.name, "result": {"items": []}}

    result = run_model_tool_loop(provider=provider, messages=[], tools=[], model=None,
                                 max_tool_rounds=2, execute_call=execute)
    assert calls[0].args["query"] == "trí tuệ nhân tạo"
    assert result["assistant_text"] == "Đã tìm thấy nguồn."
    stream.flush()
