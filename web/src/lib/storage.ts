import type { Conversation } from "./types";

const KEY = "research-agent.conversations.v1";
const MAX_CONVERSATIONS = 30;

export function loadConversations(): Conversation[] {
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as Conversation[];
    // A stream cannot survive a reload: close anything left "streaming".
    return parsed.map((c) => ({
      ...c,
      messages: c.messages.map((m) =>
        m.role === "assistant" && m.status === "streaming"
          ? { ...m, status: "stopped", thinking: false }
          : m,
      ),
    }));
  } catch {
    return [];
  }
}

export function saveConversations(conversations: Conversation[]): void {
  const trimmed = conversations.slice(0, MAX_CONVERSATIONS);
  try {
    window.localStorage.setItem(KEY, JSON.stringify(trimmed));
  } catch {
    try {
      window.localStorage.setItem(KEY, JSON.stringify(trimmed.slice(0, 5)));
    } catch {
      /* storage blocked or full: the app still works without history */
    }
  }
}
