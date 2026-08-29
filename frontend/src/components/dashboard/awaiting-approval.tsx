import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDate } from "@/lib/format";
import type { AwaitingApproval } from "@/lib/types";

export function AwaitingApprovalList({
  data,
  loading,
}: {
  data: AwaitingApproval[];
  loading?: boolean;
}) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div>
            <CardTitle className="text-base">Awaiting your approval</CardTitle>
            <CardDescription>Leave requests you can decide</CardDescription>
          </div>

          {/* A card that says "you have work to do" should be a door.
              Hidden when there is nothing to act on. */}
          {!loading && data.length > 0 && (
            <Link
              href="/approvals"
              className="inline-flex shrink-0 items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
            >
              Open
              <ArrowRight className="size-4" />
            </Link>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {loading &&
          Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="h-10 w-full" />
          ))}

        {!loading && data.length === 0 && (
          <p className="text-sm text-muted-foreground">
            Nothing waiting on you.
          </p>
        )}

        {!loading &&
          data.map((request) => (
            <Link
              key={request.id}
              href="/approvals"
              className="-mx-2 flex items-center justify-between gap-3 rounded-md border-b px-2 py-2 transition-colors last:border-0 hover:bg-muted/50"
            >
              <div className="min-w-0">
                <p className="truncate text-sm font-medium">
                  {request.employee_name}
                </p>
                <p className="text-xs text-muted-foreground">
                  {formatDate(request.start_date)} –{" "}
                  {formatDate(request.end_date)}
                </p>
              </div>

              <Badge variant="secondary" className="shrink-0">
                {request.days} days · {request.leave_type}
              </Badge>
            </Link>
          ))}
      </CardContent>
    </Card>
  );
}
