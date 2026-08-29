"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
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
import { Plus, Search } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { useDepartments } from "@/hooks/use-org";
import type { EmployeeStatus } from "@/lib/types";
import { useDebounced } from "@/hooks/use-debounce";
import { useEmployees } from "@/hooks/use-employee";
import { useAuth } from "@/store/auth";
// Base UI treats "" as no selection, so "all" is the sentinel and gets
// translated to "" (no filter) before the request goes out.
const ALL = "all";

const STATUS_LABEL: Record<EmployeeStatus, string> = {
  ACTIVE: "Active",
  ON_NOTICE: "On notice",
  EXITED: "Exited",
};

// Base UI shows the raw value in the trigger unless the Select is handed a
// value -> label map. Radix read the label off the item's children; Base UI
// keeps the two separate and wants them spelled out.
const STATUS_ITEMS = {
  [ALL]: "All statuses",
  ...STATUS_LABEL,
};

export default function EmployeesPage() {
  const user = useAuth((s) => s.user);
  
  const { data: departments } = useDepartments();

  const departmentItems = useMemo(
    () => ({
      [ALL]: "All departments",
      ...Object.fromEntries(departments.map((d) => [String(d.id), d.name])),
    }),
    [departments],
  );
  const [searchInput, setSearchInput] = useState("");
  const [department, setDepartment] = useState(ALL);
  const [status, setStatus] = useState(ALL);
  const [page, setPage] = useState(1);

  const search = useDebounced(searchInput);

  // Any filter change puts you back on page 1. Otherwise you can be on
  // page 3 of a result set that now has one page, and see nothing.
  useEffect(() => {
    setPage(1);
  }, [search, department, status]);

  const { data, loading, error } = useEmployees({
    search,
    department: department === ALL ? "" : department,
    status: status === ALL ? "" : status,
    page,
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Employees</h1>
          <p className="text-sm text-muted-foreground">
            {data ? `${data.count} people` : "Loading…"}
          </p>
        </div>

        {(user?.role === "HR" || user?.role === "ADMIN") && (
          <Button nativeButton={false} render={<Link href="/employees/new" />}>
            <Plus className="size-4" />
            Add employee
          </Button>
        )}
      </div>

      {/* Filters in one row above the table. */}
      <div className="flex flex-wrap gap-3">
        <div className="relative min-w-56 flex-1">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search name, email or ID"
            className="pl-9"
          />
        </div>

        <Select
          items={departmentItems}
          value={department}
          onValueChange={(v) => setDepartment(String(v))}
        >
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Department" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ALL}>All departments</SelectItem>
            {departments.map((d) => (
              <SelectItem key={d.id} value={String(d.id)}>
                {d.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          items={STATUS_ITEMS}
          value={status}
          onValueChange={(v) => setStatus(String(v))}
        >
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ALL}>All statuses</SelectItem>
            <SelectItem value="ACTIVE">Active</SelectItem>
            <SelectItem value="ON_NOTICE">On notice</SelectItem>
            <SelectItem value="EXITED">Exited</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Card>
        <CardContent className="p-0">
          {error && <p className="p-6 text-sm text-destructive">{error}</p>}

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Department</TableHead>
                <TableHead>Job title</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>

            <TableBody>
              {loading &&
                Array.from({ length: 8 }).map((_, i) => (
                  <TableRow key={i}>
                    <TableCell colSpan={5}>
                      <Skeleton className="h-5 w-full" />
                    </TableCell>
                  </TableRow>
                ))}

              {!loading && data?.results.length === 0 && (
                <TableRow>
                  <TableCell
                    colSpan={5}
                    className="py-10 text-center text-sm text-muted-foreground"
                  >
                    No one matches those filters.
                  </TableCell>
                </TableRow>
              )}

              {!loading &&
                data?.results.map((employee) => (
                  <TableRow key={employee.id} className="hover:bg-muted/50">
                    <TableCell className="font-mono text-xs tabular-nums">
                      {employee.employee_id}
                    </TableCell>
                    <TableCell>
                      <Link
                        href={`/employees/${employee.id}`}
                        className="font-medium hover:underline"
                      >
                        {employee.full_name}
                      </Link>
                      <p className="text-xs text-muted-foreground">
                        {employee.email}
                      </p>
                    </TableCell>
                    <TableCell className="text-sm">
                      {employee.department_name}
                    </TableCell>
                    <TableCell className="text-sm">
                      {employee.designation_title}
                    </TableCell>
                    <TableCell>
                      {/* The word carries the state — not the colour alone. */}
                      <Badge
                        variant={
                          employee.status === "ACTIVE" ? "secondary" : "outline"
                        }
                      >
                        {STATUS_LABEL[employee.status]}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {data && data.total_pages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Page {data.page} of {data.total_pages}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={!data.previous}
              onClick={() => setPage((p) => p - 1)}
            >
              Previous
            </Button>

            <Button
              variant="outline"
              size="sm"
              disabled={!data.next}
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
