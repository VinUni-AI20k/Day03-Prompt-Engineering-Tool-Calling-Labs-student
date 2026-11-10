"use client";

import { useEffect, useRef } from "react";
import type { Message } from "@/lib/types";
import { AssistantMessageView } from "./assistant-message";

type Props = {
  messages: Message[];
  onAnswer: (text: string) => void;
  onRetry: () => void;
};

export function MessageList({ messages, onAnswer, onRetry }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const stickRef = useRef(true);

  // Follow new content only while the user is near the bottom.
  useEffect(() => {
    if (stickRef.current) endRef.current?.scrollIntoView({ block: "end" });
  });

  return (
    <div
      ref={containerRef}
      onScroll={(e) => {
        const el = e.currentTarget;
        stickRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < 120;
      }}
      className="flex-1 overflow-y-auto"
      role="log"
      aria-live="polite"
      aria-label="Cuộc trò chuyện"
    >
      <div className="mx-auto w-full max-w-3xl space-y-7 px-4 py-8 sm:px-6">
        {messages.map((message, index) =>
          message.role === "user" ? (
            <div key={message.id} className="rise-in flex justify-end">
              <p className="max-w-[85%] rounded-[12px] bg-secondary px-4 py-2.5 text-[0.9375rem] leading-relaxed break-words whitespace-pre-wrap">
                {message.text}
              </p>
            </div>
          ) : (
            <AssistantMessageView
              key={message.id}
              message={message}
              isLast={index === messages.length - 1}
              onAnswer={onAnswer}
              onRetry={onRetry}
            />
          ),
        )}
        <div ref={endRef} />
      </div>
    </div>
  );
}
