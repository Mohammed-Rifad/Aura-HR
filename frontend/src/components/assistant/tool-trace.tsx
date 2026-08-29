"use client";

import { Check, Loader2, X } from "lucide-react";

import type { ChatTurn } from "@/lib/types";

// Tool names are for the model. People get sentences.
const LABELS: Record<string, string> = {
  search_employees: "Searching the directory",
  get_employee_details: "Reading an employee record",
  get_leave_balance: "Checking leave balance",
  get_leave_requests: "Reading leave requests",
  get_attendance_summary: "Checking attendance",
  get_expiring_documents: "Checking expiring documents",
  headcount_analytics: "Running headcount numbers",
  search_policies: "Searching company documents",
  approve_leave_request: "Preparing an approval",
  reject_leave_request: "Preparing a rejection",
};

export function ToolTrace({ tools }: { tools: ChatTurn["tools"] }) {
  if (tools.length === 0) return null;

  return (
    <ul className="mb-2 space-y-1">
      {tools.map((tool, index) => (
        <li
          key={`${tool.name}-${index}`}
          className="flex items-center gap-2 text-xs text-muted-foreground"
        >
          {/* ok is undefined while the tool is still running — that is the
              spinner state, and it is why ok is optional in the type. */}
          {tool.ok === undefined && (
            <Loader2 className="size-3 shrink-0 animate-spin" />
          )}
          {tool.ok === true && <Check className="size-3 shrink-0" />}
          {tool.ok === false && (
            <X className="size-3 shrink-0 text-destructive" />
          )}

          <span>{LABELS[tool.name] ?? tool.name}</span>
        </li>
      ))}
    </ul>
  );
}
