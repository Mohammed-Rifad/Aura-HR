"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/store/auth";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { useEmployee, useEmployeeLeave } from "@/hooks/use-employee";
import { expiryLabel, formatDate } from "@/lib/format";

/** One label-and-value row. Used all over the profile tab. */
function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="space-y-1">
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className="text-sm">{value ?? "—"}</dd>
    </div>
  );
}

export default function EmployeeProfilePage() {
  const { id } = useParams<{ id: string }>();
  const { data: employee, loading, error } = useEmployee(id);
  const { data: leave } = useEmployeeLeave(id);
  const user = useAuth((s) => s.user);

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (error || !employee) {
    return (
      <Card>
        <CardContent className="space-y-3 p-6">
          <p className="text-sm text-destructive">
            {error ?? "Employee not found."}
          </p>
          <Link href="/employees" className="text-sm underline">
            Back to employees
          </Link>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Link
        href="/employees"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="size-4" />
        Employees
      </Link>

             <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-2xl font-semibold tracking-tight">
          {employee.user.full_name}
        </h1>
        <Badge variant="outline" className="font-mono">
          {employee.employee_id}
        </Badge>
        <Badge variant={employee.status === "ACTIVE" ? "secondary" : "outline"}>
          {employee.status.replace("_", " ").toLowerCase()}
        </Badge>

        {/* ---- add this ---- */}
        {(user?.role === "HR" || user?.role === "ADMIN") && (
          <Button
            variant="outline"
            size="sm"
            className="ml-auto"
            render={<Link href={`/employees/${employee.id}/edit`} />}
          >
            Edit
          </Button>
        )}
      </div>


      <Tabs defaultValue="profile">
        <TabsList>
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="documents">
            Documents ({employee.documents.length})
          </TabsTrigger>
          <TabsTrigger value="leave">Leave ({leave.length})</TabsTrigger>
        </TabsList>

        {/* ---- Profile ---- */}
        <TabsContent value="profile">
          <Card>
            <CardContent className="grid gap-6 p-6 sm:grid-cols-2 lg:grid-cols-3">
              <Field label="Email" value={employee.user.email} />
              <Field label="Phone" value={employee.user.phone || "—"} />
              <Field label="Role" value={employee.user.role} />
              <Field label="Department" value={employee.department.name} />
              <Field label="Job title" value={employee.designation.title} />
              <Field
                label="Manager"
                value={employee.manager?.full_name ?? "No manager"}
              />
              <Field
                label="Joined"
                value={formatDate(employee.date_of_joining)}
              />
              <Field
                label="Date of birth"
                value={
                  employee.date_of_birth
                    ? formatDate(employee.date_of_birth)
                    : "—"
                }
              />
              <Field
                label="Employment type"
                value={employee.employment_type.replace("_", " ").toLowerCase()}
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* ---- Documents ---- */}
        <TabsContent value="documents">
          <Card>
            <CardContent className="space-y-3 p-6">
              {employee.documents.length === 0 && (
                <p className="text-sm text-muted-foreground">
                  No documents uploaded.
                </p>
              )}

              {employee.documents.map((document) => {
                const daysLeft = document.expiry_date
                  ? Math.round(
                      (new Date(document.expiry_date).getTime() - Date.now()) /
                        86400000,
                    )
                  : null;

                return (
                  <div
                    key={document.id}
                    className="flex items-center justify-between gap-3 border-b pb-3 last:border-0 last:pb-0"
                  >
                    <div className="min-w-0">
                      <p className="text-sm font-medium">
                        {document.document_type_display}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {document.document_number || "No number"}
                        {document.expiry_date &&
                          ` · expires ${formatDate(document.expiry_date)}`}
                      </p>
                    </div>

                    {daysLeft !== null && document.is_expiring_soon && (
                      <Badge
                        variant={daysLeft < 0 ? "destructive" : "secondary"}
                        className="shrink-0"
                      >
                        {expiryLabel(daysLeft)}
                      </Badge>
                    )}
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ---- Leave ---- */}
        <TabsContent value="leave">
          <Card>
            <CardContent className="space-y-3 p-6">
              {leave.length === 0 && (
                <p className="text-sm text-muted-foreground">
                  No leave requests.
                </p>
              )}

              {leave.map((request) => (
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
                    variant={
                      request.status === "APPROVED"
                        ? "secondary"
                        : request.status === "REJECTED"
                          ? "destructive"
                          : "outline"
                    }
                    className="shrink-0"
                  >
                    {request.status_display}
                  </Badge>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
