"use client";

import { RotateCcw } from "lucide-react";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import type { AssistantMessage } from "@/lib/types";
import { AskControls } from "./ask-controls";
import { Markdown } from "./markdown";
import { ToolStep } from "./tool-step";

type Props = {
  message: AssistantMessage;
  isLast: boolean;
  onAnswer: (text: string) => void;
  onRetry: () => void;
};

export function AssistantMessageView({ message, isLast, onAnswer, onRetry }: Props) {
  const toolCount = message.steps.filter((s) => s.kind === "tool").length;
  const waitingForText = message.status === "streaming" && message.thinking;

  return (
    <div className="rise-in flex gap-3">
      <Image
        src="/logo-256.jpg"
        alt=""
        width={32}
        height={32}
        className="mt-0.5 size-8 shrink-0 rounded-[6px] ring-1 ring-border"
      />
      <div className="min-w-0 flex-1">
        {toolCount > 0 && (
          <div className="mb-3 space-y-1.5">
            <p className="text-xs font-medium text-muted-foreground">
              {message.status === "streaming" ? "Agent đang chạy" : "Agent đã chạy"} {toolCount} công cụ
            </p>
            {message.steps.map((step) =>
              step.kind === "tool" ? (
                <ToolStep key={step.id} step={step} />
              ) : (
                <p key={step.id} className="px-1 text-sm text-muted-foreground">
                  {step.text}
                </p>
              ),
            )}
          </div>
        )}

        {waitingForText && (
          <div role="status" aria-live="polite" className="space-y-2">
            <p className="shimmer-text text-sm font-medium">
              {toolCount > 0 ? "Đang tổng hợp kết quả…" : "Đang suy nghĩ…"}
            </p>
            {toolCount === 0 && (
              <>
                <Skeleton className="h-3.5 w-3/4 rounded-[4px]" />
                <Skeleton className="h-3.5 w-1/2 rounded-[4px]" />
              </>
            )}
          </div>
        )}

        {message.text && <Markdown>{message.text}</Markdown>}

        {message.status === "stopped" && (
          <p className="mt-2 text-sm text-muted-foreground">Đã dừng theo yêu cầu của bạn.</p>
        )}

        {message.status === "error" && (
          <div role="alert" className="mt-2 rounded-[12px] border border-destructive/30 bg-destructive/5 p-4">
            <p className="text-sm font-medium text-destructive">Không hoàn thành được yêu cầu</p>
            {message.error && (
              <p className="mt-1 text-sm break-words text-muted-foreground">{message.error}</p>
            )}
            {isLast && (
              <Button variant="outline" size="sm" className="mt-3" onClick={onRetry}>
                <RotateCcw data-icon="inline-start" />
                Thử lại
              </Button>
            )}
          </div>
        )}

        {isLast && message.status === "done" && message.ask && !message.answered && (
          <AskControls ask={message.ask} onAnswer={onAnswer} />
        )}
      </div>
    </div>
  );
}
