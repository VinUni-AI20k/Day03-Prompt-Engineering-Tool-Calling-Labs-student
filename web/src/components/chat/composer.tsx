"use client";

import { ArrowUp, Square } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

type Props = {
  onSend: (text: string) => void;
  onStop: () => void;
  streaming: boolean;
  placeholder?: string;
  children?: React.ReactNode;
};

export function Composer({ onSend, onStop, streaming, placeholder = "Hỏi agent bất cứ điều gì…", children }: Props) {
  const [value, setValue] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!streaming) ref.current?.focus();
  }, [streaming]);

  const submit = () => {
    const text = value.trim();
    if (!text || streaming) return;
    onSend(text);
    setValue("");
  };

  return (
    <div>
      <div className="rounded-[12px] border bg-card shadow-sm transition-shadow focus-within:border-ring focus-within:ring-3 focus-within:ring-ring/30">
        <Textarea
          ref={ref}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            // Vietnamese IME (Telex/VNI) uses Enter to commit composition: do not send then.
            if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
              e.preventDefault();
              submit();
            }
          }}
          rows={1}
          maxLength={4000}
          placeholder={placeholder}
          aria-label="Nội dung tin nhắn"
          className="max-h-48 min-h-14 resize-none border-0 bg-transparent px-4 pt-4 pb-2 shadow-none focus-visible:ring-0 dark:bg-transparent"
        />
        <div className="flex items-center justify-between gap-3 px-3 pb-3">
          <p className="hidden pl-1 text-xs text-muted-foreground sm:block">
            <kbd className="font-sans">Enter</kbd> để gửi · <kbd className="font-sans">Shift + Enter</kbd> xuống dòng
          </p>
          <div className="ml-auto">
            {streaming ? (
              <Button variant="outline" size="icon-lg" onClick={onStop} aria-label="Dừng">
                <Square className="fill-current" />
              </Button>
            ) : (
              <Button size="icon-lg" onClick={submit} disabled={!value.trim()} aria-label="Gửi">
                <ArrowUp />
              </Button>
            )}
          </div>
        </div>
      </div>
      {children}
    </div>
  );
}
