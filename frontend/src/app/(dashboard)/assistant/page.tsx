"use client";

import { useEffect, useRef, useState } from "react";
import { Send, Sparkles } from "lucide-react";

import { ApprovalCard } from "@/components/assistant/approval-card";
import { ToolTrace } from "@/components/assistant/tool-trace";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useChat } from "@/hooks/use-chat";
import { cn } from "@/lib/utils";

const EXAMPLES = [
  "How many people work in Engineering?",
  "How much annual leave can I carry into next year?",
  "What notice do I have to give if I resign?",
  "Show me pending leave requests",
];

export default function AssistantPage() {
  const { turns, busy, send, decide, reset } = useChat();
  const [draft, setDraft] = useState("");
  const bottom = useRef<HTMLDivElement>(null);

  // Follow the conversation down as it grows.
  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns]);

  function submit(event: React.FormEvent) {
    event.preventDefault();
    const question = draft.trim();
    if (!question || busy) return;
    setDraft("");
    send(question);
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-6.5rem)] max-w-3xl flex-col">
      <div className="mb-4 flex shrink-0 items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Assistant</h1>
          <p className="text-sm text-muted-foreground">
            It can only see what you can see.
          </p>
        </div>

        {turns.length > 0 && (
          <Button variant="outline" size="sm" onClick={reset}>
            New chat
          </Button>
        )}
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto pr-1">
        {turns.length === 0 && (
          <div className="space-y-4 pt-10 text-center">
            <Sparkles className="mx-auto size-8 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">
              Ask about people, leave, attendance or company policy.
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {EXAMPLES.map((example) => (
                <button
                  key={example}
                  type="button"
                  onClick={() => send(example)}
                  className="rounded-full border px-3 py-1.5 text-xs text-muted-foreground transition-colors hover:bg-muted"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        )}

        {turns.map((turn) => (
          <div
            key={turn.id}
            className={cn(
              "flex",
              turn.role === "user" ? "justify-end" : "justify-start",
            )}
          >
            <div
              className={cn(
                "max-w-[85%] rounded-2xl px-4 py-2.5 text-sm",
                turn.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "border bg-card",
              )}
            >
              {turn.role === "model" && <ToolTrace tools={turn.tools} />}

              {/* whitespace-pre-wrap keeps the model's paragraph breaks. */}
              <p className="whitespace-pre-wrap">{turn.text}</p>

              {/* Empty text on a model turn means it is still working. */}
              {turn.role === "model" && !turn.text && busy && (
                <span className="animate-pulse text-muted-foreground">
                  Thinking…
                </span>
              )}

              {turn.action && (
                <ApprovalCard action={turn.action} onDecide={decide} />
              )}
            </div>
          </div>
        ))}

        <div ref={bottom} />
      </div>

      <form onSubmit={submit} className="mt-4 flex shrink-0 gap-2">
        <Input
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Ask about people, leave or policy…"
          disabled={busy}
          className="h-10"
        />
        <Button type="submit" size="icon" className="size-10" disabled={busy}>
          <Send className="size-4" />
        </Button>
      </form>
    </div>
  );
}
