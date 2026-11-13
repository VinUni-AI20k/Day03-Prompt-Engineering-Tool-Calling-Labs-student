"use client";

import { Plus, Trash2, X } from "lucide-react";
import Image from "next/image";
import { useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import type { Conversation, Health, ToolInfo } from "@/lib/types";
import { cn } from "@/lib/utils";
import { toolMeta } from "./tool-meta";

type Props = {
  conversations: Conversation[];
  activeId: string;
  tools: ToolInfo[];
  health: Health | null;
  streaming: boolean;
  onNew: () => void;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  onClose: () => void;
};

function groupByDay(conversations: Conversation[]) {
  const withMessages = conversations.filter((c) => c.messages.length > 0);
  if (withMessages.length === 0) return [];
  const startOfToday = new Date();
  startOfToday.setHours(0, 0, 0, 0);
  const day = 24 * 60 * 60 * 1000;
  const groups: { label: string; items: Conversation[] }[] = [
    { label: "Hôm nay", items: [] },
    { label: "Hôm qua", items: [] },
    { label: "Trước đó", items: [] },
  ];
  for (const c of withMessages) {
    const age = startOfToday.getTime() - c.updatedAt;
    groups[age <= 0 ? 0 : age <= day ? 1 : 2].items.push(c);
  }
  return groups.filter((g) => g.items.length > 0);
}

export function Sidebar({
  conversations,
  activeId,
  tools,
  health,
  streaming,
  onNew,
  onSelect,
  onDelete,
  onClose,
}: Props) {
  const groups = useMemo(() => groupByDay(conversations), [conversations]);

  return (
    <div className="flex h-full flex-col px-4 py-5 md:px-2 md:py-1">
      <div className="flex items-center justify-between gap-2 pb-4">
        <div className="flex min-w-0 items-center gap-3">
          <Image src="/logo-256.jpg" alt="" width={40} height={40} className="size-10 rounded-[12px] ring-1 ring-border" />
          <div className="min-w-0 leading-tight">
            <p className="truncate text-lg font-semibold tracking-tight">Research Agent</p>
            <p className="text-xs text-muted-foreground">Nhóm Ban5</p>
          </div>
        </div>
        <Button variant="ghost" size="icon-sm" className="md:hidden" onClick={onClose} aria-label="Đóng thanh bên">
          <X />
        </Button>
      </div>

      <Button size="lg" className="h-10 w-full justify-start gap-2 px-3" onClick={onNew} disabled={streaming}>
        <Plus data-icon="inline-start" />
        Chat mới
        <kbd className="ml-auto rounded-[4px] bg-primary-foreground/20 px-1.5 py-0.5 font-sans text-[11px]">⌘K</kbd>
      </Button>

      <nav aria-label="Công cụ của agent" className="mt-6">
        <p className="mb-2 px-2 text-[11px] font-medium tracking-wide text-muted-foreground uppercase">
          Công cụ của agent
        </p>
        <ul className="space-y-0.5">
          {tools.length === 0 && <li className="px-2 py-1.5 text-sm text-muted-foreground">Đang tải…</li>}
          {tools.map((tool) => {
            const { icon: Icon, label } = toolMeta(tool.name);
            return (
              <li key={tool.name}>
                <Tooltip>
                  <TooltipTrigger
                    render={<div />}
                    className="flex cursor-default items-center gap-2.5 rounded-[6px] px-2 py-1.5 text-sm text-foreground/90 hover:bg-sidebar-accent"
                  >
                    <Icon className="size-4 shrink-0 text-muted-foreground" aria-hidden />
                    <span className="font-mono text-[13px]">{tool.name}</span>
                    <span className="truncate text-xs text-muted-foreground">{label}</span>
                  </TooltipTrigger>
                  <TooltipContent side="right">{tool.description}</TooltipContent>
                </Tooltip>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="mt-6 min-h-0 flex-1 overflow-y-auto">
        {groups.length === 0 && (
          <p className="px-2 text-sm text-muted-foreground">Các cuộc trò chuyện sẽ hiện ở đây.</p>
        )}
        {groups.map((group) => (
          <section key={group.label} className="mb-4">
            <p className="mb-1.5 px-2 text-[11px] font-medium tracking-wide text-muted-foreground uppercase">
              {group.label}
            </p>
            <ul className="space-y-0.5">
              {group.items.map((c) => (
                <li key={c.id} className="group/item relative">
                  <button
                    type="button"
                    onClick={() => onSelect(c.id)}
                    disabled={streaming && c.id !== activeId}
                    aria-current={c.id === activeId ? "true" : undefined}
                    className={cn(
                      "w-full truncate rounded-[6px] px-2 py-1.5 pr-8 text-left text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50",
                      c.id === activeId ? "bg-sidebar-accent font-medium" : "hover:bg-sidebar-accent/70",
                    )}
                  >
                    {c.version && (
                      <span className="mr-2 font-mono text-[11px] text-muted-foreground">{c.version}</span>
                    )}
                    {c.title}
                  </button>
                  <button
                    type="button"
                    onClick={() => onDelete(c.id)}
                    disabled={streaming}
                    aria-label={`Xóa cuộc trò chuyện ${c.title}`}
                    className="absolute top-1/2 right-1 flex size-6 -translate-y-1/2 items-center justify-center rounded-[4px] text-muted-foreground opacity-0 outline-none group-hover/item:opacity-100 hover:text-destructive focus-visible:opacity-100 focus-visible:ring-2 focus-visible:ring-ring"
                  >
                    <Trash2 className="size-3.5" />
                  </button>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>

      <div className="mt-2 rounded-[12px] border bg-card/70 p-3" aria-live="polite">
        <div className="flex items-center gap-2">
          <span
            className={cn(
              "size-2 shrink-0 rounded-full",
              health === null ? "bg-muted-foreground/40" : health.ok ? "bg-emerald-500" : "bg-destructive",
            )}
            aria-hidden
          />
          <p className="text-sm font-medium">
            {health === null ? "Đang kiểm tra server…" : health.ok ? "Server agent sẵn sàng" : "Server agent ngắt kết nối"}
          </p>
        </div>
        {health?.ok ? (
          <p className="mt-1 truncate font-mono text-xs text-muted-foreground">
            {health.provider} · {health.model} · {health.version}
          </p>
        ) : (
          health && (
            <p className="mt-1 text-xs text-muted-foreground">
              Chạy <span className="font-mono">python server.py</span> trong starter_v0.
            </p>
          )
        )}
      </div>
    </div>
  );
}
