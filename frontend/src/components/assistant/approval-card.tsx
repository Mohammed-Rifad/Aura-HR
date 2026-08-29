"use client";

import { useState } from "react";
import { ShieldAlert } from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { PendingAction } from "@/lib/types";

export function ApprovalCard({
  action,
  onDecide,
}: {
  action: PendingAction;
  onDecide: (id: string, approve: boolean) => Promise<string | undefined>;
}) {
  const [busy, setBusy] = useState<"approve" | "reject" | null>(null);

  async function decide(approve: boolean) {
    setBusy(approve ? "approve" : "reject");
    const error = await onDecide(action.id, approve);
    if (error) toast.error(error);
    setBusy(null);
  }

  return (
    <div className="mt-3 rounded-lg border border-amber-300 bg-amber-50 p-4 dark:border-amber-900 dark:bg-amber-950/30">
      <div className="flex items-start gap-2">
        <ShieldAlert className="mt-0.5 size-4 shrink-0 text-amber-600 dark:text-amber-500" />

        <div className="min-w-0 flex-1 space-y-3">
          <div>
            <p className="text-xs font-medium text-amber-700 dark:text-amber-500">
              Needs your approval — nothing has happened yet
            </p>
            <p className="mt-1 text-sm">{action.summary}</p>
          </div>

          {action.is_open ? (
            <div className="flex gap-2">
             <Button size="sm" onClick={() => decide(true)} loading={busy === "approve"} disabled={busy !== null}>

                {busy === "approve" ? "Approving…" : "Approve"}
              </Button>
             <Button size="sm" onClick={() => decide(false)} loading={busy === "approve"} disabled={busy !== null}>

                {busy === "reject" ? "Cancelling…" : "Reject"}
              </Button>
            </div>
          ) : (
            // Once decided the buttons are gone, not disabled. A disabled
            // button still looks like an offer.
            <Badge
              variant={action.status === "APPROVED" ? "secondary" : "destructive"}
            >
              {action.status}
            </Badge>
          )}
        </div>
      </div>
    </div>
  );
}
