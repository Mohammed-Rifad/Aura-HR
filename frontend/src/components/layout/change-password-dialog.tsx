"use client";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { z } from "zod";
import type { AxiosError } from "axios";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api, errorMessage } from "@/lib/api";
import type { ApiError } from "@/lib/types";
import { useAuth } from "@/store/auth";

const schema = z
  .object({
    old_password: z.string().min(1, "Enter your current password"),
    new_password: z.string().min(8, "Use at least 8 characters"),
    confirm: z.string().min(1, "Type it again"),
  })
  .refine((values) => values.new_password === values.confirm, {
    message: "The two passwords do not match",
    path: ["confirm"],
  });

type FormValues = z.infer<typeof schema>;

export function ChangePasswordDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const router = useRouter();
  const logout = useAuth((s) => s.logout);

  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  async function onSubmit(values: FormValues) {
    try {
      await api.post("/auth/change-password/", {
        old_password: values.old_password,
        new_password: values.new_password,
      });

      reset();
      onOpenChange(false);
      toast.success("Password changed. Please sign in again.");

      // CHECK_REVOKE_TOKEN is on in SIMPLE_JWT, so the token you are holding
      // stopped being valid the moment the password changed. Signing out
      // here is not a precaution — the next request would 401 anyway, and
      // this way the user is told why.
      await logout();
      router.replace("/login");
    } catch (error) {
      const fields = (error as AxiosError<ApiError>).response?.data?.errors;
      if (fields) {
        Object.entries(fields).forEach(([name, messages]) => {
          if (name === "old_password" || name === "new_password") {
            setError(name, { message: messages[0] });
          }
        });
      }
      toast.error(errorMessage(error));
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Change password</DialogTitle>
          <DialogDescription>
            You will be signed out and will need to sign in again.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label>Current password</Label>
            <Input type="password" autoComplete="current-password" {...register("old_password")} />
            {errors.old_password && (
              <p className="text-xs text-destructive">{errors.old_password.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label>New password</Label>
            <Input type="password" autoComplete="new-password" {...register("new_password")} />
            {errors.new_password && (
              <p className="text-xs text-destructive">{errors.new_password.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label>Confirm new password</Label>
            <Input type="password" autoComplete="new-password" {...register("confirm")} />
            {errors.confirm && (
              <p className="text-xs text-destructive">{errors.confirm.message}</p>
            )}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit" loading={isSubmitting}>
              {isSubmitting ? "Changing…" : "Change password"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
