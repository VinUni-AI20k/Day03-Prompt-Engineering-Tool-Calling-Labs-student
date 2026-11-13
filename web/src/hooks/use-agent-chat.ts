"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { toast } from "sonner";
import { streamChat } from "@/lib/api";
import { compactResult } from "@/lib/format";
import { loadConversations, saveConversations } from "@/lib/storage";
import type {
  AgentEvent,
  AssistantMessage,
  Conversation,
  Message,
} from "@/lib/types";

const uid = () => crypto.randomUUID();

function makeConversation(version?: string): Conversation {
  return { id: uid(), title: "Chat mới", version, messages: [], updatedAt: Date.now() };
}

function applyEvent(message: AssistantMessage, event: AgentEvent): AssistantMessage {
  switch (event.type) {
    case "thinking":
      return { ...message, thinking: true };
    case "note":
      return {
        ...message,
        steps: [...message.steps, { kind: "note", id: uid(), text: event.text }],
      };
    case "tool_call":
      return {
        ...message,
        thinking: false,
        steps: [
          ...message.steps,
          { kind: "tool", id: event.id, name: event.name, args: event.args, status: "running" },
        ],
      };
    case "tool_result":
      return {
        ...message,
        steps: message.steps.map((step) =>
          step.kind === "tool" && step.id === event.id
            ? {
                ...step,
                status: event.error ? "error" : "done",
                result: compactResult(event.result),
                durationMs: event.duration_ms,
              }
            : step,
        ),
      };
    case "final":
      return {
        ...message,
        thinking: false,
        status: "done",
        text: event.text,
        ask: event.status === "waiting_for_user" ? event.ask : undefined,
      };
    case "error":
      return { ...message, thinking: false, status: "error", error: event.message };
    default:
      return message;
  }
}

export function useAgentChat(defaultVersion?: string) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string>("");
  const [hydrated, setHydrated] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const streamingRef = useRef(false);

  // Load history after mount so server and client markup match.
  useEffect(() => {
    const stored = loadConversations();
    const fresh = makeConversation();
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setConversations([fresh, ...stored.filter((c) => c.messages.length > 0)]);
    setActiveId(fresh.id);
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated || streaming) return;
    saveConversations(conversations.filter((c) => c.messages.length > 0));
  }, [conversations, hydrated, streaming]);

  const active = useMemo(
    () => conversations.find((c) => c.id === activeId),
    [conversations, activeId],
  );
  const activeVersion = active?.version ?? defaultVersion;

  const patchConversation = useCallback(
    (id: string, fn: (conversation: Conversation) => Conversation) => {
      setConversations((list) => list.map((c) => (c.id === id ? fn(c) : c)));
    },
    [],
  );

  const patchLastAssistant = useCallback(
    (id: string, fn: (message: AssistantMessage) => AssistantMessage) => {
      patchConversation(id, (c) => {
        const messages = [...c.messages];
        const last = messages[messages.length - 1];
        if (last?.role === "assistant") messages[messages.length - 1] = fn(last);
        return { ...c, messages, updatedAt: Date.now() };
      });
    },
    [patchConversation],
  );

  const send = useCallback(
    async (text: string) => {
      const content = text.trim();
      if (!content || streamingRef.current || !active) return;

      const conversationId = active.id;
      const userMessage: Message = { id: uid(), role: "user", text: content };
      const assistantMessage: AssistantMessage = {
        id: uid(),
        role: "assistant",
        steps: [],
        text: "",
        status: "streaming",
        thinking: true,
      };

      patchConversation(conversationId, (c) => {
        // The previous question (if any) has now been answered.
        const messages = c.messages.map((m) =>
          m.role === "assistant" && m.ask && !m.answered ? { ...m, answered: true } : m,
        );
        return {
          ...c,
          title: c.messages.length === 0 ? content.slice(0, 48) : c.title,
          version: c.version ?? activeVersion,
          messages: [...messages, userMessage, assistantMessage],
          updatedAt: Date.now(),
        };
      });

      const controller = new AbortController();
      abortRef.current = controller;
      streamingRef.current = true;
      setStreaming(true);

      try {
        await streamChat(
          { session_id: active.sessionId, message: content, version: active.version ?? activeVersion },
          (event) => {
            if (event.type === "session") {
              patchConversation(conversationId, (c) => ({ ...c, sessionId: event.session_id }));
              return;
            }
            if (event.type === "error") toast.error("Agent gặp lỗi", { description: event.message });
            if (event.type === "tool_result" && event.name === "send") {
              const result = event.result as { status?: string } | null;
              if (result?.status === "sent") {
                toast.success("Đã gửi lên Telegram", { description: "Tin nhắn đã vào kênh riêng của nhóm." });
              }
            }
            patchLastAssistant(conversationId, (m) => applyEvent(m, event));
          },
          controller.signal,
        );
        // Stream closed without a final event (server stopped mid-way).
        patchLastAssistant(conversationId, (m) =>
          m.status === "streaming"
            ? { ...m, thinking: false, status: "error", error: "Kết nối bị ngắt trước khi agent trả lời xong." }
            : m,
        );
      } catch (error) {
        const aborted = error instanceof DOMException && error.name === "AbortError";
        const message = error instanceof Error ? error.message : "Lỗi không xác định";
        if (!aborted) toast.error("Không gửi được yêu cầu", { description: message });
        patchLastAssistant(conversationId, (m) => ({
          ...m,
          thinking: false,
          status: aborted ? "stopped" : "error",
          steps: m.steps.map((s) => (s.kind === "tool" && s.status === "running" ? { ...s, status: "error" } : s)),
          error: aborted ? undefined : message,
        }));
      } finally {
        abortRef.current = null;
        streamingRef.current = false;
        setStreaming(false);
      }
    },
    [active, activeVersion, patchConversation, patchLastAssistant],
  );

  const stop = useCallback(() => abortRef.current?.abort(), []);

  const retry = useCallback(() => {
    if (!active || streamingRef.current) return;
    const messages = active.messages;
    const lastUser = [...messages].reverse().find((m) => m.role === "user");
    if (!lastUser || lastUser.role !== "user") return;
    patchConversation(active.id, (c) => ({ ...c, messages: c.messages.slice(0, -2) }));
    // Wait a tick so the trimmed state is applied before sending again.
    setTimeout(() => void send(lastUser.text), 0);
  }, [active, patchConversation, send]);

  const newChat = useCallback(() => {
    if (streamingRef.current) return;
    if (active && active.messages.length === 0) return;
    const fresh = makeConversation(activeVersion);
    setConversations((list) => [fresh, ...list]);
    setActiveId(fresh.id);
  }, [active, activeVersion]);

  /** Pick the version for the next messages. A chat that already started keeps its version, so open a new one. */
  const selectVersion = useCallback(
    (version: string) => {
      if (streamingRef.current || version === activeVersion) return false;
      if (active && active.messages.length === 0) {
        patchConversation(active.id, (c) => ({ ...c, version }));
        return false;
      }
      const fresh = makeConversation(version);
      setConversations((list) => [fresh, ...list]);
      setActiveId(fresh.id);
      return true;
    },
    [active, activeVersion, patchConversation],
  );

  const selectChat = useCallback((id: string) => {
    if (streamingRef.current) return;
    setActiveId(id);
  }, []);

  const deleteChat = useCallback(
    (id: string) => {
      if (streamingRef.current) return;
      const rest = conversations.filter((c) => c.id !== id);
      if (rest.length === 0) {
        const fresh = makeConversation();
        setConversations([fresh]);
        setActiveId(fresh.id);
        return;
      }
      setConversations(rest);
      if (id === activeId) setActiveId(rest[0].id);
    },
    [conversations, activeId],
  );

  return {
    conversations,
    active,
    activeVersion,
    hydrated,
    streaming,
    send,
    stop,
    retry,
    newChat,
    selectVersion,
    selectChat,
    deleteChat,
  };
}
