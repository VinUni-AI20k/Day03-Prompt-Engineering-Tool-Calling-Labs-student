import type { AgentEvent, Health, ToolInfo, VersionsResponse } from "./types";

async function errorMessage(res: Response): Promise<string> {
  try {
    const body = await res.json();
    if (typeof body?.detail === "string") return body.detail;
  } catch {
    /* not JSON */
  }
  if (res.status === 502 || res.status === 503 || res.status === 500) {
    return "Không kết nối được tới server agent. Kiểm tra `python server.py` đang chạy.";
  }
  return `Lỗi ${res.status}`;
}

export async function fetchHealth(): Promise<Health> {
  try {
    const res = await fetch("/api/health", { cache: "no-store" });
    if (!res.ok) return { ok: false, error: await errorMessage(res) };
    return (await res.json()) as Health;
  } catch {
    return { ok: false, error: "Không kết nối được tới server agent." };
  }
}

export async function fetchVersions(): Promise<VersionsResponse> {
  try {
    const res = await fetch("/api/versions", { cache: "no-store" });
    return res.ok ? ((await res.json()) as VersionsResponse) : { default: null, versions: [] };
  } catch {
    return { default: null, versions: [] };
  }
}

export async function fetchTools(version?: string): Promise<ToolInfo[]> {
  try {
    const query = version ? `?version=${encodeURIComponent(version)}` : "";
    const res = await fetch(`/api/tools${query}`, { cache: "no-store" });
    return res.ok ? ((await res.json()) as ToolInfo[]) : [];
  } catch {
    return [];
  }
}

/** POST /api/chat and call onEvent for every Server-Sent Event as it arrives. */
export async function streamChat(
  body: { session_id?: string; message: string; version?: string },
  onEvent: (event: AgentEvent) => void,
  signal: AbortSignal,
): Promise<void> {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  if (!res.ok || !res.body) throw new Error(await errorMessage(res));

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let boundary = buffer.indexOf("\n\n");
    while (boundary !== -1) {
      const chunk = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      for (const line of chunk.split("\n")) {
        if (!line.startsWith("data:")) continue;
        try {
          onEvent(JSON.parse(line.slice(5).trim()) as AgentEvent);
        } catch {
          /* ignore a malformed frame */
        }
      }
      boundary = buffer.indexOf("\n\n");
    }
  }
}
