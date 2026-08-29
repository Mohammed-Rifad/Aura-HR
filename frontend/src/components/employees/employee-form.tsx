"use client";

import { useMemo } from "react";
import { useRouter } from "next/navigation";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { z } from "zod";
import type { AxiosError } from "axios";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useEmployeeOptions } from "@/hooks/use-employee";
import { useDepartments, useDesignations } from "@/hooks/use-org";
import { api, errorMessage } from "@/lib/api";
import type { ApiError, EmployeeDetail } from "@/lib/types";

const NONE = "none";

// Static value -> label maps. Base UI's SelectValue shows the raw value
// unless the Select is given this mapping.
const EMPLOYMENT_ITEMS = {
  FULL_TIME: "Full time",
  PART_TIME: "Part time",
  CONTRACT: "Contract",
  INTERN: "Intern",
};

const STATUS_ITEMS = {
  ACTIVE: "Active",
  ON_NOTICE: "On notice",
  EXITED: "Exited",
};

// The shape of a valid form. Zod checks it in the browser before anything
// is sent; the backend checks it again, because the browser can be bypassed.
const schema = z.object({
  email: z.email("Enter a valid email address").or(z.literal("")),
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  phone: z.string().optional(),

  department: z.string().min(1, "Pick a department"),
  designation: z.string().min(1, "Pick a job title"),
  manager: z.string().optional(),

  date_of_joining: z.string().min(1, "A joining date is required"),
  date_of_birth: z.string().optional(),
  employment_type: z.string(),
  status: z.string(),
});

type FormValues = z.infer<typeof schema>;

/** One labelled field with its error message underneath. */
function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      {children}
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}

export function EmployeeForm({ employee }: { employee?: EmployeeDetail }) {
  const router = useRouter();
  const isEdit = Boolean(employee);

  const { data: departments, loading: departmentsLoading } = useDepartments();
  const { data: designations, loading: designationsLoading } = useDesignations();
  const { data: people, loading: peopleLoading } = useEmployeeOptions();

 

  // Base UI shows the raw value in the trigger unless you hand it a
  // value -> label map. Radix read the label off the item's children;
  // Base UI keeps the two separate and wants them spelled out.
  const departmentItems = useMemo(
    () => Object.fromEntries(departments.map((d) => [String(d.id), d.name])),
    [departments],
  );

  const designationItems = useMemo(
    () => Object.fromEntries(designations.map((d) => [String(d.id), d.title])),
    [designations],
  );

  const managerItems = useMemo(
    () => ({
      [NONE]: "No manager",
      ...Object.fromEntries(
        people.map((p) => [p.id, `${p.full_name} · ${p.employee_id}`]),
      ),
    }),
    [people],
  );

  const {
    register,
    control,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      email: "",
      first_name: "",
      last_name: "",
      phone: "",
      department: employee ? String(employee.department.id) : "",
      designation: employee ? String(employee.designation.id) : "",
      manager: employee?.manager ? String(employee.manager.id) : NONE,
      date_of_joining: employee?.date_of_joining ?? "",
      date_of_birth: employee?.date_of_birth ?? "",
      employment_type: employee?.employment_type ?? "FULL_TIME",
      status: employee?.status ?? "ACTIVE",
    },
  });

  async function onSubmit(values: FormValues) {
    // The form holds everything as strings, because that is what inputs and
    // selects give you. The API wants numbers, and empty means "not set".
    const payload: Record<string, unknown> = {
      department: Number(values.department),
      designation: Number(values.designation),
      manager:
        values.manager && values.manager !== NONE ? values.manager : null,
      date_of_joining: values.date_of_joining,
      date_of_birth: values.date_of_birth || null,
      employment_type: values.employment_type,
      status: values.status,
    };

    // Account details only exist on create. The backend ignores them on
    // update anyway, but there is no reason to send them.
    if (!isEdit) {
      payload.email = values.email;
      payload.first_name = values.first_name;
      payload.last_name = values.last_name;
      payload.phone = values.phone;
    }

    try {
      if (isEdit) {
        await api.patch(`/employees/${employee!.id}/`, payload);
        toast.success("Employee updated.");
        router.push(`/employees/${employee!.id}`);
      } else {
        const { data } = await api.post("/employees/", payload);
        toast.success("Employee added. An admin must verify the account.");
        router.push(`/employees/${data.id}`);
      }
    } catch (error) {
      // Your backend returns { errors: { field: ["message"] } }. Putting each
      // message on its own field beats one toast saying "invalid".
      const fields = (error as AxiosError<ApiError>).response?.data?.errors;
      if (fields) {
        Object.entries(fields).forEach(([name, messages]) => {
          setError(name as keyof FormValues, { message: messages[0] });
        });
      }
      toast.error(errorMessage(error));
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {!isEdit && (
        <Card>
          <CardContent className="grid gap-4 p-6 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <p className="text-sm font-medium">Login account</p>
              <p className="text-xs text-muted-foreground">
                Created locked. An admin verifies it before they can sign in.
              </p>
            </div>

            <Field label="Email" error={errors.email?.message}>
              <Input {...register("email")} placeholder="name@aurahr.com" />
            </Field>

            <Field label="Phone" error={errors.phone?.message}>
              <Input {...register("phone")} placeholder="+971…" />
            </Field>

            <Field label="First name" error={errors.first_name?.message}>
              <Input {...register("first_name")} />
            </Field>

            <Field label="Last name" error={errors.last_name?.message}>
              <Input {...register("last_name")} />
            </Field>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="grid gap-4 p-6 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <p className="text-sm font-medium">Job details</p>
          </div>

          <Field label="Department" error={errors.department?.message}>
            {/* Base UI reads the trigger's label out of the `items` map.
                Until the departments arrive that map is empty, so an edit
                form would briefly show the raw id — "3" before
                "Engineering". Don't render a control that cannot yet
                display itself correctly. */}
            {departmentsLoading ? (
              <Skeleton className="h-8 w-full" />
            ) : (
              <Controller
                control={control}
                name="department"
                render={({ field }) => (
                  <Select
                    items={departmentItems}
                    value={field.value}
                    onValueChange={(v) => field.onChange(String(v))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Choose a department" />
                    </SelectTrigger>
                    <SelectContent>
                      {departments.map((d) => (
                        <SelectItem key={d.id} value={String(d.id)}>
                          {d.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              />
            )}
          </Field>

          <Field label="Job title" error={errors.designation?.message}>
            {designationsLoading ? (
              <Skeleton className="h-8 w-full" />
            ) : (
              <Controller
                control={control}
                name="designation"
                render={({ field }) => (
                  <Select
                    items={designationItems}
                    value={field.value}
                    onValueChange={(v) => field.onChange(String(v))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Choose a job title" />
                    </SelectTrigger>
                    <SelectContent>
                      {designations.map((d) => (
                        <SelectItem key={d.id} value={String(d.id)}>
                          {d.title}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              />
            )}
          </Field>

          <Field label="Manager" error={errors.manager?.message}>
            {peopleLoading ? (
              <Skeleton className="h-8 w-full" />
            ) : (
              <Controller
                control={control}
                name="manager"
                render={({ field }) => (
                  <Select
                    items={managerItems}
                    value={field.value}
                    onValueChange={(v) => field.onChange(String(v))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="No manager" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={NONE}>No manager</SelectItem>
                      {people
                        .filter((p) => p.id !== employee?.id)
                        .map((p) => (
                          <SelectItem key={p.id} value={p.id}>
                            {p.full_name} · {p.employee_id}
                          </SelectItem>
                        ))}
                    </SelectContent>
                  </Select>
                )}
              />
            )}
          </Field>

          <Field
            label="Employment type"
            error={errors.employment_type?.message}
          >
            <Controller
              control={control}
              name="employment_type"
              render={({ field }) => (
                <Select
                  items={EMPLOYMENT_ITEMS}
                  value={field.value}
                  onValueChange={(v) => field.onChange(String(v))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(EMPLOYMENT_ITEMS).map(([value, label]) => (
                      <SelectItem key={value} value={value}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            />
          </Field>

          <Field label="Joining date" error={errors.date_of_joining?.message}>
            <Input type="date" {...register("date_of_joining")} />
          </Field>

          <Field label="Date of birth" error={errors.date_of_birth?.message}>
            <Input type="date" {...register("date_of_birth")} />
          </Field>

          {isEdit && (
            <Field label="Status" error={errors.status?.message}>
              <Controller
                control={control}
                name="status"
                render={({ field }) => (
                  <Select
                    items={STATUS_ITEMS}
                    value={field.value}
                    onValueChange={(v) => field.onChange(String(v))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(STATUS_ITEMS).map(([value, label]) => (
                        <SelectItem key={value} value={value}>
                          {label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              />
            </Field>
          )}
        </CardContent>
      </Card>

      <div className="flex gap-3">
        <Button type="submit" loading={isSubmitting}>
          {isSubmitting ? "Saving…" : isEdit ? "Save changes" : "Add employee"}
        </Button>

        <Button type="button" variant="outline" onClick={() => router.back()}>
          Cancel
        </Button>
      </div>
    </form>
  );
}
