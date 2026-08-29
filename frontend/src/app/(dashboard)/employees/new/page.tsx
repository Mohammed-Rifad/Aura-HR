"use client";

import { EmployeeForm } from "@/components/employees/employee-form";

export default function NewEmployeePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Add employee</h1>
        <p className="text-sm text-muted-foreground">
          Creates their login and their HR record together.
        </p>
      </div>
      <EmployeeForm />
    </div>
  );
}
