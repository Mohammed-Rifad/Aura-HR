"use client";

import { useMemo, useState } from "react";
import { Check, X } from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { usePendingApprovals } from "@/hooks/use-leave";
import { api, errorMessage } from "@/lib/api";
import { formatDate } from "@/lib/format";
import type { LeaveRequestListItem } from "@/lib/types";
import { useAuth } from "@/store/auth";

export default function ApprovalsPage() {
  const user = useAuth((s) => s.user);
  const { data, loading, error, refresh } = usePendingApprovals();

  const [acting, setActing] = useState<string | null>(null);
  const [rejecting, setRejecting] = useState<LeaveRequestListItem | null>(null);
  const [note, setNote] = useState("");

  // Your own request appears in the list, because the list only filters by
  // status. But nobody decides their own request, so acting on it would be
  // refused. Hide it — this inbox is "things I can act on".
  const actionable = useMemo(
    () => data.filter((r) => r.employee_code !== user?.employee?.employee_id),
    [data, user],
  );

  async function decide(
    request: LeaveRequestListItem,
    action: "approve" | "reject",
    decisionNote = "",
  ) {
    setActing(request.id);
    try {
      await api.post(`/leave/requests/${request.id}/${action}/`, {
        note: decisionNote,
      });
      toast.success(
        action === "approve"
          ? `Approved ${request.employee_name}'s leave.`
          : `Rejected ${request.employee_name}'s leave.`,
      );
      refresh();
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setActing(null);
      setRejecting(null);
      setNote("");
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Approvals</h1>
        <p className="text-sm text-muted-foreground">
          {loading
            ? "Loading…"
            : `${actionable.length} request${actionable.length === 1 ? "" : "s"} waiting on you`}
        </p>
      </div>

      <Card>
        <CardContent className="space-y-3 p-6">
          {error && <p className="text-sm text-destructive">{error}</p>}

          {loading &&
            Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-14 w-full" />
            ))}

          {!loading && actionable.length === 0 && (
            <p className="py-6 text-center text-sm text-muted-foreground">
              Nothing waiting on you.
            </p>
          )}

          {!loading &&
            actionable.map((request) => (
              <div
                key={request.id}
                className="flex flex-wrap items-center justify-between gap-3 border-b pb-3 last:border-0 last:pb-0"
              >
                <div className="min-w-0">
                  <p className="text-sm font-medium">{request.employee_name}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatDate(request.start_date)} –{" "}
                    {formatDate(request.end_date)} · {request.days} days ·{" "}
                    {request.leave_type_code}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="font-mono text-xs">
                    {request.employee_code}
                  </Badge>

                  <Button
                    size="sm"
                    variant="outline"
                    disabled={acting === request.id}
                    onClick={() => {
                      setRejecting(request);
                      setNote("");
                    }}
                    loading={acting === request.id}

                  >
                    <X className="size-4" />
                    Reject
                  </Button>

                  <Button
                    size="sm"
                    disabled={acting === request.id}
                    onClick={() => decide(request, "approve")}
                    loading={acting === request.id}

                  >
                    <Check className="size-4" />
                    Approve
                  </Button>
                </div>
              </div>
            ))}
        </CardContent>
      </Card>

      {/* Rejecting asks for a reason. Approving does not — a "yes" needs no
          explanation, a "no" does. */}
      <Dialog
        open={rejecting !== null}
        onOpenChange={(open) => !open && setRejecting(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject this request</DialogTitle>
            <DialogDescription>
              {rejecting &&
                `${rejecting.employee_name} · ${formatDate(rejecting.start_date)} – ${formatDate(rejecting.end_date)}`}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-2">
            <Label>Reason</Label>
            <Input
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="Not enough cover that week"
            />
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setRejecting(null)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              disabled={acting !== null}
              onClick={() => rejecting && decide(rejecting, "reject", note)}
            >
              Reject
            </Button>
          </DialogFooter>
        </DialogContent> 
      </Dialog>
    </div>
  );
}
