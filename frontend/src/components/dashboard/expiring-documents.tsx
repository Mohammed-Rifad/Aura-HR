import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { expiryLabel, formatDate } from "@/lib/format";
import type { ExpiringDocument } from "@/lib/types";

export function ExpiringDocuments({
  data,
  loading,
}: {
  data: ExpiringDocument[];
  loading?: boolean;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Documents expiring soon</CardTitle>
        <CardDescription>Within 30 days, or already expired</CardDescription>
      </CardHeader>

      <CardContent className="space-y-3">
        {loading &&
          Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="h-10 w-full" />
          ))}

        {!loading && data.length === 0 && (
          <p className="text-sm text-muted-foreground">
            Nothing expiring in the next 30 days.
          </p>
        )}

        {!loading &&
          data.map((document) => (
            <div
              key={document.id}
              className="flex items-center justify-between gap-3 border-b pb-3 last:border-0 last:pb-0"
            >
              <div className="min-w-0">
                <p className="truncate text-sm font-medium">
                  {document.employee_name}
                </p>
                <p className="text-xs text-muted-foreground">
                  {document.document_type} · {formatDate(document.expiry_date)}
                </p>
              </div>

              {/* The words carry the state, not just the colour. */}
              <Badge
                variant={document.days_left < 0 ? "destructive" : "secondary"}
                className="shrink-0"
              >
                {expiryLabel(document.days_left)}
              </Badge>
            </div>
          ))}
      </CardContent>
    </Card>
  );
}
