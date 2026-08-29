"use client";

import { useState } from "react";
import { ChevronLeft, ChevronRight, LogIn, LogOut } from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useAttendanceMonth,
  useAttendanceSummary,
  useAttendanceToday,
} from "@/hooks/use-attendance";
import { api, errorMessage } from "@/lib/api";
import { formatDate, formatTime } from "@/lib/format";
import type { AttendanceStatus } from "@/lib/types";
import { useAuth } from "@/store/auth";

const STATUS_VARIANT: Record<
  AttendanceStatus,
  "secondary" | "destructive" | "outline"
> = {
  PRESENT: "secondary",
  HALF_DAY: "outline",
  ABSENT: "destructive",
  ON_LEAVE: "outline",
};

export default function AttendancePage() {
  const user = useAuth((s) => s.user);
  const today = new Date();

  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1);
  const [busy, setBusy] = useState(false);

  const { data: record, loading: todayLoading, refresh: refreshToday } =
    useAttendanceToday();
  const { data: rows, loading: rowsLoading, refresh: refreshRows } =
    useAttendanceMonth(year, month);
  const { data: summary, refresh: refreshSummary } =
    useAttendanceSummary(year, month);

  const checkedIn = Boolean(record?.check_in);
  const checkedOut = Boolean(record?.check_out);

  async function clock(action: "check-in" | "check-out") {
    setBusy(true);
    try {
      await api.post(`/attendance/${action}/`);
      toast.success(action === "check-in" ? "Checked in." : "Checked out.");
      refreshToday();
      refreshRows();
      refreshSummary();
    } catch (error) {
      // "Already checked in today at 09:14", "You are on approved leave
      // today" — the backend says exactly what is wrong.
      toast.error(errorMessage(error));
    } finally {
      setBusy(false);
    }
  }

  function shiftMonth(by: number) {
    const next = new Date(year, month - 1 + by, 1);
    setYear(next.getFullYear());
    setMonth(next.getMonth() + 1);
  }

  if (user && !user.employee) {
    return (
      <Card>
        <CardContent className="p-6 text-sm text-muted-foreground">
          Your account has no employee record, so there is nothing to track.
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Attendance</h1>
        <p className="text-sm text-muted-foreground">
          Check in when you start, check out when you finish.
        </p>
      </div>

      {/* ---- today ---- */}
      <Card>
        <CardContent className="flex flex-wrap items-center justify-between gap-4 p-6">
          {todayLoading ? (
            <Skeleton className="h-12 w-64" />
          ) : (
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">
                {formatDate(new Date().toISOString())}
              </p>
              <p className="text-lg font-medium">
                {checkedIn ? `In at ${formatTime(record!.check_in)}` : "Not checked in"}
                {checkedOut && ` · Out at ${formatTime(record!.check_out)}`}
              </p>
              {checkedOut && (
                <p className="text-xs text-muted-foreground">
                  {record!.work_hours} hours recorded
                </p>
              )}
            </div>
          )}

          {/* One button, three states. There is never a choice to make. */}
          {!todayLoading && (
            <>
              {!checkedIn && (
                <Button disabled={busy} onClick={() => clock("check-in")}>
                  <LogIn className="size-4" />
                  Check in
                </Button>
              )}

              {checkedIn && !checkedOut && (
                <Button
                  variant="outline"
                  disabled={busy}
                  onClick={() => clock("check-out")}
                >
                  <LogOut className="size-4" />
                  Check out
                </Button>
              )}

              {checkedOut && <Badge variant="secondary">Done for today</Badge>}
            </>
          )}
        </CardContent>
      </Card>

      {/* ---- month ---- */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => shiftMonth(-1)}>
            <ChevronLeft className="size-4" />
          </Button>
          <p className="min-w-40 text-center text-sm font-medium">
            {new Date(year, month - 1).toLocaleDateString("en-GB", {
              month: "long",
              year: "numeric",
            })}
          </p>
          <Button variant="outline" size="sm" onClick={() => shiftMonth(1)}>
            <ChevronRight className="size-4" />
          </Button>
        </div>

        {summary && (
          <p className="text-sm text-muted-foreground">
            {summary.present} present · {summary.half_day} half · {summary.absent} absent ·{" "}
            {summary.total_hours} hours
          </p>
        )}
      </div>

      <Card>
        <CardContent className="space-y-3 p-6">
          {rowsLoading &&
            Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}

          {!rowsLoading && rows.length === 0 && (
            <p className="py-6 text-center text-sm text-muted-foreground">
              No records this month.
            </p>
          )}

          {!rowsLoading &&
            rows.map((row) => (
              <div
                key={row.id}
                className="flex items-center justify-between gap-3 border-b pb-3 last:border-0 last:pb-0"
              >
                <div>
                  <p className="text-sm font-medium">{formatDate(row.date)}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatTime(row.check_in)} – {formatTime(row.check_out)}
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  <span className="text-sm tabular-nums">{row.work_hours}h</span>
                  <Badge variant={STATUS_VARIANT[row.status]}>
                    {row.status_display}
                  </Badge>
                </div>
              </div>
            ))}
        </CardContent>
      </Card>
    </div>
  );
}
