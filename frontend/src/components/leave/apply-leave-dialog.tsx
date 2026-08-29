"use client";

import { useMemo, useState } from "react";
import { toast } from "sonner";

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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useLeaveTypes } from "@/hooks/use-leave";
import { api, errorMessage } from "@/lib/api";
import { todayISO, workingDays } from "@/lib/leave";
import type { LeaveBalance } from "@/lib/types";

export function ApplyLeaveDialog({
  open,
  onOpenChange,
  balances,
  onApplied,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  balances: LeaveBalance[];
  onApplied: () => void;
}) {
  const leaveTypes = useLeaveTypes();

  const [leaveTypeId, setLeaveTypeId] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [reason, setReason] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const typeItems = useMemo(
    () => Object.fromEntries(leaveTypes.map((t) => [String(t.id), t.name])),
    [leaveTypes],
  );

  // How many days they are asking for, updated as they pick dates.
  const requested = workingDays(startDate, endDate);

  // The balance for the type they picked, so we can compare.
  const balance = balances.find(
    (b) => String(b.leave_type.id) === leaveTypeId,
  );
  const available = balance ? Number(balance.available) : null;

  const notEnough = available !== null && requested > available;
  const canSubmit =
    leaveTypeId && startDate && endDate && requested > 0 && !notEnough;

  function reset() {
    setLeaveTypeId("");
    setStartDate("");
    setEndDate("");
    setReason("");
  }

  async function submit() {
    setSubmitting(true);
    try {
      await api.post("/leave/requests/", {
        leave_type: Number(leaveTypeId),
        start_date: startDate,
        end_date: endDate,
        reason,
      });
      toast.success("Leave requested. Your manager will be notified.");
      reset();
      onOpenChange(false);
      // Tell the page to re-fetch — the balance just changed.
      onApplied();
    } catch (error) {
      // Overlaps, insufficient balance, past dates — the backend explains
      // exactly which rule was broken, so show its words, not ours.
      toast.error(errorMessage(error));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Apply for leave</DialogTitle>
          <DialogDescription>
            Weekends are not counted. Public holidays are not handled yet.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Leave type</Label>
            <Select
              items={typeItems}
              value={leaveTypeId}
              onValueChange={(v) => setLeaveTypeId(String(v))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Choose a leave type" />
              </SelectTrigger>
              <SelectContent>
                {leaveTypes.map((type) => (
                  <SelectItem key={type.id} value={String(type.id)}>
                    {type.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label>From</Label>
              <Input
                type="date"
                min={todayISO()}
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label>To</Label>
              <Input
                type="date"
                min={startDate || todayISO()}
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label>Reason (optional)</Label>
            <Input
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Family trip"
            />
          </div>

          {/* The live summary. This is the whole point of the dialog. */}
          {requested > 0 && (
            <div
              className={
                notEnough
                  ? "rounded-md bg-destructive/10 p-3 text-sm text-destructive"
                  : "rounded-md bg-muted p-3 text-sm"
              }
            >
              <p className="font-medium">
                {requested} working {requested === 1 ? "day" : "days"}
              </p>
              {available !== null && (
                <p className="text-xs">
                  {notEnough
                    ? `You only have ${available} days of ${balance!.leave_type.code} left.`
                    : `${available} available · ${available - requested} left after this`}
                </p>
              )}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button disabled={!canSubmit} loading={submitting} onClick={submit}>

            {submitting ? "Sending…" : "Apply"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
