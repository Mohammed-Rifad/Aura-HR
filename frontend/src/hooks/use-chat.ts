"use client";

import { useCallback, useRef, useState } from "react";

import { api, authedFetch, errorMessage } from "@/lib/api";
import type { ChatEvent, ChatTurn } from "@/lib/types";

let counter = 0;
const newId = () => `turn-${counter++}`;

export function useChat() {
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [busy, setBusy] = useState(false);

  // Refs, not state, on purpose. The conversation id arrives mid-stream and
  // is needed by the very next request; state would still hold the old value
  // inside this closure. Same reasoning for the busy guard.
  const conversation = useRef<string | null>(null);
  const sending = useRef(false);

  const send = useCallback(async (question: string) => {
    if (!question.trim() || sending.current) return;
    sending.current = true;
    setBusy(true);

    const answerId = newId();

    // The empty assistant bubble goes up immediately. It is what fills in as
    // events arrive — there is no separate "waiting" state to swap out.
    setTurns((all) => [
      ...all,
      { id: newId(), role: "user", text: question, tools: [] },
      { id: answerId, role: "model", text: "", tools: [] },
    ]);

    const patch = (change: (turn: ChatTurn) => ChatTurn) =>
      setTurns((all) =>
        all.map((turn) => (turn.id === answerId ? change(turn) : turn)),
      );

    function handle(event: ChatEvent) {
      switch (event.type) {
        case "start":
          conversation.current = event.conversation;
          break;

        case "tool":
          patch((turn) => ({
            ...turn,
            tools: [...turn.tools, { name: event.name }],
          }));
          break;

        case "result":
          patch((turn) => {
            const tools = [...turn.tools];
            // The most recent unfinished call of that name. Matching by name
            // alone would tick off the wrong one when a tool is used twice.
            for (let i = tools.length - 1; i >= 0; i--) {
              if (tools[i].name === event.name && tools[i].ok === undefined) {
                tools[i] = { ...tools[i], ok: event.ok };
                break;
              }
            }
            return { ...turn, tools };
          });
          break;

        case "proposal":
          patch((turn) => ({
            ...turn,
            action: {
              id: event.action_id,
              summary: event.summary,
              status: "PENDING",
              is_open: true,
            },
          }));
          break;

        case "answer":
        case "error":
          patch((turn) => ({
            ...turn,
            text: event.type === "answer" ? event.text : event.message,
          }));
          break;
      }
    }

    try {
      const response = await authedFetch("/ai/chat/stream/", {
        method: "POST",
        body: JSON.stringify({
          conversation: conversation.current,
          message: question,
        }),
      });

      if (!response.ok || !response.body) {
        throw new Error(`Stream failed with ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Events are separated by a blank line. Network chunks do NOT line up
        // with event boundaries — one chunk can hold two events, or half of
        // one. Whatever follows the last blank line is incomplete, so it stays
        // in the buffer until the rest arrives.
        const chunks = buffer.split("\n\n");
        buffer = chunks.pop() ?? "";

        for (const chunk of chunks) {
          const line = chunk.trim();
          if (!line.startsWith("data:")) continue;
          handle(JSON.parse(line.slice(5)) as ChatEvent);
        }
      }
    } catch(error) {
        console.error("chat stream failed:", error);
      patch((turn) => ({
        ...turn,
        text: "The assistant is unavailable right now. Please try again.",
      }));
    } finally {
      sending.current = false;
      setBusy(false);
    }
  }, []);

  const decide = useCallback(async (actionId: string, approve: boolean) => {
    try {
      const { data } = await api.post(
        `/ai/actions/${actionId}/${approve ? "approve" : "reject"}/`,
        {},
      );

      setTurns((all) => [
        // Close the card, so the buttons cannot be clicked twice.
        ...all.map((turn) =>
          turn.action?.id === actionId
            ? { ...turn, action: { ...turn.action, ...data.action } }
            : turn,
        ),
        // And say what happened, as its own bubble.
        { id: newId(), role: "model" as const, text: data.answer, tools: [] },
      ]);
    } catch (error) {
      return errorMessage(error);
    }
  }, []);

  const reset = useCallback(() => {
    conversation.current = null;
    setTurns([]);
  }, []);

  return { turns, busy, send, decide, reset };
}
