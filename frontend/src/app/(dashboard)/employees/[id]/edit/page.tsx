"use client";

import { useParams } from "next/navigation";

import { EmployeeForm } from "@/components/employees/employee-form";
import { Skeleton } from "@/components/ui/skeleton";
import { useEmployee } from "@/hooks/use-employee";

export default function EditEmployeePage() {
  const { id } = useParams<{ id: string }>();
  const { data, loading } = useEmployee(id);

  if (loading) return <Skeleton className="h-96 w-full" />;
  if (!data) return <p className="text-sm text-destructive">Not found.</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">
        Edit {data.user.full_name}
      </h1>
      <EmployeeForm employee={data} />
    </div>
  );
}
