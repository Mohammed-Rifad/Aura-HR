import type { LucideIcon } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

type Tone = "default" | "warning";

export function StatCard({
  label,
  value,
  hint,
  icon: Icon,
  loading = false,
  tone = "default",
}: {
  label: string;
  value: number | string;
  hint?: string;
  icon: LucideIcon;
  loading?: boolean;
  tone?: Tone;
}) {
  return (
    <Card>
      <CardContent className="flex items-start justify-between gap-4 p-5">
        <div className="space-y-1">
          {/* Sentence case, no trailing colon. */}
          <p className="text-sm text-muted-foreground">{label}</p>

          {loading ? (
            <Skeleton className="h-9 w-16" />
          ) : (
            // Proportional figures deliberately — no tabular-nums. Tabular
            // gives every digit the width of a 0, which looks loose at this
            // size. Save it for columns that must align.
            <p className="text-3xl font-semibold">{value}</p>
          )}

          {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
        </div>

        <div
          className={cn(
            "rounded-md p-2",
            tone === "warning"
              ? "bg-amber-500/10 text-amber-600 dark:text-amber-500"
              : "bg-primary/10 text-primary",
          )}
        >
          <Icon className="size-5" />
        </div>
      </CardContent>
    </Card>
  );
}
