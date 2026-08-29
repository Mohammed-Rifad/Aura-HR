"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { DepartmentCount } from "@/lib/types";

// One hue, one step. Bar LENGTH carries the magnitude, so shading each bar by
// its value would encode the same thing twice — and with six near-equal
// departments it would exaggerate differences that are one or two people wide.
// Both steps validated against their surface (light #fcfcfb, dark #1a1a19).
const BAR = "bg-[#256abf] dark:bg-[#3987e5]";

export function HeadcountChart({
  data,
  loading,
}: {
  data: DepartmentCount[];
  loading?: boolean;
}) {
  const total = data.reduce((sum, row) => sum + row.count, 0);
  const largest = Math.max(...data.map((row) => row.count), 1);

  return (
    <Card>
      <CardHeader>
        {/* One series, so no legend — the title says what the bars are. */}
        <CardTitle className="text-base">People by department</CardTitle>
        <CardDescription>
          {loading
            ? "Loading…"
            : `${total} active across ${data.length} departments`}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-3">
        {loading &&
          Array.from({ length: 6 }).map((_, index) => (
            <Skeleton key={index} className="h-5 w-full" />
          ))}

        {!loading && data.length === 0 && (
          <p className="text-sm text-muted-foreground">
            No departments to show.
          </p>
        )}

        {!loading &&
          data.map((row) => {
            const share = total ? Math.round((row.count / total) * 100) : 0;

            return (
              <div
                key={row.code}
                className="grid grid-cols-[7.5rem_1fr_4.5rem] items-center gap-3"
              >
                <span
                  className="truncate text-sm text-muted-foreground"
                  title={row.name}
                >
                  {row.name}
                </span>

                {/* 20px bar — under the 24px cap, so the row keeps some air.
                    Rounded at the data end, square at the baseline. */}
                <div className="h-5">
                  <div
                    className={`h-full rounded-r-[4px] ${BAR}`}
                    style={{ width: `${(row.count / largest) * 100}%` }}
                  />
                </div>

                {/* Value at the tip, in a text token — text never wears the
                    data colour. tabular-nums here because it IS a column that
                    must align; the big stat-card numbers deliberately don't. */}
                <span className="text-sm tabular-nums">
                  {row.count}
                  <span className="ml-1.5 text-xs text-muted-foreground">
                    {share}%
                  </span>
                </span>
              </div>
            );
          })}
      </CardContent>
    </Card>
  );
}
