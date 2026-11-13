"use client";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { VersionInfo } from "@/lib/types";

type Props = {
  versions: VersionInfo[];
  value: string | undefined;
  disabled?: boolean;
  onChange: (version: string) => void;
};

export function versionLabel(v: VersionInfo): string {
  const score = v.accuracy === null ? "" : ` · ${Math.round(v.accuracy * 100)}%`;
  return `${v.id} · ${v.label}${score}`;
}

/** Dropdown to pick which frozen prompt/tools version the next chat runs on. */
export function VersionSelect({ versions, value, disabled, onChange }: Props) {
  if (versions.length === 0) return null;
  const items = versions.map((v) => ({ value: v.id, label: versionLabel(v) }));
  return (
    <Select
      value={value ?? null}
      items={items}
      disabled={disabled}
      onValueChange={(next) => {
        if (typeof next === "string") onChange(next);
      }}
    >
      <SelectTrigger size="sm" aria-label="Chọn version của agent" className="max-w-[16rem] bg-secondary/60">
        <SelectValue placeholder="Chọn version" />
      </SelectTrigger>
      <SelectContent align="start" className="min-w-72">
        {versions.map((v) => (
          <SelectItem key={v.id} value={v.id}>
            <span className="flex w-full items-center justify-between gap-4">
              <span>
                <span className="font-mono text-[13px] font-medium">{v.id}</span>{" "}
                <span className="text-muted-foreground">{v.label}</span>
              </span>
              {v.accuracy !== null && (
                <span className="text-xs tabular-nums text-muted-foreground">{Math.round(v.accuracy * 100)}%</span>
              )}
            </span>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
