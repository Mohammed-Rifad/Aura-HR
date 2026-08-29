"use client";

import { Fragment, useEffect, useMemo, useState } from "react";
import { ChevronDown, ChevronRight, Search } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAuditLog, useAuditModels } from "@/hooks/use-audit";
import { useDebounced } from "@/hooks/use-debounce";
import { formatDateTime } from "@/lib/format";
import type { AuditAction } from "@/lib/types";

const ALL = "all";

const ACTION_ITEMS = {
  [ALL]: "All actions",
  CREATE: "Create",
  UPDATE: "Update",
  DELETE: "Delete",
  APPROVE: "Approve",
  REJECT: "Reject",
  CANCEL: "Cancel",
  LOGIN: "Login",
};

// Words carry the meaning; colour is a second signal, never the only one.
const ACTION_VARIANT: Record<AuditAction, "secondary" | "destructive" | "outline"> = {
  CREATE: "secondary",
  UPDATE: "outline",
  DELETE: "destructive",
  APPROVE: "secondary",
  REJECT: "destructive",
  CANCEL: "outline",
  LOGIN: "outline",
};

export default function AuditPage() {
  const [searchInput, setSearchInput] = useState("");
  const [action, setAction] = useState(ALL);
  const [model, setModel] = useState(ALL);
  const [page, setPage] = useState(1);
  const [open, setOpen] = useState<string | null>(null);

  const search = useDebounced(searchInput);
  const models = useAuditModels();

  const modelItems = useMemo(
    () => ({
      [ALL]: "All records",
      ...Object.fromEntries(models.map((name) => [name, name])),
    }),
    [models],
  );

  // Any filter change puts you back on page 1, or you sit on page 5 of a
  // result set that now has one page and see nothing.
  useEffect(() => {
    setPage(1);
  }, [search, action, model]);

  const { data, loading, error } = useAuditLog({
    search,
    action: action === ALL ? "" : action,
    model: model === ALL ? "" : model,
    page,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Audit log</h1>
        <p className="text-sm text-muted-foreground">
          {loading ? "Loading…" : `${data?.count ?? 0} recorded changes`}
        </p>
      </div>

      <div className="flex flex-wrap gap-3">
        <div className="relative min-w-56 flex-1">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search by who, or what was changed"
            className="pl-9"
          />
        </div>

        <Select
          items={ACTION_ITEMS}
          value={action}
          onValueChange={(v) => setAction(String(v))}
        >
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Action" />
          </SelectTrigger>
          <SelectContent>
            {Object.entries(ACTION_ITEMS).map(([value, label]) => (
              <SelectItem key={value} value={value}>
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          items={modelItems}
          value={model}
          onValueChange={(v) => setModel(String(v))}
        >
          <SelectTrigger className="w-44">
            <SelectValue placeholder="Record type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ALL}>All records</SelectItem>
            {models.map((name) => (
              <SelectItem key={name} value={name}>
                {name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <Card>
        <CardContent className="p-0">
          {error && <p className="p-6 text-sm text-destructive">{error}</p>}

          {loading && (
            <div className="space-y-2 p-6">
              {Array.from({ length: 8 }).map((_, index) => (
                <Skeleton key={index} className="h-8 w-full" />
              ))}
            </div>
          )}

          {!loading && !error && data?.results.length === 0 && (
            <p className="p-6 text-sm text-muted-foreground">
              Nothing matches those filters.
            </p>
          )}

          {!loading && !error && (data?.results.length ?? 0) > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-8" />
                  <TableHead>When</TableHead>
                  <TableHead>Who</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>Record</TableHead>
                  <TableHead>Changed</TableHead>
                  <TableHead>From</TableHead>
                </TableRow>
              </TableHeader>

              <TableBody>
                {data!.results.map((entry) => {
                  const fields = Object.keys(entry.changes ?? {});
                  const expanded = open === entry.id;

                  return (
                    // Fragment, because one log entry can render two rows —
                    // the summary and its expanded diff.
                    <Fragment key={entry.id}>
                      <TableRow
                        className="cursor-pointer"
                        onClick={() => setOpen(expanded ? null : entry.id)}
                      >
                        <TableCell>
                          {fields.length > 0 &&
                            (expanded ? (
                              <ChevronDown className="size-4 text-muted-foreground" />
                            ) : (
                              <ChevronRight className="size-4 text-muted-foreground" />
                            ))}
                        </TableCell>
                        <TableCell className="whitespace-nowrap text-muted-foreground">
                          {formatDateTime(entry.created_at)}
                        </TableCell>
                        <TableCell>{entry.actor_label || "system"}</TableCell>
                        <TableCell>
                          <Badge variant={ACTION_VARIANT[entry.action]}>
                            {entry.action_display}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <span className="text-muted-foreground">
                            {entry.model_name}
                          </span>{" "}
                          {entry.object_label}
                        </TableCell>
                        <TableCell className="text-muted-foreground">
                          {fields.length === 0
                            ? "—"
                            : fields.length === 1
                              ? fields[0]
                              : `${fields.length} fields`}
                        </TableCell>
                        <TableCell className="font-mono text-xs text-muted-foreground">
                          {entry.ip_address ?? "—"}
                        </TableCell>
                      </TableRow>

                      {expanded && fields.length > 0 && (
                        <TableRow>
                          <TableCell colSpan={7} className="bg-muted/40">
                            <dl className="space-y-1 py-1 text-sm">
                              {fields.map((field) => (
                                <div key={field} className="flex gap-2">
                                  <dt className="w-40 shrink-0 text-muted-foreground">
                                    {field}
                                  </dt>
                                  <dd className="min-w-0">
                                    <span className="text-muted-foreground line-through">
                                      {entry.changes[field].before ?? "empty"}
                                    </span>
                                    {" → "}
                                    <span className="font-medium">
                                      {entry.changes[field].after ?? "empty"}
                                    </span>
                                  </dd>
                                </div>
                              ))}
                            </dl>
                          </TableCell>
                        </TableRow>
                      )}
                    </Fragment>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {(data?.total_pages ?? 1) > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Page {data!.page} of {data!.total_pages}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= (data?.total_pages ?? 1)}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
