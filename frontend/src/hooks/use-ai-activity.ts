"use client";

import { useCallback, useEffect, useState } from "react";

import { api } from "@/lib/api";
import type {
  AIActivitySummary,
  AIToolCall,
  ApprovalLogEntry,
  Paginated,
} from "@/lib/types";

export function useAIActivity() {
  const [calls, setCalls] = useState<AIToolCall[]>([]);
  const [approvals, setApprovals] = useState<ApprovalLogEntry[]>([]);
  const [summary, setSummary] = useState<AIActivitySummary | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(() => {
    setLoading(true);
    // All three at once. They are independent, and three round trips in
    // sequence would triple the wait for no reason.
    Promise.all([
      api.get<Paginated<AIToolCall>>("/ai/activity/"),
      api.get<Paginated<ApprovalLogEntry>>("/ai/approval-log/"),
      api.get<AIActivitySummary>("/ai/activity/summary/"),
    ])
      .then(([activity, approvalLog, stats]) => {
        setCalls(activity.data.results);
        setApprovals(approvalLog.data.results);
        setSummary(stats.data);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { calls, approvals, summary, loading, refresh };
}
