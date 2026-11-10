// Shows every tool call of one agent turn: name, args, and the raw result.
// Tool errors are highlighted, never hidden (RUBRIC C6).

const MAX_JSON_CHARS = 8000;

function toJson(value) {
  const text = JSON.stringify(value, null, 2) ?? "";
  return text.length > MAX_JSON_CHARS ? `${text.slice(0, MAX_JSON_CHARS)}\n…(đã cắt bớt)` : text;
}

function formatArgValue(value) {
  if (typeof value === "string") return value.length > 60 ? `"${value.slice(0, 57)}…"` : `"${value}"`;
  if (Array.isArray(value)) return `[${value.length}]`;
  if (value && typeof value === "object") return "{…}";
  return String(value);
}

function outcome(result) {
  if (!result || typeof result !== "object") return { kind: "ok", label: "xong" };
  if (result.error) return { kind: "error", label: `lỗi: ${result.error}` };
  if (result.awaiting_user) return { kind: "wait", label: "hỏi lại người dùng" };
  if (result.status === "needs_confirmation") return { kind: "wait", label: "chờ xác nhận" };
  if (result.status === "sent") return { kind: "ok", label: "đã gửi" };
  const items = result.items ?? result.results;
  if (Array.isArray(items)) return { kind: items.length ? "ok" : "empty", label: `${items.length} kết quả` };
  if (typeof result.markdown === "string") return { kind: "ok", label: "đã định dạng" };
  return { kind: "ok", label: "xong" };
}

function ToolCall({ event }) {
  const { tool, args = {}, result } = event;
  const state = outcome(result);
  const argEntries = Object.entries(args);
  return (
    <details className={`tool-call tool-${state.kind}`}>
      <summary>
        <span className="tool-name">{tool}</span>
        <span className="tool-args">
          (
          {argEntries.map(([key, value], index) => (
            <span key={key}>
              {index > 0 && ", "}
              <span className="arg-key">{key}</span>=<span className="arg-value">{formatArgValue(value)}</span>
            </span>
          ))}
          )
        </span>
        <span className={`tool-status status-${state.kind}`}>{state.label}</span>
      </summary>
      {state.kind === "error" && result?.message && <p className="tool-error-message">{result.message}</p>}
      <div className="tool-json">
        <div className="json-label">args</div>
        <pre>{toJson(args)}</pre>
        <div className="json-label">result</div>
        <pre>{toJson(result)}</pre>
      </div>
    </details>
  );
}

export default function ToolTrace({ rounds }) {
  const events = (rounds ?? []).flatMap((round) =>
    (round.tool_results ?? []).map((event, index) => ({ ...event, key: `${round.round}-${index}`, round: round.round }))
  );
  if (!events.length) return null;
  const roundCount = new Set(events.map((event) => event.round)).size;
  return (
    <div className="tool-trace">
      <div className="tool-trace-title">
        {events.length} tool call{events.length > 1 ? "s" : ""} · {roundCount} vòng
      </div>
      {events.map((event) => (
        <ToolCall key={event.key} event={event} />
      ))}
    </div>
  );
}
