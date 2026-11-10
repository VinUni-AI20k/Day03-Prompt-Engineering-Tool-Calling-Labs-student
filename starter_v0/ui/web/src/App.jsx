import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import ToolTrace from "./ToolTrace.jsx";
import { getInfo, newSessionId, resetSession, sendMessage, storage } from "./api.js";

const SESSION_KEY = "research-agent.session";
const MESSAGES_KEY = "research-agent.messages";

const markdownComponents = {
  a: ({ node, ...props }) => <a {...props} target="_blank" rel="noopener noreferrer" />,
};

function StatusBadge({ status }) {
  if (status === "waiting_for_user") return <span className="badge badge-wait">Đang chờ bạn trả lời</span>;
  if (status === "provider_error") return <span className="badge badge-error">Lỗi provider</span>;
  if (status === "max_tool_rounds") return <span className="badge badge-error">Dừng: quá số vòng tool</span>;
  return null;
}

function Message({ message }) {
  if (message.role === "user") {
    return (
      <div className="msg msg-user">
        <div className="bubble">{message.text}</div>
      </div>
    );
  }
  return (
    <div className="msg msg-agent">
      <div className="agent-head">
        <span className="agent-name">Agent</span>
        <StatusBadge status={message.status} />
      </div>
      <ToolTrace rounds={message.rounds} />
      {message.error ? (
        <div className="error-box">{message.error}</div>
      ) : (
        <div className="markdown">
          <ReactMarkdown components={markdownComponents}>{message.text || "_(không có nội dung trả lời)_"}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [info, setInfo] = useState(null);
  const [infoError, setInfoError] = useState(null);
  const [sessionId, setSessionId] = useState(() => storage.get(SESSION_KEY, null) || newSessionId());
  const [messages, setMessages] = useState(() => storage.get(MESSAGES_KEY, []));
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [remaining, setRemaining] = useState(null);
  const [transcriptId, setTranscriptId] = useState(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const endRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    getInfo().then(setInfo).catch((error) => setInfoError(error.message));
  }, []);

  // Effect bodies are wrapped in braces on purpose: an effect must return nothing or a cleanup
  // function. Newer Chrome returns a Promise from scrollIntoView(), which React would then try
  // to call as a cleanup -> "TypeError: t is not a function" and a blank page.
  useEffect(() => {
    storage.set(SESSION_KEY, sessionId);
  }, [sessionId]);
  useEffect(() => {
    storage.set(MESSAGES_KEY, messages);
  }, [messages]);
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, busy]);

  async function submit(text) {
    const message = text.trim();
    if (!message || busy) return;
    setMenuOpen(false);
    setInput("");
    setMessages((current) => [...current, { role: "user", text: message }]);
    setBusy(true);
    try {
      const reply = await sendMessage(sessionId, message);
      setRemaining(reply.remaining_turns);
      setTranscriptId(reply.transcript_id);
      setMessages((current) => [
        ...current,
        { role: "agent", text: reply.assistant_text, status: reply.status, error: reply.error, rounds: reply.rounds },
      ]);
    } catch (error) {
      setMessages((current) => [...current, { role: "agent", status: "provider_error", error: error.message, rounds: [] }]);
    } finally {
      setBusy(false);
      inputRef.current?.focus();
    }
  }

  async function newChat() {
    if (busy) return;
    resetSession(sessionId).catch(() => {});
    setSessionId(newSessionId());
    setMessages([]);
    setRemaining(null);
    setTranscriptId(null);
    setMenuOpen(false);
  }

  function onKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault();
      submit(input);
    }
  }

  const maxTurns = info?.max_turns;
  const turnsLeft = remaining ?? maxTurns;

  return (
    <div className="app">
      <aside className={`sidebar ${menuOpen ? "open" : ""}`}>
        <div className="brand">
          <span className="brand-mark">◎</span>
          <div>
            <div className="brand-title">Research Agent</div>
            <div className="brand-sub">Nhóm 456 · Day 03</div>
          </div>
        </div>

        <button className="btn-new" onClick={newChat} disabled={busy}>
          + Cuộc chat mới
        </button>

        <section className="side-section">
          <h3>Thử nhanh</h3>
          <div className="samples">
            {(info?.sample_questions ?? []).map((question) => (
              <button key={question} className="sample" onClick={() => submit(question)} disabled={busy}>
                {question}
              </button>
            ))}
          </div>
        </section>

        <section className="side-section">
          <h3>Tool ({info?.tools?.length ?? 0})</h3>
          <ul className="tool-list">
            {(info?.tools ?? []).map((tool) => (
              <li
                key={tool.name}
                className={tool.missing_env?.length ? "tool-off" : ""}
                title={tool.missing_env?.length ? `Chưa cấu hình: ${tool.missing_env.join(", ")}` : tool.summary}
              >
                <code>
                  {tool.name}
                  {tool.missing_env?.length > 0 && <em className="off-badge">chưa có key</em>}
                </code>
                <span>{tool.summary}</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="side-section meta">
          <h3>Phiên bản</h3>
          {infoError && <div className="error-box">Không kết nối được backend: {infoError}</div>}
          {info && (
            <dl>
              <dt>Model</dt>
              <dd>
                {info.provider} / {info.model}
              </dd>
              <dt>Artifact</dt>
              <dd className="mono">{info.artifact_version}</dd>
              <dt>Telegram</dt>
              <dd>{info.telegram_configured ? "đã cấu hình" : "tắt (send chỉ trả lỗi)"}</dd>
              {transcriptId && (
                <>
                  <dt>Transcript</dt>
                  <dd className="mono">{transcriptId}</dd>
                </>
              )}
            </dl>
          )}
        </section>
      </aside>

      <main className="main">
        <header className="topbar">
          <button className="btn-menu" onClick={() => setMenuOpen((open) => !open)} aria-label="Mở menu">
            ☰
          </button>
          <div className="topbar-title">Research Agent</div>
          {maxTurns != null && (
            <div className="turns">
              còn <strong>{turnsLeft}</strong>/{maxTurns} lượt
            </div>
          )}
        </header>

        <div className="chat">
          {messages.length === 0 && (
            <div className="empty">
              <h1>Hỏi agent một câu research</h1>
              <p>
                Agent tìm tin web, tweet theo chủ đề hoặc theo tài khoản, đọc URL, tra Wikipedia, tìm paper arXiv và tra
                policy nội bộ. Thiếu thông tin thì agent hỏi lại; muốn gửi Telegram thì agent xin xác nhận trước.
              </p>
              <p className="hint">Mỗi câu trả lời hiện kèm tool đã gọi, arguments và kết quả thô. Bấm vào để xem.</p>
            </div>
          )}
          {messages.map((message, index) => (
            <Message key={index} message={message} />
          ))}
          {busy && (
            <div className="msg msg-agent">
              <div className="agent-head">
                <span className="agent-name">Agent</span>
              </div>
              <div className="thinking">
                <span />
                <span />
                <span />
                đang gọi model và tool…
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        <form
          className="composer"
          onSubmit={(event) => {
            event.preventDefault();
            submit(input);
          }}
        >
          <textarea
            ref={inputRef}
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Ví dụ: Tin AI hôm nay có gì? (Enter để gửi, Shift+Enter xuống dòng)"
            rows={1}
            maxLength={2000}
            disabled={busy}
          />
          <button type="submit" disabled={busy || !input.trim()}>
            Gửi
          </button>
        </form>
      </main>
      {menuOpen && <div className="scrim" onClick={() => setMenuOpen(false)} />}
    </div>
  );
}
