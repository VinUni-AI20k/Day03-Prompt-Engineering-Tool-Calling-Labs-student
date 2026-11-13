"use client";

import { MessageCircleQuestionMark, ShieldQuestionMark } from "lucide-react";
import { useState } from "react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogMedia,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import type { Ask } from "@/lib/types";

type Props = { ask: Ask; onAnswer: (text: string) => void };

/** Renders the agent's clarify() question as something the user can answer in one tap. */
export function AskControls({ ask, onAnswer }: Props) {
  const [dialogOpen, setDialogOpen] = useState(ask.response_type === "yes_no");

  if (ask.response_type === "yes_no") {
    const answer = (text: string) => {
      setDialogOpen(false);
      onAnswer(text);
    };
    return (
      <>
        <div className="rise-in mt-3 rounded-[12px] border border-primary/30 bg-accent/60 p-4">
          <p className="mb-3 flex items-center gap-2 text-sm font-medium">
            <ShieldQuestionMark className="size-4 text-primary" aria-hidden />
            Cần bạn xác nhận
          </p>
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => answer("Có, đồng ý.")}>Đồng ý</Button>
            <Button variant="outline" onClick={() => answer("Không, hủy.")}>
              Không, hủy
            </Button>
          </div>
        </div>

        <AlertDialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogMedia className="bg-accent text-accent-foreground">
                <ShieldQuestionMark />
              </AlertDialogMedia>
              <AlertDialogTitle>Xác nhận trước khi thực hiện</AlertDialogTitle>
              <AlertDialogDescription>{ask.question}</AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <Button variant="outline" onClick={() => answer("Không, hủy.")}>
                Không, hủy
              </Button>
              <AlertDialogAction onClick={() => answer("Có, đồng ý.")}>Đồng ý</AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </>
    );
  }

  if (ask.response_type === "choice" && ask.options.length > 0) {
    return (
      <div className="rise-in mt-3 flex flex-wrap gap-2" role="group" aria-label="Chọn một đáp án">
        {ask.options.map((option) => (
          <Button key={option} variant="outline" onClick={() => onAnswer(option)}>
            {option}
          </Button>
        ))}
      </div>
    );
  }

  return (
    <p className="rise-in mt-3 flex items-center gap-2 text-sm text-muted-foreground">
      <MessageCircleQuestionMark className="size-4 text-primary" aria-hidden />
      Nhập câu trả lời vào ô bên dưới để agent làm tiếp.
    </p>
  );
}
