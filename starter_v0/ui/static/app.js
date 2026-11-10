const KEY = "dnh-team-chat-v1";
const MODEL_KEY = "dnh-team-model-v1";
const SESSION_KEY = "dnh-team-session-v1";

const thread = document.getElementById("thread");
const emptyEl = document.getElementById("empty");
const messagesEl = document.getElementById("messages");
const form = document.getElementById("composer");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");
const statusEl = document.getElementById("status");
const modelEl = document.getElementById("model");
const plusBtn = document.getElementById("plus");
const menu = document.getElementById("menu");
const clearBtn = document.getElementById("clear");

const COPY_SVG = `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><rect x="8" y="8" width="11" height="11" rx="2"/><path d="M6 15H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v1"/></svg>`;

const state = {
  messages: load(),
  busy: false,
  sessionId: loadSessionId(),
};

function loadSessionId() {
  try {
    const existing = localStorage.getItem(SESSION_KEY);
    if (existing && /^[A-Za-z0-9_-]{8,64}$/.test(existing)) return existing;
  } catch {
    /* ignore */
  }
  const id = cryptoRandomId();
  try {
    localStorage.setItem(SESSION_KEY, id);
  } catch {
    /* ignore */
  }
  return id;
}

function cryptoRandomId() {
  if (window.crypto && crypto.getRandomValues) {
    const bytes = new Uint8Array(16);
    crypto.getRandomValues(bytes);
    return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
  }
  return `s${Date.now().toString(36)}${Math.random().toString(36).slice(2, 10)}`;
}

function load() {
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) || "[]");
    if (!Array.isArray(raw)) return [];
    return raw
      .filter((m) => m && (m.role === "user" || m.role === "assistant") && typeof m.text === "string" && !m.pending)
      .map((m) => ({
        id: String(m.id || uid()),
        role: m.role,
        text: m.text,
        summary: typeof m.summary === "string" ? m.summary : "",
        error: Boolean(m.error),
      }));
  } catch {
    return [];
  }
}

function save() {
  const keep = state.messages.filter((m) => !m.pending);
  localStorage.setItem(KEY, JSON.stringify(keep));
}

function uid() {
  return Math.random().toString(36).slice(2, 10);
}

function iconButton(svg, label, onClick) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "icon-btn";
  btn.setAttribute("aria-label", label);
  btn.innerHTML = svg;
  btn.addEventListener("click", onClick);
  return btn;
}

function render() {
  const nearBottom = thread.scrollHeight - thread.scrollTop - thread.clientHeight < 120;
  emptyEl.hidden = state.messages.length > 0;
  messagesEl.replaceChildren();
  for (const m of state.messages) {
    messagesEl.append(m.role === "user" ? userNode(m) : assistantNode(m));
  }
  if (nearBottom || state.busy) thread.scrollTop = thread.scrollHeight;
}

function userNode(m) {
  const el = document.createElement("div");
  el.className = "msg-user";
  el.textContent = m.text;
  return el;
}

function assistantNode(m) {
  const wrap = document.createElement("div");
  const text = document.createElement("div");
  text.className = "msg-assistant" + (m.pending ? " pending" : "") + (m.error ? " error" : "");
  text.textContent = m.text;
  wrap.append(text);
  if (m.pending || m.error || !m.text) return wrap;

  const actions = document.createElement("div");
  actions.className = "actions";
  actions.append(
    iconButton(COPY_SVG, "Chép", async () => {
      try {
        await navigator.clipboard.writeText(m.text);
        statusEl.textContent = "Đã chép";
      } catch {
        statusEl.textContent = "Không chép được";
      }
    })
  );
  wrap.append(actions);
  if (m.summary) {
    const meta = document.createElement("details");
    meta.className = "meta";
    const summary = document.createElement("summary");
    summary.textContent = "Chi tiết lượt";
    const p = document.createElement("p");
    p.textContent = m.summary;
    meta.append(summary, p);
    wrap.append(meta);
  }
  return wrap;
}

function setBusy(busy, label) {
  state.busy = busy;
  statusEl.textContent = label;
  sendBtn.disabled = busy;
  input.disabled = busy;
  if (modelEl.dataset.selectable === "1") modelEl.disabled = busy;
  if (!busy) input.focus();
}

function selectedModel() {
  return (modelEl.value || "").trim();
}

function fillModels(health) {
  const models = Array.isArray(health.models) ? health.models.filter(Boolean) : [];
  const selectable = Boolean(health.model_selectable);
  modelEl.dataset.selectable = selectable ? "1" : "0";
  modelEl.disabled = !selectable;
  modelEl.replaceChildren();
  if (!models.length) {
    const opt = document.createElement("option");
    opt.value = health.model || "";
    opt.textContent = health.model || health.provider || "offline";
    modelEl.append(opt);
    return;
  }
  const saved = localStorage.getItem(MODEL_KEY) || "";
  const current = models.includes(saved) ? saved : health.model || models[0];
  for (const id of models) {
    const opt = document.createElement("option");
    opt.value = id;
    opt.textContent = id;
    if (id === current) opt.selected = true;
    modelEl.append(opt);
  }
  if (selectable && current) localStorage.setItem(MODEL_KEY, current);
}

function grow() {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 160) + "px";
  sendBtn.hidden = input.value.trim().length === 0;
}

async function post(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Session-Id": state.sessionId,
    },
    body: JSON.stringify({ ...payload, session_id: state.sessionId }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `Lỗi ${res.status}`);
  return data;
}

async function sendText(text) {
  const user = { id: uid(), role: "user", text };
  const pending = { id: uid(), role: "assistant", text: "Đang trả lời…", pending: true };
  state.messages.push(user, pending);
  save();
  render();
  setBusy(true, "Đang trả lời…");
  try {
    const data = await post("/api/chat", { text, model: selectedModel() });
    const reply = (data.assistant_text || "").trim();
    Object.assign(pending, {
      pending: false,
      text: reply || "DNH team chưa trả lời.",
      summary: data.summary || "",
      error: !reply,
    });
  } catch (err) {
    Object.assign(pending, { pending: false, text: err.message, error: true, summary: "" });
  }
  save();
  render();
  setBusy(false, "Sẵn sàng");
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text || state.busy) return;
  input.value = "";
  grow();
  sendText(text);
});

input.addEventListener("input", grow);
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});

plusBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  menu.hidden = !menu.hidden;
  plusBtn.setAttribute("aria-expanded", String(!menu.hidden));
});

clearBtn.addEventListener("click", async () => {
  menu.hidden = true;
  plusBtn.setAttribute("aria-expanded", "false");
  setBusy(true, "Đang xóa…");
  try {
    await post("/api/reset", {});
    state.messages = [];
    localStorage.removeItem(KEY);
    statusEl.textContent = "Đã xóa cuộc trò chuyện";
  } catch (err) {
    statusEl.textContent = err.message || "Không xóa được phía server";
  }
  render();
  setBusy(false, statusEl.textContent);
});

document.addEventListener("click", (e) => {
  if (!menu.hidden && !menu.parentElement.contains(e.target)) {
    menu.hidden = true;
    plusBtn.setAttribute("aria-expanded", "false");
  }
});

modelEl.addEventListener("change", async () => {
  const model = selectedModel();
  if (!model || modelEl.dataset.selectable !== "1") return;
  localStorage.setItem(MODEL_KEY, model);
  try {
    await post("/api/model", { model });
    statusEl.textContent = `Model: ${model}`;
  } catch (err) {
    statusEl.textContent = err.message;
  }
});

fetch("/api/health", { headers: { "X-Session-Id": state.sessionId } })
  .then((r) => r.json())
  .then((h) => fillModels(h))
  .catch(() => {
    modelEl.replaceChildren();
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = "offline";
    modelEl.append(opt);
    modelEl.disabled = true;
  });

render();
grow();
input.focus();
