"use client";

import { Download, Menu, Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { fetchHealth, fetchTools, fetchVersions } from "@/lib/api";
import { useAgentChat } from "@/hooks/use-agent-chat";
import type { Health, ToolInfo, VersionInfo } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Composer } from "./chat/composer";
import { EmptyState } from "./chat/empty-state";
import { MessageList } from "./chat/message-list";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Sidebar } from "./sidebar";
import { VersionSelect } from "./version-select";

export function AppShell() {
  const [versions, setVersions] = useState<VersionInfo[]>([]);
  const [defaultVersion, setDefaultVersion] = useState<string>();
  const chat = useAgentChat(defaultVersion);
  const { newChat } = chat;
  const { resolvedTheme, setTheme } = useTheme();
  const [health, setHealth] = useState<Health | null>(null);
  const [tools, setTools] = useState<ToolInfo[]>([]);
  const [navOpen, setNavOpen] = useState(false);

  useEffect(() => {
    void fetchHealth().then(setHealth);
    void fetchVersions().then((res) => {
      setVersions(res.versions);
      setDefaultVersion(res.default ?? undefined);
    });
  }, []);

  // The tool list shown in the UI follows the selected version (v0 has no `stats`).
  const activeVersion = chat.activeVersion;
  useEffect(() => {
    let cancelled = false;
    void fetchTools(activeVersion).then((list) => {
      if (!cancelled) setTools(list);
    });
    return () => {
      cancelled = true;
    };
  }, [activeVersion]);

  // Cmd/Ctrl + K starts a new chat.
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        newChat();
        setNavOpen(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [newChat]);

  const messages = chat.active?.messages ?? [];
  const isEmpty = messages.length === 0;
  const sessionId = chat.active?.sessionId;

  return (
    <div className="flex h-dvh md:gap-4 md:p-4">
      {navOpen && (
        <div className="fixed inset-0 z-40 bg-black/40 md:hidden" onClick={() => setNavOpen(false)} aria-hidden />
      )}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-72 border-r bg-sidebar transition-transform duration-200 md:static md:z-auto md:w-72 md:shrink-0 md:translate-x-0 md:border-r-0 md:bg-transparent",
          navOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <Sidebar
          conversations={chat.conversations}
          activeId={chat.active?.id ?? ""}
          tools={tools}
          health={health}
          streaming={chat.streaming}
          onNew={() => {
            chat.newChat();
            setNavOpen(false);
          }}
          onSelect={(id) => {
            chat.selectChat(id);
            setNavOpen(false);
          }}
          onDelete={chat.deleteChat}
          onClose={() => setNavOpen(false)}
        />
      </aside>

      <main className="flex min-w-0 flex-1 flex-col overflow-hidden bg-card md:rounded-[12px] md:border md:shadow-sm">
        <header className="flex h-16 shrink-0 items-center justify-between gap-3 border-b px-4 sm:px-6">
          <div className="flex min-w-0 items-center gap-3">
            <Button
              variant="ghost"
              size="icon-sm"
              className="md:hidden"
              onClick={() => setNavOpen(true)}
              aria-label="Mở thanh bên"
            >
              <Menu />
            </Button>
            <h2 className="truncate text-base font-medium">{isEmpty ? "Chat mới" : chat.active?.title}</h2>
            {versions.length === 0 && health?.ok && (
              <Tooltip>
                <TooltipTrigger render={<span />} className="inline-flex">
                  <Badge variant="secondary">{health.version}</Badge>
                </TooltipTrigger>
                <TooltipContent>
                  Server chưa hỗ trợ chọn version. Khởi động lại <span className="font-mono">python server.py</span> để có dropdown.
                </TooltipContent>
              </Tooltip>
            )}
            <VersionSelect
              versions={versions}
              value={activeVersion}
              disabled={chat.streaming}
              onChange={(version) => {
                if (chat.selectVersion(version) && !isEmpty) {
                  toast.info(`Đã mở chat mới với ${version}`, {
                    description: "Mỗi cuộc chat giữ nguyên một version để transcript không bị lẫn.",
                  });
                }
              }}
            />
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={!sessionId}
              onClick={() => {
                if (!sessionId) return;
                const link = document.createElement("a");
                link.href = `/api/transcript/${sessionId}`;
                link.download = "";
                link.click();
              }}
            >
              <Download data-icon="inline-start" />
              <span className="hidden sm:inline">Tải transcript</span>
              <span className="sr-only sm:hidden">Tải transcript</span>
            </Button>
            <Button
              variant="outline"
              size="icon-sm"
              onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
              aria-label="Đổi giao diện sáng/tối"
            >
              <Sun className="dark:hidden" />
              <Moon className="hidden dark:block" />
            </Button>
          </div>
        </header>

        {!chat.hydrated ? (
          <div className="flex-1" />
        ) : isEmpty ? (
          <EmptyState tools={tools} onSend={chat.send} onStop={chat.stop} streaming={chat.streaming} />
        ) : (
          <>
            <MessageList messages={messages} onAnswer={chat.send} onRetry={chat.retry} />
            <div className="shrink-0 px-4 pb-4 sm:px-6">
              <div className="mx-auto w-full max-w-3xl">
                <Composer
                  onSend={chat.send}
                  onStop={chat.stop}
                  streaming={chat.streaming}
                  placeholder="Nhắn tiếp cho agent…"
                />
                <p className="mt-2 text-center text-xs text-muted-foreground">
                  Agent có thể sai. Hãy kiểm tra nguồn trước khi dùng thông tin quan trọng.
                </p>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
