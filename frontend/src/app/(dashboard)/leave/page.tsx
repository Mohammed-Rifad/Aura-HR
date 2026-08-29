"use client";

import { CalendarDays } from "lucide-react";
import { useState } from "react";
import { Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { ApplyLeaveDialog } from "@/components/leave/apply-leave-dialog";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useLeaveBalances, useMyLeaveRequests } from "@/hooks/use-leave";
import { formatDate } from "@/lib/format";
import type { LeaveStatus } from "@/lib/types";
import { useAuth } from "@/store/auth";

// Words carry the state. The colour is a second signal, never the only one.
const STATUS_VARIANT: Record<
  LeaveStatus,
  "secondary" | "destructive" | "outline"
> = {
  APPROVED: "secondary",
  REJECTED: "destructive",
  PENDING: "outline",
  CANCELLED: "outline",
};

export default function LeavePage() {
  const user = useAuth((s) => s.user);
  const employeeId = user?.employee?.id;

  const [applyOpen, setApplyOpen] = useState(false);

  const {
    data: balances,
    loading: balancesLoading,
    refresh: refreshBalances,
  } = useLeaveBalances(employeeId);
  const {
    data: requests,
    loading: requestsLoading,
    refresh: refreshRequests,
  } = useMyLeaveRequests(employeeId);

  // HR and Admin accounts may have no employee record at all.
  if (user && !employeeId) {
    return (
      <Card>
        <CardContent className="p-6 text-sm text-muted-foreground">
          Your account has no employee record, so you have no leave balance.
        </CardContent>
      </Card>
    );
  }

    return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">My leave</h1>
          <p className="text-sm text-muted-foreground">
            Your balance and your requests.
          </p>
        </div>

        <Button onClick={() => setApplyOpen(true)}>
          <Plus className="size-4" />
          Apply for leave
        </Button>
      </div>

      {/* ---- balances ---- */}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {balancesLoading &&
          Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-28 w-full" />
          ))}

        {!balancesLoading &&
          balances.map((balance) => (
            <Card key={balance.id}>
              <CardContent className="space-y-1 p-5">
                <p className="text-sm text-muted-foreground">
                  {balance.leave_type.name}
                </p>
                <p className="text-3xl font-semibold">{balance.available}</p>
                <p className="text-xs text-muted-foreground">
                  {balance.used} used · {balance.pending} pending ·{" "}
                  {balance.allocated} total
                </p>
              </CardContent>
            </Card>
          ))}
      </div>

      {/* ---- history ---- */}
      <Card>
        <CardContent className="space-y-3 p-6">
          <div className="flex items-center gap-2">
            <CalendarDays className="size-4 text-muted-foreground" />
            <p className="text-sm font-medium">My requests</p>
          </div>

          {requestsLoading &&
            Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}

          {!requestsLoading && requests.length === 0 && (
            <p className="text-sm text-muted-foreground">
              You have not applied for any leave.
            </p>
          )}

          {!requestsLoading &&
            requests.map((request) => (
              <div
                key={request.id}
                className="flex items-center justify-between gap-3 border-b pb-3 last:border-0 last:pb-0"
              >
                <div className="min-w-0">
                  <p className="text-sm font-medium">
                    {formatDate(request.start_date)} –{" "}
                    {formatDate(request.end_date)}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {request.days} days · {request.leave_type_code}
                  </p>
                </div>

                <Badge
                  variant={STATUS_VARIANT[request.status]}
                  className="shrink-0"
                >
                  {request.status_display}
                </Badge>
              </div>
            ))}
        </CardContent>
      </Card>

      <ApplyLeaveDialog
        open={applyOpen}
        onOpenChange={setApplyOpen}
        balances={balances}
        onApplied={() => {
          refreshBalances();
          refreshRequests();
        }}
      />
    </div>
  );
}
