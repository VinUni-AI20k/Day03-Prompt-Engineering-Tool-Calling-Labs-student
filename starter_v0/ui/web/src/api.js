// Thin client for ui/server.py. Errors are thrown with the server's message so the UI can show them.

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  let body = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }
  if (!response.ok) {
    const detail = body?.detail;
    const message = typeof detail === "string" ? detail : `HTTP ${response.status}`;
    throw new Error(message);
  }
  return body;
}

export const getInfo = () => request("/api/info");

export const sendMessage = (sessionId, message) =>
  request("/api/chat", { method: "POST", body: JSON.stringify({ session_id: sessionId, message }) });

export const resetSession = (sessionId) =>
  request("/api/reset", { method: "POST", body: JSON.stringify({ session_id: sessionId }) });

export function newSessionId() {
  if (globalThis.crypto?.randomUUID) return crypto.randomUUID();
  return `s-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 12)}`;
}

// sessionStorage can throw (private mode, blocked storage) — the UI must work without it.
export const storage = {
  get(key, fallback) {
    try {
      const raw = sessionStorage.getItem(key);
      return raw ? JSON.parse(raw) : fallback;
    } catch {
      return fallback;
    }
  },
  set(key, value) {
    try {
      sessionStorage.setItem(key, JSON.stringify(value));
    } catch {
      /* ignore */
    }
  },
};
