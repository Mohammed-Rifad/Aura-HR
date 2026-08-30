"use client";

import { useState } from "react";
import { Check, Copy } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

export function TemporaryPasswordDialog({
  issued,
  onClose,
}: {
  issued: { email: string; password: string } | null;
  onClose: () => void;
}) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    if (!issued) return;
    await navigator.clipboard.writeText(issued.password);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <Dialog open={issued !== null} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Temporary password</DialogTitle>
          <DialogDescription>
            For {issued?.email}. Give it to them directly and ask them to
            change it after signing in.
          </DialogDescription>
        </DialogHeader>

        <div className="rounded-lg border bg-muted/50 p-4 text-center">
          <code className="font-mono text-lg tracking-wide select-all">
            {issued?.password}
          </code>
        </div>

        {/* Not a warning to be careful — a statement of fact. The server
            stored a hash; this string exists nowhere else now. */}
        <p className="text-xs text-muted-foreground">
          Shown once. It is not stored anywhere and cannot be looked up again.
          If it is lost, issue a new one.
        </p>

        <DialogFooter>
          <Button variant="outline" onClick={copy}>
            {copied ? <Check className="size-4" /> : <Copy className="size-4" />}
            {copied ? "Copied" : "Copy"}
          </Button>
          <Button onClick={onClose}>Done</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
