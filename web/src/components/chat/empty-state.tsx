"use client";

import { Calculator, FileText, Newspaper, Send, Sparkles, type LucideIcon } from "lucide-react";
import Image from "next/image";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import type { ToolInfo } from "@/lib/types";
import { Composer } from "./composer";
import { toolMeta } from "../tool-meta";

type Sample = { icon: LucideIcon; title: string; hint: string; prompt: string };

const SAMPLES: Sample[] = [
  {
    icon: Newspaper,
    title: "Tin tức AI hôm nay",
    hint: "Agent chọn lookup và tra cứu web.",
    prompt: "Tin tức AI hôm nay có gì nổi bật?",
  },
  {
    icon: FileText,
    title: "Tóm tắt tweet (thiếu thông tin)",
    hint: "Agent phải hỏi lại tài khoản nào.",
    prompt: "Tóm tắt 5 tweet mới nhất giúp mình",
  },
  {
    icon: Send,
    title: "Đăng bản tin lên Telegram",
    hint: "Agent xin xác nhận trước khi gửi.",
    prompt: "Đăng bản tin này lên Telegram giúp mình",
  },
  {
    icon: Calculator,
    title: "Thống kê nhanh",
    hint: "Agent dùng tool stats của nhóm.",
    prompt: "Tính trung bình và độ lệch chuẩn của 2, 3, 7, 10",
  },
];

type Props = {
  tools: ToolInfo[];
  onSend: (text: string) => void;
  onStop: () => void;
  streaming: boolean;
};

export function EmptyState({ tools, onSend, onStop, streaming }: Props) {
  return (
    <div className="flex flex-1 flex-col items-center overflow-y-auto px-4 py-8 sm:px-6">
      <div className="m-auto flex w-full max-w-3xl flex-col items-center">
        <Badge variant="secondary" className="mb-6 h-7 gap-1.5 px-3 text-[13px] font-normal">
          <Sparkles className="text-primary" aria-hidden />
          Chạy tool thật, mỗi lượt đều có log JSON
        </Badge>
        <Image
          src="/logo-256.jpg"
          alt="Research Agent"
          width={96}
          height={96}
          priority
          className="mb-5 size-24 rounded-[12px] ring-1 ring-border"
        />
        <h1 className="mb-8 text-center text-3xl font-semibold tracking-tight text-balance sm:text-4xl">
          Hôm nay bạn muốn nghiên cứu gì?
        </h1>

        <div className="w-full">
          <Composer onSend={onSend} onStop={onStop} streaming={streaming} placeholder="Hỏi agent bất cứ điều gì…">
            {tools.length > 0 && (
              <div className="mx-1 flex flex-wrap items-center justify-between gap-2 rounded-b-[12px] border border-t-0 bg-muted/60 px-4 py-2.5">
                <span className="text-sm text-muted-foreground">{tools.length} công cụ sẵn sàng cho agent</span>
                <ul className="flex flex-wrap gap-1.5" aria-label="Danh sách công cụ">
                  {tools.map((tool) => {
                    const { icon: Icon } = toolMeta(tool.name);
                    return (
                      <li key={tool.name}>
                        <Tooltip>
                          <TooltipTrigger
                            className="flex size-7 items-center justify-center rounded-[6px] bg-card text-muted-foreground ring-1 ring-border outline-none hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring"
                            aria-label={tool.name}
                          >
                            <Icon className="size-3.5" />
                          </TooltipTrigger>
                          <TooltipContent>
                            <span className="font-mono">{tool.name}</span>
                          </TooltipContent>
                        </Tooltip>
                      </li>
                    );
                  })}
                </ul>
              </div>
            )}
          </Composer>
        </div>

        <ul className="mt-6 grid w-full gap-3 sm:grid-cols-2">
          {SAMPLES.map((sample) => (
            <li key={sample.title}>
              <button
                type="button"
                onClick={() => onSend(sample.prompt)}
                disabled={streaming}
                className="group flex h-full w-full flex-col gap-1 rounded-[12px] border bg-muted/40 p-4 text-left transition-colors outline-none hover:border-primary/40 hover:bg-accent/50 focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50"
              >
                <sample.icon className="mb-1 size-5 text-primary" aria-hidden />
                <span className="text-sm font-medium">{sample.title}</span>
                <span className="text-xs text-muted-foreground">{sample.hint}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
