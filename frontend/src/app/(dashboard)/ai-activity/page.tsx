"use client";

import { Activity, RefreshCw, ShieldAlert, ShieldX } from "lucide-react";

import { StatCard } from "@/components/dashboard/stat-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAIActivity } from "@/hooks/use-ai-activity";
import { formatDateTime } from "@/lib/format";
import type { PendingActionStatus } from "@/lib/types";

const STATUS_VARIANT: Record<
  PendingActionStatus,
  "secondary" | "destructive" | "outline"
> = {
  APPROVED: "secondary",
  REJECTED: "destructive",
  FAILED: "destructive",
  PENDING: "outline",
  EXPIRED: "outline",
};

export default function AIActivityPage() {
  const { calls, approvals, summary, loading, refresh } = useAIActivity();

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">AI activity</h1>
          <p className="text-sm text-muted-foreground">
            Everything the assistant ran, and everything it was refused.
          </p>
        </div>

        <Button variant="outline" size="sm" onClick={refresh}>
          <RefreshCw className="size-4" />
          Refresh
        </Button>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard
          label="Tool calls"
          value={summary?.total ?? 0}
          icon={Activity}
          loading={loading}
        />
        <StatCard
          label="Refused"
          value={summary?.refused ?? 0}
          hint="Blocked by scoping or rejected as invalid"
          icon={ShieldX}
          tone="warning"
          loading={loading}
        />
        <StatCard
          label="Awaiting approval"
          value={summary?.awaiting_approval ?? 0}
          hint="Proposed writes nobody has decided"
          icon={ShieldAlert}
          tone="warning"
          loading={loading}
        />
      </div>

      <Tabs defaultValue="calls">
        <TabsList>
          <TabsTrigger value="calls">Tool calls</TabsTrigger>
          <TabsTrigger value="approvals">Proposed writes</TabsTrigger>
        </TabsList>

        {/* ---- tool calls ---- */}
        <TabsContent value="calls">
          <Card>
            <CardContent className="p-0">
              {loading && (
                <div className="space-y-2 p-6">
                  {Array.from({ length: 6 }).map((_, index) => (
                    <Skeleton key={index} className="h-8 w-full" />
                  ))}
                </div>
              )}

              {!loading && calls.length === 0 && (
                <p className="p-6 text-sm text-muted-foreground">
                  The assistant has not run anything yet.
                </p>
              )}

              {!loading && calls.length > 0 && (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>When</TableHead>
                      <TableHead>Who asked</TableHead>
                      <TableHead>Tool</TableHead>
                      <TableHead>Arguments</TableHead>
                      <TableHead>Result</TableHead>
                      <TableHead className="text-right">Took</TableHead>
                    </TableRow>
                  </TableHeader>

                  <TableBody>
                    {calls.map((call) => (
                      <TableRow key={call.id}>
                        <TableCell className="whitespace-nowrap text-muted-foreground">
                          {formatDateTime(call.created_at)}
                        </TableCell>
                        <TableCell>{call.actor_label}</TableCell>
                        <TableCell className="font-mono text-xs">
                          {call.tool_name}
                        </TableCell>
                        <TableCell className="max-w-[22rem] truncate font-mono text-xs text-muted-foreground">
                          {JSON.stringify(call.arguments)}
                        </TableCell>
                        <TableCell>
                          {call.allowed ? (
                            <Badge variant="secondary">ok</Badge>
                          ) : (
                            // The refused rows are the interesting ones —
                            // each is the scoping rules actually firing.
                            <span
                              className="text-xs text-destructive"
                              title={call.error}
                            >
                              refused
                            </span>
                          )}
                        </TableCell>
                        <TableCell className="text-right text-muted-foreground">
                          {call.duration_ms} ms
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ---- proposed writes ---- */}
        <TabsContent value="approvals">
          <Card>
            <CardContent className="p-0">
              {!loading && approvals.length === 0 && (
                <p className="p-6 text-sm text-muted-foreground">
                  The assistant has not proposed any changes.
                </p>
              )}

              {!loading && approvals.length > 0 && (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>When</TableHead>
                      <TableHead>What it wanted to do</TableHead>
                      <TableHead>Asked by</TableHead>
                      <TableHead>Decided by</TableHead>
                      <TableHead>Outcome</TableHead>
                    </TableRow>
                  </TableHeader>

                  <TableBody>
                    {approvals.map((entry) => (
                      <TableRow key={entry.id}>
                        <TableCell className="whitespace-nowrap text-muted-foreground">
                          {formatDateTime(entry.created_at)}
                        </TableCell>
                        <TableCell>{entry.summary}</TableCell>
                        <TableCell className="text-muted-foreground">
                          {entry.requested_by}
                        </TableCell>
                        <TableCell className="text-muted-foreground">
                          {entry.decided_by ?? "—"}
                        </TableCell>
                        <TableCell>
                          <Badge variant={STATUS_VARIANT[entry.status]}>
                            {entry.status}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
