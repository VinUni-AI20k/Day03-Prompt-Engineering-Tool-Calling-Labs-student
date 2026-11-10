export type ResponseType = "text" | "yes_no" | "choice";

export type Ask = {
  question: string;
  response_type: ResponseType;
  options: string[];
};

export type AgentEvent =
  | { type: "session"; session_id: string }
  | { type: "thinking"; round: number }
  | { type: "note"; text: string }
  | { type: "tool_call"; id: string; name: string; args: Record<string, unknown> }
  | {
      type: "tool_result";
      id: string;
      name: string;
      result: unknown;
      duration_ms: number;
      error: boolean;
    }
  | {
      type: "final";
      status: "answered" | "waiting_for_user" | "max_tool_rounds";
      text: string;
      ask?: Ask;
    }
  | { type: "error"; message: string };

export type Step =
  | { kind: "note"; id: string; text: string }
  | {
      kind: "tool";
      id: string;
      name: string;
      args: Record<string, unknown>;
      status: "running" | "done" | "error";
      result?: unknown;
      durationMs?: number;
    };

export type UserMessage = { id: string; role: "user"; text: string };

export type AssistantMessage = {
  id: string;
  role: "assistant";
  steps: Step[];
  text: string;
  status: "streaming" | "done" | "error" | "stopped";
  thinking: boolean;
  ask?: Ask;
  answered?: boolean;
  error?: string;
};

export type Message = UserMessage | AssistantMessage;

export type Conversation = {
  id: string;
  title: string;
  sessionId?: string;
  messages: Message[];
  updatedAt: number;
};

export type Health = {
  ok: boolean;
  provider?: string;
  model?: string | null;
  version?: string;
  artifact_version?: string;
  error?: string;
};

export type ToolInfo = { name: string; description: string };
