export function formatDuration(ms?: number): string {
  if (ms === undefined) return "";
  return ms < 1000 ? `${ms} ms` : `${(ms / 1000).toFixed(1)} s`;
}

export function previewArgs(args: Record<string, unknown>, max = 72): string {
  const text = Object.entries(args)
    .filter(([, value]) => value !== "" && value !== undefined && value !== null)
    .map(([key, value]) => `${key}: ${typeof value === "string" ? value : JSON.stringify(value)}`)
    .join(" · ");
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
}

/** Keep stored/displayed tool results small; a full dump is in the transcript file. */
export function compactResult(result: unknown, limit = 6000): unknown {
  try {
    const text = JSON.stringify(result);
    if (text && text.length > limit) return { _truncated: `${text.slice(0, limit)}…` };
  } catch {
    /* fall through */
  }
  return result;
}
