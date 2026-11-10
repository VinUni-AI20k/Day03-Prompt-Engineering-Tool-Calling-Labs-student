"use client";

import { Check, ChevronRight, LoaderCircle, TriangleAlert } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { formatDuration, previewArgs } from "@/lib/format";
import type { Step } from "@/lib/types";
import { cn } from "@/lib/utils";
import { toolMeta } from "../tool-meta";

type ToolStepData = Extract<Step, { kind: "tool" }>;

function Json({ value }: { value: unknown }) {
  return (
    <pre className="max-h-64 overflow-auto rounded-[6px] bg-background/80 p-3 font-mono text-xs leading-relaxed whitespace-pre-wrap break-words">
      {JSON.stringify(value, null, 2)}
    </pre>
  );
}

export function ToolStep({ step }: { step: ToolStepData }) {
  const { label, icon: Icon } = toolMeta(step.name);
  const confirmedSend = step.name === "send" && step.args.confirmed === true;

  return (
    <Collapsible className="rounded-[8px] bg-card/80 ring-1 ring-border">
      <CollapsibleTrigger className="group/trigger flex w-full items-center gap-3 rounded-[8px] px-3 py-2.5 text-left outline-none focus-visible:ring-2 focus-visible:ring-ring">
        <span
          className={cn(
            "flex size-6 shrink-0 items-center justify-center rounded-[6px]",
            step.status === "error" ? "bg-destructive/10 text-destructive" : "bg-accent text-accent-foreground",
          )}
          aria-hidden
        >
          <Icon className="size-3.5" />
        </span>
        <span className="min-w-0 flex-1">
          <span className="flex items-center gap-2">
            <span className="font-mono text-[13px] font-medium">{step.name}</span>
            <span className="hidden text-xs text-muted-foreground sm:inline">{label}</span>
            {confirmedSend && <Badge variant="secondary">confirmed=true</Badge>}
          </span>
          <span className="block truncate text-xs text-muted-foreground">
            {previewArgs(step.args) || "không có tham số"}
          </span>
        </span>
        <span className="flex shrink-0 items-center gap-2 text-xs text-muted-foreground">
          {step.status === "running" && (
            <>
              <LoaderCircle className="size-4 animate-spin text-primary motion-reduce:animate-none" aria-hidden />
              <span className="sr-only">Đang chạy</span>
            </>
          )}
          {step.status === "done" && (
            <>
              <Check className="size-4 text-emerald-600 dark:text-emerald-400" aria-hidden />
              <span className="sr-only">Hoàn tất</span>
            </>
          )}
          {step.status === "error" && (
            <>
              <TriangleAlert className="size-4 text-destructive" aria-hidden />
              <span className="sr-only">Lỗi</span>
            </>
          )}
          {step.durationMs !== undefined && <span className="tabular-nums">{formatDuration(step.durationMs)}</span>}
          <ChevronRight
            className="size-4 transition-transform group-data-[panel-open]/trigger:rotate-90"
            aria-hidden
          />
        </span>
      </CollapsibleTrigger>
      <CollapsibleContent>
        <div className="space-y-3 border-t px-3 py-3">
          <div>
            <p className="mb-1.5 text-xs font-medium text-muted-foreground">Tham số</p>
            <Json value={step.args} />
          </div>
          <div>
            <p className="mb-1.5 text-xs font-medium text-muted-foreground">Kết quả</p>
            {step.result === undefined ? (
              <p className="text-xs text-muted-foreground">Đang chờ kết quả…</p>
            ) : (
              <Json value={step.result} />
            )}
          </div>
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}
